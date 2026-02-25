"""Custom decorators for CineMate."""

import time
import functools
from flask import jsonify, request
from flask_login import current_user


def cached(timeout=300):
    """Simple in-memory cache decorator."""
    _cache = {}
    _times = {}
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            now = time.time()
            if key in _cache and (now - _times[key]) < timeout:
                return _cache[key]
            result = func(*args, **kwargs)
            _cache[key] = result
            _times[key] = now
            return result
        wrapper.clear_cache = lambda: _cache.clear()
        return wrapper
    return decorator


def timed(func):
    """Measure execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"  {func.__name__} took {time.time()-start:.3f}s")
        return result
    return wrapper


def api_response(func):
    """Wrap return value in JSON response with error handling."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e), 'success': False}), 500
    return wrapper


def rate_limit(max_requests=60, window=60):
    """Simple rate limiter."""
    requests_log = {}
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            # Clean old entries
            requests_log[ip] = [t for t in requests_log.get(ip, []) if now - t < window]
            if len(requests_log.get(ip, [])) >= max_requests:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            requests_log.setdefault(ip, []).append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
