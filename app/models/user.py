from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from app.models.movie import watchlist, Review, Rating, Activity, MovieList

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    """Enhanced User model with profile and preferences."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    
    # Profile information
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(500))
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    
    # Preferences
    is_private = db.Column(db.Boolean, default=False)
    email_notifications = db.Column(db.Boolean, default=True)
    theme_preference = db.Column(db.String(20), default='dark')  # 'dark' or 'light'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    watchlist = db.relationship(
        'Movie', secondary=watchlist, lazy='subquery',
        backref=db.backref('users', lazy=True)
    )
    ratings = db.relationship('Rating', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    lists = db.relationship('MovieList', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)

    def add_to_watchlist(self, movie):
        """Add movie to watchlist."""
        if not self.is_in_watchlist(movie):
            self.watchlist.append(movie)
            self._log_activity('watchlist_add', movie.id)

    def remove_from_watchlist(self, movie):
        """Remove movie from watchlist."""
        if self.is_in_watchlist(movie):
            self.watchlist.remove(movie)
            self._log_activity('watchlist_remove', movie.id)

    def is_in_watchlist(self, movie):
        """Check if movie is in watchlist."""
        return movie in self.watchlist
    
    def rate_movie(self, movie, score):
        """Rate a movie."""
        from app.repositories import RatingRepository
        rating = RatingRepository.create_or_update_rating(self.id, movie.id, score)
        self._log_activity('rating', movie.id, {'score': score})
        return rating
    
    def get_rating_for_movie(self, movie_id):
        """Get user's rating for a specific movie."""
        rating = Rating.query.filter_by(user_id=self.id, movie_id=movie_id).first()
        return rating.score if rating else None
    
    def has_reviewed(self, movie_id):
        """Check if user has reviewed a movie."""
        return Review.query.filter_by(user_id=self.id, movie_id=movie_id).first() is not None
    
    def _log_activity(self, activity_type, movie_id=None, extra_data=None):
        """Log user activity."""
        import json
        activity = Activity(
            user_id=self.id,
            activity_type=activity_type,
            movie_id=movie_id,
            activity_data=json.dumps(extra_data) if extra_data else None
        )
        db.session.add(activity)
    
    def get_stats(self):
        """Get user statistics."""
        return {
            'watchlist_count': len(self.watchlist),
            'ratings_count': self.ratings.count(),
            'reviews_count': self.reviews.count(),
            'lists_count': self.lists.count(),
            'member_since': self.created_at.strftime('%B %Y')
        }
    
    def get_favorite_genres(self, limit=5):
        """Get user's favorite genres based on ratings."""
        from sqlalchemy import func
        from app.models.movie import Genre, movie_genres, Movie
        
        # Get genres from highly rated movies
        favorite_genres = db.session.query(
            Genre.name,
            func.count(Genre.id).label('count')
        ).join(movie_genres).join(Movie).join(Rating).filter(
            Rating.user_id == self.id,
            Rating.score >= 4.0
        ).group_by(Genre.name).order_by(
            func.count(Genre.id).desc()
        ).limit(limit).all()
        
        return [genre for genre, _ in favorite_genres]
    
    def update_last_seen(self):
        """Update last seen timestamp."""
        self.last_seen = datetime.utcnow()
    
    def to_dict(self, include_private=False):
        """Convert to dictionary."""
        data = {
            'id': self.id,
            'username': self.username,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'location': self.location,
            'website': self.website,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'stats': self.get_stats()
        }
        
        if include_private:
            data['email'] = self.email
            data['is_private'] = self.is_private
            data['email_notifications'] = self.email_notifications
            data['theme_preference'] = self.theme_preference
        
        return data

    def __repr__(self):
        return f'<User {self.username}>'