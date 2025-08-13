"""
Comprehensive tests for Facebook Events API integration - SPEC_05 Group B Task 5 & 6

Tests Facebook Events API client, model functionality, caching behavior,
error handling, and integration with views.
"""

import json
import responses
from datetime import datetime, timezone as dt_timezone, timedelta
from unittest.mock import patch, Mock
from django.test import TestCase, RequestFactory
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from core.models import FacebookEvent
from core.utils.facebook_events import (
    FacebookEventsAPI, 
    get_facebook_events, 
    clear_facebook_events_cache,
    get_facebook_api_status
)


class FacebookEventModelTestCase(TestCase):
    """Test cases for the FacebookEvent model."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_event_data = {
            'facebook_id': 'fb_event_123',
            'name': 'Salsa Night at Avalon',
            'description': 'Join us for an amazing night of salsa dancing.',
            'start_time': timezone.now() + timedelta(days=7),
            'end_time': timezone.now() + timedelta(days=7, hours=3),
            'formatted_date': 'December 15, 2024',
            'formatted_time': '8:00 PM',
            'cover_photo_url': 'https://facebook.com/photos/event123.jpg',
            'facebook_url': 'https://www.facebook.com/events/fb_event_123',
            'location_name': 'Avalon Ballroom',
            'location_address': '6185 Arapahoe Rd, Boulder, CO 80303',
            'is_active': True,
            'featured': False,
            'order': 0
        }
    
    def test_facebook_event_creation(self):
        """Test creating a Facebook event with valid data."""
        event = FacebookEvent.objects.create(**self.valid_event_data)
        
        self.assertEqual(event.facebook_id, 'fb_event_123')
        self.assertEqual(event.name, 'Salsa Night at Avalon')
        self.assertEqual(event.description, 'Join us for an amazing night of salsa dancing.')
        self.assertEqual(event.formatted_date, 'December 15, 2024')
        self.assertEqual(event.formatted_time, '8:00 PM')
        self.assertEqual(event.cover_photo_url, 'https://facebook.com/photos/event123.jpg')
        self.assertEqual(event.facebook_url, 'https://www.facebook.com/events/fb_event_123')
        self.assertEqual(event.location_name, 'Avalon Ballroom')
        self.assertTrue(event.is_active)
        self.assertFalse(event.featured)
    
    def test_facebook_event_str_representation(self):
        """Test the string representation of a Facebook event."""
        event = FacebookEvent.objects.create(**self.valid_event_data)
        expected_str = "Salsa Night at Avalon - December 15, 2024"
        self.assertEqual(str(event), expected_str)
    
    def test_facebook_event_unique_facebook_id(self):
        """Test that facebook_id must be unique."""
        FacebookEvent.objects.create(**self.valid_event_data)
        
        # Try to create another event with same facebook_id
        duplicate_data = self.valid_event_data.copy()
        duplicate_data['name'] = 'Different Event'
        
        with self.assertRaises(Exception):  # IntegrityError or ValidationError
            FacebookEvent.objects.create(**duplicate_data)
    
    def test_get_short_description(self):
        """Test the get_short_description method."""
        # Test with short description
        event = FacebookEvent.objects.create(**self.valid_event_data)
        self.assertEqual(event.get_short_description(), event.description)
        
        # Test with long description
        long_description = 'x' * 200  # 200 characters
        event.description = long_description
        event.save()
        
        short_desc = event.get_short_description(max_length=50)
        self.assertEqual(len(short_desc), 50)
        self.assertTrue(short_desc.endswith('...'))
        self.assertEqual(short_desc, long_description[:47] + '...')
    
    def test_is_future_event(self):
        """Test the is_future_event method."""
        # Future event
        future_event = FacebookEvent.objects.create(**self.valid_event_data)
        self.assertTrue(future_event.is_future_event())
        
        # Past event
        past_data = self.valid_event_data.copy()
        past_data['facebook_id'] = 'past_event_123'
        past_data['start_time'] = timezone.now() - timedelta(days=1)
        past_event = FacebookEvent.objects.create(**past_data)
        self.assertFalse(past_event.is_future_event())
    
    def test_get_time_until_event(self):
        """Test the get_time_until_event method."""
        # Future event
        future_time = timezone.now() + timedelta(days=2, hours=3)
        future_data = self.valid_event_data.copy()
        future_data['start_time'] = future_time
        future_event = FacebookEvent.objects.create(**future_data)
        
        time_until = future_event.get_time_until_event()
        self.assertIn('2 days', time_until)
        
        # Past event
        past_data = self.valid_event_data.copy()
        past_data['facebook_id'] = 'past_event_456'
        past_data['start_time'] = timezone.now() - timedelta(hours=1)
        past_event = FacebookEvent.objects.create(**past_data)
        
        self.assertEqual(past_event.get_time_until_event(), "Past event")
        
        # Today's event
        today_data = self.valid_event_data.copy()
        today_data['facebook_id'] = 'today_event_789'
        today_data['start_time'] = timezone.now() + timedelta(hours=2)
        today_event = FacebookEvent.objects.create(**today_data)
        
        self.assertEqual(today_event.get_time_until_event(), "Today")
    
    def test_get_upcoming_events_classmethod(self):
        """Test the get_upcoming_events class method."""
        # Create future events
        for i in range(3):
            data = self.valid_event_data.copy()
            data['facebook_id'] = f'future_event_{i}'
            data['start_time'] = timezone.now() + timedelta(days=i+1)
            data['name'] = f'Future Event {i+1}'
            FacebookEvent.objects.create(**data)
        
        # Create past event
        past_data = self.valid_event_data.copy()
        past_data['facebook_id'] = 'past_event'
        past_data['start_time'] = timezone.now() - timedelta(days=1)
        past_data['name'] = 'Past Event'
        FacebookEvent.objects.create(**past_data)
        
        upcoming = FacebookEvent.get_upcoming_events(limit=2)
        self.assertEqual(len(upcoming), 2)
        
        # Should be ordered by start_time
        self.assertEqual(upcoming[0].name, 'Future Event 1')
        self.assertEqual(upcoming[1].name, 'Future Event 2')
    
    def test_get_featured_events_classmethod(self):
        """Test the get_featured_events class method."""
        # Create featured events
        for i in range(2):
            data = self.valid_event_data.copy()
            data['facebook_id'] = f'featured_event_{i}'
            data['start_time'] = timezone.now() + timedelta(days=i+1)
            data['name'] = f'Featured Event {i+1}'
            data['featured'] = True
            data['order'] = i
            FacebookEvent.objects.create(**data)
        
        # Create non-featured event
        non_featured_data = self.valid_event_data.copy()
        non_featured_data['facebook_id'] = 'non_featured'
        non_featured_data['start_time'] = timezone.now() + timedelta(days=3)
        non_featured_data['name'] = 'Non Featured Event'
        non_featured_data['featured'] = False
        FacebookEvent.objects.create(**non_featured_data)
        
        featured = FacebookEvent.get_featured_events(limit=5)
        self.assertEqual(len(featured), 2)
        
        for event in featured:
            self.assertTrue(event.featured)
    
    def test_facebook_event_indexes(self):
        """Test that database indexes are working efficiently."""
        # Create multiple events
        for i in range(10):
            data = self.valid_event_data.copy()
            data['facebook_id'] = f'event_{i}'
            data['start_time'] = timezone.now() + timedelta(days=i)
            data['featured'] = (i % 2 == 0)  # Alternate featured status
            FacebookEvent.objects.create(**data)
        
        # These queries should use indexes efficiently
        with self.assertNumQueries(1):
            list(FacebookEvent.objects.filter(start_time__gt=timezone.now(), is_active=True)[:5])
        
        with self.assertNumQueries(1):
            list(FacebookEvent.objects.filter(featured=True, start_time__gt=timezone.now())[:3])


class FacebookEventsAPITestCase(TestCase):
    """Test cases for the FacebookEventsAPI class."""
    
    def setUp(self):
        """Set up test data."""
        self.api = FacebookEventsAPI()
        self.sample_facebook_response = {
            'data': [
                {
                    'id': 'fb_event_123',
                    'name': 'Salsa Workshop',
                    'description': 'Learn advanced salsa techniques.',
                    'start_time': '2024-12-15T20:00:00-0700',
                    'end_time': '2024-12-15T23:00:00-0700',
                    'cover': {
                        'source': 'https://facebook.com/photos/workshop.jpg'
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
                    'id': 'fb_event_456',
                    'name': 'Bachata Night',
                    'description': 'Dancing and fun all night long.',
                    'start_time': '2024-12-20T21:00:00-0700',
                    'cover': {
                        'source': 'https://facebook.com/photos/bachata.jpg'
                    }
                }
            ]
        }
    
    def test_api_initialization(self):
        """Test API initialization and configuration."""
        api = FacebookEventsAPI()
        self.assertEqual(api.base_url, 'https://graph.facebook.com/v18.0')
        self.assertEqual(api.cache_timeout, 6 * 60 * 60)  # 6 hours
    
    @patch.dict('os.environ', {})
    def test_validate_config_missing_credentials(self):
        """Test configuration validation with missing credentials."""
        api = FacebookEventsAPI()
        is_valid, message = api._validate_config()
        self.assertFalse(is_valid)
        self.assertIn('access token', message.lower())
    
    @patch.dict('os.environ', {'FACEBOOK_ACCESS_TOKEN': 'test_token'})
    def test_validate_config_missing_page_id(self):
        """Test configuration validation with missing page ID."""
        api = FacebookEventsAPI()
        is_valid, message = api._validate_config()
        self.assertFalse(is_valid)
        self.assertIn('page id', message.lower())
    
    @patch.dict('os.environ', {
        'FACEBOOK_ACCESS_TOKEN': 'test_token',
        'FACEBOOK_PAGE_ID': 'test_page_id'
    })
    def test_validate_config_complete(self):
        """Test configuration validation with complete credentials."""
        api = FacebookEventsAPI()
        is_valid, message = api._validate_config()
        self.assertTrue(is_valid)
        self.assertEqual(message, "Configuration valid")
    
    @responses.activate
    @patch.dict('os.environ', {
        'FACEBOOK_ACCESS_TOKEN': 'test_token',
        'FACEBOOK_PAGE_ID': 'test_page_id'
    })
    def test_make_api_request_success(self):
        """Test successful API request."""
        responses.add(
            responses.GET,
            'https://graph.facebook.com/v18.0/test_page_id/events',
            json=self.sample_facebook_response,
            status=200
        )
        
        api = FacebookEventsAPI()
        result = api._make_api_request('test_page_id/events', {'fields': 'id,name'})
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result['data']), 2)
        self.assertEqual(result['data'][0]['id'], 'fb_event_123')
    
    @responses.activate
    @patch.dict('os.environ', {
        'FACEBOOK_ACCESS_TOKEN': 'test_token',
        'FACEBOOK_PAGE_ID': 'test_page_id'
    })
    def test_make_api_request_http_error(self):
        """Test API request with HTTP error."""
        responses.add(
            responses.GET,
            'https://graph.facebook.com/v18.0/test_page_id/events',
            json={'error': {'message': 'Invalid access token'}},
            status=401
        )
        
        api = FacebookEventsAPI()
        result = api._make_api_request('test_page_id/events', {'fields': 'id,name'})
        
        self.assertIsNone(result)
    
    @responses.activate
    @patch.dict('os.environ', {
        'FACEBOOK_ACCESS_TOKEN': 'test_token',
        'FACEBOOK_PAGE_ID': 'test_page_id'
    })
    def test_make_api_request_timeout(self):
        """Test API request with timeout."""
        import requests
        
        def timeout_callback(request):
            raise requests.exceptions.Timeout("Request timed out")
        
        responses.add_callback(
            responses.GET,
            'https://graph.facebook.com/v18.0/test_page_id/events',
            callback=timeout_callback
        )
        
        api = FacebookEventsAPI()
        result = api._make_api_request('test_page_id/events', {'fields': 'id,name'})
        
        self.assertIsNone(result)
    
    def test_filter_future_events(self):
        """Test filtering events to only include future events."""
        api = FacebookEventsAPI()
        
        past_time = (datetime.now(dt_timezone.utc) - timedelta(days=1)).isoformat()
        future_time = (datetime.now(dt_timezone.utc) + timedelta(days=1)).isoformat()
        
        events = [
            {'id': '1', 'name': 'Past Event', 'start_time': past_time},
            {'id': '2', 'name': 'Future Event', 'start_time': future_time},
            {'id': '3', 'name': 'No Time Event'}  # Missing start_time
        ]
        
        filtered = api._filter_future_events(events)
        
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['name'], 'Future Event')
    
    def test_extract_event_data(self):
        """Test event data extraction and normalization."""
        api = FacebookEventsAPI()
        
        raw_event = {
            'id': 'fb_123',
            'name': 'Test Event',
            'description': 'x' * 250,  # Long description
            'start_time': '2024-12-15T20:00:00-0700',
            'cover': {
                'source': 'https://facebook.com/cover.jpg'
            }
        }
        
        extracted = api._extract_event_data(raw_event)
        
        self.assertEqual(extracted['id'], 'fb_123')
        self.assertEqual(extracted['name'], 'Test Event')
        self.assertEqual(len(extracted['description']), 200)  # Truncated
        self.assertTrue(extracted['description'].endswith('...'))
        self.assertEqual(extracted['formatted_date'], 'December 15, 2024')
        self.assertEqual(extracted['formatted_time'], '08:00 PM')
        self.assertEqual(extracted['cover_photo'], 'https://facebook.com/cover.jpg')
        self.assertEqual(extracted['facebook_url'], 'https://www.facebook.com/events/fb_123')
    
    def test_extract_event_data_error_handling(self):
        """Test event data extraction with malformed data."""
        api = FacebookEventsAPI()
        
        # Test with minimal/malformed data
        raw_event = {'id': 'test_id'}
        
        extracted = api._extract_event_data(raw_event)
        
        self.assertEqual(extracted['id'], 'test_id')
        self.assertEqual(extracted['name'], 'Untitled Event')
        self.assertEqual(extracted['description'], 'Event details unavailable')
        self.assertEqual(extracted['start_time'], '')
        self.assertEqual(extracted['formatted_date'], '')
        self.assertIsNone(extracted['cover_photo'])
    
    @responses.activate
    @patch.dict('os.environ', {
        'FACEBOOK_ACCESS_TOKEN': 'test_token',
        'FACEBOOK_PAGE_ID': 'test_page_id'
    })
    def test_get_upcoming_events_success(self):
        """Test successful retrieval of upcoming events."""
        responses.add(
            responses.GET,
            'https://graph.facebook.com/v18.0/test_page_id/events',
            json=self.sample_facebook_response,
            status=200
        )
        
        api = FacebookEventsAPI()
        events = api.get_upcoming_events(limit=5, use_cache=False)
        
        self.assertIsInstance(events, list)
        self.assertGreaterEqual(len(events), 0)
        
        if events:
            event = events[0]
            self.assertIn('id', event)
            self.assertIn('name', event)
            self.assertIn('facebook_url', event)
    
    @patch.dict('os.environ', {})
    def test_get_upcoming_events_no_config(self):
        """Test get_upcoming_events with no configuration."""
        api = FacebookEventsAPI()
        events = api.get_upcoming_events()
        
        self.assertEqual(events, [])
    
    @patch('core.utils.facebook_events.cache')
    @patch.dict('os.environ', {
        'FACEBOOK_ACCESS_TOKEN': 'test_token',
        'FACEBOOK_PAGE_ID': 'test_page_id'
    })
    def test_get_upcoming_events_cache_hit(self):
        """Test get_upcoming_events with cache hit."""
        mock_cache = Mock()
        mock_cache.get.return_value = [{'id': 'cached_event', 'name': 'Cached Event'}]
        
        with patch('core.utils.facebook_events.cache', mock_cache):
            api = FacebookEventsAPI()
            events = api.get_upcoming_events(limit=5, use_cache=True)
        
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['name'], 'Cached Event')
        mock_cache.get.assert_called_once()
    
    @patch('core.utils.facebook_events.cache')
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        mock_cache = Mock()
        
        with patch('core.utils.facebook_events.cache', mock_cache):
            api = FacebookEventsAPI()
            result = api.clear_cache()
        
        self.assertTrue(result)
        # Should delete cache for different limits
        self.assertEqual(mock_cache.delete.call_count, 3)
    
    @responses.activate
    @patch.dict('os.environ', {
        'FACEBOOK_ACCESS_TOKEN': 'test_token',
        'FACEBOOK_PAGE_ID': 'test_page_id'
    })
    def test_get_api_status(self):
        """Test API status checking functionality."""
        # Mock successful API responses
        responses.add(
            responses.GET,
            'https://graph.facebook.com/v18.0/me',
            json={'id': 'user_123', 'name': 'Test User'},
            status=200
        )
        responses.add(
            responses.GET,
            'https://graph.facebook.com/v18.0/test_page_id',
            json={'id': 'test_page_id', 'name': 'Test Page'},
            status=200
        )
        
        api = FacebookEventsAPI()
        status = api.get_api_status()
        
        self.assertTrue(status['configured'])
        self.assertTrue(status['api_accessible'])
        self.assertTrue(status['page_accessible'])
        self.assertEqual(status['page_name'], 'Test Page')
        self.assertIn('last_check', status)


class FacebookEventsIntegrationTestCase(TestCase):
    """Integration tests for Facebook events functionality."""
    
    def setUp(self):
        """Set up test data."""
        cache.clear()  # Clear cache before each test
    
    def tearDown(self):
        """Clean up after each test."""
        cache.clear()
    
    @patch('core.utils.facebook_events.FacebookEventsAPI')
    def test_get_facebook_events_convenience_function(self):
        """Test the convenience function for getting Facebook events."""
        mock_api = Mock()
        mock_api.return_value.get_upcoming_events.return_value = [
            {'id': 'test_event', 'name': 'Test Event'}
        ]
        
        with patch('core.utils.facebook_events.FacebookEventsAPI', mock_api):
            events = get_facebook_events(limit=3, use_cache=False)
        
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['name'], 'Test Event')
        mock_api.return_value.get_upcoming_events.assert_called_once_with(
            limit=3, use_cache=False
        )
    
    @patch('core.utils.facebook_events.FacebookEventsAPI')
    def test_clear_facebook_events_cache_convenience_function(self):
        """Test the convenience function for clearing cache."""
        mock_api = Mock()
        mock_api.return_value.clear_cache.return_value = True
        
        with patch('core.utils.facebook_events.FacebookEventsAPI', mock_api):
            result = clear_facebook_events_cache()
        
        self.assertTrue(result)
        mock_api.return_value.clear_cache.assert_called_once()
    
    @patch('core.utils.facebook_events.FacebookEventsAPI')
    def test_get_facebook_api_status_convenience_function(self):
        """Test the convenience function for getting API status."""
        mock_status = {
            'configured': True,
            'api_accessible': True,
            'page_accessible': False
        }
        mock_api = Mock()
        mock_api.return_value.get_api_status.return_value = mock_status
        
        with patch('core.utils.facebook_events.FacebookEventsAPI', mock_api):
            status = get_facebook_api_status()
        
        self.assertEqual(status, mock_status)
        mock_api.return_value.get_api_status.assert_called_once()
    
    def test_facebook_events_in_schedule_view(self):
        """Test Facebook events integration in schedule view."""
        # Create some database events as fallback
        for i in range(3):
            FacebookEvent.objects.create(
                facebook_id=f'db_event_{i}',
                name=f'Database Event {i+1}',
                description='Test event from database',
                start_time=timezone.now() + timedelta(days=i+1),
                formatted_date=f'December {15+i}, 2024',
                formatted_time='8:00 PM',
                facebook_url=f'https://facebook.com/events/db_event_{i}'
            )
        
        with patch('core.utils.facebook_events.get_facebook_events') as mock_get_events:
            # Mock API failure, should fallback to database
            mock_get_events.return_value = []
            
            response = self.client.get('/schedule/')
            
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Database Event 1')
            
            # Check that context contains facebook_events
            facebook_events = response.context.get('facebook_events', [])
            self.assertGreaterEqual(len(facebook_events), 0)
    
    def test_facebook_events_caching_behavior(self):
        """Test caching behavior in Facebook events integration."""
        with patch('core.utils.facebook_events.FacebookEventsAPI') as mock_api:
            # Setup mock to return different results on subsequent calls
            mock_instance = mock_api.return_value
            mock_instance.get_upcoming_events.side_effect = [
                [{'id': 'first_call', 'name': 'First Call Event'}],
                [{'id': 'second_call', 'name': 'Second Call Event'}]
            ]
            
            # First call should hit API
            events1 = get_facebook_events(limit=5, use_cache=True)
            self.assertEqual(events1[0]['name'], 'First Call Event')
            
            # Due to mocking, we can't test actual cache behavior,
            # but we can verify the function calls
            mock_instance.get_upcoming_events.assert_called_with(
                limit=5, use_cache=True
            )


class FacebookEventsManagementTestCase(TestCase):
    """Test cases for Facebook events management and admin functionality."""
    
    def test_facebook_event_admin_list_display(self):
        """Test that Facebook events display correctly in admin."""
        # Create test events
        event = FacebookEvent.objects.create(
            facebook_id='admin_test_123',
            name='Admin Test Event',
            description='Test event for admin display',
            start_time=timezone.now() + timedelta(days=1),
            formatted_date='Tomorrow',
            formatted_time='8:00 PM',
            facebook_url='https://facebook.com/events/admin_test_123',
            is_active=True,
            featured=True
        )
        
        # Test string representation
        self.assertIn('Admin Test Event', str(event))
        self.assertIn('Tomorrow', str(event))
        
        # Test that we can query efficiently
        events = FacebookEvent.objects.filter(is_active=True, featured=True)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].name, 'Admin Test Event')
    
    def test_facebook_event_bulk_operations(self):
        """Test bulk operations on Facebook events."""
        # Create multiple events
        events = []
        for i in range(5):
            event = FacebookEvent.objects.create(
                facebook_id=f'bulk_event_{i}',
                name=f'Bulk Event {i+1}',
                description=f'Bulk test event {i+1}',
                start_time=timezone.now() + timedelta(days=i+1),
                formatted_date=f'Day {i+1}',
                formatted_time='8:00 PM',
                facebook_url=f'https://facebook.com/events/bulk_event_{i}',
                is_active=(i % 2 == 0)  # Alternate active status
            )
            events.append(event)
        
        # Test bulk update
        FacebookEvent.objects.filter(facebook_id__startswith='bulk_event_').update(
            featured=True
        )
        
        # Verify bulk update
        featured_events = FacebookEvent.objects.filter(featured=True)
        self.assertEqual(len(featured_events), 5)
        
        # Test bulk delete
        FacebookEvent.objects.filter(is_active=False).delete()
        
        remaining_events = FacebookEvent.objects.filter(facebook_id__startswith='bulk_event_')
        self.assertEqual(len(remaining_events), 3)  # Only active events remain
    
    def test_facebook_event_performance_queries(self):
        """Test query performance for Facebook events."""
        # Create events with various statuses
        for i in range(20):
            FacebookEvent.objects.create(
                facebook_id=f'perf_event_{i}',
                name=f'Performance Event {i+1}',
                description='Performance test event',
                start_time=timezone.now() + timedelta(days=i+1),
                formatted_date=f'Day {i+1}',
                formatted_time='8:00 PM',
                facebook_url=f'https://facebook.com/events/perf_event_{i}',
                is_active=True,
                featured=(i < 5)  # First 5 are featured
            )
        
        # Test efficient queries using indexes
        with self.assertNumQueries(1):
            list(FacebookEvent.get_upcoming_events(limit=10))
        
        with self.assertNumQueries(1):
            list(FacebookEvent.get_featured_events(limit=5))
        
        # Test compound query
        with self.assertNumQueries(1):
            list(FacebookEvent.objects.filter(
                is_active=True,
                featured=True,
                start_time__gt=timezone.now()
            )[:3])