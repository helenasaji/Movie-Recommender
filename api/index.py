from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'

@app.get("/api/recommend")
def recommend_movie(movie: str):
    if not TMDB_API_KEY:
        raise HTTPException(status_code=500, detail="TMDB API Key not configured on Vercel")

    # 1. Search for the movie ID based on the user's input title
    search_url = f"{BASE_URL}/search/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'query': movie,
        'with_original_language': 'ml'
    }
    
    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Error communicating with TMDB API")
    
    search_data = response.json().get('results', [])
    if not search_data:
        raise HTTPException(status_code=404, detail="Movie not found on TMDB")
    
    # Get the ID of the first matching Malayalam movie
    movie_id = search_data[0]['id']

    # 2. Fetch similar movies directly from TMDB's recommendation engine
    recommendations_url = f"{BASE_URL}/movie/{movie_id}/similar"
    rec_response = requests.get(recommendations_url, params={'api_key': TMDB_API_KEY, 'with_original_language': 'ml'})
    
    if rec_response.status_code != 200:
        raise HTTPException(status_code=502, detail="Error fetching recommendations from TMDB")
        
    rec_results = rec_response.json().get('results', [])
    
    recommendations = []
    for item in rec_results[:5]: # Take top 5
        recommendations.append({
            "movie_id": item.get('id'),
            "title": item.get('title')
        })

    return {"recommendations": recommendations}
