"""
Instagram API integration utilities for Sabor con Flow Dance website.

This module provides Instagram Basic Display API integration for:
- Fetching user's Instagram posts
- Caching posts data with rate limiting
- Error handling and retry logic
- Post data normalization
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class InstagramAPIError(Exception):
    """Custom exception for Instagram API errors."""
    def __init__(self, message: str, status_code: int = None, error_type: str = None):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        super().__init__(self.message)


class InstagramAPI:
    """Instagram Basic Display API client with rate limiting and error handling."""
    
    # API Endpoints
    BASE_URL = "https://graph.instagram.com"
    MEDIA_FIELDS = "id,media_type,media_url,thumbnail_url,permalink,caption,timestamp,username"
    
    # Rate limiting constants
    RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
    MAX_REQUESTS_PER_HOUR = 200  # Instagram Basic Display API limit
    CACHE_TIMEOUT = 1800  # 30 minutes
    
    def __init__(self, access_token: str = None):
        """
        Initialize Instagram API client.
        
        Args:
            access_token: Instagram Basic Display API access token
        """
        self.access_token = access_token or getattr(settings, 'INSTAGRAM_ACCESS_TOKEN', None)
        if not self.access_token:
            logger.warning("Instagram access token not configured")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SaborConFlowDance/1.0'
        })
    
    def _check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits.
        
        Returns:
            bool: True if request can be made, False if rate limited
        """
        cache_key = 'instagram_api_requests'
        requests_made = cache.get(cache_key, [])
        now = time.time()
        
        # Remove requests older than 1 hour
        requests_made = [req_time for req_time in requests_made 
                        if now - req_time < self.RATE_LIMIT_WINDOW]
        
        if len(requests_made) >= self.MAX_REQUESTS_PER_HOUR:
            logger.warning("Instagram API rate limit reached")
            return False
        
        # Add current request timestamp
        requests_made.append(now)
        cache.set(cache_key, requests_made, self.RATE_LIMIT_WINDOW)
        return True
    
    def _make_request(self, endpoint: str, params: Dict = None, retries: int = 3) -> Dict:
        """
        Make API request with error handling and retries.
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            retries: Number of retry attempts
            
        Returns:
            Dict: API response data
            
        Raises:
            InstagramAPIError: If request fails after retries
        """
        if not self.access_token:
            raise InstagramAPIError("Instagram access token not configured", error_type="auth_error")
        
        if not self._check_rate_limit():
            raise InstagramAPIError("Rate limit exceeded", status_code=429, error_type="rate_limit")
        
        url = f"{self.BASE_URL}/{endpoint}"
        params = params or {}
        params['access_token'] = self.access_token
        
        for attempt in range(retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 400:
                    error_data = response.json().get('error', {})
                    error_msg = error_data.get('message', 'Bad request')
                    raise InstagramAPIError(
                        f"Bad request: {error_msg}",
                        status_code=400,
                        error_type=error_data.get('type', 'bad_request')
                    )
                elif response.status_code == 401:
                    raise InstagramAPIError(
                        "Invalid or expired access token",
                        status_code=401,
                        error_type="auth_error"
                    )
                elif response.status_code == 403:
                    raise InstagramAPIError(
                        "Access forbidden",
                        status_code=403,
                        error_type="permission_error"
                    )
                elif response.status_code == 429:
                    raise InstagramAPIError(
                        "Rate limit exceeded",
                        status_code=429,
                        error_type="rate_limit"
                    )
                elif response.status_code >= 500:
                    if attempt == retries - 1:
                        raise InstagramAPIError(
                            f"Server error: {response.status_code}",
                            status_code=response.status_code,
                            error_type="server_error"
                        )
                    # Exponential backoff for server errors
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise InstagramAPIError(
                        f"Unexpected error: {response.status_code}",
                        status_code=response.status_code,
                        error_type="unknown_error"
                    )
                    
            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    raise InstagramAPIError(
                        f"Network error: {str(e)}",
                        error_type="network_error"
                    )
                time.sleep(2 ** attempt)
        
        raise InstagramAPIError("Max retries exceeded", error_type="timeout")
    
    def get_user_media(self, limit: int = 25, use_cache: bool = True) -> List[Dict]:
        """
        Fetch user's Instagram media posts.
        
        Args:
            limit: Number of posts to fetch (max 25 per request)
            use_cache: Whether to use cached data
            
        Returns:
            List[Dict]: List of media post data
        """
        cache_key = f'instagram_user_media_{limit}'
        
        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info("Using cached Instagram media data")
                return cached_data
        
        try:
            params = {
                'fields': self.MEDIA_FIELDS,
                'limit': min(limit, 25)  # Instagram API limit
            }
            
            response = self._make_request('me/media', params)
            media_data = response.get('data', [])
            
            # Normalize and process media data
            processed_media = []
            for media in media_data:
                processed_media.append(self._normalize_media_data(media))
            
            # Cache the results
            cache.set(cache_key, processed_media, self.CACHE_TIMEOUT)
            logger.info(f"Fetched {len(processed_media)} Instagram posts")
            
            return processed_media
            
        except InstagramAPIError as e:
            logger.error(f"Instagram API error: {e.message}")
            if use_cache:
                # Return cached data if available, even if stale
                cached_data = cache.get(cache_key)
                if cached_data:
                    logger.info("Returning stale cached data due to API error")
                    return cached_data
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Instagram media: {str(e)}")
            return []
    
    def _normalize_media_data(self, media: Dict) -> Dict:
        """
        Normalize Instagram media data for consistent structure.
        
        Args:
            media: Raw media data from Instagram API
            
        Returns:
            Dict: Normalized media data
        """
        media_type = media.get('media_type', '').upper()
        
        # Convert Instagram media types to our internal types
        if media_type in ['IMAGE', 'CAROUSEL_ALBUM']:
            normalized_type = 'image'
        elif media_type == 'VIDEO':
            normalized_type = 'video'
        else:
            normalized_type = 'image'  # Default fallback
        
        # Parse timestamp
        timestamp_str = media.get('timestamp')
        created_at = None
        if timestamp_str:
            try:
                created_at = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except ValueError:
                logger.warning(f"Invalid timestamp format: {timestamp_str}")
        
        return {
            'id': media.get('id'),
            'media_type': normalized_type,
            'media_url': media.get('media_url'),
            'thumbnail_url': media.get('thumbnail_url'),
            'permalink': media.get('permalink'),
            'caption': media.get('caption', ''),
            'username': media.get('username'),
            'created_at': created_at,
            'source': 'instagram'
        }
    
    def get_media_details(self, media_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific media post.
        
        Args:
            media_id: Instagram media ID
            
        Returns:
            Dict: Media details or None if not found
        """
        cache_key = f'instagram_media_details_{media_id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            params = {'fields': self.MEDIA_FIELDS}
            response = self._make_request(media_id, params)
            
            normalized_data = self._normalize_media_data(response)
            cache.set(cache_key, normalized_data, self.CACHE_TIMEOUT)
            
            return normalized_data
            
        except InstagramAPIError as e:
            logger.error(f"Error fetching media details for {media_id}: {e.message}")
            return None
    
    def verify_webhook(self, verify_token: str, challenge: str, provided_token: str) -> Optional[str]:
        """
        Verify Instagram webhook subscription.
        
        Args:
            verify_token: Expected verification token
            challenge: Challenge parameter from Instagram
            provided_token: Token provided by Instagram
            
        Returns:
            str: Challenge if verification successful, None otherwise
        """
        if verify_token == provided_token:
            logger.info("Instagram webhook verification successful")
            return challenge
        
        logger.warning("Instagram webhook verification failed")
        return None
    
    def refresh_access_token(self) -> Tuple[bool, str]:
        """
        Refresh the long-lived access token.
        
        Returns:
            Tuple[bool, str]: (success, new_token_or_error_message)
        """
        try:
            params = {
                'grant_type': 'ig_refresh_token',
                'access_token': self.access_token
            }
            
            response = self._make_request('refresh_access_token', params)
            new_token = response.get('access_token')
            
            if new_token:
                logger.info("Instagram access token refreshed successfully")
                return True, new_token
            else:
                return False, "No access token in response"
                
        except InstagramAPIError as e:
            logger.error(f"Error refreshing Instagram token: {e.message}")
            return False, e.message


# Utility functions for easy access
def get_instagram_posts(limit: int = 12, use_cache: bool = True) -> List[Dict]:
    """
    Convenience function to get Instagram posts.
    
    Args:
        limit: Number of posts to fetch
        use_cache: Whether to use cached data
        
    Returns:
        List[Dict]: List of Instagram posts
    """
    api = InstagramAPI()
    return api.get_user_media(limit=limit, use_cache=use_cache)


def get_instagram_post_details(media_id: str) -> Optional[Dict]:
    """
    Convenience function to get Instagram post details.
    
    Args:
        media_id: Instagram media ID
        
    Returns:
        Dict: Post details or None if not found
    """
    api = InstagramAPI()
    return api.get_media_details(media_id)


def refresh_instagram_token() -> Tuple[bool, str]:
    """
    Convenience function to refresh Instagram access token.
    
    Returns:
        Tuple[bool, str]: (success, new_token_or_error_message)
    """
    api = InstagramAPI()
    return api.refresh_access_token()