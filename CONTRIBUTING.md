# Contributing to CineMate

First off, thank you for considering contributing to CineMate! It's people like you that make CineMate such a great tool.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Guidelines](#development-guidelines)
- [Pull Request Process](#pull-request-process)
- [Style Guides](#style-guides)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

## 🚀 Getting Started

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/cinemate.git
   cd cinemate
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

5. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your TMDB API key and other settings
   ```

6. **Initialize the database**:
   ```bash
   flask db upgrade
   ```

7. **Run tests** to make sure everything works:
   ```bash
   pytest
   ```

## 🤔 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if applicable**
- **Include your environment details** (OS, Python version, browser, etc.)

**Bug Report Template:**
```markdown
**Description:**
A clear description of the bug.

**To Reproduce:**
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior:**
What you expected to happen.

**Screenshots:**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Windows 10, macOS 12]
- Python Version: [e.g., 3.9.7]
- Browser: [e.g., Chrome 95]
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:

- **Clear and descriptive title**
- **Detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any alternative solutions** you've considered

### Pull Requests

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes** following our [style guides](#style-guides)

3. **Add tests** for your changes

4. **Ensure all tests pass**:
   ```bash
   pytest
   ```

5. **Commit your changes**:
   ```bash
   git commit -m "Add amazing feature"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request** on GitHub

## 💻 Development Guidelines

### Project Structure

```
app/
├── core/           # Core utilities (cache, decorators, exceptions)
├── dto/            # Data Transfer Objects
├── ml/             # Machine Learning modules
├── models/         # Database models
├── repositories/   # Data access layer
├── routes/         # Route handlers
├── services/       # Business logic
├── static/         # Frontend assets
└── templates/      # HTML templates
```

### Architecture Principles

1. **Separation of Concerns**: Keep business logic separate from routes
2. **Repository Pattern**: Use repositories for database access
3. **DTOs**: Use DTOs for data transfer between layers
4. **Dependency Injection**: Favor composition over inheritance
5. **Single Responsibility**: Each module should do one thing well

### Adding New Features

#### 1. Backend Feature

```python
# app/services/your_service.py
class YourService:
    """Service description."""
    
    def your_method(self, param: str) -> dict:
        """
        Method description.
        
        Args:
            param: Parameter description
            
        Returns:
            Result description
        """
        # Implementation
        pass

# app/routes/your_routes.py
@bp.route('/your-endpoint')
@login_required
def your_endpoint():
    """Endpoint description."""
    result = your_service.your_method(param)
    return render_template('your_template.html', data=result)
```

#### 2. Frontend Feature

```html
<!-- app/templates/your_template.html -->
{% extends "base.html" %}

{% block content %}
<div class="container">
    <!-- Your content -->
</div>
{% endblock %}

{% block extra_js %}
<script>
// Your JavaScript
</script>
{% endblock %}
```

### Testing

#### Writing Tests

```python
# tests/test_your_feature.py
import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_your_feature(app):
    """Test description."""
    with app.test_client() as client:
        response = client.get('/your-endpoint')
        assert response.status_code == 200
```

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_your_feature.py

# Run tests matching pattern
pytest -k "test_user"
```

## 🔄 Pull Request Process

1. **Update Documentation**: Update README.md with details of changes if needed
2. **Update Tests**: Add or update tests for your changes
3. **Update Changelog**: Add your changes to CHANGELOG.md (if exists)
4. **Follow Style Guide**: Ensure code follows our style guidelines
5. **Rebase if needed**: Rebase your branch on main if there are conflicts
6. **Request Review**: Request review from maintainers

### Pull Request Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated existing tests

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed my code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Added tests that prove fix/feature works
```

## 📝 Style Guides

### Python Style Guide

Follow **PEP 8** with these specifics:

```python
# Imports
import standard_library
import third_party
from app import local_modules

# Type hints
def function_name(param: str, optional: int = 0) -> dict:
    """
    Function description.
    
    Args:
        param: Parameter description
        optional: Optional parameter description
        
    Returns:
        Return value description
    """
    result: dict = {}
    return result

# Constants
MAX_ITEMS = 100
DEFAULT_TIMEOUT = 30

# Class names (PascalCase)
class UserService:
    pass

# Function names (snake_case)
def get_user_data():
    pass

# Variable names (snake_case)
user_count = 0
```

### JavaScript Style Guide

```javascript
// Use modern ES6+ syntax
const apiCall = async (url) => {
    const response = await fetch(url);
    return response.json();
};

// Use descriptive names
const movieCards = document.querySelectorAll('.movie-card');

// Add comments for complex logic
// Calculate recommendation score using collaborative filtering
const score = calculateScore(user, movie);
```

### CSS Style Guide

```css
/* Use CSS variables */
:root {
    --primary-color: #667eea;
    --spacing-md: 1rem;
}

/* BEM naming convention */
.movie-card { }
.movie-card__title { }
.movie-card--featured { }

/* Mobile-first approach */
.container {
    padding: 1rem;
}

@media (min-width: 768px) {
    .container {
        padding: 2rem;
    }
}
```

### Commit Message Guidelines

Follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(recommendations): add collaborative filtering algorithm

Implemented user-based collaborative filtering using Pearson correlation
to improve recommendation accuracy.

Closes #123
```

```
fix(auth): resolve login redirect issue

Users were not being redirected to the correct page after login.
Fixed by updating the redirect logic in auth routes.
```

## 🎯 Areas for Contribution

### High Priority
- [ ] Implement Redis caching
- [ ] Add comprehensive test coverage
- [ ] Improve recommendation algorithm
- [ ] Add TV shows support
- [ ] Performance optimizations

### Medium Priority
- [ ] Add more social features
- [ ] Improve mobile responsiveness
- [ ] Add email notifications
- [ ] Implement GraphQL API
- [ ] Add i18n support

### Good First Issues
- [ ] Fix typos in documentation
- [ ] Add missing docstrings
- [ ] Improve error messages
- [ ] Add loading indicators
- [ ] Enhance UI animations

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/14/tutorial/)
- [TMDB API Docs](https://developers.themoviedb.org/3)
- [Collaborative Filtering](https://en.wikipedia.org/wiki/Collaborative_filtering)

## 💬 Questions?

Feel free to ask questions by:
- Opening an issue with the "question" label
- Joining our Discord server (if available)
- Emailing the maintainers

## 🙏 Thank You!

Your contributions make CineMate better for everyone. We appreciate your time and effort!

---

**Happy Coding! 🎬**
