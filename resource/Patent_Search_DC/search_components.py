import numpy as np
from clean_text import *
import pickle
import pandas as pd

"""## 6. Apply LSA with SVD to TF-IDF Matrix ¶

"""
df_merged = pd.read_csv('final_patents_dataset.csv')
df_merged = df_merged.iloc[: , 1:]

vect = pickle.load(open("vect.pickle", "rb"))
vect_text = pickle.load(open("vect_text.pickle", "rb"))

print("Applying LSA.")

# Global Variables 
K = 200 # number of components
# query = 'plant seeds'

matrix1 = vect_text.T[:,:5000]

"""### 6.1. Create Term and Document Representation """

# Applying SVD
U, s, VT = np.linalg.svd(matrix1.toarray()) # .T is used to take transpose and .toarray() is used to convert sparse matrix to normal matrix

TF_IDF_matrix_reduced = np.dot(U[:,:K], np.dot(np.diag(s[:K]), VT[:K, :]))

# Getting document and term representation
terms_rep = np.dot(U[:,:K], np.diag(s[:K])) # M X K matrix where M = Vocabulary Size and N = Number of documents
docs_rep = np.dot(np.diag(s[:K]), VT[:K, :]).T # N x K matrix

"""### 6.2. Visualize the representation"""

pickle.dump(terms_rep, open("terms_rep.pickle", "wb"))
pickle.dump(docs_rep, open("doc_rep.pickle", "wb"))

# plt.scatter(docs_rep[:,0], docs_rep[:,1], c=df1['topic'])
# plt.title("Patent Representation")
# plt.show()

# plt.scatter(terms_rep[:,0], terms_rep[:,1])
# plt.title("Term Representation")
# plt.show()

