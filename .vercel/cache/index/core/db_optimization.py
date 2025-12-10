"""
Database optimization utilities for Sabor Con Flow Dance.
SPEC_06 Group B Task 6 - Database query and performance optimization.

This module provides:
- Query optimization helpers
- Database index management
- Performance monitoring
- Slow query logging
- Cache management utilities
"""

import logging
import time
from functools import wraps
from typing import Any, Dict, List, Optional, Type
from django.core.cache import cache
from django.db import connection
from django.db.models import QuerySet, Model
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

# Performance thresholds (in milliseconds)
SLOW_QUERY_THRESHOLD = 100  # Log queries taking longer than 100ms
CRITICAL_QUERY_THRESHOLD = 500  # Alert for queries taking longer than 500ms

class QueryOptimizer:
    """
    Query optimization utilities for improving database performance.
    """
    
    @staticmethod
    def optimize_testimonial_queries():
        """
        Optimize common testimonial queries with select_related and prefetch_related.
        """
        from .models import Testimonial
        
        # Optimized query for testimonial display
        return Testimonial.objects.select_related().prefetch_related().filter(
            status='approved',
            published_at__isnull=False
        ).only(
            'id', 'student_name', 'rating', 'content', 'class_type',
            'published_at', 'photo', 'video_url', 'featured'
        )
    
    @staticmethod
    def optimize_class_queries():
        """
        Optimize class queries with instructor data.
        """
        from .models import Class
        
        return Class.objects.select_related('instructor').only(
            'id', 'name', 'level', 'day_of_week', 'start_time', 'end_time',
            'description', 'capacity', 'instructor__id', 'instructor__name',
            'instructor__photo_url', 'instructor__specialties'
        )
    
    @staticmethod
    def optimize_media_queries():
        """
        Optimize media gallery queries.
        """
        from .models import MediaGallery
        
        return MediaGallery.objects.only(
            'id', 'title', 'media_type', 'category', 'file', 'url',
            'thumbnail', 'caption', 'order', 'is_featured', 'created_at',
            'instagram_id', 'instagram_permalink'
        )
    
    @staticmethod
    def optimize_instructor_queries():
        """
        Optimize instructor queries.
        """
        from .models import Instructor
        
        return Instructor.objects.only(
            'id', 'name', 'bio', 'photo_url', 'video_url',
            'instagram', 'specialties'
        )

