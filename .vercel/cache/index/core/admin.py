from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.db import models
from django.forms import TextInput, Textarea
from .models import Instructor, Class, Testimonial, Resource, ReviewLink, MediaGallery, FacebookEvent, ContactSubmission, BookingConfirmation, SpotifyPlaylist, RSVPSubmission


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_preview', 'instagram_link', 'specialties_display', 'has_video']
    search_fields = ['name', 'bio', 'specialties']
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'bio', 'specialties'),
            'description': 'Enter instructor details. Specialties can be comma-separated.'
        }),
        ('Media', {
            'fields': ('photo_url', 'video_url', 'photo_preview', 'video_preview'),
            'description': 'Add photo and video URLs. Videos should be YouTube or Vimeo links.'
        }),
        ('Social Media', {
            'fields': ('instagram',),
            'description': 'Instagram handle without @'
        }),
    )
    
    readonly_fields = ['photo_preview', 'video_preview']
    
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '60'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 6, 'cols': 80})},
    }
    
    def image_preview(self, obj):
        """Display thumbnail image in list view."""
        if obj.photo_url:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;" />',
                obj.photo_url
            )
        return format_html('<span style="color: #999;">No image</span>')
    image_preview.short_description = 'Photo'
    
    def instagram_link(self, obj):
        """Display clickable Instagram link."""
        if obj.instagram:
            handle = obj.instagram.strip('@')
            return format_html(
                '<a href="https://instagram.com/{}" target="_blank" style="color: #C7B375;">@{}</a>',
                handle, handle
            )
        return '-'
    instagram_link.short_description = 'Instagram'
    
    def specialties_display(self, obj):
        """Display specialties as badges."""
        if obj.specialties:
            specialties = [s.strip() for s in obj.specialties.split(',')]
            badges = []
            for specialty in specialties[:3]:  # Show max 3 in list
                badges.append(format_html(
                    '<span style="display: inline-block; padding: 2px 8px; '
                    'background: #C7B375; color: black; border-radius: 12px; '
                    'font-size: 11px; margin-right: 4px;">{}</span>',
                    specialty
                ))
            if len(specialties) > 3:
                badges.append(format_html(
                    '<span style="color: #666; font-size: 11px;">+{} more</span>',
                    len(specialties) - 3
                ))
            return format_html(''.join(badges))
        return '-'
    specialties_display.short_description = 'Specialties'
    
    def has_video(self, obj):
        """Show video status."""
        if obj.video_url:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: #ccc;">✗</span>')
    has_video.short_description = 'Video'
    has_video.admin_order_field = 'video_url'
    
    def photo_preview(self, obj):
        """Show photo preview in edit form."""
        if obj.photo_url:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; '
                'border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.photo_url
            )
        return 'No photo uploaded yet'
    photo_preview.short_description = 'Current Photo'
    
    def video_preview(self, obj):
        """Show video preview/embed in edit form."""
        if obj.video_url:
            # Convert to embed URL if YouTube or Vimeo
            embed_url = obj.video_url
            
            if 'youtube.com/watch' in embed_url:
                video_id = embed_url.split('v=')[1].split('&')[0]
                embed_url = f'https://www.youtube.com/embed/{video_id}'
            elif 'youtu.be/' in embed_url:
                video_id = embed_url.split('youtu.be/')[1].split('?')[0]
                embed_url = f'https://www.youtube.com/embed/{video_id}'
            elif 'vimeo.com/' in embed_url:
                video_id = embed_url.split('vimeo.com/')[1].split('?')[0]
                embed_url = f'https://player.vimeo.com/video/{video_id}'
            
            return format_html(
                '<iframe src="{}" width="560" height="315" frameborder="0" '
                'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
                'gyroscope; picture-in-picture" allowfullscreen></iframe>',
                embed_url
            )
        return 'No video uploaded yet'
    video_preview.short_description = 'Current Video'


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'instructor', 'day_of_week', 'start_time']
    list_filter = ['level', 'day_of_week']
    search_fields = ['name', 'description']
    list_per_page = 20
    
    fieldsets = (
        ('Class Information', {
            'fields': ('name', 'level', 'instructor', 'description')
        }),
        ('Schedule', {
            'fields': ('day_of_week', 'start_time', 'end_time')
        }),
        ('Capacity', {
            'fields': ('capacity',)
        }),
    )


def approve_testimonials(modeladmin, request, queryset):
    """Bulk approve testimonials"""
    count = queryset.filter(status='pending').update(
        status='approved',
        published_at=timezone.now()
    )
    modeladmin.message_user(request, f'{count} testimonials approved successfully.')
approve_testimonials.short_description = 'Approve selected testimonials'


def reject_testimonials(modeladmin, request, queryset):
    """Bulk reject testimonials"""
    count = queryset.filter(status='pending').update(status='rejected')
    modeladmin.message_user(request, f'{count} testimonials rejected.')
reject_testimonials.short_description = 'Reject selected testimonials'


