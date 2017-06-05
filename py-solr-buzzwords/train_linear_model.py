#!/usr/bin/env python
import os
import json
import pysolr
from dataset import Dataset
from rankers import Rankers
import time

if __name__ == "__main__":

    feature_names = [] 
    dataset = Dataset()
    rankers = Rankers()
    model_name = "linear-model-"+str(int(time.time()))
    output = 'last-training.txt' 
    with open(output,'w') as fout: 
        for qid,query in enumerate(dataset.get_queries()):
            results = rankers.query('default', query, fl=['wikiTitle','score','[features efi.query='+query+']']) 
            for doc in results:
                docid = doc["wikiTitle"]
                if dataset.is_relevant(query, docid): rel=1000
                else: rel = -1
                features = doc["[features]"] 
                fvalues = map(lambda x : x.split("=")[1], features.split(","))
                feature_names = map(lambda x : x.split("=")[0], features.split(","))
                fid = range(len(fvalues))
                feature_str = " ".join(fvalues)
                fout.write(" ".join([str(rel),str(qid), " "])+feature_str+"\n")
                if rel > 0:
                    for i in range(30): fout.write(" ".join([str(rel),str(qid), " "])+feature_str+"\n") 

    import numpy as np
    
    data = np.loadtxt(output)
    y = data[:, 0]
    x = data[:, 2:]
    
    weights = np.polyfit(y, x, 1)[0].tolist()
    print "Linear Model\n  ", "\t \n+ ".join(map(lambda (w, name): str(w)+"\t* "+name, zip(weights, feature_names)))
    
    model = {} 
    model["class"] = "org.apache.solr.ltr.model.LinearModel"
    model["name"] = model_name 
    model["features"] = [] 
    for name in feature_names: 
        model["features"].append({"name": name})
    model["params"] = {
            "weights" : {
             }
    } 
    for pos, value in enumerate (weights): 
        model["params"]["weights"][feature_names[pos]] = value
    
    import requests
    import sys
    url = 'http://localhost:8983/solr/wikipedia/schema/model-store'
    headers = {"content-type": "application/json"}
    r = requests.put(url, data=json.dumps(model), headers=headers)
    if r.status_code != 200:
        print "Error uploading the model",r
        sys.exit(-1)

    ltr_ranker = {}
    rq = "{!ltr model=%s reRankDocs=%d efi.query=$query}" % (model_name, 30) 
    ltr_ranker["rq"] = rq

    rankers.add_ranker(model_name, ltr_ranker)

    ltr_ranker = {}
    rq = "{!ltr model=%s reRankDocs=%d efi.query=$query}" % (model_name, 30) 
    ltr_ranker["rq"] = rq

    rankers.add_ranker(model_name, ltr_ranker)

    print "Loaded model: ",model_name


    
    




