from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pickle
import pandas as pd

app = FastAPI()

# Allow your React frontend to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the machine learning model files
try:
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies_df = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    movies_df = None
    similarity = None

@app.get("/api/recommend")
def recommend_movie(movie: str):
    if movies_df is None or similarity is None:
        raise HTTPException(status_code=500, detail="Model files not found")
    
    try:
        # Find the movie (case-insensitive)
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
      
