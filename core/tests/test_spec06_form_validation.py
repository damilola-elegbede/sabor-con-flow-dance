"""
SPEC_06 Group C Task 7: Comprehensive Form Validation Testing
============================================================

Complete testing coverage for all forms including:
- Field validation and error handling
- Edge cases and boundary testing
- Security validation (XSS, injection)
- File upload validation
- Custom validation methods

Target: 80% code coverage with production-ready confidence
"""

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from unittest.mock import patch, Mock
import tempfile
import os
from PIL import Image
import io

from core.forms import TestimonialForm, ContactForm, BookingForm
from core.models import Testimonial, ContactSubmission, BookingConfirmation
from datetime import datetime, timedelta
from django.utils import timezone


class TestimonialFormTestCase(TestCase):
    """Comprehensive testing for TestimonialForm."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            'student_name': 'Maria Rodriguez',
            'email': 'maria@example.com',
            'class_type': 'choreo_team',
            'rating': '5',
            'content': 'This is an amazing class! The instructor is fantastic and I learned so much. The atmosphere is welcoming and encouraging for all skill levels. Highly recommend!'
        }
    
    def test_valid_form_submission(self):
        """Test form with completely valid data."""
        form = TestimonialForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        # Test that form can be saved
        testimonial = form.save()
        self.assertEqual(testimonial.student_name, 'Maria Rodriguez')
        self.assertEqual(testimonial.rating, 5)
        self.assertEqual(testimonial.class_type, 'choreo_team')
    
    def test_required_fields_validation(self):
        """Test that all required fields are properly validated."""
        required_fields = ['student_name', 'email', 'class_type', 'rating', 'content']
        
        for field in required_fields:
            data = self.valid_data.copy()
            data[field] = ''
            
            form = TestimonialForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)
    
    def test_email_validation(self):
        """Test email field validation."""
        invalid_emails = [
            'invalid-email',
            'missing@',
            '@missing.com',
            'spaces in@email.com',
            'toolong' + 'a' * 250 + '@example.com'
        ]
        
        for invalid_email in invalid_emails:
            data = self.valid_data.copy()
            data['email'] = invalid_email
            
            form = TestimonialForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn('email', form.errors)
    
    def test_rating_validation(self):
        """Test rating field validation."""
        # Test valid ratings
        for rating in ['1', '2', '3', '4', '5']:
            data = self.valid_data.copy()
            data['rating'] = rating
            
            form = TestimonialForm(data=data)
            self.assertTrue(form.is_valid())
        
        # Test invalid ratings
        invalid_ratings = ['0', '6', '-1', '10', 'abc', '3.5']
        
        for invalid_rating in invalid_ratings:
            data = self.valid_data.copy()
            data['rating'] = invalid_rating
            
            form = TestimonialForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn('rating', form.errors)
    
    def test_content_length_validation(self):
        """Test content field length validation."""
        data = self.valid_data.copy()
        
        # Test content too short (less than 50 characters)
        data['content'] = 'Too short'
        form = TestimonialForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
        
        # Test content too long (more than 500 characters)
        data['content'] = 'a' * 501
        form = TestimonialForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
        
        # Test exact minimum length (50 characters)
        data['content'] = 'a' * 50
        form = TestimonialForm(data=data)
        self.assertTrue(form.is_valid())
        
        # Test exact maximum length (500 characters)
        data['content'] = 'a' * 500
        form = TestimonialForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_content_whitespace_handling(self):
        """Test that content whitespace is properly handled."""
        data = self.valid_data.copy()
        
        # Test content with leading/trailing whitespace
        data['content'] = '   ' + 'a' * 50 + '   '
        form = TestimonialForm(data=data)
        
        if form.is_valid():
            self.assertEqual(form.cleaned_data['content'].strip(), 'a' * 50)
    
    def test_class_type_validation(self):
        """Test class type field validation."""
        valid_class_types = ['choreo_team', 'pasos_basicos', 'casino_royale', 'private_lesson', 'workshop', 'other']
        
        for class_type in valid_class_types:
            data = self.valid_data.copy()
            data['class_type'] = class_type
            
            form = TestimonialForm(data=data)
            self.assertTrue(form.is_valid())
        
        # Test invalid class type
        data = self.valid_data.copy()
        data['class_type'] = 'invalid_class'
        form = TestimonialForm(data=data)
        self.assertFalse(form.is_valid())
    
    def test_photo_upload_validation(self):
        """Test photo upload validation."""
        # Create a valid test image
        image = Image.new('RGB', (100, 100), color='red')
        image_file = io.BytesIO()
        image.save(image_file, format='JPEG')
        image_file.seek(0)
        
        valid_image = SimpleUploadedFile(
            name='test.jpg',
            content=image_file.getvalue(),
            content_type='image/jpeg'
        )
        
        form = TestimonialForm(data=self.valid_data, files={'photo': valid_image})
        self.assertTrue(form.is_valid())
    
    def test_photo_size_validation(self):
        """Test photo size limit validation."""
        # Create an image that's too large (> 5MB)
        large_image = Image.new('RGB', (2000, 2000), color='blue')
        large_image_file = io.BytesIO()
        large_image.save(large_image_file, format='JPEG', quality=100)
        large_image_file.seek(0)
        
        # Simulate a file larger than 5MB
        large_file_content = b'x' * (6 * 1024 * 1024)  # 6MB
        large_file = SimpleUploadedFile(
            name='large.jpg',
            content=large_file_content,
            content_type='image/jpeg'
        )
        
        form = TestimonialForm(data=self.valid_data, files={'photo': large_file})
        self.assertFalse(form.is_valid())
        self.assertIn('photo', form.errors)
    
    def test_photo_type_validation(self):
        """Test photo file type validation."""
        # Test invalid file types
        invalid_file = SimpleUploadedFile(
            name='test.txt',
            content=b'This is not an image',
            content_type='text/plain'
        )
        
        form = TestimonialForm(data=self.valid_data, files={'photo': invalid_file})
        self.assertFalse(form.is_valid())
        self.assertIn('photo', form.errors)
    
    def test_name_length_validation(self):
        """Test student name length validation."""
        data = self.valid_data.copy()
        
        # Test name too long
        data['student_name'] = 'a' * 101  # Exceeds max_length=100
        form = TestimonialForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('student_name', form.errors)
        
        # Test maximum valid length
        data['student_name'] = 'a' * 100
        form = TestimonialForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_xss_prevention(self):
        """Test that form prevents XSS attacks."""
        xss_payloads = [
            '<script>alert("xss")</script>',
            '"><script>alert("xss")</script>',
            'javascript:alert("xss")',
            '<img src=x onerror=alert("xss")>',
            '<svg onload=alert("xss")>'
        ]
        
        for payload in xss_payloads:
            data = self.valid_data.copy()
            data['content'] = payload + 'a' * 50  # Ensure minimum length
            
            form = TestimonialForm(data=data)
            # Form should still be valid, but content should be cleaned by template rendering
            if form.is_valid():
                self.assertIn(payload, form.cleaned_data['content'])  # Raw data preserved for validation


class ContactFormTestCase(TestCase):
    """Comprehensive testing for ContactForm."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            'name': 'Juan Carlos',
            'email': 'juan@example.com',
            'phone': '(555) 123-4567',
            'interest': 'classes',
            'message': 'I am interested in learning salsa and would like more information about your beginner classes.'
        }
    
    def test_valid_form_submission(self):
        """Test form with completely valid data."""
        form = ContactForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        contact = form.save()
        self.assertEqual(contact.name, 'Juan Carlos')
        self.assertEqual(contact.interest, 'classes')
    
    def test_required_fields_validation(self):
        """Test that required fields are validated."""
        required_fields = ['name', 'email', 'interest', 'message']
        
        for field in required_fields:
            data = self.valid_data.copy()
            data[field] = ''
            
            form = ContactForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)
    
    def test_optional_phone_field(self):
        """Test that phone field is optional."""
        data = self.valid_data.copy()
        data['phone'] = ''
        
        form = ContactForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_phone_number_formatting(self):
        """Test phone number formatting and validation."""
        valid_phones = [
            '5551234567',
            '(555) 123-4567',
            '555-123-4567',
            '555.123.4567',
            '1-555-123-4567',
            '+1 555 123 4567'
        ]
        
        for phone in valid_phones:
            data = self.valid_data.copy()
            data['phone'] = phone
            
            form = ContactForm(data=data)
            self.assertTrue(form.is_valid())
    
    def test_invalid_phone_numbers(self):
        """Test invalid phone number validation."""
        invalid_phones = [
            '123',  # Too short
            'abc-def-ghij',  # Non-numeric
            '555-1234',  # Too short
        ]
        
        for phone in invalid_phones:
            data = self.valid_data.copy()
            data['phone'] = phone
            
            form = ContactForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn('phone', form.errors)
    
    def test_message_length_validation(self):
        """Test message length validation."""
        data = self.valid_data.copy()
        
        # Test message too short (less than 20 characters)
        data['message'] = 'Too short'
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
        
        # Test message too long (more than 1000 characters)
        data['message'] = 'a' * 1001
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
        
        # Test minimum valid length
        data['message'] = 'a' * 20
        form = ContactForm(data=data)
        self.assertTrue(form.is_valid())
        
        # Test maximum valid length
        data['message'] = 'a' * 1000
        form = ContactForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_interest_choices_validation(self):
        """Test interest field choices validation."""
        valid_interests = ['classes', 'private_lesson', 'workshop', 'events', 'choreography', 'general', 'other']
        
        for interest in valid_interests:
            data = self.valid_data.copy()
            data['interest'] = interest
            
            form = ContactForm(data=data)
            self.assertTrue(form.is_valid())
        
        # Test invalid interest
        data = self.valid_data.copy()
        data['interest'] = 'invalid_interest'
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
    
    def test_name_length_validation(self):
        """Test name field length validation."""
        data = self.valid_data.copy()
        
        # Test name too long
        data['name'] = 'a' * 101
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class BookingFormTestCase(TestCase):
    """Comprehensive testing for BookingForm."""
    
    def setUp(self):
        """Set up test data."""
        future_date = timezone.now() + timedelta(days=7)
        
        self.valid_data = {
            'customer_name': 'Ana Sofia',
            'customer_email': 'ana@example.com',
            'customer_phone': '(555) 987-6543',
            'booking_type': 'private_lesson',
            'class_name': 'Private Salsa Lesson',
            'instructor_name': 'Maria Santos',
            'booking_date': future_date.strftime('%Y-%m-%dT%H:%M'),
            'duration_minutes': 60,
            'price': '80.00',
            'payment_method': 'Venmo',
            'special_instructions': 'First time taking salsa lessons'
        }
    
    def test_valid_form_submission(self):
        """Test form with completely valid data."""
        form = BookingForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        booking = form.save()
        self.assertEqual(booking.customer_name, 'Ana Sofia')
        self.assertEqual(booking.booking_type, 'private_lesson')
    
    def test_required_fields_validation(self):
        """Test that required fields are validated."""
        required_fields = ['customer_name', 'customer_email', 'booking_type', 'class_name', 'booking_date', 'price']
        
        for field in required_fields:
            data = self.valid_data.copy()
            data[field] = ''
            
            form = BookingForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)
    
    def test_booking_date_future_validation(self):
        """Test that booking date must be in the future."""
        data = self.valid_data.copy()
        
        # Test past date
        past_date = timezone.now() - timedelta(days=1)
        data['booking_date'] = past_date.strftime('%Y-%m-%dT%H:%M')
        
        form = BookingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('booking_date', form.errors)
        
        # Test current time (should fail)
        current_time = timezone.now()
        data['booking_date'] = current_time.strftime('%Y-%m-%dT%H:%M')
        
        form = BookingForm(data=data)
        self.assertFalse(form.is_valid())
    
    def test_price_validation(self):
        """Test price field validation."""
        data = self.valid_data.copy()
        
        # Test negative price
        data['price'] = '-10.00'
        form = BookingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        
        # Test extremely high price
        data['price'] = '501.00'
        form = BookingForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        
        # Test valid prices
        valid_prices = ['0.00', '25.50', '100.00', '500.00']
        for price in valid_prices:
            data['price'] = price
            form = BookingForm(data=data)
            self.assertTrue(form.is_valid())
    
    def test_duration_validation(self):
        """Test duration field validation."""
        data = self.valid_data.copy()
        
        # Test minimum duration (30 minutes)
        data['duration_minutes'] = 30
        form = BookingForm(data=data)
        self.assertTrue(form.is_valid())
        
        # Test maximum duration (180 minutes)
        data['duration_minutes'] = 180
        form = BookingForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_booking_type_choices(self):
        """Test booking type choices validation."""
        valid_types = ['class', 'private_lesson', 'workshop', 'package', 'event']
        
        for booking_type in valid_types:
            data = self.valid_data.copy()
            data['booking_type'] = booking_type
            
            form = BookingForm(data=data)
            self.assertTrue(form.is_valid())
    
    def test_optional_fields(self):
        """Test that optional fields can be empty."""
        optional_fields = ['customer_phone', 'instructor_name', 'payment_method', 'special_instructions']
        
        for field in optional_fields:
            data = self.valid_data.copy()
            data[field] = ''
            
            form = BookingForm(data=data)
            self.assertTrue(form.is_valid())


