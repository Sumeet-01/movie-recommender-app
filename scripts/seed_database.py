"""
Database seeding script for CineMate.
Populates database with sample data for development and testing.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User
from app.models.movie import Movie, Genre, Rating, Review, MovieList
from app.services.tmdb_api import tmdb_service
from datetime import datetime
import random


def seed_users():
    """Create sample users."""
    print("🌱 Seeding users...")
    
    users_data = [
        {'username': 'john_doe', 'email': 'john@example.com', 'bio': 'Movie enthusiast'},
        {'username': 'jane_smith', 'email': 'jane@example.com', 'bio': 'Film critic'},
        {'username': 'movie_buff', 'email': 'buff@example.com', 'bio': 'I love cinema!'},
        {'username': 'critic_pro', 'email': 'critic@example.com', 'bio': 'Professional critic'},
        {'username': 'casual_viewer', 'email': 'casual@example.com', 'bio': 'Watching for fun'},
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        user.set_password('password123')  # Demo password
        db.session.add(user)
        users.append(user)
    
    db.session.commit()
    print(f"✅ Created {len(users)} users")
    return users


def seed_genres():
    """Fetch and store genres from TMDB."""
    print("🌱 Seeding genres...")
    
    genres_data = tmdb_service.get_genres()
    genres = []
    
    for genre_data in genres_data:
        genre = Genre.query.filter_by(tmdb_id=genre_data['id']).first()
        if not genre:
            genre = Genre(tmdb_id=genre_data['id'], name=genre_data['name'])
            db.session.add(genre)
            genres.append(genre)
    
    db.session.commit()
    print(f"✅ Created {len(genres)} genres")
    return genres


def seed_movies():
    """Fetch and store popular movies from TMDB."""
    print("🌱 Seeding movies...")
    
    # Get popular movies
    popular_movies = tmdb_service.get_popular_movies(page=1)
    trending_movies = tmdb_service.get_trending_movies(time_window='week')
    top_rated_movies = tmdb_service.get_top_rated_movies(page=1)
    
    all_movies = popular_movies + trending_movies + top_rated_movies
    movies = []
    
    for movie_data in all_movies[:50]:  # Limit to 50 movies
        existing = Movie.query.filter_by(tmdb_id=movie_data['id']).first()
        if not existing:
            # Get detailed info
            details = tmdb_service.get_movie_details(movie_data['id'])
            if details:
                movie = Movie(
                    tmdb_id=details['id'],
                    title=details['title'],
                    overview=details.get('overview'),
                    poster_path=details.get('poster_path'),
                    backdrop_path=details.get('backdrop_path'),
                    release_date=details.get('release_date'),
                    runtime=details.get('runtime'),
                    tagline=details.get('tagline'),
                    vote_average=details.get('vote_average'),
                    vote_count=details.get('vote_count'),
                    popularity=details.get('popularity')
                )
                
                # Add genres
                if 'genres' in details:
                    for genre_data in details['genres']:
                        genre = Genre.query.filter_by(tmdb_id=genre_data['id']).first()
                        if genre:
                            movie.genres.append(genre)
                
                db.session.add(movie)
                movies.append(movie)
                
                # Commit in batches
                if len(movies) % 10 == 0:
                    db.session.commit()
                    print(f"  Processed {len(movies)} movies...")
    
    db.session.commit()
    print(f"✅ Created {len(movies)} movies")
    return movies


def seed_ratings(users, movies):
    """Create sample ratings."""
    print("🌱 Seeding ratings...")
    
    ratings = []
    for user in users[:3]:  # Use first 3 users
        # Each user rates 10-20 random movies
        num_ratings = random.randint(10, 20)
        rated_movies = random.sample(movies, min(num_ratings, len(movies)))
        
        for movie in rated_movies:
            score = random.choice([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
            rating = Rating(user_id=user.id, movie_id=movie.id, score=score)
            db.session.add(rating)
            ratings.append(rating)
    
    db.session.commit()
    print(f"✅ Created {len(ratings)} ratings")
    return ratings


def seed_reviews(users, movies):
    """Create sample reviews."""
    print("🌱 Seeding reviews...")
    
    sample_reviews = [
        "Amazing movie! Highly recommended.",
        "Great cinematography and storyline.",
        "Not bad, but could be better.",
        "Excellent performances by the cast.",
        "A masterpiece of modern cinema.",
        "Disappointing compared to expectations.",
        "Worth watching with family.",
        "Best movie of the year!",
    ]
    
    reviews = []
    for user in users[:2]:  # Use first 2 users
        # Each user writes 3-5 reviews
        num_reviews = random.randint(3, 5)
        reviewed_movies = random.sample(movies, min(num_reviews, len(movies)))
        
        for movie in reviewed_movies:
            review = Review(
                user_id=user.id,
                movie_id=movie.id,
                title=f"Review of {movie.title}",
                content=random.choice(sample_reviews),
                rating=random.choice([3.0, 3.5, 4.0, 4.5, 5.0])
            )
            db.session.add(review)
            reviews.append(review)
    
    db.session.commit()
    print(f"✅ Created {len(reviews)} reviews")
    return reviews


def seed_watchlists(users, movies):
    """Add movies to user watchlists."""
    print("🌱 Seeding watchlists...")
    
    for user in users:
        # Each user adds 5-10 movies to watchlist
        num_watchlist = random.randint(5, 10)
        watchlist_movies = random.sample(movies, min(num_watchlist, len(movies)))
        
        for movie in watchlist_movies:
            if movie not in user.watchlist:
                user.watchlist.append(movie)
    
    db.session.commit()
    print(f"✅ Populated watchlists for {len(users)} users")


def seed_lists(users, movies):
    """Create sample movie lists."""
    print("🌱 Seeding custom lists...")
    
    list_names = [
        ("Sci-Fi Favorites", "My favorite science fiction movies"),
        ("Classic Must-Watch", "Timeless classics everyone should see"),
        ("Action Packed", "Best action movies of all time"),
        ("Comedies to Watch", "Hilarious movies for a good laugh"),
        ("Drama Masterpieces", "Powerful dramatic films"),
    ]
    
    lists = []
    for user in users[:2]:
        for name, description in random.sample(list_names, 2):
            movie_list = MovieList(
                user_id=user.id,
                name=name,
                description=description,
                is_public=random.choice([True, False])
            )
            
            # Add 5-8 random movies to list
            list_movies = random.sample(movies, min(8, len(movies)))
            movie_list.movies.extend(list_movies)
            
            db.session.add(movie_list)
            lists.append(movie_list)
    
    db.session.commit()
    print(f"✅ Created {len(lists)} custom lists")
    return lists


def main():
    """Run all seeding functions."""
    app = create_app()
    
    with app.app_context():
        print("\n🚀 Starting database seeding...\n")
        
        # Check if already seeded
        if User.query.count() > 0:
            response = input("⚠️  Database appears to have data. Continue? (y/n): ")
            if response.lower() != 'y':
                print("Seeding cancelled.")
                return
            
            # Optionally clear existing data
            clear = input("Clear existing data first? (y/n): ")
            if clear.lower() == 'y':
                print("🗑️  Clearing existing data...")
                db.drop_all()
                db.create_all()
        
        try:
            # Seed in order
            users = seed_users()
            genres = seed_genres()
            movies = seed_movies()
            ratings = seed_ratings(users, movies)
            reviews = seed_reviews(users, movies)
            seed_watchlists(users, movies)
            lists = seed_lists(users, movies)
            
            print("\n✅ Database seeding completed successfully!")
            print(f"\n📊 Summary:")
            print(f"   Users: {len(users)}")
            print(f"   Genres: {len(genres)}")
            print(f"   Movies: {len(movies)}")
            print(f"   Ratings: {len(ratings)}")
            print(f"   Reviews: {len(reviews)}")
            print(f"   Lists: {len(lists)}")
            print(f"\n🎬 You can now login with:")
            print(f"   Username: john_doe")
            print(f"   Password: password123")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            db.session.rollback()
            raise


if __name__ == '__main__':
    main()
