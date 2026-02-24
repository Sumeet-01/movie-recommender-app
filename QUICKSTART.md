# CineMate - Quick Start Guide

Get up and running with CineMate in under 5 minutes! 🚀

## Prerequisites

- Python 3.8 or higher
- TMDB API Key ([Get one here](https://www.themoviedb.org/settings/api))
- Git (optional)

## Quick Setup

### 1. Clone or Download

```bash
git clone https://github.com/yourusername/cinemate.git
cd cinemate
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
FLASK_APP=run.py
FLASK_ENV=development
TMDB_API_KEY=your-tmdb-api-key-here
```

> 💡 **Tip:** Copy `.env.example` and fill in your values

### 5. Initialize Database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. (Optional) Seed Sample Data

```bash
python scripts/seed_database.py
```

This creates:
- 5 sample users (password: `password123`)
- 50 popular movies from TMDB
- Sample ratings, reviews, and watchlists

### 7. Run the Application

```bash
python run.py
```

or

```bash
flask run
```

### 8. Open in Browser

Navigate to: **http://localhost:5000**

## First Steps

### Create an Account

1. Click **Register** in the navigation bar
2. Fill in your details
3. Click **Sign Up**

### Explore Movies

- **Home**: View trending and popular movies
- **Discover**: Advanced filtering by genre, year, rating
- **Trending**: What's hot this week
- **Search**: Find specific movies (use search bar)

### Rate Movies

1. Click on any movie
2. Use the star rating system
3. Optionally write a review

### Get Recommendations

After rating 5+ movies:
1. Visit the **Recommendations** page
2. Get personalized suggestions based on your taste

### Create Lists

1. Go to **My Lists**
2. Click **Create New List**
3. Add movies to your custom collection

## Sample Users (if seeded)

| Username | Email | Password |
|----------|-------|----------|
| john_doe | john@example.com | password123 |
| jane_smith | jane@example.com | password123 |
| movie_buff | buff@example.com | password123 |

## Common Issues

### ImportError or Module Not Found

Make sure your virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### TMDB API Errors

Check that your `TMDB_API_KEY` in `.env` is correct:
1. Visit https://www.themoviedb.org/settings/api
2. Copy your API Key (v3 auth)
3. Update `.env` file

### Database Errors

Reset the database:
```bash
flask db downgrade
flask db upgrade
```

Or delete `instance/cinemate.db` and run migrations again.

## Development Features

### Enable Debug Mode

In `.env`:
```env
FLASK_ENV=development
```

### View Database

```bash
flask shell
```

```python
from app.models.user import User
from app.models.movie import Movie

# View all users
User.query.all()

# View all movies
Movie.query.all()
```

### Clear Cache

Restart the Flask application to clear the in-memory cache.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [ARCHITECTURE.md](docs/ARCHITECTURE.md) to understand the system design
- See [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute
- Explore the API endpoints at `/api/docs` (coming soon)

## Docker Quick Start (Alternative)

If you prefer using Docker:

```bash
# Build and run
docker-compose up --build

# Access at http://localhost
```

## Need Help?

- 📖 Read the [full documentation](README.md)
- 🐛 [Report issues](https://github.com/yourusername/cinemate/issues)
- 💬 [Join discussions](https://github.com/yourusername/cinemate/discussions)

---

**Happy movie browsing! 🎬🍿**
