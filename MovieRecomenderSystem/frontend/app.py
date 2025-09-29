import streamlit as st
import pickle
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup a requests session with retries
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Fetch poster from TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = session.get(url, timeout=5)
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


# Load movies and similarity matrix
movies_df = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movies = movies_df['title'].values

# Recommend movies function
def recommend(movie):
    movie_index = movies_df[movies_df['title'] == movie].index[0]
    distance = similarity[movie_index]
    movies_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies_df.iloc[i[0]].movie_id   # ✅ use TMDB movie_id column
        recommended_movies.append(movies_df.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters


# Streamlit UI
st.title("Movie Recommender System")

selected_movie_name = st.selectbox("Enter a movie! ", movies)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)

    for idx, col in enumerate(cols):
        with col:
            st.markdown(
                f"""
                <div style="
                    background-color: #f9f9f9;
                    border-radius: 15px;
                    padding: 10px;
                    text-align: center;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                ">
                    <img src="{posters[idx]}" style="width:100%; border-radius:10px;">
                    <p style="margin-top:10px; font-size:16px; font-weight:600; color:#333;">
                        {names[idx]}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
