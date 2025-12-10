# Phase 6: Features and Polish - Technical Specification

## Executive Summary

Phase 6 represents the final phase of the Sabor Con Flow dance website modernization,
focusing on contact form implementation, dependency cleanup, and accessibility polish.
This phase transforms the contact page from external-link-only to a fully functional
form submission system while dramatically reducing the npm package footprint.

**Key Deliverables:**

- PR 6.1: Contact form with Django backend handling and email notification
- PR 6.2: Dependency audit reducing npm packages to minimal (Vite only after Phase 1 Express removal)
- PR 6.3: WCAG AA accessibility compliance and SEO optimization

**Architecture Note:** The site runs on **Django** deployed to Vercel via `/api/index.py`
(WSGI handler). Phase 1 removes the unused Express.js server entirely. All backend
implementations target Django's `core/views.py` and `core/urls.py`.

---

## Current State Analysis

### Contact Page Analysis (`templates/contact.html` via Django)

**Current Implementation:**

- External links only: email (mailto), WhatsApp (external), Instagram, Facebook
- No form submission capability
- No server-side form handling
- Django templates render the page

**Current Markup Structure:**

```html
<div class="container main-content-contact">
    <h1 class="page-title">Get In Touch</h1>
    <!-- Three contact sections with external links only -->
    <div class="contact-section"><!-- Email --></div>
    <div class="contact-section"><!-- WhatsApp --></div>
    <div class="contact-section"><!-- Social Media --></div>
</div>
```

### Django Configuration

**Current Setup:**

- Django 5.2.1 deployed via Vercel WSGI
- WhiteNoise for static file serving
- Templates in `templates/` directory
- Views in `core/views.py`
- URLs in `core/urls.py`
- No email backend configured

**Relevant Files:**

- `api/index.py` - Vercel WSGI entry point
- `core/views.py` - View functions
- `core/urls.py` - URL routing
- `sabor_con_flow/settings.py` - Django settings

### Dependency Analysis

**After Phase 1 (Express removal), package.json should be minimal:**

Since the site runs on Django/Python, npm is only needed for:
1. Build tooling (Vite for CSS/JS optimization in Phase 5)
2. Development tooling (linting, formatting)

**Python Dependencies (requirements.txt):**

- Django 5.2.1
- whitenoise
- gunicorn (production)

---

## PR 6.1: Contact Form Implementation

### Overview

Implement a fully functional contact form with client-side and server-side validation,
email notification via Django's email backend, and comprehensive error handling.

### File Changes Required

| File | Action | Description |
|------|--------|-------------|
| `templates/contact.html` | Modify | Add contact form HTML |
| `core/views.py` | Modify | Add form handling view |
| `core/urls.py` | Modify | Add POST route for contact |
| `core/forms.py` | Create | Django form class |
| `static/js/contact.js` | Create | Client-side validation |
| `static/css/styles.css` | Modify | Add form styles |
| `sabor_con_flow/settings.py` | Modify | Configure email backend |

### Django Form Class

**File:** `core/forms.py`

```python
"""
Contact form for Sabor Con Flow Dance website.
"""
from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator


class ContactForm(forms.Form):
    """Contact form with validation matching client-side rules."""

    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('classes', 'Class Information'),
        ('private', 'Private Lessons'),
        ('events', 'Events & Workshops'),
        ('other', 'Other'),
    ]

    name = forms.CharField(
        min_length=2,
        max_length=100,
        validators=[
            MinLengthValidator(2, message='Name must be at least 2 characters'),
            MaxLengthValidator(100, message='Name cannot exceed 100 characters'),
        ],
        error_messages={
            'required': 'Name is required',
        }
    )

    email = forms.EmailField(
        max_length=254,
        error_messages={
            'required': 'Email is required',
            'invalid': 'Please enter a valid email address',
        }
    )

    subject = forms.ChoiceField(
        choices=SUBJECT_CHOICES,
        initial='general',
        error_messages={
            'invalid_choice': 'Please select a valid subject',
        }
    )

    message = forms.CharField(
        min_length=10,
        max_length=2000,
        widget=forms.Textarea,
        validators=[
            MinLengthValidator(10, message='Message must be at least 10 characters'),
            MaxLengthValidator(2000, message='Message cannot exceed 2000 characters'),
        ],
        error_messages={
            'required': 'Message is required',
        }
    )

    # Honeypot field for spam protection
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean(self):
        """Check honeypot field for spam."""
        cleaned_data = super().clean()
        # If honeypot field is filled, it's likely a bot
        if cleaned_data.get('website'):
            # Silently accept but don't process (appears successful to bot)
            cleaned_data['is_spam'] = True
        else:
            cleaned_data['is_spam'] = False
        return cleaned_data
```

