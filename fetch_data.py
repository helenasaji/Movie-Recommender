import requests
import csv
import os
import time

# Set this securely in your environment variables, or replace the string below for local testing
API_KEY = os.getenv('TMDB_API_KEY', 'Your_api_key')
BASE_URL = 'https://api.themoviedb.org/3'


def fetch_movies(language_code, max_pages=5):
    movies = []
    print(f"Fetching movies for language: {language_code}")

    for page in range(1, max_pages + 1):
        # 1. Discover movies by original language
        discover_url = f"{BASE_URL}/discover/movie"
        params = {
            'api_key': API_KEY,
            'with_original_language': language_code,
            'page': page,
            'sort_by': 'popularity.desc'
        }

        response = requests.get(discover_url, params=params)
        if response.status_code != 200:
            print(f"Error fetching page {page}: {response.status_code}")
            break

        data = response.json()
        results = data.get('results', [])

        if not results:
            break  # Stop if we reach a page with no results

        # 2. Loop through each movie to get its specific keyword tags
        for item in results:
            movie_id = item['id']
            keywords_url = f"{BASE_URL}/movie/{movie_id}/keywords"

            kw_response = requests.get(keywords_url, params={'api_key': API_KEY})
            keywords_list = []

            if kw_response.status_code == 200:
                kw_data = kw_response.json()
                # Extract just the string names of the keywords
                keywords_list = [kw['name'] for kw in kw_data.get('keywords', [])]

            movies.append({
                'movie_id': movie_id,
                'title': item.get('title'),
                'overview': item.get('overview', '').replace('\n', ' '),  # Clean linebreaks for CSV
                'genre_ids': item.get('genre_ids', []),
                'keywords': ", ".join(keywords_list),  # Convert list to a comma-separated string
                'language': language_code
            })

            # Pause for 100ms between requests to avoid hitting TMDB rate limits
            time.sleep(0.1)

        print(f"  - Completed page {page}/{max_pages}")

    return movies


def save_to_csv(movies_data, filename="movies_data.csv"):
    if not movies_data:
        print("No data to save.")
        return

    # Get CSV headers from the first dictionary's keys
    headers = movies_data[0].keys()

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(movies_data)

    print(f"\nSuccessfully saved {len(movies_data)} movies to {filename}")


if __name__ == "__main__":
    # To build a robust dataset, increase max_pages to 50 or 100
    malayalam_movies = fetch_movies('ml', max_pages=5)

    save_to_csv(malayalam_movies)
