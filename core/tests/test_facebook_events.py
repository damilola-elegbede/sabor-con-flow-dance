"""
Test suite for Facebook Events integration - SPEC_05 Group B Tasks 5-6.

Tests API integration, caching, database models, views, and error handling.
"""

import json
import logging
from datetime import datetime, timezone
from unittest.mock import patch, Mock, MagicMock
from django.test import TestCase, RequestFactory, override_settings
from django.core.cache import cache
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone as django_timezone
from io import StringIO

from core.models import FacebookEvent
from core.utils.facebook_events import (
    FacebookEventsAPI, 
    get_facebook_events, 
    clear_facebook_events_cache,
    get_facebook_api_status
)
from core.views import schedule_view


class FacebookEventsAPITest(TestCase):
    """Test Facebook Events API integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.api = FacebookEventsAPI()
        cache.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    @override_settings(
        FACEBOOK_ACCESS_TOKEN='test_token',
        FACEBOOK_PAGE_ID='test_page_id'
    )
    @patch.dict('os.environ', {
        'FACEBOOK_ACCESS_TOKEN': 'test_token',
        'FACEBOOK_PAGE_ID': 'test_page_id'
    })
    def test_api_configuration_valid(self):
        """Test API configuration validation."""
        api = FacebookEventsAPI()
        is_valid, message = api._validate_config()
        
        self.assertTrue(is_valid)
        self.assertEqual(message, "Configuration valid")
    
    @patch.dict('os.environ', {}, clear=True)
    def test_api_configuration_missing_token(self):
        """Test API configuration with missing access token."""
        api = FacebookEventsAPI()
        is_valid, message = api._validate_config()
        
        self.assertFalse(is_valid)
        self.assertIn("access token", message.lower())
    
    @patch.dict('os.environ', {'FACEBOOK_ACCESS_TOKEN': 'test_token'})
    def test_api_configuration_missing_page_id(self):
        """Test API configuration with missing page ID."""
        api = FacebookEventsAPI()
        is_valid, message = api._validate_config()
        
        self.assertFalse(is_valid)
        self.assertIn("page id", message.lower())
    
    @patch('core.utils.facebook_events.requests.get')
    @patch.dict('os.environ', {
        'FACEBOOK_ACCESS_TOKEN': 'test_token',
        'FACEBOOK_PAGE_ID': 'test_page_id'
    })
    def test_api_request_success(self, mock_get):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {
                    'id': '123456789',
                    'name': 'Test Event',
                    'start_time': '2024-12-25T19:00:00-0700',
                    'description': 'Test event description'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        api = FacebookEventsAPI()
        result = api._make_api_request('test_page_id/events', {'limit': 5})
        
        self.assertIsNotNone(result)
        self.assertIn('data', result)
        self.assertEqual(len(result['data']), 1)
        mock_get.assert_called_once()
    
    @patch('core.utils.facebook_events.requests.get')
    @patch.dict('os.environ', {
        'FACEBOOK_ACCESS_TOKEN': 'test_token',
        'FACEBOOK_PAGE_ID': 'test_page_id'
    })
    def test_api_request_timeout(self, mock_get):
        """Test API request timeout handling."""
        mock_get.side_effect = Exception("Connection timeout")
        
        api = FacebookEventsAPI()
        result = api._make_api_request('test_page_id/events', {'limit': 5})
        
        self.assertIsNone(result)
    
    def test_filter_future_events(self):
        """Test filtering future events."""
        # Create test events (some past, some future)
        now = datetime.now(timezone.utc)
        future_time = now.replace(year=now.year + 1).isoformat()
        past_time = now.replace(year=now.year - 1).isoformat()
        
        events = [
            {'id': '1', 'start_time': future_time, 'name': 'Future Event'},
            {'id': '2', 'start_time': past_time, 'name': 'Past Event'},
            {'id': '3', 'start_time': future_time, 'name': 'Another Future Event'},
        ]
        
        api = FacebookEventsAPI()
        future_events = api._filter_future_events(events)
        
        self.assertEqual(len(future_events), 2)
        self.assertEqual(future_events[0]['name'], 'Future Event')
        self.assertEqual(future_events[1]['name'], 'Another Future Event')
    
    def test_extract_event_data(self):
        """Test event data extraction."""
        raw_event = {
            'id': '123456789',
            'name': 'Salsa Workshop',
            'description': 'Join us for an amazing salsa workshop with live music and professional instructors!',
            'start_time': '2024-12-25T19:00:00-0700',
            'cover': {
                'source': 'https://example.com/event-cover.jpg'
            }
        }
        
        api = FacebookEventsAPI()
        extracted = api._extract_event_data(raw_event)
        
        self.assertEqual(extracted['id'], '123456789')
        self.assertEqual(extracted['name'], 'Salsa Workshop')
        self.assertEqual(extracted['start_time'], '2024-12-25T19:00:00-0700')
        self.assertEqual(extracted['cover_photo'], 'https://example.com/event-cover.jpg')
        self.assertIn('facebook.com/events/123456789', extracted['facebook_url'])
        self.assertEqual(extracted['formatted_date'], 'December 25, 2024')
        self.assertEqual(extracted['formatted_time'], '07:00 PM')
    
    def test_extract_event_data_long_description(self):
        """Test event data extraction with long description."""
        raw_event = {
            'id': '123456789',
            'name': 'Test Event',
            'description': 'A' * 300,  # Long description
            'start_time': '2024-12-25T19:00:00-0700'
        }
        
        api = FacebookEventsAPI()
        extracted = api._extract_event_data(raw_event)
        
        self.assertEqual(len(extracted['description']), 200)
        self.assertTrue(extracted['description'].endswith('...'))
    
    @patch('core.utils.facebook_events.FacebookEventsAPI._make_api_request')
    @patch.dict('os.environ', {
        'FACEBOOK_ACCESS_TOKEN': 'test_token',
        'FACEBOOK_PAGE_ID': 'test_page_id'
    })
    def test_get_upcoming_events_with_cache(self, mock_api_request):
        """Test getting upcoming events with caching."""
        # Mock API response
        mock_api_request.return_value = {
            'data': [
                {
                    'id': '123456789',
                    'name': 'Test Event',
                    'start_time': '2024-12-25T19:00:00-0700',
                    'description': 'Test description'
                }
            ]
        }
        
        api = FacebookEventsAPI()
        
        # First call should hit API
        events1 = api.get_upcoming_events(limit=5, use_cache=True)
        self.assertEqual(len(events1), 1)
        self.assertEqual(mock_api_request.call_count, 1)
        
        # Second call should use cache
        events2 = api.get_upcoming_events(limit=5, use_cache=True)
        self.assertEqual(len(events2), 1)
        self.assertEqual(mock_api_request.call_count, 1)  # Should not increase
        
        # Verify cached data
        self.assertEqual(events1[0]['id'], events2[0]['id'])


class FacebookEventModelTest(TestCase):
    """Test FacebookEvent model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.future_time = django_timezone.now() + django_timezone.timedelta(days=7)
        self.past_time = django_timezone.now() - django_timezone.timedelta(days=7)
    
    def test_create_facebook_event(self):
        """Test creating a Facebook event."""
        event = FacebookEvent.objects.create(
            facebook_id='123456789',
            name='Test Event',
            description='Test description',
            start_time=self.future_time,
            formatted_date='December 25, 2024',
            formatted_time='7:00 PM',
            facebook_url='https://facebook.com/events/123456789'
        )
        
        self.assertEqual(event.name, 'Test Event')
        self.assertEqual(event.facebook_id, '123456789')
        self.assertTrue(event.is_active)
        self.assertFalse(event.featured)
    
    def test_get_short_description(self):
        """Test getting shortened description."""
        long_desc = 'A' * 200
        event = FacebookEvent.objects.create(
            facebook_id='123456789',
            name='Test Event',
            description=long_desc,
            start_time=self.future_time,
            facebook_url='https://facebook.com/events/123456789'
        )
        
        short_desc = event.get_short_description(max_length=100)
        self.assertEqual(len(short_desc), 100)
        self.assertTrue(short_desc.endswith('...'))
    
    def test_is_future_event(self):
        """Test future event detection."""
        future_event = FacebookEvent.objects.create(
            facebook_id='123456789',
            name='Future Event',
            start_time=self.future_time,
            facebook_url='https://facebook.com/events/123456789'
        )
        
        past_event = FacebookEvent.objects.create(
            facebook_id='987654321',
            name='Past Event',
            start_time=self.past_time,
            facebook_url='https://facebook.com/events/987654321'
        )
        
        self.assertTrue(future_event.is_future_event())
        self.assertFalse(past_event.is_future_event())
    
    def test_get_time_until_event(self):
        """Test time until event calculation."""
        # Today's event
        today_event = FacebookEvent.objects.create(
            facebook_id='today',
            name='Today Event',
            start_time=django_timezone.now() + django_timezone.timedelta(hours=2),
            facebook_url='https://facebook.com/events/today'
        )
        
        # Tomorrow's event
        tomorrow_event = FacebookEvent.objects.create(
            facebook_id='tomorrow',
            name='Tomorrow Event',
            start_time=django_timezone.now() + django_timezone.timedelta(days=1, hours=1),
            facebook_url='https://facebook.com/events/tomorrow'
        )
        
        # Past event
        past_event = FacebookEvent.objects.create(
            facebook_id='past',
            name='Past Event',
            start_time=self.past_time,
            facebook_url='https://facebook.com/events/past'
        )
        
        self.assertEqual(today_event.get_time_until_event(), "Today")
        self.assertEqual(tomorrow_event.get_time_until_event(), "Tomorrow")
        self.assertEqual(past_event.get_time_until_event(), "Past event")
    
    def test_get_upcoming_events_classmethod(self):
        """Test getting upcoming events classmethod."""
        # Create test events
        FacebookEvent.objects.create(
            facebook_id='future1',
            name='Future Event 1',
            start_time=self.future_time,
            facebook_url='https://facebook.com/events/future1',
            is_active=True
        )
        
        FacebookEvent.objects.create(
            facebook_id='future2',
            name='Future Event 2',
            start_time=self.future_time + django_timezone.timedelta(days=1),
            facebook_url='https://facebook.com/events/future2',
            is_active=True
        )
        
        FacebookEvent.objects.create(
            facebook_id='past',
            name='Past Event',
            start_time=self.past_time,
            facebook_url='https://facebook.com/events/past',
            is_active=True
        )
        
        FacebookEvent.objects.create(
            facebook_id='inactive',
            name='Inactive Event',
            start_time=self.future_time,
            facebook_url='https://facebook.com/events/inactive',
            is_active=False
        )
        
        upcoming = FacebookEvent.get_upcoming_events(limit=5)
        
        self.assertEqual(len(upcoming), 2)
        self.assertEqual(upcoming[0].name, 'Future Event 1')
        self.assertEqual(upcoming[1].name, 'Future Event 2')


