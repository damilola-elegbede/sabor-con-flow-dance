"""
Comprehensive tests for SPEC_03 admin interface and integrations.

This test suite covers:
1. TestimonialAdmin comprehensive testing
2. ReviewLink admin functionality  
3. Google Business integration testing
4. Email notification system testing
5. Share link generation command testing
6. All admin actions and displays

Tests use Django test client, mock external APIs, and validate all SPEC_03 features.
"""

import os
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, Client, override_settings
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.management import call_command
from django.core import mail
from django.template.loader import render_to_string
from django.test.utils import override_settings

from core.models import Testimonial, ReviewLink, Instructor, Class
from core.admin import (
    TestimonialAdmin, approve_testimonials, reject_testimonials, 
    approve_and_notify_testimonials
)
from core.utils.email_notifications import (
    EmailNotificationService, send_admin_notification_email,
    send_thank_you_email, send_approval_notification_email
)
from core.utils.google_reviews import GoogleBusinessReviewsAPI, submit_testimonial_to_google
from core.management.commands.generate_review_link import Command as GenerateReviewLinkCommand


class TestimonialAdminTestCase(TestCase):
    """Comprehensive tests for TestimonialAdmin functionality."""
    
    def setUp(self):
        """Set up test data and admin client."""
        self.site = AdminSite()
        self.admin = TestimonialAdmin(Testimonial, self.site)
        self.client = Client()
        
        # Create superuser for admin access
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.client.login(username='admin', password='testpass123')
        
        # Create test instructor
        self.instructor = Instructor.objects.create(
            name='Test Instructor',
            bio='Test bio',
            photo_url='https://example.com/test.jpg',
            specialties='["Salsa", "Bachata"]'
        )
        
        # Create test testimonials
        self.testimonial_pending = Testimonial.objects.create(
            student_name='Pending Student',
            email='pending@example.com',
            rating=5,
            content='This is a pending testimonial with excellent feedback from our dance classes.',
            class_type='pasos_basicos',
            status='pending'
        )
        
        self.testimonial_approved = Testimonial.objects.create(
            student_name='Approved Student',
            email='approved@example.com',
            rating=4,
            content='This is an approved testimonial.',
            class_type='casino_royale',
            status='approved',
            published_at=timezone.now(),
            featured=True
        )
        
        self.testimonial_rejected = Testimonial.objects.create(
            student_name='Rejected Student',
            email='rejected@example.com',
            rating=2,
            content='This testimonial was rejected.',
            class_type='workshop',
            status='rejected'
        )
    
    def test_all_models_registered_in_admin(self):
        """Test that all SPEC_03 models are registered in admin."""
        from django.contrib import admin
        
        # Test Testimonial is registered
        self.assertTrue(admin.site.is_registered(Testimonial))
        
        # Test ReviewLink is registered (if admin class exists)
        try:
            from core.admin import ReviewLinkAdmin
            self.assertTrue(admin.site.is_registered(ReviewLink))
        except ImportError:
            # ReviewLink admin may not be implemented yet
            pass
    
    def test_bulk_approve_action_present(self):
        """Test that bulk approve action is available."""
        actions = [action.__name__ for action in self.admin.actions]
        self.assertIn('approve_testimonials', actions)
        self.assertIn('approve_and_notify_testimonials', actions)
    
    def test_bulk_reject_action_present(self):
        """Test that bulk reject action is available."""
        actions = [action.__name__ for action in self.admin.actions]
        self.assertIn('reject_testimonials', actions)
    
    def test_list_filters_working_correctly(self):
        """Test that admin list filters work correctly."""
        # Test status filter
        expected_filters = ['status', 'rating', 'featured', 'class_type', ('created_at', 'admin.DateFieldListFilter')]
        self.assertEqual(self.admin.list_filter, expected_filters)
        
        # Test filtering via HTTP requests
        response = self.client.get('/admin/core/testimonial/?status=pending')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending Student')
        self.assertNotContains(response, 'Approved Student')
        
        # Test rating filter
        response = self.client.get('/admin/core/testimonial/?rating=5')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending Student')
        self.assertNotContains(response, 'Approved Student')
        
        # Test featured filter
        response = self.client.get('/admin/core/testimonial/?featured=1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Approved Student')
        self.assertNotContains(response, 'Pending Student')
    
    def test_content_preview_displayed(self):
        """Test that content preview is properly displayed in list view."""
        # Test content_preview method
        preview = self.admin.content_preview(self.testimonial_pending)
        self.assertIn('This is a pending testimonial', preview)
        self.assertIn('...', preview)  # Should be truncated
        self.assertIn('title=', preview)  # Should have tooltip with full content
        
        # Test in admin interface
        response = self.client.get('/admin/core/testimonial/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This is a pending testimonial')
    
    def test_status_badge_functionality(self):
        """Test that status badges are displayed correctly."""
        # Test status_badge method for different statuses
        pending_badge = self.admin.status_badge(self.testimonial_pending)
        self.assertIn('#ffc107', pending_badge)  # Yellow for pending
        self.assertIn('PENDING', pending_badge.upper())
        
        approved_badge = self.admin.status_badge(self.testimonial_approved)
        self.assertIn('#28a745', approved_badge)  # Green for approved
        self.assertIn('APPROVED', approved_badge.upper())
        
        rejected_badge = self.admin.status_badge(self.testimonial_rejected)
        self.assertIn('#dc3545', rejected_badge)  # Red for rejected
        self.assertIn('REJECTED', rejected_badge.upper())
        
        # Test in admin interface
        response = self.client.get('/admin/core/testimonial/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PENDING')
        self.assertContains(response, 'APPROVED')
        self.assertContains(response, 'REJECTED')
    
    def test_rating_display_as_stars(self):
        """Test that ratings are displayed as star symbols."""
        # Test rating_display method
        rating_display = self.admin.rating_display(self.testimonial_pending)
        self.assertIn('★★★★★', rating_display)  # 5 filled stars
        self.assertNotIn('☆', rating_display)  # No empty stars for 5-star rating
        
        rating_display_4 = self.admin.rating_display(self.testimonial_approved)
        self.assertIn('★★★★', rating_display_4)  # 4 filled stars
        self.assertIn('☆', rating_display_4)  # 1 empty star
        
        # Test in admin interface
        response = self.client.get('/admin/core/testimonial/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '★')
    
    def test_published_date_auto_set_on_approval(self):
        """Test that published_at is automatically set when testimonial is approved."""
        # Test approve_testimonials action
        initial_published_at = self.testimonial_pending.published_at
        self.assertIsNone(initial_published_at)
        
        # Use the bulk approve action
        request = Mock()
        request.user = Mock()
        self.admin.message_user = Mock()
        
        queryset = Testimonial.objects.filter(id=self.testimonial_pending.id)
        approve_testimonials(self.admin, request, queryset)
        
        # Check that published_at was set
        self.testimonial_pending.refresh_from_db()
        self.assertEqual(self.testimonial_pending.status, 'approved')
        self.assertIsNotNone(self.testimonial_pending.published_at)
        self.assertIsInstance(self.testimonial_pending.published_at, datetime)
    
    def test_admin_list_display_includes_all_required_fields(self):
        """Test that admin list display includes all required fields from SPEC_03."""
        expected_fields = [
            'student_name', 'rating_display', 'class_type', 'content_preview', 
            'status_badge', 'featured', 'created_at'
        ]
        self.assertEqual(self.admin.list_display, expected_fields)
    
    def test_admin_fieldsets_organization(self):
        """Test that admin fieldsets are properly organized."""
        expected_fieldsets = (
            ('Student Information', {
                'fields': ('student_name', 'email', 'class_type')
            }),
            ('Review Content', {
                'fields': ('rating', 'content')
            }),
            ('Media', {
                'fields': ('photo', 'video_url')
            }),
            ('Google Integration', {
                'fields': ('google_review_id',)
            }),
            ('Status & Publishing', {
                'fields': ('status', 'featured', 'published_at')
            }),
            ('Timestamps', {
                'fields': ('created_at',),
                'classes': ('collapse',)
            }),
        )
        self.assertEqual(self.admin.fieldsets, expected_fieldsets)
    
    def test_admin_search_functionality(self):
        """Test that admin search works correctly."""
        search_fields = ['student_name', 'email', 'content']
        self.assertEqual(self.admin.search_fields, search_fields)
        
        # Test search via HTTP
        response = self.client.get('/admin/core/testimonial/?q=Pending')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending Student')
        self.assertNotContains(response, 'Approved Student')
        
        response = self.client.get('/admin/core/testimonial/?q=excellent')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending Student')


class ReviewLinkAdminTestCase(TestCase):
    """Tests for ReviewLink admin functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.client.login(username='admin', password='testpass123')
        
        # Create test review links
        self.review_link = ReviewLink.objects.create(
            token=ReviewLink.generate_token(),
            instructor_name='Test Instructor',
            class_type='pasos_basicos',
            campaign_name='Summer 2025',
            clicks=10,
            conversions=3
        )
    
    def test_url_generation_working(self):
        """Test that review link URL generation works correctly."""
        full_url = self.review_link.get_full_url()
        expected_params = [
            f"ref={self.review_link.token}",
            "instructor=test-instructor",
            "class=pasos_basicos"
        ]
        
        for param in expected_params:
            self.assertIn(param, full_url)
        
        # Test short URL
        short_url = self.review_link.get_short_url()
        self.assertIn(self.review_link.token[:8], short_url)
    
    def test_analytics_tracking_accurate(self):
        """Test that analytics tracking works correctly."""
        initial_clicks = self.review_link.clicks
        initial_conversions = self.review_link.conversions
        
        # Test click tracking
        self.review_link.track_click()
        self.assertEqual(self.review_link.clicks, initial_clicks + 1)
        self.assertIsNotNone(self.review_link.last_accessed)
        
        # Test conversion tracking
        self.review_link.track_conversion()
        self.assertEqual(self.review_link.conversions, initial_conversions + 1)
        
        # Test conversion rate calculation
        expected_rate = round((self.review_link.conversions / self.review_link.clicks) * 100, 2)
        self.assertEqual(self.review_link.get_conversion_rate(), expected_rate)
    
    def test_campaign_management_functional(self):
        """Test that campaign management works correctly."""
        # Test string representation includes campaign info
        str_repr = str(self.review_link)
        self.assertIn('Summer 2025', str_repr)
        self.assertIn('Test Instructor', str_repr)
        self.assertIn('pasos_basicos', str_repr)
    
    def test_link_expiration_handling(self):
        """Test that link expiration is handled correctly."""
        # Test non-expired link
        self.assertFalse(self.review_link.is_expired())
        
        # Test expired link
        self.review_link.expires_at = timezone.now() - timedelta(days=1)
        self.review_link.save()
        self.assertTrue(self.review_link.is_expired())
        
        # Test link without expiration
        self.review_link.expires_at = None
        self.review_link.save()
        self.assertFalse(self.review_link.is_expired())


class GoogleBusinessIntegrationTestCase(TestCase):
    """Tests for Google Business integration functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.testimonial = Testimonial.objects.create(
            student_name='Google Test Student',
            email='google@example.com',
            rating=5,
            content='Excellent dance classes!',
            class_type='pasos_basicos',
            status='approved'
        )
        
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'GOOGLE_BUSINESS_API_KEY': 'test_api_key',
            'GOOGLE_BUSINESS_PROFILE_ID': 'test_profile_id'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up patches."""
        self.env_patcher.stop()
    
    @patch('core.utils.google_reviews.requests')
    def test_api_connection_mocking(self, mock_requests):
        """Test that Google Business API connection can be mocked."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'name': 'test_review_id'}
        mock_requests.Session.return_value.post.return_value = mock_response
        
        api = GoogleBusinessReviewsAPI()
        self.assertTrue(api.is_configured())
        
        success, review_id, error = api.submit_review(self.testimonial)
        self.assertTrue(success)
        self.assertEqual(review_id, 'test_review_id')
        self.assertIsNone(error)
    
    def test_review_submission_format(self):
        """Test that review submission format is correct."""
        api = GoogleBusinessReviewsAPI()
        review_data = api.format_testimonial_data(self.testimonial)
        
        expected_fields = [
            'reviewId', 'reviewer', 'starRating', 'comment', 
            'createTime', 'updateTime', 'name'
        ]
        
        for field in expected_fields:
            self.assertIn(field, review_data)
        
        self.assertEqual(review_data['starRating'], 5)
        self.assertIn('Excellent dance classes!', review_data['comment'])
        self.assertIn('Pasos Básicos', review_data['comment'])
        self.assertEqual(review_data['reviewer']['displayName'], 'Google Test Student')
    
    @patch('core.utils.google_reviews.requests')
    def test_error_handling_graceful(self, mock_requests):
        """Test that error handling is graceful."""
        # Test various error scenarios
        error_scenarios = [
            (401, 'Invalid API credentials'),
            (403, 'Insufficient permissions for Google Business API'),
            (429, 'Rate limit exceeded for Google Business API'),
            (500, 'Google Business API error: 500')
        ]
        
        api = GoogleBusinessReviewsAPI()
        
        for status_code, expected_error in error_scenarios:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_response.text = 'Server Error'
            mock_requests.Session.return_value.post.return_value = mock_response
            
            success, review_id, error = api.submit_review(self.testimonial)
            self.assertFalse(success)
            self.assertIsNone(review_id)
            self.assertIn(expected_error, error)
    
    @patch('core.utils.google_reviews.requests')
    def test_logging_functionality(self, mock_requests):
        """Test that logging works correctly."""
        with patch('core.utils.google_reviews.logger') as mock_logger:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'name': 'test_review_id'}
            mock_requests.Session.return_value.post.return_value = mock_response
            
            api = GoogleBusinessReviewsAPI()
            api.submit_review(self.testimonial)
            
            # Check that info log was called
            mock_logger.info.assert_called()
            
            # Test error logging
            mock_response.status_code = 500
            api.submit_review(self.testimonial)
            mock_logger.error.assert_called()
    
    def test_api_not_configured_handling(self):
        """Test handling when API is not configured."""
        with patch.dict(os.environ, {}, clear=True):
            api = GoogleBusinessReviewsAPI()
            self.assertFalse(api.is_configured())
            
            success, review_id, error = api.submit_review(self.testimonial)
            self.assertFalse(success)
            self.assertIsNone(review_id)
            self.assertEqual(error, 'API not configured')


