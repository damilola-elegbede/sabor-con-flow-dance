"""
Test suite for SPEC_04 Group D - Performance Features Implementation

Tests:
- Image optimization utilities
- Performance monitoring endpoints
- Core Web Vitals analysis
- Service Worker functionality
- Image optimization management command
- Performance dashboard data
- Caching and optimization strategies
"""

import os
import json
import tempfile
from unittest.mock import patch, Mock, mock_open
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.management import call_command
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from io import StringIO, BytesIO
from PIL import Image

from core.utils.image_optimizer import (
    ImageOptimizer, optimize_static_image, get_responsive_srcset,
    batch_optimize_static_images
)
from core.management.commands.optimize_images import Command as OptimizeImagesCommand


class ImageOptimizerTests(TestCase):
    """Test the ImageOptimizer utility class."""
    
    def setUp(self):
        """Set up test data."""
        self.optimizer = ImageOptimizer()
        cache.clear()
        
        # Create a temporary test image
        self.test_image = Image.new('RGB', (800, 600), color='red')
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, 'test_image.jpg')
        self.test_image.save(self.test_image_path, 'JPEG', quality=95)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_optimizer_initialization(self):
        """Test ImageOptimizer initialization."""
        optimizer = ImageOptimizer()
        
        # Check optimization levels
        self.assertIn('high', optimizer.optimization_levels)
        self.assertIn('medium', optimizer.optimization_levels)
        self.assertIn('low', optimizer.optimization_levels)
        
        # Check quality settings
        self.assertEqual(optimizer.webp_quality, 80)
        self.assertEqual(optimizer.avif_quality, 70)
    
    def test_optimization_levels(self):
        """Test different optimization levels."""
        levels = self.optimizer.optimization_levels
        
        # High optimization
        high = levels['high']
        self.assertEqual(high['quality'], 85)
        self.assertTrue(high['optimize'])
        self.assertTrue(high['progressive'])
        
        # Medium optimization
        medium = levels['medium']
        self.assertEqual(medium['quality'], 90)
        self.assertTrue(medium['optimize'])
        self.assertTrue(medium['progressive'])
        
        # Low optimization
        low = levels['low']
        self.assertEqual(low['quality'], 95)
        self.assertFalse(low['optimize'])
        self.assertFalse(low['progressive'])
    
    @patch('core.utils.image_optimizer.Image.open')
    @patch('os.path.exists')
    def test_optimize_image_not_found(self, mock_exists, mock_open):
        """Test optimize_image with non-existent file."""
        mock_exists.return_value = False
        
        result = self.optimizer.optimize_image('/fake/path/image.jpg')
        self.assertIsNone(result)
    
    def test_optimize_image_basic(self):
        """Test basic image optimization."""
        result = self.optimizer.optimize_image(
            self.test_image_path,
            optimization_level='medium',
            generate_webp=False,
            generate_sizes=False
        )
        
        self.assertIsNotNone(result)
        self.assertIn('original', result)
        self.assertIn('optimized', result)
        
        # Check original info
        original = result['original']
        self.assertEqual(original['path'], self.test_image_path)
        self.assertGreater(original['size'], 0)
        self.assertEqual(original['dimensions'], (800, 600))
        
        # Check optimized info
        optimized = result['optimized']
        self.assertIsNotNone(optimized['path'])
        self.assertGreater(optimized['size'], 0)
        self.assertGreaterEqual(optimized['savings'], 0)
        self.assertEqual(optimized['dimensions'], (800, 600))
    
    def test_optimize_image_with_webp(self):
        """Test image optimization with WebP generation."""
        result = self.optimizer.optimize_image(
            self.test_image_path,
            optimization_level='medium',
            generate_webp=True,
            generate_sizes=False
        )
        
        self.assertIsNotNone(result)
        self.assertIn('webp', result)
        
        webp = result['webp']
        self.assertIsNotNone(webp['path'])
        self.assertGreater(webp['size'], 0)
        self.assertGreaterEqual(webp['savings'], 0)
        self.assertEqual(webp['dimensions'], (800, 600))
        
        # WebP should generally be smaller than original
        self.assertLess(webp['size'], result['original']['size'])
    
    def test_optimize_image_with_responsive_sizes(self):
        """Test image optimization with responsive sizes."""
        result = self.optimizer.optimize_image(
            self.test_image_path,
            optimization_level='medium',
            generate_webp=False,
            generate_sizes=True
        )
        
        self.assertIsNotNone(result)
        self.assertIn('responsive_sizes', result)
        
        responsive = result['responsive_sizes']
        
        # Should generate sizes smaller than original (800x600)
        expected_sizes = ['small', 'medium']  # 320 and 640 width
        for size_name in expected_sizes:
            if size_name in responsive:
                size_data = responsive[size_name]
                self.assertIn('optimized', size_data)
                self.assertIn('webp', size_data)
                
                # Check dimensions are scaled properly
                dims = size_data['optimized']['dimensions']
                if size_name == 'small':
                    self.assertEqual(dims[0], 320)
                elif size_name == 'medium':
                    self.assertEqual(dims[0], 640)
    
    def test_optimize_image_caching(self):
        """Test image optimization result caching."""
        # First optimization
        result1 = self.optimizer.optimize_image(
            self.test_image_path,
            optimization_level='medium',
            generate_webp=False,
            generate_sizes=False
        )
        
        # Second optimization should use cache
        result2 = self.optimizer.optimize_image(
            self.test_image_path,
            optimization_level='medium',
            generate_webp=False,
            generate_sizes=False
        )
        
        self.assertEqual(result1, result2)
    
    def test_get_cache_key(self):
        """Test cache key generation."""
        cache_key = self.optimizer._get_cache_key(self.test_image_path, 'medium')
        
        self.assertIsInstance(cache_key, str)
        self.assertIn('image_opt:', cache_key)
        self.assertIn('medium', cache_key)
    
    def test_path_utilities(self):
        """Test path utility methods."""
        test_path = '/path/to/image.jpg'
        
        # Test optimized path
        optimized_path = self.optimizer._get_optimized_path(test_path)
        self.assertEqual(optimized_path, '/path/to/image_optimized.jpg')
        
        # Test WebP path
        webp_path = self.optimizer._get_webp_path(test_path)
        self.assertEqual(webp_path, '/path/to/image.webp')
        
        # Test base path
        base_path = self.optimizer._get_base_path(test_path)
        self.assertEqual(base_path, '/path/to/image')
    
    def test_batch_optimize_directory(self):
        """Test batch directory optimization."""
        # Create multiple test images
        for i in range(3):
            img = Image.new('RGB', (400, 300), color=('red', 'green', 'blue')[i])
            img_path = os.path.join(self.temp_dir, f'test_{i}.jpg')
            img.save(img_path, 'JPEG', quality=95)
        
        # Add non-image file
        text_file = os.path.join(self.temp_dir, 'readme.txt')
        with open(text_file, 'w') as f:
            f.write('Not an image')
        
        result = self.optimizer.batch_optimize_directory(
            self.temp_dir,
            optimization_level='medium'
        )
        
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result['processed'], 3)  # At least 3 images processed
        self.assertGreaterEqual(result['skipped'], 1)  # Text file skipped
        self.assertEqual(result['errors'], 0)
        self.assertGreaterEqual(result['total_savings'], 0)
        self.assertGreaterEqual(len(result['files']), 3)
    
    @override_settings(STATICFILES_DIRS=['/fake/static/dir'])
    def test_generate_srcset(self):
        """Test srcset generation."""
        base_path = '/fake/static/dir/images/test'
        
        # Mock file existence
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            srcset = self.optimizer.generate_srcset(base_path + '.jpg')
            
            self.assertIsInstance(srcset, str)
            if srcset:  # If any files "exist"
                self.assertIn('/static/images/test_', srcset)
                self.assertIn('320w', srcset)
    
    def test_format_bytes(self):
        """Test byte formatting utility."""
        # Test various sizes
        self.assertEqual(self.optimizer._format_bytes(500), '500.0 B')
        self.assertEqual(self.optimizer._format_bytes(1536), '1.5 KB')
        self.assertEqual(self.optimizer._format_bytes(1048576), '1.0 MB')
        self.assertEqual(self.optimizer._format_bytes(1073741824), '1.0 GB')
    
    def test_estimate_load_improvement(self):
        """Test load improvement estimation."""
        # High savings
        improvement = self.optimizer._estimate_load_improvement(60)
        self.assertIn('Significant', improvement)
        
        # Moderate savings
        improvement = self.optimizer._estimate_load_improvement(35)
        self.assertIn('Moderate', improvement)
        
        # Minor savings
        improvement = self.optimizer._estimate_load_improvement(20)
        self.assertIn('Minor', improvement)
        
        # Minimal savings
        improvement = self.optimizer._estimate_load_improvement(5)
        self.assertIn('Minimal', improvement)
    
    def test_estimate_cwv_impact(self):
        """Test Core Web Vitals impact estimation."""
        # High impact
        impact = self.optimizer._estimate_cwv_impact(50)
        self.assertIn('High positive impact', impact)
        
        # Moderate impact
        impact = self.optimizer._estimate_cwv_impact(30)
        self.assertIn('Moderate positive impact', impact)
        
        # Minor impact
        impact = self.optimizer._estimate_cwv_impact(20)
        self.assertIn('Minor positive impact', impact)
        
        # Minimal impact
        impact = self.optimizer._estimate_cwv_impact(5)
        self.assertIn('Minimal impact', impact)


