library(fImport)
library(fTrading)
library(PerformanceAnalytics)
library(reshape)

source("rfapi.R")

#Configure portfolio parameters here.
tickerfile <- "sp500-tickers.txt" #Name of a file that contains the tickers I'm interested in.
from <- "2009-01-01" #Start date.
to <- "2011-02-01" #End date.
token <- paste(Sys.getenv('RFTOKEN')) #My Recorded Future token.

#Define a function which pulls market data and computes leading 1-day returns.
pull_market_data <- function(tickerlist, from, to, doparallel=FALSE, nprocs=5) {

	#This function pulls each individual name's returns.
	pull_ticker_info <- function(ticker, from, to) {
		tryCatch(ts <- cbind(yahooSeries(ticker, from, to)), error=function(ex) return(NULL))

		if(class(ts) != "timeSeries") return(NULL)
		
		colnames(ts) <- c("Open","High","Low","Close","Volume","Adj.Close")
		
		#Compute next day's returns.
		df <- as.data.frame(cbind(ts, Returns=lag(returns(ts[,'Close']), -1)))
		
		df$Day <- as.Date(rownames(df))
		df$Ticker <- ticker
		df
	}
	
	#Merge the reseults together and return. The doparallel option will speed this up, but only
	#on MacOS or Linux.
	if(doparallel) {
	    require(doMC)
	    registerDoMC(nprocs)
	    df <- foreach(t=tickerlist, .combine='rbind') %dopar% pull_ticker_info(t, from=from, to=to)
	}
	else { 
	    df <- do.call("rbind", lapply(tickerlist, FUN=pull_ticker_info, from=from, to=to))
	}
	
	rownames(df) <- NULL
	df
}

#This function will be used to compute deciles later on. It is not robust to low-variance data.
decile <- function(x) { cut(x,quantile(x,(0:10)/10,na.rm=TRUE),labels=FALSE,include.lowest=TRUE) }

#Expects a data.frame with a column called "Day", one called "Decile", and one called "Returns"
plot_decile_performance <- function(df, benchmark) {
	
	#Compute aggregate returns by decile.
	agg <- with(df, aggregate(list(Returns=Returns), by=list(Day=Day,Decile=Decile), FUN=mean, na.rm=TRUE))
	perfdf <- cast(agg, Day ~ Decile, value='Returns')
    perfdf <- as.data.frame(perfdf)
	rownames(perfdf) <- perfdf[,1]
	perfdf <- perfdf[,-1]

    #Convert and add in benchmark returns.
    rownames(benchmark) <- benchmark$Day
    benchname <- benchmark$Ticker[1]
    benchmark <- benchmark[,'Returns',drop=F]
    colnames(benchmark) <- benchname
    
    colnames(perfdf) <- paste("Decile", colnames(perfdf))
    
    perfdf <- cbind(perfdf, benchmark)
	
	chart.CumReturns(perfdf, legend.loc="topleft", main="Performance of Recorded Future Factor Deciles", colorset=rich12equal)
}


#Load up tickers to run against.
tickerlist <- scan(tickerfile, what='character')

#Pull market data for ticker list and date range.
market_data <- pull_market_data(tickerlist, from, to)
bench_data <- pull_market_data(list("SPY"), from, to)

#Pull Recorded Future data for ticker list and date range.
rf_data <- run_agg_query_by_ticker(tickerlist, from, to, token)

#Subset the Recorded Future Data to include only days I'm interested in.
rf_data <- with(rf_data, rf_data[Positive - Negative > 0,])

#You can compute your own metrics on the Recorded Future data here.
rf_data$logCount <- log(rf_data$Count)

#Merge the Recorded Future Data with the Market Data
merged_data <- merge(rf_data, market_data, by=c("Ticker","Day"))

#Calculate deciles of a variable of interest.
merged_data <- ddply(merged_data, .(Day), transform, Decile=decile(Momentum))

#Produce a plot of decile performance.
plot_decile_performance(merged_data, bench_data)


