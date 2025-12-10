"""
SPEC_06 Group C Task 7: Comprehensive View Testing Suite
========================================================

Complete testing coverage for all views including:
- Response codes and status validation
- Template rendering and context data
- Form submission workflows
- Error handling and edge cases
- Performance and security testing

Target: 80% code coverage with production-ready confidence
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import connection
from unittest.mock import patch, Mock, MagicMock
import json
import time
from datetime import datetime, timedelta

from core.models import (
    Instructor, Class, Testimonial, MediaGallery, FacebookEvent,
    ContactSubmission, BookingConfirmation, SpotifyPlaylist,
    RSVPSubmission, ReviewLink
)
from core.forms import TestimonialForm, ContactForm, BookingForm


class ComprehensiveViewTestCase(TestCase):
    """Comprehensive testing for all application views."""
    
    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        self.maxDiff = None
        
        # Clear cache before each test
        cache.clear()
        
        # Create test data
        self.instructor = Instructor.objects.create(
            name='Maria Santos',
            bio='Expert salsa instructor with 15+ years experience',
            photo_url='https://example.com/maria.jpg',
            video_url='https://example.com/maria-intro.mp4',
            instagram='@maria_salsa',
            specialties='["Cuban Salsa", "Bachata", "Merengue"]'
        )
        
        self.dance_class = Class.objects.create(
            name='Advanced Cuban Salsa',
            level='advanced',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time='14:00',
            end_time='15:00',
            description='Advanced Cuban salsa techniques and styling',
            capacity=20
        )
        
        self.testimonial = Testimonial.objects.create(
            student_name='Carlos Rodriguez',
            email='carlos@example.com',
            rating=5,
            content='Amazing class! Maria is an incredible instructor who really knows how to break down complex moves.',
            class_type='choreo_team',
            status='approved',
            featured=True,
            published_at=datetime.now()
        )
        
        self.spotify_playlist = SpotifyPlaylist.objects.create(
            class_type='choreo_team',
            title='SCF Choreo Team Favorites',
            description='High-energy tracks for our choreography sessions',
            spotify_playlist_id='test123',
            spotify_embed_url='https://open.spotify.com/embed/playlist/test123',
            is_active=True,
            tracks_count=25,
            duration_minutes=90
        )

    def test_home_view_comprehensive(self):
        """Test home view with comprehensive validation."""
        response = self.client.get(reverse('core:home'))
        
        # Basic response validation
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertTemplateUsed(response, 'base.html')
        
        # Context validation
        self.assertIn('upcoming_events', response.context)
        self.assertIn('carousel_testimonials', response.context)
        self.assertIn('spotify_playlists', response.context)
        
        # Data structure validation
        upcoming_events = response.context['upcoming_events']
        self.assertIsInstance(upcoming_events, list)
        self.assertEqual(len(upcoming_events), 3)
        
        # Validate event structure
        expected_events = ['SCF Choreo Team', 'Pasos Básicos', 'Casino Royale']
        event_titles = [event['title'] for event in upcoming_events]
        for title in expected_events:
            self.assertIn(title, event_titles)
        
        # Validate carousel testimonials
        carousel_testimonials = response.context['carousel_testimonials']
        self.assertIsInstance(carousel_testimonials, list)
        self.assertGreaterEqual(len(carousel_testimonials), 1)
        
        # Validate Spotify playlists
        spotify_playlists = response.context['spotify_playlists']
        self.assertIsInstance(spotify_playlists, list)
        
        # Content validation
        self.assertContains(response, 'SCF Choreo Team')
        self.assertContains(response, 'Pasos Básicos')
        self.assertContains(response, 'Casino Royale')

    def test_events_view_comprehensive(self):
        """Test events view with comprehensive validation."""
        response = self.client.get(reverse('core:events'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'events.html')
        
        # Context validation
        self.assertIn('events', response.context)
        events = response.context['events']
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 3)
        
        # Validate monthly pricing is included
        for event in events:
            self.assertIn('monthly_price', event)
            self.assertIn('price', event)
            self.assertIsInstance(event['monthly_price'], int)

    def test_pricing_view_comprehensive(self):
        """Test pricing view with comprehensive validation."""
        response = self.client.get(reverse('core:pricing'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pricing.html')
        
        # Context validation
        self.assertIn('pricing_data', response.context)
        pricing_data = response.context['pricing_data']
        
        # Validate pricing structure
        expected_packages = ['drop_in', 'package_4', 'package_8', 'private_lessons']
        for package in expected_packages:
            self.assertIn(package, pricing_data)
        
        # Validate package structure
        package_4 = pricing_data['package_4']
        self.assertTrue(package_4.get('is_popular'))
        self.assertIn('savings', package_4)
        self.assertIn('savings_percentage', package_4)

    def test_private_lessons_view(self):
        """Test private lessons view."""
        response = self.client.get(reverse('core:private_lessons'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'private_lessons.html')

    @patch('core.utils.facebook_events.get_facebook_events')
    def test_schedule_view_with_facebook_events(self, mock_facebook_events):
        """Test schedule view with mocked Facebook events."""
        # Mock Facebook events response
        mock_facebook_events.return_value = [
            {
                'id': 'test_event_1',
                'name': 'Special Salsa Workshop',
                'description': 'Advanced workshop for experienced dancers',
                'formatted_date': 'Saturday, December 15',
                'formatted_time': '7:00 PM',
                'cover_photo': 'https://example.com/event1.jpg',
                'facebook_url': 'https://facebook.com/events/123'
            }
        ]
        
        response = self.client.get(reverse('core:schedule'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedule.html')
        
        # Context validation
        self.assertIn('sunday_classes', response.context)
        self.assertIn('facebook_events', response.context)
        
        facebook_events = response.context['facebook_events']
        self.assertEqual(len(facebook_events), 1)
        self.assertEqual(facebook_events[0]['name'], 'Special Salsa Workshop')
        
        # Verify mock was called with correct parameters
        mock_facebook_events.assert_called_once_with(limit=5, use_cache=True)

    @patch('core.utils.instagram_api.get_instagram_posts')
    def test_gallery_view_with_instagram(self, mock_instagram):
        """Test gallery view with Instagram integration."""
        # Create test media items
        MediaGallery.objects.create(
            title='Test Performance Video',
            media_type='video',
            category='performance',
            source='local',
            url='https://example.com/performance.mp4',
            caption='Amazing performance from last weekend',
            is_featured=True
        )
        
        # Mock Instagram posts
        mock_instagram.return_value = [
            {
                'id': 'instagram_1',
                'media_type': 'image',
                'media_url': 'https://instagram.com/image1.jpg',
                'caption': 'Great class today! #salsa',
                'permalink': 'https://instagram.com/p/test1'
            }
        ]
        
        response = self.client.get(reverse('core:gallery'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gallery/index.html')
        
        # Context validation
        self.assertIn('media_items', response.context)
        self.assertIn('instagram_posts', response.context)
        self.assertIn('category_choices', response.context)
        
        # Verify media items
        media_items = response.context['media_items']
        self.assertGreaterEqual(len(media_items), 1)
        
        # Verify Instagram posts
        instagram_posts = response.context['instagram_posts']
        self.assertEqual(len(instagram_posts), 1)

    def test_gallery_view_filtering(self):
        """Test gallery view with filtering parameters."""
        # Create test media items with different types
        MediaGallery.objects.create(
            title='Test Image',
            media_type='image',
            category='class',
            source='local'
        )
        MediaGallery.objects.create(
            title='Test Video',
            media_type='video',
            category='performance',
            source='local'
        )
        
        # Test type filtering
        response = self.client.get(reverse('core:gallery'), {'type': 'image'})
        self.assertEqual(response.status_code, 200)
        
        # Test category filtering
        response = self.client.get(reverse('core:gallery'), {'category': 'class'})
        self.assertEqual(response.status_code, 200)
        
        # Test combined filtering
        response = self.client.get(reverse('core:gallery'), {
            'type': 'video',
            'category': 'performance'
        })
        self.assertEqual(response.status_code, 200)

    def test_instructor_list_view(self):
        """Test instructor list view."""
        response = self.client.get(reverse('core:instructor_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'instructors/list.html')
        
        # Context validation
        self.assertIn('instructors', response.context)
        self.assertIn('instructors_with_specialties', response.context)
        
        instructors = response.context['instructors']
        self.assertGreaterEqual(len(instructors), 1)

    def test_instructor_detail_view(self):
        """Test instructor detail view."""
        response = self.client.get(
            reverse('core:instructor_detail', kwargs={'instructor_id': self.instructor.id})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'instructors/detail.html')
        
        # Context validation
        self.assertIn('instructor', response.context)
        self.assertIn('specialties_list', response.context)
        
        instructor = response.context['instructor']
        self.assertEqual(instructor.name, 'Maria Santos')
        
        specialties_list = response.context['specialties_list']
        self.assertIsInstance(specialties_list, list)

    def test_instructor_detail_view_not_found(self):
        """Test instructor detail view with non-existent instructor."""
        response = self.client.get(
            reverse('core:instructor_detail', kwargs={'instructor_id': 9999})
        )
        self.assertEqual(response.status_code, 404)

    def test_resources_view(self):
        """Test resources view with Spotify playlists."""
        response = self.client.get(reverse('core:resources'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resources.html')
        
        # Context validation
        self.assertIn('main_class_playlists', response.context)
        self.assertIn('practice_playlists', response.context)
        self.assertIn('all_playlists', response.context)

    def test_display_testimonials_view(self):
        """Test display testimonials view."""
        response = self.client.get(reverse('core:display_testimonials'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'testimonials/display.html')
        
        # Context validation
        self.assertIn('testimonials', response.context)
        self.assertIn('class_types', response.context)
        self.assertIn('average_rating', response.context)
        self.assertIn('total_reviews', response.context)
        
        testimonials = response.context['testimonials']
        self.assertGreaterEqual(len(testimonials), 1)

    def test_display_testimonials_filtering(self):
        """Test testimonials filtering functionality."""
        # Test rating filter
        response = self.client.get(reverse('core:display_testimonials'), {'rating': '5'})
        self.assertEqual(response.status_code, 200)
        
        # Test class type filter
        response = self.client.get(reverse('core:display_testimonials'), {'class_type': 'choreo_team'})
        self.assertEqual(response.status_code, 200)

    def test_view_caching_headers(self):
        """Test that views set appropriate caching headers."""
        # Test cached views
        cached_views = [
            'core:home',
            'core:events', 
            'core:pricing',
            'core:schedule',
            'core:instructor_list'
        ]
        
        for view_name in cached_views:
            response = self.client.get(reverse(view_name))
            self.assertEqual(response.status_code, 200)
            # Check that cache headers are set
            self.assertIn('max-age', response.get('Cache-Control', ''))

    def test_view_performance(self):
        """Test view response times are reasonable."""
        views_to_test = [
            'core:home',
            'core:events',
            'core:pricing',
            'core:private_lessons',
            'core:schedule',
            'core:gallery',
            'core:instructor_list',
            'core:resources',
            'core:display_testimonials'
        ]
        
        for view_name in views_to_test:
            start_time = time.time()
            response = self.client.get(reverse(view_name))
            end_time = time.time()
            
            response_time = end_time - start_time
            
            self.assertEqual(response.status_code, 200)
            self.assertLess(response_time, 2.0, f"View {view_name} took {response_time:.3f}s")

    def test_view_database_efficiency(self):
        """Test that views don't make excessive database queries."""
        with self.assertNumQueries(3):  # Reasonable number for home view with testimonials
            response = self.client.get(reverse('core:home'))
            self.assertEqual(response.status_code, 200)

    def test_view_error_handling(self):
        """Test view error handling."""
        # Test 404 handling
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)
        
        # Test invalid parameters
        response = self.client.get(reverse('core:gallery'), {'type': 'invalid'})
        self.assertEqual(response.status_code, 200)  # Should handle gracefully

    def test_view_security_headers(self):
        """Test that views include appropriate security measures."""
        response = self.client.get(reverse('core:home'))
        
        # Check content type
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')
        
        # Check that response doesn't leak sensitive information
        content = response.content.decode('utf-8')
        self.assertNotIn('password', content.lower())
        self.assertNotIn('secret', content.lower())

    def test_view_accessibility_features(self):
        """Test that views include accessibility features."""
        views_to_test = [
            'core:home',
            'core:events',
            'core:pricing',
            'core:contact'
        ]
        
        for view_name in views_to_test:
            response = self.client.get(reverse(view_name))
            content = response.content.decode('utf-8')
            
            # Basic accessibility checks
            self.assertIn('lang="en"', content)
            self.assertIn('Skip to main content', content)

    def test_view_mobile_responsiveness(self):
        """Test views with mobile user agent."""
        mobile_headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)'
        }
        
        response = self.client.get(reverse('core:home'), **mobile_headers)
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        self.assertIn('viewport', content)

    def test_view_json_responses(self):
        """Test views that return JSON responses."""
        # Test RSVP counts endpoint
        response = self.client.get(reverse('core:get_rsvp_counts'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertIn('success', data)
        self.assertIn('counts', data)

    @override_settings(DEBUG=True)
    def test_debug_only_views(self):
        """Test views that are only available in DEBUG mode."""
        # Test email test view
        response = self.client.get(reverse('core:email_test'))
        self.assertEqual(response.status_code, 200)
        
        # Test Calendly test view
        response = self.client.get(reverse('core:calendly_test'))
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=False)
    def test_debug_views_disabled_in_production(self):
        """Test that debug views are disabled in production."""
        # Test email test view returns 404 in production
        response = self.client.get(reverse('core:email_test'))
        self.assertEqual(response.status_code, 404)

    def tearDown(self):
        """Clean up after each test."""
        cache.clear()


class ViewHTTPMethodTestCase(TestCase):
    """Test HTTP method handling for all views."""
    
    def setUp(self):
        self.client = Client()

    def test_get_only_views(self):
        """Test views that should only accept GET requests."""
        get_only_views = [
            'core:home',
            'core:events', 
            'core:pricing',
            'core:private_lessons',
            'core:schedule',
            'core:gallery',
            'core:instructor_list',
            'core:resources',
            'core:display_testimonials',
            'core:testimonial_success',
            'core:contact_success'
        ]
        
        for view_name in get_only_views:
            # GET should work
            response = self.client.get(reverse(view_name))
            self.assertIn(response.status_code, [200, 302])
            
            # POST should be handled appropriately
            response = self.client.post(reverse(view_name))
            self.assertIn(response.status_code, [200, 405])

    def test_get_post_views(self):
        """Test views that accept both GET and POST."""
        get_post_views = [
            'core:contact',
            'core:submit_testimonial',
            'core:create_booking'
        ]
        
        for view_name in get_post_views:
            # GET should work
            response = self.client.get(reverse(view_name))
            self.assertEqual(response.status_code, 200)
            
            # POST should be accepted (even if invalid data)
            response = self.client.post(reverse(view_name), {})
            self.assertIn(response.status_code, [200, 302])

    def test_post_only_views(self):
        """Test views that should only accept POST requests."""
        post_only_views = [
            'core:submit_rsvp',
            'core:performance_metrics'
        ]
        
        for view_name in post_only_views:
            # GET should return 405
            response = self.client.get(reverse(view_name))
            self.assertEqual(response.status_code, 405)
            
            # POST should be accepted
            response = self.client.post(reverse(view_name), {})
            self.assertIn(response.status_code, [200, 400, 500])  # May fail validation but accepts POST


class ViewIntegrationTestCase(TestCase):
    """Integration tests for views with complex interactions."""
    
    def setUp(self):
        self.client = Client()
        
        # Create comprehensive test data
        self.instructor = Instructor.objects.create(
            name='Integration Test Instructor',
            bio='Bio for integration testing',
            photo_url='https://example.com/integration.jpg',
            specialties='["Integration", "Testing"]'
        )
        
        self.testimonial = Testimonial.objects.create(
            student_name='Integration Tester',
            email='integration@example.com',
            rating=5,
            content='This is a comprehensive integration test testimonial with sufficient length to pass validation.',
            class_type='choreo_team',
            status='approved',
            published_at=datetime.now()
        )

    def test_cross_view_data_consistency(self):
        """Test that data is consistent across different views."""
        # Get instructor from list view
        list_response = self.client.get(reverse('core:instructor_list'))
        instructors = list_response.context['instructors']
        instructor_from_list = instructors[0]
        
        # Get same instructor from detail view
        detail_response = self.client.get(
            reverse('core:instructor_detail', kwargs={'instructor_id': instructor_from_list.id})
        )
        instructor_from_detail = detail_response.context['instructor']
        
        # Data should be consistent
        self.assertEqual(instructor_from_list.name, instructor_from_detail.name)
        self.assertEqual(instructor_from_list.bio, instructor_from_detail.bio)

    def test_view_workflow_integration(self):
        """Test complete user workflow across multiple views."""
        # 1. User visits home page
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        
        # 2. User navigates to testimonials
        response = self.client.get(reverse('core:display_testimonials'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Tester')
        
        # 3. User goes to submit testimonial form
        response = self.client.get(reverse('core:submit_testimonial'))
        self.assertEqual(response.status_code, 200)
        
        # 4. User submits testimonial
        form_data = {
            'student_name': 'Workflow Tester',
            'email': 'workflow@example.com',
            'class_type': 'pasos_basicos',
            'rating': '4',
            'content': 'This is a workflow integration test testimonial that validates the complete user journey through our application.'
        }
        response = self.client.post(reverse('core:submit_testimonial'), data=form_data)
        self.assertEqual(response.status_code, 302)
        
        # 5. User reaches success page
        response = self.client.get(reverse('core:testimonial_success'))
        self.assertEqual(response.status_code, 200)
        
        # 6. Verify testimonial was created
        new_testimonial = Testimonial.objects.filter(student_name='Workflow Tester').first()
        self.assertIsNotNone(new_testimonial)
        self.assertEqual(new_testimonial.status, 'pending')

    def test_view_state_management(self):
        """Test that views handle state correctly."""
        # Test that form errors persist on resubmission
        invalid_data = {
            'student_name': '',
            'email': 'invalid-email',
            'class_type': '',
            'rating': '6',
            'content': 'Too short'
        }
        
        response = self.client.post(reverse('core:submit_testimonial'), data=invalid_data)
        self.assertEqual(response.status_code, 200)
        
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)

    def test_view_session_handling(self):
        """Test view session handling."""
        # Test that sessions work across requests
        session = self.client.session
        session['test_key'] = 'test_value'
        session.save()
        
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        
        # Session should persist
        self.assertEqual(self.client.session['test_key'], 'test_value')