class FacebookEventsViewTest(TestCase):
    """Test Facebook events in schedule view."""
    
    def setUp(self):
        """Set up test environment."""
        self.factory = RequestFactory()
        cache.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    @patch('core.utils.facebook_events.get_facebook_events')
    def test_schedule_view_with_facebook_events(self, mock_get_events):
        """Test schedule view with Facebook events."""
        # Mock Facebook events
        mock_get_events.return_value = [
            {
                'id': '123456789',
                'name': 'Salsa Workshop',
                'description': 'Amazing workshop',
                'formatted_date': 'December 25, 2024',
                'formatted_time': '7:00 PM',
                'cover_photo': 'https://example.com/cover.jpg',
                'facebook_url': 'https://facebook.com/events/123456789'
            }
        ]
        
        request = self.factory.get('/schedule/')
        response = schedule_view(request)
        
        self.assertEqual(response.status_code, 200)
        mock_get_events.assert_called_once_with(limit=5, use_cache=True)
    
    @patch('core.utils.facebook_events.get_facebook_events')
    def test_schedule_view_facebook_api_failure(self, mock_get_events):
        """Test schedule view when Facebook API fails."""
        # Mock API failure
        mock_get_events.side_effect = Exception("API Error")
        
        request = self.factory.get('/schedule/')
        response = schedule_view(request)
        
        # Should not crash, should handle gracefully
        self.assertEqual(response.status_code, 200)
    
    @patch('core.utils.facebook_events.get_facebook_events')
    def test_schedule_view_database_fallback(self, mock_get_events):
        """Test schedule view falling back to database."""
        # Mock API returning empty
        mock_get_events.return_value = []
        
        # Create database event
        future_time = django_timezone.now() + django_timezone.timedelta(days=7)
        FacebookEvent.objects.create(
            facebook_id='db_event',
            name='Database Event',
            description='From database',
            start_time=future_time,
            formatted_date='December 25, 2024',
            formatted_time='7:00 PM',
            facebook_url='https://facebook.com/events/db_event',
            is_active=True
        )
        
        request = self.factory.get('/schedule/')
        response = schedule_view(request)
        
        self.assertEqual(response.status_code, 200)


