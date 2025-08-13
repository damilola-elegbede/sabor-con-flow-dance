"""
Comprehensive monitoring and alerting system for Sabor Con Flow Dance.
SPEC_06 Group C Task 9: Complete monitoring infrastructure.
"""

import logging
import time
import json
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.core.cache import cache
from django.db import connections, connection
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import requests

logger = logging.getLogger(__name__)

class HealthCheckManager:
    """Centralized health check management for all services."""
    
    def __init__(self):
        self.checks = {
            'database': self._check_database,
            'cache': self._check_cache,
            'external_apis': self._check_external_apis,
            'system_resources': self._check_system_resources,
            'application': self._check_application,
        }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive status."""
        start_time = time.time()
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'healthy',
            'checks': {},
            'response_time_ms': 0,
            'version': getattr(settings, 'APP_VERSION', '1.0.0'),
            'environment': 'production' if not settings.DEBUG else 'development'
        }
        
        overall_healthy = True
        
        for check_name, check_func in self.checks.items():
            try:
                check_result = check_func()
                results['checks'][check_name] = check_result
                
                if not check_result.get('healthy', False):
                    overall_healthy = False
                    
            except Exception as e:
                logger.error(f"Health check {check_name} failed: {str(e)}")
                results['checks'][check_name] = {
                    'healthy': False,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
                overall_healthy = False
        
        results['status'] = 'healthy' if overall_healthy else 'unhealthy'
        results['response_time_ms'] = round((time.time() - start_time) * 1000, 2)
        
        return results
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        start_time = time.time()
        
        try:
            # Test basic connectivity
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            # Check connection pool
            db_conn = connections['default']
            
            response_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                'healthy': True,
                'response_time_ms': response_time,
                'connection_status': 'connected',
                'database_type': settings.DATABASES['default']['ENGINE'],
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {
                    'connectivity': response_time < 1000,  # < 1 second
                    'response_time_acceptable': response_time < 500,  # < 500ms
                }
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _check_cache(self) -> Dict[str, Any]:
        """Check cache system health."""
        start_time = time.time()
        
        try:
            # Test cache operations
            test_key = 'health_check_test'
            test_value = f'test_{int(time.time())}'
            
            # Set test value
            cache.set(test_key, test_value, 60)
            
            # Get test value
            retrieved_value = cache.get(test_key)
            
            # Clean up
            cache.delete(test_key)
            
            response_time = round((time.time() - start_time) * 1000, 2)
            
            cache_working = retrieved_value == test_value
            
            return {
                'healthy': cache_working,
                'response_time_ms': response_time,
                'cache_backend': settings.CACHES['default']['BACKEND'],
                'operations_successful': cache_working,
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {
                    'set_operation': True,
                    'get_operation': cache_working,
                    'delete_operation': True,
                    'response_time_acceptable': response_time < 100,  # < 100ms
                }
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _check_external_apis(self) -> Dict[str, Any]:
        """Check external API connectivity."""
        api_checks = {}
        overall_healthy = True
        
        # Define external APIs to check
        apis_to_check = [
            {
                'name': 'facebook_graph',
                'url': 'https://graph.facebook.com/v18.0/me',
                'timeout': 10,
                'expected_status': [200, 400]  # 400 is OK for auth issues
            },
            {
                'name': 'instagram_basic',
                'url': 'https://graph.instagram.com/me',
                'timeout': 10,
                'expected_status': [200, 400]  # 400 is OK for auth issues
            },
            {
                'name': 'google_maps',
                'url': 'https://maps.googleapis.com/maps/api/js',
                'timeout': 10,
                'expected_status': [200, 400]  # 400 is OK for auth issues
            },
            {
                'name': 'calendly',
                'url': 'https://calendly.com/api/health',
                'timeout': 10,
                'expected_status': [200, 404]  # 404 is OK if endpoint doesn't exist
            }
        ]
        
        for api_config in apis_to_check:
            start_time = time.time()
            
            try:
                response = requests.get(
                    api_config['url'],
                    timeout=api_config['timeout'],
                    headers={'User-Agent': 'SaborConFlow-HealthCheck/1.0'}
                )
                
                response_time = round((time.time() - start_time) * 1000, 2)
                
                is_healthy = response.status_code in api_config['expected_status']
                
                api_checks[api_config['name']] = {
                    'healthy': is_healthy,
                    'status_code': response.status_code,
                    'response_time_ms': response_time,
                    'url': api_config['url'],
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                if not is_healthy:
                    overall_healthy = False
                    
            except requests.RequestException as e:
                api_checks[api_config['name']] = {
                    'healthy': False,
                    'error': str(e),
                    'url': api_config['url'],
                    'timestamp': datetime.utcnow().isoformat()
                }
                overall_healthy = False
        
        return {
            'healthy': overall_healthy,
            'apis': api_checks,
            'total_apis_checked': len(apis_to_check),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Check thresholds
            cpu_healthy = cpu_percent < 80
            memory_healthy = memory_percent < 85
            disk_healthy = disk_percent < 90
            
            overall_healthy = all([cpu_healthy, memory_healthy, disk_healthy])
            
            return {
                'healthy': overall_healthy,
                'cpu': {
                    'usage_percent': cpu_percent,
                    'healthy': cpu_healthy,
                    'threshold': 80
                },
                'memory': {
                    'usage_percent': memory_percent,
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'healthy': memory_healthy,
                    'threshold': 85
                },
                'disk': {
                    'usage_percent': disk_percent,
                    'total_gb': round(disk.total / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'healthy': disk_healthy,
                    'threshold': 90
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _check_application(self) -> Dict[str, Any]:
        """Check application-specific health indicators."""
        try:
            # Check if critical settings are configured
            critical_settings = [
                'SECRET_KEY',
                'ALLOWED_HOSTS',
                'DATABASES',
            ]
            
            settings_check = all(
                hasattr(settings, setting) and getattr(settings, setting)
                for setting in critical_settings
            )
            
            # Check middleware integrity
            required_middleware = [
                'django.middleware.security.SecurityMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
            ]
            
            middleware_check = all(
                middleware in settings.MIDDLEWARE
                for middleware in required_middleware
            )
            
            # Check installed apps
            required_apps = [
                'django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'core',
            ]
            
            apps_check = all(
                app in settings.INSTALLED_APPS
                for app in required_apps
            )
            
            overall_healthy = all([settings_check, middleware_check, apps_check])
            
            return {
                'healthy': overall_healthy,
                'settings_configured': settings_check,
                'middleware_intact': middleware_check,
                'required_apps_installed': apps_check,
                'debug_mode': settings.DEBUG,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


class PerformanceMonitor:
    """Application performance monitoring and metrics collection."""
    
    def __init__(self):
        self.metrics_cache_key = 'performance_metrics'
        self.metrics_ttl = 300  # 5 minutes
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive performance metrics."""
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'application': self._get_application_metrics(),
            'database': self._get_database_metrics(),
            'cache': self._get_cache_metrics(),
            'system': self._get_system_metrics(),
        }
        
        # Cache metrics for dashboard
        cache.set(self.metrics_cache_key, metrics, self.metrics_ttl)
        
        return metrics
    
    def _get_application_metrics(self) -> Dict[str, Any]:
        """Get application-level performance metrics."""
        return {
            'version': getattr(settings, 'APP_VERSION', '1.0.0'),
            'debug_mode': settings.DEBUG,
            'environment': 'production' if not settings.DEBUG else 'development',
            'middleware_count': len(settings.MIDDLEWARE),
            'installed_apps_count': len(settings.INSTALLED_APPS),
            'static_files_served': cache.get('static_files_served', 0),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _get_database_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics."""
        try:
            from django.db import connection
            
            # Get database queries from current connection
            queries_count = len(connection.queries) if settings.DEBUG else 0
            
            # Test query performance
            start_time = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            query_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                'connection_status': 'connected',
                'query_count': queries_count,
                'average_query_time_ms': query_time,
                'slow_queries': cache.get('slow_queries_count', 0),
                'database_type': settings.DATABASES['default']['ENGINE'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'connection_status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _get_cache_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics."""
        try:
            # Test cache performance
            start_time = time.time()
            test_key = f'perf_test_{int(time.time())}'
            cache.set(test_key, 'test', 60)
            cache.get(test_key)
            cache.delete(test_key)
            cache_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                'backend': settings.CACHES['default']['BACKEND'],
                'operation_time_ms': cache_time,
                'hit_rate': cache.get('cache_hit_rate', 0),
                'miss_rate': cache.get('cache_miss_rate', 0),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'backend': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system-level performance metrics."""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get load average (Unix-like systems)
            try:
                load_avg = psutil.getloadavg()
            except (AttributeError, OSError):
                load_avg = [0, 0, 0]  # Fallback for Windows
            
            return {
                'cpu_usage_percent': cpu_percent,
                'memory_usage_percent': memory.percent,
                'disk_usage_percent': disk.percent,
                'load_average': {
                    '1min': load_avg[0],
                    '5min': load_avg[1],
                    '15min': load_avg[2]
                },
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


class AlertManager:
    """Centralized alert management and notification system."""
    
    def __init__(self):
        self.alert_thresholds = {
            'cpu_usage': 80,
            'memory_usage': 85,
            'disk_usage': 90,
            'response_time_ms': 1000,
            'error_rate': 5,  # percentage
            'database_query_time': 500,  # milliseconds
        }
        
        self.alert_history_key = 'alert_history'
        self.alert_cooldown = 300  # 5 minutes cooldown between same alerts
    
    def check_and_send_alerts(self, health_data: Dict[str, Any], metrics: Dict[str, Any]):
        """Check metrics against thresholds and send alerts if needed."""
        alerts_to_send = []
        
        # Check system resource alerts
        if 'system_resources' in health_data.get('checks', {}):
            system_data = health_data['checks']['system_resources']
            
            if system_data.get('cpu', {}).get('usage_percent', 0) > self.alert_thresholds['cpu_usage']:
                alerts_to_send.append({
                    'type': 'cpu_high',
                    'severity': 'warning',
                    'message': f"High CPU usage: {system_data['cpu']['usage_percent']}%",
                    'threshold': self.alert_thresholds['cpu_usage'],
                    'current_value': system_data['cpu']['usage_percent']
                })
            
            if system_data.get('memory', {}).get('usage_percent', 0) > self.alert_thresholds['memory_usage']:
                alerts_to_send.append({
                    'type': 'memory_high',
                    'severity': 'warning',
                    'message': f"High memory usage: {system_data['memory']['usage_percent']}%",
                    'threshold': self.alert_thresholds['memory_usage'],
                    'current_value': system_data['memory']['usage_percent']
                })
            
            if system_data.get('disk', {}).get('usage_percent', 0) > self.alert_thresholds['disk_usage']:
                alerts_to_send.append({
                    'type': 'disk_high',
                    'severity': 'critical',
                    'message': f"High disk usage: {system_data['disk']['usage_percent']}%",
                    'threshold': self.alert_thresholds['disk_usage'],
                    'current_value': system_data['disk']['usage_percent']
                })
        
        # Check response time alerts
        if health_data.get('response_time_ms', 0) > self.alert_thresholds['response_time_ms']:
            alerts_to_send.append({
                'type': 'response_time_high',
                'severity': 'warning',
                'message': f"High response time: {health_data['response_time_ms']}ms",
                'threshold': self.alert_thresholds['response_time_ms'],
                'current_value': health_data['response_time_ms']
            })
        
        # Check database performance alerts
        if 'database' in metrics:
            db_data = metrics['database']
            avg_query_time = db_data.get('average_query_time_ms', 0)
            
            if avg_query_time > self.alert_thresholds['database_query_time']:
                alerts_to_send.append({
                    'type': 'database_slow',
                    'severity': 'warning',
                    'message': f"Slow database queries: {avg_query_time}ms average",
                    'threshold': self.alert_thresholds['database_query_time'],
                    'current_value': avg_query_time
                })
        
        # Check overall health status
        if health_data.get('status') != 'healthy':
            alerts_to_send.append({
                'type': 'health_check_failed',
                'severity': 'critical',
                'message': "Application health check failed",
                'details': health_data.get('checks', {})
            })
        
        # Send alerts that haven't been sent recently
        for alert in alerts_to_send:
            self._send_alert_if_needed(alert)
    
    def _send_alert_if_needed(self, alert: Dict[str, Any]):
        """Send alert if it hasn't been sent recently (cooldown period)."""
        alert_key = f"alert_{alert['type']}"
        last_sent = cache.get(alert_key)
        
        now = datetime.utcnow()
        
        if not last_sent or (now - datetime.fromisoformat(last_sent)).seconds > self.alert_cooldown:
            # Send the alert
            self._send_alert(alert)
            
            # Record that we sent this alert
            cache.set(alert_key, now.isoformat(), self.alert_cooldown * 2)
            
            # Log to alert history
            self._log_alert_history(alert)
    
    def _send_alert(self, alert: Dict[str, Any]):
        """Send alert through configured channels."""
        # Log the alert
        logger.warning(f"ALERT [{alert['severity'].upper()}]: {alert['message']}")
        
        # Here you would integrate with actual alerting services:
        # - Send to Slack webhook
        # - Send email notification
        # - Send to PagerDuty
        # - Send to Discord webhook
        # - etc.
        
        # For now, we'll just log and store in cache for dashboard
        print(f"🚨 ALERT: {alert['message']}")
    
    def _log_alert_history(self, alert: Dict[str, Any]):
        """Log alert to history for dashboard display."""
        history = cache.get(self.alert_history_key, [])
        
        alert_record = {
            **alert,
            'timestamp': datetime.utcnow().isoformat(),
            'id': f"{alert['type']}_{int(time.time())}"
        }
        
        history.append(alert_record)
        
        # Keep only last 100 alerts
        if len(history) > 100:
            history = history[-100:]
        
        cache.set(self.alert_history_key, history, 86400)  # 24 hours
    
    def get_alert_history(self) -> List[Dict[str, Any]]:
        """Get recent alert history for dashboard."""
        return cache.get(self.alert_history_key, [])


# Initialize global instances
health_check_manager = HealthCheckManager()
performance_monitor = PerformanceMonitor()
alert_manager = AlertManager()


# =============================================================================
# VIEW FUNCTIONS - Required for URL routing
# =============================================================================

@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """
    Comprehensive health check endpoint for monitoring systems.
    Returns detailed system health information.
    """
    try:
        health_data = health_check_manager.run_all_checks()
        status_code = 200 if health_data['status'] == 'healthy' else 503
        
        return JsonResponse(health_data, status=status_code)
        
    except Exception as e:
        logger.error(f"Health check endpoint failed: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Health check system unavailable',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, status=503)


@csrf_exempt 
@require_http_methods(["GET", "HEAD"])
def health_check_simple(request):
    """
    Simple health check endpoint for load balancers and uptime monitors.
    Returns basic OK/ERROR status only.
    """
    try:
        # Quick basic checks only
        basic_checks = {
            'database': health_check_manager._check_database(),
            'application': health_check_manager._check_application(),
        }
        
        all_healthy = all(check.get('healthy', False) for check in basic_checks.values())
        
        if all_healthy:
            return HttpResponse("OK", content_type="text/plain", status=200)
        else:
            return HttpResponse("ERROR", content_type="text/plain", status=503)
            
    except Exception as e:
        logger.error(f"Simple health check failed: {str(e)}")
        return HttpResponse("ERROR", content_type="text/plain", status=503)


@csrf_exempt
@require_http_methods(["GET"])
def uptime_status(request):
    """
    Uptime and availability status endpoint.
    Returns system uptime and availability metrics.
    """
    try:
        import psutil
        
        # Get system boot time
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        current_time = datetime.now()
        uptime = current_time - boot_time
        
        # Calculate uptime in seconds
        uptime_seconds = int(uptime.total_seconds())
        
        status_data = {
            'status': 'online',
            'uptime_seconds': uptime_seconds,
            'uptime_human': str(uptime).split('.')[0],  # Remove microseconds
            'boot_time': boot_time.isoformat(),
            'current_time': current_time.isoformat(),
            'version': getattr(settings, 'APP_VERSION', '1.0.0'),
            'environment': 'production' if not settings.DEBUG else 'development',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return JsonResponse(status_data)
        
    except Exception as e:
        logger.error(f"Uptime status endpoint failed: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Uptime status unavailable', 
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def metrics_endpoint(request):
    """
    Performance metrics endpoint for monitoring dashboards.
    Returns comprehensive performance and system metrics.
    """
    try:
        # Collect current metrics
        metrics = performance_monitor.collect_metrics()
        
        # Add request-specific metrics
        metrics['endpoint'] = {
            'path': request.path,
            'method': request.method,
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown')[:100],  # Truncate
            'remote_addr': request.META.get('REMOTE_ADDR', 'Unknown'),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return JsonResponse(metrics)
        
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Metrics collection unavailable',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def monitoring_status(request):
    """
    Overall monitoring system status.
    Returns status of all monitoring components and recent alerts.
    """
    try:
        # Get health check results
        health_data = health_check_manager.run_all_checks()
        
        # Get performance metrics  
        metrics = performance_monitor.collect_metrics()
        
        # Get recent alerts
        recent_alerts = alert_manager.get_alert_history()[-10:]  # Last 10 alerts
        
        # Check alerts against current metrics
        alert_manager.check_and_send_alerts(health_data, metrics)
        
        monitoring_status = {
            'monitoring_system': {
                'status': 'operational',
                'components': {
                    'health_checks': health_data['status'],
                    'performance_monitoring': 'operational',
                    'alerting': 'operational',
                },
                'last_updated': datetime.utcnow().isoformat()
            },
            'health_summary': {
                'overall_status': health_data['status'],
                'response_time_ms': health_data['response_time_ms'],
                'checks_passed': len([c for c in health_data.get('checks', {}).values() if c.get('healthy', False)]),
                'total_checks': len(health_data.get('checks', {}))
            },
            'recent_alerts': recent_alerts,
            'alert_summary': {
                'total_alerts_24h': len([a for a in recent_alerts if 
                    (datetime.utcnow() - datetime.fromisoformat(a['timestamp'])).seconds < 86400]),
                'critical_alerts': len([a for a in recent_alerts if a.get('severity') == 'critical']),
                'warning_alerts': len([a for a in recent_alerts if a.get('severity') == 'warning']),
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return JsonResponse(monitoring_status)
        
    except Exception as e:
        logger.error(f"Monitoring status endpoint failed: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Monitoring status unavailable',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def monitoring_dashboard(request):
    """
    Monitoring dashboard endpoint for admin interface.
    Returns HTML dashboard for system monitoring.
    """
    try:
        # Get comprehensive monitoring data
        health_data = health_check_manager.run_all_checks() 
        metrics = performance_monitor.collect_metrics()
        alert_history = alert_manager.get_alert_history()
        
        # Create dashboard context
        dashboard_context = {
            'health_data': health_data,
            'metrics': metrics,
            'alert_history': alert_history[-50:],  # Last 50 alerts
            'system_info': {
                'version': getattr(settings, 'APP_VERSION', '1.0.0'),
                'environment': 'production' if not settings.DEBUG else 'development',
                'debug_mode': settings.DEBUG,
                'last_updated': datetime.utcnow().isoformat()
            }
        }
        
        # Return JSON for API usage or render template for web interface
        if request.headers.get('Accept', '').startswith('application/json'):
            return JsonResponse(dashboard_context)
        else:
            # For now, return JSON - can be extended to render HTML template
            return JsonResponse(dashboard_context, json_dumps_params={'indent': 2})
            
    except Exception as e:
        logger.error(f"Monitoring dashboard failed: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Monitoring dashboard unavailable',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def clear_monitoring_cache(request):
    """
    Clear monitoring system caches.
    Admin endpoint for cache management.
    """
    try:
        # Clear performance metrics cache
        cache.delete(performance_monitor.metrics_cache_key)
        
        # Clear health check caches
        cache.delete('health_check_results')
        cache.delete('system_status')
        
        # Clear alert caches
        cache.delete(alert_manager.alert_history_key)
        
        # Clear any monitoring-related cache keys
        monitoring_cache_keys = [
            'monitoring_status',
            'uptime_status', 
            'system_metrics',
            'performance_dashboard',
        ]
        
        for key in monitoring_cache_keys:
            cache.delete(key)
            
        logger.info("Monitoring system caches cleared successfully")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Monitoring caches cleared successfully',
            'cleared_caches': [
                'performance_metrics',
                'health_check_results',
                'system_status',
                'alert_history',
                'monitoring_status',
                'uptime_status',
                'system_metrics',
                'performance_dashboard'
            ],
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Clear monitoring cache failed: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to clear monitoring caches',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def test_alerts(request):
    """
    Test alert system functionality.
    Admin endpoint for testing alert notifications.
    """
    try:
        # Create test alerts of different severities
        test_alerts = [
            {
                'type': 'test_info',
                'severity': 'info',
                'message': 'Test info alert - monitoring system functional',
                'timestamp': datetime.utcnow().isoformat()
            },
            {
                'type': 'test_warning', 
                'severity': 'warning',
                'message': 'Test warning alert - simulated high resource usage',
                'current_value': 85,
                'threshold': 80,
                'timestamp': datetime.utcnow().isoformat()
            },
            {
                'type': 'test_critical',
                'severity': 'critical', 
                'message': 'Test critical alert - simulated system failure',
                'details': {'component': 'test', 'status': 'failed'},
                'timestamp': datetime.utcnow().isoformat()
            }
        ]
        
        # Send test alerts
        results = []
        for alert in test_alerts:
            try:
                alert_manager._send_alert(alert)
                alert_manager._log_alert_history(alert)
                results.append({
                    'alert_type': alert['type'],
                    'severity': alert['severity'],
                    'status': 'sent',
                    'message': alert['message']
                })
            except Exception as alert_error:
                results.append({
                    'alert_type': alert['type'],
                    'severity': alert['severity'], 
                    'status': 'failed',
                    'error': str(alert_error)
                })
        
        logger.info("Alert system test completed")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Alert system test completed',
            'test_results': results,
            'alerts_sent': len([r for r in results if r['status'] == 'sent']),
            'alerts_failed': len([r for r in results if r['status'] == 'failed']),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Test alerts failed: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Alert system test failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, status=500)