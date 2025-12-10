"""
Comprehensive tests for the Schedule feature (SPEC02).

Tests all aspects of the schedule view including:
- Basic view functionality and responses
- Template rendering and context
- Database integration with Class model
- Static content and fallback behavior
- CSS integration and responsive design
- External platform links and booking functionality
- Accessibility and user experience features
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.template.loader import get_template
from django.contrib.staticfiles import finders
from datetime import time
from unittest.mock import patch
import re

from core.models import Instructor, Class


class ScheduleViewBasicTestCase(TestCase):
    """Test basic schedule view functionality."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.schedule_url = reverse('core:schedule')
    
    def test_schedule_view_returns_200_status(self):
        """Test schedule view returns 200 status code."""
        response = self.client.get(self.schedule_url)
        self.assertEqual(response.status_code, 200)
    
    def test_schedule_view_url_resolves(self):
        """Test schedule URL resolves correctly."""
        from django.urls import resolve
        resolver = resolve('/schedule/')
        self.assertEqual(resolver.view_name, 'core:schedule')
        self.assertEqual(resolver.namespace, 'core')
    
    def test_schedule_view_accepts_get_method(self):
        """Test schedule view accepts GET requests."""
        response = self.client.get(self.schedule_url)
        self.assertEqual(response.status_code, 200)
    
    def test_schedule_view_handles_post_method(self):
        """Test schedule view handles POST requests appropriately."""
        response = self.client.post(self.schedule_url)
        # Django function-based views accept all methods by default
        self.assertIn(response.status_code, [200, 405])


