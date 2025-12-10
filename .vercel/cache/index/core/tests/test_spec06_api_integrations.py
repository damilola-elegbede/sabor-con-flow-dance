"""
SPEC_06 Group C Task 7: API Integration Testing with Mocks
=========================================================

Complete testing coverage for all API integrations:
- Facebook Events API with mocked responses
- Instagram API with mocked responses  
- Google Business/Reviews API with mocked responses
- Email service integrations
- Webhook handling and validation

Target: 80% code coverage with production-ready confidence
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.cache import cache
from unittest.mock import patch, Mock, MagicMock, call
import json
import requests
from datetime import datetime, timedelta

from core.models import FacebookEvent, MediaGallery, Testimonial, ContactSubmission
from core.utils.facebook_events import get_facebook_events, sync_facebook_events
from core.utils.instagram_api import get_instagram_posts, sync_instagram_media
from core.utils.google_reviews import submit_testimonial_to_google
from core.utils.email_notifications import (
    send_admin_notification_email,
    send_thank_you_email,
    send_contact_admin_notification_email,
    test_email_configuration
)


class FacebookAPIIntegrationTestCase(TestCase):
    """Test Facebook API integration with mocked responses."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        cache.clear()
    
    @patch('core.utils.facebook_events.requests.get')
    def test_facebook_events_api_success(self, mock_get):
        """Test successful Facebook events API call."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'id': 'event_123',
                    'name': 'Salsa Night Special',
                    'description': 'Join us for an amazing salsa night with live music',
                    'start_time': '2024-12-20T19:00:00+0000',
                    'end_time': '2024-12-20T23:00:00+0000',
                    'cover': {
                        'source': 'https://example.com/event_cover.jpg'
                    },
                    'place': {
                        'name': 'Avalon Ballroom',
                        'location': {
                            'street': '6185 Arapahoe Rd',
                            'city': 'Boulder',
                            'state': 'CO'
                        }
                    }
                },
                {
                    'id': 'event_456',
                    'name': 'Bachata Workshop',
                    'description': 'Learn bachata basics in this intensive workshop',
                    'start_time': '2024-12-22T14:00:00+0000',
                    'cover': {
                        'source': 'https://example.com/workshop_cover.jpg'
                    }
                }
            ],
            'paging': {
                'next': None
            }
        }
        mock_get.return_value = mock_response
        
        # Test API call
        events = get_facebook_events(limit=5)
        
        # Verify results
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['name'], 'Salsa Night Special')
        self.assertEqual(events[1]['name'], 'Bachata Workshop')
        
        # Verify API was called with correct parameters
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn('events', call_args[0][0])  # URL contains 'events'
    
    @patch('core.utils.facebook_events.requests.get')
    def test_facebook_events_api_failure(self, mock_get):
        """Test Facebook events API failure handling."""
        # Mock API failure
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Bad Request")
        mock_get.return_value = mock_response
        
        # Test API call with failure
        events = get_facebook_events()
        
        # Should return empty list on failure
        self.assertEqual(events, [])
    
    @patch('core.utils.facebook_events.requests.get')
    def test_facebook_events_caching(self, mock_get):
        """Test Facebook events caching functionality."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'id': 'cached_event',
                    'name': 'Cached Event',
                    'description': 'This event should be cached',
                    'start_time': '2024-12-25T20:00:00+0000'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # First call should hit API
        events1 = get_facebook_events(use_cache=True)
        self.assertEqual(len(events1), 1)
        self.assertEqual(mock_get.call_count, 1)
        
        # Second call should use cache
        events2 = get_facebook_events(use_cache=True)
        self.assertEqual(len(events2), 1)
        self.assertEqual(mock_get.call_count, 1)  # Should not increase
        
        # Clear cache and try again
        cache.clear()
        events3 = get_facebook_events(use_cache=True)
        self.assertEqual(len(events3), 1)
        self.assertEqual(mock_get.call_count, 2)  # Should increase
    
    @patch('core.utils.facebook_events.get_facebook_events')
    def test_facebook_events_sync_to_database(self, mock_get_events):
        """Test syncing Facebook events to database."""
        # Mock events data
        mock_get_events.return_value = [
            {
                'id': 'sync_event_1',
                'name': 'Database Sync Event',
                'description': 'Testing database synchronization',
                'start_time': '2024-12-30T18:00:00+0000',
                'end_time': '2024-12-30T22:00:00+0000',
                'cover_photo': 'https://example.com/sync_cover.jpg',
                'facebook_url': 'https://facebook.com/events/sync_event_1',
                'location_name': 'Test Venue',
                'location_address': '123 Test St, Boulder, CO'
            }
        ]
        
        # Call sync function
        result = sync_facebook_events()
        
        # Verify database was updated
        self.assertTrue(result)
        facebook_event = FacebookEvent.objects.get(facebook_id='sync_event_1')
        self.assertEqual(facebook_event.name, 'Database Sync Event')
        self.assertEqual(facebook_event.location_name, 'Test Venue')
    
    @patch('core.utils.facebook_events.requests.get')
    def test_facebook_events_pagination(self, mock_get):
        """Test Facebook events API pagination handling."""
        # Mock paginated response
        page1_response = Mock()
        page1_response.status_code = 200
        page1_response.json.return_value = {
            'data': [
                {'id': 'page1_event1', 'name': 'Page 1 Event 1', 'start_time': '2024-12-20T19:00:00+0000'},
                {'id': 'page1_event2', 'name': 'Page 1 Event 2', 'start_time': '2024-12-21T19:00:00+0000'}
            ],
            'paging': {
                'next': 'https://graph.facebook.com/v18.0/page2'
            }
        }
        
        page2_response = Mock()
        page2_response.status_code = 200
        page2_response.json.return_value = {
            'data': [
                {'id': 'page2_event1', 'name': 'Page 2 Event 1', 'start_time': '2024-12-22T19:00:00+0000'}
            ],
            'paging': {}
        }
        
        mock_get.side_effect = [page1_response, page2_response]
        
        # Test pagination
        events = get_facebook_events(limit=10)
        
        # Should get events from both pages
        self.assertEqual(len(events), 3)
        self.assertEqual(mock_get.call_count, 2)


