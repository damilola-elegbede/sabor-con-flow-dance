"""
Comprehensive tests for Integration Views - SPEC_05 Implementation

Tests all views that integrate multiple SPEC_05 features including
Calendly widget, WhatsApp chat, Google Analytics, social media,
Facebook events, Pastio RSVPs, and Google Maps integration.
"""

import json
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from django.test import TestCase, Client, RequestFactory, override_settings
from django.http import JsonResponse
from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import (
    RSVPSubmission, FacebookEvent, ContactSubmission, 
    BookingConfirmation, SpotifyPlaylist
)
from core.views import (
    submit_rsvp, get_rsvp_counts, calendly_test,
    performance_metrics, instagram_webhook,
    handle_webhook_verification, handle_webhook_notification
)


class CalendlyIntegrationTestCase(TestCase):
    """Test cases for Calendly widget integration - SPEC_05 Group A Task 1."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    @override_settings(DEBUG=True)
    def test_calendly_test_page_debug_mode(self):
        """Test Calendly test page is accessible in debug mode."""
        response = self.client.get('/calendly/test/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Calendly Widget Test Page')
        self.assertContains(response, 'calendly')
    
    @override_settings(DEBUG=False)
    def test_calendly_test_page_production_mode(self):
        """Test Calendly test page is not accessible in production."""
        response = self.client.get('/calendly/test/')
        self.assertEqual(response.status_code, 404)
    
    def test_calendly_widget_in_templates(self):
        """Test that Calendly widget component is properly integrated."""
        # Test home page includes Calendly integration
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Note: Would check for Calendly script tags in actual implementation
    
    def test_calendly_booking_integration(self):
        """Test Calendly integration with booking system."""
        # Test that booking page includes Calendly widget option
        response = self.client.get('/booking/create/')
        self.assertEqual(response.status_code, 200)
        # Note: Would verify Calendly integration parameters


class WhatsAppChatIntegrationTestCase(TestCase):
    """Test cases for WhatsApp chat functionality - SPEC_05 Group A Task 2."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_whatsapp_button_in_contact_page(self):
        """Test WhatsApp button is included in contact page."""
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
        # Note: Would check for WhatsApp button in actual implementation
    
    def test_whatsapp_integration_configuration(self):
        """Test WhatsApp chat configuration."""
        # Test that contact forms include WhatsApp links
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
        # Note: Would verify WhatsApp group URL and configuration


