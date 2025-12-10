"""
Django management command to send email digests and activity summaries.
SPEC_05 Group B Task 10 - Comprehensive email notifications system.

Usage:
    python manage.py send_email_digest [--days=7] [--type=activity] [--test]
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from core.utils.email_notifications import send_digest_email, test_email_configuration
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send email digests and activity summaries to administrators'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to include in the digest (default: 7)'
        )
        
        parser.add_argument(
            '--type',
            type=str,
            choices=['activity', 'weekly', 'test'],
            default='activity',
            help='Type of digest to send: activity, weekly, or test'
        )
        
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test email configuration without sending digest'
        )

    def handle(self, *args, **options):
        days = options['days']
        digest_type = options['type']
        test_mode = options['test']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting email digest command - Type: {digest_type}, Days: {days}')
        )
        
        # Test email configuration if requested
        if test_mode or digest_type == 'test':
            self.stdout.write('Testing email configuration...')
            test_results = test_email_configuration()
            
            if test_results['configured']:
                self.stdout.write(
                    self.style.SUCCESS('✅ Email is properly configured')
                )
                self.stdout.write(f"Admin Email: {test_results['admin_email']}")
                self.stdout.write(f"From Email: {test_results['from_email']}")
                
                if test_results.get('test_email_sent'):
                    self.stdout.write(
                        self.style.SUCCESS('✅ Test email sent successfully')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ Failed to send test email')
                    )
                    for error in test_results.get('errors', []):
                        self.stdout.write(
                            self.style.ERROR(f'   Error: {error}')
                        )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Email is not properly configured')
                )
                for error in test_results.get('errors', []):
                    self.stdout.write(
                        self.style.ERROR(f'   Error: {error}')
                    )
                return
            
            if test_mode:
                return
        
        # Send digest based on type
        if digest_type == 'activity':
            self.send_activity_digest(days)
        elif digest_type == 'weekly':
            self.send_weekly_digest()
        
        self.stdout.write(
            self.style.SUCCESS('Email digest command completed successfully')
        )

    def send_activity_digest(self, days):
        """Send activity digest for specified number of days."""
        self.stdout.write(f'Sending {days}-day activity digest...')
        
        try:
            success = send_digest_email(days_back=days)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Activity digest sent successfully ({days} days)')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Failed to send activity digest')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error sending activity digest: {str(e)}')
            )
            logger.error(f"Activity digest error: {str(e)}")

    def send_weekly_digest(self):
        """Send weekly testimonial digest (legacy function)."""
        from core.utils.email_notifications import send_weekly_summary_email
        
        self.stdout.write('Sending weekly testimonial summary...')
        
        try:
            success = send_weekly_summary_email()
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS('✅ Weekly testimonial summary sent successfully')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  No new testimonials for weekly summary')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error sending weekly summary: {str(e)}')
            )
            logger.error(f"Weekly summary error: {str(e)}")