from django.shortcuts import render
from django.conf import settings

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
    return render(request, 'events.html', {'events': events})

def pricing(request):
    return render(request, 'pricing.html')

def private_lessons(request):
    return render(request, 'private_lessons.html')

def contact(request):
    return render(request, 'contact.html')
