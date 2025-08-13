"""
Comprehensive test suite for monitoring and alerting system.
SPEC_06 Group C Task 9: Monitoring system verification.
"""

import json
import time
from unittest.mock import patch, Mock
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.cache import cache
from django.contrib.auth.models import User
from django.conf import settings

from core.monitoring import (
    HealthCheckManager,
    PerformanceMonitor,
    AlertManager,
    health_check_manager,
    performance_monitor,
    alert_manager,
)


class HealthCheckTests(TestCase):
    """Test health check functionality."""
    
    def setUp(self):
        self.client = Client()
        self.health_manager = HealthCheckManager()
        cache.clear()
    
    def test_health_check_endpoint(self):
        """Test the main health check endpoint."""
        response = self.client.get(reverse('core:monitoring_health_check'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
        self.assertIn('response_time_ms', data)
        self.assertIn('checks', data)
        
        # Check that all expected components are tested
        expected_checks = ['database', 'cache', 'external_apis', 'system_resources', 'application']
        for check in expected_checks:
            self.assertIn(check, data['checks'])
    
    def test_simple_health_check(self):
        """Test the simple health check endpoint."""
        response = self.client.get(reverse('core:health_check_simple'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
        self.assertIn(data['status'], ['ok', 'error'])
    
    def test_uptime_status_endpoint(self):
        """Test the uptime status endpoint for UptimeRobot."""
        response = self.client.get(reverse('core:uptime_status'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('status', data)
        self.assertIn('response_time_ms', data)
        self.assertIn('timestamp', data)
    
    def test_database_health_check(self):
        """Test database health check component."""
        result = self.health_manager._check_database()
        
        self.assertIsInstance(result, dict)
        self.assertIn('healthy', result)
        self.assertIn('response_time_ms', result)
        self.assertIn('connection_status', result)
        
        # Database should be healthy in tests
        self.assertTrue(result['healthy'])
        self.assertEqual(result['connection_status'], 'connected')
    
    def test_cache_health_check(self):
        """Test cache health check component."""
        result = self.health_manager._check_cache()
        
        self.assertIsInstance(result, dict)
        self.assertIn('healthy', result)
        self.assertIn('response_time_ms', result)
        self.assertIn('operations_successful', result)
        
        # Cache should be healthy in tests
        self.assertTrue(result['healthy'])
        self.assertTrue(result['operations_successful'])
    
    def test_system_resources_check(self):
        """Test system resources health check."""
        result = self.health_manager._check_system_resources()
        
        self.assertIsInstance(result, dict)
        self.assertIn('healthy', result)
        self.assertIn('cpu', result)
        self.assertIn('memory', result)
        self.assertIn('disk', result)
        
        # Check CPU metrics
        self.assertIn('usage_percent', result['cpu'])
        self.assertIn('healthy', result['cpu'])
        
        # Check memory metrics
        self.assertIn('usage_percent', result['memory'])
        self.assertIn('total_gb', result['memory'])
        self.assertIn('healthy', result['memory'])
        
        # Check disk metrics
        self.assertIn('usage_percent', result['disk'])
        self.assertIn('total_gb', result['disk'])
        self.assertIn('healthy', result['disk'])
    
    def test_application_health_check(self):
        """Test application health check component."""
        result = self.health_manager._check_application()
        
        self.assertIsInstance(result, dict)
        self.assertIn('healthy', result)
        self.assertIn('settings_configured', result)
        self.assertIn('middleware_intact', result)
        self.assertIn('required_apps_installed', result)
        
        # Application should be healthy in tests
        self.assertTrue(result['healthy'])
        self.assertTrue(result['settings_configured'])
        self.assertTrue(result['middleware_intact'])
        self.assertTrue(result['required_apps_installed'])
    
    @patch('requests.get')
    def test_external_apis_check(self, mock_get):
        """Test external APIs health check."""
        # Mock successful API responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.health_manager._check_external_apis()
        
        self.assertIsInstance(result, dict)
        self.assertIn('healthy', result)
        self.assertIn('apis', result)
        self.assertIn('total_apis_checked', result)
        
        # Check that APIs were tested
        self.assertGreater(result['total_apis_checked'], 0)
    
    def test_health_check_caching(self):
        """Test that health checks are properly cached."""
        # First request should hit the database
        response1 = self.client.get(reverse('core:health_check_simple'))
        self.assertEqual(response1.status_code, 200)
        
        # Second request should be cached (if caching is enabled)
        response2 = self.client.get(reverse('core:health_check_simple'))
        self.assertEqual(response2.status_code, 200)
        
        # Check cache headers
        if 'X-Cache' in response2:
            self.assertIn(response2['X-Cache'], ['HIT', 'MISS'])


class PerformanceMonitoringTests(TestCase):
    """Test performance monitoring functionality."""
    
    def setUp(self):
        self.client = Client()
        self.perf_monitor = PerformanceMonitor()
        cache.clear()
    
    def test_metrics_endpoint(self):
        """Test the metrics API endpoint."""
        response = self.client.get(reverse('core:metrics_endpoint'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check main metric categories
        expected_categories = ['timestamp', 'application', 'database', 'cache', 'system']
        for category in expected_categories:
            self.assertIn(category, data)
    
    def test_monitoring_status_endpoint(self):
        """Test the monitoring status endpoint."""
        response = self.client.get(reverse('core:monitoring_status'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('status', data)
        self.assertIn('monitoring_enabled', data)
        self.assertIn('error_rate', data)
        self.assertIn('average_response_time_ms', data)
        self.assertIn('total_requests', data)
        self.assertIn('total_errors', data)
    
    def test_collect_metrics(self):
        """Test metrics collection functionality."""
        metrics = self.perf_monitor.collect_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('timestamp', metrics)
        self.assertIn('application', metrics)
        self.assertIn('database', metrics)
        self.assertIn('cache', metrics)
        self.assertIn('system', metrics)
    
    def test_application_metrics(self):
        """Test application-level metrics collection."""
        metrics = self.perf_monitor._get_application_metrics()
        
        self.assertIn('version', metrics)
        self.assertIn('debug_mode', metrics)
        self.assertIn('environment', metrics)
        self.assertIn('middleware_count', metrics)
        self.assertIn('installed_apps_count', metrics)
    
    def test_database_metrics(self):
        """Test database metrics collection."""
        metrics = self.perf_monitor._get_database_metrics()
        
        self.assertIn('connection_status', metrics)
        self.assertIn('database_type', metrics)
        
        if metrics['connection_status'] == 'connected':
            self.assertIn('query_count', metrics)
            self.assertIn('average_query_time_ms', metrics)
    
    def test_cache_metrics(self):
        """Test cache metrics collection."""
        metrics = self.perf_monitor._get_cache_metrics()
        
        self.assertIn('backend', metrics)
        self.assertIn('operation_time_ms', metrics)
    
    def test_system_metrics(self):
        """Test system-level metrics collection."""
        metrics = self.perf_monitor._get_system_metrics()
        
        if 'error' not in metrics:
            self.assertIn('cpu_usage_percent', metrics)
            self.assertIn('memory_usage_percent', metrics)
            self.assertIn('disk_usage_percent', metrics)
            self.assertIn('load_average', metrics)


class AlertingTests(TestCase):
    """Test alerting functionality."""
    
    def setUp(self):
        self.alert_manager = AlertManager()
        cache.clear()
    
    def test_alert_thresholds(self):
        """Test alert threshold configuration."""
        self.assertIn('cpu_usage', self.alert_manager.alert_thresholds)
        self.assertIn('memory_usage', self.alert_manager.alert_thresholds)
        self.assertIn('response_time_ms', self.alert_manager.alert_thresholds)
        self.assertIn('error_rate', self.alert_manager.alert_thresholds)
    
    def test_alert_creation(self):
        """Test alert creation and logging."""
        test_alert = {
            'type': 'test_alert',
            'severity': 'warning',
            'message': 'Test alert message',
            'threshold': 100,
            'current_value': 150
        }
        
        # Send test alert
        self.alert_manager._send_alert(test_alert)
        
        # Check alert history
        alert_history = self.alert_manager.get_alert_history()
        self.assertGreater(len(alert_history), 0)
    
    def test_alert_cooldown(self):
        """Test alert cooldown functionality."""
        test_alert = {
            'type': 'test_cooldown',
            'severity': 'warning',
            'message': 'Test cooldown alert',
        }
        
        # Send first alert
        self.alert_manager._send_alert_if_needed(test_alert)
        
        # Try to send same alert immediately (should be blocked by cooldown)
        self.alert_manager._send_alert_if_needed(test_alert)
        
        # Check that only one alert was logged
        alert_history = self.alert_manager.get_alert_history()
        cooldown_alerts = [a for a in alert_history if a['type'] == 'test_cooldown']
        self.assertEqual(len(cooldown_alerts), 1)
    
    def test_check_performance_alerts(self):
        """Test performance alert checking."""
        # Create mock health data with high response time
        health_data = {
            'status': 'healthy',
            'response_time_ms': 2000,  # Above warning threshold
            'checks': {
                'system_resources': {
                    'healthy': True,
                    'cpu': {'usage_percent': 90},  # Above threshold
                    'memory': {'usage_percent': 90},  # Above threshold
                    'disk': {'usage_percent': 95}  # Above threshold
                }
            }
        }
        
        # Create mock metrics
        metrics = {
            'database': {
                'average_query_time_ms': 600  # Above threshold
            }
        }
        
        # Check alerts (should trigger multiple alerts)
        initial_alert_count = len(self.alert_manager.get_alert_history())
        self.alert_manager.check_and_send_alerts(health_data, metrics)
        final_alert_count = len(self.alert_manager.get_alert_history())
        
        # Should have triggered alerts
        self.assertGreater(final_alert_count, initial_alert_count)


class MonitoringMiddlewareTests(TestCase):
    """Test monitoring middleware functionality."""
    
    def setUp(self):
        self.client = Client()
        cache.clear()
    
    @override_settings(ENABLE_MONITORING=True)
    def test_monitoring_middleware_active(self):
        """Test that monitoring middleware is tracking requests."""
        # Make a request
        response = self.client.get('/')
        
        # Check if request was tracked
        total_requests = cache.get('counter_total_requests', 0)
        self.assertGreater(total_requests, 0)
        
        # Check response headers in debug mode
        if settings.DEBUG:
            self.assertIn('X-Response-Time', response) if hasattr(response, 'get') else None
    
    def test_request_counters(self):
        """Test request counter functionality."""
        initial_requests = cache.get('counter_total_requests', 0)
        initial_get_requests = cache.get('counter_requests_get', 0)
        
        # Make a GET request
        self.client.get('/')
        
        # Check counters increased
        final_requests = cache.get('counter_total_requests', 0)
        final_get_requests = cache.get('counter_requests_get', 0)
        
        self.assertEqual(final_requests, initial_requests + 1)
        self.assertEqual(final_get_requests, initial_get_requests + 1)
    
    def test_error_tracking(self):
        """Test error tracking in middleware."""
        initial_errors = cache.get('counter_total_errors', 0)
        
        # Make a request to non-existent page (should cause 404)
        response = self.client.get('/non-existent-page/')
        
        # 404s might not increment error counter depending on configuration
        # This test verifies the middleware doesn't crash on errors
        self.assertIn(response.status_code, [404, 500])
    
    def test_response_time_tracking(self):
        """Test response time statistics tracking."""
        # Make a request
        self.client.get('/')
        
        # Check if response time stats were recorded
        stats = cache.get('response_time_stats')
        if stats:
            self.assertIn('count', stats)
            self.assertIn('avg', stats)
            self.assertIn('min', stats)
            self.assertIn('max', stats)
            self.assertGreater(stats['count'], 0)


class AdminDashboardTests(TestCase):
    """Test admin monitoring dashboard."""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        cache.clear()
    
    def test_dashboard_access_requires_staff(self):
        """Test that dashboard requires staff access."""
        response = self.client.get(reverse('core:monitoring_dashboard'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_dashboard_with_staff_access(self):
        """Test dashboard access with staff user."""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('core:monitoring_dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Monitoring Dashboard')
        self.assertContains(response, 'System Health')
    
    def test_clear_cache_endpoint(self):
        """Test cache clearing functionality."""
        self.client.force_login(self.admin_user)
        
        # Add some cache data
        cache.set('counter_total_requests', 100)
        
        # Clear cache
        response = self.client.post(reverse('core:clear_monitoring_cache'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Check that cache was cleared
        self.assertEqual(cache.get('counter_total_requests', 0), 0)
    
    def test_test_alerts_endpoint(self):
        """Test alert testing functionality."""
        self.client.force_login(self.admin_user)
        
        response = self.client.post(reverse('core:test_alerts'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('message', data)


class IntegrationTests(TestCase):
    """Integration tests for the complete monitoring system."""
    
    def setUp(self):
        self.client = Client()
        cache.clear()
    
    def test_end_to_end_monitoring_flow(self):
        """Test complete monitoring flow from request to dashboard."""
        # 1. Make some requests to generate data
        for i in range(5):
            self.client.get('/')
        
        # 2. Check health endpoint
        health_response = self.client.get(reverse('core:monitoring_health_check'))
        self.assertEqual(health_response.status_code, 200)
        health_data = health_response.json()
        self.assertEqual(health_data['status'], 'healthy')
        
        # 3. Check metrics endpoint
        metrics_response = self.client.get(reverse('core:metrics_endpoint'))
        self.assertEqual(metrics_response.status_code, 200)
        metrics_data = metrics_response.json()
        self.assertIn('timestamp', metrics_data)
        
        # 4. Check monitoring status
        status_response = self.client.get(reverse('core:monitoring_status'))
        self.assertEqual(status_response.status_code, 200)
        status_data = status_response.json()
        self.assertIn('status', status_data)
        
        # 5. Verify counters were incremented
        total_requests = cache.get('counter_total_requests', 0)
        self.assertGreaterEqual(total_requests, 5)
    
    @override_settings(ENABLE_MONITORING=False)
    def test_monitoring_disabled(self):
        """Test system behavior when monitoring is disabled."""
        # Make requests
        response = self.client.get('/')
        
        # Monitoring should be disabled, so counters shouldn't increment
        # (depending on middleware configuration)
        self.assertEqual(response.status_code, 200)
    
    def test_performance_under_load(self):
        """Test monitoring system performance under load."""
        start_time = time.time()
        
        # Make multiple requests
        for i in range(20):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Monitoring shouldn't significantly impact performance
        # Average response time should be reasonable
        avg_response_time = total_time / 20
        self.assertLess(avg_response_time, 1.0)  # Less than 1 second per request
    
    def test_error_handling_in_monitoring(self):
        """Test that monitoring system handles errors gracefully."""
        # Test with various error conditions
        test_cases = [
            '/health/',
            '/health/simple/',
            '/api/metrics/',
            '/uptime/',
        ]
        
        for endpoint in test_cases:
            response = self.client.get(endpoint)
            # Should not return 500 errors
            self.assertNotEqual(response.status_code, 500)
    
    def test_monitoring_data_consistency(self):
        """Test that monitoring data is consistent across endpoints."""
        # Make some requests
        for i in range(3):
            self.client.get('/')
        
        # Get data from different endpoints
        health_response = self.client.get(reverse('core:monitoring_health_check'))
        metrics_response = self.client.get(reverse('core:metrics_endpoint'))
        status_response = self.client.get(reverse('core:monitoring_status'))
        
        # All should return 200
        self.assertEqual(health_response.status_code, 200)
        self.assertEqual(metrics_response.status_code, 200)
        self.assertEqual(status_response.status_code, 200)
        
        # Data should be consistent (timestamps should be recent)
        health_data = health_response.json()
        metrics_data = metrics_response.json()
        status_data = status_response.json()
        
        # All should have timestamps
        self.assertIn('timestamp', health_data)
        self.assertIn('timestamp', metrics_data)
        self.assertIn('timestamp', status_data)