#!/usr/bin/env python
import sys
import gzip
import json
import pysolr


COMMIT_FREQ = 1000 
solr = pysolr.Solr('http://localhost:8983/solr/wikipedia', timeout=10)
count = 0
solr.delete("*:*")
solr.commit()
print "Index cleaned"
print "Indexing"
articles = []
with gzip.open(sys.argv[1],'r') as fin:
    for line in fin:
        
        article = json.loads(line)
        def remove(field): 
            if field in article: del article[field]
        article['id'] = article['wikiTitle']
        for field in ['wid','externalLinks','tables','links','templates','infobox','categories','namespace']: 
            remove(field)
        if 'paragraphs' in article and len(article['paragraphs']) > 0:
            article['description'] = article['paragraphs'][0]
        if article["type"] == "REDIRECT":
            continue
        try:
            articles.append(article) 
        except Exception as e:
            print e
            print "Article: ",json.dumps(article)
            continue
        count+=1
        print 'processed {0} articles\r'.format(count), 
        sys.stdout.flush()
        if count % COMMIT_FREQ == 0: 
            solr.add(articles)
            solr.commit() 
            articles = []

solr.add(articles)
solr.commit()
