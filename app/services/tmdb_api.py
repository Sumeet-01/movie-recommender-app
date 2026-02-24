"""
Advanced TMDB API Service with caching, error handling, and comprehensive endpoints.
"""

import requests
import os
from typing import List, Dict, Optional
from app.core.cache import cache, cache_key
from app.core.decorators import cached, timed
from app.core.exceptions import TMDbAPIException


class TMDbService:
    """Enhanced TMDB API service with advanced features."""
    
    BASE_URL = 'https://api.themoviedb.org/3'
    IMAGE_BASE_URL = 'https://image.tmdb.org/t/p'

    def __init__(self):
        self.api_key = os.environ.get('TMDB_API_KEY')
        if not self.api_key:
            raise ValueError("TMDB API key not found in environment variables.")

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make GET request to TMDB API with error handling and retries.
        Supports both API key (v3) and Bearer token (v4) authentication.
        """
        if params is None:
            params = {}
        
        # Check if using Bearer token (JWT) or API key
        headers = {}
        if self.api_key.startswith('eyJ'):  # JWT token
            headers['Authorization'] = f'Bearer {self.api_key}'
        else:  # API Key
            params['api_key'] = self.api_key
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ TMDB API request failed: {e}")
            raise TMDbAPIException(f"TMDB API request failed: {endpoint}")

    @cached(timeout=3600)  # Cache for 1 hour
    @timed
    def get_trending_movies(self, time_window: str = 'week', page: int = 1) -> List[Dict]:
        """Get trending movies for day or week."""
        cache_k = cache_key('trending', time_window, page=page)
        
        data = self._get(f'trending/movie/{time_window}', {'page': page})
        return data.get('results', []) if data else []
    
    @cached(timeout=3600)
    @timed
    def get_popular_movies(self, page: int = 1) -> List[Dict]:
        """Get popular movies."""
        data = self._get('movie/popular', {'page': page})
        return data.get('results', []) if data else []
    
    @cached(timeout=3600)
    @timed
    def get_top_rated_movies(self, page: int = 1) -> List[Dict]:
        """Get top rated movies."""
        data = self._get('movie/top_rated', {'page': page})
        return data.get('results', []) if data else []
    
    @cached(timeout=3600)
    @timed
    def get_now_playing_movies(self, page: int = 1) -> List[Dict]:
        """Get movies currently in theaters."""
        data = self._get('movie/now_playing', {'page': page})
        return data.get('results', []) if data else []
    
    @cached(timeout=3600)
    @timed
    def get_upcoming_movies(self, page: int = 1) -> List[Dict]:
        """Get upcoming movies."""
        data = self._get('movie/upcoming', {'page': page})
        return data.get('results', []) if data else []

    @cached(timeout=7200)  # Cache for 2 hours
    @timed
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Get detailed information for a specific movie."""
        params = {
            'append_to_response': 'credits,videos,images,similar,recommendations,reviews,keywords'
        }
        return self._get(f'movie/{movie_id}', params)
    
    @cached(timeout=7200)
    def get_movie_credits(self, movie_id: int) -> Optional[Dict]:
        """Get cast and crew for a movie."""
        return self._get(f'movie/{movie_id}/credits')
    
    @cached(timeout=7200)
    def get_movie_videos(self, movie_id: int) -> List[Dict]:
        """Get videos (trailers, teasers) for a movie."""
        data = self._get(f'movie/{movie_id}/videos')
        return data.get('results', []) if data else []
    
    @cached(timeout=7200)
    def get_movie_images(self, movie_id: int) -> Optional[Dict]:
        """Get images (posters, backdrops) for a movie."""
        return self._get(f'movie/{movie_id}/images')
    
    @cached(timeout=7200)
    def get_similar_movies(self, movie_id: int, page: int = 1) -> List[Dict]:
        """Get movies similar to the specified movie."""
        data = self._get(f'movie/{movie_id}/similar', {'page': page})
        return data.get('results', []) if data else []
    
    @cached(timeout=7200)
    def get_movie_recommendations(self, movie_id: int, page: int = 1) -> List[Dict]:
        """Get movie recommendations based on a specific movie."""
        data = self._get(f'movie/{movie_id}/recommendations', {'page': page})
        return data.get('results', []) if data else []
    
    @cached(timeout=1800)  # Cache for 30 minutes
    def search_movies(self, query: str, page: int = 1, year: Optional[int] = None) -> Dict:
        """Search for movies by title."""
        params = {'query': query, 'page': page}
        if year:
            params['year'] = year
        
        data = self._get('search/movie', params)
        return {
            'results': data.get('results', []) if data else [],
            'total_results': data.get('total_results', 0) if data else 0,
            'total_pages': data.get('total_pages', 0) if data else 0,
            'page': page
        }
    
    @cached(timeout=86400)  # Cache for 24 hours
    def get_genres(self) -> List[Dict]:
        """Get list of all movie genres."""
        data = self._get('genre/movie/list')
        return data.get('genres', []) if data else []
    
    @cached(timeout=3600)
    def discover_movies(self, **filters) -> List[Dict]:
        """
        Discover movies with various filters.
        
        Filters can include:
        - with_genres: Genre IDs (comma-separated)
        - sort_by: Sort results (e.g., 'popularity.desc', 'vote_average.desc')
        - year: Release year
        - vote_average.gte: Minimum rating
        - with_runtime.gte: Minimum runtime
        - with_runtime.lte: Maximum runtime
        - page: Page number
        """
        data = self._get('discover/movie', filters)
        return data.get('results', []) if data else []
    
    @cached(timeout=3600)
    def get_movies_by_genre(self, genre_id: int, page: int = 1, sort_by: str = 'popularity.desc') -> List[Dict]:
        """Get movies filtered by genre."""
        params = {
            'with_genres': genre_id,
            'sort_by': sort_by,
            'page': page
        }
        data = self._get('discover/movie', params)
        return data.get('results', []) if data else []
    
    @cached(timeout=7200)
    def get_person_details(self, person_id: int) -> Optional[Dict]:
        """Get details about a person (actor, director, etc.)."""
        return self._get(f'person/{person_id}', {'append_to_response': 'movie_credits,images'})
    
    @cached(timeout=1800)
    def search_people(self, query: str, page: int = 1) -> Dict:
        """Search for people by name."""
        data = self._get('search/person', {'query': query, 'page': page})
        return {
            'results': data.get('results', []) if data else [],
            'total_results': data.get('total_results', 0) if data else 0,
            'page': page
        }
    
    def get_image_url(self, path: Optional[str], size: str = 'original') -> Optional[str]:
        """
        Get full image URL from path.
        
        Common sizes:
        - Poster: w92, w154, w185, w342, w500, w780, original
        - Backdrop: w300, w780, w1280, original
        - Profile: w45, w185, h632, original
        """
        if not path:
            return None
        return f"{self.IMAGE_BASE_URL}/{size}{path}"
    
    def get_youtube_url(self, video_key: str) -> str:
        """Get YouTube URL for a video key."""
        return f"https://www.youtube.com/watch?v={video_key}"
    
    def get_youtube_embed_url(self, video_key: str) -> str:
        """Get YouTube embed URL for a video key."""
        return f"https://www.youtube.com/embed/{video_key}"
    
    @timed
    def get_multi_search(self, query: str, page: int = 1) -> Dict:
        """Search for movies, TV shows, and people."""
        data = self._get('search/multi', {'query': query, 'page': page})
        return {
            'results': data.get('results', []) if data else [],
            'total_results': data.get('total_results', 0) if data else 0,
            'page': page
        }
    
    def clear_cache(self):
        """Clear all TMDB service caches."""
        cache.clear()
        print("✅ TMDB service cache cleared")


# Global TMDB service instance
tmdb_service = TMDbService()

