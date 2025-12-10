"""
Monitoring middleware for comprehensive application monitoring.
SPEC_06 Group C Task 9: Monitoring and alerting implementation.
"""

import time
import logging
import json
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import sentry_sdk

logger = logging.getLogger(__name__)

class MonitoringMiddleware(MiddlewareMixin):
    """
    Comprehensive monitoring middleware that tracks:
    - Request/response times
    - Error rates
    - Resource usage
    - Performance metrics
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enable_monitoring = getattr(settings, 'ENABLE_MONITORING', True)
        # Django 4.2+ compatibility
        self.async_mode = False
        
    def process_request(self, request):
        """Track request start time and metadata."""
        if not self.enable_monitoring:
            return None
            
        # Record request start time
        request._monitoring_start_time = time.time()
        request._monitoring_start_datetime = datetime.utcnow()
        
        # Track request metadata
        request._monitoring_metadata = {
            'method': request.method,
            'path': request.path,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'remote_addr': self._get_client_ip(request),
            'content_type': request.META.get('CONTENT_TYPE', ''),
            'content_length': request.META.get('CONTENT_LENGTH', 0),
        }
        
        # Increment request counter
        self._increment_counter('total_requests')
        self._increment_counter(f'requests_{request.method.lower()}')
        
        return None
    
    def process_response(self, request, response):
        """Track response metrics and performance."""
        if not self.enable_monitoring or not hasattr(request, '_monitoring_start_time'):
            return response
        
        # Calculate response time
        response_time = (time.time() - request._monitoring_start_time) * 1000  # Convert to milliseconds
        
        # Record metrics
        self._record_response_metrics(request, response, response_time)
        
        # Check for performance alerts
        self._check_performance_alerts(request, response, response_time)
        
        # Add monitoring headers (in development)
        if settings.DEBUG:
            response['X-Response-Time'] = f'{response_time:.2f}ms'
            response['X-Monitoring-Timestamp'] = request._monitoring_start_datetime.isoformat()
        
        return response
    
    def process_exception(self, request, exception):
        """Track exceptions and errors."""
        if not self.enable_monitoring:
            return None
        
        # Increment error counters
        self._increment_counter('total_errors')
        self._increment_counter(f'errors_{exception.__class__.__name__}')
        
        # Log error details
        error_data = {
            'exception_type': exception.__class__.__name__,
            'exception_message': str(exception),
            'request_path': request.path,
            'request_method': request.method,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'remote_addr': self._get_client_ip(request),
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        logger.error(f"Exception in monitoring: {error_data}")
        
        # Send to Sentry with additional context
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("component", "monitoring_middleware")
            scope.set_context("request_details", error_data)
            sentry_sdk.capture_exception(exception)
        
        # Check for error rate alerts
        self._check_error_rate_alerts()
        
        return None
    
    def _record_response_metrics(self, request, response, response_time):
        """Record detailed response metrics."""
        # Basic metrics
        metrics = {
            'response_time_ms': response_time,
            'status_code': response.status_code,
            'content_length': len(response.content) if hasattr(response, 'content') else 0,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        # Increment status code counters
        self._increment_counter(f'status_{response.status_code}')
        
        if 200 <= response.status_code < 300:
            self._increment_counter('successful_responses')
        elif 400 <= response.status_code < 500:
            self._increment_counter('client_errors')
        elif 500 <= response.status_code:
            self._increment_counter('server_errors')
        
        # Update response time statistics
        self._update_response_time_stats(response_time)
        
        # Store recent metrics for dashboard
        recent_metrics = cache.get('recent_metrics', [])
        recent_metrics.append({
            **metrics,
            'path': request.path,
            'method': request.method,
        })
        
        # Keep only last 100 metrics
        if len(recent_metrics) > 100:
            recent_metrics = recent_metrics[-100:]
        
        cache.set('recent_metrics', recent_metrics, 3600)  # 1 hour
    
    def _update_response_time_stats(self, response_time):
        """Update response time statistics."""
        # Get current stats
        stats = cache.get('response_time_stats', {
            'count': 0,
            'sum': 0,
            'min': float('inf'),
            'max': 0,
            'avg': 0,
        })
        
        # Update stats
        stats['count'] += 1
        stats['sum'] += response_time
        stats['min'] = min(stats['min'], response_time)
        stats['max'] = max(stats['max'], response_time)
        stats['avg'] = stats['sum'] / stats['count']
        
        # Reset min if it's infinity
        if stats['min'] == float('inf'):
            stats['min'] = response_time
        
        cache.set('response_time_stats', stats, 3600)  # 1 hour
    
    def _check_performance_alerts(self, request, response, response_time):
        """Check if performance thresholds are exceeded."""
        thresholds = getattr(settings, 'PERFORMANCE_THRESHOLDS', {})
        
        # Check response time thresholds
        warning_threshold = thresholds.get('response_time_warning', 1000)
        critical_threshold = thresholds.get('response_time_critical', 3000)
        
        if response_time > critical_threshold:
            self._send_alert({
                'type': 'response_time_critical',
                'severity': 'critical',
                'message': f'Critical response time: {response_time:.2f}ms on {request.path}',
                'threshold': critical_threshold,
                'current_value': response_time,
                'path': request.path,
                'method': request.method,
            })
        elif response_time > warning_threshold:
            self._send_alert({
                'type': 'response_time_warning',
                'severity': 'warning',
                'message': f'Slow response time: {response_time:.2f}ms on {request.path}',
                'threshold': warning_threshold,
                'current_value': response_time,
                'path': request.path,
                'method': request.method,
            })
    
    def _check_error_rate_alerts(self):
        """Check if error rate exceeds thresholds."""
        # Get recent error counts
        total_requests = cache.get('counter_total_requests', 0)
        total_errors = cache.get('counter_total_errors', 0)
        
        if total_requests == 0:
            return
        
        error_rate = (total_errors / total_requests) * 100
        
        thresholds = getattr(settings, 'PERFORMANCE_THRESHOLDS', {})
        warning_threshold = thresholds.get('error_rate_warning', 5.0)
        critical_threshold = thresholds.get('error_rate_critical', 10.0)
        
        if error_rate > critical_threshold:
            self._send_alert({
                'type': 'error_rate_critical',
                'severity': 'critical',
                'message': f'Critical error rate: {error_rate:.2f}%',
                'threshold': critical_threshold,
                'current_value': error_rate,
                'total_requests': total_requests,
                'total_errors': total_errors,
            })
        elif error_rate > warning_threshold:
            self._send_alert({
                'type': 'error_rate_warning',
                'severity': 'warning',
                'message': f'High error rate: {error_rate:.2f}%',
                'threshold': warning_threshold,
                'current_value': error_rate,
                'total_requests': total_requests,
                'total_errors': total_errors,
            })
    
    def _send_alert(self, alert_data):
        """Send alert through configured channels."""
        # Add timestamp
        alert_data['timestamp'] = datetime.utcnow().isoformat()
        
        # Log the alert
        logger.warning(f"PERFORMANCE ALERT: {alert_data['message']}")
        
        # Send to Sentry
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("alert_type", alert_data['type'])
            scope.set_tag("severity", alert_data['severity'])
            scope.set_context("alert_details", alert_data)
            
            if alert_data['severity'] == 'critical':
                sentry_sdk.capture_message(alert_data['message'], level='error')
            else:
                sentry_sdk.capture_message(alert_data['message'], level='warning')
        
        # Store alert for dashboard
        alerts = cache.get('recent_alerts', [])
        alerts.append(alert_data)
        
        # Keep only last 50 alerts
        if len(alerts) > 50:
            alerts = alerts[-50:]
        
        cache.set('recent_alerts', alerts, 86400)  # 24 hours
    
    def _increment_counter(self, counter_name):
        """Increment a counter in cache."""
        key = f'counter_{counter_name}'
        try:
            current_value = cache.get(key, 0)
            cache.set(key, current_value + 1, 3600)  # 1 hour TTL
        except Exception as e:
            logger.error(f"Failed to increment counter {counter_name}: {e}")
    
    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class HealthCheckCacheMiddleware(MiddlewareMixin):
    """
    Middleware to cache health check responses for performance.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.health_check_paths = ['/health/', '/health', '/api/health/', '/api/health']
        # Django 4.2+ compatibility
        self.async_mode = False
        
    def process_request(self, request):
        """Check if this is a health check request and return cached response if available."""
        if request.path in self.health_check_paths and request.method == 'GET':
            # Check for cached health check response
            cache_key = f'health_check_response_{request.path}'
            cached_response = cache.get(cache_key)
            
            if cached_response:
                # Return cached response
                response = JsonResponse(cached_response)
                response['X-Cache'] = 'HIT'
                return response
        
        return None
    
    def process_response(self, request, response):
        """Cache health check responses."""
        if (request.path in self.health_check_paths and 
            request.method == 'GET' and 
            response.status_code == 200):
            
            try:
                # Cache the response data
                cache_key = f'health_check_response_{request.path}'
                ttl = getattr(settings, 'HEALTH_CHECK_CACHE_TTL', 60)
                
                if hasattr(response, 'content'):
                    response_data = json.loads(response.content.decode('utf-8'))
                    cache.set(cache_key, response_data, ttl)
                    response['X-Cache'] = 'MISS'
                
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Failed to cache health check response: {e}")
        
        return response