### Django View for Contact Form

**File:** `core/views.py` (add to existing file)

```python
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from .forms import ContactForm

logger = logging.getLogger(__name__)


def contact(request):
    """Render contact page."""
    return render(request, 'contact.html', {
        'title': 'Contact Us - Sabor Con Flow Dance',
        'description': 'Get in touch with Sabor Con Flow Dance. Questions about classes? Send us a message or join our WhatsApp community.',
        'canonical_path': '/contact',
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

    except Exception as e:
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

    # HTML version
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #000; color: #C7B375; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; }}
        .field {{ margin-bottom: 15px; }}
        .label {{ font-weight: bold; color: #666; }}
        .value {{ margin-top: 5px; }}
        .message-box {{ background: #fff; padding: 15px; border-left: 4px solid #C7B375; }}
        .footer {{ padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>New Contact Form Submission</h1>
        </div>
        <div class="content">
            <div class="field">
                <div class="label">From:</div>
                <div class="value">{name} &lt;{email}&gt;</div>
            </div>
            <div class="field">
                <div class="label">Subject:</div>
                <div class="value">{subject}</div>
            </div>
            <div class="field">
                <div class="label">Message:</div>
                <div class="message-box">{message.replace(chr(10), '<br>')}</div>
            </div>
        </div>
        <div class="footer">
            <p>This message was sent from the Sabor Con Flow website contact form.</p>
            <p>Reply directly to this email to respond to {name}.</p>
        </div>
    </div>
</body>
</html>
    """

    email_message = EmailMessage(
        subject=f'[Website Contact] {subject} - from {name}',
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.CONTACT_EMAIL],
        reply_to=[f'{name} <{email}>'],
    )
    email_message.content_subtype = 'plain'
    email_message.send(fail_silently=False)
```

### URL Configuration

**File:** `core/urls.py` (update)

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('events', views.events, name='events'),
    path('pricing', views.pricing, name='pricing'),
    path('private-lessons', views.private_lessons, name='private_lessons'),
    path('contact', views.contact, name='contact'),
    path('contact/submit', views.contact_submit, name='contact_submit'),
]
```

### Django Email Settings

**File:** `sabor_con_flow/settings.py` (add to existing)

```python
# Email Configuration
# For production, use environment variables
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@saborconflowdance.com')
CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'saborconflowdance@gmail.com')

# For development/testing without email
if not EMAIL_HOST:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Contact Form HTML Template

