from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
import uuid


class Instructor(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    photo_url = models.URLField()
    video_url = models.URLField(blank=True)
    instagram = models.CharField(max_length=50, blank=True)
    specialties = models.TextField()  # Store as JSON string for SQLite compatibility
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Class(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, default='Sunday')
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField()
    capacity = models.IntegerField(default=20)
    
    def __str__(self):
        return f"{self.name} - {self.get_level_display()}"
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        verbose_name_plural = "Classes"


class Testimonial(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    CLASS_TYPE_CHOICES = [
        ('choreo_team', 'SCF Choreo Team'),
        ('pasos_basicos', 'Pasos Básicos'),
        ('casino_royale', 'Casino Royale'),
        ('private_lesson', 'Private Lesson'),
        ('workshop', 'Workshop'),
        ('other', 'Other'),
    ]
    
    student_name = models.CharField(max_length=100)
    email = models.EmailField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    content = models.TextField()
    class_type = models.CharField(max_length=50, choices=CLASS_TYPE_CHOICES)
    photo = models.ImageField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    google_review_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student_name} - {self.rating} stars"
    
    class Meta:
        ordering = ['-created_at']


class MediaGallery(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    CATEGORY_CHOICES = [
        ('class', 'Class'),
        ('performance', 'Performance'),
        ('social', 'Social Dance'),
        ('workshop', 'Workshop'),
        ('event', 'Event'),
        ('team', 'Team Photos'),
        ('instagram', 'Instagram Post'),
    ]
    
    SOURCE_CHOICES = [
        ('local', 'Local Upload'),
        ('url', 'External URL'),
        ('instagram', 'Instagram'),
    ]
    
    title = models.CharField(max_length=200)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='local')
    file = models.FileField(upload_to='gallery/%Y/%m/', blank=True, null=True)
    url = models.URLField(blank=True, help_text="External URL for video or image")
    thumbnail = models.ImageField(upload_to='gallery/thumbs/%Y/%m/', blank=True, null=True)
    caption = models.TextField(blank=True)
    event = models.CharField(max_length=200, blank=True)
    tags = models.TextField(blank=True, help_text="Comma-separated tags")
    order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Instagram-specific fields
    instagram_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    instagram_permalink = models.URLField(blank=True, null=True)
    instagram_username = models.CharField(max_length=100, blank=True, null=True)
    instagram_timestamp = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_media_type_display()})"
    
    def get_tags_list(self):
        """Return tags as a list."""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def is_instagram_post(self):
        """Check if this is an Instagram post."""
        return self.source == 'instagram' and self.instagram_id
    
    def get_display_url(self):
        """Get the appropriate URL for display."""
        if self.url:
            return self.url
        elif self.file:
            return self.file.url
        return None
    
    def get_thumbnail_url(self):
        """Get the appropriate thumbnail URL."""
        if self.thumbnail:
            return self.thumbnail.url
        elif self.is_instagram_post() and self.media_type == 'video':
            # For Instagram videos, the main URL is often the thumbnail
            return self.get_display_url()
        return self.get_display_url()
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name_plural = "Media Gallery"


class Resource(models.Model):
    TYPE_CHOICES = [
        ('playlist', 'Playlist'),
        ('video', 'Video'),
        ('guide', 'Guide'),
    ]
    
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    embed_url = models.URLField()
    instagram_post_id = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"
    
    class Meta:
        ordering = ['order', 'created_at']


