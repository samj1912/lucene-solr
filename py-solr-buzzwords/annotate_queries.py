#!/usr/bin/env python

from flask import Flask
from flask import request
from flask import render_template 
import json
import pysolr
import os
from dataset import Dataset
from rankers import Rankers

app = Flask(__name__)
MAX_RESULTS = 30
dataset = Dataset()
rankers = Rankers()

@app.route("/query",  methods=['POST', 'GET'])
def query():
    global solr
    q = request.args.get('q') 
    try:
       results = rankers.query('default', q) 
    except Exception as e:
        print e
        return "Cannot connect with Lucene/Solr", e
    return render_template('annotate.html', query=q, results=results)

@app.route("/annotate",  methods=['POST', 'GET'])
def annotate():
    global solr
    q = request.args.get('q') 
    rank = int(request.args.get('rank'))
    try:
       results = rankers.query('default', q) 
    except Exception as e:
        print e
        return "Cannot connect with Lucene/Solr"
    if len(results.docs) == 0:
        return "No results for query "+q
    rank = rank % min(MAX_RESULTS, len(results.docs))
    article = results.docs[rank] 
    rel = dataset.get_relevance(q, article['wikiTitle'])
    dataset.annotate(q, article['wikiTitle'], rel)
    return render_template('annotate_res.html', query=q, article=article, rank=rank, rel=rel)


@app.route("/store",  methods=['POST', 'GET'])
def store():
    q = request.args.get('q') 
    rank = int(request.args.get('rank'))
    rel = int(request.args.get('rel'))
    results = rankers.query('default', q) 
    doc = results.docs[rank]
    dataset.annotate(q, doc["wikiTitle"], rel)
    return 'ok'


if __name__ == "__main__":
    import threading, webbrowser
    port = 5000  
    url = "http://localhost:{0}/annotate?q=berlin&rank=0".format(port)
    threading.Timer(1.25, lambda: webbrowser.open(url) ).start()
    app.run()
    