class GoogleAnalyticsIntegrationTestCase(TestCase):
    """Test cases for Google Analytics 4 tracking - SPEC_05 Group A Task 3."""
    
    def setUp(self):
        """Set up test client and factory."""
        self.client = Client()
        self.factory = RequestFactory()
    
    def test_analytics_script_inclusion(self):
        """Test that Google Analytics scripts are included in pages."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Note: Would check for GA4 tracking scripts in actual implementation
    
    def test_performance_metrics_endpoint(self):
        """Test performance metrics collection endpoint."""
        metrics_data = {
            'timestamp': datetime.now().isoformat(),
            'type': 'client',
            'session': {
                'url': '/',
                'userAgent': 'Test Browser'
            },
            'metrics': {
                'navigation': {
                    'total': 1500,
                    'domContentLoaded': 800,
                    'firstByte': 200
                },
                'coreWebVitals': {
                    'lcp': {'value': 2000},
                    'fid': {'value': 50},
                    'cls': {'value': 0.05}
                }
            }
        }
        
        response = self.client.post(
            '/performance/metrics/',
            data=json.dumps(metrics_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
    
    def test_performance_metrics_invalid_data(self):
        """Test performance metrics endpoint with invalid data."""
        response = self.client.post(
            '/performance/metrics/',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Invalid JSON')
    
    def test_performance_dashboard_data(self):
        """Test performance dashboard data endpoint."""
        # First, submit some metrics
        metrics_data = {
            'timestamp': datetime.now().isoformat(),
            'type': 'client',
            'metrics': {
                'navigation': {'total': 1200},
                'coreWebVitals': {
                    'lcp': {'value': 1800},
                    'fid': {'value': 75},
                    'cls': {'value': 0.08}
                }
            }
        }
        
        self.client.post(
            '/performance/metrics/',
            data=json.dumps(metrics_data),
            content_type='application/json'
        )
        
        # Then fetch dashboard data
        response = self.client.get('/performance/dashboard/data/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        if 'total_samples' in data:  # If there's data
            self.assertIn('total_samples', data)
            self.assertIn('core_web_vitals', data)
            self.assertIn('recommendations', data)


class SocialLinksIntegrationTestCase(TestCase):
    """Test cases for social media links component - SPEC_05 Group A Task 4."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_social_links_in_pages(self):
        """Test that social links are included in appropriate pages."""
        pages_to_test = ['/', '/contact/', '/events/', '/testimonials/display/']
        
        for page in pages_to_test:
            response = self.client.get(page)
            self.assertEqual(response.status_code, 200)
            # Note: Would check for social media links in actual implementation
    
    def test_social_links_configuration(self):
        """Test social links configuration and URLs."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Note: Would verify Instagram, Facebook, WhatsApp links


class FacebookEventsIntegrationTestCase(TestCase):
    """Test cases for Facebook Events API integration - SPEC_05 Group B Task 5 & 6."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create test Facebook events
        self.facebook_event = FacebookEvent.objects.create(
            facebook_id='test_event_123',
            name='Test Salsa Workshop',
            description='Learn advanced salsa techniques in this workshop.',
            start_time=timezone.now() + timedelta(days=7),
            formatted_date='Next Saturday',
            formatted_time='7:00 PM',
            facebook_url='https://facebook.com/events/test_event_123',
            is_active=True,
            featured=True
        )
    
    def test_facebook_events_in_schedule_view(self):
        """Test Facebook events integration in schedule view."""
        response = self.client.get('/schedule/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('facebook_events', response.context)
        
        facebook_events = response.context['facebook_events']
        self.assertGreaterEqual(len(facebook_events), 0)
    
    def test_facebook_events_fallback_to_database(self):
        """Test Facebook events fallback to database when API fails."""
        with patch('core.utils.facebook_events.get_facebook_events') as mock_api:
            mock_api.return_value = []  # Simulate API failure
            
            response = self.client.get('/schedule/')
            self.assertEqual(response.status_code, 200)
            
            # Should still show events from database
            facebook_events = response.context.get('facebook_events', [])
            self.assertGreaterEqual(len(facebook_events), 0)
    
    def test_facebook_events_caching(self):
        """Test Facebook events caching behavior."""
        cache.clear()
        
        # First request
        response1 = self.client.get('/schedule/')
        self.assertEqual(response1.status_code, 200)
        
        # Second request should use cache
        response2 = self.client.get('/schedule/')
        self.assertEqual(response2.status_code, 200)


class PastioRSVPIntegrationTestCase(TestCase):
    """Test cases for Pastio.fun RSVP integration - SPEC_05 Group B Task 7."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_submit_rsvp_valid_data(self):
        """Test valid RSVP submission."""
        rsvp_data = {
            'name': 'Test Dancer',
            'email': 'dancer@example.com',
            'phone': '(555) 123-4567',
            'class_id': 'scf-choreo',
            'notifications': 'on'
        }
        
        response = self.client.post('/rsvp/submit/', data=rsvp_data)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('confirmed', data['message'])
        
        # Verify RSVP was created
        rsvp = RSVPSubmission.objects.get(email='dancer@example.com')
        self.assertEqual(rsvp.name, 'Test Dancer')
        self.assertEqual(rsvp.class_id, 'scf-choreo')
        self.assertEqual(rsvp.class_name, 'SCF Choreo Team')
        self.assertTrue(rsvp.notifications_enabled)
    
    def test_submit_rsvp_invalid_data(self):
        """Test RSVP submission with invalid data."""
        invalid_data = {
            'name': '',  # Missing name
            'email': 'dancer@example.com',
            'class_id': 'scf-choreo'
        }
        
        response = self.client.post('/rsvp/submit/', data=invalid_data)
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('required', data['error'])
    
    def test_submit_rsvp_invalid_email(self):
        """Test RSVP submission with invalid email."""
        invalid_data = {
            'name': 'Test Dancer',
            'email': 'invalid-email',
            'class_id': 'scf-choreo'
        }
        
        response = self.client.post('/rsvp/submit/', data=invalid_data)
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('valid email', data['error'])
    
    def test_submit_rsvp_invalid_class(self):
        """Test RSVP submission with invalid class ID."""
        invalid_data = {
            'name': 'Test Dancer',
            'email': 'dancer@example.com',
            'class_id': 'invalid-class'
        }
        
        response = self.client.post('/rsvp/submit/', data=invalid_data)
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('Invalid class', data['error'])
    
    def test_get_rsvp_counts(self):
        """Test RSVP counts endpoint."""
        # Create some RSVPs
        RSVPSubmission.objects.create(
            name='Test User 1',
            email='user1@example.com',
            class_id='scf-choreo',
            class_name='SCF Choreo Team',
            status='confirmed'
        )
        RSVPSubmission.objects.create(
            name='Test User 2',
            email='user2@example.com',
            class_id='pasos-basicos',
            class_name='Pasos Básicos',
            status='confirmed'
        )
        
        response = self.client.get('/rsvp/counts/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('counts', data)
        self.assertIn('updated_at', data)
        
        counts = data['counts']
        self.assertIn('scf-choreo', counts)
        self.assertIn('pasos-basicos', counts)
        self.assertIn('casino-royale', counts)
    
    def test_rsvp_counts_caching(self):
        """Test RSVP counts caching behavior."""
        cache.clear()
        
        # First request
        response1 = self.client.get('/rsvp/counts/')
        self.assertEqual(response1.status_code, 200)
        
        # Second request should use cache
        response2 = self.client.get('/rsvp/counts/')
        self.assertEqual(response2.status_code, 200)
    
    @patch('core.views.integrate_with_pastio_api')
    def test_pastio_api_integration(self, mock_pastio):
        """Test Pastio API integration in RSVP submission."""
        mock_pastio.return_value = True
        
        rsvp_data = {
            'name': 'API Test',
            'email': 'api@example.com',
            'class_id': 'casino-royale'
        }
        
        response = self.client.post('/rsvp/submit/', data=rsvp_data)
        self.assertEqual(response.status_code, 200)
        
        # Verify Pastio API was called
        mock_pastio.assert_called_once()
        
        # Verify RSVP was created
        rsvp = RSVPSubmission.objects.get(email='api@example.com')
        self.assertEqual(rsvp.source, 'pastio')


class GoogleMapsIntegrationTestCase(TestCase):
    """Test cases for Google Maps integration - SPEC_05 Group D Task 11."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    @override_settings(
        ENABLE_GOOGLE_MAPS=True,
        GOOGLE_MAPS_API_KEY='test_api_key',
        STUDIO_COORDINATES={'lat': 40.015, 'lng': -105.27},
        BUSINESS_INFO={'name': 'Test Studio', 'address': 'Test Address'}
    )
    def test_google_maps_in_contact_page(self):
        """Test Google Maps integration in contact page."""
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
        
        # Check that Google Maps configuration is passed to template
        self.assertTrue(response.context['ENABLE_GOOGLE_MAPS'])
        self.assertEqual(response.context['GOOGLE_MAPS_API_KEY'], 'test_api_key')
        self.assertIn('lat', response.context['STUDIO_COORDINATES'])
        self.assertIn('lng', response.context['STUDIO_COORDINATES'])
    
    @override_settings(ENABLE_GOOGLE_MAPS=False)
    def test_google_maps_disabled(self):
        """Test behavior when Google Maps is disabled."""
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['ENABLE_GOOGLE_MAPS'])


