"""
Test suite for SPEC_04 Instagram Integration Features

Tests:
- Instagram API utility functions
- Instagram API error handling and rate limiting
- Instagram post synchronization command
- Instagram webhook verification
- Instagram access token management
- Gallery view Instagram integration
"""

import json
import time
from unittest.mock import patch, Mock, MagicMock
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
from io import StringIO

from core.models import MediaGallery
from core.utils.instagram_api import (
    InstagramAPI, InstagramAPIError, get_instagram_posts,
    get_instagram_post_details, refresh_instagram_token
)
from core.management.commands.sync_instagram import Command as SyncInstagramCommand


class InstagramAPITests(TestCase):
    """Test Instagram API utility functions."""
    
    def setUp(self):
        """Set up test data."""
        cache.clear()
        self.api = InstagramAPI(access_token='test_token_123')
        
        # Mock Instagram API response data
        self.mock_media_data = [
            {
                'id': '12345678901234567',
                'media_type': 'IMAGE',
                'media_url': 'https://instagram.com/image1.jpg',
                'thumbnail_url': 'https://instagram.com/thumb1.jpg',
                'permalink': 'https://instagram.com/p/abc123/',
                'caption': 'Dancing at the studio! #salsa #dance #fun',
                'timestamp': '2024-01-15T10:30:00+0000',
                'username': 'sabor_con_flow'
            },
            {
                'id': '23456789012345678',
                'media_type': 'VIDEO',
                'media_url': 'https://instagram.com/video1.mp4',
                'thumbnail_url': 'https://instagram.com/video1_thumb.jpg',
                'permalink': 'https://instagram.com/p/def456/',
                'caption': 'Check out this amazing routine! #bachata #performance',
                'timestamp': '2024-01-14T15:45:00+0000',
                'username': 'sabor_con_flow'
            }
        ]
    
    def test_instagram_api_initialization(self):
        """Test Instagram API initialization."""
        # Test with token
        api_with_token = InstagramAPI(access_token='test_token')
        self.assertEqual(api_with_token.access_token, 'test_token')
        
        # Test without token
        api_without_token = InstagramAPI()
        self.assertIsNone(api_without_token.access_token)
    
    @override_settings(INSTAGRAM_ACCESS_TOKEN='settings_token')
    def test_instagram_api_token_from_settings(self):
        """Test Instagram API token from Django settings."""
        api = InstagramAPI()
        self.assertEqual(api.access_token, 'settings_token')
    
    def test_rate_limit_check(self):
        """Test rate limiting functionality."""
        # Clear any existing rate limit data
        cache.delete('instagram_api_requests')
        
        # Should allow requests when under limit
        self.assertTrue(self.api._check_rate_limit())
        
        # Simulate rate limit exceeded
        now = time.time()
        requests_made = [now - 100] * 200  # 200 requests in last hour
        cache.set('instagram_api_requests', requests_made, 3600)
        
        # Should block when over limit
        self.assertFalse(self.api._check_rate_limit())
    
    def test_rate_limit_cleanup(self):
        """Test rate limit cleanup of old requests."""
        # Add old requests that should be cleaned up
        now = time.time()
        old_requests = [now - 7200] * 50  # 2 hours ago
        recent_requests = [now - 1800] * 50  # 30 minutes ago
        
        cache.set('instagram_api_requests', old_requests + recent_requests, 7200)
        
        # Should clean up old requests and allow new ones
        self.assertTrue(self.api._check_rate_limit())
        
        # Verify cleanup happened
        cached_requests = cache.get('instagram_api_requests', [])
        self.assertEqual(len(cached_requests), 51)  # 50 recent + 1 new
    
    @patch('core.utils.instagram_api.requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': self.mock_media_data}
        mock_get.return_value = mock_response
        
        result = self.api._make_request('me/media')
        
        self.assertEqual(result, {'data': self.mock_media_data})
        mock_get.assert_called_once()
    
    @patch('core.utils.instagram_api.requests.Session.get')
    def test_make_request_auth_error(self, mock_get):
        """Test API request with authentication error."""
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'error': {
                'message': 'Invalid access token',
                'type': 'auth_error'
            }
        }
        mock_get.return_value = mock_response
        
        with self.assertRaises(InstagramAPIError) as context:
            self.api._make_request('me/media')
        
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.error_type, 'auth_error')
    
    @patch('core.utils.instagram_api.requests.Session.get')
    def test_make_request_rate_limit_error(self, mock_get):
        """Test API request with rate limit error."""
        # Mock 429 response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        with self.assertRaises(InstagramAPIError) as context:
            self.api._make_request('me/media')
        
        self.assertEqual(context.exception.status_code, 429)
        self.assertEqual(context.exception.error_type, 'rate_limit')
    
    @patch('core.utils.instagram_api.requests.Session.get')
    def test_make_request_server_error_retry(self, mock_get):
        """Test API request retry logic for server errors."""
        # Mock server error that succeeds on retry
        mock_response_error = Mock()
        mock_response_error.status_code = 500
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {'data': []}
        
        mock_get.side_effect = [mock_response_error, mock_response_success]
        
        result = self.api._make_request('me/media', retries=2)
        self.assertEqual(result, {'data': []})
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('core.utils.instagram_api.requests.Session.get')
    def test_make_request_network_error_retry(self, mock_get):
        """Test API request retry logic for network errors."""
        import requests
        
        # Mock network error that succeeds on retry
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {'data': []}
        
        mock_get.side_effect = [
            requests.exceptions.ConnectionError("Network error"),
            mock_response_success
        ]
        
        result = self.api._make_request('me/media', retries=2)
        self.assertEqual(result, {'data': []})
        self.assertEqual(mock_get.call_count, 2)
    
    def test_make_request_no_token(self):
        """Test API request without access token."""
        api_no_token = InstagramAPI()
        
        with self.assertRaises(InstagramAPIError) as context:
            api_no_token._make_request('me/media')
        
        self.assertEqual(context.exception.error_type, 'auth_error')
        self.assertIn('not configured', context.exception.message)
    
    @patch.object(InstagramAPI, '_make_request')
    def test_get_user_media_success(self, mock_make_request):
        """Test successful user media retrieval."""
        mock_make_request.return_value = {'data': self.mock_media_data}
        
        result = self.api.get_user_media(limit=2, use_cache=False)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], '12345678901234567')
        self.assertEqual(result[0]['media_type'], 'image')  # Normalized
        self.assertEqual(result[1]['media_type'], 'video')  # Normalized
        
        # Verify API call
        mock_make_request.assert_called_once_with('me/media', {
            'fields': self.api.MEDIA_FIELDS,
            'limit': 2
        })
    
    @patch.object(InstagramAPI, '_make_request')
    def test_get_user_media_caching(self, mock_make_request):
        """Test user media caching functionality."""
        mock_make_request.return_value = {'data': self.mock_media_data}
        
        # First call should hit API and cache result
        result1 = self.api.get_user_media(limit=2, use_cache=True)
        self.assertEqual(len(result1), 2)
        mock_make_request.assert_called_once()
        
        # Second call should use cache
        result2 = self.api.get_user_media(limit=2, use_cache=True)
        self.assertEqual(len(result2), 2)
        self.assertEqual(result1, result2)
        # Should not call API again
        mock_make_request.assert_called_once()
    
    @patch.object(InstagramAPI, '_make_request')
    def test_get_user_media_api_error(self, mock_make_request):
        """Test user media retrieval with API error."""
        mock_make_request.side_effect = InstagramAPIError("API Error", error_type="api_error")
        
        # Should return empty list on error
        result = self.api.get_user_media(use_cache=False)
        self.assertEqual(result, [])
    
    @patch.object(InstagramAPI, '_make_request')
    def test_get_user_media_stale_cache_on_error(self, mock_make_request):
        """Test returning stale cache data when API fails."""
        # First, populate cache with successful data
        mock_make_request.return_value = {'data': self.mock_media_data}
        result1 = self.api.get_user_media(use_cache=True)
        self.assertEqual(len(result1), 2)
        
        # Then simulate API error
        mock_make_request.side_effect = InstagramAPIError("API Error")
        
        # Should return cached data despite error
        result2 = self.api.get_user_media(use_cache=True)
        self.assertEqual(len(result2), 2)
        self.assertEqual(result1, result2)
    
    def test_normalize_media_data(self):
        """Test media data normalization."""
        # Test IMAGE normalization
        image_data = {
            'id': '123',
            'media_type': 'IMAGE',
            'media_url': 'https://example.com/image.jpg',
            'caption': 'Test caption',
            'timestamp': '2024-01-15T10:30:00+0000',
            'username': 'testuser'
        }
        
        normalized = self.api._normalize_media_data(image_data)
        
        self.assertEqual(normalized['id'], '123')
        self.assertEqual(normalized['media_type'], 'image')
        self.assertEqual(normalized['media_url'], 'https://example.com/image.jpg')
        self.assertEqual(normalized['caption'], 'Test caption')
        self.assertEqual(normalized['username'], 'testuser')
        self.assertEqual(normalized['source'], 'instagram')
        self.assertIsInstance(normalized['created_at'], datetime)
        
        # Test VIDEO normalization
        video_data = {
            'id': '456',
            'media_type': 'VIDEO',
            'media_url': 'https://example.com/video.mp4',
            'timestamp': '2024-01-15T10:30:00+0000'
        }
        
        normalized = self.api._normalize_media_data(video_data)
        self.assertEqual(normalized['media_type'], 'video')
        
        # Test CAROUSEL_ALBUM normalization
        carousel_data = {
            'id': '789',
            'media_type': 'CAROUSEL_ALBUM',
            'media_url': 'https://example.com/carousel.jpg'
        }
        
        normalized = self.api._normalize_media_data(carousel_data)
        self.assertEqual(normalized['media_type'], 'image')
    
    def test_normalize_media_data_invalid_timestamp(self):
        """Test media data normalization with invalid timestamp."""
        data = {
            'id': '123',
            'media_type': 'IMAGE',
            'timestamp': 'invalid-timestamp'
        }
        
        normalized = self.api._normalize_media_data(data)
        self.assertIsNone(normalized['created_at'])
    
    @patch.object(InstagramAPI, '_make_request')
    def test_get_media_details(self, mock_make_request):
        """Test getting specific media details."""
        media_data = self.mock_media_data[0]
        mock_make_request.return_value = media_data
        
        result = self.api.get_media_details('12345678901234567')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], '12345678901234567')
        self.assertEqual(result['media_type'], 'image')
        
        mock_make_request.assert_called_once_with(
            '12345678901234567',
            {'fields': self.api.MEDIA_FIELDS}
        )
    
    @patch.object(InstagramAPI, '_make_request')
    def test_get_media_details_error(self, mock_make_request):
        """Test get media details with API error."""
        mock_make_request.side_effect = InstagramAPIError("Not found", status_code=404)
        
        result = self.api.get_media_details('invalid_id')
        self.assertIsNone(result)
    
    def test_verify_webhook_success(self):
        """Test successful webhook verification."""
        result = self.api.verify_webhook(
            verify_token='my_verify_token',
            challenge='challenge_123',
            provided_token='my_verify_token'
        )
        
        self.assertEqual(result, 'challenge_123')
    
    def test_verify_webhook_failure(self):
        """Test failed webhook verification."""
        result = self.api.verify_webhook(
            verify_token='my_verify_token',
            challenge='challenge_123',
            provided_token='wrong_token'
        )
        
        self.assertIsNone(result)
    
    @patch.object(InstagramAPI, '_make_request')
    def test_refresh_access_token_success(self, mock_make_request):
        """Test successful access token refresh."""
        mock_make_request.return_value = {
            'access_token': 'new_token_456',
            'expires_in': 5184000  # 60 days
        }
        
        success, result = self.api.refresh_access_token()
        
        self.assertTrue(success)
        self.assertEqual(result, 'new_token_456')
        
        mock_make_request.assert_called_once_with(
            'refresh_access_token',
            {
                'grant_type': 'ig_refresh_token',
                'access_token': 'test_token_123'
            }
        )
    
    @patch.object(InstagramAPI, '_make_request')
    def test_refresh_access_token_error(self, mock_make_request):
        """Test access token refresh error."""
        mock_make_request.side_effect = InstagramAPIError("Invalid token", error_type="auth_error")
        
        success, result = self.api.refresh_access_token()
        
        self.assertFalse(success)
        self.assertEqual(result, "Invalid token")


