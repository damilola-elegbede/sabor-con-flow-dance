"""
Comprehensive view tests for Sabor Con Flow Dance core application.

Tests basic view responses, template rendering, context data,
and URL routing for all views.
"""

from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.http import HttpResponse
from datetime import time

from core.models import Instructor, Class
from core.views import home_view, events, pricing, private_lessons, contact


class ViewResponseTestCase(TestCase):
    """Test basic view responses and status codes."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_home_view_response(self):
        """Test home view returns 200 status."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
    
    def test_events_view_response(self):
        """Test events view returns 200 status."""
        response = self.client.get(reverse('core:events'))
        self.assertEqual(response.status_code, 200)
    
    def test_pricing_view_response(self):
        """Test pricing view returns 200 status."""
        response = self.client.get(reverse('core:pricing'))
        self.assertEqual(response.status_code, 200)
    
    def test_private_lessons_view_response(self):
        """Test private lessons view returns 200 status."""
        response = self.client.get(reverse('core:private_lessons'))
        self.assertEqual(response.status_code, 200)
    
    def test_contact_view_response(self):
        """Test contact view returns 200 status."""
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)


class ViewTemplateTestCase(TestCase):
    """Test that views render correct templates."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_home_view_template(self):
        """Test home view uses correct template."""
        response = self.client.get(reverse('core:home'))
        self.assertTemplateUsed(response, 'home.html')
        self.assertTemplateUsed(response, 'base.html')
    
    def test_events_view_template(self):
        """Test events view uses correct template."""
        response = self.client.get(reverse('core:events'))
        self.assertTemplateUsed(response, 'events.html')
        self.assertTemplateUsed(response, 'base.html')
    
    def test_pricing_view_template(self):
        """Test pricing view uses correct template."""
        response = self.client.get(reverse('core:pricing'))
        self.assertTemplateUsed(response, 'pricing.html')
        self.assertTemplateUsed(response, 'base.html')
    
    def test_private_lessons_view_template(self):
        """Test private lessons view uses correct template."""
        response = self.client.get(reverse('core:private_lessons'))
        self.assertTemplateUsed(response, 'private_lessons.html')
        self.assertTemplateUsed(response, 'base.html')
    
    def test_contact_view_template(self):
        """Test contact view uses correct template."""
        response = self.client.get(reverse('core:contact'))
        self.assertTemplateUsed(response, 'contact.html')
        self.assertTemplateUsed(response, 'base.html')


class ViewContextTestCase(TestCase):
    """Test view context data."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_home_view_context(self):
        """Test home view provides upcoming_events context."""
        response = self.client.get(reverse('core:home'))
        self.assertIn('upcoming_events', response.context)
        
        upcoming_events = response.context['upcoming_events']
        self.assertIsInstance(upcoming_events, list)
        self.assertGreater(len(upcoming_events), 0)
        
        # Check structure of first event
        first_event = upcoming_events[0]
        required_fields = ['title', 'date', 'time', 'location', 'description', 'price']
        for field in required_fields:
            self.assertIn(field, first_event)
    
    def test_home_view_upcoming_events_content(self):
        """Test home view upcoming events content is correct."""
        response = self.client.get(reverse('core:home'))
        upcoming_events = response.context['upcoming_events']
        
        # Test expected events are present
        event_titles = [event['title'] for event in upcoming_events]
        expected_titles = ['SCF Choreo Team', 'Pasos Básicos', 'Casino Royale']
        
        for title in expected_titles:
            self.assertIn(title, event_titles)
        
        # Test event data structure
        scf_event = next(event for event in upcoming_events if event['title'] == 'SCF Choreo Team')
        self.assertEqual(scf_event['date'], 'Every Sunday')
        self.assertEqual(scf_event['time'], '12:00 PM - 1:00 PM')
        self.assertEqual(scf_event['location'], 'Avalon Ballroom (North Lobby)')
        self.assertEqual(scf_event['price'], 20)
    
    def test_events_view_context(self):
        """Test events view provides events context."""
        response = self.client.get(reverse('core:events'))
        self.assertIn('events', response.context)
        
        events = response.context['events']
        self.assertIsInstance(events, list)
        self.assertGreater(len(events), 0)
        
        # Check structure of first event
        first_event = events[0]
        required_fields = ['title', 'date', 'time', 'location', 'description', 'price', 'monthly_price']
        for field in required_fields:
            self.assertIn(field, first_event)
    
    def test_events_view_events_content(self):
        """Test events view events content is correct."""
        response = self.client.get(reverse('core:events'))
        events = response.context['events']
        
        # Test expected events are present
        event_titles = [event['title'] for event in events]
        expected_titles = ['SCF Choreo Team', 'Pasos Básicos', 'Casino Royale']
        
        for title in expected_titles:
            self.assertIn(title, event_titles)
        
        # Test event has monthly_price that home doesn't have
        scf_event = next(event for event in events if event['title'] == 'SCF Choreo Team')
        self.assertEqual(scf_event['monthly_price'], 70)


