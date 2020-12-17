from elasticsearch import Elasticsearch
import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib

from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel

from summa.summarizer import summarize
from summa import keywords
import pymorphy2
import string

from flask import Flask, render_template

app = Flask(__name__)
matplotlib.use('AGG')

host = 'host.docker.internal'
port = 9200
index = "wall_posts"
client = Elasticsearch([{'host': host, 'port': port}])
elastic_done = False
analyze_done = False
dfdata = {}

def normalize_text(s, morph):
    ans = ""
    l = s.split()
    table = str.maketrans('', '', string.punctuation+'»«—')
    stripped = [w.translate(table) for w in l]
    for el in stripped:
        p = morph.parse(el)[0]
        if p.tag.POS in ["CONJ", "PREP", "PRCL", "NPRO", "PRED", "INTJ", "COMP", "ADVB"]:
            continue
        ans += p.normal_form + " "
    return ans[:-1]

def collect_prepare_data(client, index_):
	global elastic_done
	model = FastTextSocialNetworkModel(tokenizer=RegexTokenizer())
	morph = pymorphy2.MorphAnalyzer()
	print("Waiting for Elastic to init")
	while not elastic_done:
		try:
			info = json.dumps(client.info(), indent=4)
			print("Elasticsearch client info():", info)
			elastic_done = True
		except ConnectionError as err:
			print ("\nElasticsearch info() ERROR:", err)
			print ("\nThe client host:", host, "is invalid or cluster is not running")
			client = None
	dfdata = None
	if client != None:
		print("Waiting for Elastic to load data")
		elastic_done = True
		number_rows = 0
		while number_rows == 0:
			try:
				resp = client.search(
					index = index_,
					params = {"size" : 0}
				)
				number_rows = int(resp["hits"]["total"]["value"])
			except Exception:
				continue
		if number_rows != 0:
			resp = client.search(
				index = index_,
				params = {"size" : number_rows}
			)
			dfdata = {"timestamp": [], "keywords": [], "sentiment": []}
			for el in resp['hits']['hits']:
				try:
					text = el["_source"]["text"]
					message = [summarize(text, language='russian', ratio=0.2, words=15)]
					result = model.predict(message, k=1)
					kw = keywords.keywords(normalize_text(text, morph), language='russian', ratio=0.1, words=3).split()
					dfdata["timestamp"].append(datetime.fromtimestamp(el["_source"]["date"]))
					dfdata["keywords"].append(kw)
					dfdata["sentiment"].append(result[0])
				except Exception:
					continue
	return dfdata

def sentiment_analyse(dfdata):
	columns = ["sentiment_float"]
	# neutral, speech, negative, positive, skip - types of sentiment
	# positive - [1 - 2]
	# neutral/speech/skip - [0, 1]
	# negative - [-1, 0]
	sentiment_float = []
	for el in dfdata["sentiment"]:
		for key in el:
			if key == "positive":
				sentiment_float.append(1 + (el[key] if el[key] <= 1. else 1.))
			if key in ["neutral", "speech", "skip"]:
				sentiment_float.append(el[key] if el[key] <= 1. else 1.)
			if key == "negative":
				sentiment_float.append(-1 * (el[key] if el[key] <= 1. else 1.))
	
	df = pd.Series(data=sentiment_float, index=dfdata["timestamp"]).sort_index()
	fig = plt.figure(figsize=(150, 40))
	plt.tight_layout()
	plt.rcParams["font.size"] = "50"
	locs, labels = plt.yticks()
	plt.yticks([-1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0], ['strong negative', 'negative', 'strong neutral', 'neutral', 'almost positive', 'positive', 'strong positive'])
	plt.plot(df.index, df)
	fig.savefig('static/images/test_sentiment.png')

def keywords_stats(dfdata):
	words = {}
	all_words_count = len(dfdata["keywords"])
	for el in dfdata["keywords"]:
		for word in el:
			if word in words:
				words[word] += 1
			else:
				words[word] = 1
	words = list(dict(sorted(words.items(), key=lambda item: item[1], reverse=True)).items())
	words_stats = words[:9]
	top_count = sum([el[1] for el in words_stats])
	words_stats.append(("other words", all_words_count - top_count))
	index = [el[0] for el in words_stats]
	data = [el[1] for el in words_stats]
	df = pd.Series(data=data, index=index)
	fig = df.plot.pie(ylabel="", figsize=(50, 50), fontsize=65).get_figure()
	fig.savefig('static/images/test_keywords.png')

@app.route('/')
def hello():
	return render_template('index.html')

def if_error():
	print("Some errors, try to rebuild app")
	with open('templates/index.html', 'w') as f:
		f.write("<!DOCTYPE html><html><title>Trend Analyze</title><head></head><body><h1>Something went wring, try to rebuild app</h1></body></html>")

if __name__ == "__main__":
	dfdata = collect_prepare_data(client, index)
	if dfdata is not None:
		while not analyze_done:
			try:
				print("Waining for analyse")
				sentiment_analyse(dfdata)
				keywords_stats(dfdata)
				analyze_done = True
			except Exception:
				if_error()
		print("Analysed")
	else:
		if_error()
	app.run(host='0.0.0.0', port=5000)