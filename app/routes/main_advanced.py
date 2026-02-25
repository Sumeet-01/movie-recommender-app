"""
CineMate Routes — Production Grade
Movies + TV Series, Top 10, OTT providers, trailers, multi-search,
India-bias, intelligent recommendations.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required
from app.services.tmdb_api import tmdb_service
from app.repositories import MovieRepository, UserRepository, RatingRepository, ReviewRepository, ListRepository
from app.core.decorators import api_response, rate_limit
from app.ml import recommendation_engine
from app import db
from app.models.movie import Movie, Rating, Review, MovieList

bp = Blueprint('main', __name__)


# ============================================================================
# HOMEPAGE
# ============================================================================

@bp.route('/')
@bp.route('/index')
def index():
    """Homepage: hero slider, Top 10, Bollywood-first, regional sections."""
    trending = tmdb_service.get_trending_movies()
    top10_india = tmdb_service.get_top10_india()
    trending_bollywood = tmdb_service.get_trending_bollywood()
    top10_series = tmdb_service.get_top10_series()
    bollywood = tmdb_service.get_bollywood_movies()
    south_indian = tmdb_service.get_south_indian_movies()
    now_playing = tmdb_service.get_now_playing_movies()
    popular = tmdb_service.get_popular_movies()
    hollywood = tmdb_service.get_hollywood_movies()
    korean = tmdb_service.get_korean_movies()
    anime = tmdb_service.get_anime_movies()
    top_rated = tmdb_service.get_top_rated_movies()
    upcoming = tmdb_service.get_upcoming_movies()
    trending_tv = tmdb_service.get_trending_tv()
    genres = tmdb_service.get_genres()

    # Personalized recommendations
    recommendations = None
    stats = None
    if current_user.is_authenticated:
        stats = current_user.get_stats()
        try:
            recommendation_engine.load_ratings_data()
            rec_data = recommendation_engine.hybrid_recommendations(current_user.id, 10)
            recommendations = []
            for rec in rec_data[:10]:
                md = tmdb_service.get_movie_details(rec['movie_id'])
                if md:
                    recommendations.append(md)
        except Exception:
            pass

    return render_template('index.html',
        title='Home',
        trending=trending,
        top10_india=top10_india,
        trending_bollywood=trending_bollywood,
        top10_series=top10_series,
        bollywood=bollywood,
        south_indian=south_indian,
        now_playing=now_playing,
        popular=popular,
        hollywood=hollywood,
        korean=korean,
        anime=anime,
        top_rated=top_rated,
        upcoming=upcoming,
        trending_tv=trending_tv,
        genres=genres,
        stats=stats,
        recommendations=recommendations,
    )


# ============================================================================
# DISCOVER
# ============================================================================

@bp.route('/discover')
def discover():
    page = request.args.get('page', 1, type=int)
    genre = request.args.get('genre', type=int)
    year = request.args.get('year', type=int)
    sort_by = request.args.get('sort', 'popularity.desc')
    min_rating = request.args.get('min_rating', type=float)
    language = request.args.get('language', '')

    filters = {'page': page, 'sort_by': sort_by}
    if genre:
        filters['with_genres'] = genre
    if year:
        filters['year'] = year
    if min_rating:
        filters['vote_average.gte'] = min_rating
    if language:
        filters['with_original_language'] = language

    movies = tmdb_service.discover_movies(**filters)
    genres = tmdb_service.get_genres()

    return render_template('discover.html',
        title='Discover Movies', movies=movies, genres=genres,
        current_filters={'page': page, 'genre': genre, 'year': year, 'sort': sort_by, 'min_rating': min_rating, 'language': language}
    )


# ============================================================================
# BROWSING PAGES
# ============================================================================

@bp.route('/trending')
def trending():
    tw = request.args.get('window', 'week')
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_trending_movies(tw, page)
    return render_template('grid_page.html', title='Trending Movies', movies=movies, subtitle='What everyone is watching this week')

@bp.route('/popular')
def popular():
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_popular_movies(page)
    return render_template('grid_page.html', title='Popular Movies', movies=movies, subtitle='Most popular right now')

@bp.route('/top-rated')
def top_rated():
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_top_rated_movies(page)
    return render_template('grid_page.html', title='Top Rated Movies', movies=movies, subtitle='Highest rated of all time')

@bp.route('/now-playing')
def now_playing():
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_now_playing_movies(page)
    return render_template('grid_page.html', title='Now In Theaters', movies=movies, subtitle='Currently showing in theaters near you')

@bp.route('/upcoming')
def upcoming():
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_upcoming_movies(page)
    return render_template('grid_page.html', title='Coming Soon', movies=movies, subtitle='Upcoming movies to look forward to')


# ============================================================================
# REGIONAL
# ============================================================================

@bp.route('/bollywood')
def bollywood():
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_bollywood_movies(page)
    return render_template('grid_page.html', title='🇮🇳 Bollywood', movies=movies, subtitle='Best of Hindi Cinema', accent='#ff6b35')

@bp.route('/south-indian')
def south_indian():
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_south_indian_movies(page)
    return render_template('grid_page.html', title='🌴 South Indian Cinema', movies=movies, subtitle='Tamil, Telugu, Malayalam & Kannada', accent='#00c9a7')

@bp.route('/tamil')
def tamil():
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_tamil_movies(page)
    return render_template('grid_page.html', title='🎭 Tamil Movies', movies=movies, subtitle="Kollywood's Finest", accent='#ffd93d')

@bp.route('/telugu')
def telugu():
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_telugu_movies(page)
    return render_template('grid_page.html', title='🎥 Telugu Movies', movies=movies, subtitle='Tollywood Hits', accent='#6bcb77')

@bp.route('/malayalam')
def malayalam():
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_malayalam_movies(page)
    return render_template('grid_page.html', title='🎞️ Malayalam Movies', movies=movies, subtitle='Mollywood Magic', accent='#4d96ff')

@bp.route('/hollywood')
def hollywood():
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_hollywood_movies(page)
    return render_template('grid_page.html', title='🎬 Hollywood', movies=movies, subtitle='English Language Blockbusters', accent='#9b59b6')

@bp.route('/korean')
def korean():
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_korean_movies(page)
    return render_template('grid_page.html', title='🇰🇷 Korean Cinema', movies=movies, subtitle='K-Movies & K-Drama Films', accent='#e74c3c')

@bp.route('/anime')
def anime():
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_anime_movies(page)
    return render_template('grid_page.html', title='🎌 Anime Movies', movies=movies, subtitle='Japanese Animation Films', accent='#e91e63')


# ============================================================================
# TV SERIES
# ============================================================================

@bp.route('/tv')
def tv_home():
    trending_tv = tmdb_service.get_trending_tv()
    popular_tv = tmdb_service.get_popular_tv()
    top_rated_tv = tmdb_service.get_top_rated_tv()
    indian_tv = tmdb_service.get_indian_tv()
    return render_template('tv_home.html',
        title='TV Series',
        trending_tv=trending_tv,
        popular_tv=popular_tv,
        top_rated_tv=top_rated_tv,
        indian_tv=indian_tv,
    )

@bp.route('/tv/<int:tv_id>')
def tv_details(tv_id):
    details = tmdb_service.get_tv_details(tv_id)
    if not details:
        flash('Series not found!', 'error')
        return redirect(url_for('main.index'))
    similar = details.get('similar', {}).get('results', [])
    for s in similar:
        s['poster_url'] = tmdb_service.img(s.get('poster_path'), 'w500')
        s['title'] = s.get('name', '')
        s['release_date'] = s.get('first_air_date', '')
        s['media_type'] = 'tv'
    return render_template('tv_details.html',
        title=details.get('title', ''),
        show=details,
        similar_shows=similar[:8],
        trailers=details.get('trailers', []),
        ott_providers=details.get('ott_providers', []),
    )


# ============================================================================
# MOVIE DETAILS (with OTT + trailers + recommendation engine feed)
# ============================================================================

@bp.route('/movie/<int:tmdb_id>')
def movie_details(tmdb_id):
    details = tmdb_service.get_movie_details(tmdb_id)
    if not details:
        flash('Movie not found!', 'error')
        return redirect(url_for('main.index'))

    # Feed recommendation engine
    recommendation_engine.ingest_movie(tmdb_id, details)

    # DB record
    movie = MovieRepository.get_or_create_by_tmdb_id(
        tmdb_id=tmdb_id,
        title=details.get('title', 'Unknown'),
        overview=details.get('overview'),
        poster_path=details.get('poster_path'),
        backdrop_path=details.get('backdrop_path'),
        release_date=details.get('release_date'),
        runtime=details.get('runtime'),
        tagline=details.get('tagline'),
        vote_average=details.get('vote_average'),
        vote_count=details.get('vote_count'),
        popularity=details.get('popularity'),
    )

    in_watchlist = False
    user_rating = None
    user_review = None
    if current_user.is_authenticated:
        in_watchlist = current_user.is_in_watchlist(movie)
        user_rating = current_user.get_rating_for_movie(movie.id)
        user_review = Review.query.filter_by(user_id=current_user.id, movie_id=movie.id).first()

    similar = tmdb_service.get_similar_movies(tmdb_id)
    reviews = ReviewRepository.get_movie_reviews(movie.id, page=1, per_page=5)
    trailers = details.get('trailers', [])
    ott_providers = details.get('ott_providers', [])

    return render_template('movie_details.html',
        title=details.get('title'),
        movie=details, movie_db=movie,
        in_watchlist=in_watchlist,
        user_rating=user_rating,
        user_review=user_review,
        similar_movies=similar[:8],
        reviews=reviews.items,
        trailers=trailers,
        ott_providers=ott_providers,
    )


# ============================================================================
# USER PAGES
# ============================================================================

@bp.route('/recommendations')
@login_required
def recommendations():
    recommendation_engine.load_ratings_data()
    rec_data = recommendation_engine.hybrid_recommendations(current_user.id, 50)
    movies = []
    for rec in rec_data:
        md = tmdb_service.get_movie_details(rec['movie_id'])
        if md:
            md['recommendation_score'] = rec['score']
            movies.append(md)
    return render_template('recommendations.html', title='Your Recommendations', movies=movies)

@bp.route('/watchlist')
@login_required
def watchlist():
    wl_movies = current_user.watchlist
    enriched = []
    for movie in wl_movies:
        details = tmdb_service.get_movie_details(movie.tmdb_id)
        if details:
            enriched.append(details)
    return render_template('watchlist.html', title='My Watchlist', movies=enriched)

@bp.route('/profile/<username>')
def profile(username):
    try:
        user = UserRepository.get_by_username(username)
    except Exception:
        flash('User not found', 'error')
        return redirect(url_for('main.index'))
    stats = user.get_stats()
    recent_ratings = RatingRepository.get_user_ratings(user.id)[:10]
    recent_reviews = ReviewRepository.get_user_reviews(user.id, page=1, per_page=5)
    return render_template('profile.html', title=f"{username}'s Profile", user=user, stats=stats, recent_ratings=recent_ratings, recent_reviews=recent_reviews.items)

@bp.route('/genre/<int:genre_id>')
def genre(genre_id):
    page = request.args.get('page', 1, type=int)
    movies = tmdb_service.get_movies_by_genre(genre_id, page)
    genres = tmdb_service.get_genres()
    name = next((g['name'] for g in genres if g['id'] == genre_id), 'Unknown')
    return render_template('genre.html', title=f"{name} Movies", movies=movies, genre_name=name, genre_id=genre_id)

@bp.route('/my-lists')
@login_required
def my_lists():
    lists = ListRepository.get_user_lists(current_user.id)
    return render_template('my_lists.html', title='My Lists', lists=lists)

@bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html', title='Settings')

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
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    if len(query) < 2:
        return jsonify({'results': [], 'total_results': 0})
    results = tmdb_service.search_multi(query, page)
    return jsonify(results)

@bp.route('/api/watchlist/add', methods=['POST'])
@login_required
def api_add_to_watchlist():
    data = request.get_json()
    tmdb_id = data.get('tmdb_id')
    if not tmdb_id:
        return jsonify({'success': False, 'error': 'tmdb_id required'}), 400
    movie = MovieRepository.get_or_create_by_tmdb_id(tmdb_id)
    current_user.add_to_watchlist(movie)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Added to watchlist'})

@bp.route('/api/watchlist/remove', methods=['POST'])
@login_required
def api_remove_from_watchlist():
    data = request.get_json()
    tmdb_id = data.get('tmdb_id')
    if not tmdb_id:
        return jsonify({'success': False, 'error': 'tmdb_id required'}), 400
    try:
        movie = MovieRepository.get_by_tmdb_id(tmdb_id)
        current_user.remove_from_watchlist(movie)
        db.session.commit()
    except Exception:
        pass
    return jsonify({'success': True, 'message': 'Removed from watchlist'})

@bp.route('/api/rate', methods=['POST'])
@login_required
def api_rate_movie():
    data = request.get_json()
    tmdb_id = data.get('tmdb_id')
    rating = data.get('rating')
    if not tmdb_id or rating is None:
        return jsonify({'success': False, 'error': 'tmdb_id and rating required'}), 400
    movie = MovieRepository.get_or_create_by_tmdb_id(tmdb_id)
    current_user.rate_movie(movie, rating)
    db.session.commit()
    try:
        recommendation_engine.load_ratings_data()
    except Exception:
        pass
    return jsonify({'success': True, 'message': 'Rating saved', 'rating': rating})

@bp.route('/api/review', methods=['POST'])
@login_required
def api_submit_review():
    data = request.get_json()
    movie_id = data.get('movie_id')
    review = Review(
        user_id=current_user.id, movie_id=movie_id,
        title=data.get('title'), content=data.get('content'),
        rating=data.get('rating'), is_spoiler=data.get('is_spoiler', False)
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Review submitted', 'review_id': review.id})

@bp.route('/api/stats')
@login_required
def api_user_stats():
    return jsonify(current_user.get_stats())

@bp.route('/api/recommendations')
@login_required
def api_recommendations():
    n = request.args.get('n', 20, type=int)
    try:
        recommendation_engine.load_ratings_data()
        recs = recommendation_engine.hybrid_recommendations(current_user.id, n)
    except Exception:
        recs = []
    return jsonify({'recommendations': recs})

@bp.route('/api/health')
def api_health():
    return jsonify({
        'status': 'ok',
        'tmdb_api': tmdb_service.health_check(),
        'database': True
    })

# Legacy routes
@bp.route('/watchlist/add/<int:movie_id>')
@login_required
def add_to_watchlist(movie_id):
    movie = MovieRepository.get_by_id(movie_id)
    current_user.add_to_watchlist(movie)
    db.session.commit()
    flash(f'"{movie.title}" added to watchlist!', 'success')
    return redirect(url_for('main.movie_details', tmdb_id=movie.tmdb_id))

@bp.route('/watchlist/remove/<int:movie_id>')
@login_required
def remove_from_watchlist(movie_id):
    movie = MovieRepository.get_by_id(movie_id)
    current_user.remove_from_watchlist(movie)
    db.session.commit()
    flash(f'"{movie.title}" removed from watchlist.', 'info')
    return redirect(url_for('main.movie_details', tmdb_id=movie.tmdb_id))
