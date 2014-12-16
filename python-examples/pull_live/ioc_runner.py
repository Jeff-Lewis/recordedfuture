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
import json

from ioc_enricher import IOCEnricher, rf_agg_name_parser

from RFAPI import RFAPI


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

def get_arguments():
    parser = argparse.ArgumentParser(description='Run ioc_enricher for all iocs between a time period.')
    parser.add_argument('token', help="Recorded Future token.")
    parser.add_argument('entity_type', default="IpAddress", choices=["IpAddress", "Hash", "InternetDomainName"], help="One of IpAddress, Hash, InternetDomainName.")
    parser.add_argument('mode', default="core", choices=["core", "related", "debug"], help="Mode for enrichment output.")
    parser.add_argument('index_min', help="Index min (in ISO format, e.g. '2014-12-16T15:00.000Z' or any prefix thereof).")
    parser.add_argument('index_max', help="Index max (in ISO format, e.g. '2014-12-16T15:00.000Z' or any prefix thereof).")
    parser.add_argument('output_type', choices=["csv", "json"], help="Output format.")
    parser.add_argument('output_file', help="Output filename.")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_arguments()
    token = args.token
    e_type = args.entity_type
    mode = args.mode
    output_type = args.output_type
    output_file = args.output_file
    index_min = args.index_min
    index_max = args.index_max
    iocs = get_all_iocs(token, e_type, index_min, index_max)
    enricher = IOCEnricher(token, iocs, e_type, mode)
    enriched_iocs = enricher.enrich()
    write_references(enriched_iocs, enricher.get_keys(), output_type, output_file)