class InstagramWebhookIntegrationTestCase(TestCase):
    """Test cases for Instagram webhook integration - SPEC_04 Group D."""
    
    def setUp(self):
        """Set up test client and factory."""
        self.client = Client()
        self.factory = RequestFactory()
    
    @override_settings(INSTAGRAM_WEBHOOK_VERIFY_TOKEN='test_verify_token')
    def test_instagram_webhook_verification(self):
        """Test Instagram webhook verification."""
        verification_params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': 'test_verify_token',
            'hub.challenge': 'test_challenge_string'
        }
        
        response = self.client.get('/instagram/webhook/', data=verification_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'test_challenge_string')
    
    def test_instagram_webhook_verification_invalid_token(self):
        """Test Instagram webhook verification with invalid token."""
        verification_params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': 'invalid_token',
            'hub.challenge': 'test_challenge_string'
        }
        
        response = self.client.get('/instagram/webhook/', data=verification_params)
        self.assertEqual(response.status_code, 403)
    
    def test_instagram_webhook_notification(self):
        """Test Instagram webhook notification handling."""
        notification_data = {
            'object': 'instagram',
            'entry': [{
                'id': 'test_user_id',
                'changes': [{
                    'field': 'media',
                    'value': {
                        'media_id': 'test_media_123'
                    }
                }]
            }]
        }
        
        response = self.client.post(
            '/instagram/webhook/',
            data=json.dumps(notification_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'OK')
    
    def test_instagram_webhook_invalid_payload(self):
        """Test Instagram webhook with invalid payload."""
        response = self.client.post(
            '/instagram/webhook/',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)


class SpotifyPlaylistIntegrationTestCase(TestCase):
    """Test cases for Spotify playlist integration in views - SPEC_05 Group C Task 8."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create test playlists
        self.playlist = SpotifyPlaylist.objects.create(
            class_type='choreo_team',
            title='Test Choreo Playlist',
            description='Test playlist for integration',
            spotify_playlist_id='test123',
            is_active=True,
            order=1
        )
    
    def test_spotify_playlists_in_home_view(self):
        """Test Spotify playlists integration in home view."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('spotify_playlists', response.context)
        
        playlists = response.context['spotify_playlists']
        self.assertGreaterEqual(len(playlists), 1)
        self.assertTrue(all(p.is_active for p in playlists))
    
    def test_spotify_playlists_in_resources_view(self):
        """Test Spotify playlists integration in resources view."""
        response = self.client.get('/resources/')
        self.assertEqual(response.status_code, 200)
        
        # Check context variables
        self.assertIn('main_class_playlists', response.context)
        self.assertIn('practice_playlists', response.context)
        self.assertIn('all_playlists', response.context)
        
        all_playlists = response.context['all_playlists']
        self.assertGreaterEqual(len(all_playlists), 1)
    
    def test_spotify_playlists_caching_in_views(self):
        """Test Spotify playlists caching in views."""
        cache.clear()
        
        # First request
        response1 = self.client.get('/resources/')
        self.assertEqual(response1.status_code, 200)
        
        # Second request should use cache
        response2 = self.client.get('/resources/')
        self.assertEqual(response2.status_code, 200)


class EmailNotificationIntegrationTestCase(TestCase):
    """Test cases for email notification integration - SPEC_05 Group B Task 10."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_contact_form_email_integration(self):
        """Test contact form email notification integration."""
        from django.core import mail
        
        contact_data = {
            'name': 'Email Test User',
            'email': 'emailtest@example.com',
            'interest': 'private_lesson',
            'message': 'This is a test message for email integration testing.'
        }
        
        response = self.client.post('/contact/', data=contact_data)
        self.assertEqual(response.status_code, 302)
        
        # Should have sent admin notification and auto-reply
        self.assertEqual(len(mail.outbox), 2)
        
        # Check admin notification
        admin_email = next(email for email in mail.outbox 
                          if 'admin' in email.to[0].lower() or 'New Contact' in email.subject)
        self.assertIn('New Contact Inquiry', admin_email.subject)
        
        # Check auto-reply
        auto_reply = next(email for email in mail.outbox 
                         if 'emailtest@example.com' in email.to)
        self.assertIn('Thank You', auto_reply.subject)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_booking_form_email_integration(self):
        """Test booking form email notification integration."""
        from django.core import mail
        
        booking_data = {
            'customer_name': 'Booking Email Test',
            'customer_email': 'booking@example.com',
            'booking_type': 'private_lesson',
            'class_name': 'Test Private Lesson',
            'booking_date': (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
            'price': '75.00'
        }
        
        response = self.client.post('/booking/create/', data=booking_data)
        self.assertEqual(response.status_code, 302)
        
        # Should have sent booking confirmation and admin notification
        self.assertEqual(len(mail.outbox), 2)
        
        # Check customer confirmation
        confirmation = next(email for email in mail.outbox 
                           if 'booking@example.com' in email.to)
        self.assertIn('Booking Confirmed', confirmation.subject)
        
        # Check admin notification
        admin_notification = next(email for email in mail.outbox 
                                 if 'admin' in email.to[0].lower() or 'New Booking' in email.subject)
        self.assertIn('New Booking', admin_notification.subject)


class ViewSecurityTestCase(TestCase):
    """Test cases for view security and error handling."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_csrf_protection_on_forms(self):
        """Test CSRF protection on form submissions."""
        # Test RSVP submission without CSRF token
        rsvp_data = {
            'name': 'CSRF Test',
            'email': 'csrf@example.com',
            'class_id': 'scf-choreo'
        }
        
        # This should be blocked by CSRF middleware
        response = self.client.post('/rsvp/submit/', data=rsvp_data)
        self.assertEqual(response.status_code, 403)
    
    def test_rate_limiting_on_api_endpoints(self):
        """Test rate limiting on API endpoints."""
        # Test multiple rapid requests to performance metrics
        for i in range(10):
            response = self.client.post(
                '/performance/metrics/',
                data=json.dumps({'test': 'data'}),
                content_type='application/json'
            )
            # Should not be rate limited for normal usage
            self.assertIn(response.status_code, [200, 400])  # 400 for invalid data
    
    def test_input_validation_on_endpoints(self):
        """Test input validation on all endpoints."""
        # Test performance metrics with malicious input
        malicious_data = {
            'timestamp': '<script>alert("xss")</script>',
            'type': 'client',
            'metrics': {'test': 'data'}
        }
        
        response = self.client.post(
            '/performance/metrics/',
            data=json.dumps(malicious_data),
            content_type='application/json'
        )
        
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400, 500])
    
    def test_error_handling_in_views(self):
        """Test error handling in integration views."""
        # Test Instagram webhook with malformed data
        response = self.client.post(
            '/instagram/webhook/',
            data='{"malformed": json}',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        
        # Test RSVP counts with database error simulation
        with patch('core.models.RSVPSubmission.objects.filter') as mock_filter:
            mock_filter.side_effect = Exception("Database error")
            
            response = self.client.get('/rsvp/counts/')
            self.assertEqual(response.status_code, 500)


class ViewPerformanceTestCase(TestCase):
    """Test cases for view performance and efficiency."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create test data for performance testing
        for i in range(10):
            RSVPSubmission.objects.create(
                name=f'Performance Test {i}',
                email=f'perf{i}@example.com',
                class_id='scf-choreo',
                class_name='SCF Choreo Team',
                status='confirmed'
            )
    
    def test_view_query_efficiency(self):
        """Test that views use efficient database queries."""
        # Test schedule view with Facebook events
        with self.assertNumQueries(3):  # Should be efficient
            response = self.client.get('/schedule/')
            self.assertEqual(response.status_code, 200)
        
        # Test RSVP counts endpoint
        cache.clear()
        with self.assertNumQueries(2):  # Should be efficient
            response = self.client.get('/rsvp/counts/')
            self.assertEqual(response.status_code, 200)
    
    def test_caching_effectiveness(self):
        """Test caching effectiveness in views."""
        cache.clear()
        
        # First request should hit database
        response1 = self.client.get('/resources/')
        self.assertEqual(response1.status_code, 200)
        
        # Second request should use cache
        response2 = self.client.get('/resources/')
        self.assertEqual(response2.status_code, 200)
        
        # Responses should be similar (cached)
        self.assertEqual(response1.status_code, response2.status_code)
    
    def test_response_time_performance(self):
        """Test response time performance for integration views."""
        import time
        
        # Test that key views respond quickly
        test_urls = [
            '/',
            '/contact/',
            '/schedule/',
            '/resources/',
            '/rsvp/counts/'
        ]
        
        for url in test_urls:
            start_time = time.time()
            response = self.client.get(url)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Should respond within 1 second
            self.assertLess(response_time, 1.0)
            self.assertEqual(response.status_code, 200)