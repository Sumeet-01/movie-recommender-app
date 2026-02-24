"""
Advanced routes for CineMate application.
Provides comprehensive API endpoints and page routes.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required
from app.services.tmdb_api import tmdb_service
from app.repositories import MovieRepository, UserRepository, RatingRepository, ReviewRepository, ListRepository
from app.core.decorators import api_response, cached, rate_limit
from app.core.validators import validate_pagination_params
from app.dto import MovieDTO, UserDTO, RatingDTO, paginated_response
from app.ml import recommendation_engine
from app import db
from app.models.movie import Movie, Rating, Review, MovieList

bp = Blueprint('main', __name__)


# ============================================================================
# PAGE ROUTES
# ============================================================================

@bp.route('/')
@bp.route('/index')
def index():
    """Enhanced homepage with multiple sections."""
    trending_movies = tmdb_service.get_trending_movies()
    popular_movies = tmdb_service.get_popular_movies()
    genres = tmdb_service.get_genres()
    
    stats = None
    recommendations = None
    
    if current_user.is_authenticated:
        stats = current_user.get_stats()
        # Get personalized recommendations
        try:
            rec_data = recommendation_engine.hybrid_recommendations(current_user.id, n_recommendations=10)
            # Fetch movie details for recommendations
            recommendations = []
            for rec in rec_data[:10]:
                movie_details = tmdb_service.get_movie_details(rec['movie_id'])
                if movie_details:
                    movie_details['poster_url'] = tmdb_service.get_image_url(movie_details.get('poster_path'), 'w500')
                    recommendations.append(movie_details)
        except Exception as e:
            print(f"Error getting recommendations: {e}")
    
    return render_template(
        'index.html',
        title='Home',
        movies=trending_movies,
        popular_movies=popular_movies,
        genres=genres[:10],  # Show top 10 genres
        stats=stats,
        recommendations=recommendations
    )


@bp.route('/discover')
def discover():
    """Advanced discover page with filters."""
    page = request.args.get('page', 1, type=int)
    genre = request.args.get('genre', type=int)
    year = request.args.get('year', type=int)
    sort_by = request.args.get('sort_by', 'popularity.desc')
    min_rating = request.args.get('min_rating', type=float)
    
    filters = {'page': page, 'sort_by': sort_by}
    
    if genre:
        filters['with_genres'] = genre
    if year:
        filters['year'] = year
    if min_rating:
        filters['vote_average.gte'] = min_rating
    
    movies = tmdb_service.discover_movies(**filters)
    genres = tmdb_service.get_genres()
    
    return render_template(
        'discover.html',
        title='Discover Movies',
        movies=movies,
        genres=genres,
        current_filters=filters
    )


@bp.route('/trending')
def trending():
    """Trending movies page."""
    time_window = request.args.get('window', 'week')
    page = request.args.get('page', 1, type=int)
    
    movies = tmdb_service.get_trending_movies(time_window, page)
    
    return render_template(
        'trending.html',
        title='Trending Movies',
        movies=movies,
        time_window=time_window
    )


@bp.route('/popular')
def popular():
    """Popular movies page."""
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_popular_movies(page)
    
    return render_template(
        'popular.html',
        title='Popular Movies',
        movies=movies
    )


@bp.route('/top-rated')
def top_rated():
    """Top rated movies page."""
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_top_rated_movies(page)
    
    return render_template(
        'top_rated.html',
        title='Top Rated Movies',
        movies=movies
    )


@bp.route('/movie/<int:tmdb_id>')
def movie_details(tmdb_id):
    """Enhanced movie details page."""
    details = tmdb_service.get_movie_details(tmdb_id)
    
    if not details:
        flash('Movie not found!', 'error')
        return redirect(url_for('main.index'))
    
    # Get or create movie in database
    movie = MovieRepository.get_or_create_by_tmdb_id(
        tmdb_id=tmdb_id,
        title=details.get('title'),
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
    
    # Get user-specific data
    in_watchlist = False
    user_rating = None
    user_review = None
    
    if current_user.is_authenticated:
        in_watchlist = current_user.is_in_watchlist(movie)
        user_rating = current_user.get_rating_for_movie(movie.id)
        user_review = Review.query.filter_by(user_id=current_user.id, movie_id=movie.id).first()
    
    # Get similar movies
    similar_movies = tmdb_service.get_similar_movies(tmdb_id)
    
    # Get reviews
    reviews = ReviewRepository.get_movie_reviews(movie.id, page=1, per_page=5)
    
    # Get trailers
    videos = details.get('videos', {}).get('results', [])
    trailers = [v for v in videos if v.get('type') == 'Trailer']
    
    return render_template(
        'movie_details.html',
        title=details.get('title'),
        movie=details,
        movie_db=movie,
        in_watchlist=in_watchlist,
        user_rating=user_rating,
        user_review=user_review,
        similar_movies=similar_movies[:6],
        reviews=reviews.items,
        trailers=trailers[:3]
    )


@bp.route('/recommendations')
@login_required
def recommendations():
    """Personalized recommendations page."""
    # Load user ratings into recommendation engine
    recommendation_engine.load_ratings_data()
    
    # Get hybrid recommendations
    rec_data = recommendation_engine.hybrid_recommendations(current_user.id, n_recommendations=50)
    
    # Fetch movie details
    movies = []
    for rec in rec_data:
        movie_details = tmdb_service.get_movie_details(rec['movie_id'])
        if movie_details:
            movie_details['recommendation_score'] = rec['score']
            movies.append(movie_details)
    
    return render_template(
        'recommendations.html',
        title='Your Recommendations',
        movies=movies
    )


@bp.route('/watchlist')
@login_required
def watchlist():
    """User's watchlist page."""
    watchlist_movies = current_user.watchlist
    
    # Enrich with TMDB data
    enriched_movies = []
    for movie in watchlist_movies:
        details = tmdb_service.get_movie_details(movie.tmdb_id)
        if details:
            enriched_movies.append(details)
    
    return render_template(
        'watchlist.html',
        title='My Watchlist',
        movies=enriched_movies
    )


