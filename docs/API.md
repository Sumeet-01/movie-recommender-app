# CineMate API Documentation

Complete API reference for CineMate's RESTful endpoints.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Most endpoints require authentication via Flask-Login session cookies.

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

### Register
```http
POST /auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

### Logout
```http
GET /auth/logout
```

## Movies

### Search Movies
```http
GET /api/search?q={query}&page={page}
```

**Parameters:**
- `q` (required): Search query
- `page` (optional): Page number (default: 1)

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [...],
    "page": 1,
    "total_pages": 10,
    "total_results": 200
  }
}
```

### Get Movie Details
```http
GET /api/movies/{tmdb_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 550,
    "title": "Fight Club",
    "overview": "...",
    "poster_path": "/...",
    "release_date": "1999-10-15",
    "runtime": 139,
    "genres": [...],
    "credits": {...},
    "videos": [...],
    "similar": [...]
  }
}
```

### Get Trending Movies
```http
GET /api/trending?time_window={window}
```

**Parameters:**
- `time_window` (optional): `day` or `week` (default: `week`)

### Get Popular Movies
```http
GET /api/popular?page={page}
```

### Get Top Rated Movies
```http
GET /api/top-rated?page={page}
```

### Discover Movies
```http
GET /api/discover?genre={genre}&year={year}&sort_by={sort}
```

**Parameters:**
- `genre` (optional): Genre ID
- `year` (optional): Release year
- `sort_by` (optional): Sort criterion

## Ratings

### Rate a Movie
```http
POST /api/rate
Content-Type: application/json

{
  "movie_id": 550,
  "score": 4.5
}
```

**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "movie_id": 550,
    "user_id": 1,
    "score": 4.5,
    "created_at": "2024-01-15T10:30:00Z"
  },
  "message": "Rating submitted successfully"
}
```

### Get User's Rating for a Movie
```http
GET /api/movies/{movie_id}/rating
```

**Authentication:** Required

### Update Rating
```http
PUT /api/ratings/{rating_id}
Content-Type: application/json

{
  "score": 5.0
}
```

### Delete Rating
```http
DELETE /api/ratings/{rating_id}
```

## Watchlist

### Add to Watchlist
```http
POST /api/watchlist/add
Content-Type: application/json

{
  "movie_id": 550
}
```

**Authentication:** Required

### Remove from Watchlist
```http
POST /api/watchlist/remove
Content-Type: application/json

{
  "movie_id": 550
}
```

### Get User's Watchlist
```http
GET /api/watchlist?page={page}
```

**Authentication:** Required

## Reviews

### Create Review
```http
POST /api/reviews
Content-Type: application/json

{
  "movie_id": 550,
  "title": "Amazing movie!",
  "content": "This is one of the best movies I've ever seen...",
  "rating": 5.0
}
```

**Authentication:** Required

### Get Movie Reviews
```http
GET /api/movies/{movie_id}/reviews?page={page}
```

### Get User's Reviews
```http
GET /api/users/{user_id}/reviews?page={page}
```

### Update Review
```http
PUT /api/reviews/{review_id}
Content-Type: application/json

{
  "title": "Updated title",
  "content": "Updated content",
  "rating": 4.5
}
```

### Delete Review
```http
DELETE /api/reviews/{review_id}
```

### Like/Unlike Review
```http
POST /api/reviews/{review_id}/like
DELETE /api/reviews/{review_id}/like
```

## Lists

### Create List
```http
POST /api/lists
Content-Type: application/json

{
  "name": "My Favorite Sci-Fi",
  "description": "Collection of best sci-fi movies",
  "is_public": true
}
```

**Authentication:** Required

### Get User's Lists
```http
GET /api/users/{user_id}/lists
```

### Get List Details
```http
GET /api/lists/{list_id}
```

### Add Movie to List
```http
POST /api/lists/{list_id}/movies
Content-Type: application/json

{
  "movie_id": 550
}
```

### Remove Movie from List
```http
DELETE /api/lists/{list_id}/movies/{movie_id}
```

### Update List
```http
PUT /api/lists/{list_id}
Content-Type: application/json

{
  "name": "Updated name",
  "description": "Updated description",
  "is_public": false
}
```

### Delete List
```http
DELETE /api/lists/{list_id}
```

## Recommendations

### Get Personalized Recommendations
```http
GET /api/recommendations?limit={limit}
```

**Authentication:** Required

**Parameters:**
- `limit` (optional): Number of recommendations (default: 20)

**Requirements:**
- User must have rated at least 5 movies

**Response:**
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "movie_id": 550,
        "score": 0.85,
        "movie": {...}
      }
    ],
    "total": 20
  }
}
```

### Get Similar Movies
```http
GET /api/movies/{movie_id}/similar?limit={limit}
```

## User

### Get User Profile
```http
GET /api/users/{user_id}
```

### Update Profile
```http
PUT /api/profile
Content-Type: application/json

{
  "bio": "Movie enthusiast",
  "location": "New York",
  "favorite_genres": [28, 12, 878]
}
```

**Authentication:** Required

### Get User Stats
```http
GET /api/users/{user_id}/stats
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_ratings": 150,
    "total_reviews": 25,
    "total_lists": 5,
    "watchlist_count": 30,
    "average_rating": 3.8,
    "favorite_genres": [...]
  }
}
```

### Get User Activity
```http
GET /api/users/{user_id}/activity?page={page}
```

## Genres

### Get All Genres
```http
GET /api/genres
```

**Response:**
```json
{
  "success": true,
  "data": [
    {"id": 28, "name": "Action"},
    {"id": 12, "name": "Adventure"},
    {"id": 16, "name": "Animation"}
  ]
}
```

## Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {...}
  }
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests (Rate Limited)
- `500` - Internal Server Error

## Rate Limiting

API endpoints are rate limited:
- Development: 100 requests/minute
- Production: 60 requests/minute

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1610000000
```

## Pagination

Paginated responses follow this format:

```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total_pages": 10,
      "total_items": 200,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

## Examples

### cURL

```bash
# Search for movies
curl "http://localhost:5000/api/search?q=inception"

# Rate a movie (requires auth cookie)
curl -X POST http://localhost:5000/api/rate \
  -H "Content-Type: application/json" \
  -d '{"movie_id": 550, "score": 4.5}' \
  --cookie "session=..."
```

### JavaScript (Fetch)

```javascript
// Search movies
const searchMovies = async (query) => {
  const response = await fetch(`/api/search?q=${query}`);
  const data = await response.json();
  return data;
};

// Rate movie
const rateMovie = async (movieId, score) => {
  const response = await fetch('/api/rate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ movie_id: movieId, score }),
    credentials: 'same-origin'
  });
  return await response.json();
};
```

### Python (requests)

```python
import requests

# Search movies
response = requests.get('http://localhost:5000/api/search', params={'q': 'inception'})
data = response.json()

# Rate movie (with session)
session = requests.Session()
session.post('http://localhost:5000/auth/login', json={
    'username': 'john_doe',
    'password': 'password123'
})

response = session.post('http://localhost:5000/api/rate', json={
    'movie_id': 550,
    'score': 4.5
})
```

---

**Last Updated:** December 2024
