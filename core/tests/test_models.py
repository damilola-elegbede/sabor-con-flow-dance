"""
Comprehensive model tests for Sabor Con Flow Dance core application.

Tests all model fields, validators, string representations, and edge cases
for Instructor, Class, Testimonial, and Resource models.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.validators import ValidationError as ValidatorError
from django.db import IntegrityError
from django.db.models import Model
from django.utils import timezone
from datetime import time, datetime
from core.models import Instructor, Class, Testimonial, Resource


class InstructorModelTestCase(TestCase):
    """Test cases for the Instructor model."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_instructor_data = {
            'name': 'Carlos Rodriguez',
            'bio': 'Professional salsa instructor with 10+ years of experience.',
            'photo_url': 'https://example.com/photos/carlos.jpg',
            'video_url': 'https://example.com/videos/carlos-demo.mp4',
            'instagram': '@carlos_salsa',
            'specialties': '["Salsa", "Bachata", "Merengue"]'
        }
    
    def test_instructor_creation(self):
        """Test creating an instructor with valid data."""
        instructor = Instructor.objects.create(**self.valid_instructor_data)
        self.assertEqual(instructor.name, 'Carlos Rodriguez')
        self.assertEqual(instructor.bio, 'Professional salsa instructor with 10+ years of experience.')
        self.assertEqual(instructor.photo_url, 'https://example.com/photos/carlos.jpg')
        self.assertEqual(instructor.video_url, 'https://example.com/videos/carlos-demo.mp4')
        self.assertEqual(instructor.instagram, '@carlos_salsa')
        self.assertEqual(instructor.specialties, '["Salsa", "Bachata", "Merengue"]')
    
    def test_instructor_str_representation(self):
        """Test the string representation of an instructor."""
        instructor = Instructor.objects.create(**self.valid_instructor_data)
        self.assertEqual(str(instructor), 'Carlos Rodriguez')
    
    def test_instructor_ordering(self):
        """Test that instructors are ordered by name."""
        instructor1 = Instructor.objects.create(
            name='Zara Martinez',
            bio='Expert bachata instructor',
            photo_url='https://example.com/zara.jpg',
            specialties='["Bachata"]'
        )
        instructor2 = Instructor.objects.create(
            name='Alex Thompson',
            bio='Salsa specialist',
            photo_url='https://example.com/alex.jpg',
            specialties='["Salsa"]'
        )
        
        instructors = list(Instructor.objects.all())
        self.assertEqual(instructors[0].name, 'Alex Thompson')
        self.assertEqual(instructors[1].name, 'Zara Martinez')
    
    def test_instructor_required_fields(self):
        """Test that required fields cannot be empty."""
        # Test missing name - will raise ValidationError on full_clean()
        instructor = Instructor(
            bio='Test bio',
            photo_url='https://example.com/test.jpg',
            specialties='["Test"]'
        )
        with self.assertRaises(ValidationError):
            instructor.full_clean()
    
    def test_instructor_max_length_validation(self):
        """Test field max length validations."""
        long_name = 'x' * 101  # Exceeds max_length=100
        long_instagram = 'x' * 51  # Exceeds max_length=50
        
        # Test name max length
        instructor = Instructor(
            name=long_name,
            bio='Test bio',
            photo_url='https://example.com/test.jpg',
            specialties='["Test"]'
        )
        with self.assertRaises(ValidationError):
            instructor.full_clean()
        
        # Test instagram max length
        instructor = Instructor(
            name='Test Name',
            bio='Test bio',
            photo_url='https://example.com/test.jpg',
            instagram=long_instagram,
            specialties='["Test"]'
        )
        with self.assertRaises(ValidationError):
            instructor.full_clean()
    
    def test_instructor_optional_fields(self):
        """Test that optional fields can be blank."""
        instructor = Instructor.objects.create(
            name='Test Instructor',
            bio='Test bio',
            photo_url='https://example.com/test.jpg',
            specialties='["Test"]'
        )
        self.assertEqual(instructor.video_url, '')
        self.assertEqual(instructor.instagram, '')
    
    def test_instructor_url_field_validation(self):
        """Test URL field validation."""
        instructor = Instructor(
            name='Test Instructor',
            bio='Test bio',
            photo_url='invalid-url',
            specialties='["Test"]'
        )
        with self.assertRaises(ValidationError):
            instructor.full_clean()


