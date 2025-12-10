"""
Comprehensive tests for Contact and Booking Forms - SPEC_05 Group B Task 10

Tests ContactForm, BookingForm validation, processing, integration with views,
and email notification workflows.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from django.test import TestCase, Client, override_settings
from django.core import mail
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse
from core.forms import ContactForm, BookingForm
from core.models import ContactSubmission, BookingConfirmation


class ContactFormTestCase(TestCase):
    """Test cases for the ContactForm."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_contact_data = {
            'name': 'Maria Rodriguez',
            'email': 'maria.rodriguez@example.com',
            'phone': '(555) 123-4567',
            'interest': 'private_lesson',
            'message': 'I would like to schedule private salsa lessons for beginners. What are your rates and availability?'
        }
    
    def test_contact_form_valid_data(self):
        """Test ContactForm with valid data."""
        form = ContactForm(data=self.valid_contact_data)
        self.assertTrue(form.is_valid())
        
        # Test that cleaned data is properly processed
        self.assertEqual(form.cleaned_data['name'], 'Maria Rodriguez')
        self.assertEqual(form.cleaned_data['email'], 'maria.rodriguez@example.com')
        self.assertEqual(form.cleaned_data['phone'], '(555) 123-4567')
        self.assertEqual(form.cleaned_data['interest'], 'private_lesson')
        self.assertIn('private salsa lessons', form.cleaned_data['message'])
    
    def test_contact_form_required_fields(self):
        """Test ContactForm required field validation."""
        # Test missing name
        invalid_data = self.valid_contact_data.copy()
        del invalid_data['name']
        form = ContactForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        
        # Test missing email
        invalid_data = self.valid_contact_data.copy()
        del invalid_data['email']
        form = ContactForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
        # Test missing interest
        invalid_data = self.valid_contact_data.copy()
        del invalid_data['interest']
        form = ContactForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('interest', form.errors)
        
        # Test missing message
        invalid_data = self.valid_contact_data.copy()
        del invalid_data['message']
        form = ContactForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
    
    def test_contact_form_email_validation(self):
        """Test email field validation."""
        invalid_emails = [
            'invalid-email',
            'test@',
            '@example.com',
            'test..test@example.com',
            'test@example',
            'test@.com'
        ]
        
        for email in invalid_emails:
            invalid_data = self.valid_contact_data.copy()
            invalid_data['email'] = email
            form = ContactForm(data=invalid_data)
            self.assertFalse(form.is_valid())
            self.assertIn('email', form.errors)
    
    def test_contact_form_phone_validation(self):
        """Test phone number validation and formatting."""
        # Test valid phone formats
        valid_phones = [
            '5551234567',
            '(555) 123-4567',
            '555-123-4567',
            '555.123.4567',
            '1-555-123-4567',
            '+1 555 123 4567'
        ]
        
        for phone in valid_phones:
            test_data = self.valid_contact_data.copy()
            test_data['phone'] = phone
            form = ContactForm(data=test_data)
            self.assertTrue(form.is_valid())
            
            # Check that phone is formatted consistently
            cleaned_phone = form.cleaned_data['phone']
            if cleaned_phone:  # Phone is optional
                self.assertRegex(cleaned_phone, r'^\(\d{3}\) \d{3}-\d{4}$')
        
        # Test invalid phone numbers
        invalid_phones = [
            '123',
            '555-123-456',  # Too short
            'abc-def-ghij',  # Non-numeric
            '555-123-45678'  # Too long for US
        ]
        
        for phone in invalid_phones:
            test_data = self.valid_contact_data.copy()
            test_data['phone'] = phone
            form = ContactForm(data=test_data)
            self.assertFalse(form.is_valid())
            self.assertIn('phone', form.errors)
    
    def test_contact_form_phone_optional(self):
        """Test that phone field is optional."""
        test_data = self.valid_contact_data.copy()
        test_data['phone'] = ''
        form = ContactForm(data=test_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['phone'], '')
    
    def test_contact_form_message_length_validation(self):
        """Test message length validation."""
        # Test too short message
        short_data = self.valid_contact_data.copy()
        short_data['message'] = 'Too short'  # Less than 20 characters
        form = ContactForm(data=short_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
        
        # Test too long message
        long_data = self.valid_contact_data.copy()
        long_data['message'] = 'x' * 1001  # More than 1000 characters
        form = ContactForm(data=long_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
        
        # Test valid length message
        valid_data = self.valid_contact_data.copy()
        valid_data['message'] = 'This is a message with exactly twenty characters to test minimum length.'
        form = ContactForm(data=valid_data)
        self.assertTrue(form.is_valid())
    
    def test_contact_form_interest_choices(self):
        """Test interest field choices validation."""
        valid_interests = [
            'classes',
            'private_lesson',
            'workshop',
            'events',
            'choreography',
            'general',
            'other'
        ]
        
        for interest in valid_interests:
            test_data = self.valid_contact_data.copy()
            test_data['interest'] = interest
            form = ContactForm(data=test_data)
            self.assertTrue(form.is_valid())
            self.assertEqual(form.cleaned_data['interest'], interest)
        
        # Test invalid interest
        invalid_data = self.valid_contact_data.copy()
        invalid_data['interest'] = 'invalid_choice'
        form = ContactForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('interest', form.errors)
    
    def test_contact_form_clean_message(self):
        """Test message cleaning and stripping."""
        test_data = self.valid_contact_data.copy()
        test_data['message'] = '   This message has extra whitespace   '
        form = ContactForm(data=test_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['message'], 'This message has extra whitespace')
    
    def test_contact_form_model_integration(self):
        """Test ContactForm integration with ContactSubmission model."""
        form = ContactForm(data=self.valid_contact_data)
        self.assertTrue(form.is_valid())
        
        # Test saving the form creates a ContactSubmission
        contact = form.save()
        self.assertIsInstance(contact, ContactSubmission)
        self.assertEqual(contact.name, 'Maria Rodriguez')
        self.assertEqual(contact.email, 'maria.rodriguez@example.com')
        self.assertEqual(contact.interest, 'private_lesson')
        self.assertEqual(contact.status, 'new')  # Default status
        self.assertFalse(contact.admin_notification_sent)  # Default
        self.assertFalse(contact.auto_reply_sent)  # Default


class BookingFormTestCase(TestCase):
    """Test cases for the BookingForm."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_booking_data = {
            'customer_name': 'Carlos Mendez',
            'customer_email': 'carlos.mendez@example.com',
            'customer_phone': '(555) 987-6543',
            'booking_type': 'private_lesson',
            'class_name': 'Private Bachata Lesson',
            'instructor_name': 'Sofia Martinez',
            'booking_date': timezone.now() + timedelta(days=3),
            'duration_minutes': 60,
            'price': Decimal('85.00'),
            'payment_method': 'Venmo',
            'special_instructions': 'Please focus on beginner footwork and basic turns.'
        }
    
    def test_booking_form_valid_data(self):
        """Test BookingForm with valid data."""
        form = BookingForm(data=self.valid_booking_data)
        self.assertTrue(form.is_valid())
        
        # Test cleaned data
        self.assertEqual(form.cleaned_data['customer_name'], 'Carlos Mendez')
        self.assertEqual(form.cleaned_data['customer_email'], 'carlos.mendez@example.com')
        self.assertEqual(form.cleaned_data['booking_type'], 'private_lesson')
        self.assertEqual(form.cleaned_data['class_name'], 'Private Bachata Lesson')
        self.assertEqual(form.cleaned_data['instructor_name'], 'Sofia Martinez')
        self.assertEqual(form.cleaned_data['duration_minutes'], 60)
        self.assertEqual(form.cleaned_data['price'], Decimal('85.00'))
    
    def test_booking_form_required_fields(self):
        """Test BookingForm required field validation."""
        required_fields = [
            'customer_name',
            'customer_email',
            'booking_type',
            'class_name',
            'booking_date',
            'price'
        ]
        
        for field in required_fields:
            invalid_data = self.valid_booking_data.copy()
            del invalid_data[field]
            form = BookingForm(data=invalid_data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)
    
    def test_booking_form_optional_fields(self):
        """Test that optional fields can be empty."""
        optional_fields = [
            'customer_phone',
            'instructor_name',
            'payment_method',
            'special_instructions'
        ]
        
        for field in optional_fields:
            test_data = self.valid_booking_data.copy()
            test_data[field] = ''
            form = BookingForm(data=test_data)
            self.assertTrue(form.is_valid())
    
    def test_booking_form_booking_type_choices(self):
        """Test booking type choices validation."""
        valid_types = [
            'class',
            'private_lesson',
            'workshop',
            'package',
            'event'
        ]
        
        for booking_type in valid_types:
            test_data = self.valid_booking_data.copy()
            test_data['booking_type'] = booking_type
            form = BookingForm(data=test_data)
            self.assertTrue(form.is_valid())
            self.assertEqual(form.cleaned_data['booking_type'], booking_type)
        
        # Test invalid booking type
        invalid_data = self.valid_booking_data.copy()
        invalid_data['booking_type'] = 'invalid_type'
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('booking_type', form.errors)
    
    def test_booking_form_date_validation(self):
        """Test booking date validation."""
        # Test past date
        past_data = self.valid_booking_data.copy()
        past_data['booking_date'] = timezone.now() - timedelta(days=1)
        form = BookingForm(data=past_data)
        self.assertFalse(form.is_valid())
        self.assertIn('booking_date', form.errors)
        self.assertIn('must be in the future', str(form.errors['booking_date']))
        
        # Test current time (should be invalid)
        now_data = self.valid_booking_data.copy()
        now_data['booking_date'] = timezone.now()
        form = BookingForm(data=now_data)
        self.assertFalse(form.is_valid())
        self.assertIn('booking_date', form.errors)
        
        # Test future date (should be valid)
        future_data = self.valid_booking_data.copy()
        future_data['booking_date'] = timezone.now() + timedelta(hours=1)
        form = BookingForm(data=future_data)
        self.assertTrue(form.is_valid())
    
    def test_booking_form_price_validation(self):
        """Test price field validation."""
        # Test negative price
        negative_data = self.valid_booking_data.copy()
        negative_data['price'] = Decimal('-10.00')
        form = BookingForm(data=negative_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        self.assertIn('cannot be negative', str(form.errors['price']))
        
        # Test very high price
        high_data = self.valid_booking_data.copy()
        high_data['price'] = Decimal('600.00')
        form = BookingForm(data=high_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        self.assertIn('unusually high', str(form.errors['price']))
        
        # Test zero price (should be valid)
        zero_data = self.valid_booking_data.copy()
        zero_data['price'] = Decimal('0.00')
        form = BookingForm(data=zero_data)
        self.assertTrue(form.is_valid())
        
        # Test reasonable price (should be valid)
        reasonable_data = self.valid_booking_data.copy()
        reasonable_data['price'] = Decimal('75.50')
        form = BookingForm(data=reasonable_data)
        self.assertTrue(form.is_valid())
    
    def test_booking_form_duration_validation(self):
        """Test duration minutes field validation."""
        # Test minimum duration
        test_data = self.valid_booking_data.copy()
        test_data['duration_minutes'] = 30
        form = BookingForm(data=test_data)
        self.assertTrue(form.is_valid())
        
        # Test maximum duration
        test_data['duration_minutes'] = 180
        form = BookingForm(data=test_data)
        self.assertTrue(form.is_valid())
        
        # Test default duration
        test_data['duration_minutes'] = 60
        form = BookingForm(data=test_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['duration_minutes'], 60)
    
    def test_booking_form_model_integration(self):
        """Test BookingForm integration with BookingConfirmation model."""
        form = BookingForm(data=self.valid_booking_data)
        self.assertTrue(form.is_valid())
        
        # Test saving the form creates a BookingConfirmation
        booking = form.save()
        self.assertIsInstance(booking, BookingConfirmation)
        self.assertEqual(booking.customer_name, 'Carlos Mendez')
        self.assertEqual(booking.customer_email, 'carlos.mendez@example.com')
        self.assertEqual(booking.booking_type, 'private_lesson')
        self.assertEqual(booking.status, 'confirmed')  # Default status
        self.assertIsNotNone(booking.booking_id)  # Should auto-generate
        self.assertFalse(booking.confirmation_email_sent)  # Default
        self.assertFalse(booking.reminder_email_sent)  # Default


class ContactFormViewIntegrationTestCase(TestCase):
    """Test cases for ContactForm integration with views."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.valid_contact_data = {
            'name': 'Integration Test User',
            'email': 'integration@example.com',
            'phone': '(555) 123-4567',
            'interest': 'classes',
            'message': 'I am interested in joining your group salsa classes. What are the schedules and prices?'
        }
    
    def test_contact_form_get_request(self):
        """Test GET request to contact form page."""
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contact Us')
        self.assertContains(response, 'name')
        self.assertContains(response, 'email')
        self.assertContains(response, 'interest')
        self.assertContains(response, 'message')
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_contact_form_valid_submission(self):
        """Test valid contact form submission."""
        response = self.client.post('/contact/', data=self.valid_contact_data)
        
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/contact/success/')
        
        # Should create ContactSubmission record
        contact = ContactSubmission.objects.get(email='integration@example.com')
        self.assertEqual(contact.name, 'Integration Test User')
        self.assertEqual(contact.interest, 'classes')
        self.assertEqual(contact.status, 'new')
    
    def test_contact_form_invalid_submission(self):
        """Test invalid contact form submission."""
        invalid_data = self.valid_contact_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        response = self.client.post('/contact/', data=invalid_data)
        
        # Should not redirect, should show form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the errors')
        self.assertContains(response, 'Enter a valid email address')
        
        # Should not create ContactSubmission record
        self.assertEqual(ContactSubmission.objects.count(), 0)
    
    def test_contact_form_empty_submission(self):
        """Test empty contact form submission."""
        response = self.client.post('/contact/', data={})
        
        # Should not redirect, should show form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')
        
        # Should not create ContactSubmission record
        self.assertEqual(ContactSubmission.objects.count(), 0)
    
    def test_contact_success_page(self):
        """Test contact success page."""
        response = self.client.get('/contact/success/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank You')


class BookingFormViewIntegrationTestCase(TestCase):
    """Test cases for BookingForm integration with views."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.valid_booking_data = {
            'customer_name': 'Booking Test User',
            'customer_email': 'booking@example.com',
            'customer_phone': '(555) 987-6543',
            'booking_type': 'private_lesson',
            'class_name': 'Private Salsa Lesson',
            'instructor_name': 'Test Instructor',
            'booking_date': (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
            'duration_minutes': 90,
            'price': '100.00',
            'payment_method': 'Cash',
            'special_instructions': 'Please bring your own dance shoes.'
        }
    
    def test_booking_form_get_request(self):
        """Test GET request to booking form page."""
        response = self.client.get('/booking/create/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Book a Class')
        self.assertContains(response, 'customer_name')
        self.assertContains(response, 'customer_email')
        self.assertContains(response, 'booking_type')
        self.assertContains(response, 'booking_date')
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_booking_form_valid_submission(self):
        """Test valid booking form submission."""
        response = self.client.post('/booking/create/', data=self.valid_booking_data)
        
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)
        
        # Should create BookingConfirmation record
        booking = BookingConfirmation.objects.get(customer_email='booking@example.com')
        self.assertEqual(booking.customer_name, 'Booking Test User')
        self.assertEqual(booking.booking_type, 'private_lesson')
        self.assertEqual(booking.class_name, 'Private Salsa Lesson')
        self.assertEqual(booking.price, Decimal('100.00'))
        self.assertIsNotNone(booking.booking_id)
        
        # Should redirect to success page with booking ID
        self.assertRedirects(response, f'/booking/success/{booking.booking_id}/')
    
    def test_booking_form_invalid_submission(self):
        """Test invalid booking form submission."""
        invalid_data = self.valid_booking_data.copy()
        invalid_data['price'] = '-50.00'  # Invalid negative price
        
        response = self.client.post('/booking/create/', data=invalid_data)
        
        # Should not redirect, should show form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the errors')
        self.assertContains(response, 'cannot be negative')
        
        # Should not create BookingConfirmation record
        self.assertEqual(BookingConfirmation.objects.count(), 0)
    
    def test_booking_success_page(self):
        """Test booking success page."""
        # Create a booking first
        booking = BookingConfirmation.objects.create(
            customer_name='Success Test',
            customer_email='success@example.com',
            booking_type='class',
            class_name='Test Class',
            booking_date=timezone.now() + timedelta(days=1),
            price=Decimal('20.00')
        )
        
        response = self.client.get(f'/booking/success/{booking.booking_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Booking Confirmed')
        self.assertContains(response, booking.booking_id)
        self.assertContains(response, 'Success Test')


class FormSecurityTestCase(TestCase):
    """Test cases for form security and validation edge cases."""
    
    def test_contact_form_xss_prevention(self):
        """Test that contact form prevents XSS attacks."""
        xss_data = {
            'name': '<script>alert("xss")</script>',
            'email': 'test@example.com',
            'interest': 'classes',
            'message': 'This message contains <script>alert("xss")</script> JavaScript.'
        }
        
        form = ContactForm(data=xss_data)
        self.assertTrue(form.is_valid())  # Form should still be valid
        
        # But the data should be properly escaped when saved
        contact = form.save()
        self.assertIn('<script>', contact.name)  # Script tags preserved but will be escaped in templates
        self.assertIn('<script>', contact.message)
    
    def test_booking_form_sql_injection_prevention(self):
        """Test that booking form prevents SQL injection attacks."""
        sql_injection_data = {
            'customer_name': "'; DROP TABLE bookings; --",
            'customer_email': 'test@example.com',
            'booking_type': 'class',
            'class_name': 'Test Class',
            'booking_date': timezone.now() + timedelta(days=1),
            'price': '20.00'
        }
        
        form = BookingForm(data=sql_injection_data)
        self.assertTrue(form.is_valid())  # Django ORM prevents SQL injection
        
        booking = form.save()
        self.assertEqual(booking.customer_name, "'; DROP TABLE bookings; --")
        # Table should still exist (SQL injection prevented)
        self.assertEqual(BookingConfirmation.objects.count(), 1)
    
    def test_form_csrf_protection(self):
        """Test that forms include CSRF protection."""
        # Test contact form CSRF
        response = self.client.get('/contact/')
        self.assertContains(response, 'csrfmiddlewaretoken')
        
        # Test booking form CSRF
        response = self.client.get('/booking/create/')
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_form_data_length_limits(self):
        """Test that forms respect field length limits."""
        # Test contact form with very long data
        long_data = {
            'name': 'x' * 101,  # Exceeds max_length=100
            'email': 'test@example.com',
            'interest': 'classes',
            'message': 'Valid message length.'
        }
        
        form = ContactForm(data=long_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        
        # Test booking form with very long data
        long_booking_data = {
            'customer_name': 'x' * 101,  # Exceeds max_length=100
            'customer_email': 'test@example.com',
            'booking_type': 'class',
            'class_name': 'Test Class',
            'booking_date': timezone.now() + timedelta(days=1),
            'price': '20.00'
        }
        
        form = BookingForm(data=long_booking_data)
        self.assertFalse(form.is_valid())
        self.assertIn('customer_name', form.errors)
    
    def test_form_unicode_handling(self):
        """Test that forms properly handle Unicode characters."""
        unicode_data = {
            'name': 'José María González',
            'email': 'josé@example.com',
            'interest': 'classes',
            'message': 'Hola! Me gustaría aprender salsa. ¿Tienen clases para principiantes?'
        }
        
        form = ContactForm(data=unicode_data)
        self.assertTrue(form.is_valid())
        
        contact = form.save()
        self.assertEqual(contact.name, 'José María González')
        self.assertIn('principiantes', contact.message)


class FormPerformanceTestCase(TestCase):
    """Test cases for form performance and efficiency."""
    
    def test_contact_form_validation_performance(self):
        """Test contact form validation performance."""
        test_data = {
            'name': 'Performance Test',
            'email': 'performance@example.com',
            'interest': 'classes',
            'message': 'This is a performance test message for form validation.'
        }
        
        # Test that form validation is fast
        import time
        start_time = time.time()
        
        for _ in range(100):
            form = ContactForm(data=test_data)
            form.is_valid()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 100 validations in under 1 second
        self.assertLess(duration, 1.0)
    
    def test_booking_form_validation_performance(self):
        """Test booking form validation performance."""
        test_data = {
            'customer_name': 'Performance Test',
            'customer_email': 'performance@example.com',
            'booking_type': 'class',
            'class_name': 'Performance Test Class',
            'booking_date': timezone.now() + timedelta(days=1),
            'price': '20.00'
        }
        
        # Test that form validation is fast
        import time
        start_time = time.time()
        
        for _ in range(100):
            form = BookingForm(data=test_data)
            form.is_valid()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 100 validations in under 1 second
        self.assertLess(duration, 1.0)
    
    def test_form_database_queries(self):
        """Test that form operations use minimal database queries."""
        contact_data = {
            'name': 'Query Test',
            'email': 'query@example.com',
            'interest': 'classes',
            'message': 'Testing database query efficiency.'
        }
        
        # Contact form should use minimal queries
        with self.assertNumQueries(1):  # Only the INSERT
            form = ContactForm(data=contact_data)
            form.is_valid()
            form.save()
        
        booking_data = {
            'customer_name': 'Query Test',
            'customer_email': 'query@example.com',
            'booking_type': 'class',
            'class_name': 'Query Test Class',
            'booking_date': timezone.now() + timedelta(days=1),
            'price': '20.00'
        }
        
        # Booking form should use minimal queries
        with self.assertNumQueries(1):  # Only the INSERT
            form = BookingForm(data=booking_data)
            form.is_valid()
            form.save()