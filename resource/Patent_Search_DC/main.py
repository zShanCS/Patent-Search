from __future__ import absolute_import
import os
from time import time
from tracemalloc import start
from scipy.spatial.distance import cosine
import numpy as np
import pickle
from Patent_Search_DC.clean_text import *
import pandas as pd
import grequests
from bs4 import BeautifulSoup, SoupStrainer
import re
from unidecode import unidecode
import threading



"""## 6.3. Using Cosine Distance Similarity to Retrieve Information"""

print(os.listdir('./'))
vect = pickle.load(open("./Patent_Search_DC/vect.pickle", "rb"))
vect_text = pickle.load(open("./Patent_Search_DC/vect_text.pickle", "rb"))

terms_rep = pickle.load(open("./Patent_Search_DC/terms_rep.pickle", "rb"))
docs_rep = pickle.load(open("./Patent_Search_DC/doc_rep.pickle", "rb"))

df_merged = pd.read_csv('./Patent_Search_DC/final_patents_dataset.csv')
df_merged = df_merged.iloc[: , 1:]
df1 = df_merged.head(5000)
print(df1.head())
print(df1.columns)
print("Data is loaded! Query is executing! ")


def nospecial(text):
  text = re.sub("â", "",text)
  text = re.sub("- Google Patents", "",text)
  return text
 

# This is a function to generate query_rep
def lsa_query_rep(query):
    word_list = []
    for word in clean_text(query).split(' '):
        if word in vect.vocabulary_.keys():
            word_list.append(word) 
    if word_list:
        query_rep = [vect.vocabulary_[x] for x in word_list]
        print(query_rep)
        query_rep = np.mean(terms_rep[query_rep],axis=0)
        return query_rep
    else:
        print("No results found! Please try again.")
        return None


def get_rankings(query, count):
    query_rep = lsa_query_rep(query)
    if query_rep is not None:

        query_doc_cos_dist = [cosine(query_rep, doc_rep) for doc_rep in docs_rep]
        query_doc_sort_index = np.argsort(np.array(query_doc_cos_dist))

        print_count = 0
        
        list_res = []
        urls = []
        titles = []
        for rank, sort_index in enumerate(query_doc_sort_index):
            url = 'https://patents.google.com/patent/US' + df1['patent_id'][sort_index]
            list_res.append({
                'score': 1 - query_doc_cos_dist[sort_index],
                'text' : (df1['text'][sort_index])[:100] + '.....',
                'docid': df1['patent_id'][sort_index],
                'url'  : url,
                'title': ''
            })
            urls.append(url)
            print ('Rank : ', rank, ' Consine : ', 1 - query_doc_cos_dist[sort_index],' Link : ', 'https://patents.google.com/patent/US' + df1['patent_id'][sort_index])
            if print_count == count :
                break
            else:
                print_count += 1

        # making requests instance
        print('SENDING BS4 REQUESTS')
        print(urls)
        rs = (grequests.get(u) for u in urls)
        reqs = grequests.map(rs)
        # print("BS4 REquests completed")
        # # using the BeautifulSoup module
        # start_time = time()
        # for idx,req in enumerate(reqs):
        #     soup = BeautifulSoup(req.text, 'html.parser')
        #     for title in soup.find_all('title'):
        #         x = str(unidecode(nospecial(title.get_text())))
        #     if '\n' in x:
        #         x = x.split('\n')[0]
        #     title = x.rstrip()
        #     print(title)
        #     titles.append(title)
        # print("--- %s seconds ---" % (time() - start_time))
        def get_title_from_req(idx,docid, req, output_dict):
            print(idx,' running' ,req,output_dict)
            starttime = time()
            parsetime_start = time()
            soup = BeautifulSoup(req.text, 'html.parser', parse_only=SoupStrainer('title'))
            parse_time = time() - parsetime_start
            soup_find_res = soup.find('title')
            find_time_start = time()
            for title in soup_find_res:
                x = str(unidecode(nospecial(title.get_text())))
            find_time = time() - find_time_start
            if '\n' in x:
                x = x.split('\n')[0]
            title = x.rstrip()
            output_dict[idx]=title
            print(idx,f" took: %s seconds has parse time {parse_time} and find time {find_time}, now {len(output_dict)} have been found" % (time() - starttime))
            return title

        titles_dict = {}
        start_time = time()
        threads = [threading.Thread(target=get_title_from_req, args=(idx,list_res[idx]['docid'],req,titles_dict)) for idx,req in enumerate(reqs)]
        [t.start() for t in threads]
        print('Now waiting for them to joing')
        [t.join() for t in threads]
        print("--- %s seconds ---" % (time() - start_time))

        print(titles_dict)
        for index, dic in enumerate(list_res):
            dic['title'] = titles_dict[index]

        print(list_res)
        return list_res
if __name__ == '__main__':
    print(get_rankings('cancer research system', 5))