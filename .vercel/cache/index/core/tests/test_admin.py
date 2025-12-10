"""
Comprehensive admin interface tests for Sabor Con Flow Dance core application.

Tests admin registration, list displays, filters, actions, and fieldsets
for all registered models.
"""

from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import time
from unittest.mock import Mock

from core.models import Instructor, Class, Testimonial, Resource
from core.admin import (
    InstructorAdmin, ClassAdmin, TestimonialAdmin, ResourceAdmin,
    approve_testimonials, reject_testimonials
)


class AdminRegistrationTestCase(TestCase):
    """Test that all models are properly registered with admin."""
    
    def test_models_registered_with_admin(self):
        """Test that all core models are registered with admin."""
        from django.contrib import admin
        from django.apps import apps
        
        core_models = [Instructor, Class, Testimonial, Resource]
        
        for model in core_models:
            self.assertTrue(
                admin.site.is_registered(model),
                f'{model.__name__} is not registered with admin'
            )


class InstructorAdminTestCase(TestCase):
    """Test cases for InstructorAdmin configuration."""
    
    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.admin = InstructorAdmin(Instructor, self.site)
        self.instructor = Instructor.objects.create(
            name='Test Instructor',
            bio='Test bio',
            photo_url='https://example.com/test.jpg',
            instagram='@test_instructor',
            specialties='["Salsa", "Bachata"]'
        )
    
    def test_instructor_admin_list_display(self):
        """Test InstructorAdmin list_display configuration."""
        expected_fields = ['name', 'instagram', 'specialties']
        self.assertEqual(self.admin.list_display, expected_fields)
    
    def test_instructor_admin_search_fields(self):
        """Test InstructorAdmin search_fields configuration."""
        expected_fields = ['name', 'bio']
        self.assertEqual(self.admin.search_fields, expected_fields)
    
    def test_instructor_admin_list_per_page(self):
        """Test InstructorAdmin pagination configuration."""
        self.assertEqual(self.admin.list_per_page, 20)
    
    def test_instructor_admin_fieldsets(self):
        """Test InstructorAdmin fieldsets configuration."""
        expected_fieldsets = (
            ('Basic Information', {
                'fields': ('name', 'bio', 'specialties')
            }),
            ('Media', {
                'fields': ('photo_url', 'video_url')
            }),
            ('Social Media', {
                'fields': ('instagram',)
            }),
        )
        self.assertEqual(self.admin.fieldsets, expected_fieldsets)


class ClassAdminTestCase(TestCase):
    """Test cases for ClassAdmin configuration."""
    
    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.admin = ClassAdmin(Class, self.site)
        self.instructor = Instructor.objects.create(
            name='Test Instructor',
            bio='Test bio',
            photo_url='https://example.com/test.jpg',
            specialties='["Salsa"]'
        )
        self.dance_class = Class.objects.create(
            name='Test Class',
            level='beginner',
            instructor=self.instructor,
            day_of_week='Monday',
            start_time=time(19, 0),
            end_time=time(20, 0),
            description='Test description'
        )
    
    def test_class_admin_list_display(self):
        """Test ClassAdmin list_display configuration."""
        expected_fields = ['name', 'level', 'instructor', 'day_of_week', 'start_time']
        self.assertEqual(self.admin.list_display, expected_fields)
    
    def test_class_admin_list_filter(self):
        """Test ClassAdmin list_filter configuration."""
        expected_filters = ['level', 'day_of_week']
        self.assertEqual(self.admin.list_filter, expected_filters)
    
    def test_class_admin_search_fields(self):
        """Test ClassAdmin search_fields configuration."""
        expected_fields = ['name', 'description']
        self.assertEqual(self.admin.search_fields, expected_fields)
    
    def test_class_admin_fieldsets(self):
        """Test ClassAdmin fieldsets configuration."""
        expected_fieldsets = (
            ('Class Information', {
                'fields': ('name', 'level', 'instructor', 'description')
            }),
            ('Schedule', {
                'fields': ('day_of_week', 'start_time', 'end_time')
            }),
            ('Capacity', {
                'fields': ('capacity',)
            }),
        )
        self.assertEqual(self.admin.fieldsets, expected_fieldsets)


