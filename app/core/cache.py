"""
Caching layer for CineMate application.
Provides in-memory caching with TTL support.
In production, replace with Redis or Memcached.
"""

import time
import threading
from typing import Any, Optional, Callable
from datetime import datetime, timedelta


class CacheEntry:
    """Represents a single cache entry with metadata."""
    
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.hits = 0
        self.last_accessed = time.time()
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if self.ttl == 0:  # 0 means no expiration
            return False
        return (time.time() - self.created_at) >= self.ttl
    
    def access(self) -> Any:
        """Record access and return value."""
        self.hits += 1
        self.last_accessed = time.time()
        return self.value


class InMemoryCache:
    """
    Thread-safe in-memory cache with TTL support.
    Suitable for development and small-scale production.
    For large-scale production, use Redis.
    """
    
    def __init__(self):
        self._cache = {}
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'evictions': 0
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                
                if entry.is_expired():
                    del self._cache[key]
                    self._stats['evictions'] += 1
                    self._stats['misses'] += 1
                    return default
                
                self._stats['hits'] += 1
                return entry.access()
            
            self._stats['misses'] += 1
            return default
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (0 for no expiration)
        """
        with self._lock:
            self._cache[key] = CacheEntry(value, ttl)
            self._stats['sets'] += 1
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key existed, False otherwise
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats['deletes'] += 1
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._stats['evictions'] += count
    
    def get_or_set(self, key: str, factory: Callable, ttl: int = 300) -> Any:
        """
        Get value from cache or set it using factory function.
        
        Args:
            key: Cache key
            factory: Function to call if key not in cache
            ttl: Time to live in seconds
            
        Returns:
            Cached or newly created value
        """
        value = self.get(key)
        
        if value is None:
            value = factory()
            self.set(key, value, ttl)
        
        return value
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self._stats,
                'size': len(self._cache),
                'hit_rate': f"{hit_rate:.2f}%",
                'total_requests': total_requests
            }
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            self._stats['evictions'] += len(expired_keys)
            return len(expired_keys)
    
    def get_keys(self, pattern: Optional[str] = None) -> list:
        """
        Get all cache keys, optionally filtered by pattern.
        
        Args:
            pattern: Optional string pattern to match (simple contains)
            
        Returns:
            List of matching keys
        """
        with self._lock:
            if pattern:
                return [key for key in self._cache.keys() if pattern in key]
            return list(self._cache.keys())


# Global cache instance
cache = InMemoryCache()


def cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from arguments.
    
    Example:
        cache_key('movies', 'trending', page=1) -> 'movies:trending:page=1'
    """
    parts = [str(arg) for arg in args]
    
    if kwargs:
        kw_parts = [f"{k}={v}" for k, v in sorted(kwargs.items())]
        parts.extend(kw_parts)
    
    return ':'.join(parts)
