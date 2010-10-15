#run these commands just once to install the libraries on your machine
#install.packages("rjson")
#install.packages("RCurl")
#install.packages("fImport")

library(RCurl)
library(rjson)
library(fImport)
token<-"Your Token Here"
url <- 'http://api.recordedfuture.com/ws/rfq/instances?q='

aggregateQuery<-'{
 "aggregate_raw": {
   "document": {"published": {"min": "2009-01-01", "max": "2009-09-30"}}
 },
 "output": {
   "fields": ["momentum", "count", "positive", "negative"],
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
        "entity_details":{"Company": [ "tickers"]}
    }
}'



run.query <- function(q) {
    jsonq = toJSON(q)
    opts = curlOptions(header = FALSE, connecttimeout = 0)
    res <- getBinaryURL(paste(url,curlEscape(jsonq), sep=''), .opts = opts)
    res <- fromJSON(rawToChar(res))
    res
}

getTickerId<-function(ticker) {
    query<-fromJSON(entityQuery)
    query$token<-token
    query$entity$attributes$string<-ticker
    res<-run.query(query)
    res$entities
}

getRFmetrics<-function(ticker){
    query<-fromJSON(aggregateQuery)
    query$token<-token
    rfid<-getTickerId(ticker)
    query$aggregate_raw$entity$id<-rfid
    res<-run.query(query)
    if(res$status == "SUCCESS" & nchar(res$aggregates)>0)
    {
        con <- textConnection(res$aggregates, "r")
        agg <- read.csv(con,head=T,as.is=T)
        close(con)
                agg$Ticker<-ticker
        agg<-agg[order(agg$Day),]
        return(agg)
    } else {
        return(NULL)
    }
}

createDataSet<-function(ticker){
    res<-getRFmetrics(ticker)
    res$sentiment.difference<- - res$Negative
    res$weighted.pos <- res$Positive * res$Momentum
    res$weighted.neg <- res$Negative * res$Momentum
    marketData<-as.data.frame(yahooSeries(ticker,from="2009-01-01",to="2010-09-30"))
    colnames(marketData)<-gsub(paste(ticker,".",sep=""),"",colnames(marketData))
    marketData$returns<-c(returns(marketData$Adj.Close,method="continuous")[-1],NA)
    spy<-as.data.frame(yahooSeries("SPY",from="2009-01-01",to="2010-09-30"))
    out<-merge(res,marketData,all.x=T,by.x=2,by.y=0)
    spy$spy.returns<-c(returns(spy$SPY.Adj.Close,method="continuous")[-1],NA)
    out<-merge(out,spy,all.x=T,by.x="Day",by.y=0)
    out$marketAdjustedReturns<-out$returns - out$spy.returns
    out<-cbind(out,weekday=as.character(dayOfWeek(as.timeDate(out$Day))))
    out
}

out<-createDataSet("AMZN")
out<-out[!(out$weekday=="Mon"),]
out<-out[!(out$weekday=="Sat"),]
out<-out[!(out$weekday=="Sun"),]
tail(out)
model.fit<-lm(marketAdjustedReturns~Momentum+Positive+Negative+weighted.pos+weighted.neg,data=out)
summary(model.fit)