"""
Caching Utilities - Phase 1.4
Provides performance caching for expensive operations using diskcache.

Features:
- Disk-based caching for embeddings and scores
- Configurable TTL (time-to-live)
- Memory-safe (doesn't consume RAM)
- Automatic cache invalidation
"""

import hashlib
import json
from functools import wraps
from typing import Any, Callable, Optional
import os


# Global cache instance
_cache_instance = None


def get_cache():
    """
    Get or create cache instance.

    Returns:
        Cache instance or None if diskcache not available
    """
    global _cache_instance

    if _cache_instance is not None:
        return _cache_instance

    try:
        from diskcache import Cache

        # Use /tmp for cache directory (safe for all systems)
        cache_dir = os.environ.get('ATS_CACHE_DIR', '/tmp/ats_cache')
        _cache_instance = Cache(cache_dir)
        return _cache_instance

    except ImportError:
        print("Warning: diskcache not installed. Caching disabled. Install: pip install diskcache")
        return None


def cache_result(
    expire: int = 3600,
    key_prefix: str = "",
    enabled: bool = True
) -> Callable:
    """
    Decorator to cache function results.

    Args:
        expire: Cache expiration time in seconds (default: 1 hour)
        key_prefix: Prefix for cache keys (default: function name)
        enabled: Enable/disable caching (default: True)

    Returns:
        Decorator function

    Example:
        @cache_result(expire=3600, key_prefix='score')
        def score_resume(resume_text, job_description):
            # Expensive operation
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Skip caching if disabled
            if not enabled:
                return func(*args, **kwargs)

            cache = get_cache()
            if cache is None:
                # Caching not available, call function directly
                return func(*args, **kwargs)

            # Generate cache key
            prefix = key_prefix or func.__name__
            key = _generate_cache_key(prefix, args, kwargs)

            # Try to get from cache
            try:
                cached_value = cache.get(key)
                if cached_value is not None:
                    return cached_value
            except Exception as e:
                print(f"Cache read error: {e}")

            # Call function and cache result
            result = func(*args, **kwargs)

            try:
                cache.set(key, result, expire=expire)
            except Exception as e:
                print(f"Cache write error: {e}")

            return result

        # Add cache management methods
        wrapper.clear_cache = lambda: _clear_cache(key_prefix or func.__name__)
        wrapper.cache_info = lambda: _cache_info(key_prefix or func.__name__)

        return wrapper
    return decorator


def _generate_cache_key(prefix: str, args: tuple, kwargs: dict) -> str:
    """
    Generate a unique cache key from function arguments.

    Args:
        prefix: Key prefix
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    # Convert args and kwargs to string
    key_parts = [prefix]

    # Add args
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        else:
            # For complex objects, use hash
            key_parts.append(str(hash(str(arg))))

    # Add kwargs
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (str, int, float, bool)):
            key_parts.append(f"{k}={v}")
        else:
            key_parts.append(f"{k}={hash(str(v))}")

    # Create hash of the key parts
    key_str = "|".join(key_parts)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()

    return f"{prefix}:{key_hash}"


def _clear_cache(prefix: str) -> int:
    """
    Clear all cache entries with given prefix.

    Args:
        prefix: Cache key prefix

    Returns:
        Number of entries cleared
    """
    cache = get_cache()
    if cache is None:
        return 0

    try:
        count = 0
        for key in list(cache.iterkeys()):
            if key.startswith(prefix):
                cache.delete(key)
                count += 1
        return count
    except Exception as e:
        print(f"Error clearing cache: {e}")
        return 0


def _cache_info(prefix: str) -> dict:
    """
    Get cache statistics for given prefix.

    Args:
        prefix: Cache key prefix

    Returns:
        Dictionary with cache statistics
    """
    cache = get_cache()
    if cache is None:
        return {'enabled': False}

    try:
        count = sum(1 for key in cache.iterkeys() if key.startswith(prefix))
        return {
            'enabled': True,
            'entries': count,
            'total_size': cache.volume()
        }
    except Exception as e:
        print(f"Error getting cache info: {e}")
        return {'enabled': True, 'error': str(e)}


def clear_all_cache():
    """Clear all cache entries"""
    cache = get_cache()
    if cache is not None:
        try:
            cache.clear()
            return True
        except Exception as e:
            print(f"Error clearing all cache: {e}")
            return False
    return False


def get_cache_stats() -> dict:
    """
    Get overall cache statistics.

    Returns:
        Dictionary with cache stats
    """
    cache = get_cache()
    if cache is None:
        return {'enabled': False}

    try:
        return {
            'enabled': True,
            'size': len(cache),
            'volume': cache.volume(),
            'directory': cache.directory
        }
    except Exception as e:
        return {'enabled': True, 'error': str(e)}


# Specialized caching decorators for common use cases

def cache_embeddings(expire: int = 7200):
    """
    Cache embeddings for 2 hours.
    Embeddings are expensive to compute but stable.
    """
    return cache_result(expire=expire, key_prefix='embeddings')


def cache_scores(expire: int = 3600):
    """
    Cache scoring results for 1 hour.
    Scores may change as algorithms are updated.
    """
    return cache_result(expire=expire, key_prefix='scores')


def cache_grammar(expire: int = 3600):
    """
    Cache grammar check results for 1 hour.
    Grammar checks are expensive but stable.
    """
    return cache_result(expire=expire, key_prefix='grammar')


def cache_keywords(expire: int = 1800):
    """
    Cache keyword extraction for 30 minutes.
    Keywords may change with job descriptions.
    """
    return cache_result(expire=expire, key_prefix='keywords')