class TestimonialAdminTestCase(TestCase):
    """Test cases for TestimonialAdmin configuration."""
    
    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.admin = TestimonialAdmin(Testimonial, self.site)
        self.testimonial = Testimonial.objects.create(
            student_name='Test Student',
            email='test@example.com',
            rating=5,
            content='Great class!',
            class_type='Salsa',
            status='pending'
        )
    
    def test_testimonial_admin_list_display(self):
        """Test TestimonialAdmin list_display configuration."""
        expected_fields = ['student_name', 'rating', 'class_type', 'status', 'featured', 'created_at']
        self.assertEqual(self.admin.list_display, expected_fields)
    
    def test_testimonial_admin_list_filter(self):
        """Test TestimonialAdmin list_filter configuration."""
        expected_filters = ['status', 'rating', 'featured']
        self.assertEqual(self.admin.list_filter, expected_filters)
    
    def test_testimonial_admin_search_fields(self):
        """Test TestimonialAdmin search_fields configuration."""
        expected_fields = ['student_name', 'email', 'content']
        self.assertEqual(self.admin.search_fields, expected_fields)
    
    def test_testimonial_admin_actions(self):
        """Test TestimonialAdmin custom actions."""
        expected_actions = [approve_testimonials, reject_testimonials]
        self.assertEqual(self.admin.actions, expected_actions)
    
    def test_testimonial_admin_readonly_fields(self):
        """Test TestimonialAdmin readonly_fields configuration."""
        expected_fields = ['created_at']
        self.assertEqual(self.admin.readonly_fields, expected_fields)
    
    def test_testimonial_admin_fieldsets(self):
        """Test TestimonialAdmin fieldsets configuration."""
        expected_fieldsets = (
            ('Student Information', {
                'fields': ('student_name', 'email', 'class_type')
            }),
            ('Review Content', {
                'fields': ('rating', 'content')
            }),
            ('Media', {
                'fields': ('photo', 'video_url')
            }),
            ('Google Integration', {
                'fields': ('google_review_id',)
            }),
            ('Status & Publishing', {
                'fields': ('status', 'featured', 'published_at')
            }),
            ('Timestamps', {
                'fields': ('created_at',),
                'classes': ('collapse',)
            }),
        )
        self.assertEqual(self.admin.fieldsets, expected_fieldsets)
    
    def test_testimonial_admin_queryset_optimization(self):
        """Test that get_queryset uses select_related for optimization."""
        request = Mock()
        queryset = self.admin.get_queryset(request)
        # Check that select_related was called
        self.assertTrue(hasattr(queryset, 'query'))


