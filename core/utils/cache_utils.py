"""
Cache utility functions for cache invalidation and management.
"""
import hashlib
import time
from django.core.cache import cache, caches
from django.conf import settings
from django.utils.cache import get_cache_key
from django.http import HttpRequest


class CacheManager:
    """
    Centralized cache management utility.
    """
    
    def __init__(self):
        self.default_cache = cache
        self.page_cache = caches['page_cache'] if 'page_cache' in settings.CACHES else cache
        self.static_cache = caches['static_cache'] if 'static_cache' in settings.CACHES else cache
    
    def invalidate_page_cache(self, path_pattern=None):
        """
        Invalidate page cache for specific patterns or all pages.
        
        Args:
            path_pattern (str): Optional pattern to match cached pages
        """
        if path_pattern:
            # Invalidate specific pattern
            cache_key = self._generate_page_cache_key(path_pattern)
            self.page_cache.delete(cache_key)
        else:
            # Clear all page cache
            self.page_cache.clear()
    
    def invalidate_static_cache(self, file_pattern=None):
        """
        Invalidate static file cache.
        
        Args:
            file_pattern (str): Optional pattern to match cached static files
        """
        if file_pattern:
            cache_key = self._generate_static_cache_key(file_pattern)
            self.static_cache.delete(cache_key)
        else:
            self.static_cache.clear()
    
    def get_cache_stats(self):
        """
        Get cache statistics and health metrics.
        
        Returns:
            dict: Cache statistics
        """
        stats = {
            'default_cache': self._get_cache_info(self.default_cache),
            'page_cache': self._get_cache_info(self.page_cache),
            'static_cache': self._get_cache_info(self.static_cache),
            'timestamp': time.time()
        }
        return stats
    
    def warm_cache(self, urls):
        """
        Pre-warm cache with frequently accessed URLs.
        
        Args:
            urls (list): List of URLs to pre-warm
        """
        from django.test import RequestFactory
        from django.core.handlers.wsgi import WSGIRequest
        
        factory = RequestFactory()
        
        for url in urls:
            try:
                request = factory.get(url)
                cache_key = self._generate_page_cache_key(url)
                # This would typically involve actually rendering the page
                # For now, we'll just set a placeholder
                self.page_cache.set(cache_key, {'warmed': True, 'url': url}, timeout=3600)
            except Exception as e:
                print(f"Failed to warm cache for {url}: {e}")
    
    def _generate_page_cache_key(self, path):
        """Generate cache key for page."""
        return f"page:{hashlib.md5(path.encode()).hexdigest()}"
    
    def _generate_static_cache_key(self, file_path):
        """Generate cache key for static file."""
        return f"static:{hashlib.md5(file_path.encode()).hexdigest()}"
    
    def _get_cache_info(self, cache_instance):
        """Get information about a cache instance."""
        try:
            # This is basic info - real implementations would vary by backend
            return {
                'backend': cache_instance.__class__.__name__,
                'location': getattr(cache_instance, 'location', 'Unknown'),
                'timeout': getattr(cache_instance, 'default_timeout', 'Unknown')
            }
        except Exception:
            return {'error': 'Unable to get cache info'}


class CacheBusting:
    """
    Utilities for cache busting and versioning.
    """
    
    @staticmethod
    def generate_version_hash(file_path):
        """
        Generate version hash for static files.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Version hash
        """
        try:
            import os
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                # Use file modification time and size for versioning
                version_string = f"{stat.st_mtime}_{stat.st_size}"
                return hashlib.md5(version_string.encode()).hexdigest()[:8]
            else:
                # Fallback to timestamp if file doesn't exist
                return hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        except Exception:
            # Ultimate fallback
            return hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    
    @staticmethod
    def add_version_to_url(url, version=None):
        """
        Add version parameter to URL for cache busting.
        
        Args:
            url (str): Original URL
            version (str): Version string (optional)
            
        Returns:
            str: URL with version parameter
        """
        if not version:
            version = str(int(time.time()))
        
        separator = '&' if '?' in url else '?'
        return f"{url}{separator}v={version}"
    
    @staticmethod
    def get_static_file_version(file_path):
        """
        Get version for static file based on content hash.
        
        Args:
            file_path (str): Static file path
            
        Returns:
            str: Version hash
        """
        cache_key = f"static_version:{file_path}"
        version = cache.get(cache_key)
        
        if not version:
            version = CacheBusting.generate_version_hash(file_path)
            cache.set(cache_key, version, timeout=86400)  # Cache for 24 hours
        
        return version


class PerformanceCache:
    """
    Performance-oriented caching utilities.
    """
    
    @staticmethod
    def cache_expensive_operation(cache_key, operation_func, timeout=300, *args, **kwargs):
        """
        Cache the result of an expensive operation.
        
        Args:
            cache_key (str): Cache key
            operation_func (callable): Function to execute if not cached
            timeout (int): Cache timeout in seconds
            *args, **kwargs: Arguments for operation_func
            
        Returns:
            Result of operation_func
        """
        result = cache.get(cache_key)
        
        if result is None:
            result = operation_func(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
        
        return result
    
    @staticmethod
    def cache_database_query(model_class, query_params, timeout=300):
        """
        Cache database query results.
        
        Args:
            model_class: Django model class
            query_params (dict): Query parameters
            timeout (int): Cache timeout in seconds
            
        Returns:
            QuerySet results
        """
        # Generate cache key from model and query params
        cache_key = f"db_query:{model_class.__name__}:{hash(str(sorted(query_params.items())))}"
        
        result = cache.get(cache_key)
        
        if result is None:
            result = list(model_class.objects.filter(**query_params))
            cache.set(cache_key, result, timeout=timeout)
        
        return result
    
    @staticmethod
    def invalidate_model_cache(model_class):
        """
        Invalidate all cached queries for a model.
        
        Args:
            model_class: Django model class
        """
        # This is a simplified approach - real implementation would track cache keys
        cache_pattern = f"db_query:{model_class.__name__}:"
        # Note: This would require a cache backend that supports pattern deletion
        # For now, we'll just document the pattern
        print(f"Would invalidate cache pattern: {cache_pattern}*")


def get_cache_headers(content_type, is_static=False):
    """
    Get appropriate cache headers for content type.
    
    Args:
        content_type (str): MIME type of content
        is_static (bool): Whether this is a static asset
        
    Returns:
        dict: Cache headers
    """
    headers = {}
    
    if is_static:
        # Static assets get long cache duration
        headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        headers['Expires'] = time.strftime('%a, %d %b %Y %H:%M:%S GMT', 
                                         time.gmtime(time.time() + 31536000))
    elif 'text/html' in content_type:
        # HTML pages get medium cache duration
        headers['Cache-Control'] = 'public, max-age=3600'
        headers['Expires'] = time.strftime('%a, %d %b %Y %H:%M:%S GMT', 
                                         time.gmtime(time.time() + 3600))
    elif 'application/json' in content_type:
        # API responses get short cache duration
        headers['Cache-Control'] = 'public, max-age=300'
        headers['Expires'] = time.strftime('%a, %d %b %Y %H:%M:%S GMT', 
                                         time.gmtime(time.time() + 300))
    else:
        # Dynamic content should not be cached
        headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        headers['Pragma'] = 'no-cache'
        headers['Expires'] = '0'
    
    return headers


# Global cache manager instance
cache_manager = CacheManager()