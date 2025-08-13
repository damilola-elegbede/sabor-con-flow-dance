"""
Django management command to sync Instagram posts with the MediaGallery model.

Usage:
    python manage.py sync_instagram [options]

Options:
    --limit: Number of posts to fetch (default: 12)
    --force: Force refresh, ignore cache
    --dry-run: Show what would be done without making changes
    --delete-removed: Delete posts no longer on Instagram
"""

import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from core.models import MediaGallery
from core.utils.instagram_api import InstagramAPI, InstagramAPIError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync Instagram posts with MediaGallery model'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=12,
            help='Number of Instagram posts to fetch (default: 12)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force refresh, ignore cache',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--delete-removed',
            action='store_true',
            help='Delete posts that are no longer on Instagram',
        )
        parser.add_argument(
            '--category',
            type=str,
            default='instagram',
            help='Category to assign to Instagram posts (default: instagram)',
        )
        parser.add_argument(
            '--featured',
            action='store_true',
            help='Mark synced posts as featured',
        )
    
    def handle(self, *args, **options):
        """Main command handler."""
        self.stdout.write("Starting Instagram sync...")
        
        limit = options['limit']
        force_refresh = options['force']
        dry_run = options['dry_run']
        delete_removed = options['delete_removed']
        category = options['category']
        mark_featured = options['featured']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be made")
            )
        
        try:
            # Initialize Instagram API
            api = InstagramAPI()
            
            # Fetch Instagram posts
            self.stdout.write(f"Fetching {limit} Instagram posts...")
            instagram_posts = api.get_user_media(
                limit=limit, 
                use_cache=not force_refresh
            )
            
            if not instagram_posts:
                self.stdout.write(
                    self.style.WARNING("No Instagram posts found")
                )
                return
            
            self.stdout.write(
                f"Found {len(instagram_posts)} Instagram posts"
            )
            
            # Validate category
            valid_categories = [choice[0] for choice in MediaGallery.CATEGORY_CHOICES]
            if category not in valid_categories:
                raise CommandError(
                    f"Invalid category '{category}'. "
                    f"Valid choices: {', '.join(valid_categories)}"
                )
            
            # Process posts
            stats = {
                'created': 0,
                'updated': 0,
                'skipped': 0,
                'deleted': 0,
                'errors': 0
            }
            
            with transaction.atomic():
                # Get existing Instagram posts
                existing_posts = {
                    post.instagram_id: post 
                    for post in MediaGallery.objects.filter(source='instagram')
                    if post.instagram_id
                }
                
                current_instagram_ids = set()
                
                # Process each Instagram post
                for post_data in instagram_posts:
                    instagram_id = post_data.get('id')
                    if not instagram_id:
                        self.stdout.write(
                            self.style.WARNING(f"Skipping post without ID: {post_data}")
                        )
                        stats['skipped'] += 1
                        continue
                    
                    current_instagram_ids.add(instagram_id)
                    
                    try:
                        result = self._process_instagram_post(
                            post_data, 
                            existing_posts.get(instagram_id),
                            category,
                            mark_featured,
                            dry_run
                        )
                        stats[result] += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error processing post {instagram_id}: {str(e)}"
                            )
                        )
                        stats['errors'] += 1
                
                # Handle deleted posts
                if delete_removed and not dry_run:
                    removed_ids = set(existing_posts.keys()) - current_instagram_ids
                    for removed_id in removed_ids:
                        post = existing_posts[removed_id]
                        self.stdout.write(
                            f"Deleting removed Instagram post: {post.title}"
                        )
                        post.delete()
                        stats['deleted'] += 1
                elif delete_removed and dry_run:
                    removed_ids = set(existing_posts.keys()) - current_instagram_ids
                    for removed_id in removed_ids:
                        post = existing_posts[removed_id]
                        self.stdout.write(
                            f"Would delete: {post.title} (ID: {removed_id})"
                        )
                        stats['deleted'] += 1
            
            # Report results
            self._report_results(stats, dry_run)
            
        except InstagramAPIError as e:
            raise CommandError(f"Instagram API error: {e.message}")
        except Exception as e:
            raise CommandError(f"Unexpected error: {str(e)}")
    
    def _process_instagram_post(self, post_data, existing_post, category, mark_featured, dry_run):
        """Process a single Instagram post."""
        instagram_id = post_data['id']
        
        # Prepare post data
        post_fields = {
            'title': self._generate_title(post_data),
            'media_type': post_data.get('media_type', 'image'),
            'category': category,
            'source': 'instagram',
            'url': post_data.get('media_url'),
            'caption': post_data.get('caption', '')[:500],  # Limit caption length
            'is_featured': mark_featured,
            'instagram_id': instagram_id,
            'instagram_permalink': post_data.get('permalink'),
            'instagram_username': post_data.get('username'),
            'instagram_timestamp': post_data.get('created_at'),
        }
        
        # Add tags based on caption
        if post_data.get('caption'):
            tags = self._extract_hashtags(post_data['caption'])
            if tags:
                post_fields['tags'] = ', '.join(tags)
        
        if existing_post:
            # Check if update is needed
            needs_update = self._needs_update(existing_post, post_fields)
            
            if not needs_update:
                self.stdout.write(f"No changes needed for: {existing_post.title}")
                return 'skipped'
            
            if dry_run:
                self.stdout.write(f"Would update: {existing_post.title}")
                return 'updated'
            
            # Update existing post
            for field, value in post_fields.items():
                setattr(existing_post, field, value)
            
            existing_post.updated_at = timezone.now()
            existing_post.save()
            
            self.stdout.write(
                self.style.SUCCESS(f"Updated: {existing_post.title}")
            )
            return 'updated'
        else:
            if dry_run:
                self.stdout.write(
                    f"Would create: {post_fields['title']} ({instagram_id})"
                )
                return 'created'
            
            # Create new post
            new_post = MediaGallery.objects.create(**post_fields)
            
            self.stdout.write(
                self.style.SUCCESS(f"Created: {new_post.title}")
            )
            return 'created'
    
    def _generate_title(self, post_data):
        """Generate a title for the Instagram post."""
        caption = post_data.get('caption', '')
        username = post_data.get('username', 'Instagram')
        
        if caption:
            # Use first line of caption as title, limit to 100 chars
            first_line = caption.split('\n')[0].strip()
            if first_line and len(first_line) <= 100:
                return first_line
            elif first_line:
                return first_line[:97] + '...'
        
        # Fallback to username and date
        created_at = post_data.get('created_at')
        if created_at:
            date_str = created_at.strftime('%Y-%m-%d')
            return f"{username} - {date_str}"
        
        return f"{username} Post"
    
    def _extract_hashtags(self, caption):
        """Extract hashtags from caption."""
        import re
        hashtags = re.findall(r'#(\w+)', caption.lower())
        # Limit to 10 hashtags and filter out common ones
        exclude_tags = {'instagram', 'post', 'photo', 'video'}
        return [tag for tag in hashtags[:10] if tag not in exclude_tags]
    
    def _needs_update(self, existing_post, new_fields):
        """Check if existing post needs updating."""
        for field, new_value in new_fields.items():
            if field == 'updated_at':  # Skip auto fields
                continue
            
            existing_value = getattr(existing_post, field)
            
            # Handle datetime fields
            if hasattr(new_value, 'replace') and hasattr(existing_value, 'replace'):
                if new_value and existing_value:
                    new_value = new_value.replace(microsecond=0)
                    existing_value = existing_value.replace(microsecond=0)
            
            if existing_value != new_value:
                return True
        
        return False
    
    def _report_results(self, stats, dry_run):
        """Report sync results."""
        total_processed = sum(stats.values())
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write("SYNC RESULTS" + (" (DRY RUN)" if dry_run else ""))
        self.stdout.write("="*50)
        
        self.stdout.write(f"Total processed: {total_processed}")
        self.stdout.write(
            self.style.SUCCESS(f"Created: {stats['created']}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Updated: {stats['updated']}")
        )
        self.stdout.write(f"Skipped: {stats['skipped']}")
        
        if stats['deleted'] > 0:
            self.stdout.write(
                self.style.WARNING(f"Deleted: {stats['deleted']}")
            )
        
        if stats['errors'] > 0:
            self.stdout.write(
                self.style.ERROR(f"Errors: {stats['errors']}")
            )
        
        self.stdout.write("="*50)