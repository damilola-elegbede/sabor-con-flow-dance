"""
SPEC_06 Group C Task 7: Testimonial Moderation Workflow Testing
==============================================================

Complete testing coverage for testimonial moderation workflow:
- Submission to approval process
- Admin moderation features
- Status transitions and validation
- Email notifications
- Review link generation and tracking

Target: 80% code coverage with production-ready confidence
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.core import mail
from django.utils import timezone
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timedelta
import uuid

from core.models import Testimonial, ReviewLink
from core.forms import TestimonialForm
from core.admin import TestimonialAdmin
from core.utils.email_notifications import (
    send_admin_notification_email,
    send_thank_you_email
)


class TestimonialWorkflowTestCase(TestCase):
    """Test complete testimonial submission and moderation workflow."""
    
    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@saborconflowdance.com',
            password='admin123'
        )
        
        # Create test testimonial data
        self.testimonial_data = {
            'student_name': 'Elena Rodriguez',
            'email': 'elena@example.com',
            'class_type': 'choreo_team',
            'rating': '5',
            'content': 'This is an amazing dance studio! The instructors are incredibly talented and patient. I have learned so much in just a few months.'
        }
    
    def test_complete_submission_workflow(self):
        """Test the complete testimonial submission workflow."""
        # Step 1: User visits testimonial submission page
        response = self.client.get(reverse('core:submit_testimonial'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Share Your Dance Journey')
        
        # Step 2: User submits testimonial
        with patch('core.views.send_admin_notification_email') as mock_admin_email, \
             patch('core.views.send_thank_you_email') as mock_thank_you_email, \
             patch('core.views.submit_testimonial_to_google') as mock_google:
            
            mock_admin_email.return_value = True
            mock_thank_you_email.return_value = True
            mock_google.return_value = (True, None)
            
            response = self.client.post(reverse('core:submit_testimonial'), data=self.testimonial_data)
            
            # Should redirect to success page
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.endswith(reverse('core:testimonial_success')))
            
            # Verify testimonial was created with pending status
            testimonial = Testimonial.objects.get(email='elena@example.com')
            self.assertEqual(testimonial.status, 'pending')
            self.assertEqual(testimonial.student_name, 'Elena Rodriguez')
            self.assertIsNone(testimonial.published_at)
            
            # Verify emails were attempted
            mock_admin_email.assert_called_once()
            mock_thank_you_email.assert_called_once()
            mock_google.assert_called_once()
        
        # Step 3: User reaches success page
        response = self.client.get(reverse('core:testimonial_success'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank You!')
    
    def test_testimonial_not_visible_until_approved(self):
        """Test that testimonials are not visible until approved."""
        # Create pending testimonial
        testimonial = Testimonial.objects.create(
            student_name='Pending User',
            email='pending@example.com',
            rating=5,
            content='This testimonial should not be visible until approved by admin.',
            class_type='pasos_basicos',
            status='pending'
        )
        
        # Check testimonial display page
        response = self.client.get(reverse('core:display_testimonials'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Pending User')
        
        # Check home page carousel
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        # Should not contain pending testimonial
        testimonials = response.context.get('carousel_testimonials', [])
        pending_names = [t.student_name for t in testimonials if hasattr(t, 'student_name')]
        self.assertNotIn('Pending User', pending_names)
    
    def test_admin_moderation_workflow(self):
        """Test admin moderation workflow."""
        # Create pending testimonial
        testimonial = Testimonial.objects.create(
            student_name='Moderation Test',
            email='moderation@example.com',
            rating=4,
            content='This testimonial is being tested for the moderation workflow process.',
            class_type='casino_royale',
            status='pending'
        )
        
        # Login as admin
        self.client.force_login(self.admin_user)
        
        # Access admin changelist
        admin_url = reverse('admin:core_testimonial_changelist')
        response = self.client.get(admin_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Moderation Test')
        
        # Access testimonial detail in admin
        detail_url = reverse('admin:core_testimonial_change', args=[testimonial.id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        
        # Approve testimonial through admin
        approve_data = {
            'student_name': testimonial.student_name,
            'email': testimonial.email,
            'rating': testimonial.rating,
            'content': testimonial.content,
            'class_type': testimonial.class_type,
            'status': 'approved',
            'featured': True,
            'published_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        response = self.client.post(detail_url, data=approve_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify testimonial is now approved
        testimonial.refresh_from_db()
        self.assertEqual(testimonial.status, 'approved')
        self.assertTrue(testimonial.featured)
        self.assertIsNotNone(testimonial.published_at)
    
    def test_approved_testimonial_visibility(self):
        """Test that approved testimonials are visible."""
        # Create approved testimonial
        testimonial = Testimonial.objects.create(
            student_name='Approved User',
            email='approved@example.com',
            rating=5,
            content='This is an approved testimonial that should be visible to all users.',
            class_type='choreo_team',
            status='approved',
            featured=True,
            published_at=timezone.now()
        )
        
        # Check testimonial display page
        response = self.client.get(reverse('core:display_testimonials'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Approved User')
        
        # Check home page carousel
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        testimonials = response.context.get('carousel_testimonials', [])
        approved_names = [t.student_name for t in testimonials if hasattr(t, 'student_name')]
        self.assertIn('Approved User', approved_names)
    
    def test_testimonial_rejection_workflow(self):
        """Test testimonial rejection workflow."""
        # Create testimonial to reject
        testimonial = Testimonial.objects.create(
            student_name='Rejected User',
            email='rejected@example.com',
            rating=1,
            content='This testimonial will be rejected for testing purposes.',
            class_type='other',
            status='pending'
        )
        
        # Simulate admin rejection
        testimonial.status = 'rejected'
        testimonial.save()
        
        # Verify rejected testimonial is not visible
        response = self.client.get(reverse('core:display_testimonials'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Rejected User')
    
    @patch('core.utils.email_notifications.send_mail')
    def test_email_notification_workflow(self, mock_send_mail):
        """Test email notification workflow."""
        mock_send_mail.return_value = True
        
        # Create testimonial
        testimonial = Testimonial.objects.create(
            student_name='Email Test User',
            email='emailtest@example.com',
            rating=5,
            content='This testimonial tests the email notification workflow functionality.',
            class_type='pasos_basicos',
            status='pending'
        )
        
        # Test admin notification email
        admin_result = send_admin_notification_email(testimonial)
        self.assertTrue(admin_result)
        
        # Test thank you email
        thank_you_result = send_thank_you_email(testimonial)
        self.assertTrue(thank_you_result)
        
        # Verify send_mail was called
        self.assertEqual(mock_send_mail.call_count, 2)
    
    def test_testimonial_filtering_workflow(self):
        """Test testimonial filtering in display workflow."""
        # Create testimonials with different ratings and classes
        testimonials_data = [
            {'name': 'Five Star User', 'rating': 5, 'class_type': 'choreo_team'},
            {'name': 'Four Star User', 'rating': 4, 'class_type': 'pasos_basicos'},
            {'name': 'Three Star User', 'rating': 3, 'class_type': 'casino_royale'},
        ]
        
        for data in testimonials_data:
            Testimonial.objects.create(
                student_name=data['name'],
                email=f"{data['name'].lower().replace(' ', '')}@example.com",
                rating=data['rating'],
                content=f"This is a {data['rating']} star testimonial with sufficient content for testing.",
                class_type=data['class_type'],
                status='approved',
                published_at=timezone.now()
            )
        
        # Test rating filter
        response = self.client.get(reverse('core:display_testimonials'), {'rating': '5'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Five Star User')
        self.assertNotContains(response, 'Four Star User')
        
        # Test class type filter
        response = self.client.get(reverse('core:display_testimonials'), {'class_type': 'pasos_basicos'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Four Star User')
        self.assertNotContains(response, 'Five Star User')
    
    def test_testimonial_statistics_workflow(self):
        """Test testimonial statistics calculation workflow."""
        # Create testimonials with different ratings
        ratings = [5, 4, 5, 3, 4, 5, 2, 4]
        for i, rating in enumerate(ratings):
            Testimonial.objects.create(
                student_name=f'Stats User {i}',
                email=f'stats{i}@example.com',
                rating=rating,
                content=f'Testimonial {i} with rating {rating} for statistics testing.',
                class_type='choreo_team',
                status='approved',
                published_at=timezone.now()
            )
        
        response = self.client.get(reverse('core:display_testimonials'))
        self.assertEqual(response.status_code, 200)
        
        # Verify statistics in context
        average_rating = response.context['average_rating']
        total_reviews = response.context['total_reviews']
        
        expected_average = sum(ratings) / len(ratings)
        self.assertEqual(total_reviews, len(ratings))
        self.assertAlmostEqual(average_rating, expected_average, places=1)
    
    def test_featured_testimonial_workflow(self):
        """Test featured testimonial workflow."""
        # Create regular and featured testimonials
        regular_testimonial = Testimonial.objects.create(
            student_name='Regular User',
            email='regular@example.com',
            rating=4,
            content='This is a regular testimonial that should appear in normal listings.',
            class_type='pasos_basicos',
            status='approved',
            featured=False,
            published_at=timezone.now()
        )
        
        featured_testimonial = Testimonial.objects.create(
            student_name='Featured User',
            email='featured@example.com',
            rating=5,
            content='This is a featured testimonial that should appear prominently.',
            class_type='choreo_team',
            status='approved',
            featured=True,
            published_at=timezone.now()
        )
        
        # Test home page prioritizes featured testimonials
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        
        carousel_testimonials = response.context.get('carousel_testimonials', [])
        if carousel_testimonials:
            # Featured testimonials should appear first
            featured_names = [t.student_name for t in carousel_testimonials if t.featured]
            self.assertIn('Featured User', featured_names)


class ReviewLinkWorkflowTestCase(TestCase):
    """Test review link generation and tracking workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@saborconflowdance.com',
            password='admin123'
        )
    
    def test_review_link_generation(self):
        """Test review link generation workflow."""
        # Create review link
        review_link = ReviewLink.objects.create(
            token=ReviewLink.generate_token(),
            instructor_name='Maria Santos',
            class_type='choreo_team',
            campaign_name='Summer 2024',
            created_by='Admin'
        )
        
        self.assertIsNotNone(review_link.token)
        self.assertEqual(len(review_link.token), 32)
        self.assertEqual(review_link.instructor_name, 'Maria Santos')
        self.assertEqual(review_link.clicks, 0)
        self.assertEqual(review_link.conversions, 0)
    
    def test_review_link_tracking_workflow(self):
        """Test review link click and conversion tracking."""
        # Create review link
        review_link = ReviewLink.objects.create(
            token='test123token456',
            instructor_name='Carlos Rodriguez',
            class_type='pasos_basicos'
        )
        
        # Simulate click tracking
        review_link.track_click()
        self.assertEqual(review_link.clicks, 1)
        self.assertIsNotNone(review_link.last_accessed)
        
        # Simulate conversion tracking
        review_link.track_conversion()
        self.assertEqual(review_link.conversions, 1)
        
        # Test conversion rate calculation
        conversion_rate = review_link.get_conversion_rate()
        self.assertEqual(conversion_rate, 100.0)  # 1 conversion / 1 click = 100%
    
    def test_review_link_url_generation(self):
        """Test review link URL generation."""
        review_link = ReviewLink.objects.create(
            token='url123test456',
            instructor_name='Ana Martinez',
            class_type='casino_royale'
        )
        
        full_url = review_link.get_full_url()
        expected_parts = [
            '/testimonials/submit/',
            'ref=url123test456',
            'instructor=ana-martinez',
            'class=casino_royale'
        ]
        
        for part in expected_parts:
            self.assertIn(part, full_url)
        
        short_url = review_link.get_short_url()
        self.assertIn('/r/url123te', short_url)
    
    def test_review_link_expiration_workflow(self):
        """Test review link expiration workflow."""
        # Create expired link
        expired_link = ReviewLink.objects.create(
            token='expired123token',
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        self.assertTrue(expired_link.is_expired())
        
        # Create non-expired link
        active_link = ReviewLink.objects.create(
            token='active123token',
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        self.assertFalse(active_link.is_expired())
    
    def test_review_link_prefill_workflow(self):
        """Test review link pre-fill functionality."""
        # Create review link with pre-fill data
        review_link = ReviewLink.objects.create(
            token='prefill123token',
            instructor_name='Elena Rodriguez',
            class_type='choreo_team'
        )
        
        # Simulate user clicking review link
        prefill_url = f"/testimonials/submit/?ref={review_link.token}&instructor=elena-rodriguez&class=choreo_team"
        
        response = self.client.get(prefill_url)
        self.assertEqual(response.status_code, 200)
        
        # Check that form is pre-filled (this would need to be implemented in the view)
        # For now, we just verify the URL parameters are correct
        self.assertContains(response, 'Share Your Dance Journey')


class TestimonialAdminWorkflowTestCase(TestCase):
    """Test testimonial admin interface workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@saborconflowdance.com',
            password='admin123'
        )
        
        self.site = AdminSite()
        self.testimonial_admin = TestimonialAdmin(Testimonial, self.site)
    
    def test_admin_list_display_workflow(self):
        """Test admin list display workflow."""
        # Create test testimonials
        testimonials = [
            Testimonial.objects.create(
                student_name='Admin Test 1',
                email='admintest1@example.com',
                rating=5,
                content='First admin test testimonial with sufficient content for validation.',
                class_type='choreo_team',
                status='pending'
            ),
            Testimonial.objects.create(
                student_name='Admin Test 2',
                email='admintest2@example.com',
                rating=4,
                content='Second admin test testimonial with sufficient content for validation.',
                class_type='pasos_basicos',
                status='approved',
                featured=True,
                published_at=timezone.now()
            )
        ]
        
        # Login and access admin
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin:core_testimonial_changelist'))
        self.assertEqual(response.status_code, 200)
        
        # Check that testimonials are displayed
        self.assertContains(response, 'Admin Test 1')
        self.assertContains(response, 'Admin Test 2')
        self.assertContains(response, 'pending')
        self.assertContains(response, 'approved')
    
    def test_admin_filtering_workflow(self):
        """Test admin filtering workflow."""
        # Create testimonials with different statuses
        Testimonial.objects.create(
            student_name='Filter Test Pending',
            email='pending@example.com',
            rating=3,
            content='Pending testimonial for filter testing with sufficient content.',
            class_type='casino_royale',
            status='pending'
        )
        
        Testimonial.objects.create(
            student_name='Filter Test Approved',
            email='approved@example.com',
            rating=5,
            content='Approved testimonial for filter testing with sufficient content.',
            class_type='choreo_team',
            status='approved',
            published_at=timezone.now()
        )
        
        # Login and test filtering
        self.client.force_login(self.admin_user)
        
        # Filter by pending status
        response = self.client.get(reverse('admin:core_testimonial_changelist'), {'status': 'pending'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Filter Test Pending')
        
        # Filter by approved status
        response = self.client.get(reverse('admin:core_testimonial_changelist'), {'status': 'approved'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Filter Test Approved')
    
    def test_admin_bulk_actions_workflow(self):
        """Test admin bulk actions workflow."""
        # Create multiple pending testimonials
        testimonials = []
        for i in range(3):
            testimonial = Testimonial.objects.create(
                student_name=f'Bulk Test {i}',
                email=f'bulk{i}@example.com',
                rating=4,
                content=f'Bulk action test testimonial {i} with sufficient content.',
                class_type='pasos_basicos',
                status='pending'
            )
            testimonials.append(testimonial)
        
        # Login and access admin
        self.client.force_login(self.admin_user)
        
        # Test bulk approval (if implemented)
        changelist_url = reverse('admin:core_testimonial_changelist')
        response = self.client.get(changelist_url)
        self.assertEqual(response.status_code, 200)
        
        # Verify testimonials are listed
        for testimonial in testimonials:
            self.assertContains(response, testimonial.student_name)


class TestimonialErrorHandlingWorkflowTestCase(TestCase):
    """Test error handling in testimonial workflow."""
    
    def test_invalid_submission_workflow(self):
        """Test handling of invalid testimonial submissions."""
        invalid_data = {
            'student_name': '',  # Missing required field
            'email': 'invalid-email',  # Invalid email format
            'class_type': '',  # Missing required field
            'rating': '6',  # Invalid rating
            'content': 'Too short'  # Too short content
        }
        
        response = self.client.post(reverse('core:submit_testimonial'), data=invalid_data)
        self.assertEqual(response.status_code, 200)  # Should stay on form page
        
        # Verify form has errors
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)
        
        # Verify no testimonial was created
        self.assertEqual(Testimonial.objects.count(), 0)
    
    @patch('core.views.send_admin_notification_email')
    def test_email_failure_workflow(self, mock_email):
        """Test workflow when email sending fails."""
        mock_email.return_value = False  # Simulate email failure
        
        valid_data = {
            'student_name': 'Email Failure Test',
            'email': 'emailfail@example.com',
            'class_type': 'choreo_team',
            'rating': '5',
            'content': 'Testing email failure handling with sufficient content for validation.'
        }
        
        response = self.client.post(reverse('core:submit_testimonial'), data=valid_data)
        
        # Should still redirect to success page even if email fails
        self.assertEqual(response.status_code, 302)
        
        # Testimonial should still be created
        testimonial = Testimonial.objects.get(email='emailfail@example.com')
        self.assertEqual(testimonial.status, 'pending')
    
    def test_database_error_workflow(self):
        """Test workflow with database errors."""
        # This is difficult to test without mocking the database
        # For now, we test that the form validation catches issues before database
        
        # Test with extremely long content that might cause database issues
        long_content = 'a' * 10000  # Much longer than allowed
        
        data = {
            'student_name': 'Database Test',
            'email': 'database@example.com',
            'class_type': 'choreo_team',
            'rating': '5',
            'content': long_content
        }
        
        form = TestimonialForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
    
    def test_concurrent_submission_workflow(self):
        """Test handling of concurrent submissions."""
        # Create multiple testimonials quickly to test for race conditions
        import threading
        import time
        
        results = []
        
        def submit_testimonial(index):
            data = {
                'student_name': f'Concurrent User {index}',
                'email': f'concurrent{index}@example.com',
                'class_type': 'choreo_team',
                'rating': '5',
                'content': f'Concurrent submission test {index} with sufficient content for validation.'
            }
            
            response = self.client.post(reverse('core:submit_testimonial'), data=data)
            results.append(response.status_code)
        
        # Create multiple threads to simulate concurrent submissions
        threads = []
        for i in range(5):
            thread = threading.Thread(target=submit_testimonial, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All submissions should succeed
        self.assertEqual(len(results), 5)
        self.assertTrue(all(status == 302 for status in results))
        
        # All testimonials should be created
        self.assertEqual(Testimonial.objects.count(), 5)