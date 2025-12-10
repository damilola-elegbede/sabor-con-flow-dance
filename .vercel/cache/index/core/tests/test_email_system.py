"""
Comprehensive tests for Email Notification System - SPEC_05 Group B Task 10

Tests email service functionality, template rendering, error handling,
and integration with contact forms and booking confirmations.
"""

import os
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, call
from django.test import TestCase, override_settings
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from core.models import (
    Testimonial, ContactSubmission, BookingConfirmation, 
    RSVPSubmission
)
from core.utils.email_notifications import (
    EmailNotificationService,
    send_admin_notification_email,
    send_thank_you_email,
    send_approval_notification_email,
    send_weekly_summary_email,
    send_contact_admin_notification_email,
    send_contact_auto_reply_email,
    send_booking_confirmation_email,
    send_booking_admin_notification_email,
    send_booking_reminder_email,
    test_email_configuration,
    send_digest_email
)


class EmailNotificationServiceTestCase(TestCase):
    """Test cases for the EmailNotificationService class."""
    
    def setUp(self):
        """Set up test data."""
        self.service = EmailNotificationService()
        
        # Create test testimonial
        self.testimonial = Testimonial.objects.create(
            student_name='John Doe',
            email='john.doe@example.com',
            rating=5,
            content='Amazing dance classes! Highly recommend.',
            class_type='choreo_team',
            status='pending'
        )
        
        # Create test contact submission
        self.contact = ContactSubmission.objects.create(
            name='Jane Smith',
            email='jane.smith@example.com',
            phone='(555) 123-4567',
            interest='private_lesson',
            message='I would like to book private salsa lessons.',
            priority='high'
        )
        
        # Create test booking
        self.booking = BookingConfirmation.objects.create(
            customer_name='Bob Johnson',
            customer_email='bob.johnson@example.com',
            customer_phone='(555) 987-6543',
            booking_type='private_lesson',
            class_name='Private Salsa Lesson',
            instructor_name='Maria Rodriguez',
            booking_date=timezone.now() + timedelta(days=2),
            duration_minutes=60,
            price=75.00,
            payment_method='Venmo'
        )
    
    def test_service_initialization(self):
        """Test EmailNotificationService initialization."""
        service = EmailNotificationService()
        
        self.assertEqual(service.site_name, "Sabor Con Flow Dance")
        self.assertEqual(service.site_url, "https://www.saborconflowdance.com")
        self.assertIn('@', service.admin_email)
        self.assertIn('@', service.from_email)
    
    @patch.dict(os.environ, {})
    def test_is_email_configured_false(self):
        """Test email configuration check when not configured."""
        service = EmailNotificationService()
        self.assertFalse(service.is_email_configured())
    
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_is_email_configured_true(self):
        """Test email configuration check when properly configured."""
        service = EmailNotificationService()
        self.assertTrue(service.is_email_configured())
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_admin_notification_success(self):
        """Test successful admin notification email sending."""
        service = EmailNotificationService()
        result = service.send_admin_notification(self.testimonial)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertIn('New Testimonial Submission', email.subject)
        self.assertIn('John Doe', email.subject)
        self.assertIn(service.admin_email, email.to)
        self.assertIn('John Doe', email.body)
        self.assertIn('5 stars', email.body)
    
    @patch.dict(os.environ, {})
    def test_send_admin_notification_no_config(self):
        """Test admin notification when email not configured."""
        service = EmailNotificationService()
        result = service.send_admin_notification(self.testimonial)
        
        self.assertFalse(result)
        self.assertEqual(len(mail.outbox), 0)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_thank_you_email_success(self):
        """Test successful thank you email sending."""
        service = EmailNotificationService()
        result = service.send_thank_you_email(self.testimonial)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertIn('Thank You', email.subject)
        self.assertIn('Sabor Con Flow Dance', email.subject)
        self.assertIn('john.doe@example.com', email.to)
        self.assertIn('John', email.body)
        self.assertIn('testimonial', email.body.lower())
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_approval_notification_success(self):
        """Test successful approval notification email sending."""
        service = EmailNotificationService()
        result = service.send_approval_notification(self.testimonial)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertIn('Published', email.subject)
        self.assertIn('john.doe@example.com', email.to)
        self.assertIn('published', email.body.lower())
        self.assertIn('facebook', email.body.lower())  # Share links
        self.assertIn('twitter', email.body.lower())
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_weekly_summary_with_testimonials(self):
        """Test weekly summary email with testimonials."""
        # Create additional testimonials
        for i in range(3):
            Testimonial.objects.create(
                student_name=f'Student {i+1}',
                email=f'student{i+1}@example.com',
                rating=4 + (i % 2),
                content=f'Great experience {i+1}!',
                class_type='pasos_basicos',
                status='approved' if i % 2 == 0 else 'pending'
            )
        
        service = EmailNotificationService()
        start_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()
        
        result = service.send_weekly_summary(start_date, end_date)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertIn('Weekly Testimonials Summary', email.subject)
        self.assertIn('4 New Submissions', email.subject)  # Including setUp testimonial
        self.assertIn(service.admin_email, email.to)
        self.assertIn('testimonials', email.body.lower())
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_weekly_summary_no_testimonials(self):
        """Test weekly summary email with no new testimonials."""
        # Clear existing testimonials
        Testimonial.objects.all().delete()
        
        service = EmailNotificationService()
        start_date = timezone.now() - timedelta(days=7)
        end_date = timezone.now()
        
        result = service.send_weekly_summary(start_date, end_date)
        
        self.assertTrue(result)  # Still returns True but doesn't send email
        self.assertEqual(len(mail.outbox), 0)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_contact_admin_notification_success(self):
        """Test successful contact admin notification email."""
        service = EmailNotificationService()
        result = service.send_contact_admin_notification(self.contact)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        # Check that tracking was updated
        self.contact.refresh_from_db()
        self.assertTrue(self.contact.admin_notification_sent)
        
        email = mail.outbox[0]
        self.assertIn('New Contact Inquiry', email.subject)
        self.assertIn('Jane Smith', email.subject)
        self.assertIn('🔥 URGENT', email.subject)  # High priority
        self.assertIn(service.admin_email, email.to)
        self.assertIn('private lesson', email.body.lower())
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_contact_auto_reply_success(self):
        """Test successful contact auto-reply email."""
        service = EmailNotificationService()
        result = service.send_contact_auto_reply(self.contact)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        # Check that tracking was updated
        self.contact.refresh_from_db()
        self.assertTrue(self.contact.auto_reply_sent)
        
        email = mail.outbox[0]
        self.assertIn('Thank You for Contacting', email.subject)
        self.assertIn('jane.smith@example.com', email.to)
        self.assertIn('Jane', email.body)
        self.assertIn('Private Lessons', email.body)
        self.assertIn('24 hours', email.body)  # High priority response time
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_booking_confirmation_success(self):
        """Test successful booking confirmation email."""
        service = EmailNotificationService()
        result = service.send_booking_confirmation(self.booking)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        # Check that tracking was updated
        self.booking.refresh_from_db()
        self.assertTrue(self.booking.confirmation_email_sent)
        
        email = mail.outbox[0]
        self.assertIn('Booking Confirmed', email.subject)
        self.assertIn(self.booking.booking_id, email.subject)
        self.assertIn('bob.johnson@example.com', email.to)
        self.assertIn('Bob', email.body)
        self.assertIn('Private Salsa Lesson', email.body)
        self.assertIn('Maria Rodriguez', email.body)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_booking_admin_notification_success(self):
        """Test successful booking admin notification email."""
        service = EmailNotificationService()
        result = service.send_booking_admin_notification(self.booking)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertIn('New Booking', email.subject)
        self.assertIn(self.booking.booking_id, email.subject)
        self.assertIn('Bob Johnson', email.subject)
        self.assertIn(service.admin_email, email.to)
        self.assertIn('Private Salsa Lesson', email.body)
        self.assertIn('$75.00', email.body)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_booking_reminder_success(self):
        """Test successful booking reminder email."""
        service = EmailNotificationService()
        result = service.send_booking_reminder(self.booking)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        # Check that tracking was updated
        self.booking.refresh_from_db()
        self.assertTrue(self.booking.reminder_email_sent)
        
        email = mail.outbox[0]
        self.assertIn('Reminder', email.subject)
        self.assertIn('Tomorrow', email.subject)
        self.assertIn('bob.johnson@example.com', email.to)
        self.assertIn('reminder', email.body.lower())
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    @patch('core.utils.email_notifications.send_mail')
    def test_email_sending_error_handling(self, mock_send_mail):
        """Test error handling when email sending fails."""
        mock_send_mail.side_effect = Exception("SMTP Error")
        
        service = EmailNotificationService()
        result = service.send_thank_you_email(self.testimonial)
        
        self.assertFalse(result)
    
    def test_email_template_context(self):
        """Test that email templates receive correct context data."""
        service = EmailNotificationService()
        
        # Test testimonial context
        with patch('core.utils.email_notifications.render_to_string') as mock_render:
            mock_render.return_value = "Mocked template"
            service.send_admin_notification(self.testimonial)
            
            # Check that render_to_string was called with correct context
            args, kwargs = mock_render.call_args
            context = args[1]  # Second argument is context
            
            self.assertEqual(context['testimonial'], self.testimonial)
            self.assertEqual(context['site_name'], service.site_name)
            self.assertIn('admin_url', context)
            self.assertIn('submission_date', context)


