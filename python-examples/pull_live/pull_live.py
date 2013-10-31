import json, sys, csv, optparse, uidecode
from recfut import page_pull, flatten_instance, run_query

def translate_id(i):
  try:
    i = int(i)
    i = uidecode.b64encode(i)
  except:
    pass
  return i
  
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
  
def pack_entity_attributes(entities, entity_headers):
  for k,e in entities.items():
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

    if options.token:
      query['token'] = options.token

    if 'aggregate' in query:
      qtype = 'aggregate'
    else:
      qtype = 'instance'

    if options.idfile:
      ids = [translate_id(i.strip()) for i in open(options.idfile).readlines()]
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
      ids = [translate_id(i.strip()) for i in open(options.sourcefile).readlines()]
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
    print >>sys.stderr, "Error parsing options:", e
  
  print >>sys.stderr, json.dumps(query, indent=2)
  return json.dumps(query)


def encode_instance(i):
  for k,v in i.items():
    if isinstance(v, unicode):
      i[k] = v.encode('utf-8')
  return i



def main():
  options, args = parse_arguments()
  query = build_query(options, args)
  
  substitute_fields = ['attributes']
  output_columns = ['id','momentum','positive','negative','canonical.id','type',
             'document.id', 'document.published','document.downloaded',
             'start','stop', 'document.url','document.title',
             'document.sourceId.id','document.sourceId.name',
             'document.sourceId.media_type','document.sourceId.topic',
             'document.sourceId.country','fragment','attributes']
  entity_columns = ['id','name','hits','type','momentum','attributes']
  
  out = csv.DictWriter(sys.stdout, output_columns, extrasaction='ignore')
  
  if json.loads(query).get('aggregate') or json.loads(query).get('output',{}).get('count'):
      res = run_query(query)
      print res

  else:
    if options.header:
      out.writerow(dict(zip(output_columns, output_columns)))
    if options.entityfile:
      entityout = csv.DictWriter(open(options.entityfile, 'w'), entity_columns, extrasaction='ignore')
      entityout.writerow(dict(zip(entity_columns, entity_columns)))

    for res in page_pull(query):
      for i in res['instances']:
        i['positive'] = i.get('attributes', {}).get('positive',0.0)
        i['negative'] = i.get('attributes', {}).get('negative',0.0)
        out.writerow(encode_instance(flatten_instance(i, res['entities'], substitute_fields)))
        
      if options.entityfile:
          entities = pack_entity_attributes(res['entities'], entity_columns)
          #print json.dumps(entities, indent=2)
          for e in entities:
            #Here we reuse the instance formatting code to format entities for output.
            entityout.writerow(encode_instance(flatten_instance(e, res['entities'], [])))
            
      if not options.page:
        break
      
if __name__ == "__main__":
  main()
