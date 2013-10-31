# rfjsontotsv.py
# v1.1
# Usage: python rfjsontotsv.py 
# optional --instance_input_file
# optional --entity_input_file
# optional --instance_output_file
# optional --entity_output_file
# Takes in instances_1.json and entities_1.json and flattens into a 
# tab-delimited file. 

import sys, codecs, csv, json
from optparse import OptionParser

def setType(v):
  global type
  type = v
  type = type.replace('RFEVE','').replace('Event','Mention')
  return type

def setId(v):
  global id
  id = v
  return id

def setCanonicId(v):
  global canonic_id
  canonic_id = v
  return canonic_id

def setEventFragment(v):
  global event_fragment
  event_fragment = v.replace("\"","").replace("\n"," ").replace("\t"," ").strip()
  return event_fragment

def setStop(v):
  global stop
  stop = v
  return stop

def setDocumentTitle(v):
  global document_title
  document_title = v.replace("\"","").replace("\n"," ").replace("\t"," ").strip()
  return document_title

def setDocumentCategory(v):
  global document_category
  document_category = v
  return document_category

def setAuthors(v):
  global authors
  authors = ""
  for i in v:
    authors = i + ";" + authors
  return authors

def setPublished(v):
  global published
  published = v
  return published

def setDocumentURL(v):
  global document_url
  document_url = v
  return document_url

def setGeneralPositive(v):
  global general_positive
  general_positive = v
  return general_positive

def setToneViolence(v):
  global violence
  violence = v
  return violence

def setToneActivism(v):
  global activism
  activism = v
  return activism

def setGeneralNegative(v):
  global general_negative
  general_negative = v
  return general_negative

def setDocumentID(v):
  global document_id
  document_id = v
  return document_id

def setDocumentSource(v):
  global document_source
  document_source = translateSource(v)
  return document_source

def setEntities(v):
  global entities
  entities = ""
  for i in v:
    if i != None:
      i = translateEntities(i)
      entities = i + ";" + entities
  return entities
  
def setTopics(v):
  global topics
  topics = ""
  for i in v:
    i = translateTopic(i)
    topics = i + ";" + topics
  return topics

def setStart(v):
  global start
  start = v
  return start

def setLanguage(v):
  global language
  language = v
  return language

def translateSource(s):
  s = s.replace("JxSDuU", "Blog")
  s = s.replace("JxSEtM", "Letters")
  s = s.replace("JxRsrB", "Niche")
  s = s.replace("JxSEtl", "Financial")
  s = s.replace("Jyfb4z", "Forum")
  s = s.replace("JxSEs4", "Government")
  s = s.replace("JxSEtC", "Social Media")
  s = s.replace("JxSEtB", "Primary Source")
  s = s.replace("JxSEtQ", "Podcast")
  s = s.replace("JxSEs2", "Mainstream")
  s = s.replace("JxSEs9", "News Agency")
  s = s.replace("JxSEtH", "Scientific Journal")
  s = s.replace("JxSEtP", "Comments")
  s = s.replace("JxSEs8", "NGO")
  s = s.replace("KDS1Zp", "Pastebin")
  s = s.replace("JxSEtN", "Exchange")

  s = mapSource(entities_dict, s)

  return s

def translateEntities(s):
  s = mapEntities(entities_dict, s)
  return s

def translateTopic(s):
  s = s.replace("JxSEs6", "Energy")
  s = s.replace("JxSEtE", "Environment")
  s = s.replace("JxSEtU", "Culture")
  s = s.replace("JxSEte", "Labor Issues")
  s = s.replace("J228of", "Labor issues")
  s = s.replace("KPzY_v", "Health_Medical_Pharma")
  s = s.replace("KPzZAK", "Hospitality_Recreation")
  s = s.replace("JxSEs5", "Geopolitical")
  s = s.replace("JxSEs-", "Healthcare")
  s = s.replace("JxSEtL", "Information Security")
  s = s.replace("JxSEtT", "Science and Technology")
  s = s.replace("JxSEtd", "Travel and Tourism")
  s = s.replace("KPzY_5", "Law_Crime")
  s = s.replace("KPzZIB", "Weather")
  s = s.replace("JxSEtK", "Financial Services")
  s = s.replace("JxSEtc", "Leisure and Entertainment")
  s = s.replace("KPzZCG", "Politics")
  s = s.replace("KPzZEu", "Religion_Belief")
  s = s.replace("KPzZA1", "Science")
  s = s.replace("JxSEs3", "General")
  s = s.replace("JxSEtJ", "Scientific Finding")
  s = s.replace("JxSEtR", "Animal Welfare")
  s = s.replace("JxSEtb", "Sports")
  s = s.replace("JxSEtj", "Podcast")
  s = s.replace("KPzZAx", "War_Conflict")
  s = s.replace("JxSEtA", "Military")
  s = s.replace("JxSEtI", "Education")
  s = s.replace("KPzY_z", "Human Interest")
  s = s.replace("KPzZBF", "Labor")
  s = s.replace("JxSEs1", "Technology")
  s = s.replace("KPzZAv", "Disaster_Accident")
  s = s.replace("KPzY_1", "Technology_Internet")
  s = s.replace("JxSEs0", "Business")
  s = s.replace("JxSEtO", "Transportation")
  s = s.replace("KPzY_x", "Entertainment_Culture")
  s = s.replace("KPzZAE", "Cyber")
  s = s.replace("KPzei2", "Other")
  s = s.replace("JxSEs7", "Legal")
  s = s.replace("JxSEs_", "Government")
  s = s.replace("JxSEtF", "Terrorism")
  s = s.replace("JxSEtV", "Economy")
  s = s.replace("JxSEtf", "Comments")
  s = s.replace("KPzY_7", "Social Issues")
  s = s.replace("KPzZAT", "Business_Finance")
  return s

