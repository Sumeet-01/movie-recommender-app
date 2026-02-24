from flask import Blueprint, render_template
from app.services.tmdb_api import tmdb_service
from flask_login import current_user, login_required
from app import db
from app.models import Movie



bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    trending_movies = tmdb_service.get_trending_movies()
    return render_template('index.html', title='Home', movies=trending_movies)


@bp.route('/movie/<int:tmdb_id>')
def movie_details(tmdb_id):
    # Fetch movie details from the TMDb API
    details = tmdb_service.get_movie_details(tmdb_id)
    if not details:
        flash('Movie not found!')
        return redirect(url_for('main.index'))

    # Check if the movie exists in our local DB, if not, add it
    movie = Movie.query.filter_by(tmdb_id=tmdb_id).first()
    if not movie:
        movie = Movie(tmdb_id=tmdb_id, title=details.get('title'), poster_path=details.get('poster_path'))
        db.session.add(movie)
        db.session.commit()

    # Check if the current user (if logged in) has this movie in their watchlist
    in_watchlist = False
    if current_user.is_authenticated:
        in_watchlist = current_user.is_in_watchlist(movie)

    return render_template('movie_details.html', title=details.get('title'), movie=details, movie_db=movie, in_watchlist=in_watchlist)

@bp.route('/watchlist/add/<int:movie_id>')
@login_required
def add_to_watchlist(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    current_user.add_to_watchlist(movie)
    db.session.commit()
    flash(f'"{movie.title}" has been added to your watchlist!')
    return redirect(url_for('main.movie_details', tmdb_id=movie.tmdb_id))

@bp.route('/watchlist/remove/<int:movie_id>')
@login_required
def remove_from_watchlist(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    current_user.remove_from_watchlist(movie)
    db.session.commit()
    flash(f'"{movie.title}" has been removed from your watchlist.')
    return redirect(url_for('main.movie_details', tmdb_id=movie.tmdb_id))