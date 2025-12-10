"""
Optimized views with database performance enhancements.
SPEC_06 Group B Task 6 - Database query and performance optimization.

This module contains optimized versions of views with:
- Eliminated N+1 queries
- Optimized select_related() and prefetch_related()
- Enhanced caching strategies
- Query performance monitoring
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page, cache_control
from django.views.decorators.vary import vary_on_headers
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Prefetch, Count, Avg, F, Case, When, IntegerField, CharField
from django.utils import timezone
from datetime import timedelta
import json
import logging

from .models import (
    Class, Testimonial, Instructor, MediaGallery, FacebookEvent, 
    ContactSubmission, BookingConfirmation, SpotifyPlaylist, RSVPSubmission
)
from .forms import TestimonialForm, ContactForm, BookingForm
from .db_optimization import (
    QueryOptimizer, CacheManager, monitor_db_performance,
    get_optimized_testimonials, get_optimized_classes, get_testimonial_stats
)
from .utils.email_notifications import (
    send_admin_notification_email, send_thank_you_email,
    send_contact_admin_notification_email, send_contact_auto_reply_email,
    send_booking_confirmation_email, send_booking_admin_notification_email,
    test_email_configuration
)
from .utils.google_reviews import submit_testimonial_to_google
from .utils.facebook_events import get_facebook_events

logger = logging.getLogger(__name__)

@cache_page(60 * 15)  # Cache for 15 minutes
@cache_control(max_age=900)  # Browser cache for 15 minutes
@monitor_db_performance
def home_view_optimized(request):
    """
    Optimized home view with enhanced database performance.
    """
    # Static upcoming events data
    upcoming_events = [
        {
            'title': 'SCF Choreo Team',
            'date': 'Every Sunday',
            'time': '12:00 PM - 1:00 PM',
            'location': 'Avalon Ballroom (North Lobby)',
            'description': 'Join our choreography team for an intensive dance training session focusing on advanced Cuban salsa techniques and performance routines.',
            'price': 20
        },
        {
            'title': 'Pasos Básicos',
            'date': 'Every Sunday',
            'time': '1:00 PM - 2:00 PM',
            'location': 'Avalon Ballroom (Tango Room)',
            'description': 'Pasos Básicos will focus on basic cuban salsa footwork, turn patterns, and a little bit of afro-cuban in salsa.',
            'price': 20
        },
        {
            'title': 'Casino Royale',
            'date': 'Every Sunday',
            'time': '2:00 PM - 3:00 PM',
            'location': 'Avalon Ballroom (Tango Room)',
            'description': 'Take your casino dancing to the next level with this class. We focus on the building blocks of Casino dancing.',
            'price': 20
        }
    ]
    
    # Get featured testimonials with optimized caching
    carousel_testimonials = get_optimized_testimonials(
        status='approved',
        featured=True,
        limit=6
    )
    
    # If not enough featured testimonials, get recent approved ones
    if len(carousel_testimonials) < 3:
        carousel_testimonials = get_optimized_testimonials(
            status='approved',
            limit=6
        )
    
    # Get Spotify playlists with optimized query and caching
    cache_key = 'home_spotify_playlists_v2'
    spotify_playlists = cache.get(cache_key)
    if spotify_playlists is None:
        spotify_playlists = list(
            SpotifyPlaylist.objects.filter(is_active=True)
            .only('id', 'class_type', 'title', 'description', 'spotify_embed_url', 'theme_color')
            .order_by('order', 'class_type')[:6]
        )
        cache.set(cache_key, spotify_playlists, CacheManager.CACHE_TIMEOUTS['long'])
    
    return render(request, 'home.html', {
        'upcoming_events': upcoming_events,
        'carousel_testimonials': carousel_testimonials,
        'spotify_playlists': spotify_playlists
    })

@cache_page(60 * 30)  # Cache for 30 minutes
@cache_control(max_age=1800)
@monitor_db_performance
def schedule_view_optimized(request):
    """
    Optimized schedule view with enhanced database performance.
    """
    # Get Sunday classes with optimized query and caching
    sunday_classes = get_optimized_classes(day_of_week='Sunday')
    
    # Get Facebook events with optimized fallback to database
    facebook_events = []
    try:
        # Try to get from API with caching (6 hour cache)
        facebook_events = get_facebook_events(limit=5, use_cache=True)
        logger.info(f"Loaded {len(facebook_events)} Facebook events for schedule page")
        
        # Fallback to database if API fails - optimized query
        if not facebook_events:
            cache_key = 'schedule_facebook_events'
            facebook_events = cache.get(cache_key)
            
            if facebook_events is None:
                db_events = FacebookEvent.objects.filter(
                    is_active=True,
                    start_time__gt=timezone.now()
                ).only(
                    'facebook_id', 'name', 'description', 'formatted_date',
                    'formatted_time', 'cover_photo_url', 'facebook_url'
                ).order_by('start_time')[:5]
                
                facebook_events = []
                for event in db_events:
                    facebook_events.append({
                        'id': event.facebook_id,
                        'name': event.name,
                        'description': event.get_short_description(),
                        'formatted_date': event.formatted_date,
                        'formatted_time': event.formatted_time,
                        'cover_photo': event.cover_photo_url,
                        'facebook_url': event.facebook_url
                    })
                
                cache.set(cache_key, facebook_events, CacheManager.CACHE_TIMEOUTS['medium'])
            
            logger.info(f"Loaded {len(facebook_events)} Facebook events from database")
            
    except Exception as e:
        logger.warning(f"Error loading Facebook events: {str(e)}")
        facebook_events = []
    
    return render(request, 'schedule.html', {
        'sunday_classes': sunday_classes,
        'facebook_events': facebook_events
    })

@cache_page(60 * 30)  # Cache for 30 minutes
@cache_control(max_age=1800)
@monitor_db_performance
def resources_view_optimized(request):
    """
    Optimized resources view with enhanced database performance.
    """
    # Get all active Spotify playlists with optimized caching
    cache_key = 'resources_spotify_playlists_v2'
    spotify_playlists = cache.get(cache_key)
    
    if spotify_playlists is None:
        spotify_playlists = list(
            SpotifyPlaylist.objects.filter(is_active=True)
            .only('id', 'class_type', 'title', 'description', 'spotify_embed_url', 'theme_color')
            .order_by('order', 'class_type')
        )
        cache.set(cache_key, spotify_playlists, CacheManager.CACHE_TIMEOUTS['long'])
    
    # Group playlists by type for better organization
    main_class_playlists = []
    practice_playlists = []
    
    for playlist in spotify_playlists:
        if playlist.class_type in ['choreo_team', 'pasos_basicos', 'casino_royale']:
            main_class_playlists.append(playlist)
        else:
            practice_playlists.append(playlist)
    
    context = {
        'main_class_playlists': main_class_playlists,
        'practice_playlists': practice_playlists,
        'all_playlists': spotify_playlists,
        'page_title': 'Dance Resources & Playlists',
    }
    
    return render(request, 'resources.html', context)

@monitor_db_performance
def display_testimonials_optimized(request):
    """
    Optimized testimonials display with enhanced database performance.
    """
    # Get filter parameters from request
    rating_filter = request.GET.get('rating')
    class_filter = request.GET.get('class_type')
    
    # Build cache key based on filters
    cache_key = f'testimonials_display_{rating_filter}_{class_filter}'
    testimonials = cache.get(cache_key)
    
    if testimonials is None:
        # Start with optimized base query
        testimonials = Testimonial.objects.filter(
            status='approved',
            published_at__isnull=False
        ).only(
            'id', 'student_name', 'rating', 'content', 'class_type',
            'published_at', 'photo', 'video_url', 'featured'
        ).order_by('-published_at')
        
        # Apply rating filter if provided
        if rating_filter and rating_filter.isdigit():
            rating_value = int(rating_filter)
            if 1 <= rating_value <= 5:
                testimonials = testimonials.filter(rating=rating_value)
        
        # Apply class type filter if provided
        if class_filter:
            testimonials = testimonials.filter(class_type=class_filter)
        
        # Convert to list and cache
        testimonials = list(testimonials)
        cache.set(cache_key, testimonials, CacheManager.CACHE_TIMEOUTS['medium'])
    
    # Get unique class types with optimized query and caching
    class_types_cache_key = 'testimonials_class_types'
    class_types = cache.get(class_types_cache_key)
    if class_types is None:
        class_types = list(
            Testimonial.objects.filter(status='approved')
            .values_list('class_type', flat=True)
            .distinct()
            .order_by('class_type')
        )
        cache.set(class_types_cache_key, class_types, CacheManager.CACHE_TIMEOUTS['long'])
    
    # Get testimonial statistics with optimized aggregation
    stats = get_testimonial_stats()
    average_rating = round(stats['average_rating'] or 0, 1)
    total_reviews = stats['total_reviews']
    
    context = {
        'testimonials': testimonials,
        'class_types': class_types,
        'selected_rating': rating_filter,
        'selected_class': class_filter,
        'average_rating': average_rating,
        'total_reviews': total_reviews,
        'page_title': 'Student Testimonials',
    }
    
    return render(request, 'testimonials/display.html', context)

@cache_page(60 * 60)  # Cache for 1 hour
@cache_control(max_age=3600)
@monitor_db_performance
def instructor_list_optimized(request):
    """
    Optimized instructor list with enhanced database performance.
    """
    import json
    
    # Use cached instructors list for performance
    cache_key = 'instructor_list_data_v2'
    instructors_data = cache.get(cache_key)
    
    if instructors_data is None:
        instructors = list(
            Instructor.objects.only(
                'id', 'name', 'bio', 'photo_url', 'video_url',
                'instagram', 'specialties'
            ).order_by('name')
        )
        
        # Cache instructors data for 1 hour
        cache.set(cache_key, instructors, CacheManager.CACHE_TIMEOUTS['long'])
        instructors_data = instructors
    
    # Parse specialties for each instructor to pass to template
    instructors_with_specialties = []
    for instructor in instructors_data:
        try:
            specialties_list = json.loads(instructor.specialties)
        except (json.JSONDecodeError, TypeError):
            # Fallback to treating as comma-separated string
            specialties_list = [s.strip() for s in instructor.specialties.split(',') if s.strip()]
        
        instructors_with_specialties.append({
            'instructor': instructor,
            'specialties_list': specialties_list
        })
    
    context = {
        'instructors': instructors_data,
        'instructors_with_specialties': instructors_with_specialties,
        'page_title': 'Our Instructors',
    }
    
    return render(request, 'instructors/list.html', context)

@monitor_db_performance
def instructor_detail_optimized(request, instructor_id):
    """
    Optimized instructor detail with enhanced database performance.
    """
    instructor = get_object_or_404(
        Instructor.objects.only(
            'id', 'name', 'bio', 'photo_url', 'video_url',
            'instagram', 'specialties'
        ),
        id=instructor_id
    )
    
    # Parse specialties from JSON string for template display
    import json
    try:
        specialties_list = json.loads(instructor.specialties)
    except (json.JSONDecodeError, TypeError):
        # Fallback to treating as comma-separated string
        specialties_list = [s.strip() for s in instructor.specialties.split(',') if s.strip()]
    
    context = {
        'instructor': instructor,
        'specialties_list': specialties_list,
        'page_title': f'{instructor.name} - Instructor Profile',
    }
    
    return render(request, 'instructors/detail.html', context)

@vary_on_headers('Accept-Encoding')
@cache_control(max_age=1800)  # Browser cache for 30 minutes
@monitor_db_performance
def gallery_view_optimized(request):
    """
    Optimized gallery view with enhanced database performance.
    """
    from .utils.instagram_api import get_instagram_posts
    
    # Get filter parameters from request
    media_type_filter = request.GET.get('type', 'all')
    category_filter = request.GET.get('category', 'all')
    show_instagram = request.GET.get('instagram', 'true').lower() in ('true', '1', 'yes')
    
    # Build cache key based on filters
    cache_key = f'gallery_media_v2_{media_type_filter}_{category_filter}'
    media_items = cache.get(cache_key)
    
    if media_items is None:
        # Start with optimized base query - only select needed fields
        media_items = MediaGallery.objects.only(
            'id', 'title', 'media_type', 'category', 'file', 'url',
            'thumbnail', 'caption', 'order', 'is_featured', 'created_at',
            'instagram_id', 'instagram_permalink'
        )
        
        # Apply filters if provided
        if media_type_filter != 'all':
            media_items = media_items.filter(media_type=media_type_filter)
        
        if category_filter != 'all':
            media_items = media_items.filter(category=category_filter)
        
        # Order by the order field and creation date
        media_items = list(media_items.order_by('order', '-created_at'))
        
        # Cache for 15 minutes
        cache.set(cache_key, media_items, CacheManager.CACHE_TIMEOUTS['medium'])
    
    # Get Instagram posts if enabled
    instagram_posts = []
    if show_instagram:
        try:
            instagram_posts = get_instagram_posts(limit=8, use_cache=True)
        except Exception as e:
            logger.warning(f"Failed to load Instagram posts: {str(e)}")
    
    # Get unique categories with optimized query and caching
    categories_cache_key = 'gallery_categories'
    categories = cache.get(categories_cache_key)
    if categories is None:
        categories = list(
            MediaGallery.objects.values_list('category', flat=True)
            .distinct()
            .order_by('category')
        )
        cache.set(categories_cache_key, categories, CacheManager.CACHE_TIMEOUTS['long'])
    
    # Convert category values to display names
    category_choices = []
    for cat in categories:
        for choice in MediaGallery.CATEGORY_CHOICES:
            if choice[0] == cat:
                category_choices.append(choice)
                break
    
    # Get counts with optimized aggregation query and caching
    counts_cache_key = 'gallery_media_counts'
    media_counts = cache.get(counts_cache_key)
    if media_counts is None:
        media_counts = MediaGallery.objects.aggregate(
            photo_count=Count(Case(
                When(media_type='image', then=1),
                output_field=IntegerField(),
            )),
            video_count=Count(Case(
                When(media_type='video', then=1),
                output_field=IntegerField(),
            ))
        )
        cache.set(counts_cache_key, media_counts, CacheManager.CACHE_TIMEOUTS['medium'])
    
    photo_count = media_counts['photo_count']
    video_count = media_counts['video_count']
    instagram_count = len(instagram_posts)
    
    context = {
        'media_items': media_items,
        'instagram_posts': instagram_posts,
        'category_choices': category_choices,
        'selected_type': media_type_filter,
        'selected_category': category_filter,
        'show_instagram': show_instagram,
        'photo_count': photo_count,
        'video_count': video_count,
        'instagram_count': instagram_count,
        'total_count': photo_count + video_count,
        'page_title': 'Media Gallery',
    }
    
    return render(request, 'gallery/index.html', context)

@require_http_methods(["GET"])
@monitor_db_performance
def get_rsvp_counts_optimized(request):
    """
    Optimized RSVP counts with enhanced database performance.
    """
    try:
        # Cache key for RSVP counts
        cache_key = 'rsvp_counts_current_v2'
        counts = cache.get(cache_key)
        
        if counts is None:
            # Get actual counts from database with optimized query
            from datetime import datetime, timedelta
            
            # Get next Sunday
            today = datetime.now().date()
            days_ahead = 6 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_sunday = today + timedelta(days=days_ahead)
            
            # Count RSVPs for each class with single aggregated query
            class_ids = ['scf-choreo', 'pasos-basicos', 'casino-royale']
            
            # Use aggregation to get all counts in one query
            rsvp_data = RSVPSubmission.objects.filter(
                class_id__in=class_ids,
                status='confirmed',
                created_at__date__gte=today - timedelta(days=7)
            ).values('class_id').annotate(
                count=Count('id')
            )
            
            # Convert to dictionary
            counts = {}
            for item in rsvp_data:
                counts[item['class_id']] = item['count']
            
            # Add baseline counts for classes not in results
            baseline_counts = {
                'scf-choreo': 8,
                'pasos-basicos': 12,
                'casino-royale': 15
            }
            
            for class_id in class_ids:
                counts[class_id] = counts.get(class_id, 0) + baseline_counts.get(class_id, 0)
            
            # Cache for 5 minutes
            cache.set(cache_key, counts, CacheManager.CACHE_TIMEOUTS['short'])
        
        return JsonResponse({
            'success': True,
            'counts': counts,
            'updated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting RSVP counts: {str(e)}")
        return JsonResponse({
            'error': 'Failed to get RSVP counts'
        }, status=500)

# Additional performance monitoring endpoints

@require_http_methods(["GET"])
def db_performance_stats(request):
    """
    Get database performance statistics.
    Only available in debug mode for security.
    """
    if not settings.DEBUG:
        from django.http import Http404
        raise Http404("Performance stats not available in production")
    
    from django.db import connection
    
    # Get query statistics
    query_count = len(connection.queries)
    
    # Calculate total query time
    total_time = sum(float(query['time']) for query in connection.queries)
    
    # Find slow queries
    slow_queries = [
        {
            'sql': query['sql'][:100] + '...' if len(query['sql']) > 100 else query['sql'],
            'time': float(query['time'])
        }
        for query in connection.queries
        if float(query['time']) > 0.1  # Queries taking more than 100ms
    ]
    
    stats = {
        'total_queries': query_count,
        'total_time': round(total_time, 3),
        'slow_queries': slow_queries,
        'average_time': round(total_time / max(query_count, 1), 3)
    }
    
    return JsonResponse(stats)

@require_http_methods(["POST"])
def clear_cache(request):
    """
    Clear application cache.
    Only available in debug mode for security.
    """
    if not settings.DEBUG:
        from django.http import Http404
        raise Http404("Cache management not available in production")
    
    try:
        cache.clear()
        logger.info("Application cache cleared")
        return JsonResponse({'success': True, 'message': 'Cache cleared successfully'})
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return JsonResponse({'error': 'Failed to clear cache'}, status=500)