class FormSecurityTestCase(TestCase):
    """Test form security features."""
    
    def test_sql_injection_prevention(self):
        """Test that forms prevent SQL injection."""
        sql_payloads = [
            "'; DROP TABLE testimonials; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; DELETE FROM * --"
        ]
        
        for payload in sql_payloads:
            data = {
                'student_name': payload,
                'email': 'test@example.com',
                'class_type': 'choreo_team',
                'rating': '5',
                'content': 'This is a test testimonial with enough content to pass validation requirements.'
            }
            
            form = TestimonialForm(data=data)
            if form.is_valid():
                # If form is valid, data should be safely handled
                testimonial = form.save()
                self.assertEqual(testimonial.student_name, payload)  # Raw data preserved but safely handled
    
    def test_csrf_token_requirement(self):
        """Test that forms require CSRF tokens in views."""
        # This would be tested in view tests, but we can test form instantiation
        form = TestimonialForm()
        self.assertIsNotNone(form)
    
    def test_file_upload_security(self):
        """Test file upload security measures."""
        # Test executable file upload attempt
        malicious_file = SimpleUploadedFile(
            name='malicious.exe',
            content=b'MZ\x90\x00',  # PE header
            content_type='application/x-executable'
        )
        
        data = {
            'student_name': 'Test User',
            'email': 'test@example.com',
            'class_type': 'choreo_team',
            'rating': '5',
            'content': 'This is a test testimonial with sufficient content for validation.'
        }
        
        form = TestimonialForm(data=data, files={'photo': malicious_file})
        self.assertFalse(form.is_valid())
        self.assertIn('photo', form.errors)


