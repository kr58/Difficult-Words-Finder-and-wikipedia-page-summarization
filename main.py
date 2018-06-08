import json
import xmltodict
import re
import collections
import codecs
import requests
from string import digits
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import urllib.request
import requests
from rake_nltk import Rake
from html.parser import HTMLParser
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from SPARQLWrapper import SPARQLWrapper, JSON
import wikipedia
import self_summarizer as summarizer
"""
MAX_HITS = "5"
sitename = None
QUESTION_BODY ="question_body"
QUESTION_TITLE ="question_title"
ANSWER_LIST ="answers"

def get_lookup_api_res_xml(query_word, max_hits):
    query=  "http://lookup.dbpedia.org/api/search/KeywordSearch?MaxHits="+max_hits+"&QueryString="+query_word
    print(query)
    r = requests.get(url = query)
    t =r.text
    return t

def cleanhtml(raw_html):
    print("RAW HTMl = ",raw_html)
    index_list=[-2]
    for i in range(0,len(raw_html)):
        if(raw_html[i]=='$' and raw_html[i+1]=='$'):
            index_list.append(i)
#    for m in re.finditer('\$\$',raw_html):
#        index_list.append(m.start())
    # print("MYLIA+ST=--------------------------------------",index_list)
    ans =""
    last=0
    for i in range(0,len(index_list),2):
        if(i+1<len(index_list)):
            ans+=raw_html[index_list[i]+2:index_list[i+1]]

    ans = helper_dollar(ans,'\$')
    cleanr = re.compile('<.*?>')
    ans = re.sub(cleanr, '', ans)
    return ans

def helper_dollar(stri,reg):
    index_list=[-1]
    for i in range(0,len(stri)):
        if(stri[i]=='$'):
            index_list.append(i)
    # print("MYLIA+ST=--------------------------------------",index_list)
    ans =""
    for i in range(0,len(index_list),2):
        if(i+1<len(index_list)):
            ans+=stri[index_list[i]+1:index_list[i+1]]
    return ans;

def get_answers(question_id):
    query=  "https://api.stackexchange.com/2.2/"+ "questions/"+question_id+"/answers?"+"site="+sitename+"&filter=withbody"
    #print("Query = ",query)
    #print(contents)
    r = requests.get(url = query)    
    data = r.json()
    return data
   
def get_keywords(string_data):
    r = Rake()
    r.extract_keywords_from_text(string_data)
    temp = r.get_ranked_phrases()  # To get keyword phrases ranked highest to lowest.
    return temp 
    # return string_data.split(' ')

def word_to_lookup(word, maxResultSize): #default max result size = 5
    res_xml = get_lookup_api_res_xml(word,maxResultSize)
    json_dump = (json.dumps(xmltodict.parse(res_xml)))
    temp = json.loads(json_dump)
    if(len(temp)>0 and "ArrayOfResult" in temp and "Result" in temp["ArrayOfResult"]):
        json_data = temp["ArrayOfResult"]["Result"]
    else:
        json_data = None
    return json_data
        
def query(link):
    global sitename
    parsed_link = urlparse(link)
    path = parsed_link.path
    path = path.split('/')
    qid = (path[2])
    sitename = parsed_link.hostname
    print(sitename)
    query=  "https://api.stackexchange.com/2.2/"+ "questions/"+qid+"?"+"site="+sitename+"&filter=withbody"
    r = requests.get(url = query)
    data = r.json()
    #print("QUEStION TITLE = ", data["items"][0]["title"] )
    
    question_title = data["items"][0]["title"] 
    question_body = data["items"][0]["body"]
    question_body = cleanhtml(question_body)
    print(question_body)
    data_dict = {}
    data_dict[QUESTION_BODY] = question_body
    answer_json = get_answers(qid)
    answers_list = []
    items_list = answer_json['items']
    for i in range(len(items_list)):
        answer = items_list[i]['body']
        answer = cleanhtml(answer)
        answers_list.append(answer)
    data_dict[ANSWER_LIST] = answers_list
    data_dict[QUESTION_TITLE] = question_title
    
    with open("data.json","w") as f:
        json.dump(data_dict,f,indent=4)
    return data_dict

def get_category_list(json_data):
    ret = []
    if( isinstance(json_data,dict)):
        json_data = [json_data]
        
    for result in json_data:
        tmp_ret = []
        if ("Categories" in result):
            categories = result["Categories"]
            if(categories is not None and "Category" in categories):
                category_list = categories["Category"]
                for label_uri_pair in category_list:
                    if(isinstance(label_uri_pair,dict) ):
	                    tmp_ret.append(label_uri_pair)
        ret.append((result["URI"],tmp_ret))
    return ret


def get_country_description(url, k):
	#query = "SELECT * WHERE {<http://dbpedia.org/page/"+word+"> <http://purl.org/dc/terms/subject> ?categories .}"
	#url = 'http://dbpedia.org/resource/Category:Elementary_geometry'
	broad = ""
	for i in range(k):
		if i == k-1:
			broad += "skos:broader?"
		else:
			broad += "skos:broader?/"

	query = "select distinct ?subcategory where {  <" + url + "> " + broad + "subcategory}"
	sparql = SPARQLWrapper("http://dbpedia.org/sparql")
	sparql.setReturnFormat(JSON)

	sparql.setQuery(query)  # the previous query as a literal string
	result = sparql.query().convert()
	#res = ast.literal_eval(result)
	final = []
	for i in result['results']['bindings']:
		final.append(i['subcategory']['value'])
	return final

def createMap(all_list):
	final = collections.OrderedDict()
	for i in all_list:
		for j in i:
			label = j[0]
			data = j[1]
			newData = collections.OrderedDict()
			for k in data:
				if isinstance(k, dict):
					newData[k['Label']] = get_country_description(k['URI'], 1)
			final[label] = newData

	with open ("try.json", 'w') as f:
		json.dump(final, f, indent=4)

	with open ("try.json", 'r') as f:
		final = json.load(f)

	Map = collections.OrderedDict()
	for key in final.keys():
		for word in final[key].keys():
			for i in final[key][word]:
				if i in Map.keys():
					if(key not in Map[i]):
						Map[i].append(key)
				else:
					Map[i] = []
					Map[i].append(key)

	with open ("map.json", 'w') as f:
	 	json.dump(Map, f, indent=4)
	with open ("map.json", 'r') as f:
		Map = json.load(f)

	maxi = 0
	index = ""
	for key in Map.keys():
		if maxi<len(Map[key]):
			maxi = len(Map[key])
			index = key

	print(key)




if __name__=='__main__':
    
    #----------- [ONLINE] uncomment to get data from web-------------
    print("Enter Link:")
    link = str(input());
    data_dict = query(link)
    #----------- [ONLINE] uncomment to get data from web-------------
    
    #----------- [OFFLINE] uncomment to load data from ofline--------
    #data_dict = json.load(open("data.json","r"))
    #----------- [OFFLINE] uncomment to load data from ofline--------
    
    
    question_body = data_dict[QUESTION_BODY]
    question_title = data_dict[QUESTION_TITLE]
    answers_list = data_dict[ANSWER_LIST]
    res_string = question_title+" "+question_body+" ";
    res_string.join(answers_list)
    temp = get_keywords(res_string)
    
    final_list = []
    for i in range(len(temp)):
        if(len(temp[i])>5):
            final_list.append(temp[i])    
    all_list = []
    for word in final_list:
        print("Word = ",word)
        json_data = word_to_lookup(word,MAX_HITS)
        if(json_data is None):
            continue
        category_list = get_category_list(json_data)
        all_list.append(category_list)
    print(all_list)
    #createMap(all_list)
"""





