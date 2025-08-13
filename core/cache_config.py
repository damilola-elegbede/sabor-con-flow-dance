"""
Enhanced cache configuration and Redis support.
SPEC_06 Group B Task 6 - Database query and performance optimization.

This module provides:
- Redis cache configuration
- Cache strategy patterns
- Performance monitoring
- Cache invalidation utilities
"""

import logging
from typing import Any, Dict, List, Optional
from django.core.cache import cache
from django.conf import settings
import json
import time

logger = logging.getLogger(__name__)

class CacheConfig:
    """
    Enhanced cache configuration for optimal performance.
    """
    
    # Cache timeout configurations (in seconds)
    TIMEOUTS = {
        'ultra_short': 60,        # 1 minute
        'short': 300,             # 5 minutes
        'medium': 1800,           # 30 minutes
        'long': 3600,             # 1 hour
        'extended': 21600,        # 6 hours
        'daily': 86400,           # 24 hours
        'weekly': 604800,         # 1 week
    }
    
    # Cache key patterns
    KEY_PATTERNS = {
        'testimonials': 'testimonials_{status}_{featured}_{limit}',
        'classes': 'classes_{day}_{instructor}',
        'instructors': 'instructors_{id}_{list}',
        'media': 'media_{type}_{category}_{order}',
        'events': 'events_{type}_{active}_{limit}',
        'playlists': 'playlists_{active}_{type}',
        'stats': 'stats_{model}_{aggregation}',
        'rsvp': 'rsvp_{class_id}_{status}_{date}',
    }
    
    @classmethod
    def get_cache_key(cls, pattern: str, **kwargs) -> str:
        """Generate cache key from pattern and parameters."""
        template = cls.KEY_PATTERNS.get(pattern, pattern)
        return template.format(**kwargs)
    
    @classmethod
    def get_timeout(cls, duration: str) -> int:
        """Get cache timeout by duration name."""
        return cls.TIMEOUTS.get(duration, cls.TIMEOUTS['medium'])

class RedisCacheBackend:
    """
    Redis-specific cache operations and optimizations.
    """
    
    @staticmethod
    def is_redis_available() -> bool:
        """Check if Redis is available and configured."""
        try:
            backend = getattr(settings, 'CACHES', {}).get('default', {}).get('BACKEND', '')
            return 'redis' in backend.lower()
        except:
            return False
    
    @staticmethod
    def get_redis_info() -> Dict[str, Any]:
        """Get Redis connection information."""
        if not RedisCacheBackend.is_redis_available():
            return {'available': False, 'error': 'Redis not configured'}
        
        try:
            # Try to get cache stats if Redis is available
            return {
                'available': True,
                'backend': settings.CACHES['default']['BACKEND'],
                'location': settings.CACHES['default'].get('LOCATION', 'Unknown'),
            }
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    @staticmethod
    def clear_pattern(pattern: str) -> int:
        """Clear cache keys matching a pattern (Redis specific)."""
        if not RedisCacheBackend.is_redis_available():
            logger.warning("Pattern deletion not available without Redis")
            return 0
        
        try:
            # This would require django-redis and connection access
            logger.info(f"Would clear cache pattern: {pattern}")
            return 0
        except Exception as e:
            logger.error(f"Failed to clear cache pattern {pattern}: {e}")
            return 0