class EmailConvenienceFunctionsTestCase(TestCase):
    """Test cases for email convenience functions."""
    
    def setUp(self):
        """Set up test data."""
        self.testimonial = Testimonial.objects.create(
            student_name='Test Student',
            email='test@example.com',
            rating=5,
            content='Great classes!',
            class_type='choreo_team'
        )
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_admin_notification_email_function(self):
        """Test send_admin_notification_email convenience function."""
        result = send_admin_notification_email(self.testimonial)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_thank_you_email_function(self):
        """Test send_thank_you_email convenience function."""
        result = send_thank_you_email(self.testimonial)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_approval_notification_email_function(self):
        """Test send_approval_notification_email convenience function."""
        result = send_approval_notification_email(self.testimonial)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_weekly_summary_email_function(self):
        """Test send_weekly_summary_email convenience function."""
        result = send_weekly_summary_email()
        
        # Should return True even if no testimonials to summarize
        self.assertTrue(result)


class EmailConfigurationTestCase(TestCase):
    """Test cases for email configuration and testing utilities."""
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_email_configuration_test_success(self):
        """Test email configuration testing with valid config."""
        result = test_email_configuration()
        
        self.assertTrue(result['configured'])
        self.assertTrue(result['test_email_sent'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertIn('Email Configuration Test', email.subject)
    
    @patch.dict(os.environ, {})
    def test_email_configuration_test_no_config(self):
        """Test email configuration testing with no config."""
        result = test_email_configuration()
        
        self.assertFalse(result['configured'])
        self.assertIn('not configured', result['errors'][0])
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    @patch('core.utils.email_notifications.send_mail')
    def test_email_configuration_test_send_error(self, mock_send_mail):
        """Test email configuration testing with send error."""
        mock_send_mail.side_effect = Exception("SMTP Error")
        
        result = test_email_configuration()
        
        self.assertTrue(result['configured'])
        self.assertFalse(result['test_email_sent'])
        self.assertIn('Failed to send test email', result['errors'][0])


class EmailDigestTestCase(TestCase):
    """Test cases for email digest functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test data across different models
        self.testimonial = Testimonial.objects.create(
            student_name='Digest Testimonial',
            email='digest@example.com',
            rating=5,
            content='Great for digest!',
            class_type='choreo_team',
            status='approved'
        )
        
        self.contact = ContactSubmission.objects.create(
            name='Digest Contact',
            email='contact@example.com',
            interest='classes',
            message='Digest contact message'
        )
        
        self.booking = BookingConfirmation.objects.create(
            customer_name='Digest Booking',
            customer_email='booking@example.com',
            booking_type='class',
            class_name='Test Class',
            booking_date=timezone.now() + timedelta(days=1),
            price=20.00
        )
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_digest_email_with_activity(self):
        """Test digest email with recent activity."""
        result = send_digest_email(days_back=7)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertIn('Activity Digest', email.subject)
        self.assertIn('3 Items', email.subject)  # 1 testimonial + 1 contact + 1 booking
        self.assertIn('testimonials', email.body.lower())
        self.assertIn('contacts', email.body.lower())
        self.assertIn('bookings', email.body.lower())
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_send_digest_email_no_activity(self):
        """Test digest email with no recent activity."""
        # Clear all data
        Testimonial.objects.all().delete()
        ContactSubmission.objects.all().delete()
        BookingConfirmation.objects.all().delete()
        
        result = send_digest_email(days_back=7)
        
        self.assertTrue(result)  # Returns True but doesn't send email
        self.assertEqual(len(mail.outbox), 0)
    
    @patch.dict(os.environ, {})
    def test_send_digest_email_no_config(self):
        """Test digest email with no email configuration."""
        result = send_digest_email(days_back=7)
        
        self.assertFalse(result)


class EmailTemplateTestCase(TestCase):
    """Test cases for email template rendering and content."""
    
    def setUp(self):
        """Set up test data."""
        self.testimonial = Testimonial.objects.create(
            student_name='Template Test',
            email='template@example.com',
            rating=4,
            content='Testing email templates!',
            class_type='casino_royale'
        )
    
    def test_admin_notification_template_context(self):
        """Test admin notification template receives correct context."""
        service = EmailNotificationService()
        
        # Mock template rendering to capture context
        with patch('core.utils.email_notifications.render_to_string') as mock_render:
            mock_render.return_value = "Test template content"
            
            service.send_admin_notification(self.testimonial)
            
            # Verify template was called with correct parameters
            mock_render.assert_called_once()
            template_name, context = mock_render.call_args[0]
            
            self.assertEqual(template_name, 'emails/admin_notification.html')
            self.assertEqual(context['testimonial'], self.testimonial)
            self.assertEqual(context['site_name'], service.site_name)
            self.assertIn('admin_url', context)
            self.assertIn('class_type_display', context)
            self.assertIn('submission_date', context)
    
    def test_thank_you_template_context(self):
        """Test thank you template receives correct context."""
        service = EmailNotificationService()
        
        with patch('core.utils.email_notifications.render_to_string') as mock_render:
            mock_render.return_value = "Test template content"
            
            service.send_thank_you_email(self.testimonial)
            
            template_name, context = mock_render.call_args[0]
            
            self.assertEqual(template_name, 'emails/thank_you.html')
            self.assertEqual(context['student_name'], 'Template Test')
            self.assertEqual(context['testimonial'], self.testimonial)
            self.assertIn('testimonials_url', context)
    
    def test_html_and_text_email_versions(self):
        """Test that emails include both HTML and text versions."""
        service = EmailNotificationService()
        
        with patch('core.utils.email_notifications.EmailMultiAlternatives') as mock_email_class:
            mock_email = Mock()
            mock_email_class.return_value = mock_email
            
            service.send_thank_you_email(self.testimonial)
            
            # Verify EmailMultiAlternatives was used
            mock_email_class.assert_called_once()
            
            # Verify both text and HTML content were provided
            args, kwargs = mock_email_class.call_args
            self.assertIn('body', kwargs)  # Text version
            
            # Verify HTML alternative was attached
            mock_email.attach_alternative.assert_called_once()
            html_content, content_type = mock_email.attach_alternative.call_args[0]
            self.assertEqual(content_type, "text/html")


class EmailIntegrationTestCase(TestCase):
    """Integration tests for email system with views and forms."""
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_testimonial_submission_email_flow(self):
        """Test complete email flow for testimonial submission."""
        response = self.client.post('/testimonials/submit/', {
            'student_name': 'Integration Test',
            'email': 'integration@example.com',
            'rating': 5,
            'content': 'This is a test testimonial for integration testing.',
            'class_type': 'choreo_team'
        })
        
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)
        
        # Should have sent two emails: admin notification and thank you
        self.assertEqual(len(mail.outbox), 2)
        
        # Check admin notification
        admin_email = next(email for email in mail.outbox if 'admin' in email.to[0].lower())
        self.assertIn('New Testimonial Submission', admin_email.subject)
        self.assertIn('Integration Test', admin_email.subject)
        
        # Check thank you email
        thank_you_email = next(email for email in mail.outbox if 'integration@example.com' in email.to)
        self.assertIn('Thank You', thank_you_email.subject)
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch.dict(os.environ, {
        'EMAIL_HOST_USER': 'test@example.com',
        'EMAIL_HOST_PASSWORD': 'testpass123'
    })
    def test_contact_form_email_flow(self):
        """Test complete email flow for contact form submission."""
        response = self.client.post('/contact/', {
            'name': 'Integration Contact',
            'email': 'contact-integration@example.com',
            'phone': '(555) 123-4567',
            'interest': 'private_lesson',
            'message': 'This is a test contact form submission for integration testing.'
        })
        
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)
        
        # Should have sent two emails: admin notification and auto-reply
        self.assertEqual(len(mail.outbox), 2)
        
        # Check admin notification
        admin_email = next(email for email in mail.outbox 
                          if any('admin' in recipient.lower() for recipient in email.to))
        self.assertIn('New Contact Inquiry', admin_email.subject)
        self.assertIn('Integration Contact', admin_email.subject)
        
        # Check auto-reply
        auto_reply = next(email for email in mail.outbox 
                         if 'contact-integration@example.com' in email.to)
        self.assertIn('Thank You for Contacting', auto_reply.subject)
    
    def test_email_error_handling_in_views(self):
        """Test that view handles email errors gracefully."""
        with patch('core.utils.email_notifications.send_admin_notification_email') as mock_send:
            mock_send.side_effect = Exception("Email error")
            
            response = self.client.post('/testimonials/submit/', {
                'student_name': 'Error Test',
                'email': 'error@example.com',
                'rating': 5,
                'content': 'This should handle email errors gracefully.',
                'class_type': 'choreo_team'
            })
            
            # Should still redirect successfully even if email fails
            self.assertEqual(response.status_code, 302)
            
            # Testimonial should still be created
            testimonial = Testimonial.objects.get(student_name='Error Test')
            self.assertEqual(testimonial.status, 'pending')