"""
Management command to sync Facebook events with local database.
SPEC_05 Group B Task 5-6 - Facebook Events synchronization.

Usage:
    python manage.py sync_facebook_events
    python manage.py sync_facebook_events --force-refresh
    python manage.py sync_facebook_events --limit 10
"""

import logging
from datetime import datetime, timezone
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone as django_timezone
from core.models import FacebookEvent
from core.utils.facebook_events import FacebookEventsAPI, get_facebook_api_status

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync Facebook events with local database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force-refresh',
            action='store_true',
            help='Force refresh events even if recently synced',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Maximum number of events to fetch (default: 20)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without making changes',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Remove past events from database',
        )
    
    def handle(self, *args, **options):
        """Main command handler."""
        self.verbosity = options['verbosity']
        self.force_refresh = options['force_refresh']
        self.limit = options['limit']
        self.dry_run = options['dry_run']
        self.cleanup = options['cleanup']
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        try:
            # Check API status first
            self.check_api_status()
            
            # Cleanup old events if requested
            if self.cleanup:
                self.cleanup_past_events()
            
            # Sync events
            self.sync_events()
            
        except Exception as e:
            logger.error(f"Facebook events sync failed: {str(e)}")
            raise CommandError(f"Sync failed: {str(e)}")
    
    def check_api_status(self):
        """Check Facebook API connectivity."""
        self.stdout.write("Checking Facebook API status...")
        
        status = get_facebook_api_status()
        
        if not status['configured']:
            raise CommandError(f"Facebook API not configured: {status['config_message']}")
        
        if not status['api_accessible']:
            raise CommandError("Cannot access Facebook API")
        
        if not status['page_accessible']:
            raise CommandError("Cannot access Facebook page")
        
        if self.verbosity >= 2:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Connected to Facebook page: {status.get('page_name', 'Unknown')}")
            )
    
    def sync_events(self):
        """Sync events from Facebook API to database."""
        self.stdout.write("Fetching events from Facebook API...")
        
        # Initialize API client
        api = FacebookEventsAPI()
        
        # Fetch events (bypass cache if force refresh)
        use_cache = not self.force_refresh
        events_data = api.get_upcoming_events(limit=self.limit, use_cache=use_cache)
        
        if not events_data:
            self.stdout.write(
                self.style.WARNING("No events retrieved from Facebook API")
            )
            return
        
        self.stdout.write(f"Retrieved {len(events_data)} events from Facebook")
        
        # Process each event
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for event_data in events_data:
            try:
                result = self.process_event(event_data)
                if result == 'created':
                    created_count += 1
                elif result == 'updated':
                    updated_count += 1
                else:
                    skipped_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to process event {event_data.get('id', 'unknown')}: {str(e)}")
                skipped_count += 1
        
        # Report results
        self.stdout.write(
            self.style.SUCCESS(
                f"Sync completed: {created_count} created, {updated_count} updated, {skipped_count} skipped"
            )
        )
    
    def process_event(self, event_data):
        """Process a single event from API data."""
        facebook_id = event_data.get('id')
        if not facebook_id:
            if self.verbosity >= 2:
                self.stdout.write(f"Skipping event without ID: {event_data}")
            return 'skipped'
        
        # Parse start time
        start_time = None
        start_time_str = event_data.get('start_time')
        if start_time_str:
            try:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid start_time for event {facebook_id}: {start_time_str}")
                return 'skipped'
        
        if not start_time:
            if self.verbosity >= 2:
                self.stdout.write(f"Skipping event without valid start_time: {facebook_id}")
            return 'skipped'
        
        # Check if event exists
        try:
            existing_event = FacebookEvent.objects.get(facebook_id=facebook_id)
            action = 'update'
        except FacebookEvent.DoesNotExist:
            existing_event = None
            action = 'create'
        
        if self.dry_run:
            self.stdout.write(f"Would {action} event: {event_data.get('name', 'Untitled')}")
            return action + 'd'
        
        # Prepare event data
        event_defaults = {
            'name': event_data.get('name', 'Untitled Event'),
            'description': event_data.get('description', ''),
            'start_time': start_time,
            'formatted_date': event_data.get('formatted_date', ''),
            'formatted_time': event_data.get('formatted_time', ''),
            'cover_photo_url': event_data.get('cover_photo'),
            'facebook_url': event_data.get('facebook_url', f"https://www.facebook.com/events/{facebook_id}"),
            'is_active': True,
            'last_synced': django_timezone.now()
        }
        
        if existing_event:
            # Update existing event
            for field, value in event_defaults.items():
                setattr(existing_event, field, value)
            existing_event.save()
            
            if self.verbosity >= 2:
                self.stdout.write(f"Updated event: {existing_event.name}")
            return 'updated'
        else:
            # Create new event
            event_defaults['facebook_id'] = facebook_id
            new_event = FacebookEvent.objects.create(**event_defaults)
            
            if self.verbosity >= 2:
                self.stdout.write(f"Created event: {new_event.name}")
            return 'created'
    
    def cleanup_past_events(self):
        """Remove past events from database."""
        self.stdout.write("Cleaning up past events...")
        
        past_events = FacebookEvent.objects.filter(
            start_time__lt=django_timezone.now()
        )
        
        count = past_events.count()
        
        if count == 0:
            self.stdout.write("No past events to clean up")
            return
        
        if self.dry_run:
            self.stdout.write(f"Would delete {count} past events")
            return
        
        past_events.delete()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {count} past events")
        )