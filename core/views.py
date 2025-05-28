from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import NewsletterSignupForm

def home(request):
    if request.method == 'POST':
        form = NewsletterSignupForm(request.POST)
        if form.is_valid():
            # Instead of saving to database, just show success message
            messages.success(request, 'Thank you for subscribing to our newsletter!')
            return redirect('home')
    else:
        form = NewsletterSignupForm()
    
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
        'form': form,
        'upcoming_events': upcoming_events
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
    return render(request, 'pricing.html')

def contact(request):
    return render(request, 'contact.html')

def register_for_class(request, event_id):
    # Static event data
    events = {
        1: {
            'title': 'SCF Choreo Team',
            'date': 'Every Sunday',
            'time': '12:00 PM - 1:00 PM',
            'location': 'Avalon Ballroom (North Lobby)',
            'description': 'Join our choreography team for an intensive dance training session focusing on advanced Cuban salsa techniques and performance routines.',
            'price': 20
        },
        2: {
            'title': 'Pasos Básicos',
            'date': 'Every Sunday',
            'time': '1:00 PM - 2:00 PM',
            'location': 'Avalon Ballroom (Tango Room)',
            'description': 'Pasos Básicos will focus on basic cuban salsa footwork, turn patterns, and a little bit of afro-cuban in salsa.',
            'price': 20
        },
        3: {
            'title': 'Casino Royale',
            'date': 'Every Sunday',
            'time': '2:00 PM - 3:00 PM',
            'location': 'Avalon Ballroom (Tango Room)',
            'description': 'Take your casino dancing to the next level with this class. We focus on the building blocks of Casino dancing.',
            'price': 20
        }
    }
    
    event = events.get(event_id)
    if not event:
        messages.error(request, 'Event not found.')
        return redirect('core:events')
    
    if request.method == 'POST':
        form = NewsletterSignupForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Registration successful! We will contact you with payment details.')
            return redirect('core:events')
    else:
        form = NewsletterSignupForm()
    
    return render(request, 'register.html', {
        'form': form,
        'event': event
    })
