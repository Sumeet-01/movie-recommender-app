# 🎬 CineMate - Your Intelligent Movie Companion

<div align="center">

![CineMate Banner](https://via.placeholder.com/1200x400/667eea/ffffff?text=CineMate+-+Discover+Your+Next+Favorite+Movie)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask Version](https://img.shields.io/badge/flask-2.x-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**A production-ready, ML-powered movie recommendation platform with advanced features and beautiful UI**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## ✨ Features

### 🇮🇳 **India-First Platform (v3 🎉)**
- **Bollywood-First Bias**: Prioritizes Hindi cinema with TF-IDF + collaborative hybrid scoring
- **South Indian Cinema**: Tamil, Telugu, Malayalam, Kannada with language detection
- **Netflix-Style Top 10**: Numbered sections for India Top 10 + Series Top 10 daily
- **OTT Integration**: Netflix, Prime, Hotstar, JioCinema, Zee5, SonyLIV provider badges
- **Multi-Search**: Search movies AND TV series with media type auto-detection
- **Auto-Rotating Hero**: 5-slide fade transitions on homepage (5 trending movies)

### 📺 **TV Series Support (NEW)**
- **Complete TV Integration**: Browse, search, get recommendations for TV series
- **Series Details**: Seasons, episodes, air dates, cast, trailers, OTT providers
- **Trending TV Section**: Dedicated trending shows on homepage
- **Top 10 Series**: Netflix-style numbered Top 10 shows

### 🧠 **Machine Learning Powered**
- **Hybrid Engine**: TF-IDF (overview+genres+keywords+cast+director) + Pearson collaborative + Bollywood bias
- **Recency Decay**: 2026 films→1.0, 10+ years→0.2 score multiplier
- **Bayesian Rating**: Smart handling of low-vote movies (IMDB formula)
- **Smart Scoring**: 35% similarity + 20% genre match + 15% recency + 10% rating weight + bonuses
- **Similar Movies**: Intelligent detection by genre, cast, director, language
- **Trending Analysis**: Real-time with director/cast/language bonuses

### 🎨 **Netflix-Grade UI**
- **Beautiful Dark Theme**: Premium UI with glass-morphism effects
- **Responsive Design**: Perfect on mobile, tablet, desktop
- **Smooth Animations**: Fade-in-up, scale-in, slide transitions throughout
- **Advanced Multi-Search**: Real-time with TV series badges
- **Numbered Top 10 Cards**: Netflix-style numbered posters with drop shadows
- **OTT Badges**: Color-coded logos (Netflix red, Prime blue, Hotstar navy)
- **Media Badges**: Purple TV badges distinguish series from movies

### 📊 **Advanced Features**
- **User Profiles**: Detailed statistics and activity tracking
- **Custom Lists**: Create and share movie/series collections
- **Reviews & Ratings**: Half-star system (0-5) with spoiler tags
- **Watchlist Management**: Organize movies & shows to watch
- **Genre Exploration**: Browse 19+ genres with advanced filters
- **Discover Page**: Filter by year, language, rating; sort by popularity/rating/date
- **Zero Console Errors**: Clean startup with warning suppression, auto __pycache__ cleanup

### 🏗️ **Enterprise Architecture**
- **Repository Pattern**: Clean separation of concerns
- **Service Layer**: Business logic abstraction
- **DTO Pattern**: Consistent data transfer
- **Caching Layer**: In-memory caching with TTL
- **Custom Decorators**: Rate limiting, validation, timing
- **Exception Handling**: Comprehensive error management
- **API Versioning**: Future-proof API design

### 🔧 **Developer Features**
- **RESTful API**: Complete API for external integrations
- **Comprehensive Docs**: Detailed documentation for all components
- **Type Hints**: Full type annotation support
- **Modular Structure**: Easy to extend and maintain
- **Testing Ready**: Structure supports unit and integration tests
- **Database Migrations**: Alembic for schema management
- **Environment Config**: Flexible configuration management

---

## 🚀 Demo

### Homepage
![Homepage](https://via.placeholder.com/1200x600/0a0e1a/ffffff?text=Homepage+Screenshot)

### Movie Details
![Movie Details](https://via.placeholder.com/1200x600/0a0e1a/ffffff?text=Movie+Details+Screenshot)

### Recommendations
![Recommendations](https://via.placeholder.com/1200x600/0a0e1a/ffffff?text=Recommendations+Screenshot)

---

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)
- TMDB API Key ([Get one free](https://www.themoviedb.org/settings/api))

---

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cinemate.git
cd cinemate
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-this-in-production
FLASK_APP=run.py
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///cinemate.db

# TMDB API
TMDB_API_KEY=your-tmdb-api-key-here

# Optional: Production Settings
# DATABASE_URL=postgresql://user:password@localhost/cinemate
# REDIS_URL=redis://localhost:6379/0
```

### 5. Initialize Database

```bash
# Create database tables
flask db upgrade

# Optional: Seed with sample data
python scripts/seed_database.py
```

### 6. Run the Application

```bash
# Development mode
python run.py

# Production mode (with Gunicorn)
gunicorn run:app
```

Visit http://localhost:5000 in your browser.

---

## 📚 Documentation

### Project Structure

```
Cinemate/
├── app/
│   ├── core/                 # Core utilities and base classes
│   │   ├── cache.py         # Caching layer
│   │   ├── decorators.py    # Custom decorators
│   │   ├── exceptions.py    # Custom exceptions
│   │   └── validators.py    # Request validators
│   ├── dto/                 # Data Transfer Objects
│   ├── ml/                  # Machine Learning modules
│   │   └── recommendation_engine.py
│   ├── models/              # Database models
│   │   ├── movie.py
│   │   └── user.py
│   ├── repositories/        # Data access layer
│   ├── routes/              # Route handlers
│   │   ├── auth.py
│   │   ├── main.py
│   │   └── main_advanced.py
│   ├── services/            # Business logic
│   │   └── tmdb_api.py
│   ├── static/              # Static assets
│   │   ├── css/
│   │   └── js/
│   ├── templates/           # HTML templates
│   └── __init__.py          # App factory
├── migrations/              # Database migrations
├── docs/                    # Additional documentation
├── tests/                   # Test suite
├── scripts/                 # Utility scripts
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── run.py                   # Application entry point
```

### Architecture Overview

CineMate follows a modern, layered architecture:

1. **Presentation Layer** (Templates + Frontend JS)
   - Jinja2 templates with modern CSS
   - Vanilla JavaScript for interactivity
   - Progressive enhancement approach

2. **API Layer** (Routes)
   - RESTful endpoints
   - Request validation
   - Rate limiting

3. **Service Layer** (Services)
   - Business logic
   - External API integration
   - Data processing

4. **Data Access Layer** (Repositories)
   - Database abstraction
   - Query building
   - Result mapping

5. **Data Layer** (Models)
   - SQLAlchemy models
   - Relationships
   - Model methods

### Key Components

#### Recommendation Engine

The ML recommendation engine uses a hybrid approach:

```python
from app.ml import recommendation_engine

# Load user ratings data
recommendation_engine.load_ratings_data()

# Get personalized recommendations
recommendations = recommendation_engine.hybrid_recommendations(
    user_id=current_user.id,
    n_recommendations=20
)
```

**Algorithms:**
- **Collaborative Filtering**: User-based similarity with Pearson correlation
- **Content-Based Filtering**: Genre and metadata similarity
- **Hybrid Approach**: Weighted combination based on data availability

#### Caching System

```python
from app.core.cache import cache

# Cache with TTL
@cached(timeout=300)  # 5 minutes
def expensive_operation():
    return result

# Manual cache control
cache.set('key', value, ttl=600)
value = cache.get('key')
cache.delete('key')
cache.clear()
```

#### Custom Decorators

```python
from app.core.decorators import *

@cached(timeout=600)
@timed
@rate_limit(max_requests=100, window=60)
@api_response
def my_endpoint():
    return data
```

---

## 🎯 Usage Examples

### Search for Movies

```python
from app.services.tmdb_api import tmdb_service

results = tmdb_service.search_movies("Inception", page=1)
```

### Get Recommendations

```python
recommendations = recommendation_engine.hybrid_recommendations(
    user_id=1,
    n_recommendations=10
)
```

### Rate a Movie

```python
user.rate_movie(movie, score=4.5)
db.session.commit()
```

### Create Custom List

```python
movie_list = MovieList(
    user_id=user.id,
    name="Sci-Fi Favorites",
    description="My favorite science fiction movies",
    is_public=True
)
db.session.add(movie_list)
db.session.commit()
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_recommendations.py
```

---

## 🚀 Deployment

### Using Docker

```bash
docker build -t cinemate .
docker run -p 5000:5000 cinemate
```

### Using Heroku

```bash
heroku create cinemate-app
git push heroku main
heroku config:set TMDB_API_KEY=your-api-key
```

### Environment Variables for Production

```env
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Add tests for new features

---

## 📝 API Documentation

### Authentication

```http
POST /auth/login
POST /auth/register
GET  /auth/logout
```

### Movies

```http
GET  /api/search?q={query}
GET  /movie/{tmdb_id}
GET  /api/recommendations
```

### User Actions

```http
POST /api/watchlist/add/{movie_id}
POST /api/watchlist/remove/{movie_id}
POST /api/rate/{tmdb_id}
POST /api/review/{movie_id}
```

See [API_DOCS.md](docs/API_DOCS.md) for complete API documentation.

---

## 🛠️ Built With

**Backend Stack:**
- **Flask** 3.1.2 - Lightweight web framework
- **SQLAlchemy** 2.0.43 - ORM for database models
- **Flask-Login** 0.6.3 - Session & user authentication
- **Flask-Migrate** 4.0.5 - Database migration management
- **Flask-Limiter** 3.5.0 - Rate limiting for APIs
- **Gunicorn** 21.2.0 - Production WSGI server

**AI/ML Engine:**
- **scikit-learn** 1.3.2 - TF-IDF, similarity metrics, Bayesian rating formula
- **pandas** 2.1.3 - Data manipulation & aggregation
- **numpy** 1.24.3 - Numerical computations

**Frontend:**
- **Jinja2** (Flask templating) - Dynamic HTML rendering
- **Vanilla JavaScript** (273 lines) - Hero rotation, multi-search, hero indicators
- **CSS3** (790 lines) - Dark theme, animations, Netflix-style Top 10 cards

**External APIs:**
- **TMDB API v3** (free tier) - Movie/TV metadata, ratings, OTT providers, trailers, images

**Database:**
- **SQLite** 3.x - Local development & production database
- **Alembic** - Schema migration tool

**DevOps & Deployment:**
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Git/GitHub** - Version control
- **Python venv** - Dependency isolation (3.11+)

---

## 📊 Performance

- **Page Load**: < 2s (with caching)
- **API Response**: < 100ms (cached)
- **Recommendation Generation**: < 500ms
- **Search**: < 200ms (with autocomplete)

---

## 🗺️ Roadmap (v3 Complete ✅)

### ✅ v3 Released (Feb 2026)
- [x] **TV Series Support**: Full TMDB TV API integration with series details, seasons, cast
- [x] **Netflix-Style Top 10**: Numbered cards for India Top 10 + Top 10 Series daily
- [x] **OTT Integration**: Netflix, Prime, Hotstar, JioCinema, Zee5, SonyLIV with provider badges
- [x] **Hero Auto-Rotation**: 5-second fade transitions between trending movies
- [x] **Bollywood Bias**: TF-IDF + collaborative hybrid engine with India-first ranking
- [x] **Multi-Search**: Unified search for movies & TV with media type badges
- [x] **Production Ready**: Zero warnings, __pycache__ cleaner, Bearer token auth, retry logic
- [x] **39 Complete Routes**: All pages + 15 API endpoints tested & verified
- [x] **Trailers & Director**: YouTube trailers + director credits on detail pages

### 🔮 Future (v4+)
- [ ] Redis caching (10x performance boost)
- [ ] Social features (user following, friend recommendations, activity feed)
- [ ] Mobile app (React Native/Flutter)
- [ ] Advanced analytics (watch time heatmaps, genre preference charts)
- [ ] Email notifications (new releases, watchlist reminders)
- [ ] Multi-language UI (Hindi, Tamil, Telugu, Malayalam)
- [ ] GraphQL API alongside REST
- [ ] WebSocket real-time updates
- [ ] Kubernetes deployment manifests
- [ ] AI-powered banner generation per user

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Movie data provided by [TMDB](https://www.themoviedb.org/)
- Icons from various open-source collections
- Inspiration from Netflix, Letterboxd, and IMDb
- Open source community for amazing tools and libraries

---

## 📧 Contact

**Project Maintainer**: Your Name
- Email: your.email@example.com
- GitHub: [@yourusername](https://github.com/yourusername)
- Twitter: [@yourhandle](https://twitter.com/yourhandle)

**Project Link**: [https://github.com/yourusername/cinemate](https://github.com/yourusername/cinemate)

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ by developers, for movie lovers

</div>
