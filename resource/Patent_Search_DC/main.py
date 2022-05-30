from __future__ import absolute_import
import os
from scipy.spatial.distance import cosine
import numpy as np
import pickle
from Patent_Search_DC.clean_text import *
import pandas as pd
import grequests
from bs4 import BeautifulSoup
import re
from unidecode import unidecode



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
        rs = (grequests.get(u) for u in urls)
        reqs = grequests.map(rs)
        # using the BeautifulSoup module
        for req in reqs:
            soup = BeautifulSoup(req.text, 'html.parser')
            for title in soup.find_all('title'):
                x = str(unidecode(nospecial(title.get_text())))
            if '\n' in x:
                x = x.split('\n')[0]
            title = x.rstrip()
            titles.append(title)
       
        for index, dic in enumerate(list_res):
            dic['title'] = titles[index]

        print(list_res)
        return list_res
if __name__ == '__main__':
    print(get_rankings('cancer research system', 5))