@bp.route('/profile/<username>')
def profile(username):
    """User profile page."""
    try:
        user = UserRepository.get_by_username(username)
    except:
        flash('User not found', 'error')
        return redirect(url_for('main.index'))
    
    stats = user.get_stats()
    recent_ratings = RatingRepository.get_user_ratings(user.id)[:10]
    recent_reviews = ReviewRepository.get_user_reviews(user.id, page=1, per_page=5)
    favorite_genres = user.get_favorite_genres()
    
    return render_template(
        'profile.html',
        title=f"{username}'s Profile",
        user=user,
        stats=stats,
        recent_ratings=recent_ratings,
        recent_reviews=recent_reviews.items,
        favorite_genres=favorite_genres
    )


@bp.route('/genre/<int:genre_id>')
def genre(genre_id):
    """Movies by genre page."""
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_movies_by_genre(genre_id, page)
    genres = tmdb_service.get_genres()
    
    genre_name = next((g['name'] for g in genres if g['id'] == genre_id), 'Unknown')
    
    return render_template(
        'genre.html',
        title=f"{genre_name} Movies",
        movies=movies,
        genre_name=genre_name,
        genre_id=genre_id
    )


@bp.route('/my-lists')
@login_required
def my_lists():
    """User's custom lists page."""
    lists = ListRepository.get_user_lists(current_user.id)
    
    return render_template(
        'my_lists.html',
        title='My Lists',
        lists=lists
    )


@bp.route('/settings')
@login_required
def settings():
    """User settings page."""
    return render_template('settings.html', title='Settings')


# Placeholder routes for footer links
@bp.route('/about')
def about():
    return render_template('about.html', title='About CineMate')

@bp.route('/features')
def features():
    return render_template('features.html', title='Features')

@bp.route('/api-docs')
def api_docs():
    return render_template('api_docs.html', title='API Documentation')