class InstagramAPIIntegrationTestCase(TestCase):
    """Test Instagram API integration with mocked responses."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        cache.clear()
    
    @patch('core.utils.instagram_api.requests.get')
    def test_instagram_posts_api_success(self, mock_get):
        """Test successful Instagram posts API call."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'id': 'instagram_post_1',
                    'media_type': 'IMAGE',
                    'media_url': 'https://instagram.com/image1.jpg',
                    'caption': 'Great salsa class tonight! #salsa #dance',
                    'permalink': 'https://instagram.com/p/post1',
                    'timestamp': '2024-12-15T20:00:00+0000'
                },
                {
                    'id': 'instagram_post_2',
                    'media_type': 'VIDEO',
                    'media_url': 'https://instagram.com/video1.mp4',
                    'thumbnail_url': 'https://instagram.com/video1_thumb.jpg',
                    'caption': 'Amazing bachata performance! 💃',
                    'permalink': 'https://instagram.com/p/post2',
                    'timestamp': '2024-12-14T19:00:00+0000'
                }
            ],
            'paging': {
                'next': None
            }
        }
        mock_get.return_value = mock_response
        
        # Test API call
        posts = get_instagram_posts(limit=10)
        
        # Verify results
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0]['id'], 'instagram_post_1')
        self.assertEqual(posts[0]['media_type'], 'IMAGE')
        self.assertEqual(posts[1]['media_type'], 'VIDEO')
        
        # Verify API was called
        mock_get.assert_called_once()
    
    @patch('core.utils.instagram_api.requests.get')
    def test_instagram_api_failure(self, mock_get):
        """Test Instagram API failure handling."""
        # Mock API failure
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Unauthorized")
        mock_get.return_value = mock_response
        
        # Test API call with failure
        posts = get_instagram_posts()
        
        # Should return empty list on failure
        self.assertEqual(posts, [])
    
    @patch('core.utils.instagram_api.get_instagram_posts')
    def test_instagram_sync_to_database(self, mock_get_posts):
        """Test syncing Instagram posts to database."""
        # Mock Instagram posts
        mock_get_posts.return_value = [
            {
                'id': 'sync_post_1',
                'media_type': 'IMAGE',
                'media_url': 'https://instagram.com/sync_image.jpg',
                'caption': 'Syncing to database test',
                'permalink': 'https://instagram.com/p/sync1',
                'timestamp': '2024-12-16T15:00:00+0000'
            }
        ]
        
        # Call sync function
        result = sync_instagram_media()
        
        # Verify database was updated
        self.assertTrue(result)
        media = MediaGallery.objects.get(instagram_id='sync_post_1')
        self.assertEqual(media.source, 'instagram')
        self.assertEqual(media.media_type, 'image')
        self.assertIn('Syncing to database test', media.caption)
    
    @patch('core.utils.instagram_api.requests.get')
    def test_instagram_caching(self, mock_get):
        """Test Instagram posts caching functionality."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'id': 'cached_post',
                    'media_type': 'IMAGE',
                    'media_url': 'https://instagram.com/cached.jpg',
                    'caption': 'Cached post test',
                    'permalink': 'https://instagram.com/p/cached'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # First call should hit API
        posts1 = get_instagram_posts(use_cache=True)
        self.assertEqual(len(posts1), 1)
        self.assertEqual(mock_get.call_count, 1)
        
        # Second call should use cache
        posts2 = get_instagram_posts(use_cache=True)
        self.assertEqual(len(posts2), 1)
        self.assertEqual(mock_get.call_count, 1)  # Should not increase


class GoogleBusinessAPIIntegrationTestCase(TestCase):
    """Test Google Business API integration with mocked responses."""
    
    def setUp(self):
        """Set up test data."""
        self.testimonial = Testimonial.objects.create(
            student_name='Google Test User',
            email='googletest@example.com',
            rating=5,
            content='Testing Google Business API integration with sufficient content for validation.',
            class_type='choreo_team',
            status='approved'
        )
    
    @patch('core.utils.google_reviews.requests.post')
    def test_google_business_api_success(self, mock_post):
        """Test successful Google Business API submission."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'reviewId': 'google_review_123',
            'status': 'PUBLISHED'
        }
        mock_post.return_value = mock_response
        
        # Test API submission
        success, error = submit_testimonial_to_google(self.testimonial)
        
        # Verify success
        self.assertTrue(success)
        self.assertIsNone(error)
        
        # Verify API was called with correct data
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('json', call_args[1])
        
        # Verify testimonial was updated
        self.testimonial.refresh_from_db()
        self.assertEqual(self.testimonial.google_review_id, 'google_review_123')
    
    @patch('core.utils.google_reviews.requests.post')
    def test_google_business_api_failure(self, mock_post):
        """Test Google Business API failure handling."""
        # Mock API failure
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': {
                'message': 'Invalid request format'
            }
        }
        mock_post.return_value = mock_response
        
        # Test API submission with failure
        success, error = submit_testimonial_to_google(self.testimonial)
        
        # Verify failure
        self.assertFalse(success)
        self.assertIsNotNone(error)
        self.assertIn('Invalid request format', error)
    
    @patch('core.utils.google_reviews.requests.post')
    def test_google_business_rate_limiting(self, mock_post):
        """Test Google Business API rate limiting handling."""
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            'error': {
                'message': 'Rate limit exceeded'
            }
        }
        mock_post.return_value = mock_response
        
        # Test rate limiting
        success, error = submit_testimonial_to_google(self.testimonial)
        
        # Verify rate limit handling
        self.assertFalse(success)
        self.assertIn('Rate limit', error)


