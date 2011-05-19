library(rjson)
library(RCurl)
library(plyr)

url <- 'http://api.recordedfuture.com/ws/rfq/instances'

aggregateQuery<-'{
 "aggregate_raw": {
   "document": {"published": {"min": "2009-01-01", "max": "2009-09-30"}}
 },
 "output": {
   "fields": ["momentum", "count", "positive", "negative"],
   "format": "csv"
 }
}'

aggregateSourceQuery<-'{
 "aggregate_raw": {
   "document": {"published": {"min": "2009-01-01", "max": "2009-09-30"}}
 },
 "output": {
   "fields": ["source","momentum", "count", "positive", "negative"],
   "format": "csv"
 }
}'

entityQuery<-'{
    "entity": {
        "type": "Company",
        "attributes": {
            "name": "tickers"
        }
    },
    "output": {
        "fields":["id","attributes"],
        "entity_details":{"Company": ["gics","tickers"]}
    }
}'


load_query <- function(filename) {
	f <- file(filename, "r")
	lines <- paste(readLines(f), collapse='\n')
	close(f)
	
	fromJSON(lines)
}

run_agg_query <- function(query, token, ids, from, to) {
    query <- fromJSON(query)
    query$token <- token
    
    #Set query parameters
    query$aggregate_raw$document$published$min <- from
    query$aggregate_raw$document$published$max <- to
    query$aggregate_raw$entity$id = as.integer(as.character(ids))
    
	opts <- curlOptions(header = FALSE, connecttimeout = 0)
	
	res <- postForm(url,q=toJSON(query), style="post", .opts = opts)

	res <- fromJSON(res)
	
	if(res$status == "SUCCESS") {
		con <- textConnection(res$aggregates, "r")
		agg <- read.csv(con)
		close(con)
		
        #Switch up data types on columns from defaults.
        agg$Day <- as.Date(as.character(agg$Day))
        agg$Entity <- as.character(agg$Entity)
		
		return(with(agg, agg[order(Day),]))
	}

	res
}

getTickerId<-function(ticker, token) {
    query<-fromJSON(entityQuery)
    query$token<-token
    query$entity$attributes$string<-ticker
    res<-run_query(query)
    
    res$entities
}


run_query <- function(q) {
	opts <- curlOptions(header = FALSE, connecttimeout = 0)

	res <- postForm(url,q=toJSON(q), style="post", .opts = opts)
	res <- fromJSON(res)

	res
}

ticker_lookup <- function(tickers, token) {
    query <- fromJSON(entityQuery)
    query$token <- token
    query$entity$attributes$string <- tickers
    res <- run_query(query)
    
    if(res$status == "SUCCESS") {
        ed <- res$entity_details
        
        #Convert the results to a data.frame
        entity_table <- as.data.frame(t(rbind(mapply(function(y, x) cbind(y, x$tickers, x$momentum), names(ed), ed))))
        colnames(entity_table) <- c("Entity","Ticker","Momentum")
        entity_table$Momentum <- as.numeric(as.character(entity_table$Momentum))
        
        #This function filters by top momentum for each entity.
        #Idea being the entity with highest momentum is most likely the "correct" one.
        entity_table <- ddply(entity_table, .(Ticker), function(x) x[x$Momentum == max(x$Momentum),][1])

        return(entity_table[entity_table$Ticker %in% tickers,])
    }
    res
}


run_agg_query_by_ticker <- function(tickers, from, to, token) {
    rf_tickermap <- ticker_lookup(tickers, token)

    #Execute query and merge in ticker info.
    resdf <- run_agg_query(aggregateQuery, token, rf_tickermap$Entity, from, to)
    if(class(resdf) == "data.frame") {
        compdf <- merge(rf_tickermap[,c('Entity','Ticker')], resdf, by='Entity')
        compdf$Ticker <- as.character(compdf$Ticker)
    
        return(with(compdf, compdf[order(Ticker, Day),]))
    }
    resdf
}

