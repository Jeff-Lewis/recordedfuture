'''
Example of ioc enrichment using RF data. Running from
the command line will query for all IOCs of a certain type
indexed by RF between given times, and enrich them. The enriched
IOCs are written to a specified output file (in either 'csv'
or 'json' format).

Contact: support@recordedfuture.com
'''
import argparse
import csv
import datetime
import json
import time

import pymongo
import pytz

from RFAPI import RFAPI
from ioc_enricher import IOCEnricher, rf_agg_name_parser, _chunks
from pprint import pprint


def get_all_iocs(token, e_type, index_min, index_max):
    '''Gets all entities of type e_type found between
    index_min and index_max
    '''
    rfqapi = RFAPI(token)
    q = {"instance": {"type": "Event",
                      "attributes": [{"entity": {"type": e_type}}],
                      "document": {"indexed": {"min": index_min,
                                               "max": index_max}}},
         "output": {"count": {"axis":[{"name":"attributes.entities",
                                       "type":e_type,
                                       "aspect":"all"}],
                              "values":["instances"]}}}
    res = rfqapi.query(q)
    iocs = res["counts"][0].keys()
    ioc_dict = {}
    for ioc in iocs:
        ioc_name, rfid, unused = rf_agg_name_parser(ioc)
        ioc_dict[ioc_name] = rfid
    return ioc_dict

def write_references(enriched_iocs, fieldnames, output_type, output_file):
    '''Writes results to desired output file in desired
    output format.
    '''
    if output_type == 'csv':
        csv.register_dialect('enricher', doublequote=False, quotechar="'", escapechar='\\')
        with open(output_file, 'wb') as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, dialect='enricher')
            w.writeheader()
            for ioc in enriched_iocs:
                ioc_resp = enriched_iocs[ioc]
                for key in ioc_resp:
                    if isinstance(ioc_resp[key], unicode):
                        ioc_resp[key] = ioc_resp[key].encode('utf8')
                    elif isinstance(ioc_resp[key], list):
                        ioc_resp[key] = '|'.join(ioc_resp[key]).encode('utf8')
                w.writerow(ioc_resp)
    elif output_type == 'json':
        with open(output_file, 'wb') as w:
            w.write(json.dumps(enriched_iocs, ensure_ascii=False, indent=4).encode('utf8'))

def write_to_db(enriched_iocs, mdb):
    bulk = mdb['iocs'].initialize_ordered_bulk_op()
    for ioc in enriched_iocs:
        bulk.find({"Name": ioc}).upsert().update({"$set": enriched_iocs[ioc]})
    return bulk.execute()
    
def write_max_index(mdb, max_index):
    # updates single entry in updates db to the latest max index
    mdb['updates'].update({}, {"$set": {"last_seen_index": max_index}}, upsert=True)


def get_indexes(args, mdb=None):
    if args.output_type in ("csv", "json"):
        index_min = args.index_min        
        if args.index_max:
            index_max = args.index_max
        else:
            index_max = _rf_date_parser(datetime.date.utcnow() + datetime.timedelta(minutes=15))
            print "Using default index_max: %s" % index_max
    elif args.output_type == 'mongo':
        last_index = mdb['updates'].find_one()
        if last_index:
            if args.index_min:
                print "Ignoring index_min, subbing value from db."
            index_min = _rf_date_parser(_rf_date_parser(last_index['last_seen_index']) - datetime.timedelta(minutes=5))
        elif args.index_min:
            index_min = args.index_min
        else:
            print "Using default index_min of today."
            index_min = _rf_date_parser(datetime.date.today())
        index_max = _rf_date_parser(_rf_date_parser(index_min) + datetime.timedelta(minutes=15))
    print index_min, index_max
    return index_min, index_max

def _rf_date_parser(d):
    if isinstance(d, basestring):
        return datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%fZ'[:len(d)-2]).replace(tzinfo=pytz.UTC)
    elif isinstance(d, datetime.date):
        return d.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def runner(args, mdb=None):
    token = args.token
    e_type = args.entity_type
    mode = args.mode
    output_type = args.output_type
    index_min, index_max = get_indexes(args, mdb)
    print "Getting all IOCs between index times"
    all_iocs = get_all_iocs(token, e_type, index_min, index_max)
    print "  %s IOCs" % len(all_iocs)
    iocs_keys = all_iocs.keys()
    for ioc_chunk in _chunks(iocs_keys, 250):
        print "    Chunk: %s" % len(ioc_chunk)
        iocs = {}
        for ioc in ioc_chunk:
            iocs[ioc] = all_iocs[ioc]
        enricher = IOCEnricher(token, iocs, e_type, mode)
        print "    Enriching chunked IOCs"
        enriched_iocs, max_index = enricher.enrich()
        print "    Writing..."
        if output_type in ("csv", "json"):
            output_file = args.output_file
            write_references(enriched_iocs, enricher.get_keys(), output_type, output_file)
            return None
        elif output_type == 'mongo':
            res = write_to_db(enriched_iocs, mdb)
            write_max_index(mdb, max_index)
            return res

def validate(args):
    if args.output_type in ("csv", "json"):
        if args.continuous or not args.index_min or not args.index_max:
            raise Exception("Can't use given inputs with output_type: %s" % args.output_type)
        elif not args.output_file:
            raise Exception("Must specify output_file for output_type: %s" % args.output_type)
        mdb = None
    elif args.output_type == 'mongo':
        if not args.continuous:
            raise Exception("mongo must be run with continuous flag.")
        try:
            mdb = pymongo.MongoClient(host=args.mongo_host, port=args.mongo_port)[args.mongodb]
        except Exception as e:
            raise Exception("Mongo connection failed: %s" % e)
    if args.continuous and args.index_max:
        raise Exception("index_max can't be used in continuous mode.")
    return mdb

def get_arguments():
    parser = argparse.ArgumentParser(description='Run ioc_enricher for all iocs between a time period.')
    parser.add_argument('token', help="Recorded Future token.")
    parser.add_argument('entity_type', default="IpAddress", choices=["IpAddress", "Hash", "InternetDomainName"], help="One of IpAddress, Hash, InternetDomainName.")
    parser.add_argument('mode', default="core", choices=["core", "related", "debug"], help="Mode for enrichment output.")
    parser.add_argument('output_type', choices=["csv", "json", "mongo"], help="Output format.")
    parser.add_argument('--index_min', 
                        default=_rf_date_parser(datetime.date.today()), 
                        help="Index min (in ISO format, e.g. '2015-01-01T00:00:00.000Z' or any prefix thereof). Default: today.")
    parser.add_argument('--index_max', help="Index max (in ISO format, e.g. '2015-01-01T00:00:00.000Z' or any prefix thereof).")
    parser.add_argument('--output_file', help="Output filename.")
    parser.add_argument('--mongo_host', default="localhost", help="Mongo host name. Default: localhost.")
    parser.add_argument('--mongo_port', type=int, default=27017, help="Mongo port number. Default: 27017. ")
    parser.add_argument('--mongodb', default="rf_iocs", help="Mongo database name. Default: rf_iocs.")
    parser.add_argument('-c', '--continuous', action="store_true", help="Toggle to run continuously. Default: False.")
    parser.add_argument('--run_frequency', type=int, default=60, help="Frequency (in seconds) to run the script after last run. Default: 60.")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_arguments()
    mdb = validate(args)
    res = runner(args, mdb)
    pprint(res)
    while args.continuous:
        time.sleep(args.run_frequency)
        res = runner(args, mdb)
        pprint(res)