MAX_HITS = "5"
sitename = None
QUESTION_BODY ="question_body"
QUESTION_TITLE ="question_title"
ANSWER_LIST ="answers"



def get_lookup_api_res_xml(query_word, max_hits):
    query=  "http://lookup.dbpedia.org/api/search/KeywordSearch?MaxHits="+max_hits+"&QueryString="+query_word
    r = requests.get(url = query)
    t =r.text
    return t

def cleanhtml(raw_html):
    # index_list=[-2]
    # for i in range(0,len(raw_html)):
    #     if(i+1<len(raw_html) and raw_html[i]=='$' and raw_html[i+1]=='$'):
    #         index_list.append(i)
    # ans =""
    # for i in range(0,len(index_list),2):
    #     if(i+1<len(index_list)):
    #         ans+=raw_html[index_list[i]+2:index_list[i+1]]
    # ans = helper_dollar(ans)
    cleanr = re.compile('<.*?>')
    ans = re.sub(cleanr, '', raw_html)
    remove_digits = str.maketrans('', '', digits)
    ans = ans.translate(remove_digits)
    return ans

def helper_dollar(stri):
    index_list=[-1]
    for i in range(0,len(stri)):
        if(stri[i]=='$'):
            index_list.append(i)
    if(len(index_list)%2==0):
        print("ERRRRRRRRROR UNBALANCED DOLLAR")
    # print("MYLIA+ST=--------------------------------------",index_list)
    ans =""
    for i in range(0,len(index_list),2):
        if(i+1<len(index_list)):
            ans+=stri[index_list[i]+1:index_list[i+1]]
    
    return ans;

