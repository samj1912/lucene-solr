## Berlin Buzzword Demo

### install the demo

from the folder `solr` run:

  ant dist
  ant server
  bin/solr -e wikipedia -Dsolr.ltr.enabled=true

then download and index the dump: 
	
  cd py-solr-buzzwords
  # get the simple wikipedia dump
  wget https://github.com/bloomberg/lucene-solr/releases/download/1.0.0/simplewiki-20170501-pages-articles.json.gz 
  ./index_wikipedia.py simplewiki-20170501-pages-articles.json.gz

install the needed python packages: 

  pip install pysolr
  pip install flask

### running the demo
run:

  cd py-solr-buzzwords
  ./demo.py 

## 1. Collect query document judgements

You can mark results us relevant, and add new query to the dataset (stored in `dataset.json`).

  ./annotate_queries.py

## 2. Extract query-document features

First you need to load the features in solr: 

  curl -XPUT 'http://localhost:8983/solr/wikipedia/schema/feature-store' --data-binary "@./features.json" -H 'Content-type:application/json'

Then, you can extract features for a query-document by using the ltr document document transformer, for example try the `berlin` query:

  http://localhost:8983/solr/wikipedia/select?indent=on&q=berlin&wt=json&fl=title,score,[features%20efi.query=berlin]

## 3. Train a linear model

The script will get the features for each query/document` in the `dataset.json` file and will produce a training file that will be use to train a model. It will train a model, and upload it on solr. 

  ./train_linear_model.py

If you run the script and then run (or refresh) `demo.py`, you will see the performance of the model on the right side of the screen. 
If you click on the name of the model, you will see how documents are ranked using that model. 

## 4. Train a tree model

Same as above, but this time we will train a tree model (LambdaMart).

  ./train_linear_model.py

LambdaMart is trained to optimize a particular quality metric, by default it will optmize Precision at 10, but you can change the metric, e.g.:

  ./train_linear_model.py P@1 
  ./train_linear_model.py NDCG@10

will optimize the model for Precision at 1 or Normalized Discounted Cumulative Gain [1].

You can also increase the number of trees used, e.g.,

  ./train_linear_model.py P@1 100
  ./train_linear_model.py NDCG@10 1000

more trees will probably make the tree more precise, but slowing down the performance at query time. 

[1] https://en.wikipedia.org/wiki/Discounted_cumulative_gain


  