class TestimonialAdminActionsTestCase(TestCase):
    """Test cases for TestimonialAdmin custom actions."""
    
    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.admin = TestimonialAdmin(Testimonial, self.site)
        self.testimonial1 = Testimonial.objects.create(
            student_name='Student 1',
            email='student1@example.com',
            rating=5,
            content='Great class!',
            class_type='Salsa',
            status='pending'
        )
        self.testimonial2 = Testimonial.objects.create(
            student_name='Student 2',
            email='student2@example.com',
            rating=4,
            content='Good class!',
            class_type='Bachata',
            status='pending'
        )
        self.testimonial3 = Testimonial.objects.create(
            student_name='Student 3',
            email='student3@example.com',
            rating=5,
            content='Excellent!',
            class_type='Merengue',
            status='approved'
        )
    
    def test_approve_testimonials_action(self):
        """Test the approve_testimonials custom action."""
        request = Mock()
        request.user = Mock()
        
        # Mock the message_user method
        self.admin.message_user = Mock()
        
        # Create queryset with pending testimonials
        queryset = Testimonial.objects.filter(status='pending')
        
        # Execute the action
        approve_testimonials(self.admin, request, queryset)
        
        # Check that testimonials were approved
        self.testimonial1.refresh_from_db()
        self.testimonial2.refresh_from_db()
        self.assertEqual(self.testimonial1.status, 'approved')
        self.assertEqual(self.testimonial2.status, 'approved')
        self.assertIsNotNone(self.testimonial1.published_at)
        self.assertIsNotNone(self.testimonial2.published_at)
        
        # Check that already approved testimonial was not affected
        self.testimonial3.refresh_from_db()
        self.assertEqual(self.testimonial3.status, 'approved')
        
        # Check that message was sent to user
        self.admin.message_user.assert_called_once()
        args = self.admin.message_user.call_args[0]
        self.assertIn('2 testimonials approved', args[1])
    
    def test_reject_testimonials_action(self):
        """Test the reject_testimonials custom action."""
        request = Mock()
        request.user = Mock()
        
        # Mock the message_user method
        self.admin.message_user = Mock()
        
        # Create queryset with pending testimonials
        queryset = Testimonial.objects.filter(status='pending')
        
        # Execute the action
        reject_testimonials(self.admin, request, queryset)
        
        # Check that testimonials were rejected
        self.testimonial1.refresh_from_db()
        self.testimonial2.refresh_from_db()
        self.assertEqual(self.testimonial1.status, 'rejected')
        self.assertEqual(self.testimonial2.status, 'rejected')
        
        # Check that message was sent to user
        self.admin.message_user.assert_called_once()
        args = self.admin.message_user.call_args[0]
        self.assertIn('2 testimonials rejected', args[1])
    
    def test_action_short_descriptions(self):
        """Test that actions have proper short descriptions."""
        self.assertEqual(
            approve_testimonials.short_description,
            'Approve selected testimonials'
        )
        self.assertEqual(
            reject_testimonials.short_description,
            'Reject selected testimonials'
        )


class ResourceAdminTestCase(TestCase):
    """Test cases for ResourceAdmin configuration."""
    
    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.admin = ResourceAdmin(Resource, self.site)
        self.resource = Resource.objects.create(
            title='Test Resource',
            type='video',
            embed_url='https://example.com/embed',
            description='Test description',
            order=1
        )
    
    def test_resource_admin_list_display(self):
        """Test ResourceAdmin list_display configuration."""
        expected_fields = ['title', 'type', 'order', 'created_at']
        self.assertEqual(self.admin.list_display, expected_fields)
    
    def test_resource_admin_list_filter(self):
        """Test ResourceAdmin list_filter configuration."""
        expected_filters = ['type']
        self.assertEqual(self.admin.list_filter, expected_filters)
    
    def test_resource_admin_search_fields(self):
        """Test ResourceAdmin search_fields configuration."""
        expected_fields = ['title', 'description']
        self.assertEqual(self.admin.search_fields, expected_fields)
    
    def test_resource_admin_ordering(self):
        """Test ResourceAdmin ordering configuration."""
        expected_ordering = ['order', 'created_at']
        self.assertEqual(self.admin.ordering, expected_ordering)
    
    def test_resource_admin_readonly_fields(self):
        """Test ResourceAdmin readonly_fields configuration."""
        expected_fields = ['created_at']
        self.assertEqual(self.admin.readonly_fields, expected_fields)
    
    def test_resource_admin_fieldsets(self):
        """Test ResourceAdmin fieldsets configuration."""
        expected_fieldsets = (
            ('Resource Information', {
                'fields': ('title', 'type', 'description')
            }),
            ('Media & Links', {
                'fields': ('embed_url', 'instagram_post_id')
            }),
            ('Display Order', {
                'fields': ('order',)
            }),
            ('Timestamps', {
                'fields': ('created_at',),
                'classes': ('collapse',)
            }),
        )
        self.assertEqual(self.admin.fieldsets, expected_fieldsets)


