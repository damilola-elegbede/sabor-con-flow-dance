from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page, cache_control, never_cache
from django.views.decorators.vary import vary_on_headers
from django.views.decorators.http import etag, condition
from django.core.cache import cache
from .utils.cache_utils import cache_manager, get_cache_headers, CacheBusting
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Prefetch, Count, Avg, F, Case, When, IntegerField, CharField
from .models import Class, Testimonial, Instructor, MediaGallery, FacebookEvent, ContactSubmission, BookingConfirmation, SpotifyPlaylist, RSVPSubmission
from .forms import TestimonialForm, ContactForm, BookingForm
from .utils.email_notifications import (
    send_admin_notification_email, send_thank_you_email,
    send_contact_admin_notification_email, send_contact_auto_reply_email,
    send_booking_confirmation_email, send_booking_admin_notification_email,
    test_email_configuration
)
from .utils.google_reviews import submit_testimonial_to_google
from .utils.facebook_events import get_facebook_events
import json
import logging

logger = logging.getLogger(__name__)

@cache_page(60 * 60, cache='page_cache')  # Cache for 1 hour
@cache_control(max_age=3600, s_maxage=86400)  # Browser cache 1hr, CDN cache 24hr
@vary_on_headers('User-Agent', 'Accept-Encoding')
def home_view(request):
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
    
    # Get featured testimonials for carousel with optimized query
    carousel_testimonials = cache.get('home_carousel_testimonials')
    if carousel_testimonials is None:
        carousel_testimonials = Testimonial.objects.filter(
            status='approved',
            featured=True
        ).exclude(
            published_at__isnull=True
        ).select_related().order_by('-published_at')[:6]  # Get up to 6 featured testimonials
        
        # If not enough featured testimonials, get recent approved ones
        if carousel_testimonials.count() < 3:
            carousel_testimonials = Testimonial.objects.filter(
                status='approved'
            ).exclude(
                published_at__isnull=True
            ).select_related().order_by('-published_at')[:6]
        
        # Convert to list to avoid repeated database hits
        carousel_testimonials = list(carousel_testimonials)
        # Cache for 30 minutes
        cache.set('home_carousel_testimonials', carousel_testimonials, 60 * 30)
    
    # Get Spotify playlists for resources section
    spotify_playlists = cache.get('home_spotify_playlists')
    if spotify_playlists is None:
        spotify_playlists = list(SpotifyPlaylist.get_active_playlists()[:6])  # Get up to 6 playlists
        # Cache for 1 hour
        cache.set('home_spotify_playlists', spotify_playlists, 60 * 60)
    
    return render(request, 'home.html', {
        'upcoming_events': upcoming_events,
        'carousel_testimonials': carousel_testimonials,
        'spotify_playlists': spotify_playlists
    })

@cache_page(60 * 30)  # Cache for 30 minutes
@cache_control(max_age=1800)  # Browser cache for 30 minutes
def events(request):
    # Static events data
    events = [
        {
            'title': 'SCF Choreo Team',
            'date': 'Every Sunday',
            'time': '12:00 PM - 1:00 PM',
            'location': 'Avalon Ballroom (North Lobby)',
            'description': 'Join our choreography team for an intensive dance training session focusing on advanced Cuban salsa techniques and performance routines.',
            'price': 20,
            'monthly_price': 70
        },
        {
            'title': 'Pasos Básicos',
            'date': 'Every Sunday',
            'time': '1:00 PM - 2:00 PM',
            'location': 'Avalon Ballroom (Tango Room)',
            'description': 'Pasos Básicos will focus on basic cuban salsa footwork, turn patterns, and a little bit of afro-cuban in salsa.',
            'price': 20,
            'monthly_price': 60
        },
        {
            'title': 'Casino Royale',
            'date': 'Every Sunday',
            'time': '2:00 PM - 3:00 PM',
            'location': 'Avalon Ballroom (Tango Room)',
            'description': 'Take your casino dancing to the next level with this class. We focus on the building blocks of Casino dancing.',
            'price': 20,
            'monthly_price': 60
        }
    ]
    return render(request, 'events.html', {'events': events})

@cache_page(60 * 60)  # Cache for 1 hour
@cache_control(max_age=3600)  # Browser cache for 1 hour
def pricing(request):
    # Pricing data for the pricing page
    pricing_data = {
        'drop_in': {
            'price': 20,
            'name': 'Drop-in Class',
            'description': 'Perfect for trying out our classes',
            'features': [
                'Single class access',
                'No commitment',
                'All skill levels welcome',
                'Meet new people'
            ]
        },
        'package_4': {
            'price': 70,
            'name': '4-Class Package',
            'description': 'Our most popular option for regular dancers',
            'features': [
                '4 classes included',
                'Valid for 2 months',
                'Save $10 vs drop-in',
                'Most popular choice'
            ],
            'is_popular': True,
            'savings': 10,
            'savings_percentage': 12.5
        },
        'package_8': {
            'price': 120,
            'name': '8-Class Package',
            'description': 'Best value for dedicated dancers',
            'features': [
                '8 classes included',
                'Valid for 3 months',
                'Save $40 vs drop-in',
                'Best value option'
            ],
            'savings': 40,
            'savings_percentage': 25
        },
        'private_lessons': {
            'price_min': 75,
            'price_max': 120,
            'name': 'Private Lessons',
            'description': 'One-on-one personalized instruction',
            'features': [
                'Personalized instruction',
                'Flexible scheduling',
                'Accelerated learning',
                'Custom choreography'
            ]
        }
    }
    
    return render(request, 'pricing.html', {'pricing_data': pricing_data})

