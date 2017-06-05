#!/usr/bin/env python 
from flask import Flask
from flask import request
from flask import render_template 
import json
import pysolr
import os
from dataset import Dataset
from rankers import Rankers
import metrics 

app = Flask(__name__)
dataset = Dataset()
rankers = Rankers()     

@app.route("/",  methods=['POST', 'GET'])
def query():
    ranker_name = request.args.get('ranker') 
    if ranker_name == None: ranker_name = 'default'
    results = {}
    relevance = {}
    rankers = Rankers()
    for q in dataset.get_queries(): 
        relevance[q] = {}
        try:
            res = rankers.topWikiTitles(ranker_name, q)
            for doc in res: 
                if dataset.is_relevant(q, doc):
                    relevance[q][doc]="relevant"
                else:
                    relevance[q][doc]="not_relevant"
            results[q] = res
        except Exception as e:
            print "ERROR", e
            return "Cannot connect with Lucene/Solr - "+str(e)
        
    rankers_names = rankers.get_rankers()
    m = [ metrics.precision, metrics.recall, metrics.fmeasure ] 
    performance = {}
    for ranker in rankers_names:
        performance[ranker] = metrics.evaluate_ranker(ranker, dataset, m, 1)
        performance[ranker].update(metrics.evaluate_ranker(ranker, dataset, m, 10))
    m = ["P@1","R@1","F@1", "P@10", "R@10", "F@10"]
    return render_template('demo.html', results=results, relevance=relevance, rankers=performance, metrics=m, current=ranker_name)

@app.route("/store",  methods=['POST', 'GET'])
def store():
    q = request.args.get('q') 
    doc = request.args.get('doc')
    if doc == None or q == None: 
        return 'missing args' 
    rel = (dataset.get_relevance(q, doc) + 1) % 2 
    dataset.annotate(q,doc,rel)
    return 'ok'


if __name__ == "__main__":
    import threading, webbrowser
    port = 5000  

    url = "http://localhost:{0}/".format(port)
    #url = "http://localhost:{0}/annotate?q=berlin&rank=0".format(port)
    threading.Timer(1.25, lambda: webbrowser.open(url) ).start()
    app.run()
    