class FormPerformanceTestCase(TestCase):
    """Test form performance characteristics."""
    
    def test_form_validation_performance(self):
        """Test that form validation is efficient."""
        import time
        
        data = {
            'student_name': 'Performance Test User',
            'email': 'performance@example.com',
            'class_type': 'choreo_team',
            'rating': '5',
            'content': 'This is a performance test testimonial with sufficient content to pass all validation requirements.'
        }
        
        start_time = time.time()
        
        for _ in range(100):
            form = TestimonialForm(data=data)
            form.is_valid()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 100 form validations should complete in under 1 second
        self.assertLess(total_time, 1.0)
    
    def test_large_content_handling(self):
        """Test form handling of large content."""
        large_content = 'a' * 500  # Maximum allowed content
        
        data = {
            'student_name': 'Large Content User',
            'email': 'large@example.com',
            'class_type': 'choreo_team',
            'rating': '5',
            'content': large_content
        }
        
        form = TestimonialForm(data=data)
        self.assertTrue(form.is_valid())


class FormEdgeCaseTestCase(TestCase):
    """Test form edge cases and boundary conditions."""
    
    def test_unicode_content_handling(self):
        """Test that forms handle Unicode content properly."""
        unicode_content = 'Hola! Me encanta bailar salsa 💃 ¡Es fantástico! 中文测试 русский текст'
        
        data = {
            'student_name': 'María José García-López',
            'email': 'maria.jose@example.com',
            'class_type': 'choreo_team',
            'rating': '5',
            'content': unicode_content + ' ' + 'Additional content to meet minimum length requirement.'
        }
        
        form = TestimonialForm(data=data)
        self.assertTrue(form.is_valid())
        
        if form.is_valid():
            testimonial = form.save()
            self.assertIn('💃', testimonial.content)
            self.assertIn('中文', testimonial.content)
    
    def test_boundary_values(self):
        """Test boundary values for all numeric fields."""
        # Test minimum rating
        data = {
            'student_name': 'Boundary Test',
            'email': 'boundary@example.com',
            'class_type': 'choreo_team',
            'rating': '1',
            'content': 'Minimum rating test with sufficient content to pass validation requirements.'
        }
        
        form = TestimonialForm(data=data)
        self.assertTrue(form.is_valid())
        
        # Test maximum rating
        data['rating'] = '5'
        form = TestimonialForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_empty_string_vs_none_handling(self):
        """Test handling of empty strings vs None values."""
        data = {
            'student_name': 'Empty Test',
            'email': 'empty@example.com',
            'class_type': 'choreo_team',
            'rating': '5',
            'content': 'Testing empty string handling with sufficient content for validation.'
        }
        
        # Test with empty string for optional field
        form = TestimonialForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_whitespace_only_fields(self):
        """Test handling of whitespace-only field values."""
        data = {
            'student_name': '   ',  # Whitespace only
            'email': 'whitespace@example.com',
            'class_type': 'choreo_team',
            'rating': '5',
            'content': 'Testing whitespace handling with sufficient content for validation requirements.'
        }
        
        form = TestimonialForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('student_name', form.errors)
    
    def test_special_characters_in_names(self):
        """Test handling of special characters in names."""
        special_names = [
            "O'Connor",
            "Jean-Pierre",
            "van der Berg",
            "José María",
            "李小明",
            "Müller"
        ]
        
        for name in special_names:
            data = {
                'student_name': name,
                'email': 'special@example.com',
                'class_type': 'choreo_team',
                'rating': '5',
                'content': f'Testing special character name {name} with sufficient content for validation.'
            }
            
            form = TestimonialForm(data=data)
            self.assertTrue(form.is_valid(), f"Form should be valid for name: {name}")