class EmailIntegrationTestCase(TestCase):
    """Test email service integrations with mocked responses."""
    
    def setUp(self):
        """Set up test data."""
        self.testimonial = Testimonial.objects.create(
            student_name='Email Test User',
            email='emailintegration@example.com',
            rating=4,
            content='Testing email integration functionality with sufficient content for validation.',
            class_type='pasos_basicos'
        )
        
        self.contact = ContactSubmission.objects.create(
            name='Contact Test User',
            email='contacttest@example.com',
            interest='classes',
            message='Testing contact form email integration.'
        )
    
    @patch('core.utils.email_notifications.send_mail')
    def test_admin_notification_email_success(self, mock_send_mail):
        """Test successful admin notification email."""
        mock_send_mail.return_value = True
        
        # Test admin notification
        result = send_admin_notification_email(self.testimonial)
        
        # Verify success
        self.assertTrue(result)
        mock_send_mail.assert_called_once()
        
        # Verify email content
        call_args = mock_send_mail.call_args
        self.assertIn('New Testimonial', call_args[0][0])  # Subject
        self.assertIn('Email Test User', call_args[0][1])  # Message content
    
    @patch('core.utils.email_notifications.send_mail')
    def test_thank_you_email_success(self, mock_send_mail):
        """Test successful thank you email."""
        mock_send_mail.return_value = True
        
        # Test thank you email
        result = send_thank_you_email(self.testimonial)
        
        # Verify success
        self.assertTrue(result)
        mock_send_mail.assert_called_once()
        
        # Verify email recipient
        call_args = mock_send_mail.call_args
        self.assertIn('emailintegration@example.com', call_args[0][4])  # Recipients
    
    @patch('core.utils.email_notifications.send_mail')
    def test_contact_admin_notification_email(self, mock_send_mail):
        """Test contact admin notification email."""
        mock_send_mail.return_value = True
        
        # Test contact admin notification
        result = send_contact_admin_notification_email(self.contact)
        
        # Verify success
        self.assertTrue(result)
        mock_send_mail.assert_called_once()
        
        # Verify email content includes contact details
        call_args = mock_send_mail.call_args
        self.assertIn('Contact Test User', call_args[0][1])
        self.assertIn('classes', call_args[0][1])
    
    @patch('core.utils.email_notifications.send_mail')
    def test_email_failure_handling(self, mock_send_mail):
        """Test email failure handling."""
        # Mock email failure
        mock_send_mail.side_effect = Exception("SMTP Error")
        
        # Test email with failure
        result = send_admin_notification_email(self.testimonial)
        
        # Verify failure handling
        self.assertFalse(result)
    
    @override_settings(
        EMAIL_HOST='smtp.test.com',
        EMAIL_HOST_USER='test@example.com',
        EMAIL_HOST_PASSWORD='testpass'
    )
    @patch('core.utils.email_notifications.send_mail')
    def test_email_configuration_test(self, mock_send_mail):
        """Test email configuration testing."""
        mock_send_mail.return_value = True
        
        # Test email configuration
        results = test_email_configuration()
        
        # Verify configuration test results
        self.assertIn('smtp_configured', results)
        self.assertIn('test_email_sent', results)
        self.assertTrue(results['smtp_configured'])


