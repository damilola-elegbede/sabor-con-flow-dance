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