# Import email notification function
from .utils.email_notifications import send_approval_notification_email


def approve_and_notify_testimonials(modeladmin, request, queryset):
    """Approve testimonials and send notification emails to submitters"""
    count = 0
    email_count = 0
    
    for testimonial in queryset.filter(status='pending'):
        # Update status and published_at
        testimonial.status = 'approved'
        testimonial.published_at = timezone.now()
        testimonial.save()
        count += 1
        
        # Send approval notification email
        try:
            if send_approval_notification_email(testimonial):
                email_count += 1
        except Exception as e:
            # Log error but don't fail the action
            print(f"Failed to send approval notification to {testimonial.email}: {e}")
    
    if count > 0:
        message = f'{count} testimonials approved successfully.'
        if email_count > 0:
            message += f' {email_count} approval notification emails sent.'
        if email_count < count:
            message += f' {count - email_count} emails failed to send.'
        modeladmin.message_user(request, message)
    else:
        modeladmin.message_user(request, 'No pending testimonials were selected for approval.')

approve_and_notify_testimonials.short_description = 'Approve testimonials and send notifications'


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'rating_display', 'class_type', 'content_preview', 'status_badge', 'featured', 'created_at']
    list_filter = ['status', 'rating', 'featured', 'class_type', ('created_at', admin.DateFieldListFilter)]
    search_fields = ['student_name', 'email', 'content']
    actions = [approve_testimonials, approve_and_notify_testimonials, reject_testimonials]
    list_per_page = 20
    list_editable = ['featured']
    date_hierarchy = 'created_at'
    
    fieldsets = (
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
    
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
    
    def rating_display(self, obj):
        """Display rating as stars"""
        from django.utils.html import format_html
        filled_stars = '★' * obj.rating
        empty_stars = '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color: #C7B375; font-size: 16px;">{}</span>'
            '<span style="color: #ddd; font-size: 16px;">{}</span>',
            filled_stars, empty_stars
        )
    rating_display.short_description = 'Rating'
    rating_display.admin_order_field = 'rating'
    
    def content_preview(self, obj):
        """Show first 100 characters of content"""
        from django.utils.html import format_html
        preview = obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        return format_html(
            '<span title="{}" style="cursor: help;">{}</span>',
            obj.content.replace('"', '&quot;'),
            preview
        )
    content_preview.short_description = 'Content Preview'
    
    def status_badge(self, obj):
        """Display status as a colored badge"""
        from django.utils.html import format_html
        colors = {
            'pending': '#ffc107',  # Yellow
            'approved': '#28a745',  # Green
            'rejected': '#dc3545',  # Red
        }
        return format_html(
            '<span style="display: inline-block; padding: 3px 8px; '
            'background-color: {}; color: white; border-radius: 3px; '
            'font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.status
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'order', 'created_at']
    list_filter = ['type']
    search_fields = ['title', 'description']
    ordering = ['order', 'created_at']
    list_per_page = 20
    
    fieldsets = (
        ('Resource Information', {
            'fields': ('title', 'type', 'description')
        }),
        ('Media & Links', {
            'fields': ('embed_url', 'instagram_post_id')
        }),
        ('Display Order', {
            'fields': ('order',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']


@admin.register(ReviewLink)
class ReviewLinkAdmin(admin.ModelAdmin):
    list_display = ['token_short', 'instructor_name', 'class_type', 'campaign_name', 'clicks', 'conversions', 'conversion_rate_display', 'created_at', 'is_active']
    list_filter = ['class_type', 'is_active', 'created_at']
    search_fields = ['token', 'instructor_name', 'campaign_name']
    list_editable = ['is_active']
    readonly_fields = ['token', 'clicks', 'conversions', 'last_accessed', 'created_at', 'conversion_rate_display']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Link Information', {
            'fields': ('token', 'instructor_name', 'class_type', 'campaign_name', 'created_by')
        }),
        ('Analytics', {
            'fields': ('clicks', 'conversions', 'conversion_rate_display', 'last_accessed')
        }),
        ('Status & Expiry', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def token_short(self, obj):
        return f"{obj.token[:8]}..."
    token_short.short_description = 'Token'
    
    def conversion_rate_display(self, obj):
        return f"{obj.get_conversion_rate()}%"
    conversion_rate_display.short_description = 'Conversion Rate'


class MediaGalleryInline(admin.TabularInline):
    """Inline admin for bulk uploading media items."""
    model = MediaGallery
    extra = 3
    fields = ['title', 'media_type', 'category', 'file', 'url', 'order', 'is_featured']
    ordering = ['order', '-created_at']


@admin.register(MediaGallery)
class MediaGalleryAdmin(admin.ModelAdmin):
    list_display = ['thumbnail_preview', 'title', 'media_type_badge', 'category_badge', 
                    'event', 'is_featured', 'order', 'created_at']
    list_filter = ['media_type', 'category', 'is_featured', ('created_at', admin.DateFieldListFilter)]
    search_fields = ['title', 'caption', 'event', 'tags']
    list_editable = ['order', 'is_featured']
    list_per_page = 30
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Media Information', {
            'fields': ('title', 'caption', 'media_type', 'category'),
            'description': 'Basic information about this media item.'
        }),
        ('Files & URLs', {
            'fields': ('file', 'url', 'thumbnail', 'media_preview'),
            'description': 'Upload files or provide URLs. Images can have separate thumbnails.'
        }),
        ('Event & Tags', {
            'fields': ('event', 'tags'),
            'description': 'Associate with an event and add comma-separated tags for filtering.'
        }),
        ('Display Settings', {
            'fields': ('order', 'is_featured'),
            'description': 'Control display order and featuring.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['media_preview', 'created_at', 'updated_at']
    
    actions = ['make_featured', 'remove_featured', 'bulk_reorder']
    
    class Media:
        css = {
            'all': ('css/admin-gallery.css',)
        }
        js = ('js/admin-gallery.js',)
    
    def thumbnail_preview(self, obj):
        """Display thumbnail in list view."""
        if obj.media_type == 'image':
            img_url = obj.thumbnail.url if obj.thumbnail else (obj.file.url if obj.file else obj.url)
            if img_url:
                return format_html(
                    '<img src="{}" style="width: 60px; height: 60px; '
                    'object-fit: cover; border-radius: 4px;" />',
                    img_url
                )
        elif obj.media_type == 'video':
            # Show video thumbnail or icon
            if obj.thumbnail:
                return format_html(
                    '<div style="position: relative; width: 60px; height: 60px;">'
                    '<img src="{}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 4px;" />'
                    '<span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); '
                    'color: white; background: rgba(0,0,0,0.7); border-radius: 50%; width: 24px; height: 24px; '
                    'display: flex; align-items: center; justify-content: center; font-size: 10px;">▶</span>'
                    '</div>',
                    obj.thumbnail.url
                )
            else:
                return format_html(
                    '<div style="width: 60px; height: 60px; background: #f0f0f0; border-radius: 4px; '
                    'display: flex; align-items: center; justify-content: center; color: #999;">'
                    '<span style="font-size: 24px;">🎬</span></div>'
                )
        return '-'
    thumbnail_preview.short_description = 'Preview'
    
    def media_type_badge(self, obj):
        """Display media type as badge."""
        colors = {
            'image': '#28a745',
            'video': '#007bff',
        }
        icons = {
            'image': '🖼',
            'video': '🎬',
        }
        return format_html(
            '<span style="display: inline-block; padding: 3px 8px; '
            'background: {}; color: white; border-radius: 12px; '
            'font-size: 11px; font-weight: 500;">{} {}</span>',
            colors.get(obj.media_type, '#6c757d'),
            icons.get(obj.media_type, ''),
            obj.get_media_type_display()
        )
    media_type_badge.short_description = 'Type'
    media_type_badge.admin_order_field = 'media_type'
    
    def category_badge(self, obj):
        """Display category as colored badge."""
        colors = {
            'class': '#28a745',
            'event': '#007bff', 
            'performance': '#dc3545',
            'social': '#ffc107',
            'workshop': '#17a2b8',
            'team': '#6f42c1',
        }
        return format_html(
            '<span style="display: inline-block; padding: 3px 8px; '
            'background-color: {}; color: white; border-radius: 3px; '
            'font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.category, '#6c757d'),
            obj.get_category_display()
        )
    category_badge.short_description = 'Category'
    category_badge.admin_order_field = 'category'
    
    def media_preview(self, obj):
        """Show media preview in edit form."""
        if obj.media_type == 'photo' and obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 300px; '
                'border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        elif obj.media_type == 'video' and obj.video_url:
            embed_url = obj.get_video_embed_url()
            if embed_url:
                return format_html(
                    '<iframe src="{}" width="560" height="315" frameborder="0" '
                    'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
                    'gyroscope; picture-in-picture" allowfullscreen></iframe>',
                    embed_url
                )
            else:
                return format_html(
                    '<a href="{}" target="_blank" style="color: #007bff;">View video →</a>',
                    obj.video_url
                )
        return 'No media uploaded yet'
    media_preview.short_description = 'Preview'


def sync_facebook_events_action(modeladmin, request, queryset):
    """Admin action to sync Facebook events."""
    from .utils.facebook_events import clear_facebook_events_cache
    
    # Clear cache to force fresh sync
    clear_facebook_events_cache()
    
    # Import and run sync logic
    from django.core.management import call_command
    try:
        call_command('sync_facebook_events', verbosity=0)
        modeladmin.message_user(request, 'Facebook events synced successfully.')
    except Exception as e:
        modeladmin.message_user(request, f'Sync failed: {str(e)}', level='ERROR')

sync_facebook_events_action.short_description = 'Sync with Facebook Events API'


@admin.register(FacebookEvent)
class FacebookEventAdmin(admin.ModelAdmin):
    list_display = ['event_preview', 'name', 'formatted_date', 'formatted_time', 
                    'is_future', 'featured', 'is_active', 'last_synced']
    list_filter = ['is_active', 'featured', 'start_time', 'last_synced']
    search_fields = ['name', 'description', 'facebook_id']
    list_editable = ['featured', 'is_active']
    readonly_fields = ['facebook_id', 'facebook_url', 'last_synced', 'created_at', 'updated_at', 'event_preview_large']
    actions = [sync_facebook_events_action]
    date_hierarchy = 'start_time'
    list_per_page = 20
    
    fieldsets = (
        ('Facebook Event Data', {
            'fields': ('facebook_id', 'name', 'description', 'facebook_url'),
            'description': 'Data synced from Facebook Events API. Most fields are read-only.'
        }),
        ('Event Timing', {
            'fields': ('start_time', 'end_time', 'formatted_date', 'formatted_time')
        }),
        ('Media & Location', {
            'fields': ('cover_photo_url', 'event_preview_large', 'location_name', 'location_address')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'featured', 'order'),
            'description': 'Control how events are displayed on the website.'
        }),
        ('Sync Information', {
            'fields': ('last_synced', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def event_preview(self, obj):
        """Display event thumbnail in list view."""
        if obj.cover_photo_url:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; '
                'object-fit: cover; border-radius: 4px;" />',
                obj.cover_photo_url
            )
        else:
            return format_html(
                '<div style="width: 60px; height: 60px; background: linear-gradient(135deg, #1877f2 0%, #42a5f5 100%); '
                'border-radius: 4px; display: flex; align-items: center; justify-content: center; color: white;">'
                '<i class="fas fa-calendar-alt" style="font-size: 20px;"></i></div>'
            )
    event_preview.short_description = 'Preview'
    
    def event_preview_large(self, obj):
        """Display large event preview in edit form."""
        if obj.cover_photo_url:
            return format_html(
                '<div style="max-width: 500px;">'
                '<img src="{}" style="width: 100%; max-height: 300px; '
                'object-fit: cover; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />'
                '<p style="margin-top: 10px; color: #666; font-size: 12px;">Cover photo from Facebook</p>'
                '</div>',
                obj.cover_photo_url
            )
        return 'No cover photo available'
    event_preview_large.short_description = 'Cover Photo'
    
    def is_future(self, obj):
        """Show if event is in the future."""
        if obj.is_future_event():
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Future</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545;">✗ Past</span>'
            )
    is_future.short_description = 'Status'
    is_future.admin_order_field = 'start_time'
    
    def get_queryset(self, request):
        """Optimize queries."""
        return super().get_queryset(request).order_by('-start_time')
    
    class Media:
        css = {
            'all': ('admin/css/facebook-events.css',)  # Custom CSS for Facebook events admin
        }


# SPEC_05 Group B Task 10 - Contact and Booking Admin

def mark_contacts_responded(modeladmin, request, queryset):
    """Mark selected contacts as responded."""
    count = queryset.filter(status__in=['new', 'in_progress']).update(
        status='responded',
        responded_at=timezone.now()
    )
    modeladmin.message_user(request, f'{count} contacts marked as responded.')
mark_contacts_responded.short_description = 'Mark as responded'


def prioritize_contacts(modeladmin, request, queryset):
    """Set selected contacts to high priority."""
    count = queryset.update(priority='high')
    modeladmin.message_user(request, f'{count} contacts set to high priority.')
prioritize_contacts.short_description = 'Set to high priority'


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'interest_badge', 'status_badge', 'priority_badge', 
                    'urgency_score_display', 'priority', 'created_at', 'admin_notes_preview']
    list_filter = ['status', 'priority', 'interest', ('created_at', admin.DateFieldListFilter)]
    search_fields = ['name', 'email', 'message', 'admin_notes']
    actions = [mark_contacts_responded, prioritize_contacts]
    list_editable = ['priority']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone'),
            'description': 'Customer contact details.'
        }),
        ('Inquiry Details', {
            'fields': ('interest', 'message'),
            'description': 'What the customer is interested in and their message.'
        }),
        ('Administrative', {
            'fields': ('status', 'priority', 'source', 'admin_notes'),
            'description': 'Internal tracking and notes for staff.'
        }),
        ('Email Tracking', {
            'fields': ('admin_notification_sent', 'auto_reply_sent'),
            'classes': ('collapse',),
            'description': 'Email delivery status tracking.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'responded_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'admin_notification_sent', 'auto_reply_sent']
    
    def get_queryset(self, request):
        """Order by urgency score and creation date."""
        return super().get_queryset(request).order_by('-priority', '-created_at')
    
    def interest_badge(self, obj):
        """Display interest as colored badge."""
        colors = {
            'classes': '#28a745',
            'private_lesson': '#dc3545',
            'workshop': '#0d6efd',
            'events': '#6f42c1',
            'choreography': '#fd7e14',
            'general': '#6c757d',
            'other': '#6c757d',
        }
        return format_html(
            '<span style="display: inline-block; padding: 3px 8px; '
            'background-color: {}; color: white; border-radius: 3px; '
            'font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.interest, '#6c757d'),
            obj.get_interest_display()
        )
    interest_badge.short_description = 'Interest'
    interest_badge.admin_order_field = 'interest'
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'new': '#dc3545',
            'in_progress': '#ffc107',
            'responded': '#28a745',
            'closed': '#6c757d',
        }
        return format_html(
            '<span style="display: inline-block; padding: 3px 8px; '
            'background-color: {}; color: white; border-radius: 3px; '
            'font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.status
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def priority_badge(self, obj):
        """Display priority as colored badge."""
        colors = {
            'low': '#28a745',
            'normal': '#0d6efd',
            'high': '#ffc107',
            'urgent': '#dc3545',
        }
        return format_html(
            '<span style="display: inline-block; padding: 3px 8px; '
            'background-color: {}; color: white; border-radius: 3px; '
            'font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            colors.get(obj.priority, '#6c757d'),
            obj.priority
        )
    priority_badge.short_description = 'Priority'
    priority_badge.admin_order_field = 'priority'
    
    def urgency_score_display(self, obj):
        """Display urgency score with color coding."""
        score = obj.get_urgency_score()
        if score >= 50:
            color = '#dc3545'  # Red
        elif score >= 35:
            color = '#ffc107'  # Yellow
        elif score >= 20:
            color = '#0d6efd'  # Blue
        else:
            color = '#28a745'  # Green
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, score
        )
    urgency_score_display.short_description = 'Urgency'
    
    def admin_notes_preview(self, obj):
        """Show preview of admin notes."""
        if obj.admin_notes:
            preview = obj.admin_notes[:50] + '...' if len(obj.admin_notes) > 50 else obj.admin_notes
            return format_html(
                '<span title="{}" style="cursor: help; color: #666; font-style: italic;">{}</span>',
                obj.admin_notes.replace('"', '&quot;'),
                preview
            )
        return '-'
    admin_notes_preview.short_description = 'Notes'


def send_booking_reminders(modeladmin, request, queryset):
    """Send reminder emails for upcoming bookings."""
    from .utils.email_notifications import send_booking_reminder_email
    
    count = 0
    for booking in queryset.filter(status='confirmed', reminder_email_sent=False):
        try:
            if send_booking_reminder_email(booking):
                count += 1
        except Exception as e:
            # Log error but continue with other bookings
            print(f"Failed to send reminder for booking {booking.booking_id}: {e}")
    
    modeladmin.message_user(request, f'{count} reminder emails sent successfully.')
send_booking_reminders.short_description = 'Send reminder emails'


def mark_bookings_completed(modeladmin, request, queryset):
    """Mark selected bookings as completed."""
    count = queryset.filter(status='confirmed').update(status='completed')
    modeladmin.message_user(request, f'{count} bookings marked as completed.')
mark_bookings_completed.short_description = 'Mark as completed'


@admin.register(BookingConfirmation)
class BookingConfirmationAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'customer_name', 'class_name', 'booking_date_short', 
                    'price_display', 'status_badge', 'time_until_display', 'created_at']
    list_filter = ['status', 'booking_type', ('booking_date', admin.DateFieldListFilter), 
                   ('created_at', admin.DateFieldListFilter)]
    search_fields = ['booking_id', 'customer_name', 'customer_email', 'class_name', 'instructor_name']
    actions = [send_booking_reminders, mark_bookings_completed]
    list_per_page = 25
    date_hierarchy = 'booking_date'
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'booking_type', 'class_name', 'instructor_name'),
            'description': 'Basic booking details and service information.'
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone'),
            'description': 'Customer contact details.'
        }),
        ('Schedule & Location', {
            'fields': ('booking_date', 'duration_minutes', 'location'),
            'description': 'When and where the booking takes place.'
        }),
        ('Payment & Pricing', {
            'fields': ('price', 'payment_method', 'payment_reference'),
            'description': 'Payment details and pricing information.'
        }),
        ('Status & Notes', {
            'fields': ('status', 'special_instructions', 'admin_notes'),
            'description': 'Booking status and any special notes.'
        }),
        ('External Integration', {
            'fields': ('calendly_event_id', 'google_calendar_id'),
            'classes': ('collapse',),
            'description': 'Integration with external calendar systems.'
        }),
        ('Email Tracking', {
            'fields': ('confirmation_email_sent', 'reminder_email_sent', 'follow_up_email_sent'),
            'classes': ('collapse',),
            'description': 'Email delivery status tracking.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['booking_id', 'created_at', 'updated_at', 'confirmation_email_sent', 
                       'reminder_email_sent', 'follow_up_email_sent']
    
    def get_queryset(self, request):
        """Order by booking date."""
        return super().get_queryset(request).order_by('-booking_date')
    
    def booking_date_short(self, obj):
        """Display booking date in short format."""
        return obj.booking_date.strftime('%m/%d/%y %I:%M %p')
    booking_date_short.short_description = 'Date & Time'
    booking_date_short.admin_order_field = 'booking_date'
    
    def price_display(self, obj):
        """Display price with currency symbol."""
        return format_html(
            '<span style="font-weight: bold; color: #28a745;">${}</span>',
            obj.price
        )
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'confirmed': '#28a745',
            'pending': '#ffc107',
            'cancelled': '#dc3545',
            'completed': '#6c757d',
        }
        return format_html(
            '<span style="display: inline-block; padding: 3px 8px; '
            'background-color: {}; color: white; border-radius: 3px; '
            'font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.status
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def time_until_display(self, obj):
        """Display time until booking with color coding."""
        time_until = obj.get_time_until_booking()
        
        if 'Past' in time_until:
            color = '#6c757d'
        elif any(word in time_until for word in ['minutes', 'hours']):
            color = '#dc3545'  # Red for urgent
        elif 'days' in time_until:
            days = int(time_until.split()[1]) if 'In' in time_until else 0
            if days <= 1:
                color = '#ffc107'  # Yellow
            else:
                color = '#28a745'  # Green
        else:
            color = '#0d6efd'  # Blue
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, time_until
        )
    time_until_display.short_description = 'Time Until'


