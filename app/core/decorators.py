"""
Custom decorators for CineMate application.
Provides caching, timing, validation, and other cross-cutting concerns.
"""

import time
import functools
from flask import jsonify, request
from flask_login import current_user
from .exceptions import AuthenticationException, ValidationException


def cached(timeout=300):
    """
    Decorator to cache function results.
    Uses a simple dictionary-based cache (in production, use Redis).
    
    Args:
        timeout: Cache timeout in seconds
    """
    cache = {}
    cache_times = {}
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            current_time = time.time()
            
            # Check if cached and not expired
            if key in cache and (current_time - cache_times[key]) < timeout:
                return cache[key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[key] = result
            cache_times[key] = current_time
            
            return result
        
        # Add cache control methods
        wrapper.clear_cache = lambda: cache.clear()
        wrapper.cache = cache
        
        return wrapper
    return decorator


def timed(func):
    """
    Decorator to measure function execution time.
    Useful for performance monitoring.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"⏱️  {func.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    return wrapper


def require_authentication(func):
    """
    Decorator to require user authentication for route access.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            raise AuthenticationException("You must be logged in to access this resource")
        return func(*args, **kwargs)
    return wrapper


def validate_request(*validators):
    """
    Decorator to validate request data using validator functions.
    
    Args:
        validators: Variable number of validator functions
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            errors = {}
            
            for validator in validators:
                result = validator(request)
                if result:
                    errors.update(result)
            
            if errors:
                raise ValidationException("Request validation failed", errors)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def api_response(func):
    """
    Decorator to standardize API responses.
    Wraps return values in a consistent JSON structure.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # If already a Response object, return as-is
            if hasattr(result, 'get_json'):
                return result
            
            # Wrap in standard response format
            return jsonify({
                'success': True,
                'data': result,
                'error': None
            }), 200
            
        except Exception as e:
            status_code = getattr(e, 'status_code', 500)
            return jsonify({
                'success': False,
                'data': None,
                'error': {
                    'message': str(e),
                    'type': e.__class__.__name__
                }
            }), status_code
    
    return wrapper


def rate_limit(max_requests=100, window=60):
    """
    Simple rate limiting decorator.
    In production, use Redis-based rate limiting.
    
    Args:
        max_requests: Maximum requests allowed
        window: Time window in seconds
    """
    requests_log = {}
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            client_id = request.remote_addr
            current_time = time.time()
            
            # Clean old entries
            if client_id in requests_log:
                requests_log[client_id] = [
                    req_time for req_time in requests_log[client_id]
                    if current_time - req_time < window
                ]
            else:
                requests_log[client_id] = []
            
            # Check rate limit
            if len(requests_log[client_id]) >= max_requests:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': window
                }), 429
            
            # Log request
            requests_log[client_id].append(current_time)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_activity(activity_type):
    """
    Decorator to log user activities.
    
    Args:
        activity_type: Type of activity being performed
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            if current_user.is_authenticated:
                # In production, log to database or analytics service
                print(f"📊 Activity: {current_user.username} - {activity_type}")
            
            return result
        return wrapper
    return decorator
