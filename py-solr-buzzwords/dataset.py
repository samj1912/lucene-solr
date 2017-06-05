
import json
import os

class Dataset:

    def __init__(self, name='dataset'):
        self.name = name
        self.filename = name+".json"
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as fin:
                self.dataset = json.load(fin)
        else:
            self.dataset = {}

    def __len__(self):
        return len(self.dataset)

    def annotate(self, query, doc, rel): 
        if query not in self.dataset:
            self.dataset[query] = {}
        docs = self.dataset[query]
        docs[doc] = rel
        self.dump()

    def is_relevant(self, query, doc):
        return self.get_relevance(query, doc) > 0

    def get_relevance(self, query, doc):
        if query not in self.dataset:
            return 0 
        if doc not in self.dataset[query]:
            return 0 
        return self.dataset[query][doc]

    def get_docs(self, query):
        return self.dataset[query] 

    def get_relevant_docs(self, query):
        count = 0
        for doc in self.get_docs(query):
            if self.is_relevant(query, doc):
                count+=1
        return count

    def get_queries(self):
        queries = self.dataset.keys()
        queries.sort()
        return queries

    def dump(self): 
        for query in self.get_queries():
            if self.get_relevant_docs(query) == 0:
                del self.dataset[query] 
        with open(self.filename, 'w') as fout:
            json.dump(self.dataset, fout, indent=4, sort_keys=True)

        
            
        
