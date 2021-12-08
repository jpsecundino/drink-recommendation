import pymongo
from sklearn.neighbors import KNeighborsClassifier

client = pymongo.MongoClient("mongodb+srv://colab:colab123@cluster1.sfizu.mongodb.net/?retryWrites=true&w=majority")
db = client.ia

collection = db['cocktails']
documents = list(collection.find())

keys_to_preserve = ['cocktailDbId', 'name', 'type', 'glass', 'IBA', 'image']

## Filter relevant properties, which is the ingredients plus glass, type, and IBA category
def get_relevant_keys(docs):
    non_relevant_keys = ['_id', 'instructions', 'IBA', 'name', '']
    keys = [list(document.keys()) for document in documents]
    unique_keys = list(set([item for sublist in keys for item in sublist]))
    for key in non_relevant_keys:
        unique_keys.remove(key)

    return unique_keys


## Transform property value into a normalized numeric value
def get_property_value(document, property):
    if property in keys_to_preserve:
        return document[property]

    return 1 if document[property] else 0


def create_data_matrix(keys):
    data_matrix = [[0 for _ in range(len(keys))] for __ in range(len(documents))]
    for i in range(len(documents)):
        for j in range(len(keys)):
            key = keys[j]
            if key in documents[i]:
                value = get_property_value(documents[i], key)
                data_matrix[i][j] = value
    return data_matrix


unique_keys = get_relevant_keys(documents)
data = create_data_matrix(unique_keys)

"""## Pré-processamento"""

import pandas as pd
import numpy as np

categorical_columns = ['glass', 'type']

database = pd.DataFrame(data, columns=unique_keys)
types = database['type']
images = get_images(list(database['image']))
database = pd.get_dummies(database, columns=categorical_columns)


ids = database['cocktailDbId'].astype(int)
database = database.drop(['cocktailDbId', 'image'], axis=1)

from sklearn.manifold import TSNE
tsne = TSNE(n_components=2, init='random',learning_rate=0.3, n_iter=1000)
database = tsne.fit_transform(database)

X, y = database, ids

recommender = KNeighborsClassifier()
recommender.fit(X, y)

"""## Recomendando drinks"""
def recommend(drink_id, num_recommendations = 6):
    filter = ids == drink_id

    query = database[filter]

    recommendation_indexes = recommender.kneighbors(query, n_neighbors=num_recommendations + 1)[:][1][0]

    import json
    # recommendations = {"recommendations": list(ids.iloc[recommendation_indexes].astype(str))}

    return list(ids.iloc[recommendation_indexes])
