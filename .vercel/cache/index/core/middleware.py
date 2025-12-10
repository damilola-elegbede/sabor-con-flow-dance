"""
Custom middleware for database performance monitoring.
SPEC_06 Group B Task 6 - Database query and performance optimization.

This middleware provides:
- Automatic slow query logging
- Database performance monitoring
- Query count tracking per request
- Performance alerts
"""

import logging
import time
from typing import Callable
from django.conf import settings
from django.db import connection
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

logger = logging.getLogger('database_performance')

class DatabasePerformanceMiddleware(MiddlewareMixin):
    """
    Middleware to monitor database performance and log slow queries.
    """
    
    # Performance thresholds (in milliseconds)
    SLOW_QUERY_THRESHOLD = 100
    CRITICAL_QUERY_THRESHOLD = 500
    TOO_MANY_QUERIES_THRESHOLD = 50
    
    def process_request(self, request: HttpRequest) -> None:
        """Initialize performance monitoring for the request."""
        request._db_performance_start_time = time.time()
        request._db_performance_start_queries = len(connection.queries) if settings.DEBUG else 0
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Monitor and log database performance after request processing."""
        
        # Only monitor in debug mode or if explicitly enabled
        if not (settings.DEBUG or getattr(settings, 'ENABLE_DB_PERFORMANCE_MONITORING', False)):
            return response
        
        # Calculate request performance metrics
        end_time = time.time()
        end_queries = len(connection.queries)
        
        request_time = (end_time - request._db_performance_start_time) * 1000  # Convert to ms
        query_count = end_queries - request._db_performance_start_queries
        
        # Log request performance
        self._log_request_performance(request, request_time, query_count)
        
        # Analyze slow queries
        self._analyze_slow_queries(request, query_count)
        
        # Check for too many queries (N+1 problem)
        self._check_query_count(request, query_count)
        
        # Add performance headers in debug mode
        if settings.DEBUG:
            response['X-DB-Query-Count'] = str(query_count)
            response['X-DB-Request-Time'] = f'{request_time:.2f}ms'
        
        return response
    
    def _log_request_performance(self, request: HttpRequest, request_time: float, query_count: int) -> None:
        """Log overall request performance."""
        path = request.get_full_path()
        method = request.method
        
        # Determine log level based on performance
        if request_time > self.CRITICAL_QUERY_THRESHOLD or query_count > self.TOO_MANY_QUERIES_THRESHOLD:
            log_level = logger.error
            severity = 'CRITICAL'
        elif request_time > self.SLOW_QUERY_THRESHOLD or query_count > 20:
            log_level = logger.warning
            severity = 'WARNING'
        else:
            log_level = logger.debug
            severity = 'INFO'
        
        log_level(
            f'[{severity}] {method} {path} - {request_time:.2f}ms, {query_count} queries'
        )
        
        # Store performance data in cache for monitoring dashboard
        self._store_performance_data(request, request_time, query_count)
    
    def _analyze_slow_queries(self, request: HttpRequest, total_queries: int) -> None:
        """Analyze individual slow queries."""
        if not settings.DEBUG:
            return
        
        slow_queries = []
        critical_queries = []
        
        # Get queries from this request
        start_index = len(connection.queries) - total_queries
        request_queries = connection.queries[start_index:]
        
        for query in request_queries:
            query_time = float(query['time']) * 1000  # Convert to ms
            
            if query_time > self.CRITICAL_QUERY_THRESHOLD:
                critical_queries.append({
                    'sql': query['sql'],
                    'time': query_time,
                    'formatted_sql': self._format_sql(query['sql'])
                })
            elif query_time > self.SLOW_QUERY_THRESHOLD:
                slow_queries.append({
                    'sql': query['sql'],
                    'time': query_time,
                    'formatted_sql': self._format_sql(query['sql'])
                })
        
        # Log critical queries
        for query in critical_queries:
            logger.error(
                f'CRITICAL SLOW QUERY ({query["time"]:.2f}ms): {query["formatted_sql"]}'
            )
            self._suggest_optimization(query['sql'])
        
        # Log slow queries
        for query in slow_queries:
            logger.warning(
                f'Slow query ({query["time"]:.2f}ms): {query["formatted_sql"]}'
            )
    
    def _check_query_count(self, request: HttpRequest, query_count: int) -> None:
        """Check for excessive query counts (potential N+1 problems)."""
        if query_count > self.TOO_MANY_QUERIES_THRESHOLD:
            logger.error(
                f'TOO MANY QUERIES: {request.method} {request.get_full_path()} '
                f'executed {query_count} queries - possible N+1 problem!'
            )
            self._suggest_n_plus_one_fixes()
        elif query_count > 20:
            logger.warning(
                f'High query count: {request.method} {request.get_full_path()} '
                f'executed {query_count} queries'
            )
    
    def _format_sql(self, sql: str) -> str:
        """Format SQL for logging (truncate if too long)."""
        if len(sql) > 200:
            return sql[:200] + '...'
        return sql
    
    def _suggest_optimization(self, sql: str) -> None:
        """Suggest optimizations based on SQL patterns."""
        suggestions = []
        
        if 'SELECT *' in sql.upper():
            suggestions.append('Use .only() or .defer() to select specific fields')
        
        if sql.upper().count('SELECT') > 1 and 'JOIN' not in sql.upper():
            suggestions.append('Consider using select_related() or prefetch_related()')
        
        if 'ORDER BY' in sql.upper() and 'LIMIT' not in sql.upper():
            suggestions.append('Consider adding LIMIT to ORDER BY queries')
        
        if 'WHERE' not in sql.upper() and 'FROM core_' in sql:
            suggestions.append('Consider adding WHERE clauses to filter results')
        
        for suggestion in suggestions:
            logger.info(f'OPTIMIZATION SUGGESTION: {suggestion}')
    
    def _suggest_n_plus_one_fixes(self) -> None:
        """Suggest fixes for N+1 query problems."""
        suggestions = [
            'Use select_related() for foreign key relationships',
            'Use prefetch_related() for many-to-many or reverse foreign key relationships',
            'Consider using .only() to limit fields fetched',
            'Use database aggregation instead of Python loops',
            'Implement query caching for repeated data access'
        ]
        
        logger.info('N+1 QUERY FIXES:')
        for suggestion in suggestions:
            logger.info(f'  - {suggestion}')
    
    def _store_performance_data(self, request: HttpRequest, request_time: float, query_count: int) -> None:
        """Store performance data for monitoring dashboard."""
        try:
            # Create performance data entry
            perf_data = {
                'path': request.get_full_path(),
                'method': request.method,
                'request_time': request_time,
                'query_count': query_count,
                'timestamp': time.time(),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:100],
            }
            
            # Store in cache (keep last 100 requests)
            cache_key = 'db_performance_history'
            performance_history = cache.get(cache_key, [])
            
            performance_history.append(perf_data)
            
            # Keep only last 100 entries
            if len(performance_history) > 100:
                performance_history = performance_history[-100:]
            
            cache.set(cache_key, performance_history, 60 * 60)  # Cache for 1 hour
            
        except Exception as e:
            logger.error(f'Failed to store performance data: {e}')

class QueryCountDebugMiddleware(MiddlewareMixin):
    """
    Simple middleware to add query count to response headers in debug mode.
    """
    
    def process_request(self, request):
        if settings.DEBUG:
            request._queries_start = len(connection.queries)
    
    def process_response(self, request, response):
        if settings.DEBUG and hasattr(request, '_queries_start'):
            query_count = len(connection.queries) - request._queries_start
            response['X-Django-Query-Count'] = query_count
        return response

class CachePerformanceMiddleware(MiddlewareMixin):
    """
    Middleware to monitor cache performance and hit rates.
    """
    
    def process_request(self, request):
        if settings.DEBUG:
            request._cache_stats_start = self._get_cache_stats()
    
    def process_response(self, request, response):
        if settings.DEBUG and hasattr(request, '_cache_stats_start'):
            start_stats = request._cache_stats_start
            end_stats = self._get_cache_stats()
            
            # Calculate cache operations for this request
            cache_hits = end_stats.get('hits', 0) - start_stats.get('hits', 0)
            cache_misses = end_stats.get('misses', 0) - start_stats.get('misses', 0)
            
            if cache_hits + cache_misses > 0:
                hit_rate = (cache_hits / (cache_hits + cache_misses)) * 100
                response['X-Cache-Hits'] = str(cache_hits)
                response['X-Cache-Misses'] = str(cache_misses)
                response['X-Cache-Hit-Rate'] = f'{hit_rate:.1f}%'
        
        return response
    
    def _get_cache_stats(self):
        """Get cache statistics if available."""
        try:
            # This is a placeholder - implement based on your cache backend
            return {'hits': 0, 'misses': 0}
        except:
            return {'hits': 0, 'misses': 0}

def get_performance_summary():
    """
    Get performance summary from cached data.
    """
    cache_key = 'db_performance_history'
    performance_history = cache.get(cache_key, [])
    
    if not performance_history:
        return {
            'total_requests': 0,
            'avg_request_time': 0,
            'avg_query_count': 0,
            'slow_requests': 0,
            'high_query_requests': 0
        }
    
    total_requests = len(performance_history)
    total_time = sum(req['request_time'] for req in performance_history)
    total_queries = sum(req['query_count'] for req in performance_history)
    
    slow_requests = sum(1 for req in performance_history if req['request_time'] > 500)
    high_query_requests = sum(1 for req in performance_history if req['query_count'] > 20)
    
    return {
        'total_requests': total_requests,
        'avg_request_time': round(total_time / total_requests, 2),
        'avg_query_count': round(total_queries / total_requests, 2),
        'slow_requests': slow_requests,
        'high_query_requests': high_query_requests,
        'slow_request_percentage': round((slow_requests / total_requests) * 100, 2),
        'high_query_percentage': round((high_query_requests / total_requests) * 100, 2)
    }