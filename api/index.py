from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'

@app.route('/api/recommend', methods=['GET'])
def recommend_movie():
    if not TMDB_API_KEY:
        return jsonify({"error": "TMDB_API_KEY not configured in environment variables"}), 500

    movie = request.args.get('movie', '')
    if not movie:
        return jsonify({"error": "No movie provided"}), 400

    search_url = f"{BASE_URL}/search/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'query': movie,
        'with_original_language': 'ml'
    }
    
    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        return jsonify({"error": "TMDB search failed"}), 502
    
    search_data = response.json().get('results', [])
    if not search_data:
        return jsonify({"error": "Movie not found on TMDB"}), 404
    
    movie_id = search_data[0]['id']

    recommendations_url = f"{BASE_URL}/movie/{movie_id}/similar"
    rec_response = requests.get(recommendations_url, params={'api_key': TMDB_API_KEY})
    
    if rec_response.status_code != 200:
        return jsonify({"error": "Failed to fetch recommendations"}), 502
        
    rec_results = rec_response.json().get('results', [])
    
    recommendations = []
    for item in rec_results[:5]:
        recommendations.append({
            "movie_id": item.get('id'),
            "title": item.get('title')
        })

    return jsonify({"recommendations": recommendations})

if __name__ == '__main__':
    app.run()
