# Import middleware classes to make them available at package level
from .monitoring import (
    DatabasePerformanceMiddleware, 
    QueryCountDebugMiddleware,
    MonitoringMiddleware,
    HealthCheckCacheMiddleware
)

# Create stub classes for missing middleware to prevent import errors
from django.utils.deprecation import MiddlewareMixin

class PerformanceMiddleware(MiddlewareMixin):
    """Stub middleware - implement as needed"""
    pass

class CacheControlMiddleware(MiddlewareMixin):
    """Stub middleware - implement as needed"""
    pass

class ETagMiddleware(MiddlewareMixin):
    """Stub middleware - implement as needed"""
    pass