**File:** `templates/contact.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="container main-content-contact">
    <h1 class="page-title">Get In Touch</h1>

    <!-- Contact Form Section -->
    <section class="contact-section contact-form-section" aria-labelledby="form-heading">
        <h2 id="form-heading" class="contact-title">Send Us a Message</h2>

        <!-- Success Message (hidden by default) -->
        <div id="form-success" class="form-message form-success" role="alert" aria-live="polite" hidden>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"
                 fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <span>Thank you! Your message has been sent successfully. We will get back to you soon.</span>
        </div>

        <!-- Error Message (hidden by default) -->
        <div id="form-error" class="form-message form-error" role="alert" aria-live="assertive" hidden>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"
                 fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            <span id="error-message">Something went wrong. Please try again or contact us directly.</span>
        </div>

        <form id="contact-form" class="contact-form" method="POST" action="{% url 'contact_submit' %}" novalidate>
            {% csrf_token %}

            <!-- Honeypot field for spam protection -->
            <div class="form-field-honeypot" aria-hidden="true">
                <label for="website">Website</label>
                <input type="text" id="website" name="website" tabindex="-1" autocomplete="off">
            </div>

            <div class="form-group">
                <label for="name" class="form-label">
                    Name <span class="required" aria-label="required">*</span>
                </label>
                <input
                    type="text"
                    id="name"
                    name="name"
                    class="form-input"
                    required
                    minlength="2"
                    maxlength="100"
                    autocomplete="name"
                    aria-describedby="name-error"
                    placeholder="Your full name"
                >
                <span id="name-error" class="form-error-text" role="alert" aria-live="polite"></span>
            </div>

            <div class="form-group">
                <label for="email" class="form-label">
                    Email <span class="required" aria-label="required">*</span>
                </label>
                <input
                    type="email"
                    id="email"
                    name="email"
                    class="form-input"
                    required
                    maxlength="254"
                    autocomplete="email"
                    aria-describedby="email-error"
                    placeholder="your.email@example.com"
                >
                <span id="email-error" class="form-error-text" role="alert" aria-live="polite"></span>
            </div>

            <div class="form-group">
                <label for="subject" class="form-label">Subject</label>
                <select id="subject" name="subject" class="form-input form-select">
                    <option value="general">General Inquiry</option>
                    <option value="classes">Class Information</option>
                    <option value="private">Private Lessons</option>
                    <option value="events">Events & Workshops</option>
                    <option value="other">Other</option>
                </select>
            </div>

            <div class="form-group">
                <label for="message" class="form-label">
                    Message <span class="required" aria-label="required">*</span>
                </label>
                <textarea
                    id="message"
                    name="message"
                    class="form-input form-textarea"
                    required
                    minlength="10"
                    maxlength="2000"
                    rows="6"
                    aria-describedby="message-error message-counter"
                    placeholder="How can we help you?"
                ></textarea>
                <div class="form-textarea-footer">
                    <span id="message-error" class="form-error-text" role="alert" aria-live="polite"></span>
                    <span id="message-counter" class="character-counter" aria-live="off">0 / 2000</span>
                </div>
            </div>

            <div class="form-actions">
                <button type="submit" id="submit-btn" class="btn btn-primary btn-submit">
                    <span class="btn-text">Send Message</span>
                    <span class="btn-loading" aria-hidden="true" hidden>
                        <svg class="spinner" viewBox="0 0 24 24" width="20" height="20">
                            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor"
                                    stroke-width="3" stroke-dasharray="30 70"/>
                        </svg>
                        Sending...
                    </span>
                </button>
            </div>
        </form>
    </section>

    <!-- Alternative Contact Methods -->
    <section class="contact-section" aria-labelledby="email-heading">
        <h2 id="email-heading" class="contact-title">Email Us Directly</h2>
        <div class="contact-item">
            <div class="contact-icon" aria-hidden="true">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36"
                     fill="#C7B375">
                    <path d="M0 0h24v24H0z" fill="none"/>
                    <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9
                             2-2V6c0-1.1-.9-2-2-2zm0 14H4V8l8 5 8-5v10zm-8-7L4 6h16l-8 5z"/>
                </svg>
            </div>
            <div>
                <p>For class information, booking, and general inquiries:</p>
                <a href="mailto:saborconflowdance@gmail.com" class="contact-link">
                    saborconflowdance@gmail.com
                </a>
            </div>
        </div>
    </section>

    <section class="contact-section" aria-labelledby="whatsapp-heading">
        <h2 id="whatsapp-heading" class="contact-title">Join Our WhatsApp Community</h2>
        <div class="contact-item">
            <div class="contact-icon" aria-hidden="true">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36">
                    <rect width="24" height="24" rx="6" ry="6" fill="#25D366"/>
                    <path fill="#ffffff" d="M17.6 6.2c-1.5-1.5-3.4-2.3-5.5-2.3-4.3 0-7.8 3.5-7.8
                          7.8 0 1.4.4 2.7 1 3.9l-1.1 4 4.1-1.1c1.1.6 2.4 1 3.7 1 4.3 0 7.8-3.5
                          7.8-7.8.1-2.1-.7-4-2.2-5.5zm-5.5 12c-1.2 0-2.3-.3-3.3-.9l-.2-.1-2.4.6.6-2.3
                          -.2-.2c-.6-1-1-2.2-1-3.4 0-3.6 2.9-6.5 6.5-6.5 1.7 0 3.3.7 4.6 1.9 1.2
                          1.2 1.9 2.8 1.9 4.6-.1 3.5-3 6.3-6.5 6.3zm3.6-4.9c-.2-.1-1.1-.6-1.3-.6
                          -.2-.1-.3-.1-.4.1-.1.2-.5.6-.6.8-.1.1-.2.1-.4 0-.6-.3-1.3-.7-1.9-1.3
                          -.8-.7-1.2-1.5-1.3-1.7-.1-.2 0-.3.1-.4l.3-.3s.1-.2.2-.3c.1-.1.1-.2.1-.3
                          0-.1 0-.2-.1-.3l-.6-1.4c-.1-.3-.3-.3-.4-.3h-.4c-.1 0-.3.1-.5.2-.2.1-.6.6
                          -.6 1.4s.6 1.6.7 1.7c.1.1 1.3 2 3.2 2.8.4.2.8.3 1 .3.2.1.5.1.7.1.2 0
                          .6-.3.7-.5.1-.3.1-.5.1-.6-.1-.1-.2-.1-.4-.2z"/>
                </svg>
            </div>
            <div>
                <p>Stay updated with class schedules, events, and connect with fellow dancers:</p>
                <a href="https://chat.whatsapp.com/GaZONDA1HgFG7C8djihJ1x"
                   target="_blank"
                   rel="noopener noreferrer"
                   class="whatsapp-button">
                    Join WhatsApp Group
                    <span class="sr-only">(opens in new tab)</span>
                </a>
            </div>
        </div>
    </section>

    <section class="contact-section" aria-labelledby="social-heading">
        <h2 id="social-heading" class="contact-title">Social Media</h2>
        <div class="contact-item">
            <div class="contact-icon" aria-hidden="true">
                <!-- Instagram icon SVG -->
            </div>
            <div>
                <p>Follow us on Instagram for photos, videos, and announcements:</p>
                <a href="https://www.instagram.com/saborconflow.dance/"
                   target="_blank"
                   rel="noopener noreferrer"
                   class="contact-link">
                    @saborconflow.dance
                    <span class="sr-only">(opens in new tab)</span>
                </a>
            </div>
        </div>
        <div class="contact-item">
            <div class="contact-icon" aria-hidden="true">
                <!-- Facebook icon SVG -->
            </div>
            <div>
                <p>Connect with us on Facebook:</p>
                <a href="https://www.facebook.com/profile.php?id=61575502290591"
                   target="_blank"
                   rel="noopener noreferrer"
                   class="contact-link">
                    Sabor Con Flow Dance
                    <span class="sr-only">(opens in new tab)</span>
                </a>
            </div>
        </div>
    </section>
</div>

<script src="{% static 'js/contact.js' %}"></script>
{% endblock %}
```