class InstagramUtilityFunctionTests(TestCase):
    """Test Instagram utility functions."""
    
    @patch('core.utils.instagram_api.InstagramAPI')
    def test_get_instagram_posts(self, mock_api_class):
        """Test get_instagram_posts utility function."""
        mock_api = Mock()
        mock_api.get_user_media.return_value = [
            {'id': '1', 'media_type': 'image'},
            {'id': '2', 'media_type': 'video'}
        ]
        mock_api_class.return_value = mock_api
        
        result = get_instagram_posts(limit=5, use_cache=False)
        
        self.assertEqual(len(result), 2)
        mock_api.get_user_media.assert_called_once_with(limit=5, use_cache=False)
    
    @patch('core.utils.instagram_api.InstagramAPI')
    def test_get_instagram_post_details(self, mock_api_class):
        """Test get_instagram_post_details utility function."""
        mock_api = Mock()
        mock_api.get_media_details.return_value = {'id': '123', 'media_type': 'image'}
        mock_api_class.return_value = mock_api
        
        result = get_instagram_post_details('123')
        
        self.assertEqual(result['id'], '123')
        mock_api.get_media_details.assert_called_once_with('123')
    
    @patch('core.utils.instagram_api.InstagramAPI')
    def test_refresh_instagram_token(self, mock_api_class):
        """Test refresh_instagram_token utility function."""
        mock_api = Mock()
        mock_api.refresh_access_token.return_value = (True, 'new_token')
        mock_api_class.return_value = mock_api
        
        success, token = refresh_instagram_token()
        
        self.assertTrue(success)
        self.assertEqual(token, 'new_token')
        mock_api.refresh_access_token.assert_called_once()