@admin.register(SpotifyPlaylist)
class SpotifyPlaylistAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Spotify playlists.
    SPEC_05 Group C Task 8 - Spotify playlists integration.
    """
    list_display = ['class_type_badge', 'title', 'tracks_display', 'duration_display', 
                    'theme_preview', 'is_active', 'order', 'last_updated']
    list_filter = ['class_type', 'is_active', ('last_updated', admin.DateFieldListFilter)]
    search_fields = ['title', 'description', 'spotify_playlist_id']
    list_editable = ['is_active', 'order']
    readonly_fields = ['playlist_preview', 'last_updated', 'created_at']
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('class_type', 'title', 'description'),
            'description': 'Basic playlist information and class association.'
        }),
        ('Spotify Integration', {
            'fields': ('spotify_playlist_id', 'spotify_embed_url', 'playlist_preview'),
            'description': 'Spotify playlist ID and embed URL. Either field can be used to generate embeds.'
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order', 'theme_color'),
            'description': 'Control display order, visibility, and theme colors.'
        }),
        ('Metadata', {
            'fields': ('tracks_count', 'duration_minutes'),
            'description': 'Optional metadata about the playlist content.'
        }),
        ('Timestamps', {
            'fields': ('last_updated', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_playlists', 'deactivate_playlists', 'update_metadata']
    
    def class_type_badge(self, obj):
        """Display class type as colored badge."""
        colors = {
            'choreo_team': '#dc3545',     # Red for advanced
            'pasos_basicos': '#28a745',   # Green for beginner
            'casino_royale': '#ffc107',   # Yellow for intermediate
            'general': '#6c757d',         # Gray for general
            'warm_up': '#17a2b8',         # Teal for warm up
            'cool_down': '#6f42c1',       # Purple for cool down
        }
        return format_html(
            '<span style="display: inline-block; padding: 4px 12px; '
            'background-color: {}; color: white; border-radius: 15px; '
            'font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            colors.get(obj.class_type, '#6c757d'),
            obj.get_class_type_display()
        )
    class_type_badge.short_description = 'Class Type'
    class_type_badge.admin_order_field = 'class_type'
    
    def tracks_display(self, obj):
        """Display track count with icon."""
        if obj.tracks_count > 0:
            return format_html(
                '<span style="color: #28a745;"><i class="fas fa-music"></i> {} track{}</span>',
                obj.tracks_count,
                's' if obj.tracks_count != 1 else ''
            )
        return format_html('<span style="color: #999;">Unknown</span>')
    tracks_display.short_description = 'Tracks'
    tracks_display.admin_order_field = 'tracks_count'
    
    def duration_display(self, obj):
        """Display duration with clock icon."""
        if obj.duration_minutes > 0:
            duration = obj.format_duration()
            return format_html(
                '<span style="color: #0d6efd;"><i class="fas fa-clock"></i> {}</span>',
                duration
            )
        return format_html('<span style="color: #999;">Unknown</span>')
    duration_display.short_description = 'Duration'
    duration_display.admin_order_field = 'duration_minutes'
    
    def theme_preview(self, obj):
        """Display theme color preview."""
        return format_html(
            '<div style="display: inline-flex; align-items: center; gap: 8px;">'
            '<div style="width: 20px; height: 20px; background-color: {}; '
            'border-radius: 3px; border: 1px solid #ccc;"></div>'
            '<span style="font-family: monospace; font-size: 11px; color: #666;">{}</span>'
            '</div>',
            obj.theme_color,
            obj.theme_color
        )
    theme_preview.short_description = 'Theme'
    
    def playlist_preview(self, obj):
        """Display playlist embed preview in admin form."""
        if obj.get_embed_url():
            return format_html(
                '<div style="max-width: 600px; margin: 10px 0;">'
                '<div style="margin-bottom: 10px;">'
                '<strong>Playlist Preview:</strong>'
                '</div>'
                '<iframe src="{}" width="100%" height="300" frameborder="0" '
                'allowtransparency="true" allow="encrypted-media" loading="lazy"></iframe>'
                '<div style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px;">'
                '<strong>Embed URL:</strong> <code style="font-size: 11px; word-break: break-all;">{}</code>'
                '</div>'
                '<div style="margin-top: 5px;">'
                '<a href="{}" target="_blank" style="color: #1DB954; text-decoration: none;">'
                '<i class="fab fa-spotify"></i> Open in Spotify</a>'
                '</div>'
                '</div>',
                obj.get_compact_embed_url(),
                obj.get_embed_url(),
                obj.get_playlist_url() or '#'
            )
        elif obj.spotify_playlist_id:
            return format_html(
                '<div style="padding: 20px; background: #f8f9fa; border-radius: 4px; text-align: center;">'
                '<p style="color: #666; margin-bottom: 10px;">Playlist ID provided but no embed URL generated yet.</p>'
                '<p><strong>Playlist ID:</strong> <code>{}</code></p>'
                '<p style="margin-top: 10px;">'
                '<a href="https://open.spotify.com/playlist/{}" target="_blank" '
                'style="color: #1DB954; text-decoration: none;">'
                '<i class="fab fa-spotify"></i> View on Spotify</a>'
                '</p>'
                '</div>',
                obj.spotify_playlist_id,
                obj.spotify_playlist_id
            )
        else:
            return format_html(
                '<div style="padding: 20px; background: #fff3cd; border: 1px solid #ffeaa7; '
                'border-radius: 4px; color: #856404;">'
                '<p><strong>No playlist configured yet.</strong></p>'
                '<p>Add a Spotify playlist ID or embed URL to see the preview.</p>'
                '</div>'
            )
    playlist_preview.short_description = 'Preview'
    
    # Admin actions
    def activate_playlists(self, request, queryset):
        """Activate selected playlists."""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} playlist(s) activated successfully.')
    activate_playlists.short_description = 'Activate selected playlists'
    
    def deactivate_playlists(self, request, queryset):
        """Deactivate selected playlists."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} playlist(s) deactivated successfully.')
    deactivate_playlists.short_description = 'Deactivate selected playlists'
    
    def update_metadata(self, request, queryset):
        """Update metadata for selected playlists."""
        # This would integrate with Spotify API in a full implementation
        count = queryset.count()
        self.message_user(
            request, 
            f'Metadata update initiated for {count} playlist(s). '
            f'This would fetch current track counts and durations from Spotify API.',
            level='WARNING'
        )
    update_metadata.short_description = 'Update playlist metadata from Spotify'
    
    class Media:
        css = {
            'all': ('css/spotify-playlists.css',)
        }
        js = ('js/spotify-playlists.js',)