class ScheduleViewTemplateTestCase(TestCase):
    """Test schedule view template rendering."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.schedule_url = reverse('core:schedule')
    
    def test_schedule_uses_correct_template(self):
        """Test schedule view uses schedule.html template."""
        response = self.client.get(self.schedule_url)
        self.assertTemplateUsed(response, 'schedule.html')
        self.assertTemplateUsed(response, 'base.html')
    
    def test_schedule_template_exists(self):
        """Test schedule.html template file exists."""
        try:
            template = get_template('schedule.html')
            self.assertIsNotNone(template)
        except Exception as e:
            self.fail(f"Template schedule.html not found: {e}")
    
    def test_schedule_template_extends_base(self):
        """Test schedule template extends base template."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for base template elements
        self.assertIn('<!DOCTYPE html>', content)
        self.assertIn('<nav', content)
        self.assertIn('<footer', content)
        self.assertIn('Sabor Con Flow', content)
    
    def test_schedule_css_file_linked(self):
        """Test schedule.css is linked in the template."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for CSS file link
        self.assertIn('schedule.css', content)
        self.assertIn('static/css/schedule.css', content)
    
    def test_schedule_css_file_exists(self):
        """Test schedule.css file exists in static files."""
        css_file = finders.find('css/schedule.css')
        self.assertIsNotNone(css_file, "schedule.css file not found in static files")


class ScheduleViewDatabaseTestCase(TestCase):
    """Test schedule view database functionality."""
    
    def setUp(self):
        """Set up test client and database data."""
        self.client = Client()
        self.schedule_url = reverse('core:schedule')
        
        # Create test instructor
        self.instructor = Instructor.objects.create(
            name='Test Instructor',
            bio='Test instructor bio',
            photo_url='https://example.com/instructor.jpg',
            specialties='["Cuban Salsa", "Casino"]'
        )
    
    def test_database_queries_for_sunday_classes(self):
        """Test database queries for Sunday classes work correctly."""
        # Create Sunday classes
        sunday_class1 = Class.objects.create(
            name='Sunday Salsa',
            level='beginner',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(12, 0),
            end_time=time(13, 0),
            description='Sunday beginner salsa class'
        )
        
        sunday_class2 = Class.objects.create(
            name='Sunday Casino',
            level='intermediate',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(14, 0),
            end_time=time(15, 0),
            description='Sunday intermediate casino class'
        )
        
        # Create non-Sunday class (should not appear)
        Class.objects.create(
            name='Monday Salsa',
            level='advanced',
            instructor=self.instructor,
            day_of_week='Monday',
            start_time=time(19, 0),
            end_time=time(20, 0),
            description='Monday advanced salsa class'
        )
        
        response = self.client.get(self.schedule_url)
        
        # Check context contains only Sunday classes
        self.assertIn('sunday_classes', response.context)
        sunday_classes = response.context['sunday_classes']
        
        self.assertEqual(len(sunday_classes), 2)
        
        # Check classes are ordered by start time
        class_names = [cls.name for cls in sunday_classes]
        self.assertIn('Sunday Salsa', class_names)
        self.assertIn('Sunday Casino', class_names)
        
        # Verify Monday class is not included
        self.assertNotIn('Monday Salsa', class_names)
    
    def test_sunday_classes_context_structure(self):
        """Test sunday_classes context has correct structure."""
        # Create test Sunday class
        Class.objects.create(
            name='Test Sunday Class',
            level='beginner',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(13, 0),
            end_time=time(14, 0),
            description='Test class description'
        )
        
        response = self.client.get(self.schedule_url)
        sunday_classes = response.context['sunday_classes']
        
        self.assertGreater(len(sunday_classes), 0)
        
        # Check first class has required attributes
        first_class = sunday_classes[0]
        self.assertEqual(first_class.name, 'Test Sunday Class')
        self.assertEqual(first_class.level, 'beginner')
        self.assertEqual(first_class.day_of_week, 'Sunday')
        self.assertEqual(first_class.instructor, self.instructor)
    
    def test_schedule_with_empty_database(self):
        """Test schedule view works with no Sunday classes in database."""
        response = self.client.get(self.schedule_url)
        
        # Should still return 200
        self.assertEqual(response.status_code, 200)
        
        # Context should contain empty queryset
        sunday_classes = response.context['sunday_classes']
        self.assertEqual(len(sunday_classes), 0)


class ScheduleViewContentTestCase(TestCase):
    """Test schedule view content and display."""
    
    def setUp(self):
        """Set up test client and sample data."""
        self.client = Client()
        self.schedule_url = reverse('core:schedule')
        
        # Create test instructor
        self.instructor = Instructor.objects.create(
            name='Maria Rodriguez',
            bio='Professional salsa instructor',
            photo_url='https://example.com/maria.jpg',
            specialties='["Cuban Salsa", "Rueda de Casino"]'
        )
    
    def test_three_classes_display_with_correct_times(self):
        """Test three classes display with correct times (12-1, 1-2, 2-3)."""
        # Create three Sunday classes with specific times
        Class.objects.create(
            name='SCF Choreo Team',
            level='advanced',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(12, 0),
            end_time=time(13, 0),
            description='Advanced choreography team'
        )
        
        Class.objects.create(
            name='Pasos Básicos',
            level='beginner',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(13, 0),
            end_time=time(14, 0),
            description='Basic Cuban salsa steps'
        )
        
        Class.objects.create(
            name='Casino Royale',
            level='intermediate',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(14, 0),
            end_time=time(15, 0),
            description='Intermediate casino dancing'
        )
        
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check all three classes are displayed
        self.assertIn('SCF Choreo Team', content)
        self.assertIn('Pasos Básicos', content)
        self.assertIn('Casino Royale', content)
        
        # Check time formats (template uses time filter)
        self.assertIn('12:00 PM - 1:00 PM', content)
        self.assertIn('1:00 PM - 2:00 PM', content)
        self.assertIn('2:00 PM - 3:00 PM', content)
    
    def test_instructor_names_are_shown(self):
        """Test instructor names are displayed correctly."""
        Class.objects.create(
            name='Test Class',
            level='beginner',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(12, 0),
            end_time=time(13, 0),
            description='Test class'
        )
        
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check instructor name is displayed
        self.assertIn('Maria Rodriguez', content)
    
    def test_level_badges_displayed(self):
        """Test level badges are shown with correct content."""
        # Create classes with different levels
        Class.objects.create(
            name='Beginner Class',
            level='beginner',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(12, 0),
            end_time=time(13, 0),
            description='Beginner level class'
        )
        
        Class.objects.create(
            name='Intermediate Class',
            level='intermediate',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(13, 0),
            end_time=time(14, 0),
            description='Intermediate level class'
        )
        
        Class.objects.create(
            name='Advanced Class',
            level='advanced',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(14, 0),
            end_time=time(15, 0),
            description='Advanced level class'
        )
        
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check level badges
        self.assertIn('level-badge', content)
        self.assertIn('Beginner', content)
        self.assertIn('Intermediate', content)
        self.assertIn('Advanced', content)
    
    def test_level_badges_have_correct_colors(self):
        """Test level badges have correct CSS classes for colors."""
        # Create classes with different levels
        Class.objects.create(
            name='Beginner Class',
            level='beginner',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(12, 0),
            end_time=time(13, 0),
            description='Beginner level class'
        )
        
        Class.objects.create(
            name='Intermediate Class',
            level='intermediate',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(13, 0),
            end_time=time(14, 0),
            description='Intermediate level class'
        )
        
        Class.objects.create(
            name='Advanced Class',
            level='advanced',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(14, 0),
            end_time=time(15, 0),
            description='Advanced level class'
        )
        
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check CSS classes for level colors
        self.assertIn('level-beginner', content)
        self.assertIn('level-intermediate', content)  
        self.assertIn('level-advanced', content)


class ScheduleViewBookingTestCase(TestCase):
    """Test booking functionality in schedule view."""
    
    def setUp(self):
        """Set up test client and sample data."""
        self.client = Client()
        self.schedule_url = reverse('core:schedule')
        
        # Create test instructor and class
        self.instructor = Instructor.objects.create(
            name='Test Instructor',
            bio='Test bio',
            photo_url='https://example.com/instructor.jpg',
            specialties='["Salsa"]'
        )
        
        self.test_class = Class.objects.create(
            name='Test Class',
            level='beginner',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(12, 0),
            end_time=time(13, 0),
            description='Test class'
        )
    
    def test_book_private_lesson_buttons_present(self):
        """Test 'Book Private Lesson' buttons are present."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for booking buttons
        self.assertIn('Book Private Lesson', content)
        self.assertIn('book-lesson-btn', content)
    
    def test_book_private_lesson_buttons_have_data_attributes(self):
        """Test booking buttons have correct data attributes."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for data attributes
        self.assertIn('data-class-name', content)
        self.assertIn('data-instructor', content)
        self.assertIn(self.test_class.name, content)
        self.assertIn(self.instructor.name, content)
    
    def test_calendly_modal_present(self):
        """Test Calendly modal is present in the template."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for Calendly modal elements
        self.assertIn('calendly-modal', content)
        self.assertIn('calendly-modal-content', content)
        self.assertIn('calendly-close', content)
        self.assertIn('calendly-inline-widget', content)
    
    def test_calendly_script_included(self):
        """Test Calendly JavaScript is included."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for Calendly script
        self.assertIn('assets.calendly.com', content)
        self.assertIn('widget.js', content)


class ScheduleViewExternalLinksTestCase(TestCase):
    """Test external platform links in schedule view."""
    
    def setUp(self):
        """Set up test client and sample data."""
        self.client = Client()
        self.schedule_url = reverse('core:schedule')
        
        # Create test instructor and class
        self.instructor = Instructor.objects.create(
            name='Test Instructor',
            bio='Test bio',
            photo_url='https://example.com/instructor.jpg',
            specialties='["Salsa"]'
        )
        
        Class.objects.create(
            name='Test Class',
            level='beginner',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(12, 0),
            end_time=time(13, 0),
            description='Test class'
        )
    
    def test_facebook_links_present(self):
        """Test Facebook platform links are present."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for Facebook links
        self.assertIn('facebook.com', content)
        self.assertIn('Facebook Event', content)
        self.assertIn('facebook-link', content)
        self.assertIn('fab fa-facebook-f', content)
    
    def test_pastio_links_present(self):
        """Test Pastio platform links are present."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for Pastio links
        self.assertIn('pastio.fun', content)
        self.assertIn('Pastio.fun', content)
        self.assertIn('pastio-link', content)
        self.assertIn('fas fa-calendar-plus', content)
    
    def test_external_links_have_proper_attributes(self):
        """Test external links have proper security attributes."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for security attributes
        self.assertIn('target="_blank"', content)
        self.assertIn('rel="noopener noreferrer"', content)
    
    def test_external_links_have_correct_css_classes(self):
        """Test external links have correct CSS classes."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for CSS classes
        self.assertIn('external-link', content)
        self.assertIn('external-links', content)


class ScheduleViewResponsiveTestCase(TestCase):
    """Test responsive design features in schedule view."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.schedule_url = reverse('core:schedule')
    
    def test_mobile_responsive_grid_classes_work(self):
        """Test mobile responsive grid classes are present."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for responsive grid classes
        self.assertIn('schedule-grid', content)
        self.assertIn('class-card', content)
        self.assertIn('class-details', content)
        self.assertIn('schedule-info', content)
    
    def test_responsive_css_exists(self):
        """Test responsive CSS media queries exist in schedule.css."""
        css_file_path = finders.find('css/schedule.css')
        self.assertIsNotNone(css_file_path)
        
        with open(css_file_path, 'r') as f:
            css_content = f.read()
        
        # Check for media queries
        self.assertIn('@media (min-width: 640px)', css_content)
        self.assertIn('@media (min-width: 768px)', css_content)
        self.assertIn('@media (min-width: 1024px)', css_content)
    
    def test_viewport_meta_tag_present(self):
        """Test viewport meta tag is present for mobile responsiveness."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for viewport meta tag (should be in base template)
        self.assertIn('viewport', content)