class ClassModelTestCase(TestCase):
    """Test cases for the Class model."""
    
    def setUp(self):
        """Set up test data."""
        self.instructor = Instructor.objects.create(
            name='Maria Santos',
            bio='Expert salsa instructor',
            photo_url='https://example.com/maria.jpg',
            specialties='["Salsa", "Bachata"]'
        )
        
        self.valid_class_data = {
            'name': 'Beginner Salsa',
            'level': 'beginner',
            'instructor': self.instructor,
            'day_of_week': 'Monday',
            'start_time': time(19, 0),  # 7:00 PM
            'end_time': time(20, 0),    # 8:00 PM
            'description': 'Perfect class for those new to salsa dancing.',
            'capacity': 25
        }
    
    def test_class_creation(self):
        """Test creating a class with valid data."""
        dance_class = Class.objects.create(**self.valid_class_data)
        self.assertEqual(dance_class.name, 'Beginner Salsa')
        self.assertEqual(dance_class.level, 'beginner')
        self.assertEqual(dance_class.instructor, self.instructor)
        self.assertEqual(dance_class.day_of_week, 'Monday')
        self.assertEqual(dance_class.start_time, time(19, 0))
        self.assertEqual(dance_class.end_time, time(20, 0))
        self.assertEqual(dance_class.description, 'Perfect class for those new to salsa dancing.')
        self.assertEqual(dance_class.capacity, 25)
    
    def test_class_str_representation(self):
        """Test the string representation of a class."""
        dance_class = Class.objects.create(**self.valid_class_data)
        self.assertEqual(str(dance_class), 'Beginner Salsa - Beginner')
    
    def test_class_level_choices(self):
        """Test that level field accepts only valid choices."""
        valid_levels = ['beginner', 'intermediate', 'advanced']
        
        for level in valid_levels:
            dance_class = Class.objects.create(
                name=f'Test {level.title()} Class',
                level=level,
                instructor=self.instructor,
                start_time=time(19, 0),
                end_time=time(20, 0),
                description='Test description'
            )
            self.assertEqual(dance_class.level, level)
    
    def test_class_invalid_level_choice(self):
        """Test that invalid level choices raise validation error."""
        invalid_class = Class(
            name='Invalid Level Class',
            level='expert',  # Invalid choice
            instructor=self.instructor,
            start_time=time(19, 0),
            end_time=time(20, 0),
            description='Test description'
        )
        with self.assertRaises(ValidationError):
            invalid_class.full_clean()
    
    def test_class_ordering(self):
        """Test that classes are ordered by day_of_week and start_time."""
        class1 = Class.objects.create(
            name='Sunday Early',
            level='beginner',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(10, 0),
            end_time=time(11, 0),
            description='Early Sunday class'
        )
        class2 = Class.objects.create(
            name='Sunday Late',
            level='intermediate',
            instructor=self.instructor,
            day_of_week='Sunday',
            start_time=time(15, 0),
            end_time=time(16, 0),
            description='Late Sunday class'
        )
        class3 = Class.objects.create(
            name='Monday Class',
            level='advanced',
            instructor=self.instructor,
            day_of_week='Monday',
            start_time=time(10, 0),
            end_time=time(11, 0),
            description='Monday class'
        )
        
        classes = list(Class.objects.all())
        # Should be ordered by day_of_week, then start_time
        self.assertEqual(classes[0].name, 'Monday Class')
        self.assertEqual(classes[1].name, 'Sunday Early')
        self.assertEqual(classes[2].name, 'Sunday Late')
    
    def test_class_default_values(self):
        """Test default values for class fields."""
        dance_class = Class.objects.create(
            name='Test Class',
            level='beginner',
            instructor=self.instructor,
            start_time=time(19, 0),
            end_time=time(20, 0),
            description='Test description'
        )
        self.assertEqual(dance_class.day_of_week, 'Sunday')
        self.assertEqual(dance_class.capacity, 20)
    
    def test_class_foreign_key_relationship(self):
        """Test the foreign key relationship with Instructor."""
        dance_class = Class.objects.create(**self.valid_class_data)
        self.assertEqual(dance_class.instructor.name, 'Maria Santos')
        
        # Test cascade delete
        instructor_id = self.instructor.id
        self.instructor.delete()
        with self.assertRaises(Class.DoesNotExist):
            Class.objects.get(instructor_id=instructor_id)
    
    def test_class_verbose_name_plural(self):
        """Test the verbose name plural is set correctly."""
        self.assertEqual(Class._meta.verbose_name_plural, 'Classes')


