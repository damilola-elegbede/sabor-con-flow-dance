"""
Management command for testing email functionality.
SPEC_05 Group B Task 10 - Comprehensive email notifications system.

Usage:
    python manage.py test_emails
    python manage.py test_emails --type contact
    python manage.py test_emails --type booking
    python manage.py test_emails --type testimonial
    python manage.py test_emails --send-test-emails
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings
from core.utils.email_notifications import (
    EmailNotificationService,
    test_email_configuration,
    send_digest_email
)
from core.models import ContactSubmission, BookingConfirmation, Testimonial
from datetime import datetime, timedelta
import os


class Command(BaseCommand):
    help = 'Test email configuration and send test emails'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=['contact', 'booking', 'testimonial', 'digest', 'all'],
            default='all',
            help='Type of email test to run'
        )
        
        parser.add_argument(
            '--send-test-emails',
            action='store_true',
            help='Actually send test emails (default: dry run)'
        )
        
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test emails to (defaults to admin email)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🧪 Email System Test - Sabor Con Flow Dance')
        )
        self.stdout.write('=' * 60)
        
        # Test basic email configuration
        self.test_configuration()
        
        # Test specific email types
        email_type = options['type']
        send_emails = options['send_test_emails']
        test_email = options['email']
        verbose = options['verbose']
        
        if email_type == 'all':
            self.test_contact_emails(send_emails, test_email, verbose)
            self.test_booking_emails(send_emails, test_email, verbose)
            self.test_testimonial_emails(send_emails, test_email, verbose)
            self.test_digest_emails(send_emails, test_email, verbose)
        elif email_type == 'contact':
            self.test_contact_emails(send_emails, test_email, verbose)
        elif email_type == 'booking':
            self.test_booking_emails(send_emails, test_email, verbose)
        elif email_type == 'testimonial':
            self.test_testimonial_emails(send_emails, test_email, verbose)
        elif email_type == 'digest':
            self.test_digest_emails(send_emails, test_email, verbose)
        
        self.stdout.write('=' * 60)
        self.stdout.write(
            self.style.SUCCESS('✅ Email testing complete!')
        )
    
    def test_configuration(self):
        """Test basic email configuration."""
        self.stdout.write('\n📧 Testing Email Configuration...')
        
        config_test = test_email_configuration()
        
        if config_test['configured']:
            self.stdout.write(
                self.style.SUCCESS('✅ Email is properly configured')
            )
            self.stdout.write(f'   From: {config_test["from_email"]}')
            self.stdout.write(f'   Admin: {config_test["admin_email"]}')
            
            if config_test.get('test_email_sent'):
                self.stdout.write(
                    self.style.SUCCESS('✅ Test email sent successfully')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Test email failed')
                )
                if config_test.get('errors'):
                    for error in config_test['errors']:
                        self.stdout.write(f'   Error: {error}')
        else:
            self.stdout.write(
                self.style.ERROR('❌ Email is not configured')
            )
            if config_test.get('errors'):
                for error in config_test['errors']:
                    self.stdout.write(f'   Error: {error}')
    
    def test_contact_emails(self, send_emails, test_email, verbose):
        """Test contact form email notifications."""
        self.stdout.write('\n📬 Testing Contact Form Emails...')
        
        service = EmailNotificationService()
        
        # Create test contact submission
        test_contact = ContactSubmission(
            name='Test User',
            email=test_email or service.admin_email,
            phone='(555) 123-4567',
            interest='private_lesson',
            message='This is a test contact form submission for email testing purposes.',
            status='new',
            priority='high'
        )
        
        if send_emails:
            # Save and send actual emails
            test_contact.save()
            
            try:
                # Test admin notification
                admin_success = service.send_contact_admin_notification(test_contact)
                if admin_success:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Contact admin notification sent')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ Contact admin notification failed')
                    )
                
                # Test auto-reply
                auto_reply_success = service.send_contact_auto_reply(test_contact)
                if auto_reply_success:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Contact auto-reply sent')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ Contact auto-reply failed')
                    )
                
                # Clean up test data
                test_contact.delete()
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Contact email test failed: {str(e)}')
                )
        else:
            self.stdout.write(
                self.style.WARNING('🔍 Dry run - Contact emails would be sent to:')
            )
            self.stdout.write(f'   Admin notification: {service.admin_email}')
            self.stdout.write(f'   Auto-reply: {test_contact.email}')
            
            if verbose:
                self.stdout.write('   Email content preview:')
                self.stdout.write(f'     - Name: {test_contact.name}')
                self.stdout.write(f'     - Interest: {test_contact.get_interest_display()}')
                self.stdout.write(f'     - Priority: {test_contact.priority}')
                self.stdout.write(f'     - Message: {test_contact.message[:50]}...')
    
    def test_booking_emails(self, send_emails, test_email, verbose):
        """Test booking confirmation email notifications."""
        self.stdout.write('\n📅 Testing Booking Emails...')
        
        service = EmailNotificationService()
        
        # Create test booking
        test_booking = BookingConfirmation(
            booking_id='TEST20241201001',
            booking_type='private_lesson',
            customer_name='Test Customer',
            customer_email=test_email or service.admin_email,
            customer_phone='(555) 123-4567',
            class_name='Private Salsa Lesson',
            instructor_name='Maria Rodriguez',
            booking_date=datetime.now() + timedelta(days=7),
            duration_minutes=60,
            price=80.00,
            payment_method='Venmo',
            status='confirmed'
        )
        
        if send_emails:
            # Save and send actual emails
            test_booking.save()
            
            try:
                # Test customer confirmation
                confirmation_success = service.send_booking_confirmation(test_booking)
                if confirmation_success:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Booking confirmation sent to customer')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ Booking confirmation failed')
                    )
                
                # Test admin notification
                admin_success = service.send_booking_admin_notification(test_booking)
                if admin_success:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Booking admin notification sent')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ Booking admin notification failed')
                    )
                
                # Test reminder (if booking is within 25 hours)
                reminder_success = service.send_booking_reminder(test_booking)
                if reminder_success:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Booking reminder sent')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠️ Booking reminder not sent (booking too far out)')
                    )
                
                # Clean up test data
                test_booking.delete()
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Booking email test failed: {str(e)}')
                )
        else:
            self.stdout.write(
                self.style.WARNING('🔍 Dry run - Booking emails would be sent to:')
            )
            self.stdout.write(f'   Customer confirmation: {test_booking.customer_email}')
            self.stdout.write(f'   Admin notification: {service.admin_email}')
            
            if verbose:
                self.stdout.write('   Booking details:')
                self.stdout.write(f'     - ID: {test_booking.booking_id}')
                self.stdout.write(f'     - Type: {test_booking.get_booking_type_display()}')
                self.stdout.write(f'     - Class: {test_booking.class_name}')
                self.stdout.write(f'     - Date: {test_booking.booking_date}')
                self.stdout.write(f'     - Price: ${test_booking.price}')
    
    def test_testimonial_emails(self, send_emails, test_email, verbose):
        """Test testimonial email notifications."""
        self.stdout.write('\n⭐ Testing Testimonial Emails...')
        
        service = EmailNotificationService()
        
        # Create test testimonial
        test_testimonial = Testimonial(
            student_name='Test Student',
            email=test_email or service.admin_email,
            rating=5,
            content='This is a test testimonial for email testing purposes. The classes are amazing and the instructors are fantastic!',
            class_type='pasos_basicos',
            status='pending'
        )
        
        if send_emails:
            # Save and send actual emails
            test_testimonial.save()
            
            try:
                # Test admin notification
                admin_success = service.send_admin_notification(test_testimonial)
                if admin_success:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Testimonial admin notification sent')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ Testimonial admin notification failed')
                    )
                
                # Test thank you email
                thank_you_success = service.send_thank_you_email(test_testimonial)
                if thank_you_success:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Testimonial thank you email sent')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ Testimonial thank you email failed')
                    )
                
                # Test approval notification (simulate approval)
                test_testimonial.status = 'approved'
                test_testimonial.published_at = datetime.now()
                test_testimonial.save()
                
                approval_success = service.send_approval_notification(test_testimonial)
                if approval_success:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Testimonial approval notification sent')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ Testimonial approval notification failed')
                    )
                
                # Clean up test data
                test_testimonial.delete()
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Testimonial email test failed: {str(e)}')
                )
        else:
            self.stdout.write(
                self.style.WARNING('🔍 Dry run - Testimonial emails would be sent to:')
            )
            self.stdout.write(f'   Admin notification: {service.admin_email}')
            self.stdout.write(f'   Thank you: {test_testimonial.email}')
            self.stdout.write(f'   Approval: {test_testimonial.email}')
            
            if verbose:
                self.stdout.write('   Testimonial details:')
                self.stdout.write(f'     - Student: {test_testimonial.student_name}')
                self.stdout.write(f'     - Rating: {test_testimonial.rating} stars')
                self.stdout.write(f'     - Class: {test_testimonial.get_class_type_display()}')
                self.stdout.write(f'     - Content: {test_testimonial.content[:50]}...')
    
    def test_digest_emails(self, send_emails, test_email, verbose):
        """Test digest and summary emails."""
        self.stdout.write('\n📊 Testing Digest Emails...')
        
        service = EmailNotificationService()
        
        if send_emails:
            try:
                # Test weekly summary
                start_date = datetime.now() - timedelta(days=7)
                end_date = datetime.now()
                
                summary_success = service.send_weekly_summary(start_date, end_date)
                if summary_success:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Weekly summary sent')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠️ Weekly summary not sent (no data)')
                    )
                
                # Test activity digest
                digest_success = send_digest_email(days_back=7)
                if digest_success:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Activity digest sent')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠️ Activity digest not sent (no activity)')
                    )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Digest email test failed: {str(e)}')
                )
        else:
            self.stdout.write(
                self.style.WARNING('🔍 Dry run - Digest emails would be sent to:')
            )
            self.stdout.write(f'   Weekly summary: {service.admin_email}')
            self.stdout.write(f'   Activity digest: {service.admin_email}')
            
            if verbose:
                # Show counts for digest content
                contact_count = ContactSubmission.objects.filter(
                    created_at__gte=datetime.now() - timedelta(days=7)
                ).count()
                
                booking_count = BookingConfirmation.objects.filter(
                    created_at__gte=datetime.now() - timedelta(days=7)
                ).count()
                
                testimonial_count = Testimonial.objects.filter(
                    created_at__gte=datetime.now() - timedelta(days=7)
                ).count()
                
                self.stdout.write('   Activity in last 7 days:')
                self.stdout.write(f'     - Contact submissions: {contact_count}')
                self.stdout.write(f'     - Bookings: {booking_count}')
                self.stdout.write(f'     - Testimonials: {testimonial_count}')
    
    def style_output(self, message, style_type='info'):
        """Helper to style output messages."""
        if style_type == 'success':
            return self.style.SUCCESS(message)
        elif style_type == 'error':
            return self.style.ERROR(message)
        elif style_type == 'warning':
            return self.style.WARNING(message)
        else:
            return message