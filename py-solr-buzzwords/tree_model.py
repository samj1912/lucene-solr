#!/usr/bin/env python
import lxml.etree
import json


class RankLibModel:
    
    def _parse_split(self, split, tree):
        pos = split.get('pos')
        if split.find("output") != None:
            subtree = {} 
            subtree['value'] = split.find("output").text.strip()
            tree[pos] = subtree
            return
        if pos == None: 
            feature_id = int(split.find("feature").text)-1
            tree['feature'] = self.feature_names[feature_id] 
            tree['threshold'] = split.find("threshold").text.strip()
        else:
            subtree = {}
            feature_id = int(split.find("feature").text)-1
            subtree['feature'] = self.feature_names[feature_id] 
            subtree['threshold'] = split.find("threshold").text
            tree[pos] = subtree
            tree = subtree
        splits = split.findall("split")
        if splits!= None: 
            for split in splits:
                self._parse_split(split, tree)

    def get_model(self):
        return self.model
         
    def __init__(self, name, ranklib_model, feature_names):
        self.model = {} 
        self.model['name'] = name
        self.model['store'] = "_DEFAULT_" 
        self.model['class'] = "org.apache.solr.ltr.model.MultipleAdditiveTreesModel" 
        self.model['params'] = {}
        trees = [] 
        self.model['params']['trees'] = trees 
        self.feature_names = feature_names
        self.model["features"] = []
        for f in feature_names: self.model["features"].append({"name": f })
        with open(ranklib_model, 'r') as fin: 
            lines = fin.readlines()
            lines = filter(lambda line: not line.startswith('##'), lines)
            xmlcontent = ''.join(lines)
        forest =  lxml.etree.fromstring(xmlcontent)
        for tree in forest: 
            w = tree.get("weight").strip()
            split = tree.find("split")
            t = {} 
            if split != None:
                self._parse_split(split, t)
            e = {
                    "weight": w,
                    "root" : t
                }
            trees.append(e)
    
    def dump(self, filename):
        with open(filename, 'w') as fout:
            json.dump(self.model, fout, indent=4, sort_keys=False)

if __name__ == "__main__":
    t = RankLibModel("model-test", "model.xml", range(20))
    
    t.dump("test.json")
        
