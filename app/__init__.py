"""
CineMate Application Factory
Creates and configures the Flask application with all extensions and blueprints.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
login.login_message_category = 'info'


def create_app(config_class=Config):
    """
    Application factory function.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Register blueprints
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Use advanced routes if available, otherwise fallback to basic
    try:
        from app.routes.main_advanced import bp as main_bp
    except ImportError:
        from app.routes.main import bp as main_bp
    
    app.register_blueprint(main_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Context processor for global template variables
    @app.context_processor
    def inject_globals():
        """Inject global variables into all templates."""
        return {
            'app_name': 'CineMate',
            'app_version': '2.0.0'
        }

    # Shell context for flask shell command
    @app.shell_context_processor
    def make_shell_context():
        """Make database and models available in flask shell."""
        from app.models import User, Movie, Rating, Review, MovieList
        return {
            'db': db,
            'User': User,
            'Movie': Movie,
            'Rating': Rating,
            'Review': Review,
            'MovieList': MovieList
        }

    # Initialize ML recommendation engine on startup
    with app.app_context():
        try:
            from app.ml import recommendation_engine
            recommendation_engine.load_ratings_data()
            print("✅ Recommendation engine initialized")
        except Exception as e:
            print(f"⚠️  Could not initialize recommendation engine: {e}")

    print(f"🎬 CineMate application started successfully!")
    
    return app


# Import models for migration context
from app import models