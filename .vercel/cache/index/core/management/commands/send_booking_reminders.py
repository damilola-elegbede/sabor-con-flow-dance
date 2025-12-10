"""
Django management command to send booking reminder emails.
SPEC_05 Group B Task 10 - Comprehensive email notifications system.

Usage:
    python manage.py send_booking_reminders [--hours=24] [--dry-run]
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import BookingConfirmation
from core.utils.email_notifications import send_booking_reminder_email
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send booking reminder emails to customers with upcoming bookings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Send reminders for bookings within this many hours (default: 24)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Send reminders even if they were already sent'
        )

    def handle(self, *args, **options):
        hours_ahead = options['hours']
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting booking reminder command - Hours ahead: {hours_ahead}')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🧪 DRY RUN MODE - No emails will be sent')
            )
        
        # Calculate time window
        now = timezone.now()
        reminder_window_start = now
        reminder_window_end = now + timedelta(hours=hours_ahead)
        
        # Find upcoming bookings that need reminders
        query_filters = {
            'booking_date__gte': reminder_window_start,
            'booking_date__lte': reminder_window_end,
            'status': 'confirmed'
        }
        
        if not force:
            query_filters['reminder_email_sent'] = False
        
        upcoming_bookings = BookingConfirmation.objects.filter(
            **query_filters
        ).order_by('booking_date')
        
        self.stdout.write(
            f'Found {upcoming_bookings.count()} bookings requiring reminders'
        )
        
        if upcoming_bookings.count() == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ No bookings require reminders at this time')
            )
            return
        
        # Process each booking
        sent_count = 0
        error_count = 0
        
        for booking in upcoming_bookings:
            time_until = booking.booking_date - now
            hours_until = time_until.total_seconds() / 3600
            
            self.stdout.write(
                f'Processing booking {booking.booking_id} - {booking.customer_name} '
                f'({hours_until:.1f} hours away)'
            )
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'  🧪 Would send reminder to {booking.customer_email} '
                        f'for {booking.class_name} on {booking.get_booking_datetime_formatted()}'
                    )
                )
                sent_count += 1
                continue
            
            try:
                success = send_booking_reminder_email(booking, hours_before=hours_ahead)
                
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✅ Reminder sent to {booking.customer_email}'
                        )
                    )
                    sent_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ❌ Failed to send reminder to {booking.customer_email}'
                        )
                    )
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'  ❌ Error sending reminder to {booking.customer_email}: {str(e)}'
                    )
                )
                error_count += 1
                logger.error(f"Booking reminder error for {booking.booking_id}: {str(e)}")
        
        # Summary
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'📊 Reminder Summary:')
        )
        self.stdout.write(f'  Total bookings processed: {upcoming_bookings.count()}')
        self.stdout.write(f'  Reminders sent: {sent_count}')
        
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f'  Errors: {error_count}')
            )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🧪 This was a dry run - no actual emails were sent')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Booking reminder command completed successfully')
            )
        
        # Show upcoming bookings that don't need reminders yet
        if not dry_run:
            future_bookings = BookingConfirmation.objects.filter(
                booking_date__gt=reminder_window_end,
                status='confirmed'
            ).order_by('booking_date')[:5]
            
            if future_bookings.exists():
                self.stdout.write('')
                self.stdout.write('📅 Next upcoming bookings:')
                for booking in future_bookings:
                    time_until = booking.booking_date - now
                    days_until = time_until.days
                    hours_until = time_until.total_seconds() / 3600
                    
                    if days_until > 0:
                        time_str = f'{days_until} days'
                    else:
                        time_str = f'{hours_until:.1f} hours'
                    
                    self.stdout.write(
                        f'  {booking.booking_id} - {booking.customer_name} '
                        f'({time_str} away) - {booking.class_name}'
                    )