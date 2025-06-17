import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies = pd.read_excel("movies_sample.xlsx")
movies['tags'] = movies['genres'].fillna('') + ' ' + movies['overview'].fillna('')

tfidf = TfidfVectorizer(stop_words='english')
vectors = tfidf.fit_transform(movies['tags'])
similarity = cosine_similarity(vectors)

def recommend(movie_title):
    try:
        idx = movies[movies['title'].str.lower() == movie_title.lower()].index[0]
        distances = list(enumerate(similarity[idx]))
        top_matches = sorted(distances, key=lambda x: x[1], reverse=True)[1:6]
        recommendations = [movies.iloc[i[0]].title for i in top_matches]
        return recommendations
    except IndexError:
        return []
