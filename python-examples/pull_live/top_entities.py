import argparse
import collections
import csv
import datetime
import json

from RFAPI import RFAPI


entity_paging_param = 150

def get_toplists(queries, rfqapi, n, period, assoc):
    '''Returns dictionary of tables (keyed by query name)
    '''
    toplists = {}
    for f in queries:
        print f
        delta = period
        datemin = datetime.datetime.utcnow()-datetime.timedelta(days=delta)
        datemax = datetime.datetime.utcnow()-datetime.timedelta(days=1)
        if datemin == datemax:
            pubtime = datemin.strftime('%b %d %Y')
        else:
            pubtime = datemin.strftime('%b %d %Y') + '--' + datemax.strftime('%b %d %Y')
        queries[f]['instance']['document']['published']['min'] = datemin.strftime('%Y-%m-%d')
        queries[f]['instance']['document']['published']['max'] = datemax.strftime('%Y-%m-%d')
        toplists[f[:-4]] = get_top_list(rfqapi, queries[f], n, pubtime, assoc)
    return toplists

def get_top_list(rfqapi, q, N, pubtime, assoc):
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
            if assoc:
                # Get associated product / malware / technologies
                pub_min = datetime.datetime.strptime(q['instance']['document']['published']['min'],'%Y-%m-%d')-datetime.timedelta(days=90)
                pub_min = pub_min.strftime('%Y-%m-%d')
                prodquery = {"instance":{"type":"Event",
                                         "attributes":[{'entity':{'id':eid}},
                                                       {'entity':{'type':['Technology','Product', 'Malware']}}],
                                         "document":{"published":{"min":pub_min}}},
                             "output":{"count": {"axis": [{"name":"attributes.entities",
                                                           "type":["Product", "Technology", 'Malware']}],
                                                 "values": ["documents"]}}}
                prods = get_top_list(rfqapi, prodquery, N, pubtime, False)
                prods = [prod[0] for prod in sorted(prods, key=lambda row: row[1], reverse=True)]
                prods = list(collections.OrderedDict.fromkeys(prods))[:5]
                new_row.append(', '.join(prods))
            new_row.append(GenerateRFURLFromEntity(eid, edetails['name'].encode('utf8'), pubtime))
            target_counts.append(new_row)
            if len(target_counts) >= N and target_counts[N-1][1] != entity_counts[eid]:
                return target_counts[:-1]
    return target_counts

def GenerateRFURLFromEntity(eid, ename=None, pubtime=None):
    '''Generates a link to RF Enterprise
    '''
    base_url = 'https://www.recordedfuture.com/live/sc/2gWqxC6apubO'
    if isinstance(eid, unicode):
        eid = eid.encode('utf8')
    if isinstance(ename, unicode):
        ename = ename.encode('utf8')
    params = '"id":"entity","value":"' + eid + '"'
    if ename: params += ',"name":"' + ename + '"'
    if pubtime: params += '%7D,%7B"id":"pubtime","value":"' + pubtime + '","name":"' + pubtime + '"'
    return base_url + '?patterns=[[%7B' + params + '%7D]]'

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

def write_details(toplists, assoc):
    for f in toplists:
        w = csv.writer(open(f + '.csv', 'wb'))
        header = ['Name', 'Hits']
        if assoc: header += ['Associated Entities']
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
    return parser.parse_args()

if __name__ == '__main__':
    args = get_arguments()
    token = args.token
    n = args.n
    period = args.period
    files = args.query_file
    assoc = args.assoc
    
    rfqapi = RFAPI(token)
    queries = get_queries(files)
    toplists = get_toplists(queries, rfqapi, n, period, assoc)
    write_details(toplists, assoc)
