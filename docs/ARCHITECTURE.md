# CineMate Architecture Documentation

## 🏗️ System Architecture

CineMate follows a **layered architecture** with clear separation of concerns, making it maintainable, testable, and scalable.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Templates  │  │     CSS      │  │  JavaScript  │  │
│  │   (Jinja2)   │  │   (Modern)   │  │  (Vanilla)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                      API Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    Routes    │  │  Decorators  │  │  Validators  │  │
│  │ Rate Limit   │  │   Caching    │  │   Auth       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    Service Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  TMDB API    │  │  ML Engine   │  │  Analytics   │  │
│  │   Service    │  │    Service   │  │   Service    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                     Data Access Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Repositories │  │     DTOs     │  │    Cache     │  │
│  │   Pattern    │  │   Mappers    │  │    Layer     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                      Data Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  SQLAlchemy  │  │   Models     │  │  Migrations  │  │
│  │   Database   │  │ Relationships│  │   (Alembic)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘

External APIs: TMDB API
```

## 📦 Layer Responsibilities

### 1. Presentation Layer
**Purpose**: User interface and client-side logic

**Components**:
- **Templates**: Jinja2 HTML templates with inheritance
- **CSS**: Modern, responsive styles with CSS variables
- **JavaScript**: Interactive features (search, rating, modals)

**Principles**:
- Progressive enhancement
- Mobile-first responsive design
- Accessibility (ARIA labels, keyboard navigation)
- Performance (lazy loading, code splitting)

### 2. API Layer
**Purpose**: HTTP request handling and routing

**Components**:
- **Routes**: URL endpoint definitions
- **Decorators**: Cross-cutting concerns (auth, rate limiting, caching)
- **Validators**: Request data validation
- **Error Handlers**: Centralized error handling

**Patterns Used**:
- Blueprint pattern for modular routes
- Decorator pattern for cross-cutting concerns
- Middleware pattern for request/response processing

### 3. Service Layer
**Purpose**: Business logic and external integrations

**Components**:
- **TMDB Service**: External API integration
- **Recommendation Engine**: ML-based recommendations
- **Analytics Service**: User statistics and insights

**Principles**:
- Single Responsibility Principle
- Dependency Injection
- Error handling and logging
- Caching strategy

### 4. Data Access Layer
**Purpose**: Database operations abstraction

**Components**:
- **Repositories**: CRUD operations and queries
- **DTOs**: Data transfer between layers
- **Cache**: In-memory caching layer

**Patterns Used**:
- Repository Pattern for data access
- DTO Pattern for data transfer
- Factory Pattern for object creation

### 5. Data Layer
**Purpose**: Data persistence and modeling

**Components**:
- **Models**: SQLAlchemy ORM models
- **Relationships**: Database relationships
- **Migrations**: Schema versioning with Alembic

**Principles**:
- ORM best practices
- Relationship management
- Index optimization
- Data integrity constraints

## 🔄 Request Flow

### Example: User rates a movie

```
1. User clicks rating stars
   │
   ▼
2. JavaScript sends POST /api/rate/{movie_id}
   │
   ▼
3. Route handler (with decorators)
   ├── @login_required (authentication)
   ├── @rate_limit (rate limiting)
   └── @api_response (response formatting)
   │
   ▼
4. Validator checks request data
   │
   ▼
5. Service layer processes business logic
   ├── Get/create movie from repository
   ├── Update user rating
   └── Trigger ML engine update
   │
   ▼
6. Repository saves to database
   │
   ▼
7. Cache updated (if applicable)
   │
   ▼
8. Response sent to client
   │
   ▼
9. JavaScript updates UI
```

## 🧠 Machine Learning Architecture

### Recommendation Engine

**Components**:
1. **Collaborative Filtering**
   - User-based similarity
   - Pearson correlation coefficient
   - Top-K similar users

2. **Content-Based Filtering**
   - Genre similarity (Jaccard index)
   - Metadata features
   - User preference profiling

3. **Hybrid Approach**
   - Weighted combination
   - Adaptive weighting based on data availability
   - Cold-start handling

**Data Flow**:
```
User Ratings → Similarity Matrix → Predictions → Recommendations
                      ↓
Movie Features → Content Profile → Similar Movies
```

### Algorithm Selection

| Scenario | Algorithm | Reason |
|----------|-----------|--------|
| New User | Content-based | No rating history |
| Active User | Hybrid | Best accuracy |
| Similar Movies | Content-based | Genre/metadata match |
| Trending | Popularity-based | Current trends |

## 🗄️ Database Schema

### Core Tables

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256),
    bio TEXT,
    created_at DATETIME,
    last_seen DATETIME
);

-- Movies table
CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    tmdb_id INTEGER UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    overview TEXT,
    poster_path VARCHAR(255),
    release_date VARCHAR(50),
    vote_average FLOAT,
    popularity FLOAT,
    created_at DATETIME
);

-- Ratings table
CREATE TABLE ratings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    score FLOAT NOT NULL,
    timestamp DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (movie_id) REFERENCES movies(id),
    UNIQUE (user_id, movie_id)
);

-- Reviews table
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    title VARCHAR(200),
    content TEXT NOT NULL,
    rating FLOAT,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (movie_id) REFERENCES movies(id)
);

-- Movie Lists table
CREATE TABLE movie_lists (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    is_public BOOLEAN,
    created_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Watchlist (Many-to-Many)
CREATE TABLE watchlist (
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    added_at DATETIME,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (movie_id) REFERENCES movies(id)
);
```

