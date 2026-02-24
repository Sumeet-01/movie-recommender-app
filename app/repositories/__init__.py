"""
Repository pattern implementation for data access layer.
Provides abstraction between business logic and data access.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import or_, and_, desc
from app import db
from app.core.exceptions import DatabaseException, ResourceNotFoundException


class BaseRepository:
    """Base repository with common CRUD operations."""
    
    model = None  # Should be overridden by subclasses
    
    @classmethod
    def get_by_id(cls, id: int):
        """Get entity by ID."""
        try:
            entity = cls.model.query.get(id)
            if not entity:
                raise ResourceNotFoundException(cls.model.__name__)
            return entity
        except Exception as e:
            if isinstance(e, ResourceNotFoundException):
                raise
            raise DatabaseException(f"Error fetching {cls.model.__name__}")
    
    @classmethod
    def get_all(cls, page: int = 1, per_page: int = 20, **filters):
        """Get all entities with pagination and filters."""
        try:
            query = cls.model.query
            
            # Apply filters
            for key, value in filters.items():
                if hasattr(cls.model, key) and value is not None:
                    query = query.filter(getattr(cls.model, key) == value)
            
            return query.paginate(page=page, per_page=per_page, error_out=False)
        except Exception as e:
            raise DatabaseException(f"Error fetching {cls.model.__name__} list")
    
    @classmethod
    def create(cls, **kwargs):
        """Create new entity."""
        try:
            entity = cls.model(**kwargs)
            db.session.add(entity)
            db.session.commit()
            return entity
        except Exception as e:
            db.session.rollback()
            raise DatabaseException(f"Error creating {cls.model.__name__}")
    
    @classmethod
    def update(cls, id: int, **kwargs):
        """Update entity by ID."""
        try:
            entity = cls.get_by_id(id)
            
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            db.session.commit()
            return entity
        except Exception as e:
            db.session.rollback()
            if isinstance(e, ResourceNotFoundException):
                raise
            raise DatabaseException(f"Error updating {cls.model.__name__}")
    
    @classmethod
    def delete(cls, id: int):
        """Delete entity by ID."""
        try:
            entity = cls.get_by_id(id)
            db.session.delete(entity)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            if isinstance(e, ResourceNotFoundException):
                raise
            raise DatabaseException(f"Error deleting {cls.model.__name__}")
    
    @classmethod
    def count(cls, **filters):
        """Count entities with optional filters."""
        try:
            query = cls.model.query
            
            for key, value in filters.items():
                if hasattr(cls.model, key) and value is not None:
                    query = query.filter(getattr(cls.model, key) == value)
            
            return query.count()
        except Exception as e:
            raise DatabaseException(f"Error counting {cls.model.__name__}")
    
    @classmethod
    def exists(cls, **filters):
        """Check if entity exists with given filters."""
        try:
            query = cls.model.query
            
            for key, value in filters.items():
                if hasattr(cls.model, key):
                    query = query.filter(getattr(cls.model, key) == value)
            
            return query.first() is not None
        except Exception as e:
            raise DatabaseException(f"Error checking {cls.model.__name__} existence")


class UserRepository(BaseRepository):
    """Repository for User entities."""
    
    from app.models.user import User
    model = User
    
    @classmethod
    def get_by_username(cls, username: str):
        """Get user by username."""
        user = cls.model.query.filter_by(username=username).first()
        if not user:
            raise ResourceNotFoundException("User")
        return user
    
    @classmethod
    def get_by_email(cls, email: str):
        """Get user by email."""
        user = cls.model.query.filter_by(email=email).first()
        if not user:
            raise ResourceNotFoundException("User")
        return user
    
    @classmethod
    def find_by_username_or_email(cls, identifier: str):
        """Find user by username or email."""
        return cls.model.query.filter(
            or_(cls.model.username == identifier, cls.model.email == identifier)
        ).first()
    
    @classmethod
    def get_user_stats(cls, user_id: int) -> Dict[str, Any]:
        """Get user statistics."""
        from app.models.movie import Rating
        
        user = cls.get_by_id(user_id)
        
        return {
            'watchlist_count': len(user.watchlist),
            'ratings_count': Rating.query.filter_by(user_id=user_id).count(),
            'reviews_count': len(user.reviews),
            'lists_count': len(user.lists)
        }


class MovieRepository(BaseRepository):
    """Repository for Movie entities."""
    
    from app.models.movie import Movie
    model = Movie
    
    @classmethod
    def get_by_tmdb_id(cls, tmdb_id: int):
        """Get movie by TMDB ID."""
        movie = cls.model.query.filter_by(tmdb_id=tmdb_id).first()
        if not movie:
            raise ResourceNotFoundException("Movie")
        return movie
    
    @classmethod
    def get_or_create_by_tmdb_id(cls, tmdb_id: int, **kwargs):
        """Get existing movie or create new one."""
        try:
            return cls.get_by_tmdb_id(tmdb_id)
        except ResourceNotFoundException:
            kwargs['tmdb_id'] = tmdb_id
            return cls.create(**kwargs)
    
    @classmethod
    def search(cls, query: str, page: int = 1, per_page: int = 20):
        """Search movies by title."""
        search_query = cls.model.query.filter(
            cls.model.title.ilike(f'%{query}%')
        )
        return search_query.paginate(page=page, per_page=per_page, error_out=False)
    
    @classmethod
    def get_popular(cls, limit: int = 20):
        """Get popular movies based on ratings."""
        from app.models.movie import Rating
        from sqlalchemy import func
        
        popular_movies = db.session.query(
            cls.model,
            func.avg(Rating.score).label('avg_rating'),
            func.count(Rating.id).label('rating_count')
        ).join(Rating).group_by(cls.model.id).order_by(
            desc('rating_count')
        ).limit(limit).all()
        
        return [movie for movie, _, _ in popular_movies]


class RatingRepository(BaseRepository):
    """Repository for Rating entities."""
    
    from app.models.movie import Rating
    model = Rating
    
    @classmethod
    def get_user_rating(cls, user_id: int, movie_id: int):
        """Get user's rating for a specific movie."""
        return cls.model.query.filter_by(
            user_id=user_id,
            movie_id=movie_id
        ).first()
    
    @classmethod
    def create_or_update_rating(cls, user_id: int, movie_id: int, score: float):
        """Create new rating or update existing one."""
        existing = cls.get_user_rating(user_id, movie_id)
        
        if existing:
            existing.score = score
            db.session.commit()
            return existing
        else:
            return cls.create(user_id=user_id, movie_id=movie_id, score=score)
    
    @classmethod
    def get_movie_ratings(cls, movie_id: int):
        """Get all ratings for a movie."""
        return cls.model.query.filter_by(movie_id=movie_id).all()
    
    @classmethod
    def get_user_ratings(cls, user_id: int):
        """Get all ratings by a user."""
        return cls.model.query.filter_by(user_id=user_id).all()
    
    @classmethod
    def get_average_rating(cls, movie_id: int) -> Optional[float]:
        """Get average rating for a movie."""
        from sqlalchemy import func
        
        result = db.session.query(
            func.avg(cls.model.score)
        ).filter_by(movie_id=movie_id).scalar()
        
        return float(result) if result else None


