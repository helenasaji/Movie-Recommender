from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TMDB_API_KEY = '60542ad334fd287729f2f848b74b1f42'
BASE_URL = 'https://api.themoviedb.org/3'

@app.get("/api/recommend")
def recommend_movie(movie: str):
    try:
        # 1. Search for the movie ID
        search_url = f"{BASE_URL}/search/movie"
        params = {
            'api_key': TMDB_API_KEY,
            'query': movie,
            'with_original_language': 'ml'
        }
        
        response = requests.get(search_url, params=params)
        if response.status_code != 200:
            return {"recommendations": [], "error": f"TMDB search failed with status {response.status_code}"}
        
        search_data = response.json().get('results', [])
        if not search_data:
            raise HTTPException(status_code=404, detail="Movie not found on TMDB")
        
        movie_id = search_data[0]['id']

        # 2. Fetch similar/recommended movies
        recommendations_url = f"{BASE_URL}/movie/{movie_id}/similar"
        rec_response = requests.get(recommendations_url, params={'api_key': TMDB_API_KEY})
        
        if rec_response.status_code != 200:
            return {"recommendations": [], "error": "Failed to fetch recommendations"}
            
        rec_results = rec_response.json().get('results', [])
        
        recommendations = []
        for item in rec_results[:5]:
            recommendations.append({
                "movie_id": item.get('id'),
                "title": item.get('title')
            })

        return {"recommendations": recommendations}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
