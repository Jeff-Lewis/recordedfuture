import recfut, json, sys, csv, optparse

def parse_arguments():
  parser = optparse.OptionParser(usage="%prog [options] queryfile.rfq")
  
  parser.set_defaults(page=True)
  parser.add_option("-t", "--token", dest="token", help="RF API Token.")
  parser.add_option("-I", "--id", dest="id", help="An RF ID.")
  parser.add_option("-i", "--idfile", dest="idfile", help="Filename of file containing list of RF IDs.")
  parser.add_option("-N", "--name", dest="name", help="Entity Name")
  parser.add_option("-n", "--namefile", dest="namefile", help="Filename of file containing list of entity names.")
  parser.add_option("-K", "--type", dest="type", help="Entity type.")
  parser.add_option("-k", "--typefile", dest="typefile", help="Filename of file containing list of entity types.")
  parser.add_option("-f", "--freetext", dest="freetext", help="Freetext to search for.")
  parser.add_option("-T", "--top", type='int', dest="top",  help="Restrict search to only top number of entities found.")
  
  (options, args) = parser.parse_args()
  return options, args
  
  
def add_query_file_var(query, name, option):
  vals = [i.strip() for i in open(option).readlines()]
  if name in query['entity']:
    query['entity'][name] = [query['entity'][name]] + vals
  else:
    query['entity'][name] = vals
  return query


def build_query(options, args):
  try:
    query = {"entity":{},"output":{"format":"csv"}}
  
    if options.token:
      query['token'] = options.token
      
    if options.id:
      query['entity']['id'] = options.id
  
    if options.idfile:
      add_query_file_var(query, 'id', options.idfile)
    
    if options.name:
      query['entity']['name'] = options.name
    
    if options.namefile:
      add_query_file_var(query, 'name', options.namefile)
  
    if options.type:
      query['entity']['type'] = options.type
    
    if options.typefile:
      add_query_file_var(query, 'type', options.typefile)

    if options.freetext:
      query['entity']['freetext'] = options.freetext
    
    if options.top:
      query['entity']['limit'] = options.top
      
  except Exception, e:
    print >>sys.stderr, "Error parsing options:", e
  
  print >>sys.stderr, json.dumps(query, indent=2)
  return json.dumps(query)

def main():
  options, args = parse_arguments()
  query = build_query(options, args)
  res = recfut.run_query(query)
  print res

if __name__=="__main__":
  main()
