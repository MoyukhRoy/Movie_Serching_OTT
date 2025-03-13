import numpy as np
import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies = pd.read_csv('/Users/user/Desktop/Movie_Serching_OTT/tmdb_5000_credits.csv')
credits = pd.read_csv('/Users/user/Desktop/Movie_Serching_OTT/tmdb_5000_movies.csv')

movies = movies.merge(credits, on='title')

movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]

movies.dropna(inplace=True)

def convert(text):
    try:
        return [i['name'] for i in ast.literal_eval(text)]
    except (ValueError, SyntaxError):
        return []

def fetch_director(text):
    try:
        return [i['name'] for i in ast.literal_eval(text) if i.get('job') == 'Director']
    except (ValueError, SyntaxError):
        return []

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convert).apply(lambda x: x[:3])  # Keep top 3 cast members
movies['crew'] = movies['crew'].apply(fetch_director)

def collapse(tags):
    return [i.replace(" ", "") for i in tags]

movies['cast'] = movies['cast'].apply(collapse)
movies['crew'] = movies['crew'].apply(collapse)
movies['genres'] = movies['genres'].apply(collapse)
movies['keywords'] = movies['keywords'].apply(collapse)

movies['overview'] = movies['overview'].fillna("").apply(lambda x: x.split())

movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

new = movies[['movie_id', 'title', 'tags']]

new.loc[:, 'tags'] = new['tags'].apply(lambda x: " ".join(x))

cv = CountVectorizer(max_features=5000, stop_words='english')
vector = cv.fit_transform(new['tags']).toarray()

similarity = cosine_similarity(vector)

def recommend(movie):
    try:
        index = new[new['title'].str.lower() == movie.lower()].index[0]
        distances = sorted(enumerate(similarity[index]), reverse=True, key=lambda x: x[1])
        recommendations = [new.iloc[i[0]].title for i in distances[1:6]]
        return recommendations
    except IndexError:
        return ["Movie not found! Try a different title."]

print(recommend('Gandhi'))

# Save data using joblib (better than pickle)
import pickle
import os

pkl_file = 'movie_list.pkl'

if os.path.exists(pkl_file):
    os.remove(pkl_file)

pickle.dump(new, open(pkl_file, 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))