def private_lessons(request):
    return render(request, 'private_lessons.html')

@cache_page(60 * 30)  # Cache for 30 minutes
@cache_control(max_age=1800)  # Browser cache for 30 minutes
def resources_view(request):
    """
    Display the resources page with Spotify playlists for each class type.
    SPEC_05 Group C Task 8 - Spotify playlists integration.
    """
    # Get all active Spotify playlists
    spotify_playlists = cache.get('resources_spotify_playlists')
    if spotify_playlists is None:
        spotify_playlists = list(SpotifyPlaylist.get_active_playlists())
        # Cache for 1 hour
        cache.set('resources_spotify_playlists', spotify_playlists, 60 * 60)
    
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

@never_cache
@csrf_protect
@require_http_methods(["GET", "POST"])
def contact(request):
    """
    Handle contact form submissions with email notifications.
    SPEC_05 Group B Task 10 - Comprehensive email notifications system.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                # Save contact submission
                contact_submission = form.save()
                
                # Send admin notification email
                try:
                    admin_email_success = send_contact_admin_notification_email(contact_submission)
                    if admin_email_success:
                        logger.info(f"Contact admin notification sent for submission {contact_submission.id}")
                    else:
                        logger.warning(f"Failed to send contact admin notification for submission {contact_submission.id}")
                except Exception as e:
                    logger.error(f"Error sending contact admin notification: {e}")
                
                # Send auto-reply email to submitter
                try:
                    auto_reply_success = send_contact_auto_reply_email(contact_submission)
                    if auto_reply_success:
                        logger.info(f"Contact auto-reply sent to {contact_submission.email}")
                    else:
                        logger.warning(f"Failed to send contact auto-reply to {contact_submission.email}")
                except Exception as e:
                    logger.error(f"Error sending contact auto-reply: {e}")
                
                messages.success(
                    request,
                    f'Thank you for contacting us, {contact_submission.name}! '
                    f'We\'ve received your inquiry about {contact_submission.get_interest_display().lower()} '
                    f'and will respond within 48 hours.'
                )
                
                # Redirect to prevent form resubmission
                return redirect('core:contact_success')
                
            except Exception as e:
                messages.error(
                    request,
                    'There was an error submitting your message. Please try again.'
                )
                logger.error(f"Error saving contact submission: {e}")
        else:
            messages.error(
                request,
                'Please correct the errors below and try again.'
            )
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'page_title': 'Contact Us',
        # Google Maps configuration - SPEC_05 Group D Task 11
        'ENABLE_GOOGLE_MAPS': getattr(settings, 'ENABLE_GOOGLE_MAPS', False),
        'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
        'GOOGLE_MAPS_ZOOM_LEVEL': getattr(settings, 'GOOGLE_MAPS_ZOOM_LEVEL', 16),
        'STUDIO_COORDINATES': getattr(settings, 'STUDIO_COORDINATES', {}),
        'BUSINESS_INFO': getattr(settings, 'BUSINESS_INFO', {}),
    }
    
    return render(request, 'contact.html', context)


def contact_success(request):
    """Display success page after contact form submission."""
    return render(request, 'contact_success.html', {
        'page_title': 'Thank You!',
    })


@never_cache
@csrf_protect
@require_http_methods(["GET", "POST"])
def create_booking(request):
    """
    Handle booking creation with email confirmations.
    SPEC_05 Group B Task 10 - Booking confirmation emails.
    """
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                # Save booking
                booking = form.save()
                
                # Send booking confirmation to customer
                try:
                    confirmation_success = send_booking_confirmation_email(booking)
                    if confirmation_success:
                        logger.info(f"Booking confirmation sent to {booking.customer_email} for booking {booking.booking_id}")
                    else:
                        logger.warning(f"Failed to send booking confirmation for booking {booking.booking_id}")
                except Exception as e:
                    logger.error(f"Error sending booking confirmation: {e}")
                
                # Send admin notification
                try:
                    admin_notification_success = send_booking_admin_notification_email(booking)
                    if admin_notification_success:
                        logger.info(f"Booking admin notification sent for booking {booking.booking_id}")
                    else:
                        logger.warning(f"Failed to send booking admin notification for booking {booking.booking_id}")
                except Exception as e:
                    logger.error(f"Error sending booking admin notification: {e}")
                
                messages.success(
                    request,
                    f'Booking confirmed! Your booking ID is {booking.booking_id}. '
                    f'A confirmation email has been sent to {booking.customer_email}.'
                )
                
                # Redirect to booking confirmation page
                return redirect('core:booking_success', booking_id=booking.booking_id)
                
            except Exception as e:
                messages.error(
                    request,
                    'There was an error processing your booking. Please try again.'
                )
                logger.error(f"Error saving booking: {e}")
        else:
            messages.error(
                request,
                'Please correct the errors below and try again.'
            )
    else:
        form = BookingForm()
    
    context = {
        'form': form,
        'page_title': 'Book a Class or Lesson',
    }
    
    return render(request, 'booking/create.html', context)


def booking_success(request, booking_id):
    """Display booking confirmation page."""
    booking = get_object_or_404(BookingConfirmation, booking_id=booking_id)
    
    context = {
        'booking': booking,
        'page_title': 'Booking Confirmed',
    }
    
    return render(request, 'booking/success.html', context)


@require_http_methods(["GET"])
def email_test(request):
    """
    Test email configuration and send test email.
    Only available in debug mode for security.
    """
    # Only allow access in debug mode
    if not settings.DEBUG:
        from django.http import Http404
        raise Http404("Test page not available in production")
    
    test_results = test_email_configuration()
    
    context = {
        'test_results': test_results,
        'page_title': 'Email Configuration Test',
    }
    
    return render(request, 'email_test.html', context)

@cache_page(60 * 30)  # Cache for 30 minutes
@cache_control(max_age=1800)
def schedule_view(request):
    """
    Display the schedule page with Sunday classes from the database.
    Fetches Class objects and passes them to the template.
    SPEC_05 Group B Task 6 - Enhanced with Facebook Events display.
    """
    # Fetch Sunday classes with optimized query and caching
    cache_key = 'schedule_sunday_classes'
    sunday_classes = cache.get(cache_key)
    if sunday_classes is None:
        sunday_classes = list(Class.objects.filter(
            day_of_week='Sunday'
        ).select_related('instructor').order_by('start_time'))
        # Cache for 1 hour
        cache.set(cache_key, sunday_classes, 60 * 60)
    
    # Fetch Facebook events for Special Events section
    facebook_events = []
    try:
        # Try to get from API with caching (6 hour cache)
        facebook_events = get_facebook_events(limit=5, use_cache=True)
        logger.info(f"Loaded {len(facebook_events)} Facebook events for schedule page")
        
        # Fallback to database if API fails
        if not facebook_events:
            db_events = FacebookEvent.get_upcoming_events(limit=5)
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
            logger.info(f"Loaded {len(facebook_events)} Facebook events from database")
            
    except Exception as e:
        logger.warning(f"Error loading Facebook events: {str(e)}")
        # Graceful fallback - no events shown
        facebook_events = []
    
    return render(request, 'schedule.html', {
        'sunday_classes': sunday_classes,
        'facebook_events': facebook_events
    })

@never_cache
@csrf_protect
@require_http_methods(["GET", "POST"])
def submit_testimonial(request):
    """
    Handle testimonial submission with proper validation and processing.
    GET: Display testimonial form
    POST: Process testimonial submission
    """
    initial_data = {}
    
    # Handle URL parameters for pre-filling form
    instructor_param = request.GET.get('instructor')
    class_param = request.GET.get('class')
    
    if instructor_param:
        initial_data['instructor_context'] = instructor_param.replace('-', ' ').title()
    
    if class_param:
        # Try to map class parameter to valid choice
        for choice in Testimonial.CLASS_TYPE_CHOICES:
            if choice[0] == class_param or choice[1].lower().replace(' ', '_') == class_param:
                initial_data['class_type'] = choice[0]
                break
    
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save testimonial with pending status
                testimonial = form.save(commit=False)
                testimonial.status = 'pending'
                testimonial.save()
                
                # Send admin notification email
                try:
                    admin_email_success = send_admin_notification_email(testimonial)
                    if admin_email_success:
                        print(f"Admin notification sent for testimonial {testimonial.id}")
                    else:
                        print(f"Failed to send admin notification for testimonial {testimonial.id}")
                except Exception as e:
                    # Log error but don't fail the submission
                    print(f"Error sending admin notification: {e}")
                
                # Send thank you email to submitter
                try:
                    thank_you_success = send_thank_you_email(testimonial)
                    if thank_you_success:
                        print(f"Thank you email sent to {testimonial.email}")
                    else:
                        print(f"Failed to send thank you email to {testimonial.email}")
                except Exception as e:
                    # Log error but don't fail the submission
                    print(f"Error sending thank you email: {e}")
                
                # Google Business API integration
                try:
                    google_success, google_error = submit_testimonial_to_google(testimonial)
                    if google_success:
                        print(f"Testimonial {testimonial.id} submitted to Google Business successfully")
                    else:
                        print(f"Failed to submit testimonial {testimonial.id} to Google Business: {google_error}")
                except Exception as e:
                    # Log error but don't fail the submission
                    print(f"Error integrating with Google Business: {e}")
                
                messages.success(
                    request, 
                    'Thank you for sharing your experience! Your testimonial has been submitted '
                    'and will be reviewed before being published.'
                )
                
                # Redirect to success page or back to form
                return redirect('core:testimonial_success')
                
            except Exception as e:
                messages.error(
                    request,
                    'There was an error submitting your testimonial. Please try again.'
                )
                print(f"Error saving testimonial: {e}")
        else:
            messages.error(
                request,
                'Please correct the errors below and try again.'
            )
    else:
        form = TestimonialForm(initial=initial_data)
    
    context = {
        'form': form,
        'page_title': 'Share Your Dance Journey',
    }
    
    return render(request, 'testimonials/submit.html', context)

def testimonial_success(request):
    """Display success page after testimonial submission."""
    return render(request, 'testimonials/success.html', {
        'page_title': 'Thank You!',
    })

def display_testimonials(request):
    """
    Display approved testimonials with filtering options.
    Shows testimonials in a masonry grid layout with rating and class type filters.
    """
    # Get filter parameters from request
    rating_filter = request.GET.get('rating')
    class_filter = request.GET.get('class_type')
    
    # Start with approved testimonials ordered by published_at desc
    testimonials = Testimonial.objects.filter(
        status='approved'
    ).exclude(
        published_at__isnull=True
    ).order_by('-published_at')
    
    # Apply rating filter if provided
    if rating_filter and rating_filter.isdigit():
        rating_value = int(rating_filter)
        if 1 <= rating_value <= 5:
            testimonials = testimonials.filter(rating=rating_value)
    
    # Apply class type filter if provided
    if class_filter:
        testimonials = testimonials.filter(class_type=class_filter)
    
    # Get unique class types for filter dropdown
    class_types = Testimonial.objects.filter(
        status='approved'
    ).values_list('class_type', flat=True).distinct()
    
    # Calculate average rating
    approved_testimonials = Testimonial.objects.filter(status='approved')
    if approved_testimonials.exists():
        total_rating = sum(t.rating for t in approved_testimonials)
        average_rating = round(total_rating / approved_testimonials.count(), 1)
        total_reviews = approved_testimonials.count()
    else:
        average_rating = 0
        total_reviews = 0
    
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
def instructor_list(request):
    """
    Display all instructors in a responsive grid layout.
    Shows instructor cards with photos, names, specialties and profile links.
    """
    import json
    
    # Use cached instructors list for performance
    cache_key = 'instructor_list_data'
    instructors_data = cache.get(cache_key)
    
    if instructors_data is None:
        instructors = Instructor.objects.all().order_by('name')
    
    # Parse specialties for each instructor to pass to template
    instructors_with_specialties = []
    for instructor in instructors:
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
        'instructors': instructors,
        'instructors_with_specialties': instructors_with_specialties,
        'page_title': 'Our Instructors',
    }
    
    return render(request, 'instructors/list.html', context)

def instructor_detail(request, instructor_id):
    """
    Display detailed instructor profile with full bio, video, and booking options.
    Shows large photo, bio, specialties as badges, intro video, and booking links.
    """
    instructor = get_object_or_404(Instructor, id=instructor_id)
    
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
def gallery_view(request):
    """
    Display the media gallery with filtering by type and category.
    Supports photo and video content organized by event/class type.
    Now includes Instagram integration for social media content.
    """
    from .utils.instagram_api import get_instagram_posts
    
    # Get filter parameters from request
    media_type_filter = request.GET.get('type', 'all')
    category_filter = request.GET.get('category', 'all')
    show_instagram = request.GET.get('instagram', 'true').lower() in ('true', '1', 'yes')
    
    # Build cache key based on filters
    cache_key = f'gallery_media_{media_type_filter}_{category_filter}'
    media_items = cache.get(cache_key)
    
    if media_items is None:
        # Start with all media items with optimized query
        media_items = MediaGallery.objects.select_related()
    
    # Apply media type filter
    if media_type_filter != 'all':
        media_items = media_items.filter(media_type=media_type_filter)
    
    # Apply category filter
    if category_filter != 'all':
        media_items = media_items.filter(category=category_filter)
    
        # Apply filters if provided
        if media_type_filter != 'all':
            media_items = media_items.filter(media_type=media_type_filter)
        
        if category_filter != 'all':
            media_items = media_items.filter(category=category_filter)
        
        # Order by the order field and creation date
        media_items = list(media_items.order_by('order', '-created_at'))
        
        # Cache for 15 minutes
        cache.set(cache_key, media_items, 60 * 15)
    
    # Apply additional filters if not cached (for dynamic filtering)
    if isinstance(media_items, list):
        # Convert back to queryset-like filtering for cached results
        if media_type_filter != 'all':
            media_items = [item for item in media_items if item.media_type == media_type_filter]
        if category_filter != 'all':
            media_items = [item for item in media_items if item.category == category_filter]
    
    # Get Instagram posts if enabled
    instagram_posts = []
    if show_instagram:
        try:
            instagram_posts = get_instagram_posts(limit=8, use_cache=True)
        except Exception as e:
            # Log error but don't break the page
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to load Instagram posts: {str(e)}")
    
    # Get unique categories for filter dropdown
    categories = MediaGallery.objects.values_list('category', flat=True).distinct()
    
    # Convert category values to display names
    category_choices = []
    for cat in categories:
        for choice in MediaGallery.CATEGORY_CHOICES:
            if choice[0] == cat:
                category_choices.append(choice)
                break
    
    # Get counts for each media type (fixed to use correct field names)
    photo_count = MediaGallery.objects.filter(media_type='image').count()
    video_count = MediaGallery.objects.filter(media_type='video').count()
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


# Performance Monitoring and Service Worker Views - SPEC_04 Group D

def service_worker(request):
    """Serve the Service Worker file with correct content type"""
    import os
    from django.http import FileResponse
    
    sw_path = os.path.join(settings.STATICFILES_DIRS[0], 'js', 'service-worker.js')
    
    try:
        response = FileResponse(
            open(sw_path, 'rb'),
            content_type='application/javascript'
        )
        response['Service-Worker-Allowed'] = '/'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    except FileNotFoundError:
        return HttpResponse(
            'Service Worker not found',
            status=404,
            content_type='text/plain'
        )

def offline_view(request):
    """Offline fallback page for PWA"""
    return render(request, 'offline.html', {
        'title': 'Offline - Sabor Con Flow Dance'
    })


@require_http_methods(["POST"])
def performance_metrics(request):
    """
    Collect performance metrics from client-side analytics
    SPEC_04 Group D - Performance monitoring endpoint
    """
    try:
        data = json.loads(request.body)
        
        # Log performance metrics
        logger.info(f"Performance metrics received: {data.get('type', 'unknown')}")
        
        # Store metrics in cache for analysis
        metrics_key = f"performance_metrics_{request.session.session_key or 'anonymous'}"
        existing_metrics = cache.get(metrics_key, [])
        existing_metrics.append({
            'timestamp': data.get('timestamp'),
            'url': data.get('session', {}).get('url'),
            'metrics': data.get('metrics', {}),
            'type': data.get('type', 'client')
        })
        
        # Keep only last 100 metrics per session
        if len(existing_metrics) > 100:
            existing_metrics = existing_metrics[-100:]
        
        cache.set(metrics_key, existing_metrics, 60 * 60 * 24)  # 24 hours
        
        # Analyze Core Web Vitals
        cwv = data.get('metrics', {}).get('coreWebVitals', {})
        if cwv:
            analyze_core_web_vitals(cwv, request)
        
        return JsonResponse({'status': 'success'})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing performance metrics: {str(e)}")
        return JsonResponse({'error': 'Processing failed'}, status=500)


def analyze_core_web_vitals(cwv, request):
    """Analyze Core Web Vitals and trigger alerts if needed"""
    try:
        # Check LCP (Largest Contentful Paint)
        lcp = cwv.get('lcp', {})
        if lcp.get('value', 0) > 4000:  # Poor LCP threshold
            logger.warning(f"Poor LCP detected: {lcp.get('value')}ms on {request.META.get('HTTP_REFERER')}")
        
        # Check FID (First Input Delay)  
        fid = cwv.get('fid', {})
        if fid.get('value', 0) > 300:  # Poor FID threshold
            logger.warning(f"Poor FID detected: {fid.get('value')}ms on {request.META.get('HTTP_REFERER')}")
        
        # Check CLS (Cumulative Layout Shift)
        cls = cwv.get('cls', {})
        if cls.get('value', 0) > 0.25:  # Poor CLS threshold
            logger.warning(f"Poor CLS detected: {cls.get('value')} on {request.META.get('HTTP_REFERER')}")
            
    except Exception as e:
        logger.error(f"Error analyzing Core Web Vitals: {str(e)}")


@cache_page(60 * 5)  # Cache for 5 minutes
def performance_dashboard_data(request):
    """
    Provide aggregated performance data for dashboard
    """
    try:
        # Get cached metrics
        metrics_key = f"performance_metrics_{request.session.session_key or 'anonymous'}"
        metrics = cache.get(metrics_key, [])
        
        if not metrics:
            return JsonResponse({
                'status': 'no_data',
                'message': 'No performance data available'
            })
        
        # Aggregate metrics
        aggregated = {
            'total_samples': len(metrics),
            'average_load_time': 0,
            'core_web_vitals': {
                'lcp': {'average': 0, 'samples': 0},
                'fid': {'average': 0, 'samples': 0},
                'cls': {'average': 0, 'samples': 0}
            },
            'page_performance': {},
            'recommendations': []
        }
        
        # Process metrics
        total_load_time = 0
        load_time_samples = 0
        
        for metric in metrics[-50:]:  # Last 50 samples
            metric_data = metric.get('metrics', {})
            
            # Navigation timing
            nav = metric_data.get('navigation', {})
            if nav.get('total'):
                total_load_time += nav['total']
                load_time_samples += 1
            
            # Core Web Vitals
            cwv = metric_data.get('coreWebVitals', {})
            for vital in ['lcp', 'fid', 'cls']:
                if vital in cwv and cwv[vital].get('value') is not None:
                    current = aggregated['core_web_vitals'][vital]
                    current['average'] = (current['average'] * current['samples'] + cwv[vital]['value']) / (current['samples'] + 1)
                    current['samples'] += 1
        
        if load_time_samples > 0:
            aggregated['average_load_time'] = total_load_time / load_time_samples
        
        # Generate recommendations
        aggregated['recommendations'] = generate_performance_recommendations(aggregated)
        
        return JsonResponse(aggregated)
        
    except Exception as e:
        logger.error(f"Error generating dashboard data: {str(e)}")
        return JsonResponse({'error': 'Failed to generate dashboard data'}, status=500)


def generate_performance_recommendations(metrics):
    """Generate performance recommendations based on metrics"""
    recommendations = []
    
    # Load time recommendations
    if metrics['average_load_time'] > 3000:
        recommendations.append({
            'type': 'critical',
            'title': 'Slow Page Load Time',
            'description': f"Average load time is {metrics['average_load_time']:.0f}ms. Target: <2500ms",
            'actions': ['Optimize images', 'Enable compression', 'Minimize JavaScript']
        })
    
    # Core Web Vitals recommendations
    cwv = metrics['core_web_vitals']
    
    if cwv['lcp']['samples'] > 0 and cwv['lcp']['average'] > 2500:
        recommendations.append({
            'type': 'warning',
            'title': 'Poor LCP Performance',
            'description': f"Average LCP is {cwv['lcp']['average']:.0f}ms. Target: <2500ms",
            'actions': ['Optimize critical images', 'Improve server response time', 'Remove render-blocking resources']
        })
    
    if cwv['fid']['samples'] > 0 and cwv['fid']['average'] > 100:
        recommendations.append({
            'type': 'warning', 
            'title': 'Poor FID Performance',
            'description': f"Average FID is {cwv['fid']['average']:.0f}ms. Target: <100ms",
            'actions': ['Reduce JavaScript execution time', 'Split long tasks', 'Use web workers']
        })
    
    if cwv['cls']['samples'] > 0 and cwv['cls']['average'] > 0.1:
        recommendations.append({
            'type': 'warning',
            'title': 'Poor CLS Performance', 
            'description': f"Average CLS is {cwv['cls']['average']:.3f}. Target: <0.1",
            'actions': ['Add size attributes to images', 'Reserve space for ads', 'Avoid inserting content above existing content']
        })
    
    # If no major issues
    if not recommendations:
        recommendations.append({
            'type': 'success',
            'title': 'Good Performance',
            'description': 'Your site is performing well! Keep monitoring.',
            'actions': ['Continue monitoring', 'Test on different devices', 'Check mobile performance']
        })
    
    return recommendations


# Instagram Webhook Handlers - SPEC_04 Group D

@csrf_exempt
@require_http_methods(["GET", "POST"])
def instagram_webhook(request):
    """
    Handle Instagram webhook verification and notifications.
    
    GET: Webhook verification
    POST: Webhook notifications
    """
    if request.method == "GET":
        return handle_webhook_verification(request)
    elif request.method == "POST":
        return handle_webhook_notification(request)


def handle_webhook_verification(request):
    """Handle Instagram webhook verification challenge."""
    verify_token = getattr(settings, 'INSTAGRAM_WEBHOOK_VERIFY_TOKEN', None)
    
    if not verify_token:
        logger.error("Instagram webhook verify token not configured")
        return HttpResponse("Webhook verify token not configured", status=400)
    
    mode = request.GET.get('hub.mode')
    token = request.GET.get('hub.verify_token')
    challenge = request.GET.get('hub.challenge')
    
    if mode == 'subscribe' and token == verify_token:
        logger.info("Instagram webhook verification successful")
        return HttpResponse(challenge, content_type='text/plain')
    else:
        logger.warning(f"Instagram webhook verification failed: mode={mode}, token={token}")
        return HttpResponse("Verification failed", status=403)


def handle_webhook_notification(request):
    """Handle Instagram webhook notifications for media updates."""
    try:
        payload = json.loads(request.body.decode('utf-8'))
        
        if not isinstance(payload, dict) or 'object' not in payload:
            logger.warning("Invalid Instagram webhook payload structure")
            return HttpResponse("Invalid payload structure", status=400)
        
        if payload.get('object') != 'instagram':
            logger.warning(f"Unexpected webhook object type: {payload.get('object')}")
            return HttpResponse("Unexpected object type", status=400)
        
        entries = payload.get('entry', [])
        for entry in entries:
            process_instagram_entry(entry)
        
        logger.info(f"Processed {len(entries)} Instagram webhook entries")
        return HttpResponse("OK", content_type='text/plain')
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Instagram webhook payload")
        return HttpResponse("Invalid JSON payload", status=400)
    except Exception as e:
        logger.error(f"Error processing Instagram webhook: {str(e)}")
        return HttpResponse("Internal error", status=500)


def process_instagram_entry(entry):
    """Process a single Instagram webhook entry."""
    try:
        user_id = entry.get('id')
        changes = entry.get('changes', [])
        
        logger.info(f"Processing Instagram entry for user {user_id} with {len(changes)} changes")
        
        for change in changes:
            field = change.get('field')
            value = change.get('value')
            
            if field == 'media':
                handle_media_change(user_id, value)
            elif field == 'mentions':
                handle_mentions_change(user_id, value)
            else:
                logger.debug(f"Ignoring Instagram webhook field: {field}")
                
    except Exception as e:
        logger.error(f"Error processing Instagram entry: {str(e)}")


def handle_media_change(user_id, value):
    """Handle Instagram media changes (new posts, updates, deletes)."""
    try:
        media_id = value.get('media_id')
        if not media_id:
            logger.warning("Instagram media change without media_id")
            return
        
        existing_media = MediaGallery.objects.filter(
            source='instagram',
            instagram_id=media_id
        ).first()
        
        # For webhook handler, we'll just log the change
        # Full sync should be handled by the management command
        logger.info(f"Instagram media change detected: {media_id}")
        
        if not existing_media:
            logger.info(f"New Instagram media detected: {media_id}")
            
    except Exception as e:
        logger.error(f"Error handling Instagram media change: {str(e)}")


def handle_mentions_change(user_id, value):
    """Handle Instagram mention notifications."""
    try:
        comment_id = value.get('comment_id')
        media_id = value.get('media_id')
        
        logger.info(f"Instagram mention detected - User: {user_id}, Media: {media_id}, Comment: {comment_id}")
        
    except Exception as e:
        logger.error(f"Error handling Instagram mention: {str(e)}")


def calendly_test(request):
    """
    Test page for Calendly widget integration - SPEC_05 Group A Task 1.
    Only available in debug mode for security.
    """
    # Only allow access in debug mode
    if not settings.DEBUG:
        from django.http import Http404
        raise Http404("Test page not available in production")
    
    context = {
        'page_title': 'Calendly Widget Test Page',
    }
    
    return render(request, 'calendly_test.html', context)


# Pastio.fun RSVP Integration - SPEC_05 Group B Task 7

@csrf_protect
@require_http_methods(["POST"])
def submit_rsvp(request):
    """
    Handle RSVP submissions for Pastio.fun integration.
    Process form data and integrate with Pastio API.
    """
    try:
        # Get form data
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        class_id = request.POST.get('class_id', '').strip()
        notifications = request.POST.get('notifications') == 'on'
        
        # Validate required fields
        if not name or not email or not class_id:
            return JsonResponse({
                'error': 'Name, email, and class selection are required.'
            }, status=400)
        
        # Validate email format
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({
                'error': 'Please enter a valid email address.'
            }, status=400)
        
        # Map class IDs to class names
        class_mapping = {
            'scf-choreo': 'SCF Choreo Team',
            'pasos-basicos': 'Pasos Básicos',
            'casino-royale': 'Casino Royale'
        }
        
        class_name = class_mapping.get(class_id)
        if not class_name:
            return JsonResponse({
                'error': 'Invalid class selection.'
            }, status=400)
        
        # Create RSVP submission record
        rsvp = RSVPSubmission.objects.create(
            name=name,
            email=email,
            phone=phone or None,
            class_id=class_id,
            class_name=class_name,
            notifications_enabled=notifications,
            status='confirmed',
            source='pastio'
        )
        
        # Log successful RSVP
        logger.info(f"RSVP submitted: {rsvp.id} - {name} for {class_name}")
        
        # In a real implementation, integrate with Pastio API here
        integrate_with_pastio_api(rsvp)
        
        # Send confirmation email if enabled
        if notifications:
            try:
                send_rsvp_confirmation_email(rsvp)
            except Exception as e:
                logger.warning(f"Failed to send RSVP confirmation email: {e}")
        
        # Send admin notification
        try:
            send_rsvp_admin_notification(rsvp)
        except Exception as e:
            logger.warning(f"Failed to send RSVP admin notification: {e}")
        
        return JsonResponse({
            'success': True,
            'message': f'Your RSVP for {class_name} has been confirmed!',
            'rsvp_id': rsvp.id
        })
        
    except Exception as e:
        logger.error(f"Error processing RSVP submission: {str(e)}")
        return JsonResponse({
            'error': 'There was an error processing your RSVP. Please try again.'
        }, status=500)


def integrate_with_pastio_api(rsvp):
    """
    Integrate RSVP submission with Pastio.fun API.
    This is a placeholder for the actual Pastio API integration.
    """
    try:
        import requests
        
        # Pastio API configuration (replace with actual values)
        PASTIO_API_URL = "https://api.pastio.fun/v1"
        PASTIO_API_KEY = getattr(settings, 'PASTIO_API_KEY', None)
        PASTIO_ORGANIZER_ID = getattr(settings, 'PASTIO_ORGANIZER_ID', 'sabor-con-flow-dance')
        
        if not PASTIO_API_KEY:
            logger.warning("Pastio API key not configured - skipping API integration")
            return False
        
        # Map class IDs to Pastio event IDs
        event_mapping = {
            'scf-choreo': 'scf-choreo-sunday',
            'pasos-basicos': 'pasos-basicos-sunday', 
            'casino-royale': 'casino-royale-sunday'
        }
        
        pastio_event_id = event_mapping.get(rsvp.class_id)
        if not pastio_event_id:
            logger.error(f"No Pastio event mapping for class: {rsvp.class_id}")
            return False
        
        # Prepare API payload
        payload = {
            'event_id': pastio_event_id,
            'attendee': {
                'name': rsvp.name,
                'email': rsvp.email,
                'phone': rsvp.phone,
                'notifications_enabled': rsvp.notifications_enabled
            },
            'source': 'website',
            'metadata': {
                'rsvp_id': rsvp.id,
                'class_name': rsvp.class_name
            }
        }
        
        # Make API request
        headers = {
            'Authorization': f'Bearer {PASTIO_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{PASTIO_API_URL}/events/{pastio_event_id}/rsvps",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            # Update RSVP with Pastio response
            pastio_data = response.json()
            rsvp.pastio_id = pastio_data.get('id')
            rsvp.save()
            
            logger.info(f"RSVP {rsvp.id} successfully integrated with Pastio: {rsvp.pastio_id}")
            return True
        else:
            logger.error(f"Pastio API error: {response.status_code} - {response.text}")
            return False
            
    except requests.RequestException as e:
        logger.error(f"Network error integrating with Pastio API: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error integrating with Pastio API: {str(e)}")
        return False


def send_rsvp_confirmation_email(rsvp):
    """Send RSVP confirmation email to attendee."""
    try:
        subject = f"RSVP Confirmed - {rsvp.class_name}"
        
        # Get next Sunday date
        from datetime import datetime, timedelta
        today = datetime.now().date()
        days_ahead = 6 - today.weekday()  # Sunday is 6
        if days_ahead <= 0:
            days_ahead += 7
        next_sunday = today + timedelta(days=days_ahead)
        
        # Class time mapping
        class_times = {
            'scf-choreo': '12:00 PM - 1:00 PM',
            'pasos-basicos': '1:00 PM - 2:00 PM',
            'casino-royale': '2:00 PM - 3:00 PM'
        }
        
        class_time = class_times.get(rsvp.class_id, 'TBD')
        
        message = f"""