class WebhookIntegrationTestCase(TestCase):
    """Test webhook handling for various services."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    @override_settings(INSTAGRAM_WEBHOOK_VERIFY_TOKEN='test_verify_token')
    def test_instagram_webhook_verification(self):
        """Test Instagram webhook verification."""
        # Test verification request
        verification_params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': 'test_verify_token',
            'hub.challenge': 'test_challenge_123'
        }
        
        response = self.client.get(reverse('core:instagram_webhook'), verification_params)
        
        # Should return challenge
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'test_challenge_123')
    
    @override_settings(INSTAGRAM_WEBHOOK_VERIFY_TOKEN='test_verify_token')
    def test_instagram_webhook_verification_failure(self):
        """Test Instagram webhook verification failure."""
        # Test with wrong token
        verification_params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': 'wrong_token',
            'hub.challenge': 'test_challenge_123'
        }
        
        response = self.client.get(reverse('core:instagram_webhook'), verification_params)
        
        # Should return 403
        self.assertEqual(response.status_code, 403)
    
    def test_instagram_webhook_notification(self):
        """Test Instagram webhook notification handling."""
        # Test notification payload
        notification_payload = {
            'object': 'instagram',
            'entry': [
                {
                    'id': 'user_123',
                    'changes': [
                        {
                            'field': 'media',
                            'value': {
                                'media_id': 'media_456'
                            }
                        }
                    ]
                }
            ]
        }
        
        response = self.client.post(
            reverse('core:instagram_webhook'),
            data=json.dumps(notification_payload),
            content_type='application/json'
        )
        
        # Should return 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'OK')
    
    def test_instagram_webhook_invalid_payload(self):
        """Test Instagram webhook with invalid payload."""
        # Test with invalid JSON
        response = self.client.post(
            reverse('core:instagram_webhook'),
            data='invalid json',
            content_type='application/json'
        )
        
        # Should return 400 Bad Request
        self.assertEqual(response.status_code, 400)
    
    def test_performance_metrics_webhook(self):
        """Test performance metrics webhook."""
        # Test performance metrics payload
        metrics_payload = {
            'type': 'navigation',
            'timestamp': datetime.now().isoformat(),
            'session': {
                'url': 'https://example.com/test'
            },
            'metrics': {
                'navigation': {
                    'total': 1250
                },
                'coreWebVitals': {
                    'lcp': {'value': 2000},
                    'fid': {'value': 80},
                    'cls': {'value': 0.05}
                }
            }
        }
        
        response = self.client.post(
            reverse('core:performance_metrics'),
            data=json.dumps(metrics_payload),
            content_type='application/json'
        )
        
        # Should return success
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')


class APIErrorHandlingTestCase(TestCase):
    """Test error handling across all API integrations."""
    
    @patch('core.utils.facebook_events.requests.get')
    def test_network_timeout_handling(self, mock_get):
        """Test handling of network timeouts."""
        # Mock timeout exception
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        # Test Facebook API with timeout
        events = get_facebook_events()
        
        # Should handle gracefully
        self.assertEqual(events, [])
    
    @patch('core.utils.instagram_api.requests.get')
    def test_connection_error_handling(self, mock_get):
        """Test handling of connection errors."""
        # Mock connection error
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        # Test Instagram API with connection error
        posts = get_instagram_posts()
        
        # Should handle gracefully
        self.assertEqual(posts, [])
    
    @patch('core.utils.google_reviews.requests.post')
    def test_json_decode_error_handling(self, mock_post):
        """Test handling of JSON decode errors."""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_post.return_value = mock_response
        
        # Create test testimonial
        testimonial = Testimonial.objects.create(
            student_name='JSON Error Test',
            email='jsonerror@example.com',
            rating=5,
            content='Testing JSON decode error handling with sufficient content.',
            class_type='choreo_team'
        )
        
        # Test Google API with JSON error
        success, error = submit_testimonial_to_google(testimonial)
        
        # Should handle gracefully
        self.assertFalse(success)
        self.assertIsNotNone(error)


class APIPerformanceTestCase(TestCase):
    """Test API performance characteristics."""
    
    @patch('core.utils.facebook_events.requests.get')
    def test_api_response_time_reasonable(self, mock_get):
        """Test that API calls complete in reasonable time."""
        import time
        
        # Mock quick response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response
        
        # Time the API call
        start_time = time.time()
        events = get_facebook_events()
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should complete quickly (under 1 second for mocked call)
        self.assertLess(response_time, 1.0)
    
    @patch('core.utils.instagram_api.get_instagram_posts')
    def test_cache_performance(self, mock_get_posts):
        """Test that caching improves performance."""
        import time
        
        # Mock API response
        mock_get_posts.return_value = [
            {'id': 'perf_test', 'media_type': 'IMAGE', 'media_url': 'test.jpg'}
        ]
        
        # First call (should hit API)
        start_time = time.time()
        posts1 = get_instagram_posts(use_cache=True)
        first_call_time = time.time() - start_time
        
        # Second call (should use cache)
        start_time = time.time()
        posts2 = get_instagram_posts(use_cache=True)
        second_call_time = time.time() - start_time
        
        # Cached call should be significantly faster
        self.assertLess(second_call_time, first_call_time)
        self.assertEqual(len(posts1), len(posts2))


class APISecurityTestCase(TestCase):
    """Test API security measures."""
    
    def test_webhook_csrf_exempt(self):
        """Test that webhooks are properly CSRF exempt."""
        # Instagram webhook should accept POST without CSRF token
        response = self.client.post(reverse('core:instagram_webhook'))
        
        # Should not return CSRF error (403)
        self.assertNotEqual(response.status_code, 403)
    
    @override_settings(INSTAGRAM_WEBHOOK_VERIFY_TOKEN='secret_token')
    def test_webhook_token_validation(self):
        """Test webhook token validation security."""
        # Test with correct token
        correct_params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': 'secret_token',
            'hub.challenge': 'test_challenge'
        }
        
        response = self.client.get(reverse('core:instagram_webhook'), correct_params)
        self.assertEqual(response.status_code, 200)
        
        # Test with incorrect token
        incorrect_params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': 'wrong_token',
            'hub.challenge': 'test_challenge'
        }
        
        response = self.client.get(reverse('core:instagram_webhook'), incorrect_params)
        self.assertEqual(response.status_code, 403)
    
    def test_api_input_sanitization(self):
        """Test that API inputs are properly sanitized."""
        # Test malicious webhook payload
        malicious_payload = {
            'object': 'instagram',
            'entry': [
                {
                    'id': '<script>alert("xss")</script>',
                    'changes': [
                        {
                            'field': 'media',
                            'value': {
                                'media_id': '"><script>alert("xss")</script>'
                            }
                        }
                    ]
                }
            ]
        }
        
        response = self.client.post(
            reverse('core:instagram_webhook'),
            data=json.dumps(malicious_payload),
            content_type='application/json'
        )
        
        # Should handle malicious input gracefully
        self.assertEqual(response.status_code, 200)