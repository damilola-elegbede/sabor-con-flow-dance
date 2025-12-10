from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from .models import Class, Testimonial
from .forms import TestimonialForm
from .utils.email_notifications import send_admin_notification_email, send_thank_you_email
from .utils.google_reviews import submit_testimonial_to_google

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
    
    # Get featured testimonials for carousel
    carousel_testimonials = Testimonial.objects.filter(
        status='approved',
        featured=True
    ).exclude(
        published_at__isnull=True
    ).order_by('-published_at')[:6]  # Get up to 6 featured testimonials
    
    # If not enough featured testimonials, get recent approved ones
    if carousel_testimonials.count() < 3:
        carousel_testimonials = Testimonial.objects.filter(
            status='approved'
        ).exclude(
            published_at__isnull=True
        ).order_by('-published_at')[:6]
    
    return render(request, 'home.html', {
        'upcoming_events': upcoming_events,
        'carousel_testimonials': carousel_testimonials
    })

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

def contact(request):
    return render(request, 'contact.html')

def schedule_view(request):
    """
    Display the schedule page with Sunday classes from the database.
    Fetches Class objects and passes them to the template.
    """
    # Fetch Sunday classes ordered by start time with instructor data
    sunday_classes = Class.objects.filter(day_of_week='Sunday').select_related('instructor').order_by('start_time')
    
    return render(request, 'schedule.html', {
        'sunday_classes': sunday_classes
    })

@csrf_protect
@require_http_methods(["GET", "POST"])
def submit_testimonial(request):
    """
    Handle testimonial submission with proper validation and processing.
    Supports parameterized review links for pre-filling form data.
    GET: Display testimonial form (with optional pre-filled data)
    POST: Process testimonial submission
    """
    review_link = None
    initial_data = {}
    
    # Handle review link parameters
    ref_token = request.GET.get('ref')
    if ref_token:
        try:
            review_link = ReviewLink.objects.get(
                token=ref_token,
                is_active=True
            )
            
            # Check if link has expired
            if review_link.is_expired():
                messages.warning(
                    request,
                    'This review link has expired, but you can still submit your testimonial below.'
                )
                review_link = None
            else:
                # Track the click
                review_link.track_click()
                
                # Pre-fill form data from review link
                if review_link.instructor_name:
                    # Store instructor name for display (not part of form)
                    initial_data['instructor_context'] = review_link.instructor_name
                
                if review_link.class_type:
                    # Map class type to form choice
                    for choice in Testimonial.CLASS_TYPE_CHOICES:
                        if choice[0] == review_link.class_type:
                            initial_data['class_type'] = choice[0]
                            break
                
        except ReviewLink.DoesNotExist:
            messages.info(
                request,
                'Review link not found, but you can still submit your testimonial below.'
            )
    
    # Handle manual URL parameters (fallback)
    if not review_link:
        instructor_param = request.GET.get('instructor')
        class_param = request.GET.get('class')
        
        if instructor_param:
            initial_data['instructor_context'] = instructor_param.replace('-', ' ').title()
        
        if class_param:
            # Try to map class parameter to valid choice
            for choice in Testimonial.CLASS_TYPE_CHOICES:
                if choice[0] == class_param or choice[1].lower() == class_param.lower():
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
                
                # Track conversion if this came from a review link
                if review_link:
                    review_link.track_conversion()
                
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
                
                # Redirect to success page
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
        # Create form with initial data
        form = TestimonialForm(initial=initial_data)
    
    # Prepare context
    context = {
        'form': form,
        'page_title': 'Share Your Dance Journey',
        'review_link': review_link,
        'instructor_context': initial_data.get('instructor_context'),
    }
    
    # Add campaign info if available
    if review_link and review_link.campaign_name:
        context['campaign_name'] = review_link.campaign_name
    
    return render(request, 'testimonials/submit.html', context)

def testimonial_success(request):
    """Display success page after testimonial submission."""
    return render(request, 'testimonials/success.html', {
        'page_title': 'Thank You!',
    })


def review_link_redirect(request, token):
    """
    Handle short URL redirects for review links.
    Redirects /r/{token} to the full testimonial submission form.
    """
    try:
        # Find the review link by token (partial match for short URLs)
        review_link = ReviewLink.objects.filter(
            token__startswith=token,
            is_active=True
        ).first()
        
        if not review_link:
            messages.error(
                request,
                'Review link not found. Please use the form below to submit your testimonial.'
            )
            return redirect('core:submit_testimonial')
        
        # Check if link has expired
        if review_link.is_expired():
            messages.warning(
                request,
                'This review link has expired, but you can still submit your testimonial below.'
            )
            return redirect('core:submit_testimonial')
        
        # Redirect to testimonial form with full token
        full_url = review_link.get_full_url()
        return redirect(f'/testimonials/submit/?ref={review_link.token}')
        
    except Exception as e:
        messages.error(
            request,
            'There was an error processing your review link. Please try again.'
        )
        print(f"Error in review_link_redirect: {e}")
        return redirect('core:submit_testimonial')


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
