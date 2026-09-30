from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'

@app.route('/api/search', methods=['GET'])
def search_movies():
    if not TMDB_API_KEY:
        return jsonify({"error": "API key not configured"}), 500

    query = request.args.get('q', '')
    if len(query.strip()) < 2:
        return jsonify([])

    search_url = f"{BASE_URL}/search/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'query': query,
        'with_original_language': 'ml'
    }
    
    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        return jsonify({"error": "TMDB search failed"}), 502
    
    results = response.json().get('results', [])
    
    movies = []
    for item in results[:6]:
        poster_path = item.get('poster_path')
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
        
        movies.append({
            "id": item.get('id'),
            "title": item.get('title'),
            "release_date": item.get('release_date', 'N/A'),
            "overview": item.get('overview', 'No plot available.'),
            "poster": poster_url
        })

    return jsonify(movies)

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    if not TMDB_API_KEY:
        return jsonify({"error": "API key not configured"}), 500

    movie_id = request.args.get('movie_id')
    if not movie_id:
        return jsonify([])

    # Fetch live similar movies from TMDB
    rec_url = f"{BASE_URL}/movie/{movie_id}/similar"
    params = {
        'api_key': TMDB_API_KEY,
        'with_original_language': 'ml'
    }
    
    response = requests.get(rec_url, params=params)
    if response.status_code != 200:
        return jsonify([])

    results = response.json().get('results', [])
    recommendations = []
    
    for item in results[:6]: # Get up to 6 recommendations
        poster_path = item.get('poster_path')
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
        
        recommendations.append({
            "id": item.get('id'),
            "title": item.get('title'),
            "release_date": item.get('release_date', 'N/A'),
            "overview": item.get('overview', 'No plot available.'),
            "poster": poster_url
        })

    return jsonify(recommendations)

if __name__ == '__main__':
    app.run()
