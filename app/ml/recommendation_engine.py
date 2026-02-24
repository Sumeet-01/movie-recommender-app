"""
Machine Learning Recommendation Engine for CineMate.
Implements collaborative filtering and content-based recommendation algorithms.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import math
from app.core.cache import cache, cache_key
from app.core.decorators import cached, timed


class RecommendationEngine:
    """
    Advanced recommendation engine with multiple algorithms.
    Combines collaborative filtering and content-based approaches.
    """
    
    def __init__(self):
        self.user_ratings = defaultdict(dict)  # {user_id: {movie_id: rating}}
        self.movie_ratings = defaultdict(dict)  # {movie_id: {user_id: rating}}
        self.movie_features = {}  # {movie_id: feature_vector}
        self.user_preferences = {}  # {user_id: preference_vector}
    
    def load_ratings_data(self):
        """Load ratings data from database."""
        from app.models.movie import Rating
        
        ratings = Rating.query.all()
        
        for rating in ratings:
            self.user_ratings[rating.user_id][rating.movie_id] = rating.score
            self.movie_ratings[rating.movie_id][rating.user_id] = rating.score
    
    def load_movie_features(self, movies_data: List[Dict]):
        """
        Load movie features from TMDB data.
        Features include genres, popularity, vote_average, etc.
        """
        for movie in movies_data:
            movie_id = movie.get('id')
            
            # Create feature vector from movie attributes
            genres = movie.get('genres', [])
            genre_ids = [g.get('id', 0) for g in genres]
            
            self.movie_features[movie_id] = {
                'genres': set(genre_ids),
                'vote_average': movie.get('vote_average', 0),
                'popularity': movie.get('popularity', 0),
                'vote_count': movie.get('vote_count', 0)
            }
    
    @timed
    def collaborative_filtering(self, user_id: int, n_recommendations: int = 10) -> List[Tuple[int, float]]:
        """
        User-based collaborative filtering.
        Finds similar users and recommends movies they liked.
        
        Returns:
            List of (movie_id, predicted_rating) tuples
        """
        if user_id not in self.user_ratings or not self.user_ratings[user_id]:
            return []
        
        # Find similar users
        similar_users = self._find_similar_users(user_id, k=20)
        
        # Get candidate movies (movies rated by similar users but not by target user)
        rated_movies = set(self.user_ratings[user_id].keys())
        candidate_movies = set()
        
        for similar_user_id, similarity in similar_users:
            candidate_movies.update(
                movie_id for movie_id in self.user_ratings[similar_user_id]
                if movie_id not in rated_movies
            )
        
        # Predict ratings for candidate movies
        predictions = []
        for movie_id in candidate_movies:
            predicted_rating = self._predict_rating(user_id, movie_id, similar_users)
            if predicted_rating > 0:
                predictions.append((movie_id, predicted_rating))
        
        # Sort by predicted rating and return top N
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n_recommendations]
    
    def _find_similar_users(self, user_id: int, k: int = 20) -> List[Tuple[int, float]]:
        """
        Find k most similar users using Pearson correlation.
        
        Returns:
            List of (user_id, similarity_score) tuples
        """
        similarities = []
        target_ratings = self.user_ratings[user_id]
        
        for other_user_id in self.user_ratings:
            if other_user_id == user_id:
                continue
            
            # Calculate Pearson correlation
            similarity = self._pearson_correlation(
                target_ratings,
                self.user_ratings[other_user_id]
            )
            
            if similarity > 0:
                similarities.append((other_user_id, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
    
    def _pearson_correlation(self, ratings1: Dict, ratings2: Dict) -> float:
        """Calculate Pearson correlation coefficient between two rating dictionaries."""
        common_movies = set(ratings1.keys()) & set(ratings2.keys())
        
        if len(common_movies) < 2:
            return 0
        
        # Get ratings for common movies
        r1 = [ratings1[movie_id] for movie_id in common_movies]
        r2 = [ratings2[movie_id] for movie_id in common_movies]
        
        # Calculate means
        mean1 = sum(r1) / len(r1)
        mean2 = sum(r2) / len(r2)
        
        # Calculate correlation
        numerator = sum((r1[i] - mean1) * (r2[i] - mean2) for i in range(len(r1)))
        
        sum_sq1 = sum((r - mean1) ** 2 for r in r1)
        sum_sq2 = sum((r - mean2) ** 2 for r in r2)
        
        denominator = math.sqrt(sum_sq1 * sum_sq2)
        
        if denominator == 0:
            return 0
        
        return numerator / denominator
    
    def _predict_rating(self, user_id: int, movie_id: int, similar_users: List[Tuple[int, float]]) -> float:
        """
        Predict rating for a movie using weighted average of similar users' ratings.
        """
        numerator = 0
        denominator = 0
        
        for similar_user_id, similarity in similar_users:
            if movie_id in self.user_ratings[similar_user_id]:
                rating = self.user_ratings[similar_user_id][movie_id]
                numerator += similarity * rating
                denominator += abs(similarity)
        
        if denominator == 0:
            return 0
        
        return numerator / denominator
    
    @timed
    def content_based_filtering(self, user_id: int, n_recommendations: int = 10) -> List[Tuple[int, float]]:
        """
        Content-based filtering using movie features.
        Recommends movies similar to those the user liked.
        
        Returns:
            List of (movie_id, similarity_score) tuples
        """
        if user_id not in self.user_ratings or not self.user_ratings[user_id]:
            return []
        
        # Build user preference profile
        user_profile = self._build_user_profile(user_id)
        
        # Get candidate movies (not rated by user)
        rated_movies = set(self.user_ratings[user_id].keys())
        candidate_movies = [
            movie_id for movie_id in self.movie_features
            if movie_id not in rated_movies
        ]
        
        # Calculate similarity scores
        recommendations = []
        for movie_id in candidate_movies:
            similarity = self._calculate_content_similarity(user_profile, movie_id)
            if similarity > 0:
                recommendations.append((movie_id, similarity))
        
        # Sort by similarity and return top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:n_recommendations]
    
    def _build_user_profile(self, user_id: int) -> Dict:
        """Build user preference profile based on rated movies."""
        user_ratings_dict = self.user_ratings[user_id]
        
        # Weight features by rating
        genre_weights = defaultdict(float)
        avg_vote_avg = 0
        avg_popularity = 0
        total_weight = 0
        
        for movie_id, rating in user_ratings_dict.items():
            if movie_id not in self.movie_features:
                continue
            
            features = self.movie_features[movie_id]
            weight = rating / 5.0  # Normalize rating
            
            # Weight genres
            for genre_id in features['genres']:
                genre_weights[genre_id] += weight
            
            # Weight other features
            avg_vote_avg += features['vote_average'] * weight
            avg_popularity += features['popularity'] * weight
            total_weight += weight
        
        if total_weight == 0:
            return {'genres': set(), 'vote_average': 0, 'popularity': 0}
        
        # Normalize
        preferred_genres = set(
            genre_id for genre_id, weight in genre_weights.items()
            if weight / total_weight > 0.3  # Threshold for preference
        )
        
        return {
            'genres': preferred_genres,
            'vote_average': avg_vote_avg / total_weight,
            'popularity': avg_popularity / total_weight
        }
    
    def _calculate_content_similarity(self, user_profile: Dict, movie_id: int) -> float:
        """Calculate similarity between user profile and movie."""
        if movie_id not in self.movie_features:
            return 0
        
        movie_features = self.movie_features[movie_id]
        
        # Genre similarity (Jaccard index)
        user_genres = user_profile['genres']
        movie_genres = movie_features['genres']
        
        if not user_genres or not movie_genres:
            genre_similarity = 0
        else:
            intersection = len(user_genres & movie_genres)
            union = len(user_genres | movie_genres)
            genre_similarity = intersection / union if union > 0 else 0
        
        # Rating similarity
        rating_diff = abs(user_profile['vote_average'] - movie_features['vote_average'])
        rating_similarity = 1 - (rating_diff / 10)  # Normalize to [0, 1]
        
        # Combine similarities (weighted)
        similarity = (
            0.7 * genre_similarity +
            0.3 * rating_similarity
        )
        
        return similarity
    
    @cached(timeout=600)
    def hybrid_recommendations(self, user_id: int, n_recommendations: int = 20) -> List[Dict]:
        """
        Hybrid approach combining collaborative and content-based filtering.
        
        Returns:
            List of recommended movie dictionaries with scores
        """
        # Get recommendations from both methods
        collab_recs = self.collaborative_filtering(user_id, n_recommendations * 2)
        content_recs = self.content_based_filtering(user_id, n_recommendations * 2)
        
        # Combine recommendations with weighted scoring
        combined_scores = defaultdict(float)
        
        # Weight collaborative filtering higher if user has many ratings
        collab_weight = min(len(self.user_ratings.get(user_id, {})) / 10, 0.7)
        content_weight = 1 - collab_weight
        
        for movie_id, score in collab_recs:
            combined_scores[movie_id] += score * collab_weight
        
        for movie_id, score in content_recs:
            combined_scores[movie_id] += score * content_weight
        
        # Sort and return top N
        recommendations = [
            {'movie_id': movie_id, 'score': score}
            for movie_id, score in combined_scores.items()
        ]
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:n_recommendations]
    
    @timed
    def similar_movies(self, movie_id: int, n_similar: int = 10) -> List[Tuple[int, float]]:
        """
        Find movies similar to the given movie based on content features.
        
        Returns:
            List of (movie_id, similarity_score) tuples
        """
        if movie_id not in self.movie_features:
            return []
        
        target_features = self.movie_features[movie_id]
        similarities = []
        
        for other_movie_id, other_features in self.movie_features.items():
            if other_movie_id == movie_id:
                continue
            
            # Calculate similarity
            similarity = self._calculate_movie_similarity(target_features, other_features)
            
            if similarity > 0:
                similarities.append((other_movie_id, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n_similar]
    
    def _calculate_movie_similarity(self, features1: Dict, features2: Dict) -> float:
        """Calculate similarity between two movies."""
        # Genre similarity
        genres1 = features1['genres']
        genres2 = features2['genres']
        
        if not genres1 or not genres2:
            genre_similarity = 0
        else:
            intersection = len(genres1 & genres2)
            union = len(genres1 | genres2)
            genre_similarity = intersection / union if union > 0 else 0
        
        # Rating similarity
        rating_diff = abs(features1['vote_average'] - features2['vote_average'])
        rating_similarity = 1 - (rating_diff / 10)
        
        # Popularity similarity
        pop_diff = abs(features1['popularity'] - features2['popularity'])
        max_pop = max(features1['popularity'], features2['popularity'], 1)
        popularity_similarity = 1 - min(pop_diff / max_pop, 1)
        
        # Weighted combination
        similarity = (
            0.6 * genre_similarity +
            0.25 * rating_similarity +
            0.15 * popularity_similarity
        )
        
        return similarity
    
    def get_trending_by_category(self, category: str = 'all', limit: int = 20) -> List[int]:
        """
        Get trending movies by category based on recent ratings.
        
        Args:
            category: 'all', 'action', 'comedy', etc.
            limit: Number of movies to return
        
        Returns:
            List of movie IDs
        """
        # Calculate trending score based on recent ratings and popularity
        trending_scores = defaultdict(float)
        
        for movie_id, user_ratings in self.movie_ratings.items():
            # Average rating
            avg_rating = sum(user_ratings.values()) / len(user_ratings)
            
            # Number of ratings (popularity)
            rating_count = len(user_ratings)
            
            # Trending score: combination of rating and count
            trending_score = avg_rating * math.log(rating_count + 1)
            trending_scores[movie_id] = trending_score
        
        # Sort by trending score
        trending = sorted(trending_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [movie_id for movie_id, _ in trending[:limit]]


# Global recommendation engine instance
recommendation_engine = RecommendationEngine()
