source('rfapi.R')

#Load up a previously saved template query.
query <- load_query('aggquery.rfq')

#Set my API token so that the service yields results.
query$token = YOURTOKEN
#query$token = paste(Sys.getenv('RFTOKEN'))

#You can change the date range like this:
query$aggregate$document$published$min = "2010-02-05"
query$aggregate$document$published$max = "2010-02-06"

#And set a list of tickers to query for like this:
tickerlist <- c('AAPL', 'MSFT', 'GOOG')
query$aggregate$entity$attributes$string = tickerlist

#Run the query (this will probably take a few minutes)
rfdf <- run_query(query)

#Now do something fun with the data!

#plot(as.Date(rfdf$Day),  rfdf$Count, type="l", main="News Coverage for Apple", sub="2010", xlab="Day", ylab="Count")
