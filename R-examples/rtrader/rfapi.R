library(RJSONIO)
library(RCurl)

url <- 'http://api.recordedfuture.com/ws/rfq/instances?q='

load_query <- function(filename) {
	f <- file(filename, "r")
	lines <- paste(readLines(f), collapse='\n')
	close(f)
	fromJSON(lines)
	
}

run_agg_query <- function(q) {
	jsonq <- toJSON(q)
	opts <- curlOptions(header = FALSE, connecttimeout = 0)
	
	res <- getBinaryURL(paste(url,curlEscape(jsonq), sep=''), .opts = opts)
	res <- fromJSON(rawToChar(res))
	
	if(res$status == "SUCCESS")
	{
		con <- textConnection(res$aggregates, "r")
		agg <- read.csv(con)
		close(con)
		return(agg)
	}
	res
}

run_query <- function(q) {
    jsonq <-gsub(" ", "", gsub("\\n", "", toJSON(q)))
	opts <- curlOptions(header = FALSE, connecttimeout = 0)
	
	res <- getBinaryURL(paste(url,curlEscape(jsonq), sep=''), .opts = opts)
	res <- fromJSON(rawToChar(res))

	res
}
