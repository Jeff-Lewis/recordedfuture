library(RJSONIO)
library(RCurl)

url <- 'http://api.recordedfuture.com/ws/rfq/instances?q='

f <- file("aggquery.rfq", "r")
lines <- paste(readLines(f), collapse='\n')
close(f)

query <- fromJSON(lines)
query$token = 'K3IfmhWl'

run_query <- function(q) {
	jsonq = toJSON(q)
	opts = curlOptions(header = FALSE)
	
	res <- getBinaryURL(paste(url,curlEscape(jsonq), sep=''), .opts = opts)
	res <- fromJSON(rawToChar(res))
	
	if(res$status == "SUCCESS")
	{
		f <- file("tmp.txt", "w")
		cat(res$aggregates, file=f)
		close(f)
		return(read.csv("tmp.txt"))
	}
	res
}