def printKeyVals(data, indent=0):
  if isinstance(data, dict): 
        for k, v in data.iteritems():
            if k == "type":
              setType(v)
            if k == "id":
              setId(v)
            if k == "canonic_id":
              setCanonicId(v)
	    if k == "attributes":
              printKeyVals(v)
            if k == "event_fragment":
              setEventFragment(v)
            if k == "stop":
              setStop(v)
            if k == "document_title":
              setDocumentTitle(v)
            if k == "document_category":
              setDocumentCategory(v)
            if k == "authors":
              setAuthors(v)
            if k == "published":
              setPublished(v)
            if k == "document_url":
              setDocumentURL(v)
            if k == "sentiments":
              printKeyVals(v)
            if k == "general_positive":
              setGeneralPositive(str(v))
            if k == "violence":
              setToneViolence(str(v))
            if k == "activism":
              setToneActivism(str(v))
            if k == "general_negative":
              setGeneralNegative(str(v))
            if k == "document_id":
              setDocumentID(v)
            if k == "document_source":
              setDocumentSource(v)
            if k == "entities":
              setEntities(v)
            if k == "topics":
              setTopics(v)
            if k == "start":
              setStart(v)
            if k == "language":
              setLanguage(v)
            printKeyVals(v)

def createEntitiesDict(entity_input_file, entity_output_file):
  entities_data = open(entity_input_file)
  entities_dict = {}
  fid = codecs.open(entity_output_file, 'wb', 'utf-8')
#  fid.write("Entity ID" + "\t" + "Entity Type" + "\t" + "Entity Name" + "\n")
  for j in entities_data:
    jdata = json.loads(j)
    entities_dict[jdata['id']] = jdata['attributes']['name']
#    fid.write(jdata['id'])
#    fid.write("\t")
    fid.write(jdata['type'])
    fid.write("\t")
    fid.write(jdata['attributes']['name'])
    fid.write("\n")
  fid.close()
  entities_data.close()
  return entities_dict

def mapSource(entities_dict, s):
  try:
    res = entities_dict[s]
  except:
    res = "None"
  return res

def mapEntities(entities_dict, s):
  try:
    res = entities_dict[s]
  except:
    res = "None"
  return res

if __name__ == "__main__":
  parser = OptionParser()
  parser.add_option('--instance_input_file')
  parser.add_option('--instance_output_file')
  parser.add_option('--entity_input_file')
  parser.add_option('--entity_output_file')
  options, args = parser.parse_args()
  if options.instance_input_file:
    instance_input_file = options.instance_input_file
  else:
    instance_input_file = 'instances_1.json'
  if options.instance_output_file:
    instance_output_file = options.instance_output_file
  else:
    instance_output_file = 'instances_1.tsv'
  if options.instance_input_file:
    entity_input_file = options.entity_input_file
  else:
    entity_input_file = 'entities_1.json'
  if options.instance_output_file:
    entity_output_file = options.entity_output_file
  else:
    entity_output_file = 'entities_1.tsv'

  entities_dict = createEntitiesDict(entity_input_file, entity_output_file)

  instances_data = open(instance_input_file)
  fid = codecs.open(instance_output_file, 'wb', 'utf-8')
  fid.write("Instance ID" + "\t" + "Event Type" + "\t" + "Fragment" + "\t" + "Start" + "\t" + "Stop" + "\t" + "Published" + "\t" + "Document Title" + "\t" + "Document ID"  "\t" + "Document Category" + "\t" + "Document Source" + "\t" + "Document URL" + "\t" + "Event ID" + "\t" "Authors" + "\t" + "Sentiment Positive" + "\t" + "Tone Violence" + "\t" + "Tone Activism" + "\t" + "Sentiment Negative" + "\t" + "Entities" + "\t" "Topics" + "\t" + "Language" + "\n")
  for j in instances_data:
    jdata = json.loads(j)
    printKeyVals(jdata)
    try:
      fid.write(id)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(type)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(event_fragment)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(start)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(stop)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(published)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(document_title)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(document_id)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(document_category)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(document_source)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(document_url)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(canonic_id)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(authors)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(general_positive)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(violence)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(activism)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(general_negative)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(entities)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(topics)
    except:
      pass
    fid.write("\t")
    try:
      fid.write(language)
    except:
      pass
    fid.write("\n")
  fid.close();
  instances_data.close()
