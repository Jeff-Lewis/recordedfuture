#Copyright (c) 2010, Recorded Future, Inc.
#All rights reserved.

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Recorded Future nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL RECORDED FUTURE, INC. BE LIABLE FOR ANY
#DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#This script shows how you can run an aggregate query against a set of dates and tickers.
#tickers are passed in via a file (one ticker per line) specified in a command line argument.
#Dates are also specified via command line.

#Some output is sent to standard error for informational purposes.

#Example run:
#company-aggrawquery.py TOKEN tickerfile.txt 2010-02-01 2010-07-28 > outputfile.txt

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
	mindate = maxdate = sys.argv[3]
if len(sys.argv) > 4:
	maxdate = sys.argv[4]


#This is an aggregate query.
querystring = """
{
  "aggregate_raw": {
    "entity": {"id": []},
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
qdict["output"]["fields"] = outfields
qdict["token"] = token
qdict["aggregate_raw"]["document"]["published"]["min"] = mindate
qdict["aggregate_raw"]["document"]["published"]["max"] = maxdate


#Iterate a single ticker at a time. Send some status output to stderr.
#If we get an error for a particular ticker, display an error message but continue running.
print "ticker,id,Day," + ','.join(outfields)

for ticker in tickerlist:
        id = recfut.lookup_id(ticker, token)
        qdict["aggregate_raw"]["entity"]["id"] = id
	print >>sys.stderr, "Running ticker " + ticker

	#If we receive an error, send it to STDERR, but continue anyway.
	res = recfut.query(q=json.dumps(qdict))
	if res["status"] == "FAILURE":
		print >>sys.stderr, res
		continue
	res = res["aggregates"].split('\n')

	if len(res) < 2:
		continue

	print '\n'.join([ticker + "," + r.rstrip() for r in res[0:-1]])


