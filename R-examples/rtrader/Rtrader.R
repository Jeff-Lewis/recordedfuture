#This is a simple "live" paper trading application written in R utilizing the Recorded Future API.
#We generate paper "orders" by watching for breaking news about S&P 500 companies.
#If we see that this is the "first" occurrence of a particular event, and news matches our screening
#criteria, we "buy" with the current stock price according to Google. We then "sell" 
#at the end of the day. We then store a data frame with profits per trade in a matrix.
#If this is the first occurrence of a particular piece of

source('rfapi.R')
library(RCurl)
library(RJSONIO)

#Gets a stock quote from google finance, returns last price as a float.
get_quote <- function(x) {
    url <- "http://www.google.com/finance/info?client=ig&q="
    res <- getURL(paste(url, x, sep=''))

    x <- tryCatch(fromJSON(substring(res, 5)), error = function(e) NA)
    if(is.na(x)) {
        return(x)
    }

    x[[1]]$l
}

#Converts a time from Recorded Future standard UTC format to local time in string of form HH-MM-SS.
from_utc <- function(time) {
    format(as.POSIXct(time, format="%Y-%m-%dT%H:%M:%S.000Z", tz="UTC"), tz="US/Eastern", format="%H-%M-%S")
}

#Converts a time from a string of form HH-MM-SS to Recorded Future standard UTC time. Assumes current date for daylight savings rules.
to_utc <- function(time) {
    format(as.POSIXct(time, format="%H-%M-%S", tz="US/Eastern"), tz="UTC", format="%Y-%m-%dT%H:%M:%S.000Z")
}

#Load up a previously saved template query.
query <- load_query('entquery.rfq')

#Initialize our trade tables
bought <- list()
trades <- list()

#Set my API token so that the service yields results.
#query$token = YOURTOKEN
query$token = paste(Sys.getenv('RFTOKEN'))

#What time do we hold until?
nexttime = Sys.time()
lasttime = nexttime - 300
closingtime = strptime(paste(Sys.Date(), "16:00:00"), format = "%Y-%m-%d %H:%M:%S")
print("starting")

#Do this every five minutes until close!
while (as.numeric(closingtime - lasttime, units = "secs") > 0 )  {
    query$instance$document$analyzed$min = to_utc(strftime(lasttime, "%H-%M-%S"))
    query$instance$document$analyzed$max = to_utc(strftime(nexttime, "%H-%M-%S"))
    
    #Run the query (this will probably take a few seconds)
    rflst <- run_query(query)

    #print(rflst)
    #Iterate through each returned instance.
    #If trade criteria has been matched, generate a trade!
    for(inst in rflst$instances) {
        if(is.null(inst$relevance)) { inst$relevance <- 0 }
        if(is.null(inst$positive)) { inst$positive <- 0 }
        if(is.null(inst$negative)) { inst$negative <- 0 }
        
        if(inst$relevance > 50 & inst$positive > 0.1 & inst$negative < 0.1) {
            entity <- rflst$entities[[as.character(inst$attributes$entity)]]
            if(is.null(entity$tickers)) { entity$tickers <- entity$name }
            if(entity$momentum > 0.005 & !(entity$tickers %in% bought)) {
                print(paste("BUY", entity$tickers)) 
                bought <- append(bought, entity$tickers)
                tradetime <- strftime(Sys.time(), "%H:%M:%S")
                trades <- append(trades, list(c(entity$tickers, tradetime, get_quote(entity$tickers))))
            }
        }
    }
    
    #Wait if necessary.
    lasttime <- nexttime
    nexttime <- nexttime + 300
    delay <- as.numeric(nexttime - Sys.time(), units="secs")
    if(delay > 0) {
        Sys.sleep(delay)
    }
}
print("ending")

#At close, get closing prices.
trades <- lapply(trades, function(x) { append(x, get_quote(x[1])) })
trades <- as.data.frame(do.call(rbind, lapply(trades, rbind)))
colnames(trades) <- c("ticker", "tt", "price", "close")
trades$price <- as.numeric(as.character(trades$price))
trades$close <- as.numeric(as.character(trades$price))


#Now calculate returns
trades$returns <- (trades$close - trades$price)/trades$price

print("Return summary:")
print(summary(trades$returns))