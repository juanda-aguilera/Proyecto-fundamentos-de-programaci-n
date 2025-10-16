import numpy as np
import pandas as pd
import ast
pd.set_option('display.max_columns', None)

movies = pd.read_csv('tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_credits.csv')

print(movies.shape)
movies.head(1)

print(credits.shape)
credits.head(1)

movies = movies.merge(credits,on='title')
movies.dropna(inplace=True)

movies.head(2)

movies = movies [['movie_id','title','overview','genres','keywords','cast','crew']]

movies.head(1)

import ast

def convert(text):
    L = []
    for i in ast.literal_eval(text):
        L.append(i['name'])
    return L

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)

movies.head(2)

import ast
ast.literal_eval('[{"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}, {"id": 14, "name": "Fantasy"}, {"id": 878, "name": "Science Fiction"}]')

def convert3(text):
    L = []
    counter = 0
    for i in ast.literal_eval(text):
        if counter < 3:
            L.append(i['name'])
            counter += 1
    return L

movies['cast'] = movies['cast'].apply(convert3)
movies.head(2)

movies['cast'] = movies['cast'].apply(lambda x: x[0:3])
movies.head(2)

def fetch_director(text):
    L = []

    for i in ast.literal_eval(text):
        if i['job'] == 'Director':
            L.append(i['name'])
    return L

movies['crew'] = movies['crew'].apply(fetch_director)
movies.sample(2)

movies['overview'] = movies['overview'].apply(lambda x:x.split())
movies.sample(2)

def collapse(L):
    L1 = []

    for i in L:
        L1.append(i.replace(" ", ""))

    return L1

movies['cast'] = movies['cast'].apply(collapse)
movies['crew'] = movies['crew'].apply(collapse)
movies['genres'] = movies['genres'].apply(collapse)
movies['keywords'] = movies['keywords'].apply(collapse)
movies.head(2)

movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew'] 
movies.head(2)

new = movies.drop(columns=['overview', 'genres', 'keywords', 'cast', 'crew'])
new.head(2)

new['tags'] = new['tags'].apply(lambda x: " ".join(x))
new.head(2)

from sklearn.feature_extraction.text import CountVectorizer

cv = CountVectorizer(max_features=5000, stop_words='english')

vector = cv.fit_transform(new['tags']).toarray()

vector.shape

from sklearn.metrics.pairwise import cosine_similarity

similarity = cosine_similarity(vector)

similarity

new[new['title'] == 'The Lego Movie'].index[0]

def recommend(movie):
    index = new[new['title'] == movie ].index[0]

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    for i in distances[1:6]:
        print(new.iloc[i[0]].title)

recommend('Spider-Man 3')

import pickle

pickle.dump(new, open('movie_list.pkl', 'wb'))

pickle.dump(similarity, open('similarity.pkl', 'wb'))

movies = pickle.load(open('movie_list.pkl', 'rb'))

movies
