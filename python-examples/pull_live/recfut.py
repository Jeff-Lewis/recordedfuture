import urllib2, urllib, json, datetime, gzip, sys, time, os
from StringIO import StringIO


def run_query(q):
  try:
    url = 'https://api.recordedfuture.com/query/'
    #url = 'http://www-5044.recfut.net:9393/rfq/'

    for i in range(3):
      try:

        request = urllib2.Request(url, urllib.urlencode({"q":q}))
        request.add_header('Accept-encoding', 'gzip')
        response = urllib2.urlopen(request)

        data = response.read()
        break

      except:
        print >>sys.stderr, "Retrying failed API call."
        time.sleep(1)

    if response.info().get('Content-Encoding') == 'gzip':
      buf = StringIO(data)
      f = gzip.GzipFile(fileobj=buf)
      data = f.read()

    return data

  except Exception, e:
    print str(e)
    return {'status': 'FAILURE', 'errors': str(e)}


def page_pull(q):
  pull = True
  while pull:
    try:
      res = run_query(q)
      res = json.loads(res)
      yield res

    except Exception, e:
      print >>sys.stderr, e

    if 'next_page_start' in res:
      print >>sys.stderr, res['next_page_start']
      q = json.loads(q)
      q['instance']['page_start'] = res['next_page_start']
      q = json.dumps(q)
    else:
      pull = False


def flatten_dict(d):
  """Produce a flattened list of key-value pairs from a nested dictionary."""
  res={}
  for k,v in d.items():
    if isinstance(v,dict):
      subdict=flatten_dict(v)
      for subk,subv in subdict.items():
        res[k+'.'+subk]=subv
    else:
      res[k]=v
  return res


def parse_value(val,entities, substitute=True):
  """
  Parse either a value or list of values and return combined results free
  of tab and newline characters.
  """
  if substitute and unicode(val) in entities and entities[unicode(val)].get('name'):
    val=entities[unicode(val)]['name']
    val=''.join([c for c in val if ord(c)<128])
    return val.replace('"', '').replace('\r',' ').replace('\n',' ').replace('\t',' ').strip()
  elif isinstance(val,unicode):
    val=''.join([c for c in val if ord(c)<128])
    return val.replace('"','').replace('\r',' ').replace('\n',' ').replace('\t',' ').strip()
  else:
    return val


def dict_to_parsed_string(d, e, s=True):
  res = []
  for k,val in d.items():
    if isinstance(val, list):
      res.append(k+":"+','.join([unicode(parse_value(v,e,s)) for v in val]))
    else:
      res.append(k+":"+unicode(parse_value(val,e,s)))
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
