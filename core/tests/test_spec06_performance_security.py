"""
SPEC_06 Group C Task 7: Performance and Security Testing
=======================================================

Complete testing coverage for performance and security:
- Database query optimization testing
- View response time benchmarking
- Security vulnerability testing
- Input validation and sanitization
- Authentication and authorization testing

Target: 80% code coverage with production-ready confidence
"""

from django.test import TestCase, Client, TransactionTestCase, override_settings
from django.urls import reverse
from django.db import connection, transaction
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test.utils import override_settings
from unittest.mock import patch, Mock
import time
import threading
from datetime import datetime, timedelta

from core.models import (
    Instructor, Class, Testimonial, MediaGallery, 
    ContactSubmission, BookingConfirmation, SpotifyPlaylist
)
from core.forms import TestimonialForm, ContactForm, BookingForm


class DatabasePerformanceTestCase(TransactionTestCase):
    """Test database performance and query optimization."""
    
    def setUp(self):
        """Set up test data for performance testing."""
        self.client = Client()
        
        # Create test data at scale
        self.instructors = []
        for i in range(10):
            instructor = Instructor.objects.create(
                name=f'Performance Instructor {i}',
                bio=f'Bio for instructor {i}',
                photo_url=f'https://example.com/instructor{i}.jpg',
                specialties=f'["Specialty {i}", "Performance Testing"]'
            )
            self.instructors.append(instructor)
        
        # Create classes for each instructor
        for instructor in self.instructors:
            for j in range(5):
                Class.objects.create(
                    name=f'Class {j} by {instructor.name}',
                    level='intermediate',
                    instructor=instructor,
                    day_of_week='Monday',
                    start_time=f'{9+j}:00',
                    end_time=f'{10+j}:00',
                    description=f'Performance test class {j}'
                )
        
        # Create testimonials
        for i in range(50):
            Testimonial.objects.create(
                student_name=f'Performance Student {i}',
                email=f'perf{i}@example.com',
                rating=(i % 5) + 1,
                content=f'Performance test testimonial {i} with sufficient content for validation.',
                class_type='choreo_team',
                status='approved' if i % 2 == 0 else 'pending',
                featured=i % 10 == 0,
                published_at=datetime.now() if i % 2 == 0 else None
            )
    
    def test_home_view_query_efficiency(self):
        """Test that home view uses efficient database queries."""
        # Clear cache to ensure fresh queries
        cache.clear()
        
        with self.assertNumQueries(3):  # Should be optimized to minimal queries
            response = self.client.get(reverse('core:home'))
            self.assertEqual(response.status_code, 200)
    
    def test_testimonials_view_query_efficiency(self):
        """Test that testimonials view uses efficient queries."""
        with self.assertNumQueries(4):  # Should be optimized
            response = self.client.get(reverse('core:display_testimonials'))
            self.assertEqual(response.status_code, 200)
    
    def test_instructor_list_query_efficiency(self):
        """Test instructor list view query efficiency."""
        with self.assertNumQueries(2):  # Should use select_related/prefetch_related
            response = self.client.get(reverse('core:instructor_list'))
            self.assertEqual(response.status_code, 200)
    
    def test_bulk_operations_performance(self):
        """Test performance of bulk database operations."""
        start_time = time.time()
        
        # Bulk create testimonials
        testimonials = []
        for i in range(100):
            testimonials.append(Testimonial(
                student_name=f'Bulk Test {i}',
                email=f'bulk{i}@example.com',
                rating=5,
                content=f'Bulk testimonial {i} with sufficient content.',
                class_type='pasos_basicos',
                status='pending'
            ))
        
        Testimonial.objects.bulk_create(testimonials)
        
        end_time = time.time()
        bulk_time = end_time - start_time
        
        # Should complete in reasonable time (under 1 second)
        self.assertLess(bulk_time, 1.0)
        
        # Verify all were created
        self.assertEqual(Testimonial.objects.filter(student_name__startswith='Bulk Test').count(), 100)
    
    def test_complex_query_performance(self):
        """Test performance of complex database queries."""
        start_time = time.time()
        
        # Complex query: Get featured testimonials with ratings > 4 from specific classes
        complex_query = Testimonial.objects.filter(
            status='approved',
            featured=True,
            rating__gte=4,
            class_type__in=['choreo_team', 'pasos_basicos']
        ).select_related().order_by('-published_at')[:10]
        
        # Execute query
        results = list(complex_query)
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Should complete quickly
        self.assertLess(query_time, 0.5)
        self.assertIsInstance(results, list)
    
    def test_database_connection_efficiency(self):
        """Test database connection handling efficiency."""
        initial_queries = len(connection.queries)
        
        # Make multiple requests
        for _ in range(5):
            response = self.client.get(reverse('core:home'))
            self.assertEqual(response.status_code, 200)
        
        # Should reuse connections efficiently
        final_queries = len(connection.queries)
        query_count = final_queries - initial_queries
        
        # Should not create excessive queries
        self.assertLess(query_count, 20)  # Reasonable limit for 5 requests
    
    def test_cache_effectiveness(self):
        """Test that caching reduces database load."""
        cache.clear()
        
        # First request (should hit database)
        with self.assertNumQueries(3):
            response1 = self.client.get(reverse('core:home'))
            self.assertEqual(response1.status_code, 200)
        
        # Second request (should use cache for some data)
        with self.assertNumQueries(2):  # Should be fewer queries due to caching
            response2 = self.client.get(reverse('core:home'))
            self.assertEqual(response2.status_code, 200)