def get_answers(question_id):
    query=  "https://api.stackexchange.com/2.2/"+ "questions/"+question_id+"/answers?"+"site="+sitename+"&filter=withbody"
    #print("Query = ",query)
    #print(contents)
    r = requests.get(url = query)    
    data = r.json()
    return data
   
def get_keywords(string_data):
    # r = Rake()
    # r.extract_keywords_from_text(string_data)
    # temp = r.get_ranked_phrases()  # To get keyword phrases ranked highest to lowest.
    # return temp
    final = [] 
    search = re.compile("[A-Za-z-]+")
    #stop = set(stopwords.words('english'))
    token = search.findall(string_data)
    # for t in token:
    #     if t not in stop:
    #         final.append(t)
    return token

def word_to_lookup(word, maxResultSize): #default max result size = 5
    res_xml = get_lookup_api_res_xml(word,maxResultSize)
    json_dump = (json.dumps(xmltodict.parse(res_xml)))
    temp = json.loads(json_dump)
    if(len(temp)>0 and "ArrayOfResult" in temp and "Result" in temp["ArrayOfResult"]):
        json_data = temp["ArrayOfResult"]["Result"]
    else:
        json_data = None
    return json_data

def get_country_description(url, k):
	#query = "SELECT * WHERE {<http://dbpedia.org/page/"+word+"> <http://purl.org/dc/terms/subject> ?categories .}"
	#url = 'http://dbpedia.org/resource/Category:Elementary_geometry'
	broad = ""
	for i in range(k):
		if i == k-1:
			broad += "skos:broader?"
		else:
			broad += "skos:broader?/"

	query = "select distinct ?subcategory where {  <" + url + "> " + broad + "subcategory}"
	sparql = SPARQLWrapper("http://dbpedia.org/sparql")
	sparql.setReturnFormat(JSON)

	sparql.setQuery(query)  # the previous query as a literal string
	result = sparql.query().convert()
	#res = ast.literal_eval(result)
	final = []
	for i in result['results']['bindings']:
		final.append(i['subcategory']['value'])
	return final