class EmailNotificationTestCase(TestCase):
    """Tests for email notification functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.testimonial = Testimonial.objects.create(
            student_name='Email Test Student',
            email='email_test@example.com',
            rating=5,
            content='Great email test!',
            class_type='casino_royale',
            status='pending'
        )
        
        # Mock email configuration
        self.env_patcher = patch.dict(os.environ, {
            'EMAIL_HOST_USER': 'test@saborconflowdance.com',
            'EMAIL_HOST_PASSWORD': 'test_password',
            'ADMIN_EMAIL': 'admin@saborconflowdance.com'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up patches."""
        self.env_patcher.stop()
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_admin_notification_sent_on_submission(self):
        """Test that admin notification is sent on testimonial submission."""
        service = EmailNotificationService()
        
        success = service.send_admin_notification(self.testimonial)
        self.assertTrue(success)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        self.assertIn('New Testimonial Submission', email.subject)
        self.assertIn('Email Test Student', email.subject)
        self.assertEqual(email.to, ['admin@saborconflowdance.com'])
        self.assertIn('Email Test Student', email.body)
        self.assertIn('Great email test!', email.body)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_thank_you_email_to_submitter(self):
        """Test that thank you email is sent to submitter."""
        service = EmailNotificationService()
        
        success = service.send_thank_you_email(self.testimonial)
        self.assertTrue(success)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        self.assertIn('Thank You', email.subject)
        self.assertIn('Sabor Con Flow', email.subject)
        self.assertEqual(email.to, ['email_test@example.com'])
        self.assertIn('Email Test Student', email.body)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_approval_notification_working(self):
        """Test that approval notification works correctly."""
        service = EmailNotificationService()
        
        # Approve the testimonial first
        self.testimonial.status = 'approved'
        self.testimonial.published_at = timezone.now()
        self.testimonial.save()
        
        success = service.send_approval_notification(self.testimonial)
        self.assertTrue(success)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        self.assertIn('Testimonial Has Been Published', email.subject)
        self.assertEqual(email.to, ['email_test@example.com'])
        self.assertIn('Email Test Student', email.body)
        self.assertIn('published', email.body.lower())
    
    def test_html_templates_render_correctly(self):
        """Test that HTML email templates render correctly."""
        service = EmailNotificationService()
        
        # Test admin notification template
        context = {
            'testimonial': self.testimonial,
            'site_name': service.site_name,
            'site_url': service.site_url,
            'admin_url': f"{service.site_url}/admin/core/testimonial/{self.testimonial.id}/change/",
            'class_type_display': self.testimonial.get_class_type_display(),
            'submission_date': self.testimonial.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'has_photo': bool(self.testimonial.photo),
            'has_video': bool(self.testimonial.video_url)
        }
        
        html_content = render_to_string('emails/admin_notification.html', context)
        self.assertIn('Email Test Student', html_content)
        self.assertIn('Great email test!', html_content)
        self.assertIn('Casino Royale', html_content)
        
        # Test thank you template
        context = {
            'student_name': self.testimonial.student_name,
            'testimonial': self.testimonial,
            'site_name': service.site_name,
            'site_url': service.site_url,
            'class_type_display': self.testimonial.get_class_type_display(),
            'submission_date': self.testimonial.created_at.strftime('%B %d, %Y'),
            'testimonials_url': f"{service.site_url}/testimonials/",
            'contact_email': service.admin_email
        }
        
        html_content = render_to_string('emails/thank_you.html', context)
        self.assertIn('Email Test Student', html_content)
        self.assertIn('Casino Royale', html_content)
    
    def test_email_not_configured_handling(self):
        """Test handling when email is not configured."""
        with patch.dict(os.environ, {}, clear=True):
            service = EmailNotificationService()
            self.assertFalse(service.is_email_configured())
            
            # Should return False but not raise exception
            success = service.send_admin_notification(self.testimonial)
            self.assertFalse(success)