class CacheManager:
    """
    Enhanced cache management for database optimization.
    """
    
    # Cache timeouts (in seconds)
    CACHE_TIMEOUTS = {
        'short': 60 * 5,      # 5 minutes
        'medium': 60 * 30,    # 30 minutes  
        'long': 60 * 60,      # 1 hour
        'extended': 60 * 60 * 6,  # 6 hours
    }
    
    @classmethod
    def get_cache_key(cls, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments."""
        key_parts = [prefix] + [str(arg) for arg in args]
        return '_'.join(key_parts)
    
    @classmethod
    def cache_queryset(cls, cache_key: str, queryset: QuerySet, timeout: str = 'medium') -> List:
        """Cache a queryset with the specified timeout."""
        cached_data = cache.get(cache_key)
        if cached_data is None:
            cached_data = list(queryset)
            cache.set(cache_key, cached_data, cls.CACHE_TIMEOUTS[timeout])
            logger.debug(f"Cached queryset with key: {cache_key}")
        return cached_data
    
    @classmethod
    def cache_aggregation(cls, cache_key: str, queryset: QuerySet, aggregation: Dict, timeout: str = 'medium') -> Dict:
        """Cache aggregation results."""
        cached_data = cache.get(cache_key)
        if cached_data is None:
            cached_data = queryset.aggregate(**aggregation)
            cache.set(cache_key, cached_data, cls.CACHE_TIMEOUTS[timeout])
            logger.debug(f"Cached aggregation with key: {cache_key}")
        return cached_data
    
    @classmethod
    def invalidate_pattern(cls, pattern: str):
        """Invalidate all cache keys matching a pattern."""
        # Note: This is a simple implementation
        # For production, consider using django-redis with pattern deletion
        logger.info(f"Cache invalidation requested for pattern: {pattern}")

class QueryPerformanceMonitor:
    """
    Monitor and log database query performance.
    """
    
    @staticmethod
    def log_slow_queries():
        """Log slow queries from connection.queries."""
        if not settings.DEBUG:
            return
            
        slow_queries = []
        for query in connection.queries:
            time_ms = float(query['time']) * 1000
            if time_ms > SLOW_QUERY_THRESHOLD:
                slow_queries.append({
                    'sql': query['sql'][:200] + '...' if len(query['sql']) > 200 else query['sql'],
                    'time_ms': time_ms,
                    'severity': 'critical' if time_ms > CRITICAL_QUERY_THRESHOLD else 'warning'
                })
        
        if slow_queries:
            logger.warning(f"Detected {len(slow_queries)} slow queries")
            for query in slow_queries:
                logger.warning(f"Slow query ({query['time_ms']:.2f}ms): {query['sql']}")
    
    @staticmethod
    def monitor_query(func):
        """Decorator to monitor query performance."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_queries = len(connection.queries)
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                end_queries = len(connection.queries)
                
                execution_time = (end_time - start_time) * 1000
                query_count = end_queries - start_queries
                
                if execution_time > SLOW_QUERY_THRESHOLD:
                    logger.warning(
                        f"Slow function: {func.__name__} took {execution_time:.2f}ms "
                        f"with {query_count} queries"
                    )
                elif settings.DEBUG:
                    logger.debug(
                        f"Function: {func.__name__} took {execution_time:.2f}ms "
                        f"with {query_count} queries"
                    )
        
        return wrapper

def monitor_db_performance(func):
    """
    Decorator for monitoring database performance in views.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        start_time = time.time()
        start_queries = len(connection.queries) if settings.DEBUG else 0
        
        try:
            response = func(request, *args, **kwargs)
            return response
        finally:
            if settings.DEBUG:
                end_time = time.time()
                end_queries = len(connection.queries)
                
                execution_time = (end_time - start_time) * 1000
                query_count = end_queries - start_queries
                
                logger.info(
                    f"View {func.__name__}: {execution_time:.2f}ms, "
                    f"{query_count} queries"
                )
                
                # Log slow queries
                QueryPerformanceMonitor.log_slow_queries()
    
    return wrapper

class DatabaseIndexManager:
    """
    Manage database indexes for optimal performance.
    """
    
    @staticmethod
    def get_recommended_indexes() -> List[Dict[str, Any]]:
        """
        Get list of recommended database indexes based on query patterns.
        """
        return [
            {
                'model': 'Testimonial',
                'fields': ['status', 'featured', 'published_at'],
                'name': 'idx_testimonial_status_featured_published',
                'reason': 'Featured testimonials filtering'
            },
            {
                'model': 'Testimonial', 
                'fields': ['status', 'published_at'],
                'name': 'idx_testimonial_status_published',
                'reason': 'Approved testimonials ordering'
            },
            {
                'model': 'Class',
                'fields': ['day_of_week', 'start_time'],
                'name': 'idx_class_day_time',
                'reason': 'Schedule queries'
            },
            {
                'model': 'MediaGallery',
                'fields': ['media_type', 'category', 'order'],
                'name': 'idx_media_type_category_order',
                'reason': 'Gallery filtering and ordering'
            },
            {
                'model': 'FacebookEvent',
                'fields': ['is_active', 'start_time'],
                'name': 'idx_facebook_event_active_time',
                'reason': 'Upcoming events queries'
            },
            {
                'model': 'FacebookEvent',
                'fields': ['featured', 'start_time'],
                'name': 'idx_facebook_event_featured_time',
                'reason': 'Featured events queries'
            },
            {
                'model': 'ContactSubmission',
                'fields': ['status', 'priority', 'created_at'],
                'name': 'idx_contact_status_priority_created',
                'reason': 'Admin dashboard queries'
            },
            {
                'model': 'BookingConfirmation',
                'fields': ['booking_date', 'status'],
                'name': 'idx_booking_date_status',
                'reason': 'Upcoming bookings queries'
            },
            {
                'model': 'RSVPSubmission',
                'fields': ['class_id', 'status', 'created_at'],
                'name': 'idx_rsvp_class_status_created',
                'reason': 'RSVP counts and filtering'
            },
            {
                'model': 'SpotifyPlaylist',
                'fields': ['is_active', 'order', 'class_type'],
                'name': 'idx_spotify_active_order_type',
                'reason': 'Active playlists ordering'
            }
        ]
    
    @staticmethod
    def generate_index_sql() -> List[str]:
        """
        Generate SQL statements for creating recommended indexes.
        Note: These are SQLite-compatible indexes.
        """
        indexes = DatabaseIndexManager.get_recommended_indexes()
        sql_statements = []
        
        # Map Django model names to database table names
        table_mapping = {
            'Testimonial': 'core_testimonial',
            'Class': 'core_class',
            'MediaGallery': 'core_mediagallery',
            'FacebookEvent': 'core_facebookevent',
            'ContactSubmission': 'core_contactsubmission',
            'BookingConfirmation': 'core_bookingconfirmation',
            'RSVPSubmission': 'core_rsvpsubmission',
            'SpotifyPlaylist': 'core_spotifyplaylist'
        }
        
        for index in indexes:
            table_name = table_mapping.get(index['model'])
            if table_name:
                fields_str = ', '.join(index['fields'])
                sql = f"CREATE INDEX IF NOT EXISTS {index['name']} ON {table_name} ({fields_str});"
                sql_statements.append(sql)
        
        return sql_statements

def optimize_database_settings():
    """
    Apply database optimization settings for SQLite.
    """
    if settings.DEBUG:
        return
    
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL;")
        
        # Optimize cache size (in pages, default page size is 4KB)
        cursor.execute("PRAGMA cache_size=2000;")  # 8MB cache
        
        # Enable memory temp store
        cursor.execute("PRAGMA temp_store=MEMORY;")
        
        # Optimize synchronous mode for better performance
        cursor.execute("PRAGMA synchronous=NORMAL;")
        
        # Enable auto vacuum
        cursor.execute("PRAGMA auto_vacuum=INCREMENTAL;")
        
        logger.info("Applied SQLite performance optimizations")

def create_database_indexes():
    """
    Create all recommended database indexes.
    """
    from django.db import connection
    
    sql_statements = DatabaseIndexManager.generate_index_sql()
    
    with connection.cursor() as cursor:
        for sql in sql_statements:
            try:
                cursor.execute(sql)
                logger.info(f"Created index: {sql}")
            except Exception as e:
                logger.error(f"Failed to create index: {sql}, Error: {e}")

class QuerySetOptimizer:
    """
    Chainable QuerySet optimizer for common patterns.
    """
    
    def __init__(self, model: Type[Model]):
        self.model = model
        self.queryset = model.objects.all()
    
    def for_display(self) -> 'QuerySetOptimizer':
        """Optimize for display purposes (select only needed fields)."""
        if self.model.__name__ == 'Testimonial':
            self.queryset = self.queryset.only(
                'id', 'student_name', 'rating', 'content', 'class_type',
                'published_at', 'photo', 'video_url', 'featured'
            )
        elif self.model.__name__ == 'Instructor':
            self.queryset = self.queryset.only(
                'id', 'name', 'bio', 'photo_url', 'video_url',
                'instagram', 'specialties'
            )
        return self
    
    def with_related(self) -> 'QuerySetOptimizer':
        """Add select_related for foreign keys."""
        if self.model.__name__ == 'Class':
            self.queryset = self.queryset.select_related('instructor')
        return self
    
    def cached(self, cache_key: str, timeout: str = 'medium') -> List:
        """Return cached results."""
        return CacheManager.cache_queryset(cache_key, self.queryset, timeout)
    
    def get_queryset(self) -> QuerySet:
        """Get the optimized queryset."""
        return self.queryset

# Usage examples and helper functions
def get_optimized_testimonials(status='approved', featured=None, limit=None):
    """Get optimized testimonials with caching."""
    cache_key = f"testimonials_{status}_{featured}_{limit}"
    
    queryset = QuerySetOptimizer(Testimonial).for_display().get_queryset()
    queryset = queryset.filter(status=status, published_at__isnull=False)
    
    if featured is not None:
        queryset = queryset.filter(featured=featured)
    
    queryset = queryset.order_by('-published_at')
    
    if limit:
        queryset = queryset[:limit]
    
    return CacheManager.cache_queryset(cache_key, queryset)

def get_optimized_classes(day_of_week=None):
    """Get optimized classes with instructor data."""
    cache_key = f"classes_{day_of_week}"
    
    queryset = QuerySetOptimizer(Class).for_display().with_related().get_queryset()
    
    if day_of_week:
        queryset = queryset.filter(day_of_week=day_of_week)
    
    queryset = queryset.order_by('start_time')
    
    return CacheManager.cache_queryset(cache_key, queryset)

def get_testimonial_stats():
    """Get testimonial statistics with caching."""
    cache_key = "testimonial_stats"
    
    from .models import Testimonial
    
    aggregation = {
        'average_rating': Avg('rating'),
        'total_reviews': Count('id'),
        'featured_count': Count(Case(When(featured=True, then=1), output_field=IntegerField()))
    }
    
    queryset = Testimonial.objects.filter(status='approved')
    return CacheManager.cache_aggregation(cache_key, queryset, aggregation)