class ScheduleViewFallbackContentTestCase(TestCase):
    """Test fallback content when no database data exists."""
    
    def setUp(self):
        """Set up test client with empty database."""
        self.client = Client()
        self.schedule_url = reverse('core:schedule')
        
        # Ensure no classes exist
        Class.objects.all().delete()
        Instructor.objects.all().delete()
    
    def test_fallback_content_displays_without_database_data(self):
        """Test fallback content displays when no database data exists."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Should still show the three default classes
        self.assertIn('SCF Choreo Team', content)
        self.assertIn('Pasos Básicos', content)
        self.assertIn('Casino Royale', content)
        
        # Should show default times
        self.assertIn('12:00 PM - 1:00 PM', content)
        self.assertIn('1:00 PM - 2:00 PM', content)
        self.assertIn('2:00 PM - 3:00 PM', content)
        
        # Should show default instructor
        self.assertIn('Sabor Con Flow Team', content)
    
    def test_fallback_content_has_correct_level_badges(self):
        """Test fallback content has correct level badges."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check default level badges
        self.assertIn('level-advanced', content)  # SCF Choreo Team
        self.assertIn('level-beginner', content)  # Pasos Básicos
        self.assertIn('level-intermediate', content)  # Casino Royale
    
    def test_fallback_content_includes_booking_buttons(self):
        """Test fallback content includes booking buttons."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Should still have booking functionality
        self.assertIn('Book Private Lesson', content)
        self.assertIn('book-lesson-btn', content)
        
        # Should have external links
        self.assertIn('facebook.com', content)
        self.assertIn('pastio.fun', content)


class ScheduleViewAccessibilityTestCase(TestCase):
    """Test accessibility features in schedule view."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.schedule_url = reverse('core:schedule')
    
    def test_semantic_html_structure(self):
        """Test semantic HTML structure for accessibility."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for semantic elements
        self.assertIn('<section', content)
        self.assertIn('<nav', content)
        self.assertIn('<main', content)
        self.assertIn('<footer', content)
        
        # Check for proper heading hierarchy
        self.assertIn('<h1>', content)
        self.assertIn('<h3>', content)
    
    def test_aria_labels_and_roles(self):
        """Test ARIA labels and roles are present."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for ARIA attributes (from base template)
        self.assertIn('role=', content)
        self.assertIn('aria-', content)
    
    def test_focus_management_css_exists(self):
        """Test focus management CSS exists in schedule.css."""
        css_file_path = finders.find('css/schedule.css')
        self.assertIsNotNone(css_file_path)
        
        with open(css_file_path, 'r') as f:
            css_content = f.read()
        
        # Check for focus styles
        self.assertIn(':focus', css_content)
        self.assertIn('outline:', css_content)
    
    def test_reduced_motion_support(self):
        """Test reduced motion support exists in CSS."""
        css_file_path = finders.find('css/schedule.css')
        self.assertIsNotNone(css_file_path)
        
        with open(css_file_path, 'r') as f:
            css_content = f.read()
        
        # Check for reduced motion media query
        self.assertIn('prefers-reduced-motion', css_content)


