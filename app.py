import streamlit as st
import pickle
import requests
import os

# Fetch movie poster from API
def fetch_poster(movie_id):
    try:
        api_key = os.getenv("TMDB_API_KEY", "02e985f1d533636364e41342cf8ba214")  # Use an environment variable for the API key
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad requests
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            return full_path
        else:
            return None
    except requests.exceptions.RequestException as e:
        st.error("Error fetching movie poster.")
        return None

# Load movie data and similarity matrix
try:
    movies = pickle.load(open('movies_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    movies_list = movies['title'].values
except FileNotFoundError:
    st.error("Required files not found. Please check the paths for 'movies_list.pkl' and 'similarity.pkl'.")

# Streamlit App Header
st.header("Movie Recommendation System")

# Dropdown to select a movie
selected_movie = st.selectbox("Select a movie", movies_list)

# Recommend function to get similar movies
def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(enumerate(similarity[index]), reverse=True, key=lambda x: x[1])
        recommended_movies = []
        recommended_posters = []
        for i in distances[1:6]:
            movie_id = movies.iloc[i[0]].id
            recommended_movies.append(movies.iloc[i[0]].title)
            poster_url = fetch_poster(movie_id)
            recommended_posters.append(poster_url if poster_url else "https://via.placeholder.com/150")  # Placeholder if no poster
        return recommended_movies, recommended_posters
    except IndexError:
        st.error("Movie not found in the dataset.")
        return [], []

# Display recommendations on button click
if st.button("Recommend"):
    movie_names, movie_posters = recommend(selected_movie)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        if idx < len(movie_names):
            with col:
                st.text(movie_names[idx])
                st.image(movie_posters[idx], width=120)
