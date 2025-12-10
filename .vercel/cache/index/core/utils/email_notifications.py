"""
Comprehensive Email Notification System for Sabor Con Flow Dance

This module provides comprehensive email functionality for the entire system:
- Testimonial notifications (admin, thank you, approval)
- Contact form notifications (admin, auto-reply)
- Booking confirmation emails (customer, admin)
- Weekly summary emails
- Enhanced testimonial notifications

SPEC_05 Group B Task 10 - Comprehensive email notifications system

Environment Variables Required:
- EMAIL_HOST_USER: SMTP username  
- EMAIL_HOST_PASSWORD: SMTP password
- ADMIN_EMAIL: Email address for admin notifications
- DEFAULT_FROM_EMAIL: Default from email address
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.utils import timezone
from django.db.models import Count, Q

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """
    Service class for handling all testimonial-related email notifications.
    
    Provides methods for sending different types of emails with HTML templates
    and proper error handling.
    """
    
    def __init__(self):
        """Initialize email service with configuration."""
        self.admin_email = os.environ.get('ADMIN_EMAIL', 'admin@saborconflowdance.com')
        self.from_email = os.environ.get('EMAIL_HOST_USER', 'noreply@saborconflowdance.com')
        self.site_name = "Sabor Con Flow Dance"
        self.site_url = "https://www.saborconflowdance.com"
    
    def is_email_configured(self) -> bool:
        """Check if email is properly configured."""
        return bool(
            os.environ.get('EMAIL_HOST_USER') and 
            os.environ.get('EMAIL_HOST_PASSWORD')
        )
    
    def send_admin_notification(self, testimonial) -> bool:
        """
        Send email notification to admin about new testimonial submission.
        
        Args:
            testimonial: Testimonial model instance
            
        Returns:
            bool: Success status
        """
        if not self.is_email_configured():
            logger.warning("Email not configured, skipping admin notification")
            return False
        
        try:
            # Prepare email context
            context = {
                'testimonial': testimonial,
                'site_name': self.site_name,
                'site_url': self.site_url,
                'admin_url': f"{self.site_url}/admin/core/testimonial/{testimonial.id}/change/",
                'class_type_display': testimonial.get_class_type_display(),
                'submission_date': testimonial.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'has_photo': bool(testimonial.photo),
                'has_video': bool(testimonial.video_url)
            }
            
            # Render HTML and text versions
            html_content = render_to_string('emails/admin_notification.html', context)
            text_content = strip_tags(html_content)
            
            subject = f'New Testimonial Submission from {testimonial.student_name}'
            
            # Create email with both HTML and text versions
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[self.admin_email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            logger.info(f"Admin notification sent for testimonial {testimonial.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send admin notification for testimonial {testimonial.id}: {str(e)}")
            return False
    
    def send_thank_you_email(self, testimonial) -> bool:
        """
        Send thank you email to testimonial submitter.
        
        Args:
            testimonial: Testimonial model instance
            
        Returns:
            bool: Success status
        """
        if not self.is_email_configured():
            logger.warning("Email not configured, skipping thank you email")
            return False
        
        try:
            # Prepare email context
            context = {
                'student_name': testimonial.student_name,
                'testimonial': testimonial,
                'site_name': self.site_name,
                'site_url': self.site_url,
                'class_type_display': testimonial.get_class_type_display(),
                'submission_date': testimonial.created_at.strftime('%B %d, %Y'),
                'testimonials_url': f"{self.site_url}/testimonials/",
                'contact_email': self.admin_email
            }
            
            # Render HTML and text versions
            html_content = render_to_string('emails/thank_you.html', context)
            text_content = strip_tags(html_content)
            
            subject = f'Thank You for Your {self.site_name} Testimonial!'
            
            # Create email with both HTML and text versions
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[testimonial.email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            logger.info(f"Thank you email sent to {testimonial.email} for testimonial {testimonial.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send thank you email for testimonial {testimonial.id}: {str(e)}")
            return False
    
    def send_approval_notification(self, testimonial) -> bool:
        """
        Send notification email when testimonial is approved.
        
        Args:
            testimonial: Testimonial model instance
            
        Returns:
            bool: Success status
        """
        if not self.is_email_configured():
            logger.warning("Email not configured, skipping approval notification")
            return False
        
        try:
            # Prepare email context
            context = {
                'student_name': testimonial.student_name,
                'testimonial': testimonial,
                'site_name': self.site_name,
                'site_url': self.site_url,
                'class_type_display': testimonial.get_class_type_display(),
                'approval_date': datetime.now().strftime('%B %d, %Y'),
                'testimonials_url': f"{self.site_url}/testimonials/",
                'share_facebook': f"https://www.facebook.com/sharer/sharer.php?u={self.site_url}/testimonials/",
                'share_twitter': f"https://twitter.com/intent/tweet?url={self.site_url}/testimonials/&text=Check out my testimonial for {self.site_name}!",
                'contact_email': self.admin_email
            }
            
            # Render HTML and text versions
            html_content = render_to_string('emails/approval_notification.html', context)
            text_content = strip_tags(html_content)
            
            subject = f'Your {self.site_name} Testimonial Has Been Published!'
            
            # Create email with both HTML and text versions
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[testimonial.email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            logger.info(f"Approval notification sent to {testimonial.email} for testimonial {testimonial.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send approval notification for testimonial {testimonial.id}: {str(e)}")
            return False
    
    def send_weekly_summary(self, start_date: datetime, end_date: datetime) -> bool:
        """
        Send weekly summary of new testimonials to admin.
        
        Args:
            start_date: Start of the week
            end_date: End of the week
            
        Returns:
            bool: Success status
        """
        if not self.is_email_configured():
            logger.warning("Email not configured, skipping weekly summary")
            return False
        
        try:
            from core.models import Testimonial
            
            # Get testimonials from the week
            week_testimonials = Testimonial.objects.filter(
                created_at__range=[start_date, end_date]
            ).order_by('-created_at')
            
            # Get statistics
            stats = {
                'total_new': week_testimonials.count(),
                'pending': week_testimonials.filter(status='pending').count(),
                'approved': week_testimonials.filter(status='approved').count(),
                'rejected': week_testimonials.filter(status='rejected').count(),
                'with_photos': week_testimonials.filter(photo__isnull=False).count(),
                'with_videos': week_testimonials.filter(video_url__isnull=False).exclude(video_url='').count(),
            }
            
            # Get rating breakdown
            rating_breakdown = {}
            for rating in range(1, 6):
                rating_breakdown[rating] = week_testimonials.filter(rating=rating).count()
            
            # Get class type breakdown
            class_breakdown = week_testimonials.values('class_type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Prepare email context
            context = {
                'site_name': self.site_name,
                'site_url': self.site_url,
                'start_date': start_date.strftime('%B %d, %Y'),
                'end_date': end_date.strftime('%B %d, %Y'),
                'testimonials': week_testimonials,
                'stats': stats,
                'rating_breakdown': rating_breakdown,
                'class_breakdown': class_breakdown,
                'admin_url': f"{self.site_url}/admin/core/testimonial/",
                'has_new_testimonials': stats['total_new'] > 0
            }
            
            # Skip if no new testimonials
            if stats['total_new'] == 0:
                logger.info(f"No new testimonials for week {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}, skipping summary")
                return True
            
            # Render HTML and text versions
            html_content = render_to_string('emails/weekly_summary.html', context)
            text_content = strip_tags(html_content)
            
            subject = f'Weekly Testimonials Summary - {stats["total_new"]} New Submissions'
            
            # Create email with both HTML and text versions
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[self.admin_email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            logger.info(f"Weekly summary sent for week {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send weekly summary: {str(e)}")
            return False
    
    # SPEC_05 Group B Task 10 - Contact Form Email Notifications
    
    def send_contact_admin_notification(self, contact_submission) -> bool:
        """
        Send email notification to admin about new contact form submission.
        
        Args:
            contact_submission: ContactSubmission model instance
            
        Returns:
            bool: Success status
        """
        if not self.is_email_configured():
            logger.warning("Email not configured, skipping contact admin notification")
            return False
        
        try:
            # Prepare email context
            context = {
                'contact': contact_submission,
                'site_name': self.site_name,
                'site_url': self.site_url,
                'admin_url': f"{self.site_url}/admin/core/contactsubmission/{contact_submission.id}/change/",
                'interest_display': contact_submission.get_interest_display(),
                'status_display': contact_submission.get_status_display(),
                'submission_date': contact_submission.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'urgency_score': contact_submission.get_urgency_score(),
                'is_urgent': contact_submission.priority in ['high', 'urgent'] or contact_submission.interest == 'private_lesson'
            }
            
            # Render HTML and text versions
            html_content = render_to_string('emails/contact_admin_notification.html', context)
            text_content = strip_tags(html_content)
            
            # Set priority-based subject
            priority_prefix = "🔥 URGENT: " if context['is_urgent'] else ""
            subject = f'{priority_prefix}New Contact Inquiry from {contact_submission.name}'
            
            # Create email with both HTML and text versions
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[self.admin_email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            # Update tracking
            contact_submission.admin_notification_sent = True
            contact_submission.save(update_fields=['admin_notification_sent'])
            
            logger.info(f"Contact admin notification sent for submission {contact_submission.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send contact admin notification for submission {contact_submission.id}: {str(e)}")
            return False
    
    def send_contact_auto_reply(self, contact_submission) -> bool:
        """
        Send auto-reply email to contact form submitter.
        
        Args:
            contact_submission: ContactSubmission model instance
            
        Returns:
            bool: Success status
        """
        if not self.is_email_configured():
            logger.warning("Email not configured, skipping contact auto-reply")
            return False
        
        try:
            # Prepare email context
            context = {
                'contact_name': contact_submission.name,
                'contact': contact_submission,
                'site_name': self.site_name,
                'site_url': self.site_url,
                'interest_display': contact_submission.get_interest_display(),
                'submission_date': contact_submission.created_at.strftime('%B %d, %Y'),
                'contact_email': self.admin_email,
                'whatsapp_url': 'https://chat.whatsapp.com/GaZONDA1HgFG7C8djihJ1x',
                'instagram_url': 'https://www.instagram.com/saborconflow.dance/',
                'facebook_url': 'https://www.facebook.com/profile.php?id=61575502290591',
                'expected_response_time': '24 hours' if contact_submission.priority in ['high', 'urgent'] else '48 hours'
            }
            
            # Render HTML and text versions
            html_content = render_to_string('emails/contact_auto_reply.html', context)
            text_content = strip_tags(html_content)
            
            subject = f'Thank You for Contacting {self.site_name}!'
            
            # Create email with both HTML and text versions
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[contact_submission.email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            # Update tracking
            contact_submission.auto_reply_sent = True
            contact_submission.save(update_fields=['auto_reply_sent'])
            
            logger.info(f"Contact auto-reply sent to {contact_submission.email} for submission {contact_submission.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send contact auto-reply for submission {contact_submission.id}: {str(e)}")
            return False
    
    # SPEC_05 Group B Task 10 - Booking Confirmation Email Notifications
    
    def send_booking_confirmation(self, booking) -> bool:
        """
        Send booking confirmation email to customer.
        
        Args:
            booking: BookingConfirmation model instance
            
        Returns:
            bool: Success status
        """
        if not self.is_email_configured():
            logger.warning("Email not configured, skipping booking confirmation")
            return False
        
        try:
            # Prepare email context
            context = {
                'booking': booking,
                'customer_name': booking.customer_name,
                'site_name': self.site_name,
                'site_url': self.site_url,
                'booking_type_display': booking.get_booking_type_display(),
                'status_display': booking.get_status_display(),
                'booking_datetime': booking.get_booking_datetime_formatted(),
                'booking_date': booking.get_booking_date_only(),
                'booking_time': booking.get_booking_time_only(),
                'time_until_booking': booking.get_time_until_booking(),
                'contact_email': self.admin_email,
                'whatsapp_url': 'https://chat.whatsapp.com/GaZONDA1HgFG7C8djihJ1x',
                'maps_url': f"https://www.google.com/maps/search/?api=1&query={booking.location.replace(' ', '+')}"
            }
            
            # Render HTML and text versions
            html_content = render_to_string('emails/booking_confirmation.html', context)
            text_content = strip_tags(html_content)
            
            subject = f'Booking Confirmed: {booking.class_name} - {booking.booking_id}'
            
            # Create email with both HTML and text versions
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[booking.customer_email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            # Update tracking
            booking.confirmation_email_sent = True
            booking.save(update_fields=['confirmation_email_sent'])
            
            logger.info(f"Booking confirmation sent to {booking.customer_email} for booking {booking.booking_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send booking confirmation for booking {booking.booking_id}: {str(e)}")
            return False
    
    def send_booking_admin_notification(self, booking) -> bool:
        """
        Send email notification to admin about new booking.
        
        Args:
            booking: BookingConfirmation model instance
            
        Returns:
            bool: Success status
        """
        if not self.is_email_configured():
            logger.warning("Email not configured, skipping booking admin notification")
            return False
        
        try:
            # Prepare email context
            context = {
                'booking': booking,
                'site_name': self.site_name,
                'site_url': self.site_url,
                'admin_url': f"{self.site_url}/admin/core/bookingconfirmation/{booking.id}/change/",
                'booking_type_display': booking.get_booking_type_display(),
                'status_display': booking.get_status_display(),
                'booking_datetime': booking.get_booking_datetime_formatted(),
                'time_until_booking': booking.get_time_until_booking(),
                'created_date': booking.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'is_urgent': booking.booking_date <= (timezone.now() + timedelta(hours=24))
            }
            
            # Render HTML and text versions
            html_content = render_to_string('emails/booking_admin_notification.html', context)
            text_content = strip_tags(html_content)
            
            # Set urgency-based subject
            urgency_prefix = "⚡ URGENT: " if context['is_urgent'] else ""
            subject = f'{urgency_prefix}New Booking: {booking.booking_id} - {booking.customer_name}'
            
            # Create email with both HTML and text versions
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[self.admin_email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            logger.info(f"Booking admin notification sent for booking {booking.booking_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send booking admin notification for booking {booking.booking_id}: {str(e)}")
            return False
    
    def send_booking_reminder(self, booking, hours_before=24) -> bool:
        """
        Send booking reminder email to customer.
        
        Args:
            booking: BookingConfirmation model instance
            hours_before: Hours before booking to send reminder
            
        Returns:
            bool: Success status
        """
        if not self.is_email_configured():
            logger.warning("Email not configured, skipping booking reminder")
            return False
        
        try:
            # Prepare email context
            context = {
                'booking': booking,
                'customer_name': booking.customer_name,
                'site_name': self.site_name,
                'site_url': self.site_url,
                'booking_datetime': booking.get_booking_datetime_formatted(),
                'booking_date': booking.get_booking_date_only(),
                'booking_time': booking.get_booking_time_only(),
                'time_until_booking': booking.get_time_until_booking(),
                'contact_email': self.admin_email,
                'whatsapp_url': 'https://chat.whatsapp.com/GaZONDA1HgFG7C8djihJ1x',
                'maps_url': f"https://www.google.com/maps/search/?api=1&query={booking.location.replace(' ', '+')}"
            }
            
            # Render HTML and text versions
            html_content = render_to_string('emails/booking_reminder.html', context)
            text_content = strip_tags(html_content)
            
            subject = f'Reminder: {booking.class_name} Tomorrow - {booking.booking_id}'
            
            # Create email with both HTML and text versions
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[booking.customer_email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            # Update tracking
            booking.reminder_email_sent = True
            booking.save(update_fields=['reminder_email_sent'])
            
            logger.info(f"Booking reminder sent to {booking.customer_email} for booking {booking.booking_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send booking reminder for booking {booking.booking_id}: {str(e)}")
            return False


# Convenience functions for use in views and management commands

# Testimonial Email Functions
def send_admin_notification_email(testimonial) -> bool:
    """Send admin notification for new testimonial."""
    service = EmailNotificationService()
    return service.send_admin_notification(testimonial)


def send_thank_you_email(testimonial) -> bool:
    """Send thank you email to testimonial submitter."""
    service = EmailNotificationService()
    return service.send_thank_you_email(testimonial)


def send_approval_notification_email(testimonial) -> bool:
    """Send approval notification to testimonial submitter."""
    service = EmailNotificationService()
    return service.send_approval_notification(testimonial)


def send_weekly_summary_email() -> bool:
    """Send weekly summary for the past week."""
    service = EmailNotificationService()
    
    # Calculate last week's date range
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday() + 7)  # Last Monday
    end_of_week = start_of_week + timedelta(days=6)  # Last Sunday
    
    return service.send_weekly_summary(start_of_week, end_of_week)


def send_custom_weekly_summary(start_date: str, end_date: str) -> bool:
    """
    Send weekly summary for custom date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        bool: Success status
    """
    service = EmailNotificationService()
    
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        return service.send_weekly_summary(start_dt, end_dt)
    except ValueError as e:
        logger.error(f"Invalid date format: {str(e)}")
        return False


# SPEC_05 Group B Task 10 - Contact Form Email Functions
def send_contact_admin_notification_email(contact_submission) -> bool:
    """Send admin notification for new contact form submission."""
    service = EmailNotificationService()
    return service.send_contact_admin_notification(contact_submission)


def send_contact_auto_reply_email(contact_submission) -> bool:
    """Send auto-reply email to contact form submitter."""
    service = EmailNotificationService()
    return service.send_contact_auto_reply(contact_submission)


# SPEC_05 Group B Task 10 - Booking Email Functions
def send_booking_confirmation_email(booking) -> bool:
    """Send booking confirmation email to customer."""
    service = EmailNotificationService()
    return service.send_booking_confirmation(booking)


def send_booking_admin_notification_email(booking) -> bool:
    """Send admin notification for new booking."""
    service = EmailNotificationService()
    return service.send_booking_admin_notification(booking)


def send_booking_reminder_email(booking, hours_before=24) -> bool:
    """Send booking reminder email to customer."""
    service = EmailNotificationService()
    return service.send_booking_reminder(booking, hours_before)


# Bulk Operations and Testing Functions
def test_email_configuration() -> dict:
    """
    Test email configuration and connectivity.
    
    Returns:
        dict: Test results with status and details
    """
    service = EmailNotificationService()
    result = {
        'configured': service.is_email_configured(),
        'admin_email': service.admin_email,
        'from_email': service.from_email,
        'errors': []
    }
    
    if not result['configured']:
        result['errors'].append('Email credentials not configured')
        return result
    
    # Test email sending
    try:
        from django.core.mail import send_mail
        send_mail(
            subject='Email Configuration Test - Sabor Con Flow',
            message='This is a test email to verify email configuration.',
            from_email=service.from_email,
            recipient_list=[service.admin_email],
            fail_silently=False,
        )
        result['test_email_sent'] = True
        logger.info("Email configuration test successful")
    except Exception as e:
        result['test_email_sent'] = False
        result['errors'].append(f"Failed to send test email: {str(e)}")
        logger.error(f"Email configuration test failed: {str(e)}")
    
    return result


def send_digest_email(days_back=7) -> bool:
    """
    Send comprehensive digest email with all recent activity.
    
    Args:
        days_back: Number of days to include in digest
        
    Returns:
        bool: Success status
    """
    service = EmailNotificationService()
    
    if not service.is_email_configured():
        logger.warning("Email not configured, skipping digest email")
        return False
    
    try:
        from core.models import Testimonial, ContactSubmission, BookingConfirmation
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Gather data
        context = {
            'site_name': service.site_name,
            'site_url': service.site_url,
            'start_date': start_date.strftime('%B %d, %Y'),
            'end_date': end_date.strftime('%B %d, %Y'),
            'days_back': days_back
        }
        
        # Testimonials
        testimonials = Testimonial.objects.filter(
            created_at__range=[start_date, end_date]
        ).order_by('-created_at')
        context['testimonials'] = {
            'total': testimonials.count(),
            'pending': testimonials.filter(status='pending').count(),
            'approved': testimonials.filter(status='approved').count(),
            'list': list(testimonials[:5])  # Latest 5
        }
        
        # Contact submissions
        contacts = ContactSubmission.objects.filter(
            created_at__range=[start_date, end_date]
        ).order_by('-created_at')
        context['contacts'] = {
            'total': contacts.count(),
            'new': contacts.filter(status='new').count(),
            'in_progress': contacts.filter(status='in_progress').count(),
            'list': list(contacts[:5])  # Latest 5
        }
        
        # Bookings
        bookings = BookingConfirmation.objects.filter(
            created_at__range=[start_date, end_date]
        ).order_by('-created_at')
        context['bookings'] = {
            'total': bookings.count(),
            'confirmed': bookings.filter(status='confirmed').count(),
            'pending': bookings.filter(status='pending').count(),
            'list': list(bookings[:5])  # Latest 5
        }
        
        # Skip if no activity
        total_activity = (context['testimonials']['total'] + 
                         context['contacts']['total'] + 
                         context['bookings']['total'])
        
        if total_activity == 0:
            logger.info(f"No activity in the last {days_back} days, skipping digest")
            return True
        
        # Render and send email
        html_content = render_to_string('emails/activity_digest.html', context)
        text_content = strip_tags(html_content)
        
        subject = f'Activity Digest - {total_activity} Items ({days_back} days)'
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=service.from_email,
            to=[service.admin_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Activity digest sent for {days_back} days with {total_activity} items")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send activity digest: {str(e)}")
        return False