"""
Google Business Profile API Integration for Testimonials

This module provides functionality to submit testimonials to Google Business Profile
using the Google My Business API. It handles authentication, data formatting,
and API communication with proper error handling and logging.

Environment Variables Required:
- GOOGLE_BUSINESS_API_KEY: Google API Key with My Business API access
- GOOGLE_BUSINESS_PROFILE_ID: The Business Profile ID from Google
"""

import os
import logging
import asyncio
from typing import Dict, Optional, Tuple
import json
from datetime import datetime

# Third-party imports for Google API integration
try:
    import requests
    from requests.auth import HTTPBasicAuth
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    requests = None

logger = logging.getLogger(__name__)


class GoogleBusinessIntegrationError(Exception):
    """Custom exception for Google Business API integration errors."""
    pass


class GoogleBusinessReviewsAPI:
    """
    Google Business Profile API client for submitting testimonials as reviews.
    
    This class handles authentication, request formatting, and API communication
    with Google's My Business API to submit customer testimonials as reviews.
    """
    
    def __init__(self):
        """Initialize the Google Business API client with configuration."""
        self.api_key = os.environ.get('GOOGLE_BUSINESS_API_KEY')
        self.profile_id = os.environ.get('GOOGLE_BUSINESS_PROFILE_ID')
        self.base_url = "https://mybusiness.googleapis.com/v4"
        
        # Validate required environment variables
        if not self.api_key:
            logger.warning("GOOGLE_BUSINESS_API_KEY not configured")
        if not self.profile_id:
            logger.warning("GOOGLE_BUSINESS_PROFILE_ID not configured")
        
        # Configure HTTP session with retries
        if requests:
            self.session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
    
    def is_configured(self) -> bool:
        """Check if the API is properly configured with required credentials."""
        return bool(self.api_key and self.profile_id and requests)
    
    def format_testimonial_data(self, testimonial) -> Dict:
        """
        Format testimonial data for Google Business API submission.
        
        Args:
            testimonial: Testimonial model instance
            
        Returns:
            Dict: Formatted data for Google Business API
        """
        # Convert class type to Google-friendly format
        class_type_mapping = {
            'choreo_team': 'SCF Choreo Team',
            'pasos_basicos': 'Pasos Básicos',
            'casino_royale': 'Casino Royale',
            'private_lesson': 'Private Lesson',
            'workshop': 'Workshop',
            'other': 'Dance Class'
        }
        
        class_name = class_type_mapping.get(testimonial.class_type, 'Dance Class')
        
        # Format review content with class context
        review_content = f"{testimonial.content}\n\n- From {class_name} student"
        
        # Prepare data for Google Business API
        review_data = {
            'reviewId': f"scf_testimonial_{testimonial.id}",
            'reviewer': {
                'displayName': testimonial.student_name,
                'isAnonymous': False
            },
            'starRating': testimonial.rating,
            'comment': review_content,
            'createTime': testimonial.created_at.isoformat() if testimonial.created_at else datetime.now().isoformat(),
            'updateTime': datetime.now().isoformat(),
            'reviewReply': None,  # No reply initially
            'name': f"accounts/{self.profile_id}/locations/{self.profile_id}/reviews/{testimonial.id}"
        }
        
        return review_data
    
    async def submit_review_async(self, testimonial) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Asynchronously submit testimonial as Google Business review.
        
        Args:
            testimonial: Testimonial model instance
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: 
                (success, google_review_id, error_message)
        """
        if not self.is_configured():
            logger.warning("Google Business API not configured, skipping review submission")
            return False, None, "API not configured"
        
        try:
            # Format testimonial data
            review_data = self.format_testimonial_data(testimonial)
            
            # Prepare API request
            url = f"{self.base_url}/accounts/{self.profile_id}/locations/{self.profile_id}/reviews"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Submit review to Google Business API
            logger.info(f"Submitting review for testimonial {testimonial.id} to Google Business")
            
            response = self.session.post(
                url,
                headers=headers,
                json=review_data,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                google_review_id = response_data.get('name', f"review_{testimonial.id}")
                
                logger.info(f"Successfully submitted review {google_review_id} for testimonial {testimonial.id}")
                return True, google_review_id, None
                
            elif response.status_code == 401:
                error_msg = "Invalid API credentials"
                logger.error(f"Google Business API authentication failed: {error_msg}")
                return False, None, error_msg
                
            elif response.status_code == 403:
                error_msg = "Insufficient permissions for Google Business API"
                logger.error(f"Google Business API permission denied: {error_msg}")
                return False, None, error_msg
                
            elif response.status_code == 429:
                error_msg = "Rate limit exceeded for Google Business API"
                logger.warning(f"Google Business API rate limited: {error_msg}")
                return False, None, error_msg
                
            else:
                error_msg = f"Google Business API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return False, None, error_msg
                
        except requests.RequestException as e:
            error_msg = f"Network error submitting to Google Business API: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error submitting to Google Business API: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def submit_review(self, testimonial) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Submit testimonial as Google Business review (synchronous wrapper).
        
        Args:
            testimonial: Testimonial model instance
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: 
                (success, google_review_id, error_message)
        """
        try:
            # Run async function in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.submit_review_async(testimonial))
        except Exception as e:
            error_msg = f"Error running async review submission: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
        finally:
            loop.close()
    
    def update_review_status(self, testimonial, google_review_id: str) -> bool:
        """
        Update testimonial with Google review ID after successful submission.
        
        Args:
            testimonial: Testimonial model instance
            google_review_id: The ID returned by Google Business API
            
        Returns:
            bool: Success status
        """
        try:
            testimonial.google_review_id = google_review_id
            testimonial.save(update_fields=['google_review_id'])
            logger.info(f"Updated testimonial {testimonial.id} with Google review ID: {google_review_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update testimonial {testimonial.id} with Google review ID: {str(e)}")
            return False