### Relationships

```
User ←──→ Movies (watchlist, many-to-many)
User ──→ Ratings (one-to-many)
User ──→ Reviews (one-to-many)
User ──→ MovieLists (one-to-many)
Movie ←── Ratings (one-to-many)
Movie ←── Reviews (one-to-many)
MovieList ←──→ Movies (many-to-many)
```

## 🔌 API Design

### REST Principles

- **Resource-based URLs**: `/api/movies/{id}`
- **HTTP Methods**: GET, POST, PUT, DELETE
- **Status Codes**: 200, 201, 400, 401, 404, 500
- **JSON Responses**: Consistent format

### Response Format

```json
{
    "success": true,
    "data": {...},
    "message": "Optional message",
    "meta": {
        "pagination": {...},
        "timestamp": "2024-01-01T00:00:00Z"
    }
}
```

### Error Format

```json
{
    "success": false,
    "error": {
        "type": "ValidationError",
        "message": "Invalid rating value",
        "details": {...}
    }
}
```

## 🚀 Performance Optimization

### Caching Strategy

**Layers**:
1. **Application Cache**: In-memory (development)
2. **Redis Cache**: Distributed (production)
3. **HTTP Cache**: Browser caching
4. **CDN**: Static assets

**Cache Keys**:
```
trending:week:page:1
movie:details:12345
user:stats:1
recommendations:1
```

**TTL Strategy**:
- Movie details: 2 hours (7200s)
- Trending: 1 hour (3600s)
- Search: 30 minutes (1800s)
- User stats: 5 minutes (300s)

### Database Optimization

**Indexes**:
```sql
CREATE INDEX idx_movies_tmdb_id ON movies(tmdb_id);
CREATE INDEX idx_ratings_user ON ratings(user_id);
CREATE INDEX idx_ratings_movie ON ratings(movie_id);
CREATE INDEX idx_reviews_movie ON reviews(movie_id);
```

**Query Optimization**:
- Use select_related for foreign keys
- Use prefetch_related for many-to-many
- Limit result sets
- Pagination everywhere

## 🔒 Security

### Authentication & Authorization

- **Flask-Login**: Session-based authentication
- **Password Hashing**: Werkzeug PBKDF2
- **CSRF Protection**: Flask built-in
- **Rate Limiting**: Custom decorator

### Input Validation

- **Server-side validation**: Always validated
- **Client-side validation**: UX improvement
- **SQL Injection**: ORM prevents
- **XSS Protection**: Template auto-escaping

### API Security

- **Rate Limiting**: 100 requests/minute
- **Authentication Required**: For user actions
- **Input Sanitization**: All inputs cleaned
- **Error Messages**: No sensitive data leak

## 🧪 Testing Strategy

### Test Pyramid

```
         /\
        /  \  E2E Tests (Few)
       /----\
      /      \  Integration Tests (Some)
     /--------\
    /          \  Unit Tests (Many)
   /____________\
```

### Test Categories

1. **Unit Tests**
   - Models
   - Services
   - Repositories
   - Utilities

2. **Integration Tests**
   - API endpoints
   - Database operations
   - External API calls

3. **End-to-End Tests**
   - User workflows
   - Critical paths

## 📊 Monitoring & Logging

### Metrics to Track

- Request count/rate
- Response times
- Error rates
- Cache hit/miss rates
- Database query times
- ML engine performance

### Logging Strategy

```python
# Request logging
@app.before_request
def log_request():
    logger.info(f"{request.method} {request.path}")

# Error logging
@app.errorhandler(Exception)
def log_error(error):
    logger.error(f"Error: {str(error)}")
```

## 🔮 Future Enhancements

### Scalability

- **Redis**: Distributed caching
- **Celery**: Background tasks
- **PostgreSQL**: Production database
- **Nginx**: Reverse proxy and load balancing
- **Docker**: Containerization
- **Kubernetes**: Orchestration

### Features

- **Real-time**: WebSockets for live updates
- **Social**: Following, activity feeds
- **Mobile**: Native app development
- **Analytics**: Advanced user insights
- **AI**: GPT-powered reviews analysis

## 📚 References

- [Flask Best Practices](https://flask.palletsprojects.com/patterns/)
- [SQLAlchemy Patterns](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)
- [Recommendation Systems](https://en.wikipedia.org/wiki/Recommender_system)
- [REST API Design](https://restfulapi.net/)
- [Software Architecture Patterns](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/)
