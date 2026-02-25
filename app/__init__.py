"""
CineMate Application Factory
Auto-initializes database, registers all blueprints, and starts ML engine.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
login.login_message_category = 'info'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance folder exists for SQLite
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Register blueprints
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.main_advanced import bp as main_bp
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

    # Global template variables
    @app.context_processor
    def inject_globals():
        return {'app_name': 'CineMate', 'app_version': '3.0.0'}

    # Auto-create database tables on startup
    with app.app_context():
        # Import all models so SQLAlchemy knows about them
        from app.models import user, movie  # noqa
        db.create_all()
        print("  Database tables ready")

        # Initialize ML engine (non-fatal if it fails)
        try:
            from app.ml import recommendation_engine
            recommendation_engine.load_ratings_data()
            print("  ML recommendation engine loaded")
        except Exception as e:
            print(f"  ML engine skipped (will work after first ratings): {e}")

    print("  CineMate application initialized!")
    return app


from app import models  # noqa
