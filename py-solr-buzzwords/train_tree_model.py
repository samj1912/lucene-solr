#!/usr/bin/env python 
import os
import json
import pysolr
from dataset import Dataset
from rankers import Rankers
import re
import time
from tree_model import RankLibModel 


if __name__ == "__main__":

    feature_names = [] 
    dataset = Dataset()
    rankers = Rankers()
    output = 'last-training-file.svm' 
    with open(output,'w') as fout: 
        for qid,query in enumerate(dataset.get_queries()):
            results = rankers.query('default', query, fl=['wikiTitle','score','[features efi.query='+query+']'])
            for doc in results:
                
                docid = doc["wikiTitle"]
                if dataset.is_relevant(query, docid): rel = dataset.get_relevance(query, docid) 
                else: rel = 0 
                features = doc["[features]"]
                fvalues = map(lambda x : x.split("=")[1], features.split(","))
                feature_names = map(lambda x : x.split("=")[0], features.split(","))
                fid = range(len(fvalues))
                feature_str = " ".join(map(lambda (k,v): str(k+1)+":"+v, zip(range(len(fvalues)),fvalues)))
                fout.write(" ".join([str(rel),"qid:"+str(qid)])+" "+feature_str+"\n")
    

    import sys
    
    if len(sys.argv) > 1:
        metric_to_optimize = sys.argv[1]

    else:
        metric_to_optimize = "P@10"
    trees = 100
    if len(sys.argv) > 2:
        trees = int(sys.argv[2])

    print "Metric to optimize ", metric_to_optimize 
    
    model_name = "tree-model-"+metric_to_optimize+"-trees-"+str(trees)+"-"+str(int(time.time()))
    
    # train using ranklib
    ranklib_model = 'model.xml'
    os.system("java -jar RankLib.jar -train "+output+" -test "+output+" -validate "+output+" -ranker 6 -metric2t "+metric_to_optimize+" -shrinkage 0.05 -tc 1024  -tree "+str(trees)+" -estop 100 -save "+ranklib_model)
    m = RankLibModel(model_name, ranklib_model, feature_names)
    m.dump( "last-lambdamart-model.json" ) 
    # load the model on solr
    import requests
    url = 'http://localhost:8983/solr/wikipedia/schema/model-store'
    headers = {"content-type": "application/json"}
    r = requests.put(url, data=json.dumps(m.get_model()), headers=headers)
    if r.status_code != 200:
        print r.text
        print "Error uploading the model"
        sys.exit(-1)
    
    ltr_ranker = {}
    rq = "{!ltr model=%s reRankDocs=%d efi.query=$query}" % (model_name, 30) 
    ltr_ranker["rq"] = rq

    rankers.add_ranker(model_name, ltr_ranker)

    print "Loaded model: ",model_name
