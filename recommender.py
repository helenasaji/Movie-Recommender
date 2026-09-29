import pandas as pd

# Load the movie data
movies = pd.read_csv('movies_data.csv')

# 1. Clean the data: Fill missing values (NaN) with empty strings
movies['overview'] = movies['overview'].fillna('')
movies['keywords'] = movies['keywords'].fillna('')
movies['genre_ids'] = movies['genre_ids'].fillna('')

# 2. Feature Engineering: Combine features into a single 'tags' column
# We convert genre_ids to strings so they can be concatenated with the text
movies['tags'] = movies['overview'] + " " + movies['keywords'] + " " + movies['genre_ids'].astype(str)

# 3. Create a clean dataframe with only what we need for the recommender
new_df = movies[['movie_id', 'title', 'tags']]

# Print the new dataframe to verify
print(new_df.head())
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 4. Text Vectorization: Convert text to numbers
# We use stop_words='english' to remove common words like 'the', 'and', 'a'
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()

# 5. Calculate Similarity
# This creates a matrix comparing every movie to every other movie
similarity = cosine_similarity(vectors)

print(f"Similarity matrix shape: {similarity.shape}")
print("Machine learning model ready!")
def recommend(movie):
	try:
		movie_index = new_df[new_df['title'] == movie].index[0]
		distances = similarity[movie_index]
		movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

		print(f"\nHere are 5 movies similar to '{movie}':")
		for i in movies_list:
			print("- " + new_df.iloc[i[0]]['title'])

	except IndexError:
		print(f"\nSorry, '{movie}' is not in the database.")

test_movie = new_df.iloc[0]['title']
recommend(test_movie)
                                                                                                                                        