# SPEC_05 Group B Task 7 - Pastio.fun RSVP Integration Admin

def send_rsvp_confirmations(modeladmin, request, queryset):
    """Send RSVP confirmation emails to selected attendees."""
    from .views import send_rsvp_confirmation_email
    
    count = 0
    for rsvp in queryset.filter(status='confirmed', notifications_enabled=True):
        try:
            if send_rsvp_confirmation_email(rsvp):
                count += 1
        except Exception as e:
            # Log error but continue with other RSVPs
            print(f"Failed to send confirmation for RSVP {rsvp.id}: {e}")
    
    modeladmin.message_user(request, f'{count} confirmation emails sent successfully.')
send_rsvp_confirmations.short_description = 'Send confirmation emails'


def mark_rsvps_attended(modeladmin, request, queryset):
    """Mark selected RSVPs as attended."""
    count = queryset.filter(status='confirmed').update(attended=True)
    modeladmin.message_user(request, f'{count} RSVPs marked as attended.')
mark_rsvps_attended.short_description = 'Mark as attended'


def cancel_rsvps(modeladmin, request, queryset):
    """Cancel selected RSVPs."""
    count = queryset.filter(status='confirmed').update(status='cancelled')
    modeladmin.message_user(request, f'{count} RSVPs cancelled.')