class FacebookEventsSyncCommandTest(TestCase):
    """Test Facebook events sync management command."""
    
    @patch('core.management.commands.sync_facebook_events.get_facebook_api_status')
    def test_sync_command_api_not_configured(self, mock_status):
        """Test sync command when API is not configured."""
        mock_status.return_value = {
            'configured': False,
            'config_message': 'Facebook access token not configured'
        }
        
        from django.core.management.base import CommandError
        with self.assertRaises(CommandError):
            call_command('sync_facebook_events', verbosity=0)
    
    @patch('core.management.commands.sync_facebook_events.FacebookEventsAPI')
    @patch('core.management.commands.sync_facebook_events.get_facebook_api_status')
    def test_sync_command_success(self, mock_status, mock_api_class):
        """Test successful sync command execution."""
        # Mock API status
        mock_status.return_value = {
            'configured': True,
            'api_accessible': True,
            'page_accessible': True,
            'page_name': 'Test Page'
        }
        
        # Mock API instance
        mock_api = Mock()
        mock_api.get_upcoming_events.return_value = [
            {
                'id': '123456789',
                'name': 'Test Event',
                'description': 'Test description',
                'start_time': '2024-12-25T19:00:00-0700',
                'formatted_date': 'December 25, 2024',
                'formatted_time': '7:00 PM',
                'facebook_url': 'https://facebook.com/events/123456789'
            }
        ]
        mock_api_class.return_value = mock_api
        
        # Capture command output
        out = StringIO()
        call_command('sync_facebook_events', verbosity=1, stdout=out)
        
        output = out.getvalue()
        self.assertIn('completed', output.lower())
    
    def test_sync_command_dry_run(self):
        """Test sync command in dry-run mode."""
        out = StringIO()
        
        with patch('core.management.commands.sync_facebook_events.get_facebook_api_status') as mock_status:
            mock_status.return_value = {
                'configured': True,
                'api_accessible': True,
                'page_accessible': True
            }
            
            with patch('core.management.commands.sync_facebook_events.FacebookEventsAPI') as mock_api_class:
                mock_api = Mock()
                mock_api.get_upcoming_events.return_value = []
                mock_api_class.return_value = mock_api
                
                call_command('sync_facebook_events', dry_run=True, verbosity=1, stdout=out)
        
        output = out.getvalue()
        self.assertIn('DRY RUN', output)