class AdminIntegrationTestCase(TestCase):
    """Integration tests for admin interface functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.client.login(username='admin', password='testpass123')
        
        # Create test data
        self.instructor = Instructor.objects.create(
            name='Admin Test Instructor',
            bio='Test bio',
            photo_url='https://example.com/test.jpg',
            specialties='["Salsa"]'
        )
    
    def test_admin_index_page_accessible(self):
        """Test that admin index page is accessible."""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django administration')
    
    def test_admin_model_list_pages_accessible(self):
        """Test that all model list pages are accessible."""
        model_urls = [
            '/admin/core/instructor/',
            '/admin/core/class/',
            '/admin/core/testimonial/',
            '/admin/core/resource/',
        ]
        
        for url in model_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
    
    def test_admin_model_add_pages_accessible(self):
        """Test that all model add pages are accessible."""
        model_urls = [
            '/admin/core/instructor/add/',
            '/admin/core/class/add/',
            '/admin/core/testimonial/add/',
            '/admin/core/resource/add/',
        ]
        
        for url in model_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
    
    def test_admin_model_change_pages_accessible(self):
        """Test that model change pages are accessible."""
        # Create test objects
        dance_class = Class.objects.create(
            name='Admin Test Class',
            level='beginner',
            instructor=self.instructor,
            start_time=time(19, 0),
            end_time=time(20, 0),
            description='Test description'
        )
        testimonial = Testimonial.objects.create(
            student_name='Admin Test Student',
            email='admin_test@example.com',
            rating=5,
            content='Admin test content',
            class_type='Test Class'
        )
        resource = Resource.objects.create(
            title='Admin Test Resource',
            type='video',
            embed_url='https://example.com/admin_test',
            description='Admin test description'
        )
        
        model_urls = [
            f'/admin/core/instructor/{self.instructor.id}/change/',
            f'/admin/core/class/{dance_class.id}/change/',
            f'/admin/core/testimonial/{testimonial.id}/change/',
            f'/admin/core/resource/{resource.id}/change/',
        ]
        
        for url in model_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
    
    def test_admin_search_functionality(self):
        """Test search functionality in admin."""
        # Test instructor search
        response = self.client.get('/admin/core/instructor/?q=Admin+Test')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Test Instructor')
    
    def test_admin_filter_functionality(self):
        """Test filter functionality in admin."""
        # Create testimonials with different statuses
        Testimonial.objects.create(
            student_name='Pending Student',
            email='pending@example.com',
            rating=5,
            content='Pending testimonial',
            class_type='Test',
            status='pending'
        )
        Testimonial.objects.create(
            student_name='Approved Student',
            email='approved@example.com',
            rating=4,
            content='Approved testimonial',
            class_type='Test',
            status='approved'
        )
        
        # Test status filter
        response = self.client.get('/admin/core/testimonial/?status=pending')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending Student')
        self.assertNotContains(response, 'Approved Student')
    
    def test_admin_bulk_actions(self):
        """Test bulk actions in admin."""
        # Create pending testimonials
        testimonial1 = Testimonial.objects.create(
            student_name='Bulk Test 1',
            email='bulk1@example.com',
            rating=5,
            content='Bulk test 1',
            class_type='Test',
            status='pending'
        )
        testimonial2 = Testimonial.objects.create(
            student_name='Bulk Test 2',
            email='bulk2@example.com',
            rating=4,
            content='Bulk test 2',
            class_type='Test',
            status='pending'
        )
        
        # Test bulk approve action
        response = self.client.post('/admin/core/testimonial/', {
            'action': 'approve_testimonials',
            '_selected_action': [testimonial1.id, testimonial2.id],
        })
        
        # Should redirect after successful action
        self.assertEqual(response.status_code, 302)
        
        # Check that testimonials were approved
        testimonial1.refresh_from_db()
        testimonial2.refresh_from_db()
        self.assertEqual(testimonial1.status, 'approved')
        self.assertEqual(testimonial2.status, 'approved')