# Import additional middleware classes from the main middleware.py file
import logging
from django.conf import settings
from django.db import connection
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

logger = logging.getLogger(__name__)

class DatabasePerformanceMiddleware(MiddlewareMixin):
    """
    Middleware to monitor database performance and log slow queries.
    """
    
    # Performance thresholds (in milliseconds)
    SLOW_QUERY_THRESHOLD = 100
    CRITICAL_QUERY_THRESHOLD = 500
    
    def process_request(self, request):
        if settings.DEBUG:
            request._db_queries_start = len(connection.queries)
    
    def process_response(self, request, response):
        if settings.DEBUG and hasattr(request, '_db_queries_start'):
            query_count = len(connection.queries) - request._db_queries_start
            
            # Calculate total query time
            start_index = len(connection.queries) - query_count
            request_queries = connection.queries[start_index:]
            total_time = sum(float(query['time']) * 1000 for query in request_queries)
            
            # Log performance metrics
            if total_time > self.CRITICAL_QUERY_THRESHOLD:
                logger.error(f'CRITICAL DB PERFORMANCE: {request.method} {request.path} - {total_time:.2f}ms, {query_count} queries')
            elif total_time > self.SLOW_QUERY_THRESHOLD:
                logger.warning(f'Slow DB performance: {request.method} {request.path} - {total_time:.2f}ms, {query_count} queries')
            
            # Add headers for debugging
            response['X-DB-Query-Count'] = query_count
            response['X-DB-Query-Time'] = f'{total_time:.2f}ms'
        
        return response

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