#This script shows how you can run an aggregate query against a set of dates and tickers.
#tickers are passed in via a file (one ticker per line) specified in a command line argument. 
#Dates are also specified via command line.

#Some output is sent to standard error for informational purposes.

#Example run:
#company-aggquery.py TOKEN tickerfile.txt 2010-02-01 2010-07-28 > outputfile.txt

import sys, recfut, json, datetime
from datetime import datetime

#Read in a ticker file and token. If no ticker file or token is given, display an error message and quit.
if len(sys.argv) < 3:
	print >>stderr, "No ticker file or no token supplied."
	print >>stderr, "Usage: " + sys.argv[0] + " tickerfile [min_date [max_date]]"
	exit(1)

token = sys.argv[1]

qtickerf = open(sys.argv[2], "r")
tickerlist = []

for line in qtickerf:
	tickerlist.append(unicode(line.rstrip()))
qtickerf.close()

#Set default dates. These can be overridden with command line options.
#If no date is given, use today.
mindate = maxdate = datetime.now()

if len(sys.argv) > 3:
	mindate = maxdate = datetime.strptime(sys.argv[3], "%Y-%m-%d") #parser.parse(sys.argv[3])
if len(sys.argv) > 4:
	maxdate = datetime.strptime(sys.argv[4], "%Y-%m-%d") #parser.parse(sys.argv[4])


#This is an aggregate query.
querystring = """
{
  "aggregate": {
    "entity": {"type": "Company", 
		"attributes": {
			"name": "tickers",
			"string": []
		}
     },
    "document": {"published": {"min": "", "max": ""}},
    "key": "tickers"
  },
  
  "output": {
    "fields": ["count", "momentum", "positive", "negative"],
    "format": "csv"
  },
  "token": ""
}
"""

#You can set whichever output fields you want to here, by default we use a limited selection
outfields = ["count", "momentum", "positive", "negative"]

#Load the query up into a dict for parameterization.
qdict = json.loads(querystring)

#Set the ticker list to pull and set the output fields in the query dict.
qdict["aggregate"]["entity"]["attributes"]["string"] = tickerlist
qdict["output"]["fields"] = outfields
qdict["token"] = token


#Iterate a single date at a time. Send some status output to stderr. We handle output of first
#iteration slightly differently. If we get an error for a particular date, display an error
#message but continue running.
run = False

for single_date in recfut.daterange(mindate, maxdate, inclusive=True):
	print >>sys.stderr, "Running date " + single_date.strftime("%Y-%m-%d")
	
	qdict["aggregate"]["document"]["published"]["min"] = unicode(single_date.strftime("%Y-%m-%d"))
	qdict["aggregate"]["document"]["published"]["max"] = unicode(single_date.strftime("%Y-%m-%d"))	
	#If we receive an error, send it to STDERR, but continue anyway.
	res = recfut.query(q=json.dumps(qdict))
	if res["status"] == "FAILURE":
		print >>sys.stderr, res
		continue
	
	if run:
		print '\n'.join(res["aggregates"].split('\n')[1:]),
	else:
		print res["aggregates"],
	run = True