class SpotifyPlaylist(models.Model):
    """
    Model to store Spotify playlists for each class type.
    SPEC_05 Group C Task 8 - Spotify playlists integration.
    """
    
    CLASS_TYPE_CHOICES = [
        ('choreo_team', 'SCF Choreo Team'),
        ('pasos_basicos', 'Pasos Básicos'),
        ('casino_royale', 'Casino Royale'),
        ('general', 'General Practice'),
        ('warm_up', 'Warm Up'),
        ('cool_down', 'Cool Down'),
    ]
    
    # Basic Information
    class_type = models.CharField(max_length=20, choices=CLASS_TYPE_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Spotify Integration
    spotify_playlist_id = models.CharField(max_length=50, help_text="Spotify playlist ID (not full URL)")
    spotify_embed_url = models.URLField(help_text="Full Spotify embed URL")
    
    # Display Options
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    theme_color = models.CharField(max_length=7, default='#C7B375', help_text="Hex color code for playlist theme")
    
    # Metadata
    tracks_count = models.IntegerField(default=0, help_text="Number of tracks in playlist")
    duration_minutes = models.IntegerField(default=0, help_text="Total duration in minutes")
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_class_type_display()} - {self.title}"
    
    def get_embed_url(self):
        """Generate Spotify embed URL with compact theme."""
        if self.spotify_embed_url:
            return self.spotify_embed_url
        elif self.spotify_playlist_id:
            return f"https://open.spotify.com/embed/playlist/{self.spotify_playlist_id}?utm_source=generator&theme=0"
        return None
    
    def get_compact_embed_url(self):
        """Generate compact Spotify embed URL."""
        base_url = self.get_embed_url()
        if base_url:
            # Add compact view parameters
            separator = '&' if '?' in base_url else '?'
            return f"{base_url}{separator}theme=0&view=compact&height=380"
        return None
    
    def get_playlist_url(self):
        """Get direct Spotify playlist URL for opening in app."""
        if self.spotify_playlist_id:
            return f"https://open.spotify.com/playlist/{self.spotify_playlist_id}"
        return None
    
    def format_duration(self):
        """Format duration in human-readable format."""
        if self.duration_minutes <= 0:
            return "Unknown"
        
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes} min"
    
    @classmethod
    def get_active_playlists(cls):
        """Get all active playlists ordered by display order."""
        return cls.objects.filter(is_active=True).order_by('order', 'class_type')
    
    @classmethod
    def get_playlist_for_class(cls, class_type):
        """Get playlist for specific class type."""
        try:
            return cls.objects.get(class_type=class_type, is_active=True)
        except cls.DoesNotExist:
            return None
    
    class Meta:
        ordering = ['order', 'class_type']
        verbose_name = "Spotify Playlist"
        verbose_name_plural = "Spotify Playlists"


