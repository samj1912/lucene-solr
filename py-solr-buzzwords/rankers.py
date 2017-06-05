#!/usr/bin/env python

import json
import pysolr

MAX_RESULTS = 30

def _get_or_default(ranker, name, default):
    if name in ranker: return ranker[name]
    return default

class Rankers:
    def __init__(self, rankers_file='rankers.json'):
        self.rankers_file = rankers_file
        self.rankers = json.load(open(rankers_file, 'r'))

    def add_ranker(self, name, ranker):
        self.rankers[name] = ranker
        with open(self.rankers_file, 'w') as fout:
            json.dump(self.rankers, fout, indent=2, sort_keys=True)

    def get_rankers(self):
        return self.rankers.keys()

    def query(self, ranker, query, fl=['wikiTitle','score']):
        ranker = self.rankers[ranker]
        solr_url = _get_or_default(ranker,  'solr_url','http://localhost:8983/solr/wikipedia')
        search_handler = _get_or_default(ranker, 'search_handler', '/select')
        solr = pysolr.Solr(solr_url, timeout=10, search_handler=search_handler)
        rows = _get_or_default(ranker, 'rows', MAX_RESULTS)
        rq = _get_or_default(ranker, 'rq', None)
        defType = _get_or_default(ranker, 'defType', None)

        params = {}
        params['fl'] = fl
        params['rows'] = rows
        if defType: params['defType'] = defType
        if rq: 
            params['rq'] =  rq.replace('$query', query)
        results = solr.search(query, **params)
        return results 
    
    def topWikiTitles(self, ranker, query):
        return map(lambda x: x['wikiTitle'], self.query(ranker, query, fl=['wikiTitle']))

                
if __name__ == '__main__': 
    import sys
    ranker = sys.argv[1]
    query = sys.argv[2] 
    rankers = Rankers()
    print json.dumps(rankers.topWikiTitles(ranker, query), indent=4)
    
        