class ReviewRepository(BaseRepository):
    """Repository for Review entities."""
    
    from app.models.movie import Review
    model = Review
    
    @classmethod
    def get_movie_reviews(cls, movie_id: int, page: int = 1, per_page: int = 10):
        """Get reviews for a movie with pagination."""
        from datetime import datetime
        
        query = cls.model.query.filter_by(movie_id=movie_id).order_by(
            desc(cls.model.created_at)
        )
        return query.paginate(page=page, per_page=per_page, error_out=False)
    
    @classmethod
    def get_user_reviews(cls, user_id: int, page: int = 1, per_page: int = 10):
        """Get reviews by a user with pagination."""
        query = cls.model.query.filter_by(user_id=user_id).order_by(
            desc(cls.model.created_at)
        )
        return query.paginate(page=page, per_page=per_page, error_out=False)


class ListRepository(BaseRepository):
    """Repository for custom movie lists."""
    
    from app.models.movie import MovieList
    model = MovieList
    
    @classmethod
    def get_user_lists(cls, user_id: int):
        """Get all lists created by a user."""
        return cls.model.query.filter_by(user_id=user_id).all()
    
    @classmethod
    def get_public_lists(cls, page: int = 1, per_page: int = 20):
        """Get public lists."""
        query = cls.model.query.filter_by(is_public=True).order_by(
            desc(cls.model.created_at)
        )
        return query.paginate(page=page, per_page=per_page, error_out=False)
