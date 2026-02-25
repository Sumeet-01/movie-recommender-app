"""In-memory cache with TTL support."""

import time
import threading


class InMemoryCache:
    def __init__(self):
        self._cache = {}
        self._lock = threading.RLock()

    def get(self, key, default=None):
        with self._lock:
            entry = self._cache.get(key)
            if entry and (time.time() - entry['time']) < entry['ttl']:
                return entry['value']
            if entry:
                del self._cache[key]
            return default

    def set(self, key, value, ttl=300):
        with self._lock:
            self._cache[key] = {'value': value, 'time': time.time(), 'ttl': ttl}

    def delete(self, key):
        with self._lock:
            self._cache.pop(key, None)

    def clear(self):
        with self._lock:
            self._cache.clear()


cache = InMemoryCache()

def cache_key(*args, **kwargs):
    return f"{':'.join(str(a) for a in args)}:{str(sorted(kwargs.items()))}"