# Convenience functions for use in views and tasks
def submit_testimonial_to_google(testimonial) -> Tuple[bool, Optional[str]]:
    """
    Submit a testimonial to Google Business Profile.
    
    Args:
        testimonial: Testimonial model instance
        
    Returns:
        Tuple[bool, Optional[str]]: (success, error_message)
    """
    api = GoogleBusinessReviewsAPI()
    
    if not api.is_configured():
        logger.info("Google Business API not configured, skipping submission")
        return True, None  # Don't treat as error if not configured
    
    success, google_review_id, error_message = api.submit_review(testimonial)
    
    if success and google_review_id:
        # Update testimonial with Google review ID
        api.update_review_status(testimonial, google_review_id)
        logger.info(f"Successfully submitted testimonial {testimonial.id} to Google Business")
        return True, None
    else:
        logger.error(f"Failed to submit testimonial {testimonial.id} to Google Business: {error_message}")
        return False, error_message


def prepare_for_async_submission(testimonial_id: int) -> Dict:
    """
    Prepare testimonial data for async task queue submission.
    
    This function can be used with Django's task queue systems like Celery
    to submit reviews asynchronously.
    
    Args:
        testimonial_id: ID of the testimonial to submit
        
    Returns:
        Dict: Task data for queue processing
    """
    return {
        'task_type': 'google_business_review',
        'testimonial_id': testimonial_id,
        'timestamp': datetime.now().isoformat(),
        'retry_count': 0,
        'max_retries': 3
    }


# Example task function for Celery or similar task queue
async def process_google_review_task(task_data: Dict) -> Dict:
    """
    Process Google Business review submission as an async task.
    
    This function is designed to work with task queue systems.
    
    Args:
        task_data: Task data from prepare_for_async_submission
        
    Returns:
        Dict: Task result with status and details
    """
    from core.models import Testimonial
    
    testimonial_id = task_data['testimonial_id']
    retry_count = task_data.get('retry_count', 0)
    max_retries = task_data.get('max_retries', 3)
    
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        success, error_message = submit_testimonial_to_google(testimonial)
        
        if success:
            return {
                'status': 'success',
                'testimonial_id': testimonial_id,
                'message': 'Successfully submitted to Google Business'
            }
        else:
            # Retry logic
            if retry_count < max_retries:
                return {
                    'status': 'retry',
                    'testimonial_id': testimonial_id,
                    'error': error_message,
                    'retry_count': retry_count + 1
                }
            else:
                return {
                    'status': 'failed',
                    'testimonial_id': testimonial_id,
                    'error': error_message,
                    'final_attempt': True
                }
                
    except Testimonial.DoesNotExist:
        return {
            'status': 'failed',
            'testimonial_id': testimonial_id,
            'error': 'Testimonial not found'
        }
    except Exception as e:
        return {
            'status': 'error',
            'testimonial_id': testimonial_id,
            'error': str(e)
        }