### Client-Side Validation JavaScript

**File:** `static/js/contact.js`

```javascript
/**
 * Contact Form Handler for Django Backend
 * Provides client-side validation and AJAX form submission with CSRF token
 */
(function() {
    'use strict';

    const form = document.getElementById('contact-form');
    if (!form) return;

    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    const successMsg = document.getElementById('form-success');
    const errorMsg = document.getElementById('form-error');
    const errorText = document.getElementById('error-message');
    const messageField = document.getElementById('message');
    const messageCounter = document.getElementById('message-counter');
    const honeypot = document.getElementById('website');

    // Get CSRF token from Django
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    // Validation rules
    const validators = {
        name: {
            validate: (value) => value.trim().length >= 2 && value.trim().length <= 100,
            message: 'Name must be between 2 and 100 characters'
        },
        email: {
            validate: (value) => {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                return emailRegex.test(value.trim()) && value.length <= 254;
            },
            message: 'Please enter a valid email address'
        },
        message: {
            validate: (value) => value.trim().length >= 10 && value.trim().length <= 2000,
            message: 'Message must be between 10 and 2000 characters'
        }
    };

    // Initialize character counter
    function updateCharacterCount() {
        const count = messageField.value.length;
        const max = 2000;
        messageCounter.textContent = `${count} / ${max}`;

        if (count > max * 0.9) {
            messageCounter.classList.add('warning');
        } else {
            messageCounter.classList.remove('warning');
        }

        if (count > max) {
            messageCounter.classList.add('error');
        } else {
            messageCounter.classList.remove('error');
        }
    }

    messageField.addEventListener('input', updateCharacterCount);

    // Validate a single field
    function validateField(field) {
        const name = field.name;
        const value = field.value;
        const errorElement = document.getElementById(`${name}-error`);
        const validator = validators[name];

        if (!validator) return true;

        const isValid = validator.validate(value);

        if (!isValid) {
            field.classList.add('invalid');
            field.classList.remove('valid');
            field.setAttribute('aria-invalid', 'true');
            if (errorElement) {
                errorElement.textContent = validator.message;
            }
        } else {
            field.classList.remove('invalid');
            field.classList.add('valid');
            field.setAttribute('aria-invalid', 'false');
            if (errorElement) {
                errorElement.textContent = '';
            }
        }

        return isValid;
    }

    // Validate all fields
    function validateForm() {
        const fields = form.querySelectorAll('[required]');
        let isValid = true;

        fields.forEach(field => {
            if (!validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    // Real-time validation on blur
    form.querySelectorAll('.form-input').forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => {
            if (input.classList.contains('invalid')) {
                validateField(input);
            }
        });
    });

    // Set loading state
    function setLoading(loading) {
        submitBtn.disabled = loading;
        btnText.hidden = loading;
        btnLoading.hidden = !loading;

        if (loading) {
            submitBtn.setAttribute('aria-busy', 'true');
        } else {
            submitBtn.removeAttribute('aria-busy');
        }
    }

    // Show message
    function showMessage(type, message) {
        successMsg.hidden = type !== 'success';
        errorMsg.hidden = type !== 'error';

        if (type === 'error' && message) {
            errorText.textContent = message;
        }

        // Scroll to message
        const msgElement = type === 'success' ? successMsg : errorMsg;
        msgElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        msgElement.focus();
    }

    // Hide messages
    function hideMessages() {
        successMsg.hidden = true;
        errorMsg.hidden = true;
    }

    // Reset form
    function resetForm() {
        form.reset();
        form.querySelectorAll('.form-input').forEach(input => {
            input.classList.remove('valid', 'invalid');
            input.removeAttribute('aria-invalid');
        });
        form.querySelectorAll('.form-error-text').forEach(error => {
            error.textContent = '';
        });
        updateCharacterCount();
    }

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Check honeypot (spam protection)
        if (honeypot && honeypot.value) {
            // Silently fail - likely a bot
            showMessage('success');
            resetForm();
            return;
        }

        hideMessages();

        if (!validateForm()) {
            // Focus first invalid field
            const firstInvalid = form.querySelector('.invalid');
            if (firstInvalid) {
                firstInvalid.focus();
            }
            return;
        }

        setLoading(true);

        const formData = new FormData(form);
        const data = {
            name: formData.get('name').trim(),
            email: formData.get('email').trim(),
            subject: formData.get('subject'),
            message: formData.get('message').trim(),
            website: formData.get('website') || ''  // Honeypot
        };

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                showMessage('success');
                resetForm();
            } else {
                showMessage('error', result.message || 'Failed to send message. Please try again.');
            }
        } catch (error) {
            console.error('Contact form error:', error);
            showMessage('error', 'Network error. Please check your connection and try again.');
        } finally {
            setLoading(false);
        }
    });

    // Initialize
    updateCharacterCount();
})();
```