def createMap(all_list):
	print('Parsing Data')
	final = collections.OrderedDict()
	for i in all_list:
		for j in i:
			label = j[0]
			data = j[1]
			newData = collections.OrderedDict()
			for k in data:
				if isinstance(k, dict):
					newData[k['Label']] = get_country_description(k['URI'], 1)
			final[label] = newData

	with open ("try.json", 'w') as f:
		json.dump(final, f, indent=4)

	with open ("try.json", 'r') as f:
		final = json.load(f)

	print('Creating mapping')

	Map = collections.OrderedDict()
	for key in final.keys():
		for word in final[key].keys():
			for i in final[key][word]:
				if i in Map.keys():
					if key not in Map[i]:
						Map[i].append(key)
				else:
					Map[i] = []
					Map[i].append(key)

	with open ("map.json", 'w') as f:
	 	json.dump(Map, f, indent=4)
	with open ("map.json", 'r') as f:
		Map = json.load(f)

	print('Done')

	maxi = 0
	index = []
	for key in Map.keys():
		if maxi<=len(Map[key]):
			if(maxi == len(Map[key])):
				index.append(key)
			else:
				index = []
				index.append(key)
			maxi = len(Map[key])

	print(index)
	return Map, index
        
def query(link):
    global sitename
    parsed_link = urlparse(link)
    path = parsed_link.path
    path = path.split('/')
    qid = (path[2])
    sitename = parsed_link.hostname
    print(sitename)
    query=  "https://api.stackexchange.com/2.2/"+ "questions/"+qid+"?"+"site="+sitename+"&filter=withbody"
    r = requests.get(url = query)
    data = r.json()
    #print("QUEStION TITLE = ", data["items"][0]["title"] )
    tot_data = ""
    question_title = data["items"][0]["title"]
    tot_data+=question_title
    question_body = data["items"][0]["body"]
    tot_data+=question_body
    answer_json = get_answers(qid)
    items_list = answer_json['items']
    for i in range(len(items_list)):
        answer = items_list[i]['body']
        tot_data+=answer
    return tot_data

def get_category_list(json_data):
    ret = []
    if( isinstance(json_data,dict)):
        json_data = [json_data]
        
    for result in json_data:
        tmp_ret = []
        if ("Categories" in result):
            categories = result["Categories"]
            if(categories is not None and "Category" in categories):
                category_list = categories["Category"]
                for label_uri_pair in category_list:
                    if(isinstance(label_uri_pair,dict)):
                        tmp_ret.append(label_uri_pair)
        ret.append((result["URI"],tmp_ret))
    return ret

def removeExtras(final_list):
    with open("detf.json", 'r') as f:
        newDic = json.load(f)

    stemmer = PorterStemmer()

    add = []
    delete = []
    t=[]
    for i in final_list:
    	t.append(i)

    for i in range(len(t)):
    	norm = t[i].lower()
    	word = stemmer.stem(norm)
    	if word in newDic.keys():
    		if newDic[word]>400:
    			delete.append(i)
    	else:
    		x = word.split(' ')
    		if len(x) == 2:
    			x[0] = stemmer.stem(x[0].lower())
    			if x[0] in newDic.keys() and x[1] in newDic.keys() and newDic[x[0]] > 400 and newDic[x[1]] > 400:
    				delete.append(i)
    			#if x[0] in newDic.keys() and newDic[x[0]] < 400:

    		elif len(x) > 2:
    			delete.append(i)

    final_word_list = []
    for i in range(len(final_list)):
        if i not in delete:
            final_word_list.append(final_list[i])

    return final_word_list

