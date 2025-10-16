import pickle
import streamlit as st
import requests
import pandas as pd

st.markdown("""
    <style>
        /* Fondo general */
        .stApp {
            background-color: #696969;
            color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
        }

        /* Encabezado principal */
        h1 {
            color: #FFFFFF;
            text-align: center;
            font-size: 40px !important;
        }

        /* Texto del sidebar */
        [data-testid="stSidebar"] {
            background-color: #000000;
            color: #FFFFFF;
        }

        /* Títulos de las películas */
        .movie-title {
            color: #45a29e;
            font-size: 18px;
            text-align: center;
        }

        /* Botón */
        div.stButton > button {
            background-color: #000000;
            color: white;
            border-radius: 10px;
            height: 50px;
            width: 250px;
            font-size: 18px;
        }

        div.stButton > button:hover {
            background-color: #8A2BE2;
            color: black;
        }
            
        [data-testid="stSidebar"] * {
            font-size: 20px !important; 

         div[data-baseweb="select"] > div {
            background-color: #000000;
            color: #FFFFFF ;
            border: 2px solid #45a29e ;
            border-radius: 10px;
            font-size: 18px;
        }
            
        ul[role="listbox"] li {
            background-color: #000000;
            color: white;
            font-size: 16px ;
        }
    </style>
""", unsafe_allow_html=True)

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    
    data= requests.get(url)

    data = data.json()

    poster_path = data ['poster_path']

    full_path = "https://Image.tmdb.org/t/p/w500/" + poster_path

    return full_path

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



with st.sidebar:
    st.header("StreamWise : Mejor recomendacion al elegir qué ver.")
    st.image('https://cdn.hobbyconsolas.com/sites/navi.axelspringer.es/public/media/image/2016/06/607612-proximas-peliculas-pixar-despues-buscando-dory.jpg?tf=1200x')
    st.write('¿Cansado de pasar más tiempo buscando qué ver que disfrutando una película? Nuestro sistema inteligente analiza tus gustos y te recomienda películas hechas para ti. Así, elegir qué ver será tan fácil como presionar play.')
    st.write('Grupo de Proyecto')
    st.write('Juan Sebastian Toro')
    st.write('Juan David Aguilera')
    st.write('Juan Manuel Patarroyo')
    st.write('Tania Alejandra Rojas')


st.header('Sistema de recomendación')
movies = pd.read_pickle('movie_list.pkl') 
similarity = pd.read_pickle('similarity.pkl')

movie_list = movies ['title'].values
selected_movie = st.selectbox(
    "Selecciona una película de la lista", 
    movie_list
)

import streamlit as st

if st.button('Mostrar Recomendaciones'):
    recommended_movie_names, recommended_movie_posters = recommend (selected_movie)
    
    cols = st.columns (5)

    for i,col in enumerate(cols):
        col.text(recommended_movie_names[i])
        col.image(recommended_movie_posters[i])

