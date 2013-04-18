library(rjson)
library(RCurl)
library(plyr)

url <- 'http://api.recordedfuture.com/query'

aggregateQuery<-'{
 "aggregate": {
   "document": {"published": {"min": "2009-01-01", "max": "2009-09-30"}}
 },
 "output": {
   "format": "csv"
 }
}'


entityQuery<-'{
  "entity": {
    "attributes": {
      "name": "external_links.bloomberg.id",
      "exists": true
    },
    "type":"Company",
    "limit":10000
  }
}'


load_query <- function(filename) {
    f <- file(filename, "r")
    lines <- paste(readLines(f), collapse='\n')
    close(f)
    
    fromJSON(lines)
}

run_agg_query <- function(query, token, ids, from, to, name="attention_by_half_hour") {
    query <- fromJSON(query)
    query$token <- token
    
    #Set query parameters
    query$aggregate$document$published$min <- from
    query$aggregate$document$published$max <- to
    query$aggregate$entity$id <- ids
    query$aggregate$name <- name
    
    opts <- curlOptions(header = FALSE, connecttimeout = 0)
    res <- postForm(url,q=toJSON(query), style="post", .opts = opts)

    con <- textConnection(res, "r")
    agg <- read.csv(con, as.is=T)
    close(con)

    #Switch up data types on columns from defaults.
    agg$Time <- as.POSIXct(agg$Time, tz="UTC")

    return(with(agg, agg[order(Time),]))
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

bloomberg_lookup <- function(token) {
    query <- fromJSON(entityQuery)
    query$token <- token
    res <- run_query(query)
    
    if(res$status == "SUCCESS") {
        ed <- res$entity_details
        
        #Convert the results to a data.frame
        entity_table <- as.data.frame(t(rbind(mapply(function(y, x) cbind(y, as.character(x$external_links$bloomberg$id[[1]]), x$name), names(ed), ed))))
        colnames(entity_table) <- c("Entity","Bloomberg.ID","Name")
        entity_table$Entity <- as.character(entity_table$Entity)
        entity_table$Bloomberg.ID <- as.character(entity_table$Bloomberg.ID)

        return(entity_table)
    }
    res
}


run_agg_query_bbg <- function(from, to, token) {
    rf_bbgidmap <- bloomberg_lookup(token)

    #Execute query and merge in ticker info.
    resdf <- run_agg_query(aggregateQuery, token, rf_bbgidmap$Entity, from, to)
    if(class(resdf) == "data.frame") {
        compdf <- merge(rf_bbgidmap, resdf, by='Entity')
    
        return(with(compdf, compdf[order(Time, Entity),]))
    }
    resdf
}