class ReviewLink(models.Model):
    """Model to track shareable review links and their analytics."""
    
    # Link identification
    token = models.CharField(max_length=32, unique=True, db_index=True)
    
    # Pre-fill parameters
    instructor_name = models.CharField(max_length=100, blank=True)
    class_type = models.CharField(max_length=50, blank=True)
    
    # Campaign tracking
    campaign_name = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.CharField(max_length=100, default='System')
    
    # Analytics
    clicks = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)  # Successful testimonial submissions
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        parts = []
        if self.instructor_name:
            parts.append(f"Instructor: {self.instructor_name}")
        if self.class_type:
            parts.append(f"Class: {self.class_type}")
        if self.campaign_name:
            parts.append(f"Campaign: {self.campaign_name}")
        
        if parts:
            return f"Review Link ({', '.join(parts)})"
        return f"Review Link - {self.token[:8]}"
    
    def get_full_url(self, request=None):
        """Generate the full URL for this review link."""
        base_url = "/testimonials/submit/"
        params = [f"ref={self.token}"]
        
        if self.instructor_name:
            params.append(f"instructor={self.instructor_name.lower().replace(' ', '-')}")
        if self.class_type:
            params.append(f"class={self.class_type}")
            
        return f"{base_url}?{'&'.join(params)}"
    
    def get_short_url(self):
        """Generate a shortened version of the URL."""
        return f"/r/{self.token[:8]}"
    
    def track_click(self):
        """Track a click on this review link."""
        self.clicks += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['clicks', 'last_accessed'])
    
    def track_conversion(self):
        """Track a successful testimonial submission from this link."""
        self.conversions += 1
        self.save(update_fields=['conversions'])
    
    def get_conversion_rate(self):
        """Calculate conversion rate as percentage."""
        if self.clicks == 0:
            return 0
        return round((self.conversions / self.clicks) * 100, 2)
    
    def is_expired(self):
        """Check if the link has expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    @classmethod
    def generate_token(cls):
        """Generate a unique token for a new review link."""
        while True:
            token = uuid.uuid4().hex
            if not cls.objects.filter(token=token).exists():
                return token
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Review Link"
        verbose_name_plural = "Review Links"


class FacebookEvent(models.Model):
    """
    Model to store Facebook events for caching and display.
    SPEC_05 Group B Task 6 - Local storage for Facebook events.
    """
    
    # Facebook event data
    facebook_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Timing information
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    formatted_date = models.CharField(max_length=50, blank=True)
    formatted_time = models.CharField(max_length=20, blank=True)
    
    # Media and links
    cover_photo_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField()
    
    # Event details
    location_name = models.CharField(max_length=200, blank=True)
    location_address = models.TextField(blank=True)
    
    # Meta information
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.formatted_date}"
    
    def get_short_description(self, max_length: int = 150) -> str:
        """Get truncated description for display."""
        if len(self.description) <= max_length:
            return self.description
        return self.description[:max_length-3] + '...'
    
    def is_future_event(self) -> bool:
        """Check if event is in the future."""
        return self.start_time > timezone.now()
    
    def get_time_until_event(self) -> str:
        """Get human-readable time until event."""
        if not self.is_future_event():
            return "Past event"
        
        time_diff = self.start_time - timezone.now()
        days = time_diff.days
        
        if days == 0:
            return "Today"
        elif days == 1:
            return "Tomorrow"
        elif days < 7:
            return f"In {days} days"
        elif days < 30:
            weeks = days // 7
            return f"In {weeks} week{'s' if weeks > 1 else ''}"
        else:
            months = days // 30
            return f"In {months} month{'s' if months > 1 else ''}"
    
    @classmethod
    def get_upcoming_events(cls, limit: int = 5):
        """Get upcoming Facebook events ordered by start time."""
        return cls.objects.filter(
            is_active=True,
            start_time__gt=timezone.now()
        ).order_by('start_time')[:limit]
    
    @classmethod
    def get_featured_events(cls, limit: int = 3):
        """Get featured upcoming events."""
        return cls.objects.filter(
            is_active=True,
            featured=True,
            start_time__gt=timezone.now()
        ).order_by('order', 'start_time')[:limit]
    
    class Meta:
        ordering = ['start_time']
        verbose_name = "Facebook Event"
        verbose_name_plural = "Facebook Events"
        indexes = [
            models.Index(fields=['start_time', 'is_active']),
            models.Index(fields=['featured', 'start_time']),
        ]


class ContactSubmission(models.Model):
    """
    Model to store contact form submissions.
    SPEC_05 Group B Task 10 - Comprehensive email notifications system.
    """
    
    INTEREST_CHOICES = [
        ('classes', 'Group Classes'),
        ('private_lesson', 'Private Lessons'),
        ('workshop', 'Workshops'),
        ('events', 'Events & Performances'),
        ('choreography', 'Choreography Services'),
        ('general', 'General Inquiry'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('responded', 'Responded'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Contact Information
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Inquiry Details
    interest = models.CharField(max_length=20, choices=INTEREST_CHOICES)
    message = models.TextField()
    
    # Administrative Fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    source = models.CharField(max_length=50, default='website', help_text="Where the contact came from")
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, help_text="Internal notes for staff")
    
    # Email Tracking
    admin_notification_sent = models.BooleanField(default=False)
    auto_reply_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.get_interest_display()} ({self.get_status_display()})"
    
    def get_urgency_score(self):
        """Calculate urgency score for prioritization."""
        score = 0
        
        # Priority weight
        priority_weights = {'low': 1, 'normal': 2, 'high': 3, 'urgent': 4}
        score += priority_weights.get(self.priority, 2) * 10
        
        # Time since creation (older = more urgent)
        age_hours = (timezone.now() - self.created_at).total_seconds() / 3600
        if age_hours > 24:
            score += 5
        elif age_hours > 8:
            score += 3
        
        # Interest type weight (private lessons = higher priority)
        if self.interest in ['private_lesson', 'choreography']:
            score += 5
        
        return score
    
    def mark_responded(self):
        """Mark this contact as responded to."""
        self.status = 'responded'
        self.responded_at = timezone.now()
        self.save(update_fields=['status', 'responded_at'])
    
    @classmethod
    def get_pending_count(cls):
        """Get count of pending contacts."""
        return cls.objects.filter(status__in=['new', 'in_progress']).count()
    
    @classmethod
    def get_recent_inquiries(cls, days=7):
        """Get recent inquiries for dashboard."""
        since = timezone.now() - timedelta(days=days)
        return cls.objects.filter(created_at__gte=since).order_by('-created_at')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['created_at', 'status']),
            models.Index(fields=['interest', 'status']),
        ]


class BookingConfirmation(models.Model):
    """
    Model to store booking confirmations for email notifications.
    SPEC_05 Group B Task 10 - Booking confirmation emails.
    """
    
    BOOKING_TYPE_CHOICES = [
        ('class', 'Group Class'),
        ('private_lesson', 'Private Lesson'),
        ('workshop', 'Workshop'),
        ('package', 'Class Package'),
        ('event', 'Special Event'),
    ]
    
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending Payment'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    # Booking Information
    booking_id = models.CharField(max_length=20, unique=True, db_index=True)
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPE_CHOICES)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    
    # Class/Service Details
    class_name = models.CharField(max_length=100)
    instructor_name = models.CharField(max_length=100, blank=True)
    booking_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    location = models.CharField(max_length=200, default="Avalon Ballroom, Boulder, CO")
    
    # Pricing
    price = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # Status and Notes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    special_instructions = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    # External Integration
    calendly_event_id = models.CharField(max_length=100, blank=True)
    google_calendar_id = models.CharField(max_length=100, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Email Tracking
    confirmation_email_sent = models.BooleanField(default=False)
    reminder_email_sent = models.BooleanField(default=False)
    follow_up_email_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.booking_id} - {self.customer_name} ({self.class_name})"
    
    def get_booking_datetime_formatted(self):
        """Get formatted booking date and time."""
        return self.booking_date.strftime('%A, %B %d, %Y at %I:%M %p')
    
    def get_booking_date_only(self):
        """Get formatted booking date only."""
        return self.booking_date.strftime('%A, %B %d, %Y')
    
    def get_booking_time_only(self):
        """Get formatted booking time only."""
        return self.booking_date.strftime('%I:%M %p')
    
    def is_upcoming(self):
        """Check if booking is in the future."""
        return self.booking_date > timezone.now()
    
    def get_time_until_booking(self):
        """Get human-readable time until booking."""
        if not self.is_upcoming():
            return "Past booking"
        
        time_diff = self.booking_date - timezone.now()
        hours = time_diff.total_seconds() / 3600
        
        if hours < 1:
            minutes = int(time_diff.total_seconds() / 60)
            return f"In {minutes} minutes"
        elif hours < 24:
            return f"In {int(hours)} hours"
        else:
            days = time_diff.days
            return f"In {days} days"
    
    def generate_booking_id(self):
        """Generate a unique booking ID."""
        if not self.booking_id:
            prefix = self.booking_type[:3].upper()
            timestamp = timezone.now().strftime('%Y%m%d%H%M')
            counter = BookingConfirmation.objects.filter(
                booking_id__startswith=f"{prefix}{timestamp[:8]}"
            ).count() + 1
            self.booking_id = f"{prefix}{timestamp}{counter:02d}"
    
    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.generate_booking_id()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_upcoming_bookings(cls, days=7):
        """Get upcoming bookings."""
        end_date = timezone.now() + timedelta(days=days)
        return cls.objects.filter(
            booking_date__gte=timezone.now(),
            booking_date__lte=end_date,
            status='confirmed'
        ).order_by('booking_date')
    
    @classmethod
    def get_todays_bookings(cls):
        """Get today's bookings."""
        today = timezone.now().date()
        return cls.objects.filter(
            booking_date__date=today,
            status='confirmed'
        ).order_by('booking_date')
    
    class Meta:
        ordering = ['-booking_date']
        verbose_name = "Booking Confirmation"
        verbose_name_plural = "Booking Confirmations"
        indexes = [
            models.Index(fields=['booking_date', 'status']),
            models.Index(fields=['customer_email', 'status']),
            models.Index(fields=['booking_type', 'booking_date']),
        ]


