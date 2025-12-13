import json
import logging
from email.utils import formataddr

from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.mail import EmailMessage

from .forms import ContactForm

logger = logging.getLogger(__name__)

def home(request):
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

    return render(request, 'home.html', {
        'current_page': 'home',
        'upcoming_events': upcoming_events,
        'hero_video_path': settings.HERO_VIDEO_PATH,
        'second_video_path': settings.SECOND_VIDEO_PATH,
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
    return render(request, 'events.html', {
        'current_page': 'events',
        'events': events
    })

def pricing(request):
    return render(request, 'pricing.html', {
        'current_page': 'pricing'
    })

def private_lessons(request):
    return render(request, 'private_lessons.html', {
        'current_page': 'private_lessons'
    })

def contact(request):
    return render(request, 'contact.html', {
        'current_page': 'contact'
    })


@require_http_methods(["POST"])
@csrf_protect
def contact_submit(request):
    """Handle contact form submission via AJAX."""
    try:
        # Parse JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request format'
            }, status=400)

        # Validate form
        form = ContactForm(data)

        if not form.is_valid():
            # Collect all errors into a single message
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(error)
            return JsonResponse({
                'success': False,
                'message': '. '.join(errors)
            }, status=400)

        # Check for spam (honeypot)
        if form.cleaned_data.get('is_spam'):
            # Pretend success but don't send email
            logger.info('Spam submission detected and blocked')
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your message!'
            })

        # Get cleaned data
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        subject_key = form.cleaned_data['subject']
        message = form.cleaned_data['message']

        # Map subject key to display name
        subject_map = dict(ContactForm.SUBJECT_CHOICES)
        subject_display = subject_map.get(subject_key, 'General Inquiry')

        # Log submission
        logger.info(f'Contact form submission from {name} <{email}> - {subject_display}')

        # Send email notification if configured
        if hasattr(settings, 'EMAIL_HOST') and settings.EMAIL_HOST:
            try:
                send_contact_email(name, email, subject_display, message)
            except Exception as e:
                logger.error(f'Failed to send contact email: {e}')
                # Don't fail the request if email fails

        return JsonResponse({
            'success': True,
            'message': 'Thank you for your message. We will get back to you soon!'
        })

    except Exception:
        logger.exception('Contact form error')
        return JsonResponse({
            'success': False,
            'message': 'An unexpected error occurred. Please try again later.'
        }, status=500)


def send_contact_email(name, email, subject, message):
    """Send contact form notification email."""
    # Plain text version
    text_content = f"""
New Contact Form Submission
===========================

From: {name} <{email}>
Subject: {subject}

Message:
--------
{message}

---
This message was sent from the Sabor Con Flow website contact form.
Reply directly to this email to respond to {name}.
    """

    email_message = EmailMessage(
        subject=f'[Website Contact] {subject} - from {name}',
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.CONTACT_EMAIL],
        reply_to=[formataddr((name, email))],
    )
    email_message.send(fail_silently=False)
