'''
Generates csv of references from Recorded Future matching a list of
IOCs in an input file (one IOC per line).

Contact: support@recordedfuture.com
'''
import argparse
import csv

from RFAPI import RFAPI


def query_generator(iocs, pubmin, pubmax):
    q = {"instance": {"type": "Event",
                      "document": {"published": {"min": pubmin, "max": pubmax}},
                      "limit": 7500,
                      "searchtype": "scan"}}
    for ioc_chunk in chunks(iocs, 100):
        q['instance']['attributes'] = [{"name": "Event.event_fragment", 'string': ioc_chunk}]
        yield q

def get_iocs(fname):
    '''Read IOCs from file fname
    '''
    with open(fname, 'rb') as f:
        iocs = set([l.strip() for l in f.readlines() if len(l.strip()) > 0])
    return list(iocs)

def get_rf_references(iocs, token, pubmin, pubmax):
    '''Pulls Recorded Future references to IOCs
    '''
    rfqapi = RFAPI(token)
    queries = list(query_generator(iocs, pubmin, pubmax))
    for res in rfqapi.batch_query(queries):
        yield res['instances']

def write_references(w, refs):
    '''Writes references to specified file (csv format)
    '''
    newrow = []
    for inst in refs:
        pub = inst['document']['published'] if ('document' in inst and 'published' in inst['document']) else ''
        fragment = inst['fragment'].encode('utf8') if 'fragment' in inst else ''
        url = inst['document']['url']
        newrow = [pub, fragment, url]
        w.writerow(newrow)

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def get_arguments():
    parser = argparse.ArgumentParser(description='Generate csv of references to IOCs.')
    parser.add_argument('token', help="Recorded Future token.")
    parser.add_argument('ioc_file',help="Filename for list of IOCs (one per line).")
    parser.add_argument('output_file',help="Filename for output references (csv).")
    parser.add_argument('min', help="Min publish time (format: 2014-01-01T00:00:00.000Z).")
    parser.add_argument('max', help="Max publish time (format: 2014-01-01T00:00:00.000Z).")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_arguments()
    token = args.token
    fin = args.ioc_file
    fout = args.output_file
    pubmin = args.min
    pubmax = args.max
    iocs = get_iocs(fin)
    with open(fout, 'wb') as f:
        w = csv.writer(f)
        w.writerow(['published', 'fragment', 'url'])
        for refs in get_rf_references(iocs, token, pubmin, pubmax):
            write_references(w, refs)
