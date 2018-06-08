#! /usr/bin/python3
from urllib.parse import urlparse
import urllib.request
import requests
import json
# query=  "https://api.stackexchange.com/2.2/"+ "questions/"+question_id+"/answers?"+"site="+sitename+"&filter=withbody"

query = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&redirects=1&titles="
x = input("Enter Title: ")

query = query + x 
r = requests.get(url = query)    
data = r.json()
with open ('wiki.json','w') as f:
	json.dump(data,f,indent=4)
print (data)