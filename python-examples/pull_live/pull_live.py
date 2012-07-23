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
  
  (options, args) = parser.parse_args()
  return options, args


def build_query(options, args):
  try:
    query = json.loads(open(args[0]).read())
  
    if options.token:
      query['token'] = options.token
  
    if options.idfile:
      ids = [translate_id(i.strip()) for i in open(options.idfile).readlines()]
      if 'instance' in query:
        if 'attributes' not in query['instance']:
          query['instance']['attributes'] = {}
        if 'entity' not in query['instance']['attributes']:
          query['instance']['attributes']['entity'] = {}
        query['instance']['attributes']['entity']['id'] = ids 
    
    if options.sourcefile:
      ids = [translate_id(i.strip()) for i in open(options.sourcefile).readlines()]
      if 'instance' in query:
        if 'document' not in query['instance']:
          query['instance']['document'] = {}
        if 'source' not in query['instance']['document']:
          query['instance']['document']['source'] = {}
        query['instance']['document']['source']['id'] = ids   
  
    if options.min:
      if 'instance' in query:
        if 'document' not in query['instance']:
          query['instance']['document'] = {}
        if 'published' not in query['instance']['document']:
          query['instance']['document']['published'] = {}
        query['instance']['document']['published']['min'] = options.min

    if options.max:
      query['instance']['document']['published']['max'] = options.max
      
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
  
  out = csv.DictWriter(sys.stdout, output_columns, extrasaction='ignore')

  if options.header:
    out.writerow(dict(zip(output_columns, output_columns)))
  
  for res in page_pull(query):
    for i in res['instances']:
      i['positive'] = i.get('attributes', {}).get('positive',0.0)
      i['negative'] = i.get('attributes', {}).get('negative',0.0)
      out.writerow(encode_instance(flatten_instance(i, res['entities'], substitute_fields)))
    if not options.page:
      break
      
if __name__ == "__main__":
  main()
