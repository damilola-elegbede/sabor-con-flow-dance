"""
Facebook Events API Integration for SPEC_05 Group B Task 5

Provides functionality to fetch upcoming events from Facebook Page API
with caching, error handling, and proper data extraction.
"""

import os
import logging
import requests
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

class FacebookEventsAPI:
    """
    Facebook Graph API client for fetching page events.
    Handles authentication, caching, and error recovery.
    """
    
    def __init__(self):
        self.access_token = os.environ.get('FACEBOOK_ACCESS_TOKEN')
        self.page_id = os.environ.get('FACEBOOK_PAGE_ID')
        self.base_url = 'https://graph.facebook.com/v18.0'
        self.cache_timeout = 6 * 60 * 60  # 6 hours in seconds
        
    def _validate_config(self) -> Tuple[bool, str]:
        """Validate API configuration."""
        if not self.access_token:
            return False, "Facebook access token not configured"
        if not self.page_id:
            return False, "Facebook page ID not configured"
        return True, "Configuration valid"
    
    def _make_api_request(self, endpoint: str, params: dict) -> Optional[dict]:
        """
        Make authenticated request to Facebook Graph API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            API response data or None if failed
        """
        try:
            params['access_token'] = self.access_token
            
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error("Facebook API request timed out")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"Facebook API HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Facebook API request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Facebook API request: {str(e)}")
            return None
    
    def _filter_future_events(self, events: List[dict]) -> List[dict]:
        """
        Filter events to only include future events.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Filtered list of future events
        """
        future_events = []
        current_time = datetime.now(timezone.utc)
        
        for event in events:
            try:
                # Parse start_time from Facebook format
                start_time_str = event.get('start_time')
                if not start_time_str:
                    continue
                
                # Facebook returns ISO format: 2024-01-15T19:00:00-0700
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                
                # Only include future events
                if start_time > current_time:
                    future_events.append(event)
                    
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse event start_time: {start_time_str} - {str(e)}")
                continue
        
        # Sort by start time (ascending)
        future_events.sort(key=lambda x: x.get('start_time', ''))
        return future_events
    
    def _extract_event_data(self, raw_event: dict) -> dict:
        """
        Extract and normalize event data from Facebook API response.
        
        Args:
            raw_event: Raw event data from Facebook API
            
        Returns:
            Normalized event dictionary
        """
        try:
            # Extract cover photo URL
            cover_photo = None
            if 'cover' in raw_event and 'source' in raw_event['cover']:
                cover_photo = raw_event['cover']['source']
            
            # Parse and format start time
            start_time_str = raw_event.get('start_time', '')
            formatted_date = ''
            formatted_time = ''
            
            if start_time_str:
                try:
                    start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                    formatted_date = start_time.strftime('%B %d, %Y')
                    formatted_time = start_time.strftime('%I:%M %p')
                except (ValueError, TypeError):
                    logger.warning(f"Failed to format event time: {start_time_str}")
            
            # Truncate description if too long
            description = raw_event.get('description', '')
            if len(description) > 200:
                description = description[:197] + '...'
            
            return {
                'id': raw_event.get('id'),
                'name': raw_event.get('name', 'Untitled Event'),
                'description': description,
                'start_time': start_time_str,
                'formatted_date': formatted_date,
                'formatted_time': formatted_time,
                'cover_photo': cover_photo,
                'facebook_url': f"https://www.facebook.com/events/{raw_event.get('id')}"
            }
            
        except Exception as e:
            logger.error(f"Error extracting event data: {str(e)}")
            return {
                'id': raw_event.get('id', 'unknown'),
                'name': raw_event.get('name', 'Event'),
                'description': 'Event details unavailable',
                'start_time': '',
                'formatted_date': '',
                'formatted_time': '',
                'cover_photo': None,
                'facebook_url': f"https://www.facebook.com/events/{raw_event.get('id', '')}"
            }
    
    def get_upcoming_events(self, limit: int = 5, use_cache: bool = True) -> List[dict]:
        """
        Fetch upcoming events from Facebook Page.
        
        Args:
            limit: Maximum number of events to return
            use_cache: Whether to use cached results
            
        Returns:
            List of upcoming event dictionaries
        """
        # Check configuration
        is_valid, error_msg = self._validate_config()
        if not is_valid:
            logger.warning(f"Facebook Events API not configured: {error_msg}")
            return []
        
        # Check cache first
        cache_key = f'facebook_events_{self.page_id}_{limit}'
        if use_cache:
            cached_events = cache.get(cache_key)
            if cached_events is not None:
                logger.info(f"Returning {len(cached_events)} cached Facebook events")
                return cached_events
        
        try:
            # Fetch events from Facebook API
            logger.info(f"Fetching events for Facebook page {self.page_id}")
            
            # API fields to retrieve
            fields = [
                'id',
                'name', 
                'description',
                'start_time',
                'end_time',
                'cover',
                'place',
                'ticket_uri'
            ]
            
            params = {
                'fields': ','.join(fields),
                'time_filter': 'upcoming',  # Only future events
                'limit': limit * 2  # Get more to account for filtering
            }
            
            response_data = self._make_api_request(f"{self.page_id}/events", params)
            
            if not response_data:
                logger.error("Failed to fetch Facebook events")
                return []
            
            raw_events = response_data.get('data', [])
            logger.info(f"Fetched {len(raw_events)} events from Facebook API")
            
            # Filter for future events only
            future_events = self._filter_future_events(raw_events)
            logger.info(f"Filtered to {len(future_events)} future events")
            
            # Extract and normalize event data
            processed_events = []
            for raw_event in future_events[:limit]:
                processed_event = self._extract_event_data(raw_event)
                processed_events.append(processed_event)
            
            # Cache the results
            if use_cache:
                cache.set(cache_key, processed_events, self.cache_timeout)
                logger.info(f"Cached {len(processed_events)} Facebook events for {self.cache_timeout/3600} hours")
            
            return processed_events
            
        except Exception as e:
            logger.error(f"Unexpected error fetching Facebook events: {str(e)}")
            return []
    
    def clear_cache(self) -> bool:
        """
        Clear all cached Facebook events data.
        
        Returns:
            True if cache cleared successfully
        """
        try:
            # Clear cache for different limits
            for limit in [5, 10, 20]:
                cache_key = f'facebook_events_{self.page_id}_{limit}'
                cache.delete(cache_key)
            
            logger.info("Facebook events cache cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing Facebook events cache: {str(e)}")
            return False
    
    def get_api_status(self) -> dict:
        """
        Check Facebook API connectivity and return status.
        
        Returns:
            Status dictionary with configuration and connectivity info
        """
        is_valid, config_message = self._validate_config()
        
        status = {
            'configured': is_valid,
            'config_message': config_message,
            'api_accessible': False,
            'page_accessible': False,
            'last_check': datetime.now().isoformat()
        }
        
        if not is_valid:
            return status
        
        # Test API connectivity
        try:
            response_data = self._make_api_request('me', {'fields': 'id,name'})
            if response_data:
                status['api_accessible'] = True
                
                # Test page access
                page_data = self._make_api_request(self.page_id, {'fields': 'id,name'})
                if page_data:
                    status['page_accessible'] = True
                    status['page_name'] = page_data.get('name', 'Unknown')
                    
        except Exception as e:
            logger.error(f"Error checking Facebook API status: {str(e)}")
        
        return status


# Convenience functions for easy import

def get_facebook_events(limit: int = 5, use_cache: bool = True) -> List[dict]:
    """
    Get upcoming Facebook events with default configuration.
    
    Args:
        limit: Maximum number of events to return
        use_cache: Whether to use cached results
        
    Returns:
        List of upcoming event dictionaries
    """
    api = FacebookEventsAPI()
    return api.get_upcoming_events(limit=limit, use_cache=use_cache)


def clear_facebook_events_cache() -> bool:
    """
    Clear Facebook events cache.
    
    Returns:
        True if cache cleared successfully
    """
    api = FacebookEventsAPI()
    return api.clear_cache()


def get_facebook_api_status() -> dict:
    """
    Get Facebook API connectivity status.
    
    Returns:
        Status dictionary
    """
    api = FacebookEventsAPI()
    return api.get_api_status()