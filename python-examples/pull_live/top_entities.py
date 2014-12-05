'''
Generates tables of top entities from specified queries as
in the Recorded Future Cyber Daily.

Contact: support@recordedfuture.com
'''
import argparse
import collections
import copy
import csv
import datetime
import json
import os

from RFAPI import RFAPI


entity_paging_param = 150
emerging_threshold = datetime.timedelta(days=7)

def get_toplists(queries, rfqapi, n, period, bools):
    '''Returns dictionary of tables (keyed by query name)
    '''
    toplists = {}
    for f in queries:
        print f
        if bools['new']:
            delta = emerging_threshold
        else:
            delta = datetime.datetime(days=period)
        datemin = datetime.datetime.utcnow()-delta
        datemax = datetime.datetime.utcnow()-datetime.timedelta(days=1)
        if datemin == datemax:
            pubtime = datemin.strftime('%b %d %Y')
        else:
            pubtime = datemin.strftime('%b %d %Y') + '--' + datemax.strftime('%b %d %Y')
        queries[f]['instance']['document']['published']['min'] = datemin.strftime('%Y-%m-%d')
        queries[f]['instance']['document']['published']['max'] = datemax.strftime('%Y-%m-%d')
        toplists[f[:-4]] = get_toplist(rfqapi, queries[f], n, pubtime, bools)
    return toplists

def get_toplist(rfqapi, q, N, pubtime, bools):
    '''Returns toplist table for a particular query
    '''
    entity_counts = collections.Counter()
    res = rfqapi.query(q)
    for entity in res['counts'][0]:
        if 'instances' not in res['counts'][0][entity]:
            entity_counts[entity] = res['counts'][0][entity]['documents']
        else:
            entity_counts[entity] = res['counts'][0][entity]['instances']
    target_counts = []
    entities = sorted(entity_counts.keys(), key=lambda eid: entity_counts[eid], reverse=True)
    if bools['new']: # remove old entities and singletons
        entities = remove_old_entities(entities,rfqapi,q)
        entities = [eid for eid in entities if entity_counts[eid] > 1]
    entities = entities[:2*N]
    # Resolve entities to get their names
    for i in range(len(entities)/entity_paging_param+1):
        entity_ids = entities[i*entity_paging_param:(i+1)*entity_paging_param]
        if len(entity_ids) == 0: continue
        query = {"entity":{"id":entity_ids, "limit":entity_paging_param*2}}
        entity_res = rfqapi.query(query)
        for eid in filter(lambda e: e in entity_res['entities'], entity_ids):
            edetails = entity_res['entity_details'][eid]
            new_row = [edetails['name'].encode('utf8'), entity_counts[eid]]
            if bools['assoc']:
                # Get associated product / malware / technologies
                prodquery = {"instance":{"type":"Event",
                                         "attributes":[{'entity':{'id':eid}},
                                                       {'entity':{'type':['Technology','Product', 'Malware']}}]},
                             "output":{"count": {"axis": [{"name":"attributes.entities",
                                                           "type":["Product", "Technology", 'Malware']}],
                                                 "values": ["documents"]}}}
                prods = get_toplist(rfqapi, prodquery, N, pubtime, {"assoc": False, "new": False})
                prods = [prod[0] for prod in sorted(prods, key=lambda row: row[1], reverse=True)]
                prods = list(collections.OrderedDict.fromkeys(prods))[:5]
                new_row.append(', '.join(prods))
            new_row.append(generate_rfurl_from_entity(eid, edetails['name'].encode('utf8'), pubtime))
            target_counts.append(new_row)
            if len(target_counts) >= N and target_counts[N-1][1] != entity_counts[eid]:
                return target_counts[:-1]
    return target_counts

