from django import forms
from django.core.validators import MinLengthValidator
from .models import Testimonial, ContactSubmission, BookingConfirmation

class TestimonialForm(forms.ModelForm):
    """Form for submitting student testimonials."""
    
    CLASS_TYPE_CHOICES = [
        ('', 'Select a class type'),
        ('choreo_team', 'SCF Choreo Team'),
        ('pasos_basicos', 'Pasos Básicos'),
        ('casino_royale', 'Casino Royale'),
        ('private_lesson', 'Private Lesson'),
        ('workshop', 'Workshop'),
        ('other', 'Other'),
    ]
    
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    student_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'required': True,
        }),
        help_text='Your name will be displayed with your testimonial'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
            'required': True,
        }),
        help_text='We\'ll use this to contact you if needed (not displayed publicly)'
    )
    
    class_type = forms.ChoiceField(
        choices=CLASS_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True,
        }),
        help_text='Which class or service are you reviewing?'
    )
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'rating-radio',
        }),
        help_text='How would you rate your experience?'
    )
    
    content = forms.CharField(
        validators=[MinLengthValidator(50)],
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Share your dance journey and experience with Sabor Con Flow...',
            'rows': 6,
            'required': True,
            'maxlength': 500,
            'data-min-length': '50',
        }),
        help_text='Minimum 50 characters, maximum 500 characters'
    )
    
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/*',
            'data-preview': 'true',
        }),
        help_text='Optional: Upload a photo from your dance experience (max 5MB)'
    )
    
    class Meta:
        model = Testimonial
        fields = ['student_name', 'email', 'class_type', 'rating', 'content', 'photo']
    
    def clean_rating(self):
        """Validate rating is between 1 and 5."""
        rating = self.cleaned_data.get('rating')
        if rating:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise forms.ValidationError('Rating must be between 1 and 5 stars.')
        return rating
    
    def clean_content(self):
        """Validate content length and content."""
        content = self.cleaned_data.get('content')
        if content:
            if len(content.strip()) < 50:
                raise forms.ValidationError('Your testimonial must be at least 50 characters long.')
            if len(content) > 500:
                raise forms.ValidationError('Your testimonial cannot exceed 500 characters.')
        return content.strip()
    
    def clean_photo(self):
        """Validate photo size and format."""
        photo = self.cleaned_data.get('photo')
        if photo:
            # Check file size (5MB limit)
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Photo size cannot exceed 5MB.')
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if photo.content_type not in allowed_types:
                raise forms.ValidationError('Please upload a valid image file (JPEG, PNG, GIF, or WebP).')
        
        return photo 


class ContactForm(forms.ModelForm):
    """
    Contact form for general inquiries and booking requests.
    SPEC_05 Group B Task 10 - Comprehensive email notifications system.
    """
    
    INTEREST_CHOICES = [
        ('', 'What are you interested in?'),
        ('classes', 'Group Classes'),
        ('private_lesson', 'Private Lessons'),
        ('workshop', 'Workshops'),
        ('events', 'Events & Performances'),
        ('choreography', 'Choreography Services'),
        ('general', 'General Inquiry'),
        ('other', 'Other'),
    ]
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'required': True,
        }),
        help_text='Your full name'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
            'required': True,
        }),
        help_text='We\'ll use this to respond to your inquiry'
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(555) 123-4567',
            'type': 'tel',
        }),
        help_text='Optional - for urgent inquiries or booking confirmations'
    )
    
    interest = forms.ChoiceField(
        choices=INTEREST_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True,
        }),
        help_text='Select what you\'re most interested in'
    )
    
    message = forms.CharField(
        validators=[MinLengthValidator(20)],
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Tell us about your inquiry, questions, or what you\'d like to learn...',
            'rows': 5,
            'required': True,
            'maxlength': 1000,
            'data-min-length': '20',
        }),
        help_text='Minimum 20 characters, maximum 1000 characters'
    )
    
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'phone', 'interest', 'message']
    
    def clean_message(self):
        """Validate message content and length."""
        message = self.cleaned_data.get('message')
        if message:
            if len(message.strip()) < 20:
                raise forms.ValidationError('Your message must be at least 20 characters long.')
            if len(message) > 1000:
                raise forms.ValidationError('Your message cannot exceed 1000 characters.')
        return message.strip()
    
    def clean_phone(self):
        """Validate phone number format if provided."""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove all non-digit characters
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) < 10:
                raise forms.ValidationError('Please enter a valid phone number.')
            # Format as (XXX) XXX-XXXX for US numbers
            if len(phone_digits) == 10:
                phone = f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
            elif len(phone_digits) == 11 and phone_digits[0] == '1':
                phone = f"({phone_digits[1:4]}) {phone_digits[4:7]}-{phone_digits[7:]}"
        return phone


class BookingForm(forms.ModelForm):
    """
    Booking form for class and lesson confirmations.
    SPEC_05 Group B Task 10 - Booking confirmation emails.
    """
    
    BOOKING_TYPE_CHOICES = [
        ('', 'Select booking type'),
        ('class', 'Group Class'),
        ('private_lesson', 'Private Lesson'),
        ('workshop', 'Workshop'),
        ('package', 'Class Package'),
        ('event', 'Special Event'),
    ]
    
    customer_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'required': True,
        })
    )
    
    customer_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
            'required': True,
        })
    )
    
    customer_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(555) 123-4567',
            'type': 'tel',
        })
    )
    
    booking_type = forms.ChoiceField(
        choices=BOOKING_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True,
        })
    )
    
    class_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Pasos Básicos, Private Lesson with Maria',
            'required': True,
        })
    )
    
    instructor_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Instructor name (if known)',
        })
    )
    
    booking_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
            'required': True,
        })
    )
    
    duration_minutes = forms.IntegerField(
        initial=60,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '30',
            'max': '180',
            'step': '15',
        })
    )
    
    price = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'step': '0.01',
            'required': True,
        })
    )
    
    payment_method = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Cash, Venmo, PayPal',
        })
    )
    
    special_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Any special requests or notes...',
            'rows': 3,
            'maxlength': 500,
        })
    )
    
    class Meta:
        model = BookingConfirmation
        fields = [
            'customer_name', 'customer_email', 'customer_phone',
            'booking_type', 'class_name', 'instructor_name',
            'booking_date', 'duration_minutes', 'price',
            'payment_method', 'special_instructions'
        ]
    
    def clean_booking_date(self):
        """Validate booking date is in the future."""
        booking_date = self.cleaned_data.get('booking_date')
        if booking_date:
            from django.utils import timezone
            if booking_date <= timezone.now():
                raise forms.ValidationError('Booking date must be in the future.')
        return booking_date
    
    def clean_price(self):
        """Validate price is reasonable."""
        price = self.cleaned_data.get('price')
        if price:
            if price < 0:
                raise forms.ValidationError('Price cannot be negative.')
            if price > 500:
                raise forms.ValidationError('Price seems unusually high. Please verify.')
        return price