class RSVPSubmission(models.Model):
    """
    Model to store RSVP submissions for Pastio.fun integration.
    SPEC_05 Group B Task 7 - Pastio.fun events integration.
    """
    
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    SOURCE_CHOICES = [
        ('pastio', 'Pastio.fun'),
        ('website', 'Website Direct'),
        ('facebook', 'Facebook Event'),
        ('instagram', 'Instagram'),
        ('other', 'Other'),
    ]
    
    # RSVP Information
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Class Information
    class_id = models.CharField(max_length=50, help_text="Internal class identifier")
    class_name = models.CharField(max_length=100)
    
    # RSVP Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='pastio')
    notifications_enabled = models.BooleanField(default=True, help_text="Send reminders and updates")
    
    # External Integration
    pastio_id = models.CharField(max_length=100, blank=True, null=True, help_text="Pastio.fun RSVP ID")
    facebook_event_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional Info
    special_requirements = models.TextField(blank=True, help_text="Dietary restrictions, accessibility needs, etc.")
    plus_one = models.BooleanField(default=False, help_text="Bringing a plus one")
    plus_one_name = models.CharField(max_length=100, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attended = models.BooleanField(null=True, blank=True, help_text="Whether they actually attended")
    
    # Admin Notes
    admin_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.class_name} ({self.get_status_display()})"
    
    def get_display_name(self):
        """Get name for display, including plus one if applicable."""
        if self.plus_one and self.plus_one_name:
            return f"{self.name} +1 ({self.plus_one_name})"
        elif self.plus_one:
            return f"{self.name} +1"
        return self.name
    
    def get_party_size(self):
        """Get total party size."""
        return 2 if self.plus_one else 1
    
    def get_next_class_date(self):
        """Get the next occurrence of this class."""
        from datetime import datetime, timedelta
        today = datetime.now().date()
        days_ahead = 6 - today.weekday()  # Sunday is 6
        if days_ahead <= 0:
            days_ahead += 7
        return today + timedelta(days=days_ahead)
    
    def get_class_time(self):
        """Get the time for this class."""
        class_times = {
            'scf-choreo': '12:00 PM - 1:00 PM',
            'pasos-basicos': '1:00 PM - 2:00 PM',
            'casino-royale': '2:00 PM - 3:00 PM'
        }
        return class_times.get(self.class_id, 'TBD')
    
    def is_upcoming(self):
        """Check if the RSVP is for an upcoming class."""
        next_class = self.get_next_class_date()
        from datetime import datetime
        return next_class >= datetime.now().date()
    
    def can_cancel(self):
        """Check if RSVP can still be cancelled."""
        return self.status == 'confirmed' and self.is_upcoming()
    
    def cancel(self, reason=''):
        """Cancel this RSVP."""
        if self.can_cancel():
            self.status = 'cancelled'
            if reason:
                self.admin_notes = f"Cancelled: {reason}\n{self.admin_notes}"
            self.save(update_fields=['status', 'admin_notes', 'updated_at'])
            return True
        return False
    
    @classmethod
    def get_class_counts(cls, date=None):
        """Get RSVP counts for each class on a given date."""
        from datetime import datetime, timedelta
        
        if date is None:
            # Get next Sunday
            today = datetime.now().date()
            days_ahead = 6 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            date = today + timedelta(days=days_ahead)
        
        # Count confirmed RSVPs for each class
        counts = {}
        class_ids = ['scf-choreo', 'pasos-basicos', 'casino-royale']
        
        for class_id in class_ids:
            count = cls.objects.filter(
                class_id=class_id,
                status='confirmed',
                created_at__date__gte=date - timedelta(days=7),  # Recent RSVPs
                created_at__date__lte=date
            ).count()
            
            # Add plus ones
            plus_ones = cls.objects.filter(
                class_id=class_id,
                status='confirmed',
                plus_one=True,
                created_at__date__gte=date - timedelta(days=7),
                created_at__date__lte=date
            ).count()
            
            counts[class_id] = count + plus_ones
        
        return counts
    
    @classmethod
    def get_upcoming_rsvps(cls, class_id=None, limit=None):
        """Get upcoming RSVPs, optionally filtered by class."""
        queryset = cls.objects.filter(
            status='confirmed'
        ).order_by('-created_at')
        
        if class_id:
            queryset = queryset.filter(class_id=class_id)
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    @classmethod
    def get_weekly_stats(cls):
        """Get weekly RSVP statistics."""
        from datetime import datetime, timedelta
        from django.db.models import Count
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        stats = {
            'total_rsvps': cls.objects.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            ).count(),
            'confirmed_rsvps': cls.objects.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date,
                status='confirmed'
            ).count(),
            'by_class': {},
            'by_source': {}
        }
        
        # Count by class
        by_class = cls.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='confirmed'
        ).values('class_id', 'class_name').annotate(count=Count('id'))
        
        for item in by_class:
            stats['by_class'][item['class_id']] = {
                'name': item['class_name'],
                'count': item['count']
            }
        
        # Count by source
        by_source = cls.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='confirmed'
        ).values('source').annotate(count=Count('id'))
        
        for item in by_source:
            stats['by_source'][item['source']] = item['count']
        
        return stats
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "RSVP Submission"
        verbose_name_plural = "RSVP Submissions"
        unique_together = [['email', 'class_id', 'created_at']]  # Prevent duplicate RSVPs
        indexes = [
            models.Index(fields=['class_id', 'status']),
            models.Index(fields=['created_at', 'status']),
            models.Index(fields=['email', 'class_id']),
            models.Index(fields=['pastio_id']),
        ]