class TestimonialModelTestCase(TestCase):
    """Test cases for the Testimonial model."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_testimonial_data = {
            'student_name': 'Jennifer Lopez',
            'email': 'jennifer@example.com',
            'rating': 5,
            'content': 'Amazing classes! I learned so much and had a great time.',
            'class_type': 'Salsa Beginner',
            'photo': None,
            'video_url': 'https://example.com/jennifer-testimonial.mp4',
            'google_review_id': 'google_123456',
            'status': 'approved',
            'featured': True
        }
    
    def test_testimonial_creation(self):
        """Test creating a testimonial with valid data."""
        testimonial = Testimonial.objects.create(**self.valid_testimonial_data)
        self.assertEqual(testimonial.student_name, 'Jennifer Lopez')
        self.assertEqual(testimonial.email, 'jennifer@example.com')
        self.assertEqual(testimonial.rating, 5)
        self.assertEqual(testimonial.content, 'Amazing classes! I learned so much and had a great time.')
        self.assertEqual(testimonial.class_type, 'Salsa Beginner')
        self.assertEqual(testimonial.video_url, 'https://example.com/jennifer-testimonial.mp4')
        self.assertEqual(testimonial.google_review_id, 'google_123456')
        self.assertEqual(testimonial.status, 'approved')
        self.assertTrue(testimonial.featured)
    
    def test_testimonial_str_representation(self):
        """Test the string representation of a testimonial."""
        testimonial = Testimonial.objects.create(**self.valid_testimonial_data)
        self.assertEqual(str(testimonial), 'Jennifer Lopez - 5 stars')
    
    def test_testimonial_rating_validation(self):
        """Test rating field validation (1-5 range)."""
        # Test valid ratings
        for rating in [1, 2, 3, 4, 5]:
            testimonial = Testimonial.objects.create(
                student_name=f'Student {rating}',
                email=f'student{rating}@example.com',
                rating=rating,
                content='Good class',
                class_type='Test Class'
            )
            self.assertEqual(testimonial.rating, rating)
        
        # Test invalid ratings
        invalid_ratings = [0, 6, -1, 10]
        for rating in invalid_ratings:
            testimonial = Testimonial(
                student_name='Test Student',
                email='test@example.com',
                rating=rating,
                content='Test content',
                class_type='Test Class'
            )
            with self.assertRaises(ValidationError):
                testimonial.full_clean()
    
    def test_testimonial_status_choices(self):
        """Test status field choices."""
        valid_statuses = ['pending', 'approved', 'rejected']
        
        for status in valid_statuses:
            testimonial = Testimonial.objects.create(
                student_name=f'Student {status}',
                email=f'{status}@example.com',
                rating=5,
                content='Test content',
                class_type='Test Class',
                status=status
            )
            self.assertEqual(testimonial.status, status)
    
    def test_testimonial_default_values(self):
        """Test default values for testimonial fields."""
        testimonial = Testimonial.objects.create(
            student_name='Test Student',
            email='test@example.com',
            rating=4,
            content='Test content',
            class_type='Test Class'
        )
        self.assertEqual(testimonial.status, 'pending')
        self.assertFalse(testimonial.featured)
        self.assertIsNotNone(testimonial.created_at)
    
    def test_testimonial_ordering(self):
        """Test that testimonials are ordered by created_at descending."""
        # Create testimonials with slight delay to ensure different timestamps
        import time
        testimonial1 = Testimonial.objects.create(
            student_name='First Student',
            email='first@example.com',
            rating=5,
            content='First testimonial',
            class_type='Test Class'
        )
        time.sleep(0.01)  # Small delay
        testimonial2 = Testimonial.objects.create(
            student_name='Second Student',
            email='second@example.com',
            rating=4,
            content='Second testimonial',
            class_type='Test Class'
        )
        
        testimonials = list(Testimonial.objects.all())
        self.assertEqual(testimonials[0].student_name, 'Second Student')
        self.assertEqual(testimonials[1].student_name, 'First Student')
    
    def test_testimonial_email_validation(self):
        """Test email field validation."""
        testimonial = Testimonial(
            student_name='Test Student',
            email='invalid-email',
            rating=5,
            content='Test content',
            class_type='Test Class'
        )
        with self.assertRaises(ValidationError):
            testimonial.full_clean()
    
    def test_testimonial_optional_fields(self):
        """Test that optional fields can be blank/null."""
        testimonial = Testimonial.objects.create(
            student_name='Test Student',
            email='test@example.com',
            rating=4,
            content='Test content',
            class_type='Test Class'
        )
        # For ImageField, check if it has no file
        self.assertFalse(testimonial.photo)
        # video_url can be None due to null=True
        self.assertIsNone(testimonial.video_url)
        self.assertEqual(testimonial.google_review_id, '')
        self.assertIsNone(testimonial.published_at)
    
    def test_testimonial_auto_timestamps(self):
        """Test automatic timestamp creation."""
        before_creation = timezone.now()
        testimonial = Testimonial.objects.create(
            student_name='Test Student',
            email='test@example.com',
            rating=5,
            content='Test content',
            class_type='Test Class'
        )
        after_creation = timezone.now()
        
        self.assertGreaterEqual(testimonial.created_at, before_creation)
        self.assertLessEqual(testimonial.created_at, after_creation)


class ResourceModelTestCase(TestCase):
    """Test cases for the Resource model."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_resource_data = {
            'title': 'Salsa Basic Steps Tutorial',
            'type': 'video',
            'embed_url': 'https://www.youtube.com/embed/abc123',
            'instagram_post_id': 'C12345abcde',
            'description': 'Learn the fundamental steps of salsa dancing.',
            'order': 1
        }
    
    def test_resource_creation(self):
        """Test creating a resource with valid data."""
        resource = Resource.objects.create(**self.valid_resource_data)
        self.assertEqual(resource.title, 'Salsa Basic Steps Tutorial')
        self.assertEqual(resource.type, 'video')
        self.assertEqual(resource.embed_url, 'https://www.youtube.com/embed/abc123')
        self.assertEqual(resource.instagram_post_id, 'C12345abcde')
        self.assertEqual(resource.description, 'Learn the fundamental steps of salsa dancing.')
        self.assertEqual(resource.order, 1)
    
    def test_resource_str_representation(self):
        """Test the string representation of a resource."""
        resource = Resource.objects.create(**self.valid_resource_data)
        self.assertEqual(str(resource), 'Salsa Basic Steps Tutorial (Video)')
    
    def test_resource_type_choices(self):
        """Test type field choices."""
        valid_types = ['playlist', 'video', 'guide']
        
        for resource_type in valid_types:
            resource = Resource.objects.create(
                title=f'Test {resource_type.title()}',
                type=resource_type,
                embed_url='https://example.com/embed',
                description=f'Test {resource_type} description'
            )
            self.assertEqual(resource.type, resource_type)
    
    def test_resource_invalid_type_choice(self):
        """Test that invalid type choices raise validation error."""
        resource = Resource(
            title='Invalid Type Resource',
            type='book',  # Invalid choice
            embed_url='https://example.com/embed',
            description='Test description'
        )
        with self.assertRaises(ValidationError):
            resource.full_clean()
    
    def test_resource_ordering(self):
        """Test that resources are ordered by order field, then created_at."""
        import time
        resource1 = Resource.objects.create(
            title='Third Resource',
            type='video',
            embed_url='https://example.com/3',
            description='Third resource',
            order=3
        )
        time.sleep(0.01)
        resource2 = Resource.objects.create(
            title='First Resource',
            type='guide',
            embed_url='https://example.com/1',
            description='First resource',
            order=1
        )
        time.sleep(0.01)
        resource3 = Resource.objects.create(
            title='Second Resource A',
            type='playlist',
            embed_url='https://example.com/2a',
            description='Second resource A',
            order=2
        )
        time.sleep(0.01)
        resource4 = Resource.objects.create(
            title='Second Resource B',
            type='video',
            embed_url='https://example.com/2b',
            description='Second resource B',
            order=2
        )
        
        resources = list(Resource.objects.all())
        self.assertEqual(resources[0].title, 'First Resource')
        self.assertEqual(resources[1].title, 'Second Resource A')
        self.assertEqual(resources[2].title, 'Second Resource B')
        self.assertEqual(resources[3].title, 'Third Resource')
    
    def test_resource_default_values(self):
        """Test default values for resource fields."""
        resource = Resource.objects.create(
            title='Test Resource',
            type='video',
            embed_url='https://example.com/test',
            description='Test description'
        )
        self.assertEqual(resource.order, 0)
        self.assertIsNotNone(resource.created_at)
    
    def test_resource_optional_fields(self):
        """Test that optional fields can be blank."""
        resource = Resource.objects.create(
            title='Test Resource',
            type='video',
            embed_url='https://example.com/test',
            description='Test description'
        )
        self.assertEqual(resource.instagram_post_id, '')
    
    def test_resource_max_length_validation(self):
        """Test field max length validations."""
        long_title = 'x' * 201  # Exceeds max_length=200
        long_type = 'x' * 21   # Exceeds max_length=20
        long_instagram_id = 'x' * 101  # Exceeds max_length=100
        
        # Test title max length
        resource = Resource(
            title=long_title,
            type='video',
            embed_url='https://example.com/test',
            description='Test description'
        )
        with self.assertRaises(ValidationError):
            resource.full_clean()
        
        # Test type max length  
        resource = Resource(
            title='Test Resource',
            type=long_type,
            embed_url='https://example.com/test',
            description='Test description'
        )
        with self.assertRaises(ValidationError):
            resource.full_clean()
        
        # Test instagram_post_id max length
        resource = Resource(
            title='Test Resource',
            type='video',
            embed_url='https://example.com/test',
            instagram_post_id=long_instagram_id,
            description='Test description'
        )
        with self.assertRaises(ValidationError):
            resource.full_clean()
    
    def test_resource_url_field_validation(self):
        """Test URL field validation."""
        resource = Resource(
            title='Test Resource',
            type='video',
            embed_url='invalid-url',
            description='Test description'
        )
        with self.assertRaises(ValidationError):
            resource.full_clean()
    
    def test_resource_auto_timestamps(self):
        """Test automatic timestamp creation."""
        before_creation = timezone.now()
        resource = Resource.objects.create(
            title='Test Resource',
            type='video',
            embed_url='https://example.com/test',
            description='Test description'
        )
        after_creation = timezone.now()
        
        self.assertGreaterEqual(resource.created_at, before_creation)
        self.assertLessEqual(resource.created_at, after_creation)


