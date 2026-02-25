"""Custom exceptions for CineMate."""

class CineMateException(Exception):
    def __init__(self, message="An error occurred", status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class TMDbAPIException(CineMateException):
    def __init__(self, message="TMDB API error", status_code=500):
        super().__init__(message, status_code)

class ValidationException(CineMateException):
    def __init__(self, message="Validation failed", errors=None):
        self.errors = errors or {}
        super().__init__(message, 400)

class ResourceNotFoundException(CineMateException):
    def __init__(self, resource_name="Resource"):
        super().__init__(f"{resource_name} not found", 404)

class DatabaseException(CineMateException):
    def __init__(self, message="Database operation failed"):
        super().__init__(message, 500)
