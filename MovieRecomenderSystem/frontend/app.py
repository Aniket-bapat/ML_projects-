import streamlit as st
import pickle

movies_df = pickle.load(open('movies.pkl','rb'))
movies = movies_df['title'].values
similarity = pickle.load(open('similarity.pkl','rb'))
print(type(movies_df))

def recommend(movie):
    movie_index =  movies_df[movies_df['title']== movie].index[0]
    distance = similarity[movie_index]
    movies_list = sorted(list(enumerate(distance)),reverse=True,key = lambda x:x[1])[1:5]
    recomended_movies = []
    for i in movies_list:
        recomended_movies.append(movies_df.iloc[i[0]].title)
    
    return recomended_movies

st.title('Movie Recommender System')

selected_movie_name = st.selectbox('Enter a movie !',movies)

if st.button('Recommend'):  
    recomendation = recommend(selected_movie_name)
    for i in recomendation:
        st.write(i)
    st.write(selected_movie_name)