if __name__=='__main__':
    
    #----------- [ONLINE] uncomment to get data from web-------------
    print("Enter Link:")
    link = str(input());
    tot_data = query(link)
    #----------- [ONLINE] uncomment to get data from web-------------
    
    #----------- [OFFLINE] uncomment to load data from ofline--------
    #data_dict = json.load(open("data.json","r"))
    #----------- [OFFLINE] uncomment to load data from ofline--------
    print("CLEANED DATA = ")
    cleaned_data = cleanhtml(tot_data)
    #print(cleaned_data)
    temp = get_keywords(cleaned_data)
    
    words = " ".join(temp)
    
    r = Rake()
    r.extract_keywords_from_text(words)
    temp = r.get_ranked_phrases()

    final_list = []
    for i in range(len(temp)):
        if(len(temp[i])>3):
            final_list.append(temp[i])

    print(final_list)
    print(len(final_list))
    final_word_list = removeExtras(final_list)
   
    all_list = []
    for word in final_word_list:
        print("Word = ",word)
        json_data = word_to_lookup(word,MAX_HITS)
        #print("Word = ",word, "   ", len(json_data))
        if(json_data is None):
            continue
        category_list = get_category_list(json_data)
        all_list.append(category_list)

    Map, index = createMap(all_list)
    summary_list = []
    for i in index:
        j = Map[i]
        for x in j:
            summary_list.append(x)

    summary_list = list(set(summary_list))
    print("Summary List-----------",summary_list)
    for link in summary_list:
        parsed_link = urlparse(link)
        path = parsed_link.path
        path = path.split('/')
        pageId = (path[-1])

        try:
            summary = wikipedia.summary(pageId)
            # print("----------------Summary-----------------------")
            # print(summary)
            # print("----------------------------------------------")
            ss = summarizer.SimpleSummarizer()
            # f = open('text','r')

            summarized_summary = ss.summarize( summary ,5)
            final_summary = ""
            print("\n")
            print("-----------------------     " + pageId + "     ------------------------------")
            for line in summarized_summary:
                if(line!="\n"):
                    final_summary+=line
            final_summary = re.sub(' +', ' ',final_summary)
            print(final_summary)
            print("---------------------------------------------------------------------")
            print("\n")
        except Exception as e:
            print("Unable To find Page on Wikipedia......")
        

    # index = createMap(None)
    
    # with open ("d.json", 'r') as f:
    #     tf = json.load(f)

    # avg = 0
    # newDic = collections.OrderedDict()
    # for key in tf.keys():
    #     newDic[key]=len(tf[key])
    #     avg+=len(tf[key])

    # print(avg/len(tf.keys()))

    # with open ("detf.json", 'w') as f:
    # 	json.dump(newDic, f, indent=4)







































        

"""
main_data = []
class MyHTMLParser(HTMLParser):
    def __init__(self):
        #super() does not work for this class
        HTMLParser.__init__(self)
        self.tag_stack = []
        self.attr_stack = []
        self.count = -1
        self.chk1 = False

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr[0] == 'class' and attr[1] == 'question-hyperlink':
                #print ("     attr:", attr)
                self.tag_stack.append(str(tag))
                self.count = 0
                self.
            elif (attr[0] == 'class' and attr[1] == 'post-text'):
                self.tag_stack.append(str(tag))
                self.count = 0
            else:
                self.tag_stack.append(str(tag))
                count+=1

    def handle_endtag(self, tag):
    	if(len(self.tag_stack)>0):
    		if(count != -1):
    			count -= 1
    		else:
    			self.tag_stack.pop()

    def handle_data(self, data):
    	if(len(self.tag_stack) > 0 and self.tag_stack[len(self.tag_stack)-1] != 'script' and data!='\n' and self.chk1 == True):
    		print(data)
    		main_data.append(data.strip(' '))

def parse(word):
	charRe = re.compile("[A-Za-z0-9~]+")
	string = charRe.findall(word)
	if(len(string) == 0):
		return None
	return string[0]


"""
#html = codecs.open("./abc.html", 'r', encoding = 'utf-8', errors = 'ignore')
# parser = MyHTMLParser()
# parser.feed(html.read())
#parser.feed('<p><a class=link href=#main>tag soup</p ></a>')
"""
stemmer = PorterStemmer()
final = []
for i in main_data:
	t=''
	if(i!='\n'):
		t = i.strip(' \n ')
	if(t!=''):
		x = t.split(' ')
		for j in x:
			final.append(j)



#print(final)
data = []
for i in final:
	x = parse(i)
	if x != None:
		data.append(x)

print(data)"""
#print(get_country_description("xx"))
# for i in final:
# 	print(get_country_description(i))"""

# soup = BeautifulSoup(html, 'lxml')
# text = soup.find('div', attrs={'class':'post-text'})
# print(text)
# for i in soup.find_all('head'):
#     for j in i.find_all('title'):
#         print(j)

#for i in soup.find_all('p'):
#	print(i)