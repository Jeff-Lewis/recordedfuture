'''
This module contains several functions for accessing the Recorded Future API from Python.
'''


import urllib, json, datetime, zlib, sys


def query(q, usecompression=True):
	"""
	Issue a JSON-formatted query against the Recorded Future web service
	and return a dict corresponding to the JSON object returned as a result
	of that query.    
	"""
    try:
		url = 'http://api.recordedfuture.com/ws/rfq/instances?%s'
		
		if usecompression:
			url = url + '&compress=1'

		data = urllib.urlopen(url % urllib.urlencode({"q":q}))	
		
		if type(data) != str:
			data = data.read()
			
		if usecompression:
			data = zlib.decompress(data)
        #print data
		return json.loads(data)
    except Exception, e:
		print str(e)
		return {'status': 'FAILURE', 'errors': str(e)}


def daterange(start, stop, step=datetime.timedelta(days=1), inclusive=False): 
  	"""Produce a range of dates given start and end date and optionally step size."""
	# inclusive=False to behave like range by default 
	if step.days > 0: 
	  while start < stop: 
	    yield start 
	    start = start + step 
	    # not +=! don't modify object passed in if it's mutable 
	    # since this function is not restricted to 
	    # only types from datetime module 
	elif step.days < 0: 
	  while start > stop: 
	    yield start 
	    start = start + step 
	if inclusive and start == stop: 
	  yield start 


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

def parse_value(val,entities):
	"""
	Parse either a value or list of values and return combined results free
	of tab and newline characters.
	"""
    if unicode(val) in entities:
        val=entities[unicode(val)]['name']
        val=''.join([c for c in val if ord(c)<128])
        return val.replace('\n',' ').replace('\t',' ').strip()
    elif isinstance(val,unicode):
        val=''.join([c for c in val if ord(c)<128])
        return val.replace('\n',' ').replace('\t',' ').strip()
    else:
        return val


def flatten_query(q, outputorder=False):
	"""Run a query against the Recorded Future API and flatten the results
	into a list of tab-delimited rows. Useful for producing datasets from 
	query results. The optional outputorder argument specifies which columns
	to include in output and in which order they should appear."""
	result = query(q)
	
	if result['status']=='FAILURE':
		print 'FAILURE'
		print result['errors'][0]
		#print result['stacktrace'].replace('\n',' ')
		sys.exit(1)
	elif 'count' in result:
		print 'COUNT'
		print result['count']
		sys.exit(0)

	if 'entities' in result:
		entities=result['entities']
	else:
		entities={}

	output_data=[]
	if 'instances' in result:
		output_data=result['instances']
	elif 'sources' in result:
		output_data=result['sources']
	elif 'entity_details' in result:
		output_data=[]
		for key,val in result['entity_details'].items():
			val['id']=key
			output_data.append(val)
			
	if not outputorder: 
		headers=[]
		for instance in output_data:
			flat_instance=flatten_dict(instance)
			headers+=[k for k in flat_instance if k not in headers]

		if "document.id" in headers:
			headers=['document.id']+[h for h in headers if h!='document.id']
	else:
		headers = outputorder

	rows=[]
	for instance in output_data:
		flat_instance=flatten_dict(instance)
		newrow=[]
		for col in headers:
			if col in flat_instance:
				val=flat_instance[col]
				if isinstance(val,list):
					newrow.append(','.join([unicode(parse_value(v,entities)) for v in val]))
				else:
					newrow.append(parse_value(val,entities))
			else:
				newrow.append(' ')

		rows.append(newrow)

	retrows = []
	retrows.append('\t'.join(headers))
	for row in rows:
		retrows.append('\t'.join(['"'+v if isinstance(v,unicode) else str(v) for v in row]))
		
	return retrows