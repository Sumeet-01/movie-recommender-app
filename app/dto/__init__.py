"""
Data Transfer Objects (DTOs) for CineMate application.
Provides standardized data structures for API responses and data transformation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class UserDTO:
    """User data transfer object."""
    id: int
    username: str
    email: str
    created_at: datetime
    watchlist_count: int = 0
    ratings_count: int = 0
    reviews_count: int = 0
    lists_count: int = 0
    
    @classmethod
    def from_model(cls, user, include_stats=False):
        """Create DTO from User model."""
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at if hasattr(user, 'created_at') else datetime.utcnow()
        }
        
        if include_stats:
            from app.repositories import UserRepository
            stats = UserRepository.get_user_stats(user.id)
            data.update(stats)
        
        return cls(**data)
    
    def to_dict(self, exclude_email=False):
        """Convert to dictionary."""
        data = asdict(self)
        if exclude_email:
            data.pop('email', None)
        return data


@dataclass
class MovieDTO:
    """Movie data transfer object."""
    id: int
    tmdb_id: int
    title: str
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    genres: Optional[List[Dict]] = None
    runtime: Optional[int] = None
    tagline: Optional[str] = None
    
    @classmethod
    def from_tmdb_data(cls, data: Dict):
        """Create DTO from TMDB API response."""
        return cls(
            id=data.get('id', 0),
            tmdb_id=data.get('id', 0),
            title=data.get('title', 'Unknown'),
            overview=data.get('overview'),
            poster_path=data.get('poster_path'),
            backdrop_path=data.get('backdrop_path'),
            release_date=data.get('release_date'),
            vote_average=data.get('vote_average'),
            vote_count=data.get('vote_count'),
            genres=data.get('genres', []),
            runtime=data.get('runtime'),
            tagline=data.get('tagline')
        )
    
    @classmethod
    def from_model(cls, movie, include_details=False):
        """Create DTO from Movie model."""
        data = {
            'id': movie.id,
            'tmdb_id': movie.tmdb_id,
            'title': movie.title,
            'poster_path': movie.poster_path
        }
        
        if include_details:
            # Fetch additional details from TMDB if needed
            pass
        
        return cls(**data)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    def get_poster_url(self, size='w500'):
        """Get full poster URL."""
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/{size}{self.poster_path}"
        return "https://via.placeholder.com/500x750.png?text=No+Image"
    
    def get_backdrop_url(self, size='w1280'):
        """Get full backdrop URL."""
        if self.backdrop_path:
            return f"https://image.tmdb.org/t/p/{size}{self.backdrop_path}"
        return None


@dataclass
class RatingDTO:
    """Rating data transfer object."""
    id: int
    user_id: int
    movie_id: int
    score: float
    timestamp: datetime
    username: Optional[str] = None
    movie_title: Optional[str] = None
    
    @classmethod
    def from_model(cls, rating, include_relations=False):
        """Create DTO from Rating model."""
        data = {
            'id': rating.id,
            'user_id': rating.user_id,
            'movie_id': rating.movie_id,
            'score': rating.score,
            'timestamp': rating.timestamp
        }
        
        if include_relations:
            data['username'] = rating.user.username if hasattr(rating, 'user') else None
            data['movie_title'] = rating.movie.title if hasattr(rating, 'movie') else None
        
        return cls(**data)
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ReviewDTO:
    """Review data transfer object."""
    id: int
    user_id: int
    movie_id: int
    content: str
    rating: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]
    username: Optional[str] = None
    movie_title: Optional[str] = None
    likes_count: int = 0
    
    @classmethod
    def from_model(cls, review, include_relations=False):
        """Create DTO from Review model."""
        data = {
            'id': review.id,
            'user_id': review.user_id,
            'movie_id': review.movie_id,
            'content': review.content,
            'rating': review.rating if hasattr(review, 'rating') else None,
            'created_at': review.created_at,
            'updated_at': review.updated_at if hasattr(review, 'updated_at') else None,
            'likes_count': len(review.likes) if hasattr(review, 'likes') else 0
        }
        
        if include_relations:
            data['username'] = review.user.username if hasattr(review, 'user') else None
            data['movie_title'] = review.movie.title if hasattr(review, 'movie') else None
        
        return cls(**data)
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class MovieListDTO:
    """Movie list data transfer object."""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    is_public: bool
    created_at: datetime
    movies_count: int = 0
    username: Optional[str] = None
    movies: Optional[List[MovieDTO]] = None
    
    @classmethod
    def from_model(cls, movie_list, include_movies=False):
        """Create DTO from MovieList model."""
        data = {
            'id': movie_list.id,
            'user_id': movie_list.user_id,
            'name': movie_list.name,
            'description': movie_list.description,
            'is_public': movie_list.is_public,
            'created_at': movie_list.created_at,
            'movies_count': len(movie_list.movies) if hasattr(movie_list, 'movies') else 0,
            'username': movie_list.user.username if hasattr(movie_list, 'user') else None
        }
        
        if include_movies and hasattr(movie_list, 'movies'):
            data['movies'] = [MovieDTO.from_model(m) for m in movie_list.movies]
        
        return cls(**data)
    
    def to_dict(self):
        """Convert to dictionary."""
        data = asdict(self)
        if self.movies:
            data['movies'] = [m.to_dict() for m in self.movies]
        return data


@dataclass
class PaginationDTO:
    """Pagination metadata."""
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def from_pagination(cls, pagination):
        """Create DTO from Flask-SQLAlchemy pagination object."""
        return cls(
            page=pagination.page,
            per_page=pagination.per_page,
            total=pagination.total,
            total_pages=pagination.pages,
            has_next=pagination.has_next,
            has_prev=pagination.has_prev
        )
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ApiResponseDTO:
    """Standardized API response wrapper."""
    success: bool
    data: Any
    message: Optional[str] = None
    errors: Optional[Dict] = None
    meta: Optional[Dict] = None
    
    def to_dict(self):
        """Convert to dictionary."""
        response = {
            'success': self.success,
            'data': self.data
        }
        
        if self.message:
            response['message'] = self.message
        
        if self.errors:
            response['errors'] = self.errors
        
        if self.meta:
            response['meta'] = self.meta
        
        return response


def paginated_response(items: List, pagination, item_serializer=None):
    """
    Create a paginated API response.
    
    Args:
        items: List of items to return
        pagination: Pagination object
        item_serializer: Optional function to serialize items
    
    Returns:
        Dictionary with data and pagination metadata
    """
    if item_serializer:
        items = [item_serializer(item) for item in items]
    
    return {
        'items': items,
        'pagination': PaginationDTO.from_pagination(pagination).to_dict()
    }
