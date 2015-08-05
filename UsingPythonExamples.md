# Introduction #

Using the example code in the python-examples directory is straightforward and will allow you to pull both instance and entity information from the [Recorded Future API](http://code.google.com/p/recordedfuture/wiki/RecordedFutureAPI). You'll need [Python 2.6 (or greater)](http://www.python.org/) installed in order to use these scripts. You will also need a Recorded Future API token. To obtain access to a token, please e-mail [sales@recordedfuture.com](mailto:sales@recordedfuture.com).


# Instructions #

## Get the code ##

The easiest way to get the code is to save the following files to the same directory:
  * [instancequery.rfq](http://recordedfuture.googlecode.com/svn/trunk/python-examples/pull_live/instancequery.rfq)
  * [RFAPI.py](http://recordedfuture.googlecode.com/svn/trunk/python-examples/pull_live/RFAPI.py)
  * [pull\_live.py](http://recordedfuture.googlecode.com/svn/trunk/python-examples/pull_live/pull_live.py)
  * [entity\_lookup.py](http://recordedfuture.googlecode.com/svn/trunk/python-examples/pull_live/entity_lookup.py)

You can also [browse for it](http://code.google.com/p/recordedfuture/source/browse/#svn/trunk/python-examples/pull_live) and view the files online for now if you'd prefer.

Alternatively, if you have [Subversion](http://subversion.tigris.org/) installed, you can check out the code as follows:

```
svn checkout http://recordedfuture.googlecode.com/svn/trunk/python-examples/pull_live recordedfuture-read-only 
```

A new directory called "recordedfuture-read-only" will be created in your current working directory and the python files will be included in it.

In any case, you'll want to fire up a terminal (cmd.exe on Windows, Terminal on Mac, or Xterm/gnome-terminal on Linux) and cd to the directory that houses these files for the remainder of this tutorial.


## Run the code ##

Running the code is simple when you've got Python 2.6+ installed. We'll go over the two types of queries separately. For more options to parameterize the query, you can run:
```
python pull_live.py --help
```
or
```
python entity_lookup.py --help
```

### Entity Queries ###
An entity query will look up information about entities in our system. This will help you obtain entity IDs for later queries to the system. For instance, if you want to look up the entity id for "Chevy Chase", you could run something like the following:
```
python entity_lookup.py -t MYTOKEN --type=Person --name="Chevy Chase"
```

Which yields:
```
Id,Name,Type,Hits,Momentum,Attributes
B_asX,Chevy Chase,Person,3950,0.0010537690652378975,birth:1943-10-08|gender:male
```

## Other examples ##
Top 20 commodities in the system.
```
python entity_lookup.py -t MYTOKEN --type=Commodity --top=20
```

Top 50 entities with "Illinois" in the name:
```
python entity_lookup.py -t MYTOKEN --freetext="Illinois" --top=50
```

Look up the entity with the id "B\_LyO" (Apple):
```
python entity_lookup.py -t MYTOKEN--id="B_LyO"
```

You can also specify types, names, or ids in a list from a file, with values one-per-line with the arguments "typefile", "namefile", and "idfile", respectively.


### Instance Queries ###
An instance query pulls information about any occurrences of an entity or event from our database, subject to the constraints of the query itself. If, for instance, you only want to see instances published in a particular date range, you will set that in the query. By default, our query **instancequery.rfq** is set up to pull all occurrences of a list of entities and events (identified by an RF ID) over a user-specified date range. The list of entities is provided in the query itself, but may be provided in a separate file. That file should contain entity ids, one per line, for which the user wants to see entity occurrences and event instances. A sample file **idfile.txt** is provided in the example directory. IDs can be specified from this file with the option "-i idfile.txt".

To run the example instance query which pulls everything related to the entities listed in instancequery.rfq you'll do the following:
```
python pull_live.py -t MYTOKEN --min 2012-08-15 --max 2012-08-20 -p instancequery.rfq > output_file.csv
```

MYTOKEN will be substituted with your API Token. The fifth and sixth arguments above are the date range over which you want to run the query. Query ouput will be placed in the file **output\_file.csv** and you should see something like this in your terminal - this is the fully parameterized query you are executing against the API:
```
{
  "instance": {
    "attributes": {
      "entity": {
        "id": "B_Ggm"
      }
    }, 
    "document": {
      "published": {
        "max": "2012-08-20", 
        "min": "2012-08-15"
      }
    }, 
    "limit": 20000
  }, 
  "token": "MYTOKEN"
}

```


## Examine the output ##

### Instance Query Output ###
Some lines of the instance query output should look something like this:
```
id,momentum,positive,negative,canonical.id,type,document.id,document.published,document.downloaded,start,stop,document.url,document.title,document.sourceId.id,document.sourceId.name,document.sourceId.media_type,document.sourceId.topic,document.sourceId.country,fragment,attributes
GP8HngAGiYj,0.00208338366054,0.0,0.0,GI-LKYw3RgP,CoOccurrence,JP2_CI,2012-08-17T12:30:24.000Z,2012-08-17T12:34:06.930Z,2012-08-17T12:30:24.000Z,2012-08-17T12:30:24.000Z,http://theaviationist.com/2012/08/17/gunship-releasing-flares/,Video shows Syrian Mil Mi-25 gunship releasing flares. A sign that rebels got their hands on MANPADS?,I8K-8k,The Aviationist,Blog,Geopolitical,United States of America,"Lockheed Martin, Boeing, Honeywell and Pratt & Whitney sued by F-22 pilot's widow.","entities:Pratt & Whitney,F-22,Honeywell International Inc,Boeing,Lockheed Martin||positive:0.0||general_positive:0.0||general_negative:0.47368422||negative:0.0"
GP7pV6ABCxu,0.075499758726,0.0,0.0,B_Ggm,EntityOccurrence,JPugEC,2012-08-16T02:03:38.000Z,2012-08-16T02:03:40.260Z,2011-01-01T00:00:00.000Z,2011-12-31T23:59:59.000Z,http://feeds.bizjournals.com/~r/vertical_30/~3/h2SDu6QnxXE/hypersonic-boeing-waverider-fails.html,Hypersonic Boeing Waverider fails after six seconds,C11,Bizjournals.com,Niche,,United States of America,"The Waverider is a collaboration between Boeing and Pratt & Whitney Rocketdyne, and the Air Force Research Laboratory and Defense Advanced Research Projects Agency (DARPA).","positive:0.0||negative:0.0||entity:Boeing||general_negative:0.0||inherited_locations:Huntington Beach,California,Ohio||general_positive:0.0||document_category:Disaster_Accident"
GP7pV6ABCxt,0.075499758726,0.0,0.0,B_Ggm,EntityOccurrence,JPugEC,2012-08-16T02:03:38.000Z,2012-08-16T02:03:40.260Z,2010-01-01T00:00:00.000Z,2010-12-31T23:59:59.000Z,http://feeds.bizjournals.com/~r/vertical_30/~3/h2SDu6QnxXE/hypersonic-boeing-waverider-fails.html,Hypersonic Boeing Waverider fails after six seconds,C11,Bizjournals.com,Niche,,United States of America,"The Waverider is a collaboration between Boeing and Pratt & Whitney Rocketdyne, and the Air Force Research Laboratory and Defense Advanced Research Projects Agency (DARPA).","positive:0.0||negative:0.0||entity:Boeing||general_negative:0.0||inherited_locations:Ohio,California,Huntington Beach||general_positive:0.0||document_category:Disaster_Accident"
GP7pV6ABCxs,0.075499758726,0.0,0.0,B_Ggm,EntityOccurrence,JPugEC,2012-08-16T02:03:38.000Z,2012-08-16T02:03:40.260Z,2012-08-15T00:00:00.000Z,2012-08-15T23:59:59.000Z,http://feeds.bizjournals.com/~r/vertical_30/~3/h2SDu6QnxXE/hypersonic-boeing-waverider-fails.html,Hypersonic Boeing Waverider fails after six seconds,C11,Bizjournals.com,Niche,,United States of America,"Steve Wilhelm Staff Writer- Puget Sound Business Journal Email The Boeing-built hypersonic Waverider, which was to have traveled at six times the speed of sound, failed in a test Wednesday.",positive:0.0||negative:0.0||entity:Boeing||general_negative:0.0||general_positive:0.0||document_category:Disaster_Accident
....
```

This file is a csv file, with column headings at the top. It should be pretty straightforward to open this in Excel or read it in with R's read.csv() command or python's csv module.


## Modify the queries ##

Users will likely want to try running their own queries, and the neat thing about the JSON query API is how flexible it is. You can query the data in the Recorded Future database from all sorts of directions. Changing dates and IDs really just scratches the surface.

Before modifying these queries, we recommend reading [our API documentation](http://www.recordedfuture.com/api/home/). There you will find what type of data you can ask for and what the various metadata fields in the results mean.

## Direct access to the API ##

In case you want to integrate the Recorded Future API into custom applications then some example client code can be found in [RFAPI.py](http://recordedfuture.googlecode.com/svn/trunk/python-examples/pull_live/RFAPI.py).