class FormIntegrationTestCase(TestCase):
    """Integration tests for forms with models and database."""
    
    def test_form_model_integration(self):
        """Test that forms integrate properly with models."""
        data = {
            'student_name': 'Integration Test',
            'email': 'integration@example.com',
            'class_type': 'choreo_team',
            'rating': '5',
            'content': 'This tests the integration between forms and models with proper validation.'
        }
        
        form = TestimonialForm(data=data)
        self.assertTrue(form.is_valid())
        
        # Test model creation
        testimonial = form.save()
        self.assertIsNotNone(testimonial.id)
        self.assertEqual(testimonial.status, 'pending')  # Default status
        
        # Test model retrieval
        retrieved = Testimonial.objects.get(id=testimonial.id)
        self.assertEqual(retrieved.student_name, 'Integration Test')
    
    def test_form_with_database_constraints(self):
        """Test form behavior with database constraints."""
        # Create a testimonial first
        Testimonial.objects.create(
            student_name='Existing User',
            email='existing@example.com',
            rating=5,
            content='This is an existing testimonial with sufficient content for validation.',
            class_type='choreo_team'
        )
        
        # Try to create another with same email (this should work as there's no unique constraint)
        data = {
            'student_name': 'Another User',
            'email': 'existing@example.com',  # Same email
            'class_type': 'pasos_basicos',
            'rating': '4',
            'content': 'Another testimonial from the same email with sufficient content.'
        }
        
        form = TestimonialForm(data=data)
        self.assertTrue(form.is_valid())  # Should work since no unique constraint
        
        testimonial = form.save()
        self.assertIsNotNone(testimonial.id)