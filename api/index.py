from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import pickle
import pandas as pd

app = FastAPI()

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve paths to model files in the api folder
current_dir = os.path.dirname(os.path.abspath(__file__))
movie_dict_path = os.path.join(current_dir, 'movie_dict.pkl')
similarity_path = os.path.join(current_dir, 'similarity.pkl')

# Load model data
try:
    with open(movie_dict_path, 'rb') as f:
        movies_dict = pickle.load(f)
    movies_df = pd.DataFrame(movies_dict)

    with open(similarity_path, 'rb') as f:
        similarity = pickle.load(f)
except FileNotFoundError:
    movies_df = None
    similarity = None


@app.get("/api/recommend")
def recommend_movie(movie: str):
    if movies_df is None or similarity is None:
        raise HTTPException(status_code=500, detail="Model files not found")

    try:
        # Case-insensitive title match
        movie_index = movies_df[movies_df['title'].str.lower() == movie.lower()].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommendations = []
        for i in movies_list:
            recommendations.append({
                "movie_id": int(movies_df.iloc[i[0]]['movie_id']),
                "title": str(movies_df.iloc[i[0]]['title'])
            })

        return {"recommendations": recommendations}

    except IndexError:
        raise HTTPException(status_code=404, detail="Movie not found in database")
