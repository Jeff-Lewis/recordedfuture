# Recorded Future API #

## version 2.0.0 ##

Contents

**1**[version2.0.0](#version_2.0.0.md)<br>
<b>2</b><a href='#Introduction.md'>Introduction</a><br>
<font color='white'><code>  .  </code></font><b>2.1</b><a href='#Quick_Start:_Creating_Requests.md'>Quick Start: Creating Requests</a><br>
<b>3</b><a href='#Input_and_Output_in_JSON.md'>Input and Output in JSON</a><br>
<b>4</b><a href='#Entity_query_specification.md'>Entity query specification</a><br>
<b>5</b><a href='#Source_query_specification.md'>Source query specification</a><br>
<b>6</b><a href='#Instance_query_specification.md'>Instance query specification</a><br>
<font color='white'><code>  .  </code></font><b>4.1</b><a href='#Matching_on_instance_identity_or_type.md'>Matching on instance identity or type</a><br>
<font color='white'><code>  .  </code></font><b>4.2</b><a href='#Matching_on_instance_time.md'>Matching on instance time</a><br>
<font color='white'><code>  .  </code></font><b>4.3</b><a href='#Matching_on_the_canonical_item.md'>Matching on the canonical item</a><br>
<font color='white'><code>  .  </code></font><b>4.4</b><a href='#Matching_on_attributes.md'>Matching on attributes</a><br>
<font color='white'><code>  .  </code></font><b>4.5</b><a href='#Matching_on_document_and_source_aspects.md'>Matching on document and source aspects</a><br>
<font color='white'><code>  .  </code></font><b>4.6</b><a href='#Matching_on_free_text.md'>Matching on free text features</a><br>
<font color='white'><code>  .  </code></font><b>4.7</b><a href='#Exclusion.md'>Exclusion</a><br>
<font color='white'><code>  .  </code></font><b>4.8</b><a href='#Response_specification.md'>Response specification</a><br>
<b>7</b><a href='#Output_fields.md'>Output fields</a><br>
<b>8</b><a href='#Aggregate_Queries.md'>Aggregate Queries</a><br>
<b>9</b><a href='#On_the_fly_aggregation.md'>On the fly aggregation</a><br>
<b>10</b><a href='#Paging_instance_results.md'>Paging Instance Results</a><br>
<b>11</b><a href='#Using_the_Recorded_Future_API_with_R.md'>Using the Recorded Future API with R</a><br>
<b>12</b><a href='#Using_the_Recorded_Future_API_with_Python.md'>Using the Recorded Future API with Python</a><br>
<b>13</b><a href='#Entity_and_Event_Types.md'>Entity and Event Types</a><br>
<font color='white'><code>  .  </code></font><b>10.1</b><a href='#Entity_Types.md'>Entity Types</a><br>
<font color='white'><code>  .  </code></font><b>10.2</b><a href='#Event_Types.md'>Event Types</a><br>

<h2>Introduction</h2>

Recorded Future’s API enables you to build analytic applications and perform analysis which is aware of events happening around the globe 24x7. You can perform queries and receive results from the Recorded Future Temporal Analytics™ Engine across a vast set of events, entities, and time points spanning from the far past into the future.<br>
<br>
Your application can come alive with real-time access into the Recorded Future engine, completely aware of events as they unfold around the world. Your analysis of, for example, financial markets can be made aware of events involving companies, people, products, etc. and historical archives allow you to extensively backtest results.<br>
<br>
Sample applications and analysis built/done with the Recorded Future API include:<br>
<br>
<ul><li>Interactive dashboards of global events<br>
</li><li>Google earth overlay of global events<br>
</li><li>Backtesting whether FT Alphaville (high profile financial blog) is "better" than general news in predicting stock returns<br>
</li><li>Backtesting news-based trading strategies for sources of uncorrelated alpha</li></ul>

To access Recorded Future through the API:<br>
<br>
<ol><li>Request a Recorded Future API token.<br>
</li><li>Create a structured JSON string that describes the query.<br>
</li><li>Create and submit the associated URL.<br>
</li><li>Retrieve and parse the results.</li></ol>

<h3>Quick Start: Creating Requests</h3>

Queries are sent using HTTPS GET or POST to<br>
<blockquote><a href='https://api.recordedfuture.com/query'>https://api.recordedfuture.com/query</a></blockquote>

Query parameters should be used with the key "q" and a JSON-encoded query object as its value.<br>
<br>
Data will be gzipped with HTTPS content encoding if requested by the client by setting the the HTTPS "Accept-encoding" header to "gzip".<br>
<br>
Queries are expressed in JSON and the returned output is expressed in JSON (by default) or CSV.<br>
<br>
As a quick example, suppose we want to query for the first 100 'Cyber Attack' events associated with the Syrian Electronic Army that were published in January 2015. We can execute the following instance query against Recorded Future's API to do this:<br>
<br>
<pre><code>{<br>
  "instance": {<br>
    "type": ["CyberAttack"],<br>
    "attributes": {<br>
      "entity": {<br>
        "id":"BFHu9W"<br>
      }<br>
    },<br>
    "document": {<br>
      "published": {"min": "2015-01-01", "max": "2015-01-31"}<br>
    },<br>
    "limit": 100<br>
  },<br>
  "token": "TOKEN"<br>
}<br>
</code></pre>


Note: for information on how to retrieve an entity's id -  a unique id created by Recorded Future, which is BFHu9W for the Syrian Electronic Army in this case - see the "Entity query specification" section of this page.<br>
<br>
For this example, the returned result contains a number of fields with information about the event including: the text fragment the event was found in (“French newspaper Le Monde's Twitter account suffers hacking attack”), the document source ("IBTimes UK"), and the document it was found in (the URL that displays the actual document).<br>
<br>
<pre><code>        {<br>
            "id": "GUgYXSAqFHT",<br>
            "type": "CyberAttack",<br>
            "cluster_ids": [<br>
                "C0bYw9girdQ"<br>
            ],<br>
            "start": "2015-01-21T06:21:06.000Z",<br>
            "stop": "2015-01-21T06:21:06.000Z",<br>
            "tagged_fragment": "Signs of &lt;i id=GUgYXSAqFHT&gt;hacking came after 7:00 pm ET, as the logo of the &lt;e id=BFHu9W&gt;Syrian Electronic Army&lt;/e&gt;&lt;/i&gt; was seen in a tweet sent from the official &lt;e id=I2M5pa&gt;Le Monde&lt;/e&gt; account.",<br>
            "fragment": "Signs of hacking came after 7:00 pm ET, as the logo of the Syrian Electronic Army was seen in a tweet sent from the official Le Monde account.",<br>
            "item_fragment": "hacking came after 7:00 pm ET, as the logo of the Syrian Electronic Army",<br>
            "precision": "ms",<br>
            "time_type": "in",<br>
            "document": {<br>
                "id": "M8bkbW",<br>
                "title": "\n\nFrench newspaper Le Monde's Twitter account suffers hacking attack\n",<br>
                "url": "http://www.ibtimes.co.uk/french-newspaper-le-mondes-twitter-account-suffers-hacking-attack-1484357",<br>
                "language": "eng",<br>
                "published": "2015-01-21T06:21:06.000Z",<br>
                "downloaded": "2015-01-21T06:21:23.796Z",<br>
                "indexed": "2015-01-21T06:21:43.120Z",<br>
                "sourceId": {<br>
                    "id": "K3hhZz",<br>
                    "name": "IBTimescouk  Europe",<br>
                    "description": "Europe  Feed",<br>
                    "media_type": "JxSEs2",<br>
                    "country": "United Kingdom",<br>
                    "topic": "JxSEs3"<br>
                }<br>
            },<br>
            "attributes": {<br>
                "indicator": "hacking came after 7:00 pm ET , as the logo of the Syrian Electronic Army",<br>
                "general_negative": 0,<br>
                "function": "id",<br>
                "document_category": "Cyber",<br>
                "canonic_id": "C_1bJjzhPM5",<br>
                "extended_entities": [<br>
                    "0f-N9",<br>
                    "C3Oxl8"<br>
                ],<br>
                "analyzed": "2015-01-21T06:21:43.031Z",<br>
                "attacker": "BFHu9W",<br>
                "positive": 0,<br>
                "sentiments": {<br>
                    "general_positive": 0,<br>
                    "violence": 0,<br>
                    "activism": 0,<br>
                    "general_negative": 0,<br>
                    "negative": 0,<br>
                    "positive": 0,<br>
                    "profanity": 0<br>
                },<br>
                "violence": 0,<br>
                "document_external_id": "http://www.ibtimes.co.uk/french-newspaper-le-mondes-twitter-account-suffers-hacking-attack-1484357",<br>
                "binning_id": "C_1bJjzhPM5",<br>
                "entities": [<br>
                    "BFHu9W",<br>
                    "I2M5pa"<br>
                ],<br>
                "general_positive": 0,<br>
                "hits": 0,<br>
                "topics": [<br>
                    "KPzZCG",<br>
                    "KPzZAE"<br>
                ],<br>
                "negative": 0,<br>
                "fragment_count": 1<br>
            }<br>
        }<br>
</code></pre>


Entities – the people, companies, organizations, and places of the Recorded Future who/where list – are created on-demand as they are harvested by a query. Once an entity is defined, all references to that entity are defined as entity instances that point to the underlying canonical entity. Entities are returned in a separate structure, to avoid duplication, and in the instances only references to the entities are present, using an opaque identifier.<br>
<br>
This documentation will go into detail on how to query entities, sources, and instances within the Recorded Future system.<br>
<br>
<h2>Input and Output in JSON</h2>

The Recorded Future API supports JSON as the input and output format. For a detailed JSON specification, visit Douglas Crockford’s site <a href='http://www.json.org/'>JSON.org</a>, paying particular attention to <a href='http://tools.ietf.org/html/rfc4627'>RFC 4627</a>. This section provides a short excerpt.<br>
<br>
<b>Tip</b>: If you are using <a href='http://www.r-project.org'>R</a>, you don’t need to worry about formatting JSON input or parsing JSON output. R packages manage input and output for you. See “Using the Recorded Future API with R” to learn more.<br>
<br>
<b>JSON</b> (JavaScript Object Notation) is a lightweight data-interchange format. It is easy for humans to read and write. It is easy for machines to parse and generate. JSON is a text format that is completely language independent but uses conventions that are familiar to programmers of the C-family of languages, including C, C++, C#, Java, JavaScript, Perl, Python, and many others. These properties make JSON an ideal data-interchange language.<br>
JSON is built on two structures:<br>
<br>
<ul><li>A collection of name/value pairs. In various languages, this is realized as an <i>object</i>, record, struct, dictionary, hash table, keyed list, or associative array.<br>
</li><li>An ordered list of values. In most languages, this is realized as an <i>array</i>, vector, list, or sequence.</li></ul>

These are universal data structures. Virtually all modern programming languages support them in one form or another. It makes sense that a data format that is interchangeable with programming languages also be based on these structures.<br>
In JSON, which always uses Unicode encoding, they take on these forms:<br>
<br>
<ul><li>An <i>object</i> is an unordered set of name/value pairs. An object begins with { <font size='1'>(left brace)</font> and ends with } <font size='1'>(right brace)</font>. Each name is followed by : <font size='1'>(colon)</font> and the name/value pairs are separated by , <font size='1'>(comma)</font>.<br>
</li><li>An <i>array</i> is an ordered collection of values. An array begins with <code>[</code> <font size='1'>(left bracket)</font> and ends with <code>]</code> <font size='1'>(right bracket)</font>. Values are separated by , <font size='1'>(comma)</font>.<br>
</li><li>A <i>value</i> can be a <i>string</i> in double quotes, or a <i>number</i>, or true or false or null, or an <i>object</i> or an <i>array</i>. These structures can be nested.<br>
</li><li>A <i>string</i> is a collection of zero or more Unicode characters, wrapped in double quotes, using backslash escapes. A character is represented as a single character string. A string is very much like a C or Java string.<br>
</li><li>A <i>number</i> is very much like a C or Java number, except that the octal and hexadecimal formats are not used.<br>
</li><li>Whitespace can be inserted between any pair of tokens.</li></ul>


<h2>Entity query specification</h2>

Entity queries allow users to look up an identifier for an entity in the Recorded Future system. You can think of entities as nouns: the people, places, and things we want to find information about. We support entity lookup by name or freetext search. When searching for an entity using the 'name' field the exact string pattern will be searched for, whereas a search using the freetext field is not exact. The retrieved entity IDs are used to query the system for information related to specific entities.<br>
<br>
An entity query has the following structure:<br>
<br>
<pre><code>{<br>
  "entity": &lt;entity spec&gt;,<br>
  "token" &lt;string&gt;<br>
}<br>
</code></pre>

The <i>entity spec</i> section specifies conditions that must be true for all returned entities.<br>
<br>
<pre><code>"entity": {<br>
  "id": [string] (optional),<br>
  "type": [string] (optional),<br>
  "name": [string] (optional),<br>
  "created": [string] (optional),<br>
  "attributes": [string] (optional),<br>
  "freetext": &lt;freetext spec&gt; (optional),<br>
  "limit": [integer] (optional - default is 100)<br>
}<br>
</code></pre>

As an example, the following query will look up Recorded Future's entity information for Edward Snowden:<br>
<br>
<pre><code>{<br>
  "entity": {<br>
    "type": "Person",<br>
    "name": "Edward Snowden"<br>
  },<br>
  "token": "TOKEN"<br>
}<br>
</code></pre>

The response for this entity query will be:<br>
<br>
<pre><code>{<br>
    "count": {<br>
        "entities": {<br>
            "returned": 1,<br>
            "total": 1<br>
        }<br>
    },<br>
    "next_page_start": "1",<br>
    "status": "SUCCESS",<br>
    "entities": [<br>
        "J5K1uB"<br>
    ],<br>
    "entity_details": {<br>
        "J5K1uB": {<br>
            "name": "Edward Snowden",<br>
            "hits": 3477157,<br>
            "type": "Person",<br>
            "alias": [<br>
                "Сноудене",<br>
                "إدوراد سنودن",<br>
                "ادوارد اسنودن",<br>
                "Edward Joseph Snowden",<br>
                "ادورد سنودن"<br>
            ],<br>
            "curated": 1,<br>
            "gender": "male",<br>
            "id": "J5K1uB"<br>
        }<br>
    }<br>
}<br>
</code></pre>

One key field included in this response is the id. In Recorded Future, a unique id exists for each entity. For Edward Snowden, this id is J5K1uB. This entity id can be used in other queries.<br>
<br>
As another example, suppose we want to query for all entities with Bloomberg IDs. We can use the attribute field to do this:<br>
<br>
<pre><code>{<br>
  "entity": {<br>
    "attributes": {<br>
      "name": "external_links.bloomberg.id",<br>
      "exists": true<br>
    },<br>
    "limit":1000<br>
  },<br>
  "token": "TOKEN"<br>
}<br>
</code></pre>

The returned results will be:<br>
<br>
<pre><code>{<br>
    "count": {<br>
        "entities": {<br>
            "returned": 10,<br>
            "total": 5444<br>
        }<br>
    },<br>
    "next_page_start": "10",<br>
    "status": "SUCCESS",<br>
    "entities": [<br>
        "B_JMt",<br>
        "B_LyO",<br>
        "B_HE4",<br>
        "B_E-a",<br>
        "B_E7B",<br>
        "B_Lho",<br>
        "CANiy",<br>
        "B_IxU",<br>
        "B_FBR",<br>
        "B_XKi"<br>
    ],<br>
    "entity_details": {<br>
        "CANiy": {<br>
            "name": "Sony Corp",<br>
            "hits": 16427818,<br>
            "type": "Company",<br>
            "external_links": {<br>
                "bloomberg": {<br>
                    "id": [<br>
                        "EQ0010136500001000"<br>
                    ]<br>
                }<br>
            },<br>
            ...<br>
<br>
</code></pre>


<h2>Source query specification</h2>

Source queries allow users to look up an identifier for a source in the Recorded Future system. Sources are the sites that information comes from: blogs and news sites, for example. We support entity source by id, name, media type, topic, and country.<br>
<br>
A source query has the following structure:<br>
<br>
<pre><code>{<br>
  "source": &lt;source spec&gt;,<br>
  "token" &lt;string&gt;<br>
}<br>
</code></pre>


The <i>source spec</i> section specifies conditions that must be true for all returned sources.<br>
<br>
<pre><code>"source": {<br>
  "id": [string] (optional),<br>
  "name": [string] (optional),<br>
  "description": [string] (optional),<br>
  "created": [string] (optional - can use min and max boundaries),<br>
  "topic": [string] (optional),<br>
  "media_type": [string] (optional),<br>
  "country": [string] (optional),<br>
  "limit": [integer] (optional - default is 100)<br>
}<br>
</code></pre>

The following query will return source information for 'Information Security' (topic id of KPzZAE) 'Blogs' (media_type id of JxSDuU). The number of results returned is limited to 20:<br>
<br>
<pre><code>{<br>
  "source": {<br>
    "topic": "KPzZAE",<br>
    "media_type": "JxSDuU",<br>
    "limit": 20<br>
  },<br>
  "token": "TOKEN"<br>
}<br>
</code></pre>

The response of this source query will be:<br>
<br>
<pre><code>{<br>
    "status": "SUCCESS",<br>
    "sources": {<br>
        "MkoDs5": {<br>
            "media_type": "JxSDuU",<br>
            "created": "2014-12-21T14:32:20.643Z",<br>
            "name": "HubPages | romantibensky"<br>
        },<br>
        "M2ssv8": {<br>
            "media_type": "JxSDuU",<br>
            "created": "2015-01-14T16:52:36.826Z",<br>
            "name": "BankInvestmentConsultant | Fixed Income"<br>
        },<br>
    ...<br>
}<br>
</code></pre>

Within the returned results will be the source id, a unique identifier in Recorded Future's system. MkoDs5 is the source id for the HubPages | romantibenksy blog. The source id can then be utilized in other queries against Recorded Future's system.<br>
<br>
<h2>Instance query specification</h2>

Instance queries are given as the q parameter in the API URL. They need to be <a href='http://en.wikipedia.org/wiki/URL_encoding'>URL encoded</a>. Within the <a href='#Quick_Start:_Creating_Requests.md'>Quick Start: Creating Requests</a> section of this document we showed an example instance query where we are looking for cyber attack events related to the Syrian Electronic Army in the month of January 2015.<br>
<br>
An instance query has the following structure:<br>
<br>
<pre><code>{<br>
  "instance": &lt;instance spec&gt;,<br>
  "output": &lt;output_spec&gt; (optional)<br>
}<br>
</code></pre>


The <i>instance spec</i> section specifies conditions that must be true for all returned instances.<br>
<br>
<pre><code>"instance": {<br>
    "id": [string],<br>
    "cluster_id" [string],<br>
    "type": [string],<br>
    "start": [string],<br>
    "stop": [string]<br>
    "attributes": attributes-constraints,<br>
    "document": document-constraints,<br>
    "source": source-constraints,<br>
    "freetext": [string],<br>
    "limit": integer<br>
}<br>
</code></pre>

<h3>Matching on instance identity or type</h3>

<i>id</i> matches on instance identifiers. An identifier is a string and is a system-defined identification of the instance. You’ll usually match on instance identifiers only when you’re looking for detailed instance information using identifiers returned in the results of earlier queries. The value of <i>id</i> must be a string or a list of strings. <i>id</i> matches if the instance identifier matches one of the provided identifiers.<br>
<br>
<i>cluster<code>_</code>id</i> matches on an event identifier.<br>
<br>
<i>type</i> matches on the names of the canonical types of instances. The canonical types are the event types and entity types in the system, as described by the system metadata specification. The value of <i>type</i> must be a string or a list of strings. <i>type</i> matches if the name of the canonical type of the instance is one of the supplied instance type names. A list of all current entity and event types is available <a href='#Entity_and_Event_Types.md'>at the end of this document</a>.<br>
<br>
<h3>Matching on instance time</h3>

<i>start</i> specifies the minimum instance start time. The time must be specified as a string with the date format YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.000Z in UTC. It is possible to specify time with only initial portions of the time specification. That is, a timestamp can be specified as "2015-01" to indicate January, 2015 or "2015-01-01 12:00" to indicate noon, UTC on 2015-01-01.<br>
<br>
<i>stop</i> specifies the maximum instance stop time and must be a string formatted according to the same rules as <i>start</i>.<br>
<br>
<h3>Matching on the canonical item</h3>

The canonical parameter matches on aspects of the instance's canonical item. The aspects are specified using the structure:<br>
<br>
<pre><code>"canonical": {<br>
    "id": [string],<br>
    "name": [string]<br>
}<br>
</code></pre>

<i>id</i> matches on canonical identifiers. An identifier is a string, and is a system defined identification of the canonical item. The value must be a string or a list of strings. The value matches if the canonical identifier matches one of the provided identifiers.<br>
<br>
You’ll usually match on canonical identifiers only when you’re looking for detailed instance information using identifiers returned in the results of earlier queries.<br>
<br>
<i>name matches on canonical names. Only canonical entities have names; canonical events do not. The value of</i>name<i>must be a string or a list of strings. The parameter matches if the canonical name identifier matches one of the supplied names.</i>

<h3>Matching on attributes</h3>

The attributes parameter matches on the attributes of the instance. The attributes section is a list of match criteria for attributes, and all entries in the list must match, in order for an instance to match. Attributes are identified by name or by type. Named attributes can be used only if a distinct type constraint has been set in the query, then all attributes of the typed item are available to be referenced by name. Typed attributes match all attributes of an item with that type. The structure of an attribute match is:<br>
<br>
<pre><code>{<br>
  name-or-type,<br>
  value-constraint<br>
}<br>
</code></pre>

The <i>name-or-type</i> part is either "name": <i>attribute-name</i> or "type": <i>type</i>. The <i>value-constraint</i> part is type dependent. Here is the list of different types, and how to match on them:<br>
<br>
<pre><code>"string":  [string]<br>
"int":     [integer]<br>
"float":   [float]<br>
"bool":    [bool]<br>
"entity":  entity-match<br>
</code></pre>

Matching for the string, integer, float, and Boolean are all of the form that a single value or a list of values of the specified type. If a list is supplied, a match is found if any element of the list matches. For entity matches, the structure is a subset of the structure for entity instances, excluding the time and document constraints.<br>
<br>
<pre><code>"entity": {<br>
    "id": [string],<br>
}<br>
</code></pre>

<i>id</i> matches on the canonical entity identifier<br>
<br>
<br>
<h3>Matching on document and source aspects</h3>

<i>document</i> matches on aspects of the document in which the instance was found, or aspects of the source the document was received from. It has the following structure:<br>
<br>
<pre><code>"document": {<br>
    "id": [string],<br>
    "published": time-range,<br>
    "downloaded": time-range,<br>
    "source": source-constraints<br>
}<br>
</code></pre>

<i>id</i> matches on document identifiers. An identifier is a string, and is a system defined identification of the document. The value of the parameter must be an string or a list of strings. The parameter matches if the document identifier matches one of the provided identifiers. You’ll usually match on document identifiers only when you’re looking for detailed instance information using identifiers returned in the results of earlier queries.<br>
<br>
<i>published</i> matches on the publication date of the document. The value is a time-range structure:<br>
<br>
<pre><code>{<br>
    "min": time-spec,<br>
    "max": time-spec<br>
}<br>
</code></pre>

If <i>published</i> is not specified, there is no constraint on the document publication time. If <i>min</i> is specified, the publication time must not be earlier than the given time. If <i>max</i> is specified, the publication time must not be later than the given time. The time must be specified as a string with the date format YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.000Z in UTC. It is possible to specify time with only initial portions of the time specification. That is, a timestamp can be specified as "2012-05" to indicate May, 2012, or "2012-05-01 12:00" to indicate noon, UTC on 2012-05-01.<br>
<br>
<i>downloaded</i> matches on the date Recorded Future downloaded the document. <i>downloaded</i> has the same structure as <i>published</i>.<br>
<br>
The source constraint has the following structure:<br>
<br>
<pre><code>"source": {<br>
    "id": [string],<br>
    "name": [string],<br>
    "topic": [string],<br>
    "media_type": [string],<br>
    "country": [string]<br>
}<br>
</code></pre>

<i>id</i> matches on source identifiers. An identifier is a string, and is a system defined identification of a source. The value of the parameter must be a string or a list of strings. The parameter matches if the source identifier matches one of the provided identifiers.<br>
<br>
<i>name</i> matches on source name. A source name is a short string identifying the source. The value of the parameter must be a string or a list of strings. The parameter matches if the source name matches one of the supplied names.<br>
<br>
<i>description</i> matches on source descriptions. A source description is a somewhat longer string identifying the source. The value of the parameter must be a string or a list of strings. The parameter matches if the source description matches one of the provided names.<br>
<br>
<i>topic</i> matches on source topics. (Recorded Future categorizes all Sources into topics.) The value of the parameter must be a string or a list of strings. The parameter matches if the source topic matches one of the following names:<br>
<br>
<font face='Courier'>Animal Welfare</font><br>
<font face='Courier'>Business/Finance</font><br>
<font face='Courier'>Disaster/Accident</font><br>
<font face='Courier'>Education</font><br>
<font face='Courier'>Energy</font><br>
<font face='Courier'>Entertainment/Culture</font><br>
<font face='Courier'>Environment</font><br>
<font face='Courier'>General</font><br>
<font face='Courier'>Geopolitics</font><br>
<font face='Courier'>Government</font><br>
<font face='Courier'>Healthcare</font><br>
<font face='Courier'>Human Interest</font><br>
<font face='Courier'>Information Security</font><br>
<font face='Courier'>Information Security - Notable</font><br>
<font face='Courier'>Labor Issues</font><br>
<font face='Courier'>Law/Crime</font><br>
<font face='Courier'>Malware Analysis</font><br>
<font face='Courier'>Military</font><br>
<font face='Courier'>Other</font><br>
<font face='Courier'>Politics</font><br>
<font face='Courier'>Recreation</font><br>
<font face='Courier'>Religion</font><br>
<font face='Courier'>Science</font><br>
<font face='Courier'>Scientific Journal</font><br>
<font face='Courier'>Social Issues</font><br>
<font face='Courier'>Sports</font><br>
<font face='Courier'>Tech Policy</font><br>
<font face='Courier'>Technology</font><br>
<font face='Courier'>Technology/Internet</font><br>
<font face='Courier'>Terrorism</font><br>
<font face='Courier'>Transportation</font><br>
<font face='Courier'>War/Conflict</font><br>
<font face='Courier'>Weather</font><br>

<i>media<code>_</code>type</i> matches on source media types. (The system categorizes all Sources into media types.) The value of the parameter must be a string or a list of strings. <i>media<code>_</code>type</i> matches if the source media type matches one of the following names:<br>
<br>
<font face='Courier'>Blog</font><br>
<font face='Courier'>Comments</font><br>
<font face='Courier'>Cyber Vulnerabilities</font><br>
<font face='Courier'>Exchange</font><br>
<font face='Courier'>Financial</font><br>
<font face='Courier'>Forum</font><br>
<font face='Courier'>Government</font><br>
<font face='Courier'>IRC Channels</font><br>
<font face='Courier'>Letters</font><br>
<font face='Courier'>Mainstream</font><br>
<font face='Courier'>NGO</font><br>
<font face='Courier'>News Agency</font><br>
<font face='Courier'>Niche</font><br>
<font face='Courier'>Paste Site</font><br>
<font face='Courier'>Podcast</font><br>
<font face='Courier'>Primary Source</font><br>
<font face='Courier'>Scientific Journal</font><br>
<font face='Courier'>Social Media</font><br>

<i>country</i> matches on the originating country of the source. The value of <i>country</i> must be a string or a list of strings. <i>country</i> matches if the source country matches one of the country names specified in the metadata document.<br>
<br>
As another example, suppose we want to find the number of references to Apple that we indexed in the month of August 2014. We can run the following query:<br>
<br>
<pre><code>{<br>
  "instance": {<br>
    "type": "Event",<br>
    "attributes": [<br>
      {<br>
        "entity": {<br>
          "id": "B_LyO"<br>
        }<br>
      }<br>
    ],<br>
    "document": {<br>
      "indexed": {<br>
        "min": "2014-08-01T00:00:00",<br>
        "max": "2014-09-01T00:00:00"<br>
      }<br>
    }<br>
  },<br>
  "token": "TOKEN"<br>
}<br>
</code></pre>

The result of this query is the following:<br>
<br>
<pre><code>{<br>
    "count": {<br>
        "references": {<br>
            "returned": 0,<br>
            "total": 639981<br>
        }<br>
    },<br>
    "status": "SUCCESS",<br>
    "instances": [],<br>
    "entities": {}<br>
}<br>
</code></pre>

<h3>Matching on free text</h3>

The "freetext" section allows you to match on free text features of an instance.<br>
Fields available for free text search include the document title and instance<br>
fragment. A free text specification looks like this.<br>
<pre><code>"freetext": [["aa","bb"], ["cc","dd"]]<br>
</code></pre>

This will match instances which contain the string ("aa" OR "bb") AND ("cc" OR "dd").<br>
<br>
<h3>Exclusion</h3>

It is possible to exclude terms in searches. For example, to retrieve information on Volvo starting from December 2014 - but exclude the terms 'market cap' and 'earnings' from the results - we could use the following query:<br>
<br>
<pre><code><br>
{<br>
  "instance": {<br>
    "start": "2014-12",<br>
    "attributes": [<br>
      {"entity":{"id":["JyQgS"]}},<br>
      {"not":{<br>
        "name":"Event.event_fragment",<br>
        "string":["market cap", "earnings"]<br>
      }<br>
      }<br>
    ]<br>
  },<br>
  "token":TOKEN<br>
}<br>
<br>
</code></pre>

<h3>Entity details</h3>

The "<i>entity_details</i>" section is a dictionary keyed by entity type name, and the values are lists of the attribute names that should be included in the output. The type, name and momentum are given for all entities. Some attributes are entity attributes, and they may be followed recursively to a certain maximum depth. The default depth is 2, which returns entity information for entities listed as attributes of instances that meet the initial query criteria. You can change the default by setting the depth parameter in the output section.  If set to 0, no entity details are given, and if set to -1, there is no depth limit.<br>
<br>
<br>
<h3>Response Specification Options</h3>
<pre><code>"output": {<br>
  "format":string,<br>
  "timezone":string<br>
}<br>
</code></pre>

<i>type</i> defines the shape of the output response, it can be either "csv" or "json". It is "json" by default.<br>
<i>timezone</i> defines the timezone used to format the response items. Default is to format in UTC.<br>
<br>
<h1>Output fields</h1>
Available output fields include<br>
<br>
<table><thead><th> <b>Field name</b> </th><th> <b>Description</b> </th></thead><tbody>
<tr><td> "id"              </td><td> The identity number of the instance </td></tr>
<tr><td> "type"            </td><td> The name of the type of the instance </td></tr>
<tr><td> "time"            </td><td> Start and stop time of the instance </td></tr>
<tr><td> "time_fragment"   </td><td> The text fragment from which the time was derived </td></tr>
<tr><td> "time_fragment_context" </td><td> A larger context of the time fragment </td></tr>
<tr><td> "fragment"        </td><td> The text fragment this instance was found in </td></tr>
<tr><td> "momentum         </td><td> The momentum value of this instance, a value between 0 and 1. For aggregate queries, this is the average momentum. </td></tr>
<tr><td> "sentiment"       </td><td> The list of sentiments of this instance, either "positive" or negative". </td></tr>
<tr><td> "attributes"      </td><td> The attributes of this instance. The attributes with basic types are given inline. The entity attributes are given as references to the entity identifiers. <br>The entities themselves are given in a separate dictionary, with the string form of the entity identifier as the key, and the entity details as the value. </td></tr>
<tr><td> "canonical.id"    </td><td> The identity number of the canonical item of this instance </td></tr>
<tr><td> "hits"            </td><td> The number of times a canonical id has been previously observed when a record is created. </td></tr>
<tr><td> "document.id"     </td><td> The identity number of the document </td></tr>
<tr><td> "document.title"  </td><td> The title of the document </td></tr>
<tr><td> "document.url"    </td><td> The URL of the document </td></tr>
<tr><td> "document.published" </td><td> The point in time when the document was published by the source </td></tr>
<tr><td> "document.downloaded" </td><td> The point in time when the document was downloaded </td></tr>
<tr><td> "document.sourceId.id" </td><td> The identity number of the source </td></tr>
<tr><td> "document.sourceId.name" </td><td> The name of the source </td></tr>
<tr><td> "document.sourceId.media_type" </td><td> The media type of the source </td></tr>
<tr><td> "document.sourceId.topic" </td><td> The source topic   </td></tr>
<tr><td> "document.sourceId.country" </td><td> The originating country of the source </td></tr></tbody></table>


<h3>Response specification</h3>

Responses are returned as a structured JSON string or as CSV, as defined in the output section of the query. A JSON response has the following structure:<br>
<br>
<pre><code>{<br>
  "status": &lt;"SUCCESS" or "FAILURE"&gt;<br>
  "error": &lt;describes the problem in case of FAILURE&gt;<br>
  "instances": &lt;list of matching events instances, in decreasing momentum order&gt;<br>
  "entities": &lt;a dictionary with details for entities involved in the events&gt;<br>
}<br>
</code></pre>


If the query is successful, the format will be what is specified by the user. If the query is unsuccessful, a JSON formatted error message will be returned.<br>
<br>
<h2>Aggregate Queries</h2>

Functionality is deprecated<br>
<br>
<h1>On the fly aggregation</h1>
These aggregates are not pre-calculated, but instead calculated on the fly. The aggregates are formed as a normal instance query, but with a aggregation specification in the output section. No limit spec is needed, the API will aggregate all matching instances.<br>
<br>
The aggregate are much quicker than fetching instance details and aggregating on the client side, but still it will take some time for very wide aggregates, which match many millions of instances.<br>
<br>
The output count specification should be a list of dictionaries with the keys axis and values.<br>
<br>
The axis specification defines what to aggregate on. It is specified by providing a sequence of the various axis choices. It could also be empty, meaning that a total aggregate should be produced. The axis choices are:<br>
<table><thead><th> <b>Axis name</b> </th><th> <b>Axis Description</b> </th></thead><tbody>
<tr><td> type             </td><td> The metadata type for an instance </td></tr>
<tr><td> source           </td><td> The source ID of the instance's document </td></tr>
<tr><td> source_topic     </td><td> The topic of the source of the instance's document </td></tr>
<tr><td> source_media_type </td><td> The media type of the source of the instance's document </td></tr>
<tr><td> source_country   </td><td> The country of the source of the instance's document </td></tr>
<tr><td> document         </td><td> The ID of the instance's document </td></tr>
<tr><td> canonic          </td><td> The canonic ID of the instance </td></tr>
<tr><td> tempus           </td><td> The tempus of the instance: either 'historic' or 'prediction' </td></tr>
<tr><td> publication_minute </td><td> The minute of publication of the document </td></tr>
<tr><td> publication_hour </td><td> The hour of publication of the document </td></tr>
<tr><td> publication_day  </td><td> The day of publication of the document </td></tr>
<tr><td> publication_month </td><td> The month of publication of the document </td></tr>
<tr><td> publication_year </td><td> The year of publication of the document </td></tr>
<tr><td> publication_month_in_year </td><td> The month of a year of publication of the document </td></tr>
<tr><td> publication_day_in_month </td><td> The day in a month of publication of the document </td></tr>
<tr><td> publication_weekday </td><td> The weekday of publication of the document </td></tr>
<tr><td> start_minute     </td><td> The minute of the instance start time </td></tr>
<tr><td> start_hour       </td><td> The hour of the instance start time </td></tr>
<tr><td> start_day        </td><td> The day of the instance start time </td></tr>
<tr><td> start_month      </td><td> The month of the instance start time </td></tr>
<tr><td> start_year       </td><td> The year of the instance start time </td></tr>
<tr><td> start_month_in_year </td><td> The month of a year of the instance start time </td></tr>
<tr><td> start_day_in_month </td><td> The day in a month of the instance start time </td></tr>
<tr><td> start_weekday    </td><td> The weekday of the instance start time </td></tr>
<tr><td> stop_minute      </td><td> The minute of the instance stop time </td></tr>
<tr><td> stop_hour        </td><td> The hour of the instance stop time </td></tr>
<tr><td> stop_day         </td><td> The day of the instance stop time </td></tr>
<tr><td> stop_month       </td><td> The month of the instance stop time </td></tr>
<tr><td> stop_year        </td><td> The year of the instance stop time </td></tr>
<tr><td> stop_month_in_year </td><td> The month of a year of the instance stop time </td></tr>
<tr><td> stop_day_in_month </td><td> The day in a month of the instance stop time </td></tr>
<tr><td> stop_weekday     </td><td> The weekday of the instance stop time </td></tr>
<tr><td> loader           </td><td> The origin of the document (mostly of internal interest) </td></tr></tbody></table>

The values specification defines what should be calculated for each time point for the axis. The specification should be a list of dictionary entries, each with a key 'type' defining which value type is requested. The allowed values are:<br>
<br>
<table><thead><th> <b>Count type</b> </th><th> <b>Value Description</b> </th></thead><tbody>
<tr><td> instances         </td><td> The number of matching instances </td></tr>
<tr><td> documents         </td><td> The number of distinct documents for the matching instances </td></tr>
<tr><td> momentum          </td><td> The average momentum for the matching instances </td></tr>
<tr><td> sentiment         </td><td> The sentiments for the matching instances </td></tr></tbody></table>

A sentiment entry has two required keys:<br>
<br>
<table><thead><th> <b>Sentiment type key</b> </th><th> <b>Key options and meaning</b> </th></thead><tbody>
<tr><td> kind	                     </td><td> Either general or finance, to choose on of the two sentiment kinds </td></tr>
<tr><td> style                     </td><td>	Either combined (positive-negative), positive, or negative </td></tr></tbody></table>

The output format defaults to JSON, but can be changed to CSV by setting the format key in the output section to csv.<br>
<br>
Example:<br>
<pre><code>{<br>
  "instance": {<br>
    "attributes": {"entity": {"id": "B_LyO"}},<br>
    "document": {<br>
      "published": {"min": "2011-04", "max": "2011-05"}<br>
    }<br>
  },<br>
  "output": {<br>
    "count": [{"axis": ["publication_day", "source_media_type"],<br>
               "values": [{"type": "instances"}, <br>
                          {"type": "sentiment", <br>
                           "kind": "general", "style": "combined"}, <br>
                          {"type": "momentum"}]}],<br>
     "format": "csv"<br>
  },<br>
  "token": "TOKEN"<br>
}<br>
</code></pre>

Here is a sample CSV output of this query. It shows the first few lines of the response.<br>
<pre><code>publication_day,source_media_type,instances,general_combined,momentum<br>
2011-04-01,Blog,611,0.0,0.38483444<br>
2011-04-01,Mainstream,123,0.0,0.37988955<br>
2011-04-01,News Agency,154,0.0,0.3903726<br>
2011-04-01,Niche,348,0.0,0.41963947<br>
2011-04-01,Primary Source,3,0.0,0.3637922<br>
2011-04-02,Blog,283,0.0,0.4196129<br>
2011-04-02,Mainstream,55,0.0,0.4168904<br>
2011-04-02,News Agency,45,0.0,0.4575829<br>
2011-04-02,Niche,59,0.0,0.4094747<br>
...<br>
</code></pre>

Here is the corresponding JSON output:<br>
<pre><code>{<br>
  "status": "SUCCESS", <br>
  "counts": [<br>
    {<br>
      "2011-04-13": {<br>
        "Niche": {<br>
          "instances": 268, <br>
          "momentum": 0.4584336, <br>
          "general_combined": 0.0<br>
        }, <br>
        "Primary Source": {<br>
          "instances": 1, <br>
          "momentum": 0.39325377, <br>
          "general_combined": 0.0<br>
        }, <br>
        "Mainstream": {<br>
          "instances": 182, <br>
          "momentum": 0.45799348000000001, <br>
          "general_combined": 0.0<br>
        }, <br>
...<br>
</code></pre>

<h1>Paging instance results</h1>

The default limit of the number of resulting instances in an instance query is 100. The limit can be explicitly set as described above, up to a maximum of 100,000 instances. Sometimes, it’s hard to know how many instances a query will result in, and sometimes it’s desirable to be able to page through the - possibly very large - result set.<br>
<br>
If not all instances matching a query are returned by the API, due to the response exceeding the implicit or explicit instance limit, the JSON response will contain the key next_page_start with an opaque value. If CSV output is requested there is no place in the output for this information, so instead the HTTP response header RFQ-next_page_start is set to the opaque value. In order to get the next set of matching instances (the next page), the same query should be executed again, with the instance query key page_start set to the value of the last next_page_start.<br>
<br>
To get all matching instances of a query, this process should be repeated until next_page_start is not set in a query response.<br>
<br>
<br>
<h2>Paging Example</h2>

An example query where paging is utilized:<br>
<br>
<pre><code>{<br>
    "reference": {<br>
        "type": "RFEVEProtest",<br>
        "attributes": [<br>
            {<br>
                "not": {<br>
                    "name": "location",<br>
                    "entity": {<br>
                        "id": "B_FAG"<br>
                    }<br>
                }<br>
            }<br>
        ],<br>
        "document": {<br>
            "published": {<br>
                "min": "2014-10-27",<br>
                "max": "2014-10-27"<br>
            }<br>
        },<br>
        "limit": 7500,<br>
        "searchtype": "scan"<br>
    },<br>
    "token": "TOKEN"<br>
}<br>
</code></pre>

The response:<br>
<br>
<pre><code>{<br>
    "count": {<br>
        "references": {<br>
            "returned": 472,<br>
            "total": 62771<br>
        }<br>
    },<br>
    "next_page_start": "c2Nhbjs4OzMwOTc5MjkzOTowb0lBaUc3NVMtZWlna3RLMDVKaHhnOzMwOTM1MTQwOTpOYnNYYUp5YlFxMjUtUkcwWEVsYXdnOzc4OTI5NjE2OmlvbGowZlJVU1RXVGlFVC10eEZFMEE7MzI1OTg2NDgwOk9tUE5nZTM2UjJLWUJ4QmJ2dDY0SXc7MTM4NDUxMzkyOlBRWUZ5cjY3UXBldWk4N3RMcmhQWUE7Nzg5Mjk2MTk6aW9sajBmUlVTVFdUaUVULXR4RkUwQTszMTM3MDA4MjI6SDkzWWd6X0lUOTZ3N3dDNnFRbHVGdzsyODMyMDM4NTI6SU50MEVJUWlUVnFjTUhXZWVvdHR2UTsxO3RvdGFsX2hpdHM6NjI3NzE7",<br>
    "status": "SUCCESS",<br>
...<br>
<br>
</code></pre>

After getting the first response, you would then set "page_start" in the query to "next_page_start" from the response and make a second query for the next page:<br>
<br>
<pre><code>{<br>
    "reference": {<br>
        "type": "RFEVEProtest",<br>
        "attributes": [<br>
            {<br>
                "not": {<br>
                    "name": "location",<br>
                    "entity": {<br>
                        "id": "B_FAG"<br>
                    }<br>
                }<br>
            }<br>
        ],<br>
        "document": {<br>
            "published": {<br>
                "min": "2014-10-27",<br>
                "max": "2014-10-27"<br>
            }<br>
        },<br>
        "limit": 7500,<br>
        "searchtype": "scan",<br>
        "page_start": "c2Nhbjs4OzMwOTc5MjkzOTowb0lBaUc3NVMtZWlna3RLMDVKaHhnOzMwOTM1MTQwOTpOYnNYYUp5YlFxMjUtUkcwWEVsYXdnOzc4OTI5NjE2OmlvbGowZlJVU1RXVGlFVC10eEZFMEE7MzI1OTg2NDgwOk9tUE5nZTM2UjJLWUJ4QmJ2dDY0SXc7MTM4NDUxMzkyOlBRWUZ5cjY3UXBldWk4N3RMcmhQWUE7Nzg5Mjk2MTk6aW9sajBmUlVTVFdUaUVULXR4RkUwQTszMTM3MDA4MjI6SDkzWWd6X0lUOTZ3N3dDNnFRbHVGdzsyODMyMDM4NTI6SU50MEVJUWlUVnFjTUhXZWVvdHR2UTsxO3RvdGFsX2hpdHM6NjI3NzE7"<br>
    },<br>
    "token":"TOKEN"<br>
}<br>
</code></pre>


<h2>Using the Recorded Future API with R</h2>

<a href='http://www.r-project.org/'>R</a> is a language and environment for statistical computing and graphics. You can use commonly- available R packages to assist with forming and executing queries, and obtaining and parsing the results.<br>
<br>
The <a href='http://www.omegahat.org/RJSONIO/'>RJSONIO Package</a> contains functions that facilitate reading and writing JSON data:<br>
<br>
<b>The <i>fromJSON</i> function converts a JSON string into R list objects.<br></b> The <i>toJSON</i> function converts R list objects into a JSON string.<br>
<br>
The following sample shows a Recorded Future query as a standard R list object with two top level elements:  instance and output.<br>
<pre><code>&gt;print(Rquery)<br>
<br>
$instance<br>
$instance$type<br>
[1] "ProductRelease"<br>
<br>
$instance$attributes<br>
$instance$attributes[[1]]<br>
$instance$attributes[[1]]$type<br>
[1] "Company"<br>
<br>
$instance$document<br>
$instance$document$published<br>
$instance$document$published$min<br>
[1] "2010-01-01"<br>
<br>
$instance$document$published$max<br>
[1] "2010-03-12"<br>
<br>
 $instance$limit<br>
[1] 1<br>
<br>
</code></pre>

To create a JSON string, apply the toJSON function to this R list object:<br>
<br>
<pre><code>&gt; json.Query&lt;-toJSON(Rquery)<br>
<br>
&gt; cat(json.Query)<br>
</code></pre>

The following sample shows the resulting JSON string:<br>
<br>
<pre><code>{<br>
    "instance": {<br>
        "type": ["ProductRelease"],<br>
        "attributes": [{"type": "Company",<br>
                    "entity": {"attributes": [{"name": "gics",<br>
                                    "string": "Information Technology"}]}}],<br>
        "document": {<br>
            "published": {"min": "2010-01-01", "max": "2010-03-12"}<br>
        },<br>
        "limit": 1<br>
    }<br>
}<br>
</code></pre>

The <a href='http://www.omegahat.org/RCurl/'>RCURL Package</a> is an R-interface to the <a href='http://curl.haxx.se/'>libcurl</a> library. This package assists with creating and submitting URLs that contain the JSON formatted query and with retrieving the results from the response.<br>
<br>
The following sample uses RCURL routines to form a URL and retrieve data and then uses the fromJSON function from the RJSONIO package to create the resulting R list objects.<br>
<br>
<pre><code>&gt; opts = curlOptions(header = FALSE)<br>
<br>
&gt; url&lt;-paste("http://api.recordedfuture.com/query?q=", RCurl::curlEscape(jsonQuery),sep="")<br>
<br>
&gt; jsonResult&lt;-getBinaryURL(url, .opts = opts)<br>
<br>
&gt; jsonResult &lt;-fromJSON(jsonResult)<br>
</code></pre>

<h2>Using the Recorded Future API with Python</h2>

A number of Python libraries are available to facilitate reading and writing JSON data, including the popular <a href='http://www.undefined.org/python/'>simplejson</a> and <a href='http://sourceforge.net/projects/json-py/'>json-py</a>.<br>
<br>
The following sample Python code executes two queries and prints some of the results. If you test this sample by incorporating it into your code, remember to replace the value TOKEN with a valid Recorded Future API token.<br>
<br>
<pre><code>#Sample Python query:<br>
<br>
#----------------------------------------------<br>
<br>
qsource2="""{<br>
  "comment": "Barack Obama quotations.",<br>
  "instance": {<br>
    "type": "Quotation",<br>
    "attributes": {<br>
      "entity": {<br>
        "id":"B_FCc"<br>
      }<br>
    },<br>
    "limit": 3<br>
  },<br>
  "token": "ABCDEF"<br>
}"""<br>
<br>
qsource="""{<br>
<br>
  "comment": "Q1 earnings calls",<br>
<br>
  "instance": {<br>
    "type": ["ConferenceCall"],<br>
    "attributes": [ {"name": "year", "string": "2009"},<br>
    "limit": 50,<br>
    "document": {<br>
      "source": {<br>
         "topic": "Business"<br>
      }<br>
    }<br>
  },<br>
  "token": "TOKEN"<br>
<br>
}""" <br>
</code></pre>

The following Python sample makes use of the Recorded Future event instances web service.<br>
<br>
<pre><code>#-------------------------------------------------------<br>
#Python example that takes query and executes<br>
#------------------------------------------------------<br>
import sys, urllib, json<br>
<br>
# Simple program showing how to use the event instances web-service from Python<br>
<br>
# Web service URL<br>
url = 'http://api.recordedfuture.com/query?%s'<br>
<br>
# Wraps the web-service into a python function<br>
# Input: q: a JSON-formatted string specifying the query<br>
# Out: Dict corresponding to the JSON object returned by the web service<br>
def query(q):<br>
    try:<br>
        data = urllib.urlopen(url % urllib.urlencode({"q":q}))<br>
        if type(data) != str:<br>
            data = data.read()<br>
        #print data<br>
        return json.loads(data)<br>
    except Exception, e:<br>
        return {'status': 'FAILURE', 'errors': str(e)}<br>
<br>
# Main program code:<br>
# Open a specified query file (JSON-formatted), and run that query<br>
# The result is a list of event instances matching the query, ordered by momentum<br>
# and a dictionary with detailed information about the involved entities<br>
<br>
# Read the query<br>
qsource = open(sys.argv[1], "r").read()<br>
<br>
# Run the query<br>
res = query(q=qsource)<br>
print(str(res))<br>
<br>
# Check if the query succeeded<br>
if res['status'] == 'FAILURE':<br>
    print("Error: " + str(res['errors']))<br>
    sys.exit(1)<br>
<br>
# Get the returned structures<br>
entities = res["entities"]<br>
evis = res["instances"]<br>
<br>
# Utility function to pretty print an entity overview (name and type)<br>
def eninfo(en):<br>
    return "%s[%s]" % (en["name"], en["type"])<br>
<br>
def utf8(s):<br>
    return s.encode('utf-8') if type(s) in [unicode, str] else s<br>
<br>
# Iterate of the event instances<br>
for evi in evis:  <br>
    # Print basic event instance info (type and time)<br>
    print (evi["type"], evi["start"], "-", evi["stop"])<br>
<br>
       # Print the event roles and their values<br>
    for k, v in evi["attributes"].items():<br>
        # No metadata available here, so use a simple method to check if<br>
        # the value is an entity reference: try to look it up in the<br>
        # entity dictionary<br>
        if type(v) in [long, int]:<br>
            en = entities.get(str(v))<br>
            if en:<br>
                v = eninfo(en)<br>
        print ("  %s=%s" % (k, v))<br>
    # Print anonymous entity references (not tied to a role) in the event instance<br>
    v = evi.get("mentions")<br>
    if v:<br>
        v = v if type(v) == list else [v]<br>
        print ("  mentions=%s" % ", ".join([eninfo(entities[str(enid)]) for enid in v]))<br>
<br>
    # Print document information<br>
    doc = evi["document"]<br>
    print ("  document:")<br>
    for key in ["title", "sourceId", "url"]:<br>
            print ("    %s=%s" % (key, utf8(doc[key])))<br>
<br>
print ("\nDetails about involved entities:\n")<br>
<br>
for id, en in entities.items():<br>
    print (eninfo(en), "(id=" + str(id) + ")")<br>
    for k, v in en.items():<br>
        if k in ["name", "type"]:<br>
            continue<br>
        print ("  %s=%s" % (k, v))<br>
</code></pre>

<h2>Entity and Event Types</h2>

The following event and entity types are currently available in the system.<br>
<br>
<h3>Entity Types</h3>

<font face='Courier'>Anniversary</font><br>
<font face='Courier'>City</font><br>
<font face='Courier'>Commodity</font><br>
<font face='Courier'>Company</font><br>
<font face='Courier'>Continent</font><br>
<font face='Courier'>Country</font><br>
<font face='Courier'>Coup</font><br>
<font face='Courier'>CreditCardNumber</font><br>
<font face='Courier'>Currency</font><br>
<font face='Courier'>CurrencyPair</font><br>
<font face='Courier'>CyberAttackCampaign</font><br>
<font face='Courier'>CyberVulnerability</font><br>
<font face='Courier'>EconomicIndicator</font><br>
<font face='Courier'>EmailAddress</font><br>
<font face='Courier'>EntertainmentAwardEvent</font><br>
<font face='Courier'>EntityList</font><br>
<font face='Courier'>Facility</font><br>
<font face='Courier'>FaxNumber</font><br>
<font face='Courier'>Feature</font><br>
<font face='Courier'>FileName</font><br>
<font face='Courier'>GeoEntity</font><br>
<font face='Courier'>Hash</font><br>
<font face='Courier'>Holiday</font><br>
<font face='Courier'>Identifier</font><br>
<font face='Courier'>Industry</font><br>
<font face='Courier'>IndustryTerm</font><br>
<font face='Courier'>InternetDomainName</font><br>
<font face='Courier'>IpAddress</font><br>
<font face='Courier'>Malware</font><br>
<font face='Courier'>MalwareSignature</font><br>
<font face='Courier'>MarketIndex</font><br>
<font face='Courier'>MedicalCondition</font><br>
<font face='Courier'>MedicalTreatment</font><br>
<font face='Courier'>Movement</font><br>
<font face='Courier'>Movie</font><br>
<font face='Courier'>MusicAlbum</font><br>
<font face='Courier'>MusicGroup</font><br>
<font face='Courier'>NaturalFeature</font><br>
<font face='Courier'>OperatingSystem</font><br>
<font face='Courier'>Operation</font><br>
<font face='Courier'>OrgEntity</font><br>
<font face='Courier'>Organization</font><br>
<font face='Courier'>Person</font><br>
<font face='Courier'>PhoneNumber</font><br>
<font face='Courier'>Position</font><br>
<font face='Courier'>Product</font><br>
<font face='Courier'>ProgrammingLanguage</font><br>
<font face='Courier'>ProvinceOrState</font><br>
<font face='Courier'>PublishedMedium</font><br>
<font face='Courier'>RadioProgram</font><br>
<font face='Courier'>RadioStation</font><br>
<font face='Courier'>Region</font><br>
<font face='Courier'>Religion</font><br>
<font face='Courier'>ReportingEntity</font><br>
<font face='Courier'>Sector</font><br>
<font face='Courier'>Source</font><br>
<font face='Courier'>SourceMediaType</font><br>
<font face='Courier'>SportsEvent</font><br>
<font face='Courier'>SportsGame</font><br>
<font face='Courier'>SportsLeague</font><br>
<font face='Courier'>TVShow</font><br>
<font face='Courier'>TVStation</font><br>
<font face='Courier'>Technology</font><br>
<font face='Courier'>TechnologyArea</font><br>
<font face='Courier'>Topic</font><br>
<font face='Courier'>TwitterHandle</font><br>
<font face='Courier'>URL</font><br>
<font face='Courier'>Username</font><br>

<font face='Courier'>WinRegKey</font><br>

<h3>Event Types</h3>

<font face='Courier'>Acquisition</font><br>
<font face='Courier'>Alliance</font><br>
<font face='Courier'>AnalystEarningsEstimate</font><br>
<font face='Courier'>AnalystRecommendation</font><br>
<font face='Courier'>Announcement</font><br>
<font face='Courier'>ArmedAssault</font><br>
<font face='Courier'>ArmedAttack</font><br>
<font face='Courier'>ArmsPurchaseSale</font><br>
<font face='Courier'>Arrest</font><br>
<font face='Courier'>Arson</font><br>
<font face='Courier'>Bankruptcy</font><br>
<font face='Courier'>BeneficialOwnershipFiling</font><br>
<font face='Courier'>BiologicalTerrorism</font><br>
<font face='Courier'>Bombing</font><br>
<font face='Courier'>BonusSharesIssuance</font><br>
<font face='Courier'>BusinessRelation</font><br>
<font face='Courier'>BusinessTransaction</font><br>
<font face='Courier'>BusinessTransactionText</font><br>
<font face='Courier'>Buybacks</font><br>
<font face='Courier'>CandidatePosition</font><br>
<font face='Courier'>Ceasefire</font><br>
<font face='Courier'>ChemicalTerrorism</font><br>
<font face='Courier'>CivilCourtProceeding</font><br>
<font face='Courier'>ClinicalTrial</font><br>
<font face='Courier'>CoEntityText</font><br>
<font face='Courier'>CoOccurrence</font><br>
<font face='Courier'>CompanyAccountingChange</font><br>
<font face='Courier'>CompanyAffiliates</font><br>
<font face='Courier'>CompanyCompetitor</font><br>
<font face='Courier'>CompanyCustomer</font><br>
<font face='Courier'>CompanyEarningsAnnouncement</font><br>
<font face='Courier'>CompanyEarningsGuidance</font><br>
<font face='Courier'>CompanyEmployeesNumber</font><br>
<font face='Courier'>CompanyExpansion</font><br>
<font face='Courier'>CompanyForceMajeure</font><br>
<font face='Courier'>CompanyFounded</font><br>
<font face='Courier'>CompanyInvestment</font><br>
<font face='Courier'>CompanyLaborIssues</font><br>
<font face='Courier'>CompanyLayoffs</font><br>
<font face='Courier'>CompanyLegalIssues</font><br>
<font face='Courier'>CompanyListingChange</font><br>
<font face='Courier'>CompanyLocation</font><br>
<font face='Courier'>CompanyMeeting</font><br>
<font face='Courier'>CompanyNameChange</font><br>
<font face='Courier'>CompanyProduct</font><br>
<font face='Courier'>CompanyReorganization</font><br>
<font face='Courier'>CompanyRestatement</font><br>
<font face='Courier'>CompanyTechnology</font><br>
<font face='Courier'>CompanyTicker</font><br>
<font face='Courier'>CompanyUsingProduct</font><br>
<font face='Courier'>ConferenceCall</font><br>
<font face='Courier'>Conviction</font><br>
<font face='Courier'>CreditRating</font><br>
<font face='Courier'>CrimeAndViolence</font><br>
<font face='Courier'>CriminalCourtProceeding</font><br>
<font face='Courier'>CyberAttack</font><br>
<font face='Courier'>Cyberterrorism</font><br>
<font face='Courier'>DatedEvent</font><br>
<font face='Courier'>DebtFinancing</font><br>
<font face='Courier'>DelayedFiling</font><br>
<font face='Courier'>DiplomaticRelations</font><br>
<font face='Courier'>DiseaseOutbreak</font><br>
<font face='Courier'>Dividend</font><br>
<font face='Courier'>EconomicEvent</font><br>
<font face='Courier'>Election</font><br>
<font face='Courier'>EmploymentChange</font><br>
<font face='Courier'>EmploymentRelation</font><br>
<font face='Courier'>EntityOccurrence</font><br>
<font face='Courier'>EnvironmentalIssue</font><br>
<font face='Courier'>EquityFinancing</font><br>
<font face='Courier'>ExtendedPatentFiling</font><br>
<font face='Courier'>Extinction</font><br>
<font face='Courier'>FDAPhase</font><br>
<font face='Courier'>FamilyRelation</font><br>
<font face='Courier'>FinancialFiling</font><br>
<font face='Courier'>GeoPolitical</font><br>
<font face='Courier'>Hijacking</font><br>
<font face='Courier'>HostageRelease</font><br>
<font face='Courier'>HostageTakingKidnapping</font><br>
<font face='Courier'>IPO</font><br>
<font face='Courier'>IndicesChanges</font><br>
<font face='Courier'>Indictment</font><br>
<font face='Courier'>InsiderTransaction</font><br>
<font face='Courier'>JointVenture</font><br>
<font face='Courier'>LocatedEvent</font><br>
<font face='Courier'>LocationEvent</font><br>
<font face='Courier'>ManMadeDisaster</font><br>
<font face='Courier'>Merger</font><br>
<font face='Courier'>MilitaryAction</font><br>
<font face='Courier'>MilitaryManeuver</font><br>
<font face='Courier'>MilitaryOperation</font><br>
<font face='Courier'>MiscTerrorism</font><br>
<font face='Courier'>MnA</font><br>
<font face='Courier'>MovieRelease</font><br>
<font face='Courier'>MusicAlbumRelease</font><br>
<font face='Courier'>NaturalDisaster</font><br>
<font face='Courier'>NuclearMaterialTransaction</font><br>
<font face='Courier'>NuclearTerrorism</font><br>
<font face='Courier'>PatentFiling</font><br>
<font face='Courier'>PatentIssuance</font><br>
<font face='Courier'>PersonAttributes</font><br>
<font face='Courier'>PersonCareer</font><br>
<font face='Courier'>PersonCommunication</font><br>
<font face='Courier'>PersonEducation</font><br>
<font face='Courier'>PersonEmailAddress</font><br>
<font face='Courier'>PersonLocation</font><br>
<font face='Courier'>PersonMeeting</font><br>
<font face='Courier'>PersonParty</font><br>
<font face='Courier'>PersonRelation</font><br>
<font face='Courier'>PersonThreat</font><br>
<font face='Courier'>PersonTravel</font><br>
<font face='Courier'>PoliceOperation</font><br>
<font face='Courier'>PoliticalEndorsement</font><br>
<font face='Courier'>PoliticalEvent</font><br>
<font face='Courier'>PoliticalRelationship</font><br>
<font face='Courier'>PollResult</font><br>
<font face='Courier'>PressRelease</font><br>
<font face='Courier'>ProductIssues</font><br>
<font face='Courier'>ProductRecall</font><br>
<font face='Courier'>ProductRelease</font><br>
<font face='Courier'>Quotation</font><br>
<font face='Courier'>QuotationText</font><br>
<font face='Courier'>RFEVEAcquisition</font><br>
<font face='Courier'>RFEVEArmedAssault</font><br>
<font face='Courier'>RFEVEIedExplosion</font><br>
<font face='Courier'>RFEVELegislation</font><br>
<font face='Courier'>RFEVEMalwareThreat</font><br>
<font face='Courier'>RFEVEMerger</font><br>
<font face='Courier'>RFEVEOrganizationRelationship</font><br>
<font face='Courier'>RFEVEPersonCareer</font><br>
<font face='Courier'>RFEVEPersonCommunication</font><br>
<font face='Courier'>RFEVEPoliticalRelationship</font><br>
<font face='Courier'>RFEVEProtest</font><br>
<font face='Courier'>RadiologicalMaterialTransaction</font><br>
<font face='Courier'>Robbery</font><br>
<font face='Courier'>SecondaryIssuance</font><br>
<font face='Courier'>SourceLocation</font><br>
<font face='Courier'>Speech</font><br>
<font face='Courier'>StandardEvent</font><br>
<font face='Courier'>StatusEvent</font><br>
<font face='Courier'>StockSplit</font><br>
<font face='Courier'>TerrorCommunication</font><br>
<font face='Courier'>TerrorFinancing</font><br>
<font face='Courier'>Trafficking</font><br>
<font face='Courier'>Trial</font><br>
<font face='Courier'>Vandalism</font><br>
<font face='Courier'>Visit</font><br>
<font face='Courier'>VotingResult</font><br>