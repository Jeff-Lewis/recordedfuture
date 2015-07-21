#!/usr/bin/env python
"""Example script that provides command-line searching/fetching of Recorded
Future references and aggregates.

"""

import json
import sys
import csv
import optparse

from RFAPI import RFAPI

def parse_arguments():
    parser = optparse.OptionParser(usage="%prog [options] queryfile.rfq")
    parser.set_defaults(page=True)
    parser.add_option("--min", dest="min", help="Minimum published date.")
    parser.add_option("--max", dest="max", help="Maximum published date.")
    parser.add_option("-t", "--token", dest="token", help="RF API Token.")
    parser.add_option("-i", "--idfile", dest="idfile", help="Filename of file containing list of RF IDs.")
    parser.add_option("-s", "--sourcefile", dest="sourcefile", help="Filename of the file containing a list of source IDs.")
    parser.add_option("-p", "--page", action="store_true", dest="page", help="Turn paging of results on.")
    parser.add_option("-n", "--no-page", action="store_false", dest="page", help="Turn paging of results off.")
    parser.add_option("--no-header", action="store_false", dest="header", default=True, help="Turn header output off.")
    parser.add_option("-e", "--entity_file", dest="entityfile", default=False, help="Store entities returned by query in file. (Not available for aggregate queries)")
    parser.add_option("-f", "--freetext_file", dest="freetextfile", default=False, help="File that contains freetext strings to search for - one per line.")

    (options, args) = parser.parse_args()
    return options, args

def flatten_dict(d):
    """Produce a flattened list of key-value pairs from a nested dictionary.

    """
    res = {}
    for k, v in d.items():
        if isinstance(v, dict):
            subdict = flatten_dict(v)
            for subk, subv in subdict.items():
                res[k+'.'+subk] = subv
        else:
            res[k] = v
    return res

def parse_value(val, entities, substitute=True):
    """Parse either a value or list of values and return combined results free
    of tab and newline characters.

    """
    if substitute and unicode(val) in entities and entities[unicode(val)].get('name'):
        val = entities[unicode(val)]['name']
        val = ''.join([c for c in val if ord(c)<128])
        return val.replace('"', '').replace('\r',' ').replace('\n',' ').replace('\t',' ').strip()
    elif isinstance(val, unicode):
        val = ''.join([c for c in val if ord(c)<128])
        return val.replace('"','').replace('\r',' ').replace('\n',' ').replace('\t',' ').strip()
    else:
        return val

def dict_to_parsed_string(d, e, s=True):
    res = []
    for k, val in d.items():
        if isinstance(val, list):
            res.append(k+":"+','.join([unicode(parse_value(v, e, s)) for v in val]))
        else:
            res.append(k+":"+unicode(parse_value(val, e, s)))
    return '||'.join(res)

def substitute_entities(i, e, fields):
    for f in fields:
        i[f] = parse_value(i[f], e)
    return i

def flatten_attributes(i, e, substitute=True):
    try:
        return dict_to_parsed_string(i['attributes'], e, substitute)
    except:
        return None

def flatten_instance(i, e, fields):
    i['attributes'] = flatten_attributes(i, e, 'attributes' in fields)
    i = flatten_dict(i)
    i = substitute_entities(i, e, fields)
    return i

def pack_entity_attributes(entities, entity_headers):
    for k, e in entities.items():
        e['attributes'] = {}
        e['id'] = k
        for a in e:
            if a not in entity_headers:
                e['attributes'][a] = e[a]
        for a in e['attributes']:
            del e[a]
    return entities.values()

def build_query(options, args):
    try:
        query = json.loads(open(args[0]).read())
        if 'aggregate' in query:
            qtype = 'aggregate'
        else:
            qtype = 'instance'
            query['instance']['searchtype'] = 'scan'
            if 'limit' not in query['instance']:
                query['instance']['limit'] = 10000

        if options.idfile:
            ids = [i.strip() for i in open(options.idfile).readlines()]
            if qtype == "instance":
                if qtype in query:
                    if 'attributes' not in query[qtype]:
                        query[qtype]['attributes'] = {}
                    if 'entity' not in query[qtype]['attributes']:
                        query[qtype]['attributes']['entity'] = {}
                query[qtype]['attributes']['entity']['id'] = ids
            if qtype == "aggregate":
                if "entity" not in query[qtype]:
                    query[qtype]['entity'] = {}
                query[qtype]['entity']['id'] = ids

        if options.sourcefile:
            ids = [i.strip() for i in open(options.sourcefile).readlines()]
            if qtype in query:
                if 'document' not in query[qtype]:
                    query[qtype]['document'] = {}
                if 'source' not in query[qtype]['document']:
                    query[qtype]['document']['source'] = {}
                query[qtype]['document']['source']['id'] = ids

        if options.min:
            if qtype in query:
                if 'document' not in query[qtype]:
                    query[qtype]['document'] = {}
                if 'published' not in query[qtype]['document']:
                    query[qtype]['document']['published'] = {}
            query[qtype]['document']['published']['min'] = options.min

        if options.max:
            query[qtype]['document']['published']['max'] = options.max

        if options.freetextfile:
            query[qtype]['freetext'] = [[l.strip() for l in open(options.freetextfile).readlines()]]
    except Exception, e:
        print >> sys.stderr, "Error parsing options:", e
        exit(1)

    print >> sys.stderr, json.dumps(query, indent=2)
    return query

def encode_instance(i):
    for k, v in i.items():
        if isinstance(v, unicode):
            i[k] = v.encode('utf-8')
    return i

def main():
    options, args = parse_arguments()
    query = build_query(options, args)

    api = RFAPI(options.token)

    substitute_fields = ['attributes']
    output_columns = ['id', 'momentum', 'positive', 'negative', 'canonical.id',
            'type', 'document.id', 'document.published', 'document.downloaded',
            'start', 'stop', 'document.url','document.title',
            'document.sourceId.id', 'document.sourceId.name',
            'document.sourceId.media_type', 'document.sourceId.topic',
            'document.sourceId.country', 'fragment', 'attributes']
    entity_columns = ['id', 'name', 'hits', 'type', 'momentum', 'attributes']

    out = csv.DictWriter(sys.stdout, output_columns, extrasaction='ignore')

    if query.get('aggregate') or query.get('output', {}).get('count'):
        res = api.query(query)
        print res
        return
        
    if options.header:
        out.writerow(dict(zip(output_columns, output_columns)))
    if options.entityfile:
        entityout = csv.DictWriter(open(options.entityfile, 'w'), entity_columns, extrasaction='ignore')
        entityout.writerow(dict(zip(entity_columns, entity_columns)))

    for res in api.paged_query(query):
        for i in res['instances']:
            i['positive'] = i.get('attributes', {}).get('positive', 0.0)
            i['negative'] = i.get('attributes', {}).get('negative', 0.0)
            out.writerow(encode_instance(flatten_instance(i, res['entities'], substitute_fields)))

        if options.entityfile:
            entities = pack_entity_attributes(res['entities'], entity_columns)
            for e in entities:
                #Here we reuse the instance formatting code to format entities for output.
                entityout.writerow(encode_instance(flatten_instance(e, res['entities'], [])))

        if not options.page:
            break

if __name__ == "__main__":
    main()
