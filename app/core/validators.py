"""
Validators for request data validation.
Provides reusable validation functions for common scenarios.
"""

import re
from typing import Dict, Any, Optional


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """Validate username (alphanumeric and underscores, 3-30 chars)."""
    pattern = r'^[a-zA-Z0-9_]{3,30}$'
    return bool(re.match(pattern, username))


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength.
    Returns dict with 'valid' boolean and 'issues' list.
    """
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        issues.append("Password must contain at least one digit")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues
    }


def validate_rating(rating: Any) -> bool:
    """Validate movie rating (0.5 to 5.0, increments of 0.5)."""
    try:
        rating = float(rating)
        return 0.5 <= rating <= 5.0 and (rating * 2) % 1 == 0
    except (ValueError, TypeError):
        return False


def validate_required_fields(data: Dict, required_fields: list) -> Optional[Dict]:
    """
    Validate that all required fields are present.
    Returns dict of missing fields or None if all present.
    """
    missing = []
    errors = {}
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing.append(field)
    
    if missing:
        errors['missing_fields'] = missing
        return errors
    
    return None


def validate_pagination_params(page: Any, per_page: Any) -> Dict[str, int]:
    """
    Validate and sanitize pagination parameters.
    Returns dict with valid page and per_page values.
    """
    try:
        page = int(page) if page else 1
        per_page = int(per_page) if per_page else 20
    except (ValueError, TypeError):
        page = 1
        per_page = 20
    
    # Ensure reasonable limits
    page = max(1, page)
    per_page = max(1, min(per_page, 100))  # Max 100 items per page
    
    return {'page': page, 'per_page': per_page}


class RequestValidator:
    """Base class for request validators."""
    
    @staticmethod
    def validate_registration(request) -> Optional[Dict]:
        """Validate user registration request."""
        data = request.form or request.get_json() or {}
        errors = {}
        
        # Check required fields
        required = validate_required_fields(data, ['username', 'email', 'password'])
        if required:
            errors.update(required)
            return errors
        
        # Validate username
        if not validate_username(data['username']):
            errors['username'] = "Username must be 3-30 alphanumeric characters"
        
        # Validate email
        if not validate_email(data['email']):
            errors['email'] = "Invalid email format"
        
        # Validate password
        password_check = validate_password_strength(data['password'])
        if not password_check['valid']:
            errors['password'] = password_check['issues']
        
        return errors if errors else None
    
    @staticmethod
    def validate_login(request) -> Optional[Dict]:
        """Validate user login request."""
        data = request.form or request.get_json() or {}
        errors = {}
        
        required = validate_required_fields(data, ['username', 'password'])
        if required:
            errors.update(required)
        
        return errors if errors else None
    
    @staticmethod
    def validate_rating(request) -> Optional[Dict]:
        """Validate movie rating request."""
        data = request.form or request.get_json() or {}
        errors = {}
        
        required = validate_required_fields(data, ['rating'])
        if required:
            errors.update(required)
            return errors
        
        if not validate_rating(data['rating']):
            errors['rating'] = "Rating must be between 0.5 and 5.0 in 0.5 increments"
        
        return errors if errors else None
