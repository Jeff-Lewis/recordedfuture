'''
IOCEnricher class to support enriching a collection of IOCs provided by
another process (e.g. ioc_runner.py).

Contact: support@recordedfuture.com
'''
import base64
import collections
import datetime
import json
import re

from RFAPI import RFAPI


class IOCEnricher(object):
    '''Enriches a list of IOCs with data from Recorded Future.
    '''

    _VALID_TYPES = ["IpAddress",
                    "Hash",
                    "InternetDomainName"]
    _INSTANCES_OR_DOCUMENTS = 'instances'
    _MALICIOUS_INDICATORS = ["compromised",
                             "malicious",
                             "suspected", 
                             "threat", 
                             "malware", 
                             "infected", 
                             "honeypot", 
                             "attacked from", 
                             "exploit", 
                             "attacks from", 
                             "bad http request from", 
                             "attack detected", 
                             "attack deteted"]
    _RELATED_ENTITY_TYPES = ['Malware',
                             'CyberVulnerability',
                             'IpAddress',
                             'Hash',
                             'InternetDomainName']
    # can be "document" also, but enrichment will take much longer
    # to pull document-level co-entities. fragment-level will use
    # extended_entities where available
    _RELATED_ENTITY_SCOPE = "fragment"
    _FEATURES = {"debug": collections.OrderedDict([("RFID", ""),
                                                   ("EntityType", ""),
                                                   ("TotalHits", 0),
                                                   ("7DayHits", 0), 
                                                   ("1DayHits", 0),
                                                   ("MaliciousHits", 0), 
                                                   ("InfoSecHits", 0),
                                                   ("PasteHits", 0), 
                                                   ("SocialMediaHits", 0)]),
                 "related": collections.OrderedDict([("RelatedMalware", []),
                                                     ("RelatedCyberVulnerability", []), 
                                                     ("RelatedIpAddress", []), 
                                                     ("RelatedInternetDomainName", []),
                                                     ("RelatedHash", []),
                                                     ("RelatedMalwareCount", 0), 
                                                     ("RelatedCyberVulnerabilityCount", 0),
                                                     ("RelatedIpAddressCount", 0), 
                                                     ("RelatedInternetDomainNameCount", 0),
                                                     ("RelatedHashCount", 0),
                                                     ("Score", 0.0)]),
                 "core": collections.OrderedDict([("Name", ""),
                                                  ("RFURL", ""),
                                                  ("MostRecent", ""),
                                                  ("MostRecentSource", ""),
                                                  ("MostRecentTitle", ""),
                                                  ("MostRecentFragment", ""),
                                                  ("MostRecentURL", ""),
                                                  ("RecentInfoSecSource", ""), 
                                                  ("RecentInfoSecTitle", ""),
                                                  ("RecentInfoSecFragment", ""), 
                                                  ("RecentInfoSecURL", ""), 
                                                  ("RecentPasteSource", ""), 
                                                  ("RecentPasteTitle", ""), 
                                                  ("RecentPasteFragment", ""), 
                                                  ("RecentPasteURL", ""),
                                                  ("RecentSocialMediaSource", ""), 
                                                  ("RecentSocialMediaTitle", ""), 
                                                  ("RecentSocialMediaFragment", ""), 
                                                  ("RecentSocialMediaURL", ""), 
                                                  ("FirstSource", ""), 
                                                  ("FirstTitle", ""), 
                                                  ("FirstFragment", ""), 
                                                  ("FirstURL", ""), 
                                                  ("FirstPublished", "")])}
    
    def __init__(self, token, iocs, entity_type, mode='core'):
        '''
        Parameters
        ----------
        token : str
            Recorded Future API token
        iocs : list or dict
            List of IOCs to enrich or dict of IOCs keyed by name with the value as the RFID. 
        entity_type : {"IpAddress", "Hash", "InternetDomainName"}
            Name of Recorded Future entity type for IOC.
        mode : {"core", "related", "debug"}
            Subset of features to return with enrichment. "core" is default.
        '''
        self.rfqapi = RFAPI(token)
        self.response = collections.OrderedDict()
        # need all features early for scoring; they're removed later
        # need to test whether this can be avoided
        keys = self._FEATURES['core']
        keys.update(self._FEATURES['debug'])
        if mode in ('related', 'debug'):
            keys.update(self._FEATURES['related'])
        if mode not in ('core', 'related', 'debug'):
            raise ValueError('"mode" must be one of ("core", "related", "debug"). Input: %s.' % mode)
        self.mode = mode
        self.entity_type = entity_type
        if isinstance(iocs, list):
            self.iocs = self._get_rfids(iocs)
        elif isinstance(iocs, dict):
            self.iocs = iocs
        else:
            raise ValueError('"iocs" must be list or dict.')
        for ioc in self.iocs:
            new_resp = {}
	    for key in keys:
                new_resp[key] = keys[key]
                if key == 'Name':
                    new_resp[key] = ioc
                elif key == 'RFID':
                    new_resp[key] = self.iocs[ioc]
                elif key == 'EntityType':
                    new_resp[key] = self.entity_type
            self.response[ioc] = new_resp
        self.keys = keys
    
    def get_keys(self, mode=None):
        '''Getter for the keys in the response.
        '''
        return [key for key in self.keys if key not in self._get_extra_features(mode)]
    
    def _get_extra_features(self, mode=None):
        if not mode:
            mode = self.mode
        extra_features = []
        if mode in ('core', 'related'):
            extra_features = self._FEATURES['debug'].keys()
        return extra_features
    
    def get_references(self, name):
      q = { "cluster": {
            "data_group": "EnrichIpAddress",
            "function": "enriched-ip-address",
	    "attributes": [ { 
	      "ip": name 
	      }]
	    },
	    "limit": 1001
	  }

      res = self.rfqapi.query(q)
      return res['events']

    def enrich(self):
        '''Enriches the given IOC.
        Returns
        -------
        response : dict
            The enrichment package containing all keys requested by "mode" parameter.
        '''
        print "    Getting all references"
        max_index = None
        for names in _chunks(self.iocs.keys(), 250):
          refs = self.get_references(names)

          for ioc in self.response:
            ioc_resp = self.response[ioc]

            print "    Enriching response"
            for ref in refs:
	      ioc_resp['MostRecent'] = ref['stats']['stats']['MostRecent']['Published']
	      ioc_resp['FirstPublished'] = ref['stats']['stats']['First']['Published']
              ioc_resp['TotalHits'] = ref['stats']['metrics']['TotalHits']
              ioc_resp['1DayHits'] = ref['stats']['metrics']['1DayHits']
              ioc_resp['7DayHits'] = ref['stats']['metrics']['7DayHits']
              ioc_resp['MaliciousHits'] = ref['stats']['metrics']['MaliciousHits']
              ioc_resp["RecentPasteTitle"] = ref['stats']['stats']['RecentPaste']['Title']
              ioc_resp["MostRecentSource"] = ref['stats']['stats']['MostRecent']['Source']['name']
              ioc_resp["FirstSource"] = ref['stats']['stats']['First']['Source']['name']
              ioc_resp["FirstURL"] = ref['stats']['stats']['First']['URL']
              ioc_resp["RecentPasteFragment"] = ref['stats']['stats']['RecentPaste']['Fragment']
              ioc_resp["RecentPasteSource"] = ref['stats']['stats']['RecentPaste']['Source']['name']
              ioc_resp["FirstTitle"] = ref['stats']['stats']['First']['Title']
              ioc_resp["RecentSocialMediaSource"] = ref['stats']['stats']['RecentSocialMedia']['Source']['name']
              ioc_resp["MostRecentURL"] = ref['stats']['stats']['MostRecent']['URL']
              ioc_resp["RecentSocialMediaFragment"] = ref['stats']['stats']['RecentSocialMedia']['Fragment']
              ioc_resp["FirstFragment"] = ref['stats']['stats']['First']['Fragment']
	      ioc_resp["MostRecentTitle"] = ref['stats']['stats']['MostRecent']['Title']
              ioc_resp["RecentPasteURL"] = ref['stats']['stats']['RecentPaste']['URL']
              ioc_resp["RecentSocialMediaURL"] = ref['stats']['stats']['RecentSocialMedia']['URL']
	      ioc_resp["RecentSocialMediaTitle"] = ref['stats']['stats']['RecentSocialMedia']['Title']

            # Get RF URL
            if 'RFURL' in ioc_resp:
                ioc_resp['RFURL'] = _generate_rfURL_from_entity(ioc, ioc_resp.get('RFID', None))
            # Score the ref
            if 'Score' in ioc_resp:
                self.score(ioc_resp)
            # Remove unnecessary features
            extra_features = self._get_extra_features()
            for key in extra_features:
                del ioc_resp[key]
        return self.response, max_index
                    
    
    def _get_rfids(self, iocs):
        new_iocs = collections.OrderedDict()
        edetails = {}
        for names in _chunks(iocs, 250):
            if len(names) == 0: continue
            q = {"entity": {"name": names, 
                            "type": self.entity_type,
                            "limit": 501}}
            res = self.rfqapi.query(q)
            if len(res['entities']) == 0: continue
            for ent in res['entities']:
                edetails[res['entity_details'][ent]['name']] = ent
        for ioc in iocs:
            new_iocs[ioc] = edetails[ioc] if ioc in edetails else None
        return new_iocs

def _generate_rfURL_from_entity(name, eid):
    base_url = 'https://www.recordedfuture.com/live/sc/'
    if isinstance(eid, unicode): 
        eid = eid.encode('utf8')
    if isinstance(name, unicode): 
        name = name.encode('utf8')
    params = []
    params.append({"id": "groupname", "value": "Mentions", "name": "Mentions"})
    freetext_hash = "freetext:" + base64.encodestring(name).strip()
    if eid: 
        params.append({"id": "entities", "value": ",".join([eid, freetext_hash]), "name": ",".join([name, '"' + name + '"'])})
    else:
        params.append({"id": "entity", "value": freetext_hash, "name": '"' + name + '"'})
    params = json.dumps([params])
    pattern = params.replace(' ', '')
    return base_url + '2gWqxC6apubO?patterns=' + pattern
    
def _rfid_date_conv(date):
    if isinstance(date, datetime.datetime):
        return date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    elif isinstance(date, basestring):
        return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
    
def _chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

rfq_aspect_all_pattern = re.compile('(.*) \((.*), (.*)\)')
def rf_agg_name_parser(name):
    '''Returns name, rfid, type
    '''
    return rfq_aspect_all_pattern.match(name).groups()
