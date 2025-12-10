from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models import Testimonial
from core.forms import TestimonialForm


class TestimonialFormTests(TestCase):
    """Test cases for the testimonial form."""
    
    def setUp(self):
        self.client = Client()
    
    def test_testimonial_form_valid_data(self):
        """Test form with valid data."""
        form_data = {
            'student_name': 'Maria Rodriguez',
            'email': 'maria@example.com',
            'class_type': 'choreo_team',
            'rating': '5',
            'content': 'This is a great class with amazing instructors. I learned so much and had a wonderful time dancing with everyone.',
        }
        form = TestimonialForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_testimonial_form_invalid_rating(self):
        """Test form with invalid rating."""
        form_data = {
            'student_name': 'Maria Rodriguez',
            'email': 'maria@example.com',
            'class_type': 'choreo_team',
            'rating': '6',  # Invalid rating
            'content': 'This is a great class with amazing instructors. I learned so much and had a wonderful time dancing with everyone.',
        }
        form = TestimonialForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_testimonial_form_short_content(self):
        """Test form with content too short."""
        form_data = {
            'student_name': 'Maria Rodriguez',
            'email': 'maria@example.com',
            'class_type': 'choreo_team',
            'rating': '5',
            'content': 'Too short',  # Less than 50 characters
        }
        form = TestimonialForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_testimonial_form_missing_required_fields(self):
        """Test form with missing required fields."""
        form_data = {
            'student_name': '',
            'email': '',
            'class_type': '',
            'rating': '',
            'content': '',
        }
        form = TestimonialForm(data=form_data)
        self.assertFalse(form.is_valid())


class TestimonialViewTests(TestCase):
    """Test cases for testimonial views."""
    
    def setUp(self):
        self.client = Client()
    
    def test_submit_testimonial_get(self):
        """Test GET request to submit testimonial page."""
        response = self.client.get(reverse('core:submit_testimonial'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Share Your Dance Journey')
        self.assertIn('form', response.context)
    
    def test_submit_testimonial_post_valid(self):
        """Test POST request with valid testimonial data."""
        form_data = {
            'student_name': 'Carlos Silva',
            'email': 'carlos@example.com',
            'class_type': 'casino_royale',
            'rating': '4',
            'content': 'Amazing class! The instructor was very patient and the atmosphere was fantastic. I learned a lot about Cuban salsa.',
        }
        response = self.client.post(reverse('core:submit_testimonial'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect to success page
        
        # Check that testimonial was created
        testimonial = Testimonial.objects.first()
        self.assertIsNotNone(testimonial)
        self.assertEqual(testimonial.student_name, 'Carlos Silva')
        self.assertEqual(testimonial.status, 'pending')
    
    def test_submit_testimonial_post_invalid(self):
        """Test POST request with invalid testimonial data."""
        form_data = {
            'student_name': '',
            'email': 'invalid-email',
            'class_type': '',
            'rating': '6',
            'content': 'Short',
        }
        response = self.client.post(reverse('core:submit_testimonial'), data=form_data)
        self.assertEqual(response.status_code, 200)  # Stay on form page
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())
    
    def test_testimonial_success_page(self):
        """Test testimonial success page."""
        response = self.client.get(reverse('core:testimonial_success'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank You!')


class TestimonialModelTests(TestCase):
    """Test cases for the Testimonial model."""
    
    def test_create_testimonial(self):
        """Test creating a testimonial."""
        testimonial = Testimonial.objects.create(
            student_name='Elena Martinez',
            email='elena@example.com',
            class_type='pasos_basicos',
            rating=5,
            content='Fantastic experience! The Pasos Básicos class was perfect for beginners like me.',
            status='pending'
        )
        
        self.assertEqual(testimonial.student_name, 'Elena Martinez')
        self.assertEqual(testimonial.rating, 5)
        self.assertEqual(testimonial.status, 'pending')
        self.assertEqual(str(testimonial), 'Elena Martinez - 5 stars')
    
    def test_testimonial_class_type_choices(self):
        """Test that class type choices are properly defined."""
        testimonial = Testimonial.objects.create(
            student_name='Diego Lopez',
            email='diego@example.com',
            class_type='choreo_team',
            rating=4,
            content='Great choreography team with challenging routines and supportive members.',
        )
        
        self.assertEqual(testimonial.get_class_type_display(), 'SCF Choreo Team')