class PerformanceMonitoringTests(TestCase):
    """Test performance monitoring endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        cache.clear()
    
    def test_performance_metrics_endpoint(self):
        """Test performance metrics collection endpoint."""
        url = reverse('core:performance_metrics')
        
        metrics_data = {
            'type': 'client',
            'timestamp': 1640995200000,  # January 1, 2022
            'session': {
                'url': '/test-page/'
            },
            'metrics': {
                'navigation': {
                    'total': 1500,
                    'dns': 50,
                    'tcp': 100,
                    'tls': 150,
                    'ttfb': 200,
                    'download': 300
                },
                'coreWebVitals': {
                    'lcp': {'value': 2000, 'rating': 'good'},
                    'fid': {'value': 80, 'rating': 'good'},
                    'cls': {'value': 0.05, 'rating': 'good'}
                }
            }
        }
        
        response = self.client.post(
            url,
            data=json.dumps(metrics_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data['status'], 'success')
    
    def test_performance_metrics_invalid_json(self):
        """Test performance metrics with invalid JSON."""
        url = reverse('core:performance_metrics')
        
        response = self.client.post(
            url,
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(response_data['error'], 'Invalid JSON')
    
    def test_performance_metrics_method_not_allowed(self):
        """Test performance metrics endpoint with wrong method."""
        url = reverse('core:performance_metrics')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)  # Method not allowed
    
    @patch('core.views.analyze_core_web_vitals')
    def test_performance_metrics_cwv_analysis(self, mock_analyze):
        """Test Core Web Vitals analysis trigger."""
        url = reverse('core:performance_metrics')
        
        metrics_data = {
            'type': 'client',
            'metrics': {
                'coreWebVitals': {
                    'lcp': {'value': 3000},  # Poor LCP
                    'fid': {'value': 200},   # Poor FID
                    'cls': {'value': 0.3}    # Poor CLS
                }
            }
        }
        
        response = self.client.post(
            url,
            data=json.dumps(metrics_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        mock_analyze.assert_called_once()
    
    def test_performance_dashboard_data_no_data(self):
        """Test performance dashboard with no data."""
        url = reverse('core:performance_dashboard_data')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertEqual(response_data['status'], 'no_data')
    
    def test_performance_dashboard_data_with_metrics(self):
        """Test performance dashboard with cached metrics."""
        # Simulate cached metrics
        session_key = 'test_session'
        metrics_key = f"performance_metrics_{session_key}"
        
        test_metrics = [
            {
                'timestamp': 1640995200000,
                'url': '/test-page/',
                'metrics': {
                    'navigation': {'total': 1500},
                    'coreWebVitals': {
                        'lcp': {'value': 2000},
                        'fid': {'value': 80},
                        'cls': {'value': 0.05}
                    }
                }
            }
        ]
        
        cache.set(metrics_key, test_metrics, 3600)
        
        # Mock session key
        session = self.client.session
        session.session_key = session_key
        session.save()
        
        url = reverse('core:performance_dashboard_data')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertIn('total_samples', response_data)
        self.assertIn('average_load_time', response_data)
        self.assertIn('core_web_vitals', response_data)
        self.assertIn('recommendations', response_data)
    
    def test_service_worker_endpoint(self):
        """Test service worker endpoint."""
        url = reverse('core:service_worker')
        
        # Mock settings for static files
        with override_settings(STATICFILES_DIRS=['/fake/static/dir']):
            with patch('os.path.join') as mock_join:
                mock_join.return_value = '/fake/static/dir/sw.js'
                
                with patch('builtins.open', mock_open(read_data='// Service Worker')):
                    with patch('os.path.exists', return_value=True):
                        response = self.client.get(url)
                        
                        self.assertEqual(response.status_code, 200)
                        self.assertEqual(response['Content-Type'], 'application/javascript')
                        self.assertEqual(response['Service-Worker-Allowed'], '/')
                        self.assertIn('no-cache', response['Cache-Control'])
    
    def test_service_worker_not_found(self):
        """Test service worker endpoint when file not found."""
        url = reverse('core:service_worker')
        
        with override_settings(STATICFILES_DIRS=['/fake/static/dir']):
            with patch('builtins.open', side_effect=FileNotFoundError):
                response = self.client.get(url)
                
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.content.decode(), 'Service Worker not found')


class OptimizeImagesCommandTests(TestCase):
    """Test the optimize_images management command."""
    
    def setUp(self):
        """Set up test data."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test image
        test_image = Image.new('RGB', (400, 300), color='red')
        self.test_image_path = os.path.join(self.temp_dir, 'test_image.jpg')
        test_image.save(self.test_image_path, 'JPEG', quality=95)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_optimize_single_file_command(self):
        """Test optimizing a single file via command."""
        out = StringIO()
        
        call_command(
            'optimize_images',
            f'--file={self.test_image_path}',
            '--level=medium',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Starting Image Optimization', output)
        self.assertIn('Optimizing file:', output)
    
    def test_optimize_directory_command(self):
        """Test optimizing a directory via command."""
        out = StringIO()
        
        call_command(
            'optimize_images',
            f'--directory={self.temp_dir}',
            '--level=medium',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Starting Image Optimization', output)
        self.assertIn('Optimizing directory:', output)
    
    def test_optimize_command_dry_run(self):
        """Test optimize images command in dry run mode."""
        out = StringIO()
        
        call_command(
            'optimize_images',
            f'--file={self.test_image_path}',
            '--dry-run',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('DRY RUN:', output)
        self.assertIn('Would optimize this file', output)
    
    def test_optimize_command_file_not_found(self):
        """Test optimize images command with non-existent file."""
        from django.core.management.base import CommandError
        
        with self.assertRaises(CommandError) as context:
            call_command('optimize_images', '--file=/fake/path/image.jpg')
        
        self.assertIn('File not found', str(context.exception))
    
    def test_optimize_command_directory_not_found(self):
        """Test optimize images command with non-existent directory."""
        from django.core.management.base import CommandError
        
        with self.assertRaises(CommandError) as context:
            call_command('optimize_images', '--directory=/fake/path/')
        
        self.assertIn('Directory not found', str(context.exception))
    
    @override_settings(STATICFILES_DIRS=[])
    def test_optimize_static_no_staticfiles_dirs(self):
        """Test optimize static images with no STATICFILES_DIRS."""
        from django.core.management.base import CommandError
        
        with self.assertRaises(CommandError) as context:
            call_command('optimize_images')
        
        self.assertIn('STATICFILES_DIRS not configured', str(context.exception))
    
    @override_settings(STATICFILES_DIRS=['/fake/static/'])
    def test_optimize_static_no_images_dir(self):
        """Test optimize static images with no images directory."""
        from django.core.management.base import CommandError
        
        with self.assertRaises(CommandError) as context:
            call_command('optimize_images')
        
        self.assertIn('Images directory not found', str(context.exception))


class CoreWebVitalsAnalysisTests(TestCase):
    """Test Core Web Vitals analysis functionality."""
    
    def test_analyze_core_web_vitals_good_metrics(self):
        """Test Core Web Vitals analysis with good metrics."""
        from core.views import analyze_core_web_vitals
        
        request = Mock()
        request.META = {'HTTP_REFERER': 'https://example.com/test'}
        
        cwv = {
            'lcp': {'value': 1500},  # Good LCP
            'fid': {'value': 50},    # Good FID
            'cls': {'value': 0.05}   # Good CLS
        }
        
        # Should not raise any warnings for good metrics
        with patch('core.views.logger') as mock_logger:
            analyze_core_web_vitals(cwv, request)
            mock_logger.warning.assert_not_called()
    
    def test_analyze_core_web_vitals_poor_lcp(self):
        """Test Core Web Vitals analysis with poor LCP."""
        from core.views import analyze_core_web_vitals
        
        request = Mock()
        request.META = {'HTTP_REFERER': 'https://example.com/test'}
        
        cwv = {
            'lcp': {'value': 5000},  # Poor LCP
            'fid': {'value': 50},
            'cls': {'value': 0.05}
        }
        
        with patch('core.views.logger') as mock_logger:
            analyze_core_web_vitals(cwv, request)
            mock_logger.warning.assert_called()
            warning_call = mock_logger.warning.call_args[0][0]
            self.assertIn('Poor LCP detected', warning_call)
    
    def test_analyze_core_web_vitals_poor_fid(self):
        """Test Core Web Vitals analysis with poor FID."""
        from core.views import analyze_core_web_vitals
        
        request = Mock()
        request.META = {'HTTP_REFERER': 'https://example.com/test'}
        
        cwv = {
            'lcp': {'value': 1500},
            'fid': {'value': 400},   # Poor FID
            'cls': {'value': 0.05}
        }
        
        with patch('core.views.logger') as mock_logger:
            analyze_core_web_vitals(cwv, request)
            mock_logger.warning.assert_called()
            warning_call = mock_logger.warning.call_args[0][0]
            self.assertIn('Poor FID detected', warning_call)
    
    def test_analyze_core_web_vitals_poor_cls(self):
        """Test Core Web Vitals analysis with poor CLS."""
        from core.views import analyze_core_web_vitals
        
        request = Mock()
        request.META = {'HTTP_REFERER': 'https://example.com/test'}
        
        cwv = {
            'lcp': {'value': 1500},
            'fid': {'value': 50},
            'cls': {'value': 0.3}    # Poor CLS
        }
        
        with patch('core.views.logger') as mock_logger:
            analyze_core_web_vitals(cwv, request)
            mock_logger.warning.assert_called()
            warning_call = mock_logger.warning.call_args[0][0]
            self.assertIn('Poor CLS detected', warning_call)


class PerformanceRecommendationsTests(TestCase):
    """Test performance recommendations generation."""
    
    def test_generate_performance_recommendations_good_performance(self):
        """Test recommendations for good performance."""
        from core.views import generate_performance_recommendations
        
        metrics = {
            'average_load_time': 1500,  # Good load time
            'core_web_vitals': {
                'lcp': {'average': 2000, 'samples': 10},   # Good LCP
                'fid': {'average': 80, 'samples': 10},     # Good FID
                'cls': {'average': 0.05, 'samples': 10}    # Good CLS
            }
        }
        
        recommendations = generate_performance_recommendations(metrics)
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Should include success recommendation
        success_rec = next((r for r in recommendations if r['type'] == 'success'), None)
        self.assertIsNotNone(success_rec)
        self.assertIn('Good Performance', success_rec['title'])
    
    def test_generate_performance_recommendations_slow_load(self):
        """Test recommendations for slow load time."""
        from core.views import generate_performance_recommendations
        
        metrics = {
            'average_load_time': 5000,  # Slow load time
            'core_web_vitals': {
                'lcp': {'average': 2000, 'samples': 10},
                'fid': {'average': 80, 'samples': 10},
                'cls': {'average': 0.05, 'samples': 10}
            }
        }
        
        recommendations = generate_performance_recommendations(metrics)
        
        # Should include critical recommendation for slow load time
        critical_rec = next((r for r in recommendations if r['type'] == 'critical'), None)
        self.assertIsNotNone(critical_rec)
        self.assertIn('Slow Page Load Time', critical_rec['title'])
        self.assertIn('actions', critical_rec)
    
    def test_generate_performance_recommendations_poor_cwv(self):
        """Test recommendations for poor Core Web Vitals."""
        from core.views import generate_performance_recommendations
        
        metrics = {
            'average_load_time': 2000,
            'core_web_vitals': {
                'lcp': {'average': 4000, 'samples': 10},   # Poor LCP
                'fid': {'average': 200, 'samples': 10},    # Poor FID
                'cls': {'average': 0.3, 'samples': 10}     # Poor CLS
            }
        }
        
        recommendations = generate_performance_recommendations(metrics)
        
        # Should include warnings for each poor metric
        warning_recs = [r for r in recommendations if r['type'] == 'warning']
        self.assertGreaterEqual(len(warning_recs), 3)  # One for each poor CWV
        
        # Check for specific recommendations
        titles = [r['title'] for r in warning_recs]
        self.assertIn('Poor LCP Performance', titles)
        self.assertIn('Poor FID Performance', titles)
        self.assertIn('Poor CLS Performance', titles)


class PerformanceCachingTests(TestCase):
    """Test performance-related caching."""
    
    def setUp(self):
        """Set up test data."""
        cache.clear()
    
    def test_performance_metrics_caching(self):
        """Test performance metrics storage in cache."""
        from core.views import performance_metrics
        
        # Mock request
        request = Mock()
        request.body = json.dumps({
            'type': 'client',
            'timestamp': 1640995200000,
            'metrics': {'navigation': {'total': 1500}}
        }).encode()
        request.session = {'session_key': 'test_session'}
        
        response = performance_metrics(request)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        
        # Verify metrics are cached
        metrics_key = 'performance_metrics_test_session'
        cached_metrics = cache.get(metrics_key)
        self.assertIsNotNone(cached_metrics)
        self.assertIsInstance(cached_metrics, list)
    
    def test_performance_metrics_cache_limit(self):
        """Test performance metrics cache size limit."""
        metrics_key = 'performance_metrics_test_session'
        
        # Add 105 metrics (should be limited to 100)
        metrics = []
        for i in range(105):
            metrics.append({
                'timestamp': 1640995200000 + i,
                'metrics': {'navigation': {'total': 1500 + i}}
            })
        
        cache.set(metrics_key, metrics, 3600)
        
        # Simulate adding one more through the endpoint
        from core.views import performance_metrics
        
        request = Mock()
        request.body = json.dumps({
            'type': 'client',
            'timestamp': 1640995200106,
            'metrics': {'navigation': {'total': 1606}}
        }).encode()
        request.session = {'session_key': 'test_session'}
        
        performance_metrics(request)
        
        # Check that cache is limited to 100 items
        cached_metrics = cache.get(metrics_key)
        self.assertLessEqual(len(cached_metrics), 100)


class UtilityFunctionTests(TestCase):
    """Test utility functions for performance features."""
    
    def setUp(self):
        """Set up test data."""
        self.temp_dir = tempfile.mkdtemp()
        test_image = Image.new('RGB', (400, 300), color='red')
        self.test_image_path = os.path.join(self.temp_dir, 'test.jpg')
        test_image.save(self.test_image_path, 'JPEG', quality=95)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_optimize_static_image_utility(self):
        """Test optimize_static_image utility function."""
        result = optimize_static_image(self.test_image_path, level='medium')
        
        self.assertIsNotNone(result)
        self.assertIn('original', result)
        self.assertIn('optimized', result)
    
    @override_settings(STATICFILES_DIRS=['/fake/static/'])
    def test_get_responsive_srcset_utility(self):
        """Test get_responsive_srcset utility function."""
        with patch('os.path.exists', return_value=True):
            srcset = get_responsive_srcset('/fake/static/images/test.jpg')
            
            self.assertIsInstance(srcset, str)
    
    @override_settings(STATICFILES_DIRS=None)
    def test_batch_optimize_static_images_no_settings(self):
        """Test batch_optimize_static_images with no settings."""
        result = batch_optimize_static_images()
        self.assertIsNone(result)
    
    @override_settings(STATICFILES_DIRS=['/fake/static/'])
    def test_batch_optimize_static_images_no_directory(self):
        """Test batch_optimize_static_images with non-existent directory."""
        result = batch_optimize_static_images()
        self.assertIsNone(result)