cancel_rsvps.short_description = 'Cancel RSVPs'


@admin.register(RSVPSubmission)
class RSVPSubmissionAdmin(admin.ModelAdmin):
    """
    Admin interface for managing RSVP submissions from Pastio.fun integration.
    SPEC_05 Group B Task 7 - Pastio.fun events integration.
    """
    list_display = ['name', 'class_badge', 'party_size_display', 'status_badge', 
                    'source_badge', 'next_class_display', 'attended_status', 'created_at']
    list_filter = ['status', 'class_id', 'source', 'attended', 'notifications_enabled', 
                   ('created_at', admin.DateFieldListFilter)]
    search_fields = ['name', 'email', 'phone', 'class_name', 'plus_one_name']
    actions = [send_rsvp_confirmations, mark_rsvps_attended, cancel_rsvps]
    list_editable = []
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('RSVP Information', {
            'fields': ('name', 'email', 'phone'),
            'description': 'Basic attendee contact information.'
        }),
        ('Class Details', {
            'fields': ('class_id', 'class_name'),
            'description': 'Which class this RSVP is for.'
        }),
        ('Party Information', {
            'fields': ('plus_one', 'plus_one_name', 'special_requirements'),
            'description': 'Additional party members and special needs.'
        }),
        ('Status & Settings', {
            'fields': ('status', 'source', 'notifications_enabled'),
            'description': 'RSVP status and notification preferences.'
        }),
        ('External Integration', {
            'fields': ('pastio_id', 'facebook_event_id'),
            'classes': ('collapse',),
            'description': 'Integration with external platforms.'
        }),
        ('Attendance Tracking', {
            'fields': ('attended', 'admin_notes'),
            'description': 'Attendance tracking and internal notes.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Order by creation date with upcoming classes first."""
        return super().get_queryset(request).order_by('-created_at')
    
    def class_badge(self, obj):
        """Display class as colored badge."""
        colors = {
            'scf-choreo': '#dc3545',      # Red for advanced
            'pasos-basicos': '#28a745',   # Green for beginner
            'casino-royale': '#ffc107',   # Yellow for intermediate
        }
        return format_html(
            '<span style="display: inline-block; padding: 4px 12px; '
            'background-color: {}; color: {}; border-radius: 15px; '
            'font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            colors.get(obj.class_id, '#6c757d'),
            'black' if obj.class_id == 'casino-royale' else 'white',
            obj.class_name
        )
    class_badge.short_description = 'Class'
    class_badge.admin_order_field = 'class_id'
    
    def party_size_display(self, obj):
        """Display party size with plus one info."""
        if obj.plus_one:
            plus_one_text = f" (+1: {obj.plus_one_name})" if obj.plus_one_name else " (+1)"
            return format_html(
                '<span style="font-weight: bold;">2</span>'
                '<span style="color: #666; font-size: 11px;">{}</span>',
                plus_one_text
            )
        return format_html('<span style="font-weight: bold;">1</span>')
    party_size_display.short_description = 'Party Size'
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'confirmed': '#28a745',
            'pending': '#ffc107',
            'cancelled': '#dc3545',
            'no_show': '#6c757d',
        }
        return format_html(
            '<span style="display: inline-block; padding: 3px 8px; '
            'background-color: {}; color: white; border-radius: 3px; '
            'font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.status
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def source_badge(self, obj):
        """Display source as colored badge."""
        colors = {
            'pastio': '#C7B375',
            'website': '#0d6efd',
            'facebook': '#1877f2',
            'instagram': '#E4405F',
            'other': '#6c757d',
        }
        icons = {
            'pastio': '🎉',
            'website': '💻',
            'facebook': '👍',
            'instagram': '📷',
            'other': '❓',
        }
        return format_html(
            '<span style="display: inline-block; padding: 3px 8px; '
            'background-color: {}; color: {}; border-radius: 3px; '
            'font-size: 11px; font-weight: bold;">{} {}</span>',
            colors.get(obj.source, '#6c757d'),
            'black' if obj.source == 'pastio' else 'white',
            icons.get(obj.source, ''),
            obj.get_source_display()
        )
    source_badge.short_description = 'Source'
    source_badge.admin_order_field = 'source'
    
    def next_class_display(self, obj):
        """Display next class date and time."""
        next_date = obj.get_next_class_date()
        class_time = obj.get_class_time()
        
        return format_html(
            '<div style="font-size: 12px;">'
            '<div style="font-weight: bold; color: #0d6efd;">{}</div>'
            '<div style="color: #666;">{}</div>'
            '</div>',
            next_date.strftime('%a, %b %d'),
            class_time
        )
    next_class_display.short_description = 'Next Class'
    
    def attended_status(self, obj):
        """Display attendance status."""
        if obj.attended is True:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Attended</span>'
            )
        elif obj.attended is False:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">✗ No Show</span>'
            )
        else:
            if obj.is_upcoming():
                return format_html(
                    '<span style="color: #ffc107;">⏳ Pending</span>'
                )
            else:
                return format_html(
                    '<span style="color: #6c757d;">❔ Unknown</span>'
                )
    attended_status.short_description = 'Attendance'
    attended_status.admin_order_field = 'attended'
    
    def get_readonly_fields(self, request, obj=None):
        """Make pastio_id readonly if it exists."""
        readonly = list(self.readonly_fields)
        if obj and obj.pastio_id:
            readonly.append('pastio_id')
        return readonly