class ModelIntegrationTestCase(TestCase):
    """Integration tests for model relationships and edge cases."""
    
    def test_model_count_queries(self):
        """Test database query efficiency for model relationships."""
        instructor = Instructor.objects.create(
            name='Test Instructor',
            bio='Test bio',
            photo_url='https://example.com/test.jpg',
            specialties='["Test"]'
        )
        
        # Create multiple classes for the instructor
        for i in range(3):
            Class.objects.create(
                name=f'Class {i}',
                level='beginner',
                instructor=instructor,
                start_time=time(19, i),
                end_time=time(20, i),
                description=f'Description {i}'
            )
        
        # Test that we can efficiently get instructor with classes
        with self.assertNumQueries(2):  # One for instructor, one for classes
            instructor = Instructor.objects.get(id=instructor.id)
            classes = list(instructor.class_set.all())
            self.assertEqual(len(classes), 3)
    
    def test_model_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test minimum valid rating
        testimonial = Testimonial.objects.create(
            student_name='Min Rating',
            email='min@example.com',
            rating=1,
            content='Minimum rating',
            class_type='Test'
        )
        self.assertEqual(testimonial.rating, 1)
        
        # Test maximum valid rating
        testimonial = Testimonial.objects.create(
            student_name='Max Rating',
            email='max@example.com',
            rating=5,
            content='Maximum rating',
            class_type='Test'
        )
        self.assertEqual(testimonial.rating, 5)
        
        # Test empty but allowed fields
        instructor = Instructor.objects.create(
            name='Empty Fields',
            bio='',  # Empty but allowed
            photo_url='https://example.com/empty.jpg',
            specialties=''  # Empty but allowed
        )
        self.assertEqual(instructor.bio, '')
        self.assertEqual(instructor.specialties, '')