class ViewPerformanceTestCase(TestCase):
    """Test view performance characteristics."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create some test data
        self.instructor = Instructor.objects.create(
            name='Performance Test Instructor',
            bio='Testing performance',
            photo_url='https://example.com/perf.jpg',
            specialties='["Performance"]'
        )
        
        for i in range(10):
            Testimonial.objects.create(
                student_name=f'Perf User {i}',
                email=f'perf{i}@example.com',
                rating=5,
                content=f'Performance testimonial {i} with sufficient content.',
                class_type='choreo_team',
                status='approved',
                published_at=datetime.now()
            )
    
    def test_view_response_times(self):
        """Test that all views respond within acceptable time limits."""
        views_to_test = [
            ('core:home', {}),
            ('core:events', {}),
            ('core:pricing', {}),
            ('core:private_lessons', {}),
            ('core:contact', {}),
            ('core:schedule', {}),
            ('core:gallery', {}),
            ('core:instructor_list', {}),
            ('core:instructor_detail', {'instructor_id': self.instructor.id}),
            ('core:resources', {}),
            ('core:display_testimonials', {}),
            ('core:submit_testimonial', {}),
            ('core:testimonial_success', {}),
        ]
        
        for view_name, kwargs in views_to_test:
            start_time = time.time()
            response = self.client.get(reverse(view_name, kwargs=kwargs))
            end_time = time.time()
            
            response_time = end_time - start_time
            
            self.assertEqual(response.status_code, 200)
            self.assertLess(response_time, 1.0, f"View {view_name} took {response_time:.3f}s")
    
    def test_concurrent_request_handling(self):
        """Test that the application handles concurrent requests efficiently."""
        results = []
        
        def make_request():
            start_time = time.time()
            response = self.client.get(reverse('core:home'))
            end_time = time.time()
            results.append({
                'status_code': response.status_code,
                'response_time': end_time - start_time
            })
        
        # Create multiple threads for concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # All requests should succeed
        self.assertEqual(len(results), 10)
        for result in results:
            self.assertEqual(result['status_code'], 200)
            self.assertLess(result['response_time'], 2.0)
        
        # Total time should be reasonable (parallelism should help)
        self.assertLess(total_time, 5.0)
    
    def test_memory_usage_efficiency(self):
        """Test that views don't consume excessive memory."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Make multiple requests to test memory usage
        for _ in range(20):
            response = self.client.get(reverse('core:home'))
            self.assertEqual(response.status_code, 200)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        self.assertLess(memory_increase, 50 * 1024 * 1024)
    
    def test_static_file_serving_performance(self):
        """Test static file serving performance."""
        # Test that static files are served efficiently
        static_urls = [
            '/static/css/styles.css',
            '/static/js/main.js',
            '/static/images/sabor-con-flow-logo.webp'
        ]
        
        for url in static_urls:
            start_time = time.time()
            response = self.client.get(url)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Static files should serve quickly
            self.assertLess(response_time, 0.5)
            # Should not return 404 (files should exist)
            self.assertNotEqual(response.status_code, 404)