@bp.route('/contact')
def contact():
    return render_template('contact.html', title='Contact Us')


# ============================================================================
# API ENDPOINTS
# ============================================================================

@bp.route('/api/search')
@rate_limit(max_requests=30, window=60)
def api_search():
    """Search API endpoint."""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if len(query) < 2:
        return jsonify({'results': [], 'total_results': 0})
    
    results = tmdb_service.search_movies(query, page)
    return jsonify(results)


@bp.route('/api/watchlist/add/<int:movie_id>', methods=['POST'])
@login_required
@api_response
def api_add_to_watchlist(movie_id):
    """Add movie to watchlist API."""
    movie = MovieRepository.get_by_id(movie_id)
    current_user.add_to_watchlist(movie)
    db.session.commit()
    return {'message': 'Added to watchlist', 'success': True}


@bp.route('/api/watchlist/remove/<int:movie_id>', methods=['POST'])
@login_required
@api_response
def api_remove_from_watchlist(movie_id):
    """Remove movie from watchlist API."""
    movie = MovieRepository.get_by_id(movie_id)
    current_user.remove_from_watchlist(movie)
    db.session.commit()
    return {'message': 'Removed from watchlist', 'success': True}


@bp.route('/api/rate/<int:tmdb_id>', methods=['POST'])
@login_required
@api_response
def api_rate_movie(tmdb_id):
    """Rate a movie API."""
    data = request.get_json()
    rating = data.get('rating')
    
    # Get or create movie
    movie = MovieRepository.get_or_create_by_tmdb_id(tmdb_id)
    
    # Create or update rating
    current_user.rate_movie(movie, rating)
    db.session.commit()
    
    # Update recommendation engine
    recommendation_engine.load_ratings_data()
    
    return {'message': 'Rating saved', 'rating': rating}


@bp.route('/api/review/<int:movie_id>', methods=['POST'])
@login_required
@api_response
def api_submit_review(movie_id):
    """Submit a review API."""
    data = request.get_json()
    content = data.get('content')
    rating = data.get('rating')
    title = data.get('title')
    is_spoiler = data.get('is_spoiler', False)
    
    review = Review(
        user_id=current_user.id,
        movie_id=movie_id,
        title=title,
        content=content,
        rating=rating,
        is_spoiler=is_spoiler
    )
    
    db.session.add(review)
    db.session.commit()
    
    return {'message': 'Review submitted', 'review_id': review.id}


@bp.route('/api/stats')
@login_required
@api_response
def api_user_stats():
    """Get user statistics API."""
    stats = UserRepository.get_user_stats(current_user.id)
    favorite_genres = current_user.get_favorite_genres()
    
    return {
        **stats,
        'favorite_genres': favorite_genres
    }


@bp.route('/api/recommendations')
@login_required
@cached(timeout=600)
@api_response
def api_recommendations():
    """Get recommendations API."""
    n = request.args.get('n', 20, type=int)
    
    recommendation_engine.load_ratings_data()
    recommendations = recommendation_engine.hybrid_recommendations(current_user.id, n)
    
    return {'recommendations': recommendations}


# Legacy routes (backwards compatibility)
@bp.route('/watchlist/add/<int:movie_id>')
@login_required
def add_to_watchlist(movie_id):
    """Legacy: Add to watchlist (redirects)."""
    movie = MovieRepository.get_by_id(movie_id)
    current_user.add_to_watchlist(movie)
    db.session.commit()
    flash(f'"{movie.title}" added to watchlist!', 'success')
    return redirect(url_for('main.movie_details', tmdb_id=movie.tmdb_id))


@bp.route('/watchlist/remove/<int:movie_id>')
@login_required
def remove_from_watchlist(movie_id):
    """Legacy: Remove from watchlist (redirects)."""
    movie = MovieRepository.get_by_id(movie_id)
    current_user.remove_from_watchlist(movie)
    db.session.commit()
    flash(f'"{movie.title}" removed from watchlist.', 'info')
    return redirect(url_for('main.movie_details', tmdb_id=movie.tmdb_id))