### Contact Form CSS Styles

**Add to:** `static/css/styles.css`

(Same CSS as original spec - form styles are frontend-only and don't change)

---

## PR 6.2: Dependency Audit and Cleanup

### Overview

After Phase 1 removes Express.js, the npm dependencies become minimal. The site runs on
Django/Python, so Node.js is only needed for build tooling.

### Post-Phase 1 Package.json

**File:** `package.json` (after Express removal)

```json
{
  "name": "sabor-con-flow-dance",
  "version": "1.0.0",
  "private": true,
  "description": "Sabor con Flow Dance - Build tooling for static assets",
  "scripts": {
    "build": "vite build",
    "dev": "vite",
    "lint:css": "stylelint 'static/css/**/*.css'",
    "lint:css:fix": "stylelint 'static/css/**/*.css' --fix"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "stylelint": "^16.0.0",
    "stylelint-config-standard": "^36.0.0"
  }
}
```

### Python Dependencies

**File:** `requirements.txt`

```text
Django>=5.2.1
whitenoise>=6.6.0
gunicorn>=21.2.0
```

### Dependency Count Comparison

| Metric | Before Phase 1 | After Phase 1 | After Phase 6 |
|--------|----------------|---------------|---------------|
| npm direct deps | 957 | 0 | 3 (dev only) |
| npm total (node_modules) | ~1200 | 0 | ~50 |
| Python deps | 4 | 4 | 4 |
| node_modules size | ~500MB | 0 | ~20MB |

---

## PR 6.3: Accessibility and SEO Polish

### Overview

Comprehensive WCAG AA compliance audit, SEO optimization, and final polish.

### Django Template Updates

**File:** `templates/base.html` (layout equivalent)

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- Primary Meta Tags -->
    <title>{{ title|default:"Sabor Con Flow - Cuban Salsa Dance Classes in Boulder" }}</title>
    <meta name="description" content="{{ description|default:"Learn Cuban salsa, casino, and Afro-Cuban dance in Boulder, Colorado. Weekly classes for all levels, private lessons, and community events." }}">
    <meta name="keywords" content="cuban salsa, casino dance, salsa classes boulder, cuban dance colorado, afro-cuban dance, dance lessons boulder">
    <meta name="author" content="Sabor Con Flow Dance">
    <meta name="robots" content="index, follow">

    <!-- Canonical URL -->
    <link rel="canonical" href="https://www.saborconflowdance.com{{ canonical_path|default:"" }}">

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://www.saborconflowdance.com{{ canonical_path|default:"" }}">
    <meta property="og:title" content="{{ og_title|default:title|default:"Sabor Con Flow - Cuban Salsa Dance Classes" }}">
    <meta property="og:description" content="{{ og_description|default:"Learn Cuban salsa, casino, and Afro-Cuban dance in Boulder, Colorado." }}">
    <meta property="og:image" content="https://www.saborconflowdance.com{% static 'images/og-image.jpg' %}">
    <meta property="og:locale" content="en_US">
    <meta property="og:site_name" content="Sabor Con Flow Dance">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{{ title|default:"Sabor Con Flow - Cuban Salsa Dance Classes" }}">
    <meta name="twitter:description" content="{{ description|default:"Learn Cuban salsa, casino, and Afro-Cuban dance in Boulder, Colorado." }}">
    <meta name="twitter:image" content="https://www.saborconflowdance.com{% static 'images/og-image.jpg' %}">

    <!-- Favicon -->
    <link rel="icon" type="image/png" href="{% static 'images/favicon/favicon.png' %}">
    <link rel="apple-touch-icon" sizes="180x180" href="{% static 'images/sabor-con-flow-logo.png' %}">
    <meta name="theme-color" content="#000000">

    <!-- Fonts (after Phase 1 Bootstrap removal) -->
    <link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

    <!-- Stylesheets (after Phase 2 CSS modularization) -->
    <link href="{% static 'css/main.css' %}" rel="stylesheet">

    <!-- JSON-LD Structured Data -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "DanceSchool",
        "name": "Sabor Con Flow Dance",
        "description": "Cuban salsa, casino, and Afro-Cuban dance classes in Boulder, Colorado.",
        "url": "https://www.saborconflowdance.com",
        "email": "saborconflowdance@gmail.com",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Boulder",
            "addressRegion": "CO",
            "addressCountry": "US"
        },
        "sameAs": [
            "https://www.instagram.com/saborconflow.dance/",
            "https://www.facebook.com/profile.php?id=61575502290591"
        ],
        "priceRange": "$$"
    }
    </script>
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>

    <header class="header" role="banner">
        <button
            class="menu-toggle"
            aria-label="Open navigation menu"
            aria-expanded="false"
            aria-controls="main-navigation"
        >
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
        </button>
        <a href="{% url 'home' %}" class="header-logo-link" aria-label="Sabor Con Flow - Home">
            <img src="{% static 'images/sabor-con-flow-logo.png' %}" alt="" class="header-logo" aria-hidden="true">
        </a>
        <nav id="main-navigation" class="nav" role="navigation" aria-label="Main navigation">
            <a href="{% url 'home' %}"><span>Home</span></a>
            <a href="{% url 'about' %}"><span>About</span></a>
            <a href="{% url 'events' %}"><span>Events</span></a>
            <a href="{% url 'pricing' %}"><span>Pricing</span></a>
            <a href="{% url 'private_lessons' %}"><span>Private Lessons</span></a>
            <a href="{% url 'contact' %}"><span>Contact</span></a>
        </nav>
    </header>

    <main id="main-content" class="main-content" role="main">
        {% block content %}{% endblock %}
    </main>

    <footer class="footer" role="contentinfo">
        <div class="container">
            <nav class="social-links" aria-label="Social media links">
                <!-- Social icons with aria-labels -->
            </nav>
            <p><small>&copy; {% now "Y" %} Sabor Con Flow Dance. All rights reserved.</small></p>
        </div>
    </footer>

    <script src="{% static 'js/main.js' %}"></script>
