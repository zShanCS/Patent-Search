from __future__ import absolute_import
import os
from scipy.spatial.distance import cosine
import numpy as np
import pickle
from clean_text import *
import pandas as pd

"""## 6.3. Using Cosine Distance Similarity to Retrieve Information"""

print(os.listdir('./'))
vect = pickle.load(open("vect.pickle", "rb"))
vect_text = pickle.load(open("vect_text.pickle", "rb"))

terms_rep = pickle.load(open("terms_rep.pickle", "rb"))
docs_rep = pickle.load(open("doc_rep.pickle", "rb"))

df_merged = pd.read_csv('final_patents_dataset.csv')
df_merged = df_merged.iloc[: , 1:]
df1 = df_merged.head(5000)
print(df1.head())
print(df1.columns)
print("Data is loaded! Query is executing! ")

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
        for rank, sort_index in enumerate(query_doc_sort_index):
            list_res.append({
                'score': 1 - query_doc_cos_dist[sort_index],
                'text' : df1['patent_id'][sort_index]
            })
            print ('Rank : ', rank, ' Consine : ', 1 - query_doc_cos_dist[sort_index],' Link : ', ' https://patents.google.com/patent/US' + df1['patent_id'][sort_index])
            if print_count == count :
                break
            else:
                print_count += 1
        print(list_res)
        return list_res
if __name__ == '__main__':
    print(get_rankings('lights with street lamp', 10))