import json, urllib, recfut, sys

def generate_sentiment_sparkline(ticker, from_date, to_date, token):
    #Do an RF entity lookup
    eid = recfut.lookup_id(ticker, token)

    #Next, do an aggregate_raw query on that entity ID.
    aggquerystring = '{"aggregate_raw":{},"output":{"fields":["positive","negative"]}}'
    query = json.loads(aggquerystring)
    query["token"] = token
    query["aggregate_raw"] = {"entity":{"id":eid}, "document":{"published":{"min":from_date,"max":to_date}}}
    res = recfut.query(json.dumps(query))

    #Grab our data from the result object.
    pos = [r["positive"] for r in res["aggregates"]]
    neg = [r["negative"] for r in res["aggregates"]]

    #Do a moving average on the data.
    n = 20
    pos = [sum(pos[i-n:i])/n for i in range(n,len(pos))]
    neg = [sum(neg[i-n:i])/n for i in range(n,len(neg))]

    minpos,maxpos = min(pos),max(pos)
    minneg,maxneg = min(neg),max(neg)

    pos = [str(i) for i in pos]
    neg = [str(i) for i in neg]

    #Set up graph formatting.
    graph_params = {
        "chs":"200x80",
        "cht":"ls",
        "chco":"000000,FF0000",
        "chds":"%f,%f,%f,%f" % (0.0,maxpos,0.0,maxpos),
        "chd":"t:%s|%s" % (",".join(pos), ",".join(neg)),
        "chdl":"Positive|Negative",
        "chdlp":"b",
        "chls":"1|1",
        "chma":"5,5,5,5"
    }

    #Request the chart from Google.
    url = "http://chart.apis.google.com/chart"
    val = urllib.urlopen(url, data=urllib.urlencode(graph_params))

    return val.read()

if __name__ == "__main__":
    ticker = "AAPL"
    from_date = "2010-05-21"
    to_date = "2010-11-21"
    token = "MYTOKEN"

    val = generate_sentiment_sparkline(ticker, from_date, to_date, token)

    f = open("out.png", "w")
    print >>f, val
    f.close()