</body>
</html>
```

### View Updates for SEO Meta

**File:** `core/views.py` (update existing views)

```python
# Page meta data dictionary
PAGE_META = {
    'home': {
        'title': 'Sabor Con Flow - Cuban Salsa Dance Classes in Boulder',
        'description': 'Learn Cuban salsa, casino, and Afro-Cuban dance in Boulder, Colorado. Weekly classes for all levels, private lessons, and community events.',
        'canonical_path': '/',
    },
    'about': {
        'title': 'About Us - Sabor Con Flow Dance',
        'description': 'Meet our instructors and learn about our mission to bring authentic Cuban dance culture to Boulder, Colorado.',
        'canonical_path': '/about',
    },
    'events': {
        'title': 'Dance Classes & Events - Sabor Con Flow',
        'description': 'Weekly Cuban salsa classes every Sunday at Avalon Ballroom. Pasos Basicos, Casino Royale, and SCF Choreo Team.',
        'canonical_path': '/events',
    },
    'pricing': {
        'title': 'Class Pricing - Sabor Con Flow Dance',
        'description': 'Affordable dance class pricing. Drop-in $20, monthly passes available. Private lessons starting at $80.',
        'canonical_path': '/pricing',
    },
    'private_lessons': {
        'title': 'Private Dance Lessons - Sabor Con Flow',
        'description': 'One-on-one Cuban salsa instruction tailored to your goals. Perfect for beginners, wedding prep, or advanced technique.',
        'canonical_path': '/private-lessons',
    },
    'contact': {
        'title': 'Contact Us - Sabor Con Flow Dance',
        'description': 'Get in touch with Sabor Con Flow Dance. Questions about classes? Send us a message or join our WhatsApp community.',
        'canonical_path': '/contact',
    },
}