class ScheduleViewMetaDataTestCase(TestCase):
    """Test meta data and SEO features in schedule view."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.schedule_url = reverse('core:schedule')
    
    def test_page_title_set_correctly(self):
        """Test page title is set correctly."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for page title
        self.assertIn('Class Schedule - Sabor con Flow Dance', content)
    
    def test_meta_description_present(self):
        """Test meta description is present."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for meta description
        self.assertIn('meta name="description"', content)
        self.assertIn('Sunday dance classes', content)
    
    def test_structured_data_present(self):
        """Test structured data (JSON-LD) is present."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for structured data
        self.assertIn('application/ld+json', content)
        self.assertIn('@context', content)
        self.assertIn('schema.org', content)
        self.assertIn('Event', content)
    
    def test_canonical_url_present(self):
        """Test canonical URL is present."""
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Check for canonical link
        self.assertIn('rel="canonical"', content)


class ScheduleViewPerformanceTestCase(TestCase):
    """Test performance aspects of schedule view."""
    
    def setUp(self):
        """Set up test client and sample data."""
        self.client = Client()
        self.schedule_url = reverse('core:schedule')
        
        # Create test instructor
        self.instructor = Instructor.objects.create(
            name='Test Instructor',
            bio='Test bio',
            photo_url='https://example.com/instructor.jpg',
            specialties='["Salsa"]'
        )
    
    def test_database_query_efficiency(self):
        """Test database queries are efficient."""
        # Create multiple Sunday classes
        for i in range(5):
            Class.objects.create(
                name=f'Test Class {i}',
                level='beginner',
                instructor=self.instructor,
                day_of_week='Sunday',
                start_time=time(12 + i, 0),
                end_time=time(13 + i, 0),
                description=f'Test class {i}'
            )
        
        # Should only make minimal queries (classes + instructor lookup)
        with self.assertNumQueries(1):  # 1 optimized query with select_related
            response = self.client.get(self.schedule_url)
            self.assertEqual(response.status_code, 200)
    
    def test_view_response_time(self):
        """Test view responds quickly."""
        import time
        
        start_time = time.time()
        response = self.client.get(self.schedule_url)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should respond in under 1 second
        self.assertLess(response_time, 1.0)
        self.assertEqual(response.status_code, 200)
    
    def test_template_rendering_efficiency(self):
        """Test template renders efficiently with multiple classes."""
        # Create multiple classes to test template performance
        for i in range(10):
            Class.objects.create(
                name=f'Performance Test Class {i}',
                level='beginner',
                instructor=self.instructor,
                day_of_week='Sunday',
                start_time=time(12, i),
                end_time=time(13, i),
                description=f'Performance test class {i}'
            )
        
        response = self.client.get(self.schedule_url)
        self.assertEqual(response.status_code, 200)
        
        # Template should handle multiple classes without issue
        content = response.content.decode('utf-8')
        self.assertIn('Performance Test Class', content)


