import pickle
import streamlit as st
import requests
import pandas as pd

modo_oscuro = st.toggle("🌙 Modo oscuro", value=True)

if modo_oscuro:
    fondo_color = "#2b2b2b"
    texto_color = "#ffffff"
else:
    fondo_color = "#f0f0f0"
    texto_color = "#000000"

st.markdown(f"""
    <style>
        .stApp {{
            background-color: {fondo_color};
            color: {texto_color};
        }}
        [data-testid="stSidebar"] {{
            background-color: {'#000' if modo_oscuro else '#d9d9d9'};
            color: {texto_color};
        }}
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        /* Fondo general */
        .stApp {
            background: linear-gradient(135deg, #1f1c2c, #928dab);
            color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
        }

        /* Encabezado principal */
        h1 {
            color: #FFFFFF;
            text-align: center;
            font-size: 40px !important;
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
            background: linear-gradient(135deg, #4F4459, #9D68BD);
            color: black;
        }

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
            
        img {
            border-radius: 10px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;

        }
            
        img:hover {
            transform: scale(1.05);
            box-shadow: 0px 0px 15px #8A2BE2;

        [data-testid="stSidebar"] {
            background-color: #111;
            color: #eee;
            padding: 20px;
            font-size: 18px;
            border-right: 2px solid #8A2BE2;
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

def fetch_genre(movie_id):
    """
    Devuelve los géneros de una película desde TMDB.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = requests.get(url)

    if response.status_code != 200:
        return "Desconocido"

    data = response.json()
    if "genres" in data and isinstance(data["genres"], list) and len(data["genres"]) > 0:
        return ", ".join([genre["name"] for genre in data["genres"]])
    else:
        return "Desconocido"

def recommend(movie):
    
    index = movies[movies['title'] == movie].index[0]

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_similarity = []
    recommended_movie_genres = []

    for i in distances[1:num_recs + 1]:
        movie_id = movies.iloc[i[0]].movie_id
        nombre = movies.iloc[i[0]].title
        poster = fetch_poster(movie_id)
        genre = fetch_genre(movie_id)

        recommended_movie_names.append(nombre)
        recommended_movie_posters.append(poster)
        recommended_movie_similarity.append(i[1])
        recommended_movie_genres.append(genre)

    return recommended_movie_names, recommended_movie_posters, recommended_movie_similarity, recommended_movie_genres



with st.sidebar:
    st.header("StreamWise ")
    st.subheader("Mejor recomendacion al elegir qué ver.")
    st.image('https://cdn.hobbyconsolas.com/sites/navi.axelspringer.es/public/media/image/2016/06/607612-proximas-peliculas-pixar-despues-buscando-dory.jpg?tf=1200x')
    st.write('¿Cansado de pasar más tiempo buscando qué ver que disfrutando una película? Nuestro sistema inteligente analiza tus gustos y te recomienda películas hechas para ti. Así, elegir qué ver será tan fácil como presionar play.')
    st.write('Grupo de Proyecto')
    st.write('Juan Sebastian Toro')
    st.write('Juan David Aguilera')
    st.write('Juan Manuel Patarroyo')
    st.write('Tania Alejandra Rojas')


st.header('Sistema de recomendación🎞️🎬')
st.subheader("Descubre películas similares según tus gustos 🎥")
movies = pd.read_pickle('movie_list.pkl') 
similarity = pd.read_pickle('similarity.pkl')

movie_list = movies ['title'].values
selected_movie = st.selectbox(
    "Selecciona una película de la lista", 
    movie_list
)

import streamlit as st

num_recs = st.slider(
    "🎞️ Cantidad de recomendaciones a mostrar", 
    min_value=5, 
    max_value=20, 
    value=10, 
    step=1
)

if st.button('Mostrar Recomendaciones'):
    recommended_movie_names, recommended_movie_posters, recommended_movie_similarity, recommended_movie_genres = recommend (selected_movie)
    
    cols = st.columns(5)
    for i, col in enumerate(cols * (len(recommended_movie_names)//5 + 1)):
        if i < len(recommended_movie_names):
            col.text(recommended_movie_names[i])
            col.image(recommended_movie_posters[i])
            col.text(f"⭐ {recommended_movie_similarity[i] * 100:.1f}%")
            col.text(f"🎭 {recommended_movie_genres[i]}")
