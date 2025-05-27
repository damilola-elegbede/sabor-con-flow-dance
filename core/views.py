from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Event, Subscriber, ClassRegistration
from .forms import NewsletterSignupForm, ClassRegistrationForm
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    if request.method == 'POST':
        form = NewsletterSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for subscribing to our newsletter!')
            return redirect('home')
    else:
        form = NewsletterSignupForm()
    
    upcoming_events = Event.objects.filter(is_active=True).order_by('date', 'time')[:3]
    return render(request, 'home.html', {
        'form': form,
        'upcoming_events': upcoming_events,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

def events(request):
    events = Event.objects.filter(is_active=True).order_by('date', 'time')
    return render(request, 'events.html', {'events': events})

def pricing(request):
    return render(request, 'pricing.html')

def contact(request):
    return render(request, 'contact.html')

def register_for_class(request, event_id):
    event = get_object_or_404(Event, id=event_id, is_active=True)
    
    if request.method == 'POST':
        form = ClassRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            
            try:
                # Create Stripe customer
                customer = stripe.Customer.create(
                    email=registration.email,
                    name=registration.name,
                    phone=registration.phone
                )
                registration.stripe_customer_id = customer.id
                
                # Create Stripe payment intent
                intent = stripe.PaymentIntent.create(
                    amount=int(event.price * 100),  # Convert to cents
                    currency='usd',
                    customer=customer.id,
                    metadata={
                        'registration_id': registration.id,
                        'event_id': event.id
                    }
                )
                
                registration.payment_id = intent.id
                registration.save()
                
                return JsonResponse({
                    'client_secret': intent.client_secret
                })
            except stripe.error.StripeError as e:
                messages.error(request, f'Payment error: {str(e)}')
                return JsonResponse({'error': str(e)}, status=400)
    else:
        form = ClassRegistrationForm()
    
    return render(request, 'register.html', {
        'form': form,
        'event': event,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        registration = ClassRegistration.objects.get(payment_id=payment_intent['id'])
        registration.payment_status = 'completed'
        registration.save()
        
        # Send confirmation email here
        
    return JsonResponse({'status': 'success'})
