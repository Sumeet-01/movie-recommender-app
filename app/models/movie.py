from app import db
from datetime import datetime
from sqlalchemy import func

# Association table for watchlist
watchlist = db.Table('watchlist',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'), primary_key=True),
    db.Column('added_at', db.DateTime, default=datetime.utcnow)
)

# Association table for movie lists
list_movies = db.Table('list_movies',
    db.Column('list_id', db.Integer, db.ForeignKey('movie_lists.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'), primary_key=True),
    db.Column('added_at', db.DateTime, default=datetime.utcnow),
    db.Column('position', db.Integer, default=0)
)

# Association table for review likes
review_likes = db.Table('review_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('review_id', db.Integer, db.ForeignKey('reviews.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class Movie(db.Model):
    """Enhanced Movie model with additional metadata."""
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    overview = db.Column(db.Text)
    poster_path = db.Column(db.String(255))
    backdrop_path = db.Column(db.String(255))
    release_date = db.Column(db.String(50))
    runtime = db.Column(db.Integer)
    tagline = db.Column(db.String(500))
    vote_average = db.Column(db.Float, default=0.0)
    vote_count = db.Column(db.Integer, default=0)
    popularity = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ratings = db.relationship('Rating', backref='movie', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='movie', lazy='dynamic', cascade='all, delete-orphan')
    genres = db.relationship('Genre', secondary='movie_genres', backref='movies')
    
    def __repr__(self):
        return f'<Movie {self.title}>'
    
    def get_average_rating(self):
        """Calculate average user rating."""
        avg = db.session.query(func.avg(Rating.score)).filter_by(movie_id=self.id).scalar()
        return round(float(avg), 2) if avg else 0.0
    
    def get_rating_count(self):
        """Get total number of ratings."""
        return self.ratings.count()
    
    def get_poster_url(self, size='w500'):
        """Get full poster URL."""
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/{size}{self.poster_path}"
        return "https://via.placeholder.com/500x750.png?text=No+Image"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'tmdb_id': self.tmdb_id,
            'title': self.title,
            'overview': self.overview,
            'poster_path': self.poster_path,
            'backdrop_path': self.backdrop_path,
            'release_date': self.release_date,
            'runtime': self.runtime,
            'tagline': self.tagline,
            'vote_average': self.vote_average,
            'vote_count': self.vote_count,
            'user_rating': self.get_average_rating(),
            'user_rating_count': self.get_rating_count()
        }


class Genre(db.Model):
    """Movie genre model."""
    __tablename__ = 'genres'
    
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Genre {self.name}>'


# Association table for movie-genre relationship
movie_genres = db.Table('movie_genres',
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)


class Rating(db.Model):
    """Enhanced rating model with half-star support."""
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)  # 0.5 to 5.0 in 0.5 increments
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    # Unique constraint: one rating per user per movie
    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_rating'),)
    
    def __repr__(self):
        return f'<Rating User:{self.user_id} Movie:{self.movie_id} Score:{self.score}>'


class Review(db.Model):
    """User review model."""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float)  # Optional: can rate inline with review
    is_spoiler = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    likes = db.relationship('User', secondary=review_likes, backref='liked_reviews')
    
    def __repr__(self):
        return f'<Review {self.id} by User:{self.user_id}>'
    
    def get_likes_count(self):
        """Get number of likes."""
        return len(self.likes)


class MovieList(db.Model):
    """Custom user-created movie lists."""
    __tablename__ = 'movie_lists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    movies = db.relationship('Movie', secondary=list_movies, backref='lists')
    
    def __repr__(self):
        return f'<MovieList {self.name}>'
    
    def get_movie_count(self):
        """Get number of movies in list."""
        return len(self.movies)


class Activity(db.Model):
    """User activity tracking."""
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 'rating', 'review', 'watchlist', etc.
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))
    activity_data = db.Column(db.Text)  # JSON string for additional data
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Activity {self.activity_type} by User:{self.user_id}>'