class SyncInstagramCommandTests(TestCase):
    """Test the sync_instagram management command."""
    
    def setUp(self):
        """Set up test data."""
        cache.clear()
        
        # Create existing Instagram media
        self.existing_media = MediaGallery.objects.create(
            title='Existing Instagram Post',
            media_type='image',
            category='instagram',
            source='instagram',
            instagram_id='existing_123',
            instagram_permalink='https://instagram.com/p/existing123/',
            url='https://instagram.com/existing.jpg'
        )
    
    @patch('core.utils.instagram_api.InstagramAPI')
    def test_sync_instagram_command_basic(self, mock_api_class):
        """Test basic sync instagram command functionality."""
        # Mock API response
        mock_api = Mock()
        mock_api.get_user_media.return_value = [
            {
                'id': 'new_post_123',
                'media_type': 'image',
                'media_url': 'https://instagram.com/new.jpg',
                'caption': 'New Instagram post',
                'permalink': 'https://instagram.com/p/new123/',
                'username': 'sabor_con_flow',
                'created_at': timezone.now()
            }
        ]
        mock_api_class.return_value = mock_api
        
        # Capture command output
        out = StringIO()
        call_command('sync_instagram', '--limit=1', stdout=out)
        
        # Verify new media was created
        new_media = MediaGallery.objects.filter(instagram_id='new_post_123').first()
        self.assertIsNotNone(new_media)
        self.assertEqual(new_media.title, 'New Instagram post')
        self.assertEqual(new_media.source, 'instagram')
        
        # Verify command output
        output = out.getvalue()
        self.assertIn('Starting Instagram sync', output)
        self.assertIn('Created:', output)
    
    @patch('core.utils.instagram_api.InstagramAPI')
    def test_sync_instagram_command_update_existing(self, mock_api_class):
        """Test updating existing Instagram posts."""
        # Mock API response with updated data
        mock_api = Mock()
        mock_api.get_user_media.return_value = [
            {
                'id': 'existing_123',
                'media_type': 'image',
                'media_url': 'https://instagram.com/existing_updated.jpg',
                'caption': 'Updated caption for existing post',
                'permalink': 'https://instagram.com/p/existing123/',
                'username': 'sabor_con_flow',
                'created_at': timezone.now()
            }
        ]
        mock_api_class.return_value = mock_api
        
        out = StringIO()
        call_command('sync_instagram', '--limit=1', stdout=out)
        
        # Verify existing media was updated
        updated_media = MediaGallery.objects.get(instagram_id='existing_123')
        self.assertEqual(updated_media.caption, 'Updated caption for existing post')
        self.assertEqual(updated_media.url, 'https://instagram.com/existing_updated.jpg')
        
        # Verify command output
        output = out.getvalue()
        self.assertIn('Updated:', output)
    
    @patch('core.utils.instagram_api.InstagramAPI')
    def test_sync_instagram_command_dry_run(self, mock_api_class):
        """Test sync instagram command in dry run mode."""
        mock_api = Mock()
        mock_api.get_user_media.return_value = [
            {
                'id': 'dry_run_123',
                'media_type': 'image',
                'media_url': 'https://instagram.com/dryrun.jpg',
                'caption': 'Dry run post',
                'permalink': 'https://instagram.com/p/dryrun123/',
                'username': 'sabor_con_flow',
                'created_at': timezone.now()
            }
        ]
        mock_api_class.return_value = mock_api
        
        out = StringIO()
        call_command('sync_instagram', '--dry-run', '--limit=1', stdout=out)
        
        # Verify no media was actually created
        dry_run_media = MediaGallery.objects.filter(instagram_id='dry_run_123').first()
        self.assertIsNone(dry_run_media)
        
        # Verify dry run output
        output = out.getvalue()
        self.assertIn('DRY RUN MODE', output)
        self.assertIn('Would create:', output)
    
    @patch('core.utils.instagram_api.InstagramAPI')
    def test_sync_instagram_command_delete_removed(self, mock_api_class):
        """Test deleting posts no longer on Instagram."""
        # Mock API returning no posts (simulating removed posts)
        mock_api = Mock()
        mock_api.get_user_media.return_value = []
        mock_api_class.return_value = mock_api
        
        # Verify existing media exists
        self.assertTrue(MediaGallery.objects.filter(instagram_id='existing_123').exists())
        
        out = StringIO()
        call_command('sync_instagram', '--delete-removed', stdout=out)
        
        # Verify existing media was deleted
        self.assertFalse(MediaGallery.objects.filter(instagram_id='existing_123').exists())
        
        # Verify command output
        output = out.getvalue()
        self.assertIn('Deleting removed Instagram post', output)
    
    @patch('core.utils.instagram_api.InstagramAPI')
    def test_sync_instagram_command_custom_category(self, mock_api_class):
        """Test sync with custom category."""
        mock_api = Mock()
        mock_api.get_user_media.return_value = [
            {
                'id': 'custom_cat_123',
                'media_type': 'image',
                'media_url': 'https://instagram.com/custom.jpg',
                'caption': 'Custom category post',
                'permalink': 'https://instagram.com/p/custom123/',
                'username': 'sabor_con_flow',
                'created_at': timezone.now()
            }
        ]
        mock_api_class.return_value = mock_api
        
        out = StringIO()
        call_command('sync_instagram', '--category=social', '--limit=1', stdout=out)
        
        # Verify media was created with custom category
        new_media = MediaGallery.objects.filter(instagram_id='custom_cat_123').first()
        self.assertIsNotNone(new_media)
        self.assertEqual(new_media.category, 'social')
    
    def test_sync_instagram_command_invalid_category(self):
        """Test sync with invalid category."""
        with self.assertRaises(CommandError) as context:
            call_command('sync_instagram', '--category=invalid_category')
        
        self.assertIn('Invalid category', str(context.exception))
    
    @patch('core.utils.instagram_api.InstagramAPI')
    def test_sync_instagram_command_api_error(self, mock_api_class):
        """Test sync command with Instagram API error."""
        mock_api = Mock()
        mock_api.get_user_media.side_effect = InstagramAPIError("API Error", error_type="api_error")
        mock_api_class.return_value = mock_api
        
        with self.assertRaises(CommandError) as context:
            call_command('sync_instagram')
        
        self.assertIn('Instagram API error', str(context.exception))
    
    @patch('core.utils.instagram_api.InstagramAPI')
    def test_sync_instagram_command_hashtag_extraction(self, mock_api_class):
        """Test hashtag extraction from captions."""
        mock_api = Mock()
        mock_api.get_user_media.return_value = [
            {
                'id': 'hashtag_test_123',
                'media_type': 'image',
                'media_url': 'https://instagram.com/hashtag.jpg',
                'caption': 'Dancing tonight! #salsa #bachata #dance #fun #studio',
                'permalink': 'https://instagram.com/p/hashtag123/',
                'username': 'sabor_con_flow',
                'created_at': timezone.now()
            }
        ]
        mock_api_class.return_value = mock_api
        
        call_command('sync_instagram', '--limit=1')
        
        # Verify hashtags were extracted as tags
        new_media = MediaGallery.objects.filter(instagram_id='hashtag_test_123').first()
        self.assertIsNotNone(new_media)
        
        tags_list = new_media.get_tags_list()
        expected_tags = ['salsa', 'bachata', 'dance', 'fun', 'studio']
        self.assertEqual(tags_list, expected_tags)