class FacebookEventsCacheTest(TestCase):
    """Test Facebook events caching functionality."""
    
    def setUp(self):
        """Set up test environment."""
        cache.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    def test_clear_cache_function(self):
        """Test cache clearing functionality."""
        # Set some cache values
        cache.set('facebook_events_test_page_5', ['event1'], 3600)
        cache.set('facebook_events_test_page_10', ['event1', 'event2'], 3600)
        
        # Verify cache is set
        self.assertIsNotNone(cache.get('facebook_events_test_page_5'))
        
        # Clear cache
        result = clear_facebook_events_cache()
        
        # Should return True on success
        self.assertTrue(result)


class FacebookEventsLoggingTest(TestCase):
    """Test logging functionality for Facebook events."""
    
    def setUp(self):
        """Set up logging test."""
        self.logger = logging.getLogger('core.utils.facebook_events')
        self.log_handler = logging.StreamHandler()
        self.logger.addHandler(self.log_handler)
        self.logger.setLevel(logging.DEBUG)
    
    def tearDown(self):
        """Clean up logging test."""
        self.logger.removeHandler(self.log_handler)
    
    @patch('core.utils.facebook_events.requests.get')
    @patch.dict('os.environ', {
        'FACEBOOK_ACCESS_TOKEN': 'test_token',
        'FACEBOOK_PAGE_ID': 'test_page_id'
    })
    def test_api_error_logging(self, mock_get):
        """Test that API errors are properly logged."""
        mock_get.side_effect = Exception("Network error")
        
        api = FacebookEventsAPI()
        
        with self.assertLogs('core.utils.facebook_events', level='ERROR') as log:
            result = api._make_api_request('test_page_id/events', {'limit': 5})
            
        self.assertIsNone(result)
        self.assertTrue(any('Network error' in message for message in log.output))


