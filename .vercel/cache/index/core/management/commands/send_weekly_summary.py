"""
Django management command to send weekly testimonial summary emails.

This command can be run manually or scheduled via cron/task scheduler to send
weekly summary emails to administrators about new testimonial submissions.

Usage:
    python manage.py send_weekly_summary
    python manage.py send_weekly_summary --start-date 2024-01-01 --end-date 2024-01-07
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
import sys

from core.utils.email_notifications import send_weekly_summary_email, send_custom_weekly_summary


class Command(BaseCommand):
    help = 'Send weekly testimonials summary email to administrators'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date for summary in YYYY-MM-DD format (default: last Monday)'
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='End date for summary in YYYY-MM-DD format (default: last Sunday)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending email'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Send email even if no new testimonials in the period'
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        
        try:
            start_date = options.get('start_date')
            end_date = options.get('end_date')
            dry_run = options.get('dry_run', False)
            force = options.get('force', False)
            
            # Validate date inputs
            if start_date and end_date:
                try:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    
                    if start_dt > end_dt:
                        raise CommandError("Start date must be before end date")
                        
                except ValueError:
                    raise CommandError("Invalid date format. Use YYYY-MM-DD")
                    
                date_range_msg = f"Custom date range: {start_date} to {end_date}"
                
            elif start_date or end_date:
                raise CommandError("Both --start-date and --end-date must be provided together")
                
            else:
                # Default to last week (Monday to Sunday)
                today = timezone.now().date()
                start_dt = today - timedelta(days=today.weekday() + 7)  # Last Monday
                end_dt = start_dt + timedelta(days=6)  # Last Sunday
                start_date = start_dt.strftime('%Y-%m-%d')
                end_date = end_dt.strftime('%Y-%m-%d')
                date_range_msg = f"Default last week: {start_date} to {end_date}"
            
            self.stdout.write(f"Preparing weekly summary for {date_range_msg}")
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING("DRY RUN MODE: No email will be sent")
                )
                
                # Import here to check testimonials
                from core.models import Testimonial
                
                testimonials = Testimonial.objects.filter(
                    created_at__date__range=[start_date, end_date]
                )
                
                count = testimonials.count()
                self.stdout.write(f"Found {count} testimonials in date range")
                
                if count > 0:
                    self.stdout.write("Testimonials found:")
                    for t in testimonials:
                        status_color = self.style.SUCCESS if t.status == 'approved' else (
                            self.style.WARNING if t.status == 'pending' else self.style.ERROR
                        )
                        self.stdout.write(
                            f"  - {t.student_name} ({status_color(t.status)}) - "
                            f"{t.rating} stars - {t.created_at.strftime('%Y-%m-%d %H:%M')}"
                        )
                else:
                    self.stdout.write("No testimonials found in date range")
                    
                self.stdout.write("Email would be sent to configured admin email address")
                return
            
            # Send the actual email
            if start_date and end_date:
                success = send_custom_weekly_summary(start_date, end_date)
            else:
                success = send_weekly_summary_email()
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Weekly summary email sent successfully for {date_range_msg}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to send weekly summary email for {date_range_msg}"
                    )
                )
                sys.exit(1)
                
        except Exception as e:
            raise CommandError(f"Error sending weekly summary: {str(e)}")
    
    def format_testimonial_summary(self, testimonials):
        """Format testimonials for display in dry run mode."""
        if not testimonials:
            return "No testimonials found in the specified date range."
        
        lines = []
        for testimonial in testimonials:
            lines.append(
                f"- {testimonial.student_name} ({testimonial.status}) "
                f"- {testimonial.rating} stars - {testimonial.created_at.strftime('%Y-%m-%d')}"
            )
        
        return "\n".join(lines)