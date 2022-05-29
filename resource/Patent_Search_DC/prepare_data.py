"""## 1. Imports"""
from clean_text import *
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pickle
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
# %matplotlib inline

"""## 2. Load Dataset"""
#df_merged = pd.read_csv('patents_dataset.csv')
#print("Read dataset successfuly.")
#df_merged.head()


"""## 3. Preprocess Dataset"""

#print("Cleaning dataset.")
#df_merged['cleaned_text']=df_merged['text'].apply(clean_text)
#df_merged.to_csv('cleaned_patents_dataset.csv')
#print("Cleaned dataset successfuly.")

df_merged = pd.read_csv('cleaned_patents_dataset.csv')
df_merged = df_merged.iloc[: , 1:]
"""## 4. Creating TF-IDF Matrix

### 4.1. Create and apply a vectorizer with 6000 features
"""
print("Applying TFIDF.")
vect =TfidfVectorizer(stop_words=stop_words,max_features=6000)
vect_text=vect.fit_transform(df_merged['cleaned_text'])

pickle.dump(vect, open("vect.pickle", "wb"))
pickle.dump(vect_text, open("vect_text.pickle", "wb"))

"""## 5. Topic Modelling using LDA

### 5.1. Fit LDA model on all vectors
"""
print("Applying LDA.")
lda_model=LatentDirichletAllocation(n_components=200,
learning_method='online',random_state=42,max_iter=1) 
lda_top=lda_model.fit_transform(vect_text)

"""### 5.2. Print example LDA embedding for first vector"""

# print("Document 0: ")
# for i,topic in enumerate(lda_top[0]):
#   print("Topic ",i,": ",topic*100,"%")


"""### 5.3. Print all topic names under each labelled number """

# vocab = vect.get_feature_names()
# for i, comp in enumerate(lda_model.components_):
#      vocab_comp = zip(vocab, comp)
#      sorted_words = sorted(vocab_comp, key= lambda x:x[1], reverse=True)[:10]
#      print("\nTopic "+str(i)+": ")
#      for t in sorted_words:
#             print(t[0],end=" ")



"""### 5.4. Make a new column in dataframe for the topic using LDA"""

i = 0
topic_list = np.zeros(50000) 
for vct in lda_top:
    topic_list[i]= np.argmax(vct, axis = 0) 
    i += 1 

df_merged['topic'] = list(topic_list)
df_merged.to_csv('final_patents_dataset.csv')
# df_merged.head(10)
