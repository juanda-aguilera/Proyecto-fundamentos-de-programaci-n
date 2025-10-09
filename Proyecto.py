import pandas as pd
import numpy as np
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity


metadata = pd.read_csv('movies_metadata.csv', low_memory=False)

credits = pd.read_csv('credits.csv')
keywords = pd.read_csv('keywords.csv')

metadata = metadata.drop([19730, 29503, 35587])
metadata['id'] = metadata['id'].astype('int')
credits['id'] = credits['id'].astype('int')
keywords['id'] = keywords['id'].astype('int')

metadata = metadata.merge(credits, on='id')
metadata = metadata.merge(keywords, on='id')


C = metadata['vote_average'].mean()
m = metadata['vote_count'].quantile(0.90)

q_movies = metadata.copy().loc[metadata['vote_count'] >= m]

def weighted_rating(x, m=m, C=C):
    v = x['vote_count']
    R = x['vote_average']
    return (v / (v + m) * R) + (m / (m + v) * C)

q_movies['score'] = q_movies.apply(weighted_rating, axis=1)
q_movies = q_movies.sort_values('score', ascending=False)

metadata['overview'] = metadata['overview'].fillna('')

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(metadata['overview'])
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

metadata = metadata.reset_index()
indices = pd.Series(metadata.index, index=metadata['title']).drop_duplicates()

def get_recommendations(title, cosine_sim=cosine_sim):
    if title not in indices:
        return f"'{title}' no se encuentra en el conjunto de datos."
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return metadata['title'].iloc[movie_indices]

features = ['cast', 'crew', 'keywords', 'genres']
for feature in features:
    metadata[feature] = metadata[feature].apply(literal_eval)

def get_director(x):
    for i in x:
        if i['job'] == 'Director':
            return i['name']
    return np.nan

metadata['director'] = metadata['crew'].apply(get_director)

def get_list(x):
    if isinstance(x, list):
        names = [i['name'] for i in x]
        return names[:3]
    return []

for feature in ['cast', 'keywords', 'genres']:
    metadata[feature] = metadata[feature].apply(get_list)

def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    elif isinstance(x, str):
        return str.lower(x.replace(" ", ""))
    else:
        return ''

for feature in ['cast', 'keywords', 'director', 'genres']:
    metadata[feature] = metadata[feature].apply(clean_data)

def create_soup(x):
    return ' '.join(x['keywords']) + ' ' + ' '.join(x['cast']) + ' ' + x['director'] + ' ' + ' '.join(x['genres'])

metadata['soup'] = metadata.apply(create_soup, axis=1)

count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(metadata['soup'])

cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

indices = pd.Series(metadata.index, index=metadata['title'])

def get_recommendations_soup(title, cosine_sim=cosine_sim2):
    if title not in indices:
        return f"'{title}' no se encuentra en el conjunto de datos."
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return metadata['title'].iloc[movie_indices]

print("🎬 Recomendaciones basadas en sinopsis:")
print(get_recommendations('The Dark Knight Rises'))

print("\n🍿 Recomendaciones basadas en contenido (director, elenco, keywords, géneros):")
print(get_recommendations_soup('The Dark Knight Rises'))