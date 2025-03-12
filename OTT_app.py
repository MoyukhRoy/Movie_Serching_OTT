import pickle
import streamlit as st
import requests
import gdown
import os

# Google Drive File ID for similarity.pkl
FILE_ID = "1Q3WDcXpHo9iPRatysz-a2UwS3vpaYnbA"  # Replace this with your actual Google Drive File ID
FILE_URL = f"https://drive.google.com/uc?id={FILE_ID}"
FILE_NAME = "similarity.pkl"

# Function to download similarity.pkl if not found locally
def download_similarity():
    if not os.path.exists(FILE_NAME):
        with st.spinner("Downloading similarity.pkl from Google Drive..."):
            gdown.download(FILE_URL, FILE_NAME, quiet=False)

# Call the function to ensure similarity.pkl is available
download_similarity()

# Load similarity.pkl after downloading
try:
    with open(FILE_NAME, 'rb') as f:
        similarity = pickle.load(f)
except Exception as e:
    st.error(f"Error loading similarity.pkl: {e}")
    st.stop()

# Load movie data
movies = pickle.load(open('movie_list.pkl', 'rb'))

# Function to fetch movie posters
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3813334bf63de7d92c53f6d207da332b&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return "https://via.placeholder.com/500"  # Placeholder if no poster found

# Function to recommend movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movie_names = []
    recommended_movie_posters = []
    
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

# Streamlit UI
st.header('🎬 Movie Recommender System')

# Dropdown for movie selection
movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

# Show recommendations on button click
if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    
    cols = st.columns(5)
    for col, name, poster in zip(cols, recommended_movie_names, recommended_movie_posters):
        with col:
            st.text(name)
            st.image(poster)
