source('rfapi.R')

#Set my API token so that the service yields results.
#query$token = YOURTOKEN
token <- paste(Sys.getenv('RFTOKEN'))

#You can change the date range like this:
from <- "2009-01-01"
to <- "2011-05-12"

#And set a list of tickers to query for like this:
tickerlist <- c('AAPL', 'MSFT', 'GOOG')
tickertable <- ticker_lookup(tickerlist, token)

rfdf <- run_agg_query(aggregateQuery, token, as.character(tickertable$Entity), from, to)
browser()
rfdf <- merge(tickertable, rfdf)
rfdf <- with(rfdf, rfdf[order(Day,Entity),])

#Now do something fun with the data!
aapldf <- subset(rfdf, Ticker=="AAPL")
with(aapldf, plot(Day, Count, type="l", main="News Coverage for Apple", sub=paste(from,to), xlab="Day", ylab="Count"))
