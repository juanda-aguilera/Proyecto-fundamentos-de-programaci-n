import pickle
import streamlit as st
import requests
import pandas as pd
import streamlit.components.v1 as components

modo_oscuro = st.toggle("🌙 Modo oscuro", value=True)

if modo_oscuro:
    fondo_color = "#1e1e1e"
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
        .movie-title {{
            color: #45a29e;
            font-size: 18px;
            text-align: center;
        }}
        img {{
            border-radius: 10px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }}
        img:hover {{
            transform: scale(1.05);
            box-shadow: 0px 0px 15px #8A2BE2;
        }}
    </style>
""", unsafe_allow_html=True)

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=es-ES"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', '')
    return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else ""

def fetch_genre(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=es-ES"
    data = requests.get(url).json()
    genres = data.get("genres", [])
    return ", ".join([g["name"] for g in genres]) if genres else "Desconocido"

def fetch_overview(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=es-ES"
    data = requests.get(url).json()
    return data.get("overview", "Sin sinopsis disponible.")

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    names, posters, sims, genres, ids = [], [], [], [], []
    for i in distances[1:num_recs + 1]:
        movie_id = movies.iloc[i[0]].movie_id
        ids.append(movie_id)
        names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))
        sims.append(i[1])
        genres.append(fetch_genre(movie_id))
    return names, posters, sims, genres, ids

with st.sidebar:
    st.header("🎬 StreamWise")
    st.image('https://cdn.hobbyconsolas.com/sites/navi.axelspringer.es/public/media/image/2016/06/607612-proximas-peliculas-pixar-despues-buscando-dory.jpg?tf=1200x')
    st.write('Recomendaciones personalizadas según tus gustos cinematográficos.')
    st.write('👥 Grupo del Proyecto:')
    st.write('Juan Sebastián Toro\nJuan David Aguilera\nJuan Manuel Patarroyo\nTania Alejandra Rojas')

st.header('Sistema de recomendación🎞️🎬')
st.subheader("Descubre películas similares según tus gustos 🎥")

movies = pd.read_pickle('movie_list.pkl')
similarity = pd.read_pickle('similarity.pkl')

movie_list = movies['title'].values
selected_movie = st.selectbox("Selecciona una película de la lista", movie_list)

num_recs = st.slider("🎞️ Cantidad de recomendaciones a mostrar", 5, 20, 10)

if st.button('Mostrar Recomendaciones'):
    names, posters, sims, genres, ids = recommend(selected_movie)
    cols = st.columns(5)

    for i, col in enumerate(cols * ((len(names) // 5) + 1)):
        if i < len(names):
            with col:
                st.markdown(f"<div class='movie-title'>{names[i]}</div>", unsafe_allow_html=True)
                overview = fetch_overview(ids[i])
                genre = genres[i]

                # Crear bloque HTML interactivo con sinopsis ampliada
                html_code = f"""
                <html>
                <head>
                <style>
                    .poster {{
                        border-radius: 10px;
                        cursor: pointer;
                        transition: transform 0.3s ease, box-shadow 0.3s ease;
                    }}
                    .poster:hover {{
                        transform: scale(1.05);
                        box-shadow: 0 0 15px #8A2BE2;
                    }}
                    .overlay {{
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background-color: rgba(0, 0, 0, 0.8);
                        display: none;
                        align-items: center;
                        justify-content: center;
                        z-index: 999;
                    }}
                    .sinopsis-box {{
                        background-color: #1e1e1e;
                        color: white;
                        width: 70%;
                        max-height: 80%;
                        overflow-y: auto;
                        padding: 30px;
                        border-radius: 15px;
                        border: 2px solid #8A2BE2;
                        box-shadow: 0 0 20px rgba(0,0,0,0.7);
                        font-family: 'Segoe UI';
                        text-align: justify;
                    }}
                    .close-btn {{
                        background-color: #8A2BE2;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 8px;
                        cursor: pointer;
                        margin-top: 20px;
                    }}
                    .close-btn:hover {{
                        background-color: #A85BEA;
                    }}
                </style>
                </head>
                <body>
                    <img id="poster{i}" src="{posters[i]}" width="180" class="poster">
                    <div id="overlay{i}" class="overlay">
                        <div class="sinopsis-box">
                            <h2 style="text-align:center;">{names[i]}</h2>
                            <p><b>🎭 Género:</b> {genre}</p>
                            <p>{overview}</p>
                            <div style="text-align:center;">
                                <button class="close-btn" id="close{i}">Cerrar</button>
                            </div>
                        </div>
                    </div>
                    <script>
                        var overlay = document.getElementById("overlay{i}");
                        var img = document.getElementById("poster{i}");
                        var closeBtn = document.getElementById("close{i}");
                        img.onclick = function() {{
                            overlay.style.display = "flex";
                        }}
                        closeBtn.onclick = function() {{
                            overlay.style.display = "none";
                        }}
                        window.onclick = function(event) {{
                            if (event.target == overlay) {{
                                overlay.style.display = "none";
                            }}
                        }}
                    </script>
                </body>
                </html>
                """
                components.html(html_code, height=300)
                st.text(f"⭐ {sims[i]*100:.1f}%")
