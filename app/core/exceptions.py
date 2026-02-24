"""
Custom exceptions for the CineMate application.
Provides granular error handling and better debugging.
"""

class CineMateException(Exception):
    """Base exception for all CineMate errors."""
    def __init__(self, message="An error occurred", status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class APIException(CineMateException):
    """Exception for API-related errors."""
    def __init__(self, message="API request failed", status_code=500):
        super().__init__(message, status_code)


class TMDbAPIException(APIException):
    """Specific exception for TMDB API errors."""
    def __init__(self, message="TMDB API error", status_code=500):
        super().__init__(message, status_code)


class ValidationException(CineMateException):
    """Exception for validation errors."""
    def __init__(self, message="Validation failed", errors=None):
        self.errors = errors or {}
        super().__init__(message, 400)


class ResourceNotFoundException(CineMateException):
    """Exception when a requested resource is not found."""
    def __init__(self, resource_name="Resource"):
        message = f"{resource_name} not found"
        super().__init__(message, 404)


class DuplicateResourceException(CineMateException):
    """Exception when trying to create a duplicate resource."""
    def __init__(self, resource_name="Resource"):
        message = f"{resource_name} already exists"
        super().__init__(message, 409)


class AuthenticationException(CineMateException):
    """Exception for authentication failures."""
    def __init__(self, message="Authentication required"):
        super().__init__(message, 401)


class AuthorizationException(CineMateException):
    """Exception for authorization failures."""
    def __init__(self, message="Insufficient permissions"):
        super().__init__(message, 403)


class CacheException(CineMateException):
    """Exception for cache-related errors."""
    def __init__(self, message="Cache operation failed"):
        super().__init__(message, 500)


class DatabaseException(CineMateException):
    """Exception for database-related errors."""
    def __init__(self, message="Database operation failed"):
        super().__init__(message, 500)