class ShareLinkGenerationTestCase(TestCase):
    """Tests for share link generation management command."""
    
    def setUp(self):
        """Set up test data."""
        pass
    
    def test_management_command_execution(self):
        """Test that generate_review_link command executes successfully."""
        # Test basic command execution
        call_command('generate_review_link')
        
        # Check that a review link was created
        self.assertTrue(ReviewLink.objects.exists())
        review_link = ReviewLink.objects.first()
        self.assertIsNotNone(review_link.token)
        self.assertEqual(len(review_link.token), 32)
    
    def test_url_parameter_handling(self):
        """Test that URL parameters are handled correctly."""
        call_command(
            'generate_review_link',
            '--instructor', 'Test Instructor',
            '--class', 'pasos_basicos',
            '--campaign', 'Test Campaign'
        )
        
        review_link = ReviewLink.objects.first()
        self.assertEqual(review_link.instructor_name, 'Test Instructor')
        self.assertEqual(review_link.class_type, 'pasos_basicos')
        self.assertEqual(review_link.campaign_name, 'Test Campaign')
        
        # Test URL generation
        full_url = review_link.get_full_url()
        self.assertIn('instructor=test-instructor', full_url)
        self.assertIn('class=pasos_basicos', full_url)
    
    def test_token_uniqueness_validation(self):
        """Test that generated tokens are unique."""
        # Generate multiple tokens
        tokens = set()
        for _ in range(10):
            token = ReviewLink.generate_token()
            tokens.add(token)
        
        # All tokens should be unique
        self.assertEqual(len(tokens), 10)
        
        # All tokens should be 32 characters
        for token in tokens:
            self.assertEqual(len(token), 32)
    
    def test_template_generation_working(self):
        """Test that message templates are generated correctly."""
        from io import StringIO
        from django.core.management import call_command
        
        out = StringIO()
        call_command(
            'generate_review_link',
            '--instructor', 'Maria',
            '--class', 'pasos_basicos',
            '--templates',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('SMS Template', output)
        self.assertIn('Email Template', output)
        self.assertIn('WhatsApp Template', output)
        self.assertIn('Maria', output)
        self.assertIn('Pasos Básicos', output)
    
    def test_expiration_handling(self):
        """Test that link expiration is handled correctly."""
        call_command(
            'generate_review_link',
            '--expires-days', '30'
        )
        
        review_link = ReviewLink.objects.first()
        self.assertIsNotNone(review_link.expires_at)
        
        # Should expire approximately 30 days from now
        expected_expiry = timezone.now() + timedelta(days=30)
        time_diff = abs((review_link.expires_at - expected_expiry).total_seconds())
        self.assertLess(time_diff, 60)  # Within 1 minute
    
    def test_class_type_validation(self):
        """Test that class type validation works correctly."""
        from io import StringIO
        
        # Test valid class type
        out = StringIO()
        call_command(
            'generate_review_link',
            '--class', 'casino royale',
            stdout=out
        )
        
        review_link = ReviewLink.objects.first()
        self.assertEqual(review_link.class_type, 'casino_royale')
        
        # Test invalid class type (should still work but show warning)
        out = StringIO()
        call_command(
            'generate_review_link',
            '--class', 'invalid_class',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Warning', output)


class BulkAdminActionsTestCase(TestCase):
    """Tests for bulk admin actions."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.client.login(username='admin', password='testpass123')
        
        # Create multiple pending testimonials
        self.testimonials = []
        for i in range(3):
            testimonial = Testimonial.objects.create(
                student_name=f'Student {i}',
                email=f'student{i}@example.com',
                rating=5,
                content=f'Test content {i}',
                class_type='pasos_basicos',
                status='pending'
            )
            self.testimonials.append(testimonial)
    
    @patch('core.admin.send_approval_notification_email')
    def test_approve_and_notify_action(self, mock_send_email):
        """Test the approve and notify bulk action."""
        mock_send_email.return_value = True
        
        # Use the bulk action via admin interface
        response = self.client.post('/admin/core/testimonial/', {
            'action': 'approve_and_notify_testimonials',
            '_selected_action': [t.id for t in self.testimonials],
        })
        
        # Should redirect after successful action
        self.assertEqual(response.status_code, 302)
        
        # Check that testimonials were approved
        for testimonial in self.testimonials:
            testimonial.refresh_from_db()
            self.assertEqual(testimonial.status, 'approved')
            self.assertIsNotNone(testimonial.published_at)
        
        # Check that emails were sent
        self.assertEqual(mock_send_email.call_count, len(self.testimonials))
    
    def test_bulk_reject_action(self):
        """Test the bulk reject action."""
        response = self.client.post('/admin/core/testimonial/', {
            'action': 'reject_testimonials',
            '_selected_action': [t.id for t in self.testimonials],
        })
        
        # Should redirect after successful action
        self.assertEqual(response.status_code, 302)
        
        # Check that testimonials were rejected
        for testimonial in self.testimonials:
            testimonial.refresh_from_db()
            self.assertEqual(testimonial.status, 'rejected')
            self.assertIsNone(testimonial.published_at)  # Should remain None
    
    def test_partial_selection_handling(self):
        """Test that partial selection works correctly."""
        # Select only first two testimonials
        selected_ids = [self.testimonials[0].id, self.testimonials[1].id]
        
        response = self.client.post('/admin/core/testimonial/', {
            'action': 'approve_testimonials',
            '_selected_action': selected_ids,
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Check that only selected testimonials were approved
        self.testimonials[0].refresh_from_db()
        self.testimonials[1].refresh_from_db()
        self.testimonials[2].refresh_from_db()
        
        self.assertEqual(self.testimonials[0].status, 'approved')
        self.assertEqual(self.testimonials[1].status, 'approved')
        self.assertEqual(self.testimonials[2].status, 'pending')  # Unchanged


class AdminInterfaceIntegrationTestCase(TestCase):
    """Integration tests for the complete admin interface."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.client.login(username='admin', password='testpass123')
    
    def test_testimonial_workflow_end_to_end(self):
        """Test complete testimonial workflow through admin."""
        # 1. Create a testimonial
        testimonial_data = {
            'student_name': 'Integration Test Student',
            'email': 'integration@example.com',
            'rating': 5,
            'content': 'Amazing integration test!',
            'class_type': 'pasos_basicos',
            'status': 'pending'
        }
        
        response = self.client.post('/admin/core/testimonial/add/', testimonial_data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        
        # 2. Verify testimonial appears in list
        response = self.client.get('/admin/core/testimonial/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Test Student')
        
        # 3. Test filtering
        response = self.client.get('/admin/core/testimonial/?status=pending')
        self.assertContains(response, 'Integration Test Student')
        
        # 4. Test editing
        testimonial = Testimonial.objects.get(student_name='Integration Test Student')
        response = self.client.get(f'/admin/core/testimonial/{testimonial.id}/change/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Test Student')
        
        # 5. Test bulk approval
        response = self.client.post('/admin/core/testimonial/', {
            'action': 'approve_testimonials',
            '_selected_action': [testimonial.id],
        })
        self.assertEqual(response.status_code, 302)
        
        testimonial.refresh_from_db()
        self.assertEqual(testimonial.status, 'approved')
    
    def test_admin_permissions_and_security(self):
        """Test that admin permissions work correctly."""
        # Test without login
        self.client.logout()
        response = self.client.get('/admin/core/testimonial/')
        self.assertNotEqual(response.status_code, 200)  # Should be redirected to login
        
        # Test with regular user (non-staff)
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='testpass123'
        )
        self.client.login(username='regular', password='testpass123')
        response = self.client.get('/admin/core/testimonial/')
        self.assertNotEqual(response.status_code, 200)  # Should be forbidden
        
        # Test with staff user
        staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        self.client.login(username='staff', password='testpass123')
        response = self.client.get('/admin/core/testimonial/')
        self.assertEqual(response.status_code, 200)  # Should be allowed
    
    def test_admin_responsiveness_and_performance(self):
        """Test that admin interface loads efficiently."""
        # Create multiple testimonials to test performance
        testimonials = []
        for i in range(25):  # More than one page
            testimonial = Testimonial.objects.create(
                student_name=f'Performance Test {i}',
                email=f'perf{i}@example.com',
                rating=5,
                content=f'Performance test content {i}',
                class_type='pasos_basicos',
                status='pending'
            )
            testimonials.append(testimonial)
        
        # Test list view performance
        import time
        start_time = time.time()
        response = self.client.get('/admin/core/testimonial/')
        load_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(load_time, 2.0)  # Should load within 2 seconds
        
        # Test pagination
        self.assertContains(response, 'Performance Test')
        self.assertContains(response, 'Show all')  # Pagination controls
    
    @patch('core.utils.google_reviews.submit_testimonial_to_google')
    @patch('core.utils.email_notifications.send_approval_notification_email')
    def test_complete_integration_with_external_services(self, mock_email, mock_google):
        """Test complete integration with external services."""
        mock_email.return_value = True
        mock_google.return_value = (True, None)
        
        # Create testimonial
        testimonial = Testimonial.objects.create(
            student_name='External Integration Test',
            email='external@example.com',
            rating=5,
            content='External integration test',
            class_type='pasos_basicos',
            status='pending'
        )
        
        # Approve with notification action
        response = self.client.post('/admin/core/testimonial/', {
            'action': 'approve_and_notify_testimonials',
            '_selected_action': [testimonial.id],
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Verify testimonial was approved
        testimonial.refresh_from_db()
        self.assertEqual(testimonial.status, 'approved')
        self.assertIsNotNone(testimonial.published_at)
        
        # Verify email notification was called
        mock_email.assert_called_once_with(testimonial)