Hi {rsvp.name},

Your RSVP for {rsvp.class_name} has been confirmed!

Class Details:
- Date: {next_sunday.strftime('%A, %B %d, %Y')}
- Time: {class_time}
- Location: Avalon Ballroom, Boulder, CO

What to bring:
- Comfortable clothes you can move in
- Water bottle
- Positive energy and willingness to learn!

We're excited to see you on the dance floor!

Questions? Reply to this email or contact us at info@saborconflowdance.com

Best regards,
Sabor Con Flow Dance Team

---
To unsubscribe from future reminders, reply with "UNSUBSCRIBE"
        """.strip()
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [rsvp.email],
            fail_silently=False,
        )
        
        logger.info(f"RSVP confirmation email sent to {rsvp.email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending RSVP confirmation email: {str(e)}")
        return False


def send_rsvp_admin_notification(rsvp):
    """Send RSVP notification to admin."""
    try:
        subject = f"New RSVP: {rsvp.class_name} - {rsvp.name}"
        
        message = f"""
New RSVP Received

Class: {rsvp.class_name}
Name: {rsvp.name}
Email: {rsvp.email}
Phone: {rsvp.phone or 'Not provided'}
Notifications: {'Yes' if rsvp.notifications_enabled else 'No'}
Source: {rsvp.source}
RSVP ID: {rsvp.id}
Pastio ID: {rsvp.pastio_id or 'Not synced'}