def home(request):
    return render(request, 'home.html', PAGE_META['home'])


def about(request):
    return render(request, 'about.html', PAGE_META['about'])


def events(request):
    context = {**PAGE_META['events'], 'events': get_events()}
    return render(request, 'events.html', context)


def pricing(request):
    return render(request, 'pricing.html', PAGE_META['pricing'])


def private_lessons(request):
    return render(request, 'private-lessons.html', PAGE_META['private_lessons'])


def contact(request):
    return render(request, 'contact.html', PAGE_META['contact'])
```

---

## Testing Checklist

### PR 6.1 Tests

**File:** `core/tests/test_contact.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
import json


class ContactFormTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.submit_url = reverse('contact_submit')

    def test_contact_page_loads(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Get In Touch')

    def test_valid_submission(self):
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'general',
            'message': 'This is a test message for the contact form.'
        }
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['success'])

    def test_empty_name_rejected(self):
        data = {
            'name': '',
            'email': 'test@example.com',
            'subject': 'general',
            'message': 'Test message here.'
        }
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_email_rejected(self):
        data = {
            'name': 'Test User',
            'email': 'not-an-email',
            'subject': 'general',
            'message': 'Test message here.'
        }
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_short_message_rejected(self):
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'general',
            'message': 'Short'
        }
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_honeypot_silently_succeeds(self):
        """Spam submissions should appear successful but not send email."""
        data = {
            'name': 'Spam Bot',
            'email': 'spam@example.com',
            'subject': 'general',
            'message': 'Buy cheap products at spam.com',
            'website': 'http://spam.com'  # Honeypot filled
        }
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['success'])  # Appears successful to bot
```

### Run Tests

```bash
# Django tests
python manage.py test core.tests.test_contact

