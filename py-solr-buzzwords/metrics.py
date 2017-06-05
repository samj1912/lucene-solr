#!/usr/bin/env python

from rankers import Rankers

def _get_relevant_docs(dataset, query, results,  k=-1):
    res_size = len(results)
    dat_size = len(dataset)
    if res_size == 0 or k == 0 or dat_size == 0: return 0
    if k >= 0: results = results[0: min(k, res_size)]
    relevant = 0
    for result in results:
        if dataset.is_relevant(query, result): relevant+=1
    return relevant

def precision(dataset, query, results, k=-1):
    relevant = _get_relevant_docs(dataset, query, results, k) 
    res_size = min(len(results),k)
    name = "P"
    if k >= 0: name+='@'+str(k)
    if res_size == 0: return 0.0, name
    return float(relevant)/float(res_size), name 

def recall(dataset, query, results, k=-1):
    dataset_relevant = dataset.get_relevant_docs(query)
    query_relevant = _get_relevant_docs(dataset, query, results, k) 

    name = "R"
    if k >= 0: name+='@'+str(k)

    if dataset_relevant == 0: return 0.0, name
    return float(query_relevant) / float(dataset_relevant), name

def fmeasure(dataset, query, results, k=-1):
    p,_ = precision(dataset, query, results, k)
    r,_ = recall(dataset, query, results, k)
    name = "F"
    if k >= 0: name+='@'+str(k)
    if (p*r) == 0: return 0.0, name
    return 2*p*r/(p+r), name

def avg(metric, dataset, queries, k=-1):
    partials = {} 
    for q in queries:
        partials[q], name = metric(dataset, q, queries[q], k) 
    return sum(partials.values())/len(partials),name

def evaluate_ranker(ranker, dataset, metrics, k=-1):
    values = {}
    queries = {}
    rankers = Rankers()
    for query in dataset.get_queries():
        queries[query] = rankers.topWikiTitles(ranker, query)
        for metric in metrics:
            value, name = avg(metric, dataset, queries, k) 
            values[name] = value 
    return values
    
if __name__ == '__main__':
    import sys
    from dataset import Dataset
    from rankers import Rankers
    
    dataset = Dataset()
    rankers = Rankers()
    ranker = sys.argv[1]
    queries = {}
    for query in dataset.get_queries():
        queries[query] = rankers.topWikiTitles(ranker, query)
    for k in [1,2,3,10]:
        for metric in precision, recall, fmeasure:
            value, name = avg(metric, dataset, queries, k)
            print name,'\t', value

        


    
