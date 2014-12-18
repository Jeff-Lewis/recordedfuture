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
        
    def enrich(self):
        '''Enriches the given IOC.
        Returns
        -------
        response : dict
            The enrichment package containing all keys requested by "mode" parameter.
        '''
        # print "Getting all references"
        refs, edetails = self._get_all_references()
        # print "Getting enrichment from references"
        self._get_enrichment(refs, edetails)
        # print "Getting URL and Score"
        for ioc in self.response:
            ioc_resp = self.response[ioc]
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
        return self.response

    def score(self, ioc_resp):
        spec_keys = ('7DayHits', '1DayHits')
        nonzero_keys = ('MaliciousHits',
                        'InfoSecHits',
                        'PasteHits',
                        'RelatedMalwareCount',
                        'RelatedCyberVulnerabilityCount',
                        'RelatedIpAddressCount',
                        'RelatedInternetDomainNameCount',
                        'RelatedHashCount')
        max_score = 0.0
        # score special keys
        if 'TotalHits' in self.keys:
            for key in filter(lambda k: k in self.keys, spec_keys):
                if ((ioc_resp[key]*2) > ioc_resp["TotalHits"]): 
                    ioc_resp['Score'] += 1
                max_score += len(spec_keys)
        # score nonzero keys
        for key in filter(lambda k: k in self.keys, nonzero_keys):
            if ioc_resp[key] > 0:
                ioc_resp['Score'] += 1
            max_score += 1
        ioc_resp['Score'] = ioc_resp['Score'] / max_score        

    def _get_enrichment(self, refs, edetails):
        today = datetime.datetime.today()
        one_day_hit_string = _rfid_date_conv(today - datetime.timedelta(days=1))
        seven_day_hit_string = _rfid_date_conv(today - datetime.timedelta(days=7))
        
        # first get everything from all references
        ioc_to_rfid = self.iocs
        rfid_to_ioc = {}
        for ioc in filter(lambda i: ioc_to_rfid[i], ioc_to_rfid):
            rfid_to_ioc[ioc_to_rfid[ioc]] = ioc
        recent_pub = {"MostRecent": {},
                      "Paste": {},
                      "InfoSec": {},
                      "SocialMedia": {}}
        first_pub = {}
        for ref in refs:
            fragment = ref['fragment'].lower()
            attrs = ref['attributes']
            source_topic = ref['document']['sourceId'].get('topic', None)
            source_media_type = ref['document']['sourceId'].get('media_type', None)
            pub_date = ref['document']['published']
            # get entities mentioned
            rfids = filter(lambda ioc: ioc in rfid_to_ioc, attrs.get('entities', []))
            ioc_rfids = [rfid for rfid in rfids if rfid in rfid_to_ioc]
            # get string hits that aren't included in the entity hits
            other_hits = [ioc for ioc in ioc_to_rfid if (ioc in fragment and ioc_to_rfid[ioc] not in ioc_rfids)]
            # increment hit counts and get recent hits
            iocs = [rfid_to_ioc[rfid] for rfid in ioc_rfids]
            for ioc in iocs + other_hits:
                ioc_resp = self.response[ioc]
                # update dates
                recent_pub['MostRecent'][ioc] = self._safe_update_date(ioc_resp, 
                                                                       pub_date, 
                                                                       recent_pub['MostRecent'][ioc] if ioc in recent_pub['MostRecent'] else '', 
                                                                       'MostRecent', 
                                                                       pub_date > recent_pub['MostRecent'][ioc] if ioc in recent_pub['MostRecent'] and len(recent_pub['MostRecent'][ioc]) > 0 else True)
                first_pub[ioc] = self._safe_update_date(ioc_resp, 
                                                        pub_date, 
                                                        first_pub[ioc] if ioc in first_pub else '', 
                                                        'FirstPublished', 
                                                        pub_date < first_pub[ioc] if ioc in first_pub and len(first_pub[ioc]) > 0 else True)
                # update hit counters
                self._safe_update_hits(ioc_resp, 
                                       'TotalHits', 
                                       True)
                self._safe_update_hits(ioc_resp, 
                                       '1DayHits', 
                                       pub_date >= one_day_hit_string)
                self._safe_update_hits(ioc_resp, 
                                       '7DayHits', 
                                       pub_date >= seven_day_hit_string)
                self._safe_update_hits(ioc_resp, 
                                       'MaliciousHits', 
                                       any(term in fragment for term in self._MALICIOUS_INDICATORS))
                # update hit counters and references
                conditions = {"InfoSec": source_topic == 'KPzZAE',
                              "Paste": source_media_type == 'KDS1Zp',
                              "SocialMedia": source_media_type == 'JxSEtC'}
                for key in conditions:
                    condition = conditions[key]
                    recent_pub[key][ioc] = self._safe_update_hits_and_refs(ioc_resp,
                                                                           ref,
                                                                           key,
                                                                           condition,
                                                                           recent_pub[key][ioc] if ioc in recent_pub[key] else '',
                                                                           pub_date > recent_pub[key][ioc] if ioc in recent_pub[key] and len(recent_pub[key][ioc]) > 0 else True)
                # update references for first and recent
                self._safe_update_refs(ioc_resp, 
                                       ref, 
                                       'MostRecent', 
                                       pub_date == recent_pub['MostRecent'][ioc])
                self._safe_update_refs(ioc_resp, 
                                       ref, 
                                       'First', 
                                       pub_date == first_pub[ioc])
        # get related content at fragment scope
        if self.mode in ('debug', 'related') and self._RELATED_ENTITY_SCOPE == 'fragment':
            self._safe_get_related_entities_from_frags(refs, edetails)
        # get related content at document scope
        if self.mode in ('debug', 'related') and self._RELATED_ENTITY_SCOPE == 'document':
            # print "Getting related content from documents"
            docs = self._get_docs()
            self._safe_get_related_entities_from_docs(docs)
            

    def _safe_update_hits_and_refs(self, ioc_resp, ref, key, condition, cur_date, date_condition):
        pub_date = ref['document']['published']
        date_update = self._safe_update_date(ioc_resp, pub_date, cur_date, key, date_condition and condition)
        if condition:
            # update hits
            self._safe_update_hits(ioc_resp, key + 'Hits', condition)
            # get recent frags
            self._safe_update_refs(ioc_resp, ref, 'Recent' + key, pub_date == date_update)
        return date_update
                    
    def _safe_update_date(self, ioc_resp, date, existing_val, key, condition):
        if condition and key in ioc_resp:
            ioc_resp[key] = date
        return date if condition else existing_val
    
    def _safe_update_hits(self, ioc_resp, key, condition):
        if condition and key in ioc_resp:
            ioc_resp[key] += 1

    def _safe_update_refs(self, ioc_resp, ref, key, condition):
        if condition:
            key_suffixes = {'Source': ref['document']['sourceId']['name'].replace('\n', ' ').replace('\r', ' '),
                            'Title': ref['document']['title'].replace('\n', ' ').replace('\r', ' '), 
                            'Fragment': ref['fragment'].replace('\n', ' ').replace('\r', ' '), 
                            'URL': ref['document']['url'] if 'url' in ref['document'] else ''}
            for suffix in filter(lambda suf: key + suf in ioc_resp, key_suffixes):
                ioc_resp[key + suffix] = key_suffixes[suffix]
                    
    def _get_all_references(self):
        refs = []
        seen_ids = set()
        edetails = {}
        for names in _chunks(self.iocs.keys(), 1000):
            q = {"instance": {"type": "Event",
                              "limit": 100000,
                              "searchtype": "scan"}}
            q['instance']['attributes'] = [[{"name": "Event.event_fragment", 'string': names}]]
            rfids = [self.iocs[name] for name in names if self.iocs[name]]
            q['instance']['attributes'][0].append({"name": "entities",
                                                   "entity": {"id": rfids}})
            # print len(self.iocs.keys()),
            for res in self.rfqapi.paged_query(q):
                refs.extend([inst for inst in res['instances'] if inst['id'] not in seen_ids])
                seen_ids.update([inst['id'] for inst in res['instances']])
                edetails.update({ eid: res['entities'][eid] for eid in res['entities'] if res['entities'][eid]['type'] in self._RELATED_ENTITY_TYPES})
        return refs, edetails

    def _get_docs(self):
        all_docs = set()
        for names in _chunks(self.iocs.keys(), 1000):
            q = {"instance": {"type": "Event"},
                 "output": {"count": {"axis": [{"name": "attributes.entities",
                                                "type": [self.entity_type],
                                                "aspect": "name"},
                                                "document"],
                                      "values": [self._INSTANCES_OR_DOCUMENTS]}}}
            q['instance']['attributes'] = [[{"name": "Event.event_fragment", 'string': names}]]
            rfids = [self.iocs[name] for name in names if self.iocs[name]]
            q['instance']['attributes'][0].append({"name": "entities",
                                                   "entity": {"id": rfids}})
            res = self.rfqapi.query(q)
            counts = res["counts"][0]
            if len(counts) != 0:
                for ioc in filter(lambda i: i in self.iocs, counts):
                    docids = counts[ioc].keys()
                    self.response[ioc]['DocumentIds'] = docids
                    all_docs.update(docids)
        return list(all_docs)

    def _safe_get_related_entities_from_frags(self, refs, edetails):
        ioc_to_rfid = self.iocs
        rfid_to_ioc = {}
        for ioc in filter(lambda i: ioc_to_rfid[i], ioc_to_rfid):
            rfid_to_ioc[ioc_to_rfid[ioc]] = ioc
        entities_to_lookup = set()
        for ref in refs:
            related_ents = ref['attributes'].get('extended_entities', ref['attributes'].get('entities', []))
            entities_to_lookup.update([eid for eid in related_ents if eid not in edetails])
        # print "Updating entity resolution"
        edetails.update(self._resolve_related_entities(list(entities_to_lookup)))
        # print "Updated related entities"
        for ref in refs:
            fragment = ref['fragment'].lower()
            # get related entities from reference
            related_ents = ref['attributes'].get('extended_entities', ref['attributes'].get('entities', []))
            # get entities mentioned
            rfids = filter(lambda ioc: ioc in rfid_to_ioc, related_ents)
            ioc_rfids = [rfid for rfid in rfids if rfid in rfid_to_ioc]
            # get string hits that aren't included in the entity hits
            other_hits = [ioc for ioc in ioc_to_rfid if (ioc in fragment and ioc_to_rfid[ioc] not in ioc_rfids)]
            iocs = [rfid_to_ioc[rfid] for rfid in ioc_rfids]
            for ioc in iocs + other_hits:
                ioc_resp = self.response[ioc]
                for ent in filter(lambda eid: eid in edetails and eid != ioc_resp['RFID'], related_ents):
                    etype, name = edetails[ent]['type'], edetails[ent]['name']
                    if name not in ioc_resp['Related' + etype]:
                        ioc_resp['Related' + etype].append(name)
                    if 'Related' + etype + 'Count' in ioc_resp:
                        ioc_resp['Related' + etype + 'Count'] = len(ioc_resp['Related' + etype])
                for etype in self._RELATED_ENTITY_TYPES:
                    if 'Related' + etype not in self.keys and 'Related' + etype in ioc_resp:
                        del ioc_resp['Related' + etype]

    def _resolve_related_entities(self, eids):
        if len(eids) == 0:
            return {}
        for ents in _chunks(eids, 1000):
            q = {"entity": {"id": ents,
                            "limit": 1001}}
            res = self.rfqapi.query(q)
        return { eid: res['entity_details'][eid] for eid in res['entity_details'] if res['entity_details'][eid]['type'] in self._RELATED_ENTITY_TYPES }

    def _safe_get_related_entities_from_docs(self, docs):
        for docids in _chunks(docs, 1000):
            q = {"instance": {"type": "Event",
                              "document": {"id": docids}},
                 "output": {"count": {"axis": ["document",
                                               {"name": "attributes.entities",
                                                "type": self._RELATED_ENTITY_TYPES,
                                                "aspect": "all"}],
                                      "values": [self._INSTANCES_OR_DOCUMENTS]}}}
            res = self.rfqapi.query(q)
            counts = res['counts'][0]
            for ioc in self.response:
                ioc_resp = self.response[ioc]
                for docid in filter(lambda did: did in counts, ioc_resp['DocumentIds']):
                    for asp_name in filter(lambda n: n != 'NONE', counts[docid]):
                        name, unused, etype = rf_agg_name_parser(asp_name)
                        if name == ioc: continue
                        # update related counts
                        ioc_resp['Related' + etype].append(name)
                        if 'Related' + etype + 'Count' in ioc_resp:
                            ioc_resp['Related' + etype + 'Count'] = len(ioc_resp['Related' + etype])
        for ioc in self.response:
            ioc_resp = self.response[ioc]
            if 'DocumentIds' not in self.keys and 'DocumentIds' in ioc_resp:
                del ioc_resp['DocumentIds']
            for etype in self._RELATED_ENTITY_TYPES:
                if 'Related' + etype not in self.keys and 'Related' + etype in ioc_resp:
                    del ioc_resp['Related' + etype]
    
    def _get_rfids(self):
        new_iocs = collections.OrderedDict()
        edetails = {}
        for names in _chunks(self.iocs, 500):
            if len(names) == 0: continue
            q = {"entity": {"name": names, 
                            "type": self.entity_type,
                            "limit": 501}}
            res = self.rfqapi.query(q)
            if len(res['entities']) == 0: continue
            for ent in res['entities']:
                edetails[res['entity_details'][ent]['name']] = ent
        for ioc in self.iocs:
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