# All tests
python manage.py test
```

---

## Success Criteria

### PR 6.1: Contact Form

- [ ] Form renders correctly with Django CSRF token
- [ ] Client-side validation prevents invalid submissions
- [ ] Server-side validation matches client rules
- [ ] Email notifications sent when configured
- [ ] Honeypot blocks spam silently
- [ ] Form is fully keyboard accessible
- [ ] Mobile responsive design

### PR 6.2: Dependencies

- [ ] npm dependencies reduced to ~3 dev packages (Vite, Stylelint)
- [ ] Python requirements unchanged
- [ ] Site deploys successfully to Vercel
- [ ] No runtime errors

### PR 6.3: A11y & SEO

- [ ] Lighthouse accessibility score > 95
- [ ] All pages have unique meta descriptions
- [ ] Open Graph images render in social previews
- [ ] JSON-LD validates in Google's testing tool
- [ ] Skip link works correctly
- [ ] Keyboard navigation complete
- [ ] Screen reader testing passed

---

## Appendix: File Changes Summary

### New Files

| File | Description |
|------|-------------|
| `core/forms.py` | Django contact form class |
| `static/js/contact.js` | Client-side form validation |

### Modified Files

| File | Changes |
|------|---------|
| `templates/contact.html` | Add contact form with CSRF |
| `templates/base.html` | SEO meta, JSON-LD, a11y |
| `core/views.py` | Contact submit view, SEO meta |
| `core/urls.py` | Add contact submit URL |
| `sabor_con_flow/settings.py` | Email configuration |
| `static/css/styles.css` | Form styles |
| `package.json` | Minimal dev dependencies |

---

**Document Version:** 2.0 (Corrected for Django architecture)
**Last Updated:** 2024-12-10
**Author:** Principal Architect Agent (with corrections)