class CacheStrategy:
    """
    Cache strategy patterns for different data types.
    """
    
    @staticmethod
    def cache_queryset(
        cache_key: str,
        queryset_func: callable,
        timeout: str = 'medium',
        force_refresh: bool = False
    ) -> List[Any]:
        """
        Cache queryset results with configurable timeout.
        """
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_data
        
        logger.debug(f"Cache MISS: {cache_key}")
        
        # Execute queryset and cache results
        start_time = time.time()
        data = list(queryset_func())
        execution_time = (time.time() - start_time) * 1000
        
        # Cache the results
        timeout_seconds = CacheConfig.get_timeout(timeout)
        cache.set(cache_key, data, timeout_seconds)
        
        logger.debug(
            f"Cached {len(data)} items in {cache_key} "
            f"(execution: {execution_time:.2f}ms, timeout: {timeout})"
        )
        
        return data
    
    @staticmethod
    def cache_aggregation(
        cache_key: str,
        aggregation_func: callable,
        timeout: str = 'medium',
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Cache database aggregation results.
        """
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Aggregation cache HIT: {cache_key}")
                return cached_data
        
        logger.debug(f"Aggregation cache MISS: {cache_key}")
        
        # Execute aggregation and cache results
        start_time = time.time()
        data = aggregation_func()
        execution_time = (time.time() - start_time) * 1000
        
        # Cache the results
        timeout_seconds = CacheConfig.get_timeout(timeout)
        cache.set(cache_key, data, timeout_seconds)
        
        logger.debug(
            f"Cached aggregation in {cache_key} "
            f"(execution: {execution_time:.2f}ms, timeout: {timeout})"
        )
        
        return data
    
    @staticmethod
    def cache_api_response(
        cache_key: str,
        api_func: callable,
        timeout: str = 'long',
        force_refresh: bool = False
    ) -> Any:
        """
        Cache external API responses with longer timeouts.
        """
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"API cache HIT: {cache_key}")
                return cached_data
        
        logger.debug(f"API cache MISS: {cache_key}")
        
        try:
            # Execute API call and cache results
            start_time = time.time()
            data = api_func()
            execution_time = (time.time() - start_time) * 1000
            
            # Cache the results
            timeout_seconds = CacheConfig.get_timeout(timeout)
            cache.set(cache_key, data, timeout_seconds)
            
            logger.debug(
                f"Cached API response in {cache_key} "
                f"(execution: {execution_time:.2f}ms, timeout: {timeout})"
            )
            
            return data
            
        except Exception as e:
            logger.error(f"API call failed for {cache_key}: {e}")
            # Return cached data if available, even if expired
            cached_data = cache.get(f"{cache_key}_backup")
            if cached_data is not None:
                logger.info(f"Using backup cache for {cache_key}")
                return cached_data
            raise

class CacheInvalidation:
    """
    Cache invalidation strategies and utilities.
    """
    
    @staticmethod
    def invalidate_model_cache(model_name: str) -> int:
        """
        Invalidate all cache keys related to a specific model.
        """
        invalidated_count = 0
        
        # Define cache key patterns for each model
        model_patterns = {
            'testimonial': [
                'testimonials_*',
                'stats_testimonial_*',
                'home_carousel_*'
            ],
            'class': [
                'classes_*',
                'schedule_*',
                'instructor_classes_*'
            ],
            'instructor': [
                'instructors_*',
                'instructor_list_*',
                'classes_*'  # Classes include instructor data
            ],
            'mediagallery': [
                'media_*',
                'gallery_*'
            ],
            'facebookevent': [
                'events_*',
                'schedule_facebook_*'
            ],
            'spotifyplaylist': [
                'playlists_*',
                'resources_*',
                'home_spotify_*'
            ],
            'rsvpsubmission': [
                'rsvp_*',
                'stats_rsvp_*'
            ]
        }
        
        patterns = model_patterns.get(model_name.lower(), [])
        
        for pattern in patterns:
            if RedisCacheBackend.is_redis_available():
                count = RedisCacheBackend.clear_pattern(pattern)
                invalidated_count += count
            else:
                # Fallback for non-Redis backends
                logger.info(f"Would invalidate pattern: {pattern}")
        
        logger.info(f"Invalidated {invalidated_count} cache keys for model: {model_name}")
        return invalidated_count
    
    @staticmethod
    def invalidate_view_cache(view_name: str) -> None:
        """
        Invalidate cache for specific views.
        """
        view_cache_keys = {
            'home': ['home_carousel_testimonials', 'home_spotify_playlists'],
            'schedule': ['schedule_sunday_classes', 'schedule_facebook_events'],
            'testimonials': ['testimonials_*', 'testimonial_stats'],
            'gallery': ['gallery_media_*', 'gallery_categories'],
            'instructors': ['instructor_list_data', 'instructors_*'],
            'resources': ['resources_spotify_playlists'],
        }
        
        keys_to_clear = view_cache_keys.get(view_name, [])
        
        for key in keys_to_clear:
            if '*' in key:
                if RedisCacheBackend.is_redis_available():
                    RedisCacheBackend.clear_pattern(key)
                else:
                    logger.info(f"Would clear cache pattern: {key}")
            else:
                cache.delete(key)
                logger.debug(f"Cleared cache key: {key}")
    
    @staticmethod
    def warm_cache() -> Dict[str, Any]:
        """
        Warm up critical cache entries.
        """
        warming_results = {}
        
        try:
            # Import here to avoid circular imports
            from .models import Testimonial, Class, Instructor, SpotifyPlaylist
            
            # Warm testimonials cache
            start_time = time.time()
            testimonials = list(
                Testimonial.objects.filter(status='approved', featured=True)
                .only('id', 'student_name', 'rating', 'content')[:6]
            )
            cache.set('home_carousel_testimonials', testimonials, CacheConfig.get_timeout('medium'))
            warming_results['testimonials'] = {
                'count': len(testimonials),
                'time': (time.time() - start_time) * 1000
            }
            
            # Warm classes cache
            start_time = time.time()
            classes = list(
                Class.objects.filter(day_of_week='Sunday')
                .select_related('instructor')
                .only('name', 'start_time', 'instructor__name')
            )
            cache.set('schedule_sunday_classes', classes, CacheConfig.get_timeout('long'))
            warming_results['classes'] = {
                'count': len(classes),
                'time': (time.time() - start_time) * 1000
            }
            
            # Warm instructors cache
            start_time = time.time()
            instructors = list(
                Instructor.objects.only('id', 'name', 'photo_url', 'specialties')
            )
            cache.set('instructor_list_data', instructors, CacheConfig.get_timeout('long'))
            warming_results['instructors'] = {
                'count': len(instructors),
                'time': (time.time() - start_time) * 1000
            }
            
            # Warm playlists cache
            start_time = time.time()
            playlists = list(
                SpotifyPlaylist.objects.filter(is_active=True)
                .only('id', 'class_type', 'title', 'spotify_embed_url')
            )
            cache.set('home_spotify_playlists', playlists, CacheConfig.get_timeout('long'))
            warming_results['playlists'] = {
                'count': len(playlists),
                'time': (time.time() - start_time) * 1000
            }
            
            logger.info(f"Cache warming completed: {warming_results}")
            
        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
            warming_results['error'] = str(e)
        
        return warming_results

class CacheMetrics:
    """
    Cache performance metrics and monitoring.
    """
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """
        Get cache performance statistics.
        """
        stats = {
            'backend': settings.CACHES['default']['BACKEND'],
            'redis_available': RedisCacheBackend.is_redis_available(),
            'cache_keys_count': 0,
            'hit_rate': 0,
            'memory_usage': 0
        }
        
        try:
            # Get basic cache information
            if RedisCacheBackend.is_redis_available():
                redis_info = RedisCacheBackend.get_redis_info()
                stats.update(redis_info)
            
            # Add performance metrics if available
            performance_data = cache.get('cache_performance_metrics', {})
            stats.update(performance_data)
            
        except Exception as e:
            stats['error'] = str(e)
            logger.error(f"Failed to get cache stats: {e}")
        
        return stats
    
    @staticmethod
    def track_cache_operation(operation: str, cache_key: str, hit: bool) -> None:
        """
        Track cache operations for metrics.
        """
        try:
            metrics_key = 'cache_performance_metrics'
            metrics = cache.get(metrics_key, {
                'total_operations': 0,
                'hits': 0,
                'misses': 0,
                'operations_by_key': {}
            })
            
            metrics['total_operations'] += 1
            
            if hit:
                metrics['hits'] += 1
            else:
                metrics['misses'] += 1
            
            # Track by cache key pattern
            key_pattern = cache_key.split('_')[0] if '_' in cache_key else cache_key
            if key_pattern not in metrics['operations_by_key']:
                metrics['operations_by_key'][key_pattern] = {'hits': 0, 'misses': 0}
            
            if hit:
                metrics['operations_by_key'][key_pattern]['hits'] += 1
            else:
                metrics['operations_by_key'][key_pattern]['misses'] += 1
            
            # Calculate hit rate
            if metrics['total_operations'] > 0:
                metrics['hit_rate'] = (metrics['hits'] / metrics['total_operations']) * 100
            
            cache.set(metrics_key, metrics, CacheConfig.get_timeout('daily'))
            
        except Exception as e:
            logger.error(f"Failed to track cache operation: {e}")

# Cache configuration for different environments
def get_redis_cache_config():
    """
    Get Redis cache configuration for production.
    """
    return {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 20,
                    'retry_on_timeout': True,
                },
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            },
            'KEY_PREFIX': 'sabor_con_flow',
            'TIMEOUT': 1800,  # 30 minutes default
        }
    }

def get_memory_cache_config():
    """
    Get in-memory cache configuration for development.
    """
    return {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'sabor-con-flow-cache',
            'TIMEOUT': 300,  # 5 minutes default
            'OPTIONS': {
                'MAX_ENTRIES': 2000,
                'CULL_FREQUENCY': 4,
            },
        }
    }