class FacebookEventsIntegrationTest(TestCase):
    """Integration tests for Facebook events functionality."""
    
    def setUp(self):
        """Set up integration test environment."""
        cache.clear()
        FacebookEvent.objects.all().delete()
    
    def tearDown(self):
        """Clean up integration test environment."""
        cache.clear()
        FacebookEvent.objects.all().delete()
    
    @patch('core.utils.facebook_events.FacebookEventsAPI._make_api_request')
    @patch.dict('os.environ', {
        'FACEBOOK_ACCESS_TOKEN': 'test_token',
        'FACEBOOK_PAGE_ID': 'test_page_id'
    })
    def test_end_to_end_facebook_events_flow(self, mock_api_request):
        """Test complete Facebook events flow."""
        # Mock API response
        from datetime import timedelta
        future_time = datetime.now(timezone.utc) + timedelta(days=7)
        mock_api_request.return_value = {
            'data': [
                {
                    'id': '123456789',
                    'name': 'Integration Test Event',
                    'description': 'End-to-end test event',
                    'start_time': future_time.isoformat(),
                    'cover': {
                        'source': 'https://example.com/cover.jpg'
                    }
                }
            ]
        }
        
        # Test API functionality
        events = get_facebook_events(limit=5, use_cache=True)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['name'], 'Integration Test Event')
        
        # Test caching
        mock_api_request.reset_mock()
        events_cached = get_facebook_events(limit=5, use_cache=True)
        self.assertEqual(len(events_cached), 1)
        mock_api_request.assert_not_called()  # Should use cache
        
        # Test cache clearing
        clear_facebook_events_cache()
        events_fresh = get_facebook_events(limit=5, use_cache=True)
        mock_api_request.assert_called()  # Should hit API again
        
        # Test database storage
        FacebookEvent.objects.create(
            facebook_id='123456789',
            name='Integration Test Event',
            description='End-to-end test event',
            start_time=django_timezone.now() + django_timezone.timedelta(days=7),
            facebook_url='https://facebook.com/events/123456789'
        )
        
        upcoming = FacebookEvent.get_upcoming_events(limit=5)
        self.assertEqual(len(upcoming), 1)
        self.assertEqual(upcoming[0].name, 'Integration Test Event')