Submitted: {rsvp.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        
        logger.info(f"RSVP admin notification sent for {rsvp.id}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending RSVP admin notification: {str(e)}")
        return False


@require_http_methods(["GET"])
def get_rsvp_counts(request):
    """
    Get current RSVP counts for each class.
    Used by JavaScript to update real-time counts.
    """
    try:
        # Cache key for RSVP counts
        cache_key = 'rsvp_counts_current'
        counts = cache.get(cache_key)
        
        if counts is None:
            # Get actual counts from database
            from django.db.models import Count
            from datetime import datetime, timedelta
            
            # Get next Sunday
            today = datetime.now().date()
            days_ahead = 6 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_sunday = today + timedelta(days=days_ahead)
            
            # Count RSVPs for each class for next Sunday
            class_ids = ['scf-choreo', 'pasos-basicos', 'casino-royale']
            counts = {}
            
            for class_id in class_ids:
                count = RSVPSubmission.objects.filter(
                    class_id=class_id,
                    status='confirmed',
                    created_at__date__gte=today - timedelta(days=7)  # Recent RSVPs
                ).count()
                
                # Add some baseline/default counts for demo
                baseline_counts = {
                    'scf-choreo': 8,
                    'pasos-basicos': 12,
                    'casino-royale': 15
                }
                
                counts[class_id] = count + baseline_counts.get(class_id, 0)
            
            # Cache for 5 minutes
            cache.set(cache_key, counts, 60 * 5)
        
        return JsonResponse({
            'success': True,
            'counts': counts,
            'updated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting RSVP counts: {str(e)}")
        return JsonResponse({
            'error': 'Failed to get RSVP counts'
        }, status=500)


# Health check endpoint for CI/CD deployments - SPEC_06 Group D Task 10
@require_http_methods(["GET"])
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def health_check(request):
    """
    Health check endpoint for deployment verification and monitoring.
    Returns comprehensive system status including database, cache, and dependencies.
    """
    from django.db import connection
    from django.core.cache import cache
    from datetime import datetime
    import time
    
    start_time = time.time()
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'environment': getattr(settings, 'ENVIRONMENT', 'production'),
        'checks': {}
    }
    
    # Database connectivity check
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        health_status['checks']['database'] = {
            'status': 'healthy',
            'response_time_ms': round((time.time() - start_time) * 1000, 2)
        }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Cache connectivity check
    cache_start = time.time()
    try:
        cache_key = f'health_check_{int(time.time())}'
        cache.set(cache_key, 'test', 10)
        cache_value = cache.get(cache_key)
        cache.delete(cache_key)
        
        if cache_value == 'test':
            health_status['checks']['cache'] = {
                'status': 'healthy',
                'response_time_ms': round((time.time() - cache_start) * 1000, 2)
            }
        else:
            health_status['checks']['cache'] = {
                'status': 'degraded',
                'error': 'Cache value mismatch'
            }
    except Exception as e:
        health_status['checks']['cache'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Application-specific checks
    app_start = time.time()
    try:
        # Check if we can query models
        testimonial_count = Testimonial.objects.filter(is_approved=True).count()
        instructor_count = Instructor.objects.count()
        
        health_status['checks']['application'] = {
            'status': 'healthy',
            'response_time_ms': round((time.time() - app_start) * 1000, 2),
            'metrics': {
                'testimonials': testimonial_count,
                'instructors': instructor_count
            }
        }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['application'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Static files check
    static_start = time.time()
    try:
        from django.contrib.staticfiles import finders
        css_file = finders.find('css/styles.css')
        js_file = finders.find('js/main.js')
        
        health_status['checks']['static_files'] = {
            'status': 'healthy' if css_file and js_file else 'degraded',
            'response_time_ms': round((time.time() - static_start) * 1000, 2),
            'found_files': {
                'css': bool(css_file),
                'js': bool(js_file)
            }
        }
    except Exception as e:
        health_status['checks']['static_files'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Overall response time
    health_status['total_response_time_ms'] = round((time.time() - start_time) * 1000, 2)
    
    # Determine overall status
    unhealthy_checks = [check for check in health_status['checks'].values() 
                       if check.get('status') == 'unhealthy']
    
    if unhealthy_checks:
        health_status['status'] = 'unhealthy'
        status_code = 503
    elif any(check.get('status') == 'degraded' for check in health_status['checks'].values()):
        health_status['status'] = 'degraded'
        status_code = 200
    else:
        status_code = 200
    
    return JsonResponse(health_status, status=status_code)


def php_redirect(request):
    """
    Handle requests for common PHP files that don't exist in Django.
    This prevents 400/404 errors from browser autocomplete, extensions, or bots.
    """
    requested_path = request.path
    
    # Log the attempt for monitoring
    logger.info(f"PHP file requested: {requested_path} from IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
    
    # Map common PHP files to appropriate Django views
    php_redirects = {
        '/profile.php': '/',  # Redirect to home page
        '/index.php': '/',    # Redirect to home page  
        '/admin.php': '/admin/',  # Redirect to Django admin
        '/login.php': '/admin/',  # Redirect to Django admin login
    }
    
    redirect_url = php_redirects.get(requested_path, '/')
    
    # Return a 301 permanent redirect with a helpful message
    response = redirect(redirect_url, permanent=True)
    
    # Add a custom header to indicate this was a PHP compatibility redirect
    response['X-PHP-Redirect'] = 'This site uses Django, not PHP'
    
    return response