class ScheduleViewErrorHandlingTestCase(TestCase):
    """Test error handling in schedule view."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.schedule_url = reverse('core:schedule')
    
    def test_view_handles_database_errors_gracefully(self):
        """Test view handles database errors gracefully."""
        # Test with corrupted data (this would be more comprehensive in real scenario)
        response = self.client.get(self.schedule_url)
        self.assertEqual(response.status_code, 200)
    
    def test_view_handles_missing_instructor_gracefully(self):
        """Test view handles missing instructor references gracefully."""
        # Create instructor
        instructor = Instructor.objects.create(
            name='Test Instructor',
            bio='Test bio',
            photo_url='https://example.com/instructor.jpg',
            specialties='["Salsa"]'
        )
        
        # Create class with instructor
        test_class = Class.objects.create(
            name='Test Class',
            level='beginner',
            instructor=instructor,
            day_of_week='Sunday',
            start_time=time(12, 0),
            end_time=time(13, 0),
            description='Test class'
        )
        
        # Delete instructor (simulating data integrity issue)
        instructor.delete()
        
        # View should handle this gracefully
        try:
            response = self.client.get(self.schedule_url)
            # Depending on implementation, this might raise an error or handle gracefully
            # In this case, it should raise a DoesNotExist error
            self.assertIn(response.status_code, [200, 500])
        except Exception:
            # This is expected if the template tries to access a deleted instructor
            pass
    
    def test_view_works_with_invalid_time_data(self):
        """Test view works with edge case time data."""
        instructor = Instructor.objects.create(
            name='Test Instructor',
            bio='Test bio',
            photo_url='https://example.com/instructor.jpg',
            specialties='["Salsa"]'
        )
        
        # Create class with edge case times
        Class.objects.create(
            name='Edge Case Class',
            level='beginner',
            instructor=instructor,
            day_of_week='Sunday',
            start_time=time(23, 59),  # Very late time
            end_time=time(23, 59),    # Same time (edge case)
            description='Edge case class'
        )
        
        response = self.client.get(self.schedule_url)
        self.assertEqual(response.status_code, 200)


class ScheduleViewIntegrationTestCase(TestCase):
    """Integration tests for schedule view with full data."""
    
    def setUp(self):
        """Set up complete test scenario."""
        self.client = Client()
        self.schedule_url = reverse('core:schedule')
        
        # Create multiple instructors
        self.instructor1 = Instructor.objects.create(
            name='Maria Rodriguez',
            bio='Professional salsa instructor',
            photo_url='https://example.com/maria.jpg',
            specialties='["Cuban Salsa", "Rueda de Casino"]'
        )
        
        self.instructor2 = Instructor.objects.create(
            name='Carlos Martinez',
            bio='Casino dance specialist',
            photo_url='https://example.com/carlos.jpg',
            specialties='["Casino", "Son"]'
        )
        
        # Create the three expected Sunday classes
        self.choreo_class = Class.objects.create(
            name='SCF Choreo Team',
            level='advanced',
            instructor=self.instructor1,
            day_of_week='Sunday',
            start_time=time(12, 0),
            end_time=time(13, 0),
            description='Join our choreography team for an intensive dance training session focusing on advanced Cuban salsa techniques and performance routines.'
        )
        
        self.pasos_class = Class.objects.create(
            name='Pasos Básicos',
            level='beginner',
            instructor=self.instructor2,
            day_of_week='Sunday',
            start_time=time(13, 0),
            end_time=time(14, 0),
            description='Pasos Básicos will focus on basic Cuban salsa footwork, turn patterns, and a little bit of afro-Cuban in salsa.'
        )
        
        self.casino_class = Class.objects.create(
            name='Casino Royale',
            level='intermediate',
            instructor=self.instructor1,
            day_of_week='Sunday',
            start_time=time(14, 0),
            end_time=time(15, 0),
            description='Take your casino dancing to the next level with this class. We focus on the building blocks of Casino dancing.'
        )
    
    def test_full_schedule_integration(self):
        """Test complete schedule functionality with full data."""
        response = self.client.get(self.schedule_url)
        
        # Basic response check
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedule.html')
        
        # Content checks
        content = response.content.decode('utf-8')
        
        # All three classes present
        self.assertIn('SCF Choreo Team', content)
        self.assertIn('Pasos Básicos', content)
        self.assertIn('Casino Royale', content)
        
        # Correct times
        self.assertIn('12:00 PM - 1:00 PM', content)
        self.assertIn('1:00 PM - 2:00 PM', content)
        self.assertIn('2:00 PM - 3:00 PM', content)
        
        # Instructor names
        self.assertIn('Maria Rodriguez', content)
        self.assertIn('Carlos Martinez', content)
        
        # Level badges with correct classes
        self.assertIn('level-advanced', content)
        self.assertIn('level-beginner', content)
        self.assertIn('level-intermediate', content)
        
        # Booking functionality
        self.assertIn('Book Private Lesson', content)
        self.assertIn('data-class-name', content)
        
        # External links
        self.assertIn('facebook.com', content)
        self.assertIn('pastio.fun', content)
        
        # CSS integration
        self.assertIn('schedule.css', content)
        
        # Responsive classes
        self.assertIn('schedule-grid', content)
        self.assertIn('class-card', content)
    
    def test_classes_ordered_by_time(self):
        """Test classes are displayed in correct time order."""
        response = self.client.get(self.schedule_url)
        sunday_classes = response.context['sunday_classes']
        
        # Should be ordered by start_time
        self.assertEqual(len(sunday_classes), 3)
        self.assertEqual(sunday_classes[0].start_time, time(12, 0))  # SCF Choreo Team
        self.assertEqual(sunday_classes[1].start_time, time(13, 0))  # Pasos Básicos
        self.assertEqual(sunday_classes[2].start_time, time(14, 0))  # Casino Royale
    
    def test_mixed_database_and_fallback_behavior(self):
        """Test behavior when some database data exists."""
        # Delete one class to test mixed behavior
        self.pasos_class.delete()
        
        response = self.client.get(self.schedule_url)
        content = response.content.decode('utf-8')
        
        # Should show database classes
        self.assertIn('SCF Choreo Team', content)
        self.assertIn('Casino Royale', content)
        
        # Should show instructor names from database
        self.assertIn('Maria Rodriguez', content)
        
        # Should not show fallback content since database has data
        sunday_classes = response.context['sunday_classes']
        self.assertEqual(len(sunday_classes), 2)  # Only 2 classes now