class InstagramIntegrationTests(TestCase):
    """Test Instagram integration in gallery view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        cache.clear()
    
    @patch('core.utils.instagram_api.get_instagram_posts')
    def test_gallery_instagram_integration(self, mock_get_posts):
        """Test Instagram posts in gallery view."""
        # Mock Instagram posts
        mock_get_posts.return_value = [
            {
                'id': 'insta_1',
                'media_type': 'image',
                'media_url': 'https://instagram.com/image1.jpg',
                'caption': 'Instagram post 1',
                'permalink': 'https://instagram.com/p/insta1/'
            },
            {
                'id': 'insta_2',
                'media_type': 'video',
                'media_url': 'https://instagram.com/video1.mp4',
                'caption': 'Instagram post 2',
                'permalink': 'https://instagram.com/p/insta2/'
            }
        ]
        
        response = self.client.get(reverse('core:gallery_view'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['instagram_posts']), 2)
        self.assertEqual(response.context['instagram_count'], 2)
        
        # Verify Instagram API was called correctly
        mock_get_posts.assert_called_once_with(limit=8, use_cache=True)
    
    @patch('core.utils.instagram_api.get_instagram_posts')
    def test_gallery_instagram_disabled(self, mock_get_posts):
        """Test gallery with Instagram disabled."""
        response = self.client.get(reverse('core:gallery_view'), {'instagram': 'false'})
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['show_instagram'])
        self.assertEqual(response.context['instagram_posts'], [])
        
        # Instagram API should not be called when disabled
        mock_get_posts.assert_not_called()
    
    @patch('core.utils.instagram_api.get_instagram_posts')
    def test_gallery_instagram_error_handling(self, mock_get_posts):
        """Test gallery with Instagram API error."""
        # Mock Instagram API error
        mock_get_posts.side_effect = Exception("Instagram API error")
        
        response = self.client.get(reverse('core:gallery_view'))
        
        # Should handle error gracefully
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['instagram_posts'], [])
        self.assertEqual(response.context['instagram_count'], 0)


class InstagramErrorHandlingTests(TestCase):
    """Test Instagram API error handling."""
    
    def test_instagram_api_error_creation(self):
        """Test InstagramAPIError creation."""
        error = InstagramAPIError(
            message="Test error",
            status_code=400,
            error_type="test_error"
        )
        
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.error_type, "test_error")
        self.assertEqual(str(error), "Test error")
    
    def test_instagram_api_error_minimal(self):
        """Test InstagramAPIError with minimal parameters."""
        error = InstagramAPIError("Simple error")
        
        self.assertEqual(error.message, "Simple error")
        self.assertIsNone(error.status_code)
        self.assertIsNone(error.error_type)


class InstagramCachingTests(TestCase):
    """Test Instagram API caching behavior."""
    
    def setUp(self):
        """Set up test data."""
        cache.clear()
        self.api = InstagramAPI(access_token='test_token')
    
    @patch.object(InstagramAPI, '_make_request')
    def test_media_details_caching(self, mock_make_request):
        """Test media details caching."""
        mock_make_request.return_value = {
            'id': '123',
            'media_type': 'IMAGE',
            'media_url': 'https://example.com/image.jpg'
        }
        
        # First call
        result1 = self.api.get_media_details('123')
        self.assertIsNotNone(result1)
        mock_make_request.assert_called_once()
        
        # Second call should use cache
        result2 = self.api.get_media_details('123')
        self.assertEqual(result1, result2)
        # Should not call API again
        mock_make_request.assert_called_once()
    
    def test_rate_limit_caching(self):
        """Test rate limit request tracking in cache."""
        cache.delete('instagram_api_requests')
        
        # Make a few requests
        for i in range(3):
            self.api._check_rate_limit()
        
        # Verify requests are tracked in cache
        cached_requests = cache.get('instagram_api_requests', [])
        self.assertEqual(len(cached_requests), 3)