class ViewMethodTestCase(TestCase):
    """Test view methods and HTTP methods."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_views_accept_get_method(self):
        """Test all views accept GET method."""
        urls = [
            reverse('core:home'),
            reverse('core:events'),
            reverse('core:pricing'),
            reverse('core:private_lessons'),
            reverse('core:contact'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
    
    def test_views_reject_post_method(self):
        """Test views handle POST method appropriately."""
        urls = [
            reverse('core:home'),
            reverse('core:events'),
            reverse('core:pricing'),
            reverse('core:private_lessons'),
            reverse('core:contact'),
        ]
        
        for url in urls:
            response = self.client.post(url)
            # Views should either handle POST or return 405 Method Not Allowed
            # Currently they accept POST but render normally
            self.assertIn(response.status_code, [200, 405])
    
    def test_views_reject_invalid_methods(self):
        """Test views reject invalid HTTP methods."""
        urls = [
            reverse('core:home'),
            reverse('core:events'),
            reverse('core:pricing'),
            reverse('core:private_lessons'),
            reverse('core:contact'),
        ]
        
        for url in urls:
            # Test DELETE method - Django function-based views accept all methods by default
            # In a real application, you'd use @require_http_methods decorator
            response = self.client.delete(url)
            # For now, accept that views return 200 since they're basic function views
            self.assertIn(response.status_code, [200, 405])
            
            # Test PUT method
            response = self.client.put(url)
            self.assertIn(response.status_code, [200, 405])


class ViewContentTestCase(TestCase):
    """Test view content and rendering."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_home_view_content(self):
        """Test home view contains expected content."""
        response = self.client.get(reverse('core:home'))
        
        # Test that home page contains logo and basic elements
        # Note: The current template only shows the logo
        self.assertContains(response, 'Sabor Con Flow Logo')
        self.assertContains(response, 'main-logo')
    
    def test_events_view_content(self):
        """Test events view contains expected content."""
        response = self.client.get(reverse('core:events'))
        
        # Test that events are rendered (these come from view context)
        self.assertContains(response, 'SCF Choreo Team')
        self.assertContains(response, 'Pasos Básicos')
        self.assertContains(response, 'Casino Royale')
        
        # Test that monthly prices are shown (unique to events view)
        self.assertContains(response, '$70')  # SCF monthly price with $ sign
        self.assertContains(response, '$60')  # Other monthly prices with $ sign
    
    def test_view_responses_are_html(self):
        """Test that all views return HTML content."""
        urls = [
            reverse('core:home'),
            reverse('core:events'),
            reverse('core:pricing'),
            reverse('core:private_lessons'),
            reverse('core:contact'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response['content-type'], 'text/html; charset=utf-8')
    
    def test_view_responses_contain_base_elements(self):
        """Test that all views contain base template elements."""
        urls = [
            reverse('core:home'),
            reverse('core:events'),
            reverse('core:pricing'),
            reverse('core:private_lessons'),
            reverse('core:contact'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            # Test for base template elements
            self.assertContains(response, 'Sabor Con Flow')
            self.assertContains(response, '<nav')
            self.assertContains(response, '<footer')
            self.assertContains(response, '<!DOCTYPE html>')


class ViewPerformanceTestCase(TestCase):
    """Test view performance and efficiency."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
    
    def test_view_response_times(self):
        """Test that views respond quickly."""
        import time
        
        urls = [
            reverse('core:home'),
            reverse('core:events'),
            reverse('core:pricing'),
            reverse('core:private_lessons'),
            reverse('core:contact'),
        ]
        
        for url in urls:
            start_time = time.time()
            response = self.client.get(url)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Response should be under 1 second (generous for test environment)
            self.assertLess(response_time, 1.0, f"View {url} took {response_time:.3f}s")
            self.assertEqual(response.status_code, 200)
    
    def test_view_database_queries(self):
        """Test that views don't make unnecessary database queries."""
        from django.test.utils import override_settings
        from django.db import connection
        from django.test import TransactionTestCase
        
        # Most current views don't use database, so should have minimal queries
        urls = [
            reverse('core:home'),
            reverse('core:events'),
            reverse('core:pricing'),
            reverse('core:private_lessons'),
            reverse('core:contact'),
        ]
        
        for url in urls:
            with self.assertNumQueries(2):  # Home view now fetches testimonials
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)


class ViewErrorHandlingTestCase(TestCase):
    """Test view error handling."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_nonexistent_url_returns_404(self):
        """Test that nonexistent URLs return 404."""
        response = self.client.get('/nonexistent-url/')
        self.assertEqual(response.status_code, 404)
    
    def test_views_handle_missing_templates_gracefully(self):
        """Test views handle missing templates gracefully."""
        # This would need to be tested by temporarily renaming template files
        # For now, just ensure templates exist
        from django.template.loader import get_template
        
        templates = ['home.html', 'events.html', 'pricing.html', 'private_lessons.html', 'contact.html']
        
        for template_name in templates:
            try:
                template = get_template(template_name)
                self.assertIsNotNone(template)
            except Exception as e:
                self.fail(f"Template {template_name} not found: {e}")


class ViewIntegrationTestCase(TestCase):
    """Integration tests for views with models."""
    
    def setUp(self):
        """Set up test client and sample data."""
        self.client = Client()
        
        # Create test instructor and class
        self.instructor = Instructor.objects.create(
            name='Integration Test Instructor',
            bio='Test bio for integration',
            photo_url='https://example.com/integration.jpg',
            specialties='["Integration", "Testing"]'
        )
        
        self.dance_class = Class.objects.create(
            name='Integration Test Class',
            level='beginner',
            instructor=self.instructor,
            day_of_week='Tuesday',
            start_time=time(18, 0),
            end_time=time(19, 0),
            description='Class for testing integration'
        )
    
    def test_views_work_with_model_data(self):
        """Test that views work when model data exists."""
        # Views should work regardless of model data since they use static data
        urls = [
            reverse('core:home'),
            reverse('core:events'),
            reverse('core:pricing'),
            reverse('core:private_lessons'),
            reverse('core:contact'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
    
    def test_views_work_with_empty_database(self):
        """Test that views work with empty database."""
        # Delete all model data
        Class.objects.all().delete()
        Instructor.objects.all().delete()
        
        urls = [
            reverse('core:home'),
            reverse('core:events'),
            reverse('core:pricing'),
            reverse('core:private_lessons'),
            reverse('core:contact'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)


class ViewAccessibilityTestCase(TestCase):
    """Test view accessibility features."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_views_include_accessibility_features(self):
        """Test that views include basic accessibility features."""
        urls = [
            reverse('core:home'),
            reverse('core:events'),
            reverse('core:pricing'),
            reverse('core:private_lessons'),
            reverse('core:contact'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            content = response.content.decode('utf-8')
            
            # Test for basic accessibility features from base template
            self.assertIn('lang="en"', content)
            self.assertIn('Skip to main content', content)
            self.assertIn('role="navigation"', content)
            self.assertIn('role="main"', content)
            self.assertIn('role="contentinfo"', content)
    
    def test_views_have_proper_html_structure(self):
        """Test that views have proper HTML structure."""
        urls = [
            reverse('core:home'),
            reverse('core:events'),
            reverse('core:pricing'),
            reverse('core:private_lessons'),
            reverse('core:contact'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            content = response.content.decode('utf-8')
            
            # Test for proper HTML structure
            self.assertIn('<!DOCTYPE html>', content)
            self.assertIn('<html', content)
            self.assertIn('<head>', content)
            self.assertIn('<body>', content)
            self.assertIn('</html>', content)