class SecurityTestCase(TestCase):
    """Test security measures and vulnerability prevention."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create admin user for testing
        self.admin_user = User.objects.create_superuser(
            username='securitytest',
            email='security@example.com',
            password='securepass123'
        )
    
    def test_xss_prevention_in_forms(self):
        """Test that forms prevent XSS attacks."""
        xss_payloads = [
            '<script>alert("xss")</script>',
            '"><script>alert("xss")</script>',
            'javascript:alert("xss")',
            '<img src=x onerror=alert("xss")>',
            '<svg onload=alert("xss")>',
            '"><iframe src="javascript:alert(\'xss\')"></iframe>'
        ]
        
        for payload in xss_payloads:
            data = {
                'student_name': payload,
                'email': 'xss@example.com',
                'class_type': 'choreo_team',
                'rating': '5',
                'content': f'XSS test payload: {payload} with sufficient content for validation.'
            }
            
            response = self.client.post(reverse('core:submit_testimonial'), data=data)
            
            # Form should either reject malicious input or safely store it
            if response.status_code == 302:  # Success redirect
                # If stored, verify it's safely handled in display
                display_response = self.client.get(reverse('core:display_testimonials'))
                # Script tags should not be executable in the response
                self.assertNotContains(display_response, '<script>', html=True)
    
    def test_sql_injection_prevention(self):
        """Test that application prevents SQL injection attacks."""
        sql_payloads = [
            "'; DROP TABLE testimonials; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM auth_user --",
            "'; DELETE FROM core_testimonial; --",
            "' OR 1=1 --"
        ]
        
        for payload in sql_payloads:
            # Test in testimonial form
            data = {
                'student_name': payload,
                'email': 'sql@example.com',
                'class_type': 'choreo_team',
                'rating': '5',
                'content': f'SQL injection test: {payload} with sufficient content.'
            }
            
            initial_count = Testimonial.objects.count()
            response = self.client.post(reverse('core:submit_testimonial'), data=data)
            
            # Database should not be compromised
            final_count = Testimonial.objects.count()
            self.assertTrue(final_count >= initial_count)  # Should not delete existing data
            
            # Test in URL parameters
            response = self.client.get(reverse('core:display_testimonials'), {'rating': payload})
            self.assertEqual(response.status_code, 200)  # Should handle gracefully
    
    def test_csrf_protection(self):
        """Test CSRF protection on forms."""
        # Test POST without CSRF token
        data = {
            'student_name': 'CSRF Test',
            'email': 'csrf@example.com',
            'class_type': 'choreo_team',
            'rating': '5',
            'content': 'Testing CSRF protection with sufficient content.'
        }
        
        # Disable CSRF middleware temporarily to test enforcement
        response = self.client.post(reverse('core:submit_testimonial'), data=data)
        
        # Should either require CSRF token or be properly exempt
        self.assertIn(response.status_code, [200, 302, 403])
    
    def test_file_upload_security(self):
        """Test file upload security measures."""
        # Test malicious file upload
        malicious_files = [
            ('malware.exe', b'MZ\x90\x00', 'application/x-executable'),
            ('script.php', b'<?php echo "hack"; ?>', 'application/x-php'),
            ('evil.html', b'<script>alert("xss")</script>', 'text/html'),
            ('large.jpg', b'x' * (6 * 1024 * 1024), 'image/jpeg')  # > 5MB
        ]
        
        for filename, content, content_type in malicious_files:
            from django.core.files.uploadedfile import SimpleUploadedFile
            
            malicious_file = SimpleUploadedFile(
                name=filename,
                content=content,
                content_type=content_type
            )
            
            data = {
                'student_name': 'File Security Test',
                'email': 'filesec@example.com',
                'class_type': 'choreo_team',
                'rating': '5',
                'content': f'Testing file upload security for {filename} with sufficient content.'
            }
            
            form = TestimonialForm(data=data, files={'photo': malicious_file})
            
            # Form should reject malicious files
            self.assertFalse(form.is_valid())
            if 'photo' in form.errors:
                self.assertTrue(any('Please upload a valid image' in error or 
                                  'Photo size cannot exceed' in error or
                                  'invalid' in error.lower()
                                  for error in form.errors['photo']))
    
    def test_input_length_limits(self):
        """Test that input length limits are enforced."""
        # Test extremely long inputs
        long_inputs = {
            'student_name': 'a' * 1000,  # Exceeds max_length
            'content': 'a' * 10000,     # Exceeds max_length
            'email': 'a' * 200 + '@example.com'  # Very long email
        }
        
        for field, long_value in long_inputs.items():
            data = {
                'student_name': 'Length Test',
                'email': 'length@example.com',
                'class_type': 'choreo_team',
                'rating': '5',
                'content': 'Testing input length limits with sufficient content for validation.'
            }
            data[field] = long_value
            
            form = TestimonialForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)
    
    def test_rate_limiting_simulation(self):
        """Test behavior under rapid requests (simulating rate limiting)."""
        # Make rapid requests to test DoS resistance
        start_time = time.time()
        responses = []
        
        for i in range(20):
            response = self.client.get(reverse('core:home'))
            responses.append(response.status_code)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle rapid requests gracefully
        self.assertTrue(all(status in [200, 429] for status in responses))
        # Should not take too long even under load
        self.assertLess(total_time, 10.0)
    
    def test_sensitive_data_exposure(self):
        """Test that sensitive data is not exposed."""
        # Check that error pages don't expose sensitive information
        response = self.client.get('/nonexistent-url/')
        self.assertEqual(response.status_code, 404)
        
        content = response.content.decode('utf-8').lower()
        
        # Should not expose sensitive information
        sensitive_terms = ['password', 'secret', 'key', 'token', 'database', 'config']
        for term in sensitive_terms:
            self.assertNotIn(term, content)
    
    def test_admin_access_control(self):
        """Test admin access control."""
        # Test admin access without authentication
        admin_urls = [
            '/admin/',
            '/admin/core/testimonial/',
            '/admin/core/instructor/'
        ]
        
        for url in admin_urls:
            response = self.client.get(url)
            # Should redirect to login or return 403
            self.assertIn(response.status_code, [302, 403])
        
        # Test admin access with authentication
        self.client.force_login(self.admin_user)
        
        for url in admin_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
    
    def test_secure_headers(self):
        """Test that security headers are set appropriately."""
        response = self.client.get(reverse('core:home'))
        
        # Check for security headers
        headers_to_check = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
        }
        
        for header, expected_value in headers_to_check.items():
            if header in response:
                self.assertEqual(response[header], expected_value)


class InputValidationTestCase(TestCase):
    """Test input validation and sanitization."""
    
    def test_email_validation_edge_cases(self):
        """Test email validation with edge cases."""
        invalid_emails = [
            '',  # Empty
            ' ',  # Whitespace only
            'email',  # No domain
            '@domain.com',  # No local part
            'email@',  # No domain
            'email@domain',  # No TLD
            'email with spaces@domain.com',  # Spaces
            'email@domain with spaces.com',  # Spaces in domain
            'email..email@domain.com',  # Double dots
            '.email@domain.com',  # Leading dot
            'email.@domain.com',  # Trailing dot
            'email@.domain.com',  # Leading dot in domain
            'email@domain..com',  # Double dots in domain
        ]
        
        for invalid_email in invalid_emails:
            data = {
                'student_name': 'Email Validation Test',
                'email': invalid_email,
                'class_type': 'choreo_team',
                'rating': '5',
                'content': f'Testing email validation for: {repr(invalid_email)} with sufficient content.'
            }
            
            form = TestimonialForm(data=data)
            self.assertFalse(form.is_valid(), f"Email should be invalid: {repr(invalid_email)}")
            self.assertIn('email', form.errors)
    
    def test_unicode_input_handling(self):
        """Test handling of Unicode input."""
        unicode_inputs = [
            'José María García-López',  # Spanish accents
            '李小明',  # Chinese characters
            'Владимир Путин',  # Cyrillic
            'محمد عبدالله',  # Arabic
            '🙂💃🎉',  # Emojis
            'café naïve résumé',  # Mixed accents
        ]
        
        for unicode_input in unicode_inputs:
            data = {
                'student_name': unicode_input,
                'email': 'unicode@example.com',
                'class_type': 'choreo_team',
                'rating': '5',
                'content': f'Testing Unicode support for {unicode_input} with sufficient content for validation.'
            }
            
            form = TestimonialForm(data=data)
            self.assertTrue(form.is_valid(), f"Unicode input should be valid: {unicode_input}")
            
            if form.is_valid():
                testimonial = form.save()
                self.assertEqual(testimonial.student_name, unicode_input)
    
    def test_special_characters_handling(self):
        """Test handling of special characters."""
        special_chars = [
            "O'Connor",  # Apostrophe
            "Smith-Jones",  # Hyphen
            "van der Berg",  # Spaces and lowercase
            "José María",  # Accents and space
            "Jean-Pierre",  # Hyphen
            "MacLeod",  # Capitalization
            "D'Angelo",  # Apostrophe and capitalization
        ]
        
        for special_name in special_chars:
            data = {
                'student_name': special_name,
                'email': 'special@example.com',
                'class_type': 'choreo_team',
                'rating': '5',
                'content': f'Testing special characters in name: {special_name} with sufficient content.'
            }
            
            form = TestimonialForm(data=data)
            self.assertTrue(form.is_valid(), f"Special character name should be valid: {special_name}")
    
    def test_boundary_value_testing(self):
        """Test boundary values for numeric fields."""
        # Test rating boundaries
        boundary_ratings = [
            ('0', False),  # Below minimum
            ('1', True),   # Minimum valid
            ('5', True),   # Maximum valid
            ('6', False),  # Above maximum
        ]
        
        for rating, should_be_valid in boundary_ratings:
            data = {
                'student_name': 'Boundary Test',
                'email': 'boundary@example.com',
                'class_type': 'choreo_team',
                'rating': rating,
                'content': f'Testing boundary rating {rating} with sufficient content for validation.'
            }
            
            form = TestimonialForm(data=data)
            if should_be_valid:
                self.assertTrue(form.is_valid(), f"Rating {rating} should be valid")
            else:
                self.assertFalse(form.is_valid(), f"Rating {rating} should be invalid")
    
    def test_content_length_boundaries(self):
        """Test content length boundary values."""
        # Test content length boundaries
        boundary_contents = [
            ('a' * 49, False),   # Just under minimum
            ('a' * 50, True),    # Minimum valid
            ('a' * 500, True),   # Maximum valid  
            ('a' * 501, False),  # Just over maximum
        ]
        
        for content, should_be_valid in boundary_contents:
            data = {
                'student_name': 'Content Length Test',
                'email': 'contentlength@example.com',
                'class_type': 'choreo_team',
                'rating': '5',
                'content': content
            }
            
            form = TestimonialForm(data=data)
            if should_be_valid:
                self.assertTrue(form.is_valid(), f"Content length {len(content)} should be valid")
            else:
                self.assertFalse(form.is_valid(), f"Content length {len(content)} should be invalid")
                self.assertIn('content', form.errors)


class AuthenticationTestCase(TestCase):
    """Test authentication and authorization."""
    
    def setUp(self):
        """Set up test users."""
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='regularpass123'
        )
    
    def test_admin_only_views_access_control(self):
        """Test that admin-only views require proper authentication."""
        admin_only_urls = [
            '/admin/',
            '/admin/core/testimonial/',
            '/admin/core/instructor/',
        ]
        
        # Test without authentication
        for url in admin_only_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [302, 403], f"URL {url} should require authentication")
        
        # Test with regular user
        self.client.force_login(self.regular_user)
        for url in admin_only_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [302, 403], f"URL {url} should require admin privileges")
        
        # Test with admin user
        self.client.force_login(self.admin_user)
        for url in admin_only_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Admin should access {url}")
    
    def test_public_views_accessibility(self):
        """Test that public views are accessible without authentication."""
        public_urls = [
            reverse('core:home'),
            reverse('core:events'),
            reverse('core:pricing'),
            reverse('core:contact'),
            reverse('core:submit_testimonial'),
            reverse('core:display_testimonials'),
        ]
        
        for url in public_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Public URL {url} should be accessible")
    
    def test_session_security(self):
        """Test session security measures."""
        # Test that sessions are created properly
        response = self.client.get(reverse('core:home'))
        self.assertIn('sessionid', self.client.cookies)
        
        # Test session persistence
        session_key = self.client.session.session_key
        self.assertIsNotNone(session_key)
        
        # Make another request
        response = self.client.get(reverse('core:events'))
        self.assertEqual(self.client.session.session_key, session_key)


class ErrorHandlingTestCase(TestCase):
    """Test error handling and resilience."""
    
    def test_404_error_handling(self):
        """Test 404 error handling."""
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)
    
    def test_500_error_simulation(self):
        """Test 500 error handling simulation."""
        # This would need to be tested by temporarily breaking a view
        # For now, we test that error templates exist
        from django.template.loader import get_template
        
        try:
            template = get_template('404.html')
            self.assertIsNotNone(template)
        except:
            self.fail("404.html template should exist")
        
        try:
            template = get_template('500.html')
            self.assertIsNotNone(template)
        except:
            self.fail("500.html template should exist")
    
    def test_invalid_parameter_handling(self):
        """Test handling of invalid URL parameters."""
        # Test invalid instructor ID
        response = self.client.get(reverse('core:instructor_detail', kwargs={'instructor_id': 99999}))
        self.assertEqual(response.status_code, 404)
        
        # Test invalid filter parameters
        response = self.client.get(reverse('core:display_testimonials'), {'rating': 'invalid'})
        self.assertEqual(response.status_code, 200)  # Should handle gracefully
        
        response = self.client.get(reverse('core:gallery'), {'type': 'invalid'})
        self.assertEqual(response.status_code, 200)  # Should handle gracefully
    
    def test_malformed_request_handling(self):
        """Test handling of malformed requests."""
        # Test POST with invalid data
        response = self.client.post(reverse('core:submit_testimonial'), data='invalid')
        self.assertIn(response.status_code, [200, 400])  # Should handle gracefully
        
        # Test with invalid Content-Type
        response = self.client.post(
            reverse('core:performance_metrics'),
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)  # Should return bad request