def remove_old_entities(entities, rfqapi, q):
    new_entities = []
    new_q = copy.deepcopy(q)
    del new_q['comment']
    cache_name = 'old_entities' + str(emerging_threshold.days) + '.oldcache'
    f = open(cache_name,'ab+')
    f.seek(0, os.SEEK_SET)
    old_entities = {}
    for line in f.readlines():
        eid, date = line.strip().split('\t')
        date = datetime.datetime.strptime(date,'%Y-%m-%d')
        old_entities[eid] = date
    for eid in entities:
        if not is_old(rfqapi, q, eid, old_entities, f):
            new_entities.append(eid)
    return new_entities

def is_old(rfqapi, q, eid, old_entities, f):
    min_date = datetime.datetime.strptime(q['instance']['document']['published']['min'],'%Y-%m-%d')
    threshold = min_date
    if eid in old_entities and old_entities[eid] <= threshold:
        return True
    elif eid in old_entities and old_entities[eid] > threshold:
        return False
    new_q = {"instance":{"attributes":[{"entity":{"id":eid}}],
                         "limit":0,
                         "document":{"published":{"max":(threshold-datetime.timedelta(days=1)).strftime('%Y-%m-%d')}}}}
    res = rfqapi.query(new_q)
    if res['count']['references']['total'] > 0:        
        # store threshold to cache if there are older hits (don't compute the oldest)
        f.write('\t'.join((eid,threshold.strftime('%Y-%m-%d')))+'\n')
        return True
    elif eid not in old_entities:
        new_q = {"instance":{"attributes":[{"entity":{"id":eid}}],
                             "document":{"published":{"min":threshold.strftime('%Y-%m-%d')}}},
                 "output":{"count": {"axis": ["publication_day"],
                                     "values": ["instances"]}}}
        res = rfqapi.query(new_q)
        earliest = min(res['counts'][0].keys())
        # store earliest date to cache
        f.write('\t'.join((eid,earliest))+'\n')                
    return False


def generate_rfurl_from_entity(eid, ename, pubtime=None):
    base_url = 'https://www.recordedfuture.com/live/sc/'
    if isinstance(eid,unicode): eid = eid.encode('utf8')
    if isinstance(ename,unicode): ename = ename.encode('utf8')
    params = []
    params.append({"id": "groupname", "value": "Mentions", "name": "Mentions"})
    params.append({"id": "entity", "value": eid, "name": ename})
    if pubtime: params.append({"id": "pubtime", "value": pubtime, "name": pubtime})
    params = json.dumps([params])
    return base_url + '2gWqxC6apubO?patterns=' + params

def clean_name(name, header):
    '''Obfuscates suspicious links
    '''
    header = header.lower()
    if 'malware' in header or 'ip address' in header or 'domain' in header:
        return name.replace('.', '[.]')
    else:
        return name

def get_queries(files):
    '''Loads queries
    '''
    queries = {}
    for f in files:
        queries[f] = json.loads(open(f, 'rb').read())
    return queries

def write_details(toplists, bools):
    csv.register_dialect('toplists', doublequote=False, quotechar="'", escapechar='\\')
    for f in toplists:
        w = csv.writer(open(f + '.csv', 'wb'), dialect='toplists')
        header = ['Name', 'Hits']
        if bools['assoc']: header += ['Associated Entities']
        header += ['Link']
        w.writerow(header)
        w.writerows(toplists[f])

def get_arguments():
    parser = argparse.ArgumentParser(description='Pull top lists from Recorded Future.')
    parser.add_argument('token', help="Recorded Future API token.")
    parser.add_argument('n', help="Number of results to return per query.", type=int)
    parser.add_argument('period', help="Number of days back to query.", type=int)
    parser.add_argument('query_file', nargs='+', help="Query files.")
    parser.add_argument('-assoc', '--assoc', help="Include associated products, techs, malware.", action='store_true')
    parser.add_argument('-new', '--new', help="Include only entities first seen in the last %s days." % emerging_threshold.days, action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_arguments()
    token = args.token
    n = args.n
    period = args.period
    files = args.query_file
    bools = {"assoc": args.assoc,
             "new": args.new}
    rfqapi = RFAPI(token)
    queries = get_queries(files)
    toplists = get_toplists(queries, rfqapi, n, period, bools)
    write_details(toplists, bools)
