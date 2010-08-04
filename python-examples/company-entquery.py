#This script shows how you can run an entity query against a set of dates and tickers.
#tickers are passed in via a file (one ticker per line) specified in a command line argument.
#Dates are also specified via command line:

#Some output is sent to standard error for informational purposes.

#Example run:
#company-entquery.py TOKEN tickerfile.txt 2010-02-01 2010-07-28 > outputfile.txt


import sys, recfut, json, datetime
from datetime import datetime


#Read in a ticker file. If no ticker file or token is given, display an error message and quit.
if len(sys.argv) < 3:
	print >>sys.stderr, "No ticker file or token supplied."
	print >>sys.stderr, "Usage: " + sys.argv[0] + " tickerfile token [min_date [max_date]]"
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


#This is an instance query.
entquerystring = """
{
	"instance": {
		"document": {
			"published": {
					"min": "",
					"max": ""
			}
		},
		"attributes": {
			"type": "Company",
			"entity": {
				"attributes": {
					"name": "tickers",
					"string": []
				}
			}
		},
		"type": "EntityOccurrence"
	},
	"output": {
		"fields": [ ]
	},
	"token": ""
}"""


#You can set whichever output fields you want to here, by default we use a limited selection
outfields = ["id","time","source.name", "document.published","document.type","type", "momentum", "sentiment"]
#outfields = [ "id", "type", "time", "momentum", "sentiment", "attributes", "source.name", "source.topic", "document.id", "document.title", "source.description", "source.media_type", "document.published", "fragment", "fragment_coentities", "document_coentities", "document.coentities" ]

#Set the order of the output fields we'd like to see. If you decide to
outorder = ["id","document.published", "document.source.name", "start","stop","type", "momentum", "positive", "negative"]
#outorder = [ "id", "type", "start", "stop", "momentum", "positive", "negative", "attributes", "source.name", "source.topic", "document.id", "document.title", "source.description", "source.media_type", "document.published", "fragment", "fragment_coentities", "document_coentities", "document.coentities" ]
#outorder = False   #If you want to use the default output order.


#Load the query up into a dict for parameterization.
qdict = json.loads(entquerystring)

#Set the dates to pull and set the output fields in the query dict. Set the query token.

qdict["instance"]["document"]["published"]["min"] = mindate.strftime("%Y-%m-%d")
qdict["instance"]["document"]["published"]["max"] = maxdate.strftime("%Y-%m-%d")

qdict["output"]["fields"] = outfields
qdict["token"] = token


#Iterate a single ticker at a time. Send some status output to stderr. If we get an error for a
#particular date, display an error message but continue running.
run = False

for ticker in tickerlist:
	
	#Set the ticker.
	qdict["instance"]["attributes"]["entity"]["attributes"]["string"] = ticker
	
	print >>sys.stderr, "Running ticker " + ticker
	
	#First run with an EntityOccurrence filter.
	qdict["instance"]["type"] = "EntityOccurrence"
	
	#Run the query against Recorded Future and get back a flat table of results.
	res = recfut.flatten_query(q=json.dumps(qdict), outputorder=outorder)
	
	#Print column header information on first pass of the loop.
	if not run:
		print 'ticker\t' + res[0]
		run = True
	
	#For identification purposes, print the ticker as the first column of every row.
	for row in res[1:]:
		print ticker + '\t' + row
	
	#Now remove the EntityOccurrence filter.
	del qdict["instance"]["type"]
	#Run the new query.
	res = recfut.flatten_query(q=json.dumps(qdict), outputorder=outorder)
	
	#Print the new results with ticker.
	for row in res[1:]:
		print ticker + '\t' + row
