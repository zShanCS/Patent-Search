# Patent-Search-DC
# Project Title

Distributed Patent Semantic Search using Inverted Indices and Topic Modelling

## Description

This code proposes a novel approach, where the full text of a given patent application is compared to existing patents using machine learning and natural language processing techniques such as TFIDF vectorizer and topic modelling using Linear Discriminant Analysis (LDA) to classify the patents using embeddings and topics and uses Latent Semantic Analysis (LSA) with SVD to automatically detect inventions that are similar to the one described in the submitted document with similarity measure as the cosine distance formula. 

### Executing program

1. Run prepare_data.py
2. Run search_components.py
3. Now whenever a query needs to be executed just run main.py.


## Authors

- Dawood Wasif
- Zeeshan Ahmad
- Qasim Khan

## Acknowledgments

Largely inspired from Shah Khalid (https://www.linkedin.com/in/shah-khalid-68149a10a/?originalSubdomain=pk)

* [On The Current State of Scholarly Retrieval Systems](https://www.etasr.com/index.php/ETASR/article/view/2448)
* [An Effective Scholarly Search by Combining Inverted Indices and Structured Search With Citation Networks Analysis](https://ieeexplore.ieee.org/abstract/document/9522111)

## LICENSE
You are free to use the content of this repository under the terms of the Creative Commons Attribution License (http://creativecommons.org/licenses/by/4.0), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.
