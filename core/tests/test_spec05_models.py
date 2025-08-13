"""
Comprehensive tests for SPEC_05 New Models Implementation

Tests all new models introduced in SPEC_05 including FacebookEvent,
ContactSubmission, BookingConfirmation, RSVPSubmission, and SpotifyPlaylist
with complete validation, relationships, and business logic testing.
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from django.db.models import Q
from core.models import (
    FacebookEvent, ContactSubmission, BookingConfirmation, 
    RSVPSubmission, SpotifyPlaylist
)


class FacebookEventModelTestCase(TestCase):
    """Test cases for the FacebookEvent model - SPEC_05 Group B Task 6."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_event_data = {
            'facebook_id': 'fb_event_12345',
            'name': 'Salsa Social Night',
            'description': 'Join us for an evening of social salsa dancing with live music and professional instructors.',
            'start_time': timezone.now() + timedelta(days=10),
            'end_time': timezone.now() + timedelta(days=10, hours=4),
            'formatted_date': 'Saturday, January 20, 2024',
            'formatted_time': '7:00 PM',
            'cover_photo_url': 'https://facebook.com/events/cover_12345.jpg',
            'facebook_url': 'https://www.facebook.com/events/fb_event_12345',
            'location_name': 'Avalon Ballroom',
            'location_address': '6185 Arapahoe Rd, Boulder, CO 80303',
            'is_active': True,
            'featured': True,
            'order': 1
        }
    
    def test_facebook_event_creation(self):
        """Test creating a Facebook event with valid data."""
        event = FacebookEvent.objects.create(**self.valid_event_data)
        
        self.assertEqual(event.facebook_id, 'fb_event_12345')
        self.assertEqual(event.name, 'Salsa Social Night')
        self.assertEqual(event.description, 'Join us for an evening of social salsa dancing with live music and professional instructors.')
        self.assertEqual(event.formatted_date, 'Saturday, January 20, 2024')
        self.assertEqual(event.formatted_time, '7:00 PM')
        self.assertEqual(event.location_name, 'Avalon Ballroom')
        self.assertTrue(event.is_active)
        self.assertTrue(event.featured)
        self.assertIsNotNone(event.created_at)
        self.assertIsNotNone(event.last_synced)
    
    def test_facebook_event_str_representation(self):
        """Test the string representation of a Facebook event."""
        event = FacebookEvent.objects.create(**self.valid_event_data)
        expected = "Salsa Social Night - Saturday, January 20, 2024"
        self.assertEqual(str(event), expected)
    
    def test_facebook_event_unique_facebook_id(self):
        """Test that facebook_id must be unique."""
        FacebookEvent.objects.create(**self.valid_event_data)
        
        # Try to create duplicate
        duplicate_data = self.valid_event_data.copy()
        duplicate_data['name'] = 'Different Event Name'
        
        with self.assertRaises(IntegrityError):
            FacebookEvent.objects.create(**duplicate_data)
    
    def test_facebook_event_get_short_description(self):
        """Test the get_short_description method."""
        event = FacebookEvent.objects.create(**self.valid_event_data)
        
        # Test default length
        short_desc = event.get_short_description()
        self.assertLessEqual(len(short_desc), 150)
        
        # Test custom length
        custom_desc = event.get_short_description(max_length=50)
        self.assertLessEqual(len(custom_desc), 50)
        
        # Test with short description
        event.description = "Short desc"
        event.save()
        self.assertEqual(event.get_short_description(), "Short desc")
    
    def test_facebook_event_is_future_event(self):
        """Test the is_future_event method."""
        # Future event
        future_event = FacebookEvent.objects.create(**self.valid_event_data)
        self.assertTrue(future_event.is_future_event())
        
        # Past event
        past_data = self.valid_event_data.copy()
        past_data['facebook_id'] = 'past_event'
        past_data['start_time'] = timezone.now() - timedelta(days=1)
        past_event = FacebookEvent.objects.create(**past_data)
        self.assertFalse(past_event.is_future_event())
    
    def test_facebook_event_get_time_until_event(self):
        """Test the get_time_until_event method."""
        # Test different time scenarios
        scenarios = [
            (timedelta(hours=2), "Today"),
            (timedelta(days=1, hours=2), "Tomorrow"),
            (timedelta(days=3), "In 3 days"),
            (timedelta(days=10), "In 1 week"),
            (timedelta(days=45), "In 1 month"),
            (timedelta(days=-1), "Past event")
        ]
        
        for i, (delta, expected_pattern) in enumerate(scenarios):
            event_data = self.valid_event_data.copy()
            event_data['facebook_id'] = f'time_test_{i}'
            event_data['start_time'] = timezone.now() + delta
            event = FacebookEvent.objects.create(**event_data)
            
            result = event.get_time_until_event()
            if "Past event" in expected_pattern:
                self.assertEqual(result, "Past event")
            else:
                self.assertIn(expected_pattern.split()[0], result)  # Check first word
    
    def test_facebook_event_get_upcoming_events(self):
        """Test the get_upcoming_events class method."""
        # Create mix of past and future events
        past_event = FacebookEvent.objects.create(
            facebook_id='past_event',
            name='Past Event',
            description='Past event',
            start_time=timezone.now() - timedelta(days=1),
            formatted_date='Yesterday',
            formatted_time='7:00 PM',
            facebook_url='https://facebook.com/events/past',
            is_active=True
        )
        
        future_events = []
        for i in range(5):
            event_data = self.valid_event_data.copy()
            event_data['facebook_id'] = f'future_event_{i}'
            event_data['name'] = f'Future Event {i+1}'
            event_data['start_time'] = timezone.now() + timedelta(days=i+1)
            future_events.append(FacebookEvent.objects.create(**event_data))
        
        # Test get_upcoming_events
        upcoming = FacebookEvent.get_upcoming_events(limit=3)
        self.assertEqual(len(upcoming), 3)
        
        # Should be ordered by start_time
        for i in range(len(upcoming) - 1):
            self.assertLessEqual(upcoming[i].start_time, upcoming[i+1].start_time)
        
        # Should not include past events
        for event in upcoming:
            self.assertTrue(event.is_future_event())
    
    def test_facebook_event_get_featured_events(self):
        """Test the get_featured_events class method."""
        # Create featured and non-featured events
        featured_events = []
        for i in range(3):
            event_data = self.valid_event_data.copy()
            event_data['facebook_id'] = f'featured_event_{i}'
            event_data['name'] = f'Featured Event {i+1}'
            event_data['start_time'] = timezone.now() + timedelta(days=i+1)
            event_data['featured'] = True
            event_data['order'] = i
            featured_events.append(FacebookEvent.objects.create(**event_data))
        
        # Create non-featured event
        non_featured_data = self.valid_event_data.copy()
        non_featured_data['facebook_id'] = 'non_featured'
        non_featured_data['name'] = 'Non Featured Event'
        non_featured_data['featured'] = False
        FacebookEvent.objects.create(**non_featured_data)
        
        # Test get_featured_events
        featured = FacebookEvent.get_featured_events(limit=5)
        self.assertEqual(len(featured), 3)
        
        # Should all be featured
        for event in featured:
            self.assertTrue(event.featured)
        
        # Should be ordered by order, then start_time
        for i in range(len(featured) - 1):
            self.assertLessEqual(featured[i].order, featured[i+1].order)


class ContactSubmissionModelTestCase(TestCase):
    """Test cases for the ContactSubmission model - SPEC_05 Group B Task 10."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_contact_data = {
            'name': 'Maria Gonzalez',
            'email': 'maria.gonzalez@example.com',
            'phone': '(555) 123-4567',
            'interest': 'private_lesson',
            'message': 'I would like to schedule private bachata lessons. I am a complete beginner and would prefer evening classes.',
            'status': 'new',
            'priority': 'normal',
            'source': 'website'
        }
    
    def test_contact_submission_creation(self):
        """Test creating a contact submission with valid data."""
        contact = ContactSubmission.objects.create(**self.valid_contact_data)
        
        self.assertEqual(contact.name, 'Maria Gonzalez')
        self.assertEqual(contact.email, 'maria.gonzalez@example.com')
        self.assertEqual(contact.phone, '(555) 123-4567')
        self.assertEqual(contact.interest, 'private_lesson')
        self.assertEqual(contact.status, 'new')
        self.assertEqual(contact.priority, 'normal')
        self.assertEqual(contact.source, 'website')
        self.assertFalse(contact.admin_notification_sent)
        self.assertFalse(contact.auto_reply_sent)
        self.assertIsNotNone(contact.created_at)
    
    def test_contact_submission_str_representation(self):
        """Test the string representation of a contact submission."""
        contact = ContactSubmission.objects.create(**self.valid_contact_data)
        expected = "Maria Gonzalez - Private Lessons (New)"
        self.assertEqual(str(contact), expected)
    
    def test_contact_submission_choices_validation(self):
        """Test choice field validation for contact submission."""
        # Test valid interest choices
        valid_interests = ['classes', 'private_lesson', 'workshop', 'events', 'choreography', 'general', 'other']
        for interest in valid_interests:
            data = self.valid_contact_data.copy()
            data['email'] = f'test_{interest}@example.com'
            data['interest'] = interest
            contact = ContactSubmission.objects.create(**data)
            self.assertEqual(contact.interest, interest)
        
        # Test valid status choices
        valid_statuses = ['new', 'in_progress', 'responded', 'closed']
        for status in valid_statuses:
            data = self.valid_contact_data.copy()
            data['email'] = f'test_{status}@example.com'
            data['status'] = status
            contact = ContactSubmission.objects.create(**data)
            self.assertEqual(contact.status, status)
        
        # Test valid priority choices
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        for priority in valid_priorities:
            data = self.valid_contact_data.copy()
            data['email'] = f'test_{priority}@example.com'
            data['priority'] = priority
            contact = ContactSubmission.objects.create(**data)
            self.assertEqual(contact.priority, priority)
    
    def test_contact_submission_get_urgency_score(self):
        """Test the get_urgency_score method."""
        # Test high priority
        high_priority_data = self.valid_contact_data.copy()
        high_priority_data['priority'] = 'high'
        high_priority_data['interest'] = 'private_lesson'
        contact = ContactSubmission.objects.create(**high_priority_data)
        
        score = contact.get_urgency_score()
        self.assertGreater(score, 20)  # Should have high score
        
        # Test low priority
        low_priority_data = self.valid_contact_data.copy()
        low_priority_data['priority'] = 'low'
        low_priority_data['interest'] = 'general'
        low_priority_data['email'] = 'low@example.com'
        low_contact = ContactSubmission.objects.create(**low_priority_data)
        
        low_score = low_contact.get_urgency_score()
        self.assertLess(low_score, score)  # Should be lower than high priority
    
    def test_contact_submission_mark_responded(self):
        """Test the mark_responded method."""
        contact = ContactSubmission.objects.create(**self.valid_contact_data)
        self.assertEqual(contact.status, 'new')
        self.assertIsNone(contact.responded_at)
        
        contact.mark_responded()
        contact.refresh_from_db()
        
        self.assertEqual(contact.status, 'responded')
        self.assertIsNotNone(contact.responded_at)
    
    def test_contact_submission_get_pending_count(self):
        """Test the get_pending_count class method."""
        # Create contacts with different statuses
        for i, status in enumerate(['new', 'in_progress', 'responded', 'closed']):
            data = self.valid_contact_data.copy()
            data['email'] = f'test_{i}@example.com'
            data['status'] = status
            ContactSubmission.objects.create(**data)
        
        pending_count = ContactSubmission.get_pending_count()
        self.assertEqual(pending_count, 2)  # 'new' and 'in_progress'
    
    def test_contact_submission_get_recent_inquiries(self):
        """Test the get_recent_inquiries class method."""
        # Create old inquiry
        old_data = self.valid_contact_data.copy()
        old_data['email'] = 'old@example.com'
        old_contact = ContactSubmission.objects.create(**old_data)
        old_contact.created_at = timezone.now() - timedelta(days=10)
        old_contact.save()
        
        # Create recent inquiry
        recent_data = self.valid_contact_data.copy()
        recent_data['email'] = 'recent@example.com'
        recent_contact = ContactSubmission.objects.create(**recent_data)
        
        recent_inquiries = ContactSubmission.get_recent_inquiries(days=7)
        self.assertEqual(len(recent_inquiries), 1)
        self.assertEqual(recent_inquiries[0].email, 'recent@example.com')


class BookingConfirmationModelTestCase(TestCase):
    """Test cases for the BookingConfirmation model - SPEC_05 Group B Task 10."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_booking_data = {
            'customer_name': 'Carlos Rodriguez',
            'customer_email': 'carlos.rodriguez@example.com',
            'customer_phone': '(555) 987-6543',
            'booking_type': 'private_lesson',
            'class_name': 'Private Salsa Intensive',
            'instructor_name': 'Sofia Martinez',
            'booking_date': timezone.now() + timedelta(days=5),
            'duration_minutes': 90,
            'location': 'Avalon Ballroom, Boulder, CO',
            'price': Decimal('120.00'),
            'payment_method': 'Credit Card',
            'payment_reference': 'CC_12345',
            'status': 'confirmed',
            'special_instructions': 'Focus on advanced turn patterns and styling.',
            'calendly_event_id': 'calendly_event_123'
        }
    
    def test_booking_confirmation_creation(self):
        """Test creating a booking confirmation with valid data."""
        booking = BookingConfirmation.objects.create(**self.valid_booking_data)
        
        self.assertEqual(booking.customer_name, 'Carlos Rodriguez')
        self.assertEqual(booking.customer_email, 'carlos.rodriguez@example.com')
        self.assertEqual(booking.booking_type, 'private_lesson')
        self.assertEqual(booking.class_name, 'Private Salsa Intensive')
        self.assertEqual(booking.instructor_name, 'Sofia Martinez')
        self.assertEqual(booking.duration_minutes, 90)
        self.assertEqual(booking.price, Decimal('120.00'))
        self.assertEqual(booking.status, 'confirmed')
        self.assertIsNotNone(booking.booking_id)  # Should auto-generate
        self.assertFalse(booking.confirmation_email_sent)
        self.assertFalse(booking.reminder_email_sent)
    
    def test_booking_confirmation_str_representation(self):
        """Test the string representation of a booking confirmation."""
        booking = BookingConfirmation.objects.create(**self.valid_booking_data)
        expected_pattern = f"{booking.booking_id} - Carlos Rodriguez (Private Salsa Intensive)"
        self.assertEqual(str(booking), expected_pattern)
    
    def test_booking_confirmation_auto_booking_id(self):
        """Test automatic booking ID generation."""
        booking = BookingConfirmation.objects.create(**self.valid_booking_data)
        
        self.assertIsNotNone(booking.booking_id)
        self.assertTrue(booking.booking_id.startswith('PRI'))  # private_lesson prefix
        self.assertEqual(len(booking.booking_id), 15)  # Expected length
        
        # Test different booking types
        class_data = self.valid_booking_data.copy()
        class_data['customer_email'] = 'class@example.com'
        class_data['booking_type'] = 'class'
        class_booking = BookingConfirmation.objects.create(**class_data)
        
        self.assertTrue(class_booking.booking_id.startswith('CLA'))
    
    def test_booking_confirmation_unique_booking_id(self):
        """Test that booking IDs are unique."""
        booking1 = BookingConfirmation.objects.create(**self.valid_booking_data)
        
        booking2_data = self.valid_booking_data.copy()
        booking2_data['customer_email'] = 'different@example.com'
        booking2 = BookingConfirmation.objects.create(**booking2_data)
        
        self.assertNotEqual(booking1.booking_id, booking2.booking_id)
    
    def test_booking_confirmation_datetime_methods(self):
        """Test datetime formatting methods."""
        booking = BookingConfirmation.objects.create(**self.valid_booking_data)
        
        # Test formatted datetime
        formatted_datetime = booking.get_booking_datetime_formatted()
        self.assertIn('at', formatted_datetime)
        self.assertIn('M', formatted_datetime)  # AM/PM
        
        # Test date only
        formatted_date = booking.get_booking_date_only()
        self.assertNotIn(':', formatted_date)  # No time
        
        # Test time only
        formatted_time = booking.get_booking_time_only()
        self.assertIn(':', formatted_time)  # Has time
        self.assertIn('M', formatted_time)  # AM/PM
    
    def test_booking_confirmation_is_upcoming(self):
        """Test the is_upcoming method."""
        # Future booking
        future_booking = BookingConfirmation.objects.create(**self.valid_booking_data)
        self.assertTrue(future_booking.is_upcoming())
        
        # Past booking
        past_data = self.valid_booking_data.copy()
        past_data['customer_email'] = 'past@example.com'
        past_data['booking_date'] = timezone.now() - timedelta(days=1)
        past_booking = BookingConfirmation.objects.create(**past_data)
        self.assertFalse(past_booking.is_upcoming())
    
    def test_booking_confirmation_get_time_until_booking(self):
        """Test the get_time_until_booking method."""
        # Test different time scenarios
        scenarios = [
            (timedelta(minutes=30), "minutes"),
            (timedelta(hours=2), "hours"),
            (timedelta(days=3), "days"),
            (timedelta(days=-1), "Past booking")
        ]
        
        for i, (delta, expected_unit) in enumerate(scenarios):
            booking_data = self.valid_booking_data.copy()
            booking_data['customer_email'] = f'time_test_{i}@example.com'
            booking_data['booking_date'] = timezone.now() + delta
            booking = BookingConfirmation.objects.create(**booking_data)
            
            result = booking.get_time_until_booking()
            if "Past booking" in expected_unit:
                self.assertEqual(result, "Past booking")
            else:
                self.assertIn(expected_unit, result)
    
    def test_booking_confirmation_class_methods(self):
        """Test class methods for querying bookings."""
        # Create mix of bookings
        today = timezone.now()
        
        # Today's booking
        today_data = self.valid_booking_data.copy()
        today_data['customer_email'] = 'today@example.com'
        today_data['booking_date'] = today.replace(hour=15, minute=0, second=0, microsecond=0)
        today_booking = BookingConfirmation.objects.create(**today_data)
        
        # Future booking
        future_data = self.valid_booking_data.copy()
        future_data['customer_email'] = 'future@example.com'
        future_data['booking_date'] = today + timedelta(days=3)
        future_booking = BookingConfirmation.objects.create(**future_data)
        
        # Past booking
        past_data = self.valid_booking_data.copy()
        past_data['customer_email'] = 'past@example.com'
        past_data['booking_date'] = today - timedelta(days=1)
        past_booking = BookingConfirmation.objects.create(**past_data)
        
        # Test get_upcoming_bookings
        upcoming = BookingConfirmation.get_upcoming_bookings(days=7)
        self.assertGreaterEqual(len(upcoming), 2)  # Today's and future
        
        # Test get_todays_bookings
        todays = BookingConfirmation.get_todays_bookings()
        self.assertEqual(len(todays), 1)
        self.assertEqual(todays[0].customer_email, 'today@example.com')


class RSVPSubmissionModelTestCase(TestCase):
    """Test cases for the RSVPSubmission model - SPEC_05 Group B Task 7."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_rsvp_data = {
            'name': 'Ana Martinez',
            'email': 'ana.martinez@example.com',
            'phone': '(555) 456-7890',
            'class_id': 'scf-choreo',
            'class_name': 'SCF Choreo Team',
            'status': 'confirmed',
            'source': 'pastio',
            'notifications_enabled': True,
            'pastio_id': 'pastio_rsvp_12345',
            'special_requirements': 'Vegetarian meal preference',
            'plus_one': True,
            'plus_one_name': 'Roberto Martinez'
        }
    
    def test_rsvp_submission_creation(self):
        """Test creating an RSVP submission with valid data."""
        rsvp = RSVPSubmission.objects.create(**self.valid_rsvp_data)
        
        self.assertEqual(rsvp.name, 'Ana Martinez')
        self.assertEqual(rsvp.email, 'ana.martinez@example.com')
        self.assertEqual(rsvp.phone, '(555) 456-7890')
        self.assertEqual(rsvp.class_id, 'scf-choreo')
        self.assertEqual(rsvp.class_name, 'SCF Choreo Team')
        self.assertEqual(rsvp.status, 'confirmed')
        self.assertEqual(rsvp.source, 'pastio')
        self.assertTrue(rsvp.notifications_enabled)
        self.assertTrue(rsvp.plus_one)
        self.assertEqual(rsvp.plus_one_name, 'Roberto Martinez')
        self.assertIsNotNone(rsvp.created_at)
    
    def test_rsvp_submission_str_representation(self):
        """Test the string representation of an RSVP submission."""
        rsvp = RSVPSubmission.objects.create(**self.valid_rsvp_data)
        expected = "Ana Martinez - SCF Choreo Team (Confirmed)"
        self.assertEqual(str(rsvp), expected)
    
    def test_rsvp_submission_get_display_name(self):
        """Test the get_display_name method."""
        # Test with plus one name
        rsvp = RSVPSubmission.objects.create(**self.valid_rsvp_data)
        display_name = rsvp.get_display_name()
        self.assertEqual(display_name, "Ana Martinez +1 (Roberto Martinez)")
        
        # Test with plus one but no name
        rsvp_data = self.valid_rsvp_data.copy()
        rsvp_data['email'] = 'test2@example.com'
        rsvp_data['plus_one_name'] = ''
        rsvp2 = RSVPSubmission.objects.create(**rsvp_data)
        self.assertEqual(rsvp2.get_display_name(), "Ana Martinez +1")
        
        # Test without plus one
        rsvp_data = self.valid_rsvp_data.copy()
        rsvp_data['email'] = 'test3@example.com'
        rsvp_data['plus_one'] = False
        rsvp_data['plus_one_name'] = ''
        rsvp3 = RSVPSubmission.objects.create(**rsvp_data)
        self.assertEqual(rsvp3.get_display_name(), "Ana Martinez")
    
    def test_rsvp_submission_get_party_size(self):
        """Test the get_party_size method."""
        # Test with plus one
        rsvp = RSVPSubmission.objects.create(**self.valid_rsvp_data)
        self.assertEqual(rsvp.get_party_size(), 2)
        
        # Test without plus one
        rsvp_data = self.valid_rsvp_data.copy()
        rsvp_data['email'] = 'single@example.com'
        rsvp_data['plus_one'] = False
        single_rsvp = RSVPSubmission.objects.create(**rsvp_data)
        self.assertEqual(single_rsvp.get_party_size(), 1)
    
    def test_rsvp_submission_class_time_methods(self):
        """Test class time and date related methods."""
        rsvp = RSVPSubmission.objects.create(**self.valid_rsvp_data)
        
        # Test get_class_time
        class_time = rsvp.get_class_time()
        self.assertIn(':', class_time)  # Should contain time format
        self.assertIn('M', class_time)  # Should have AM/PM
        
        # Test get_next_class_date
        next_date = rsvp.get_next_class_date()
        self.assertIsInstance(next_date, type(timezone.now().date()))
        
        # Test is_upcoming
        is_upcoming = rsvp.is_upcoming()
        self.assertIsInstance(is_upcoming, bool)
    
    def test_rsvp_submission_can_cancel_and_cancel(self):
        """Test the can_cancel and cancel methods."""
        rsvp = RSVPSubmission.objects.create(**self.valid_rsvp_data)
        
        # Should be able to cancel confirmed upcoming RSVP
        self.assertTrue(rsvp.can_cancel())
        
        # Test cancellation
        result = rsvp.cancel(reason="Schedule conflict")
        self.assertTrue(result)
        
        rsvp.refresh_from_db()
        self.assertEqual(rsvp.status, 'cancelled')
        self.assertIn("Schedule conflict", rsvp.admin_notes)
        
        # Should not be able to cancel again
        self.assertFalse(rsvp.can_cancel())
    
    def test_rsvp_submission_class_methods(self):
        """Test class methods for RSVP analytics."""
        # Create RSVPs for different classes
        class_data = [
            ('scf-choreo', 'SCF Choreo Team'),
            ('pasos-basicos', 'Pasos Básicos'),
            ('casino-royale', 'Casino Royale')
        ]
        
        for i, (class_id, class_name) in enumerate(class_data):
            for j in range(i + 2):  # Different numbers for each class
                rsvp_data = self.valid_rsvp_data.copy()
                rsvp_data['email'] = f'test_{class_id}_{j}@example.com'
                rsvp_data['class_id'] = class_id
                rsvp_data['class_name'] = class_name
                rsvp_data['plus_one'] = (j == 0)  # First one has plus one
                RSVPSubmission.objects.create(**rsvp_data)
        
        # Test get_class_counts
        counts = RSVPSubmission.get_class_counts()
        self.assertIn('scf-choreo', counts)
        self.assertIn('pasos-basicos', counts)
        self.assertIn('casino-royale', counts)
        
        # Test get_upcoming_rsvps
        upcoming = RSVPSubmission.get_upcoming_rsvps(limit=5)
        self.assertLessEqual(len(upcoming), 5)
        
        # Test get_upcoming_rsvps with class filter
        choreo_rsvps = RSVPSubmission.get_upcoming_rsvps(class_id='scf-choreo')
        for rsvp in choreo_rsvps:
            self.assertEqual(rsvp.class_id, 'scf-choreo')
        
        # Test get_weekly_stats
        stats = RSVPSubmission.get_weekly_stats()
        self.assertIn('total_rsvps', stats)
        self.assertIn('confirmed_rsvps', stats)
        self.assertIn('by_class', stats)
        self.assertIn('by_source', stats)
    
    def test_rsvp_submission_unique_constraint(self):
        """Test unique constraint on email + class_id + created_at."""
        RSVPSubmission.objects.create(**self.valid_rsvp_data)
        
        # Try to create duplicate RSVP
        duplicate_data = self.valid_rsvp_data.copy()
        duplicate_data['name'] = 'Different Name'
        
        # This should raise an IntegrityError due to unique_together constraint
        with self.assertRaises(IntegrityError):
            RSVPSubmission.objects.create(**duplicate_data)


class ModelRelationshipsTestCase(TestCase):
    """Test cases for model relationships and integration."""
    
    def test_models_create_without_errors(self):
        """Test that all models can be created without errors."""
        # Create one instance of each new model
        facebook_event = FacebookEvent.objects.create(
            facebook_id='test_fb_123',
            name='Test Facebook Event',
            description='Test description',
            start_time=timezone.now() + timedelta(days=1),
            formatted_date='Tomorrow',
            formatted_time='8:00 PM',
            facebook_url='https://facebook.com/events/test_fb_123'
        )
        
        contact = ContactSubmission.objects.create(
            name='Test Contact',
            email='contact@example.com',
            interest='classes',
            message='Test message for contact form testing.'
        )
        
        booking = BookingConfirmation.objects.create(
            customer_name='Test Customer',
            customer_email='customer@example.com',
            booking_type='class',
            class_name='Test Class',
            booking_date=timezone.now() + timedelta(days=2),
            price=Decimal('25.00')
        )
        
        rsvp = RSVPSubmission.objects.create(
            name='Test RSVP',
            email='rsvp@example.com',
            class_id='scf-choreo',
            class_name='SCF Choreo Team'
        )
        
        playlist = SpotifyPlaylist.objects.create(
            class_type='choreo_team',
            title='Test Playlist',
            description='Test playlist description',
            spotify_playlist_id='test_playlist_123'
        )
        
        # Verify all were created successfully
        self.assertEqual(FacebookEvent.objects.count(), 1)
        self.assertEqual(ContactSubmission.objects.count(), 1)
        self.assertEqual(BookingConfirmation.objects.count(), 1)
        self.assertEqual(RSVPSubmission.objects.count(), 1)
        self.assertEqual(SpotifyPlaylist.objects.count(), 1)
    
    def test_model_indexes_and_performance(self):
        """Test that model indexes work correctly for performance."""
        # Create multiple records for performance testing
        for i in range(20):
            FacebookEvent.objects.create(
                facebook_id=f'perf_test_{i}',
                name=f'Performance Test Event {i}',
                description='Performance test',
                start_time=timezone.now() + timedelta(days=i),
                formatted_date=f'Day {i}',
                formatted_time='8:00 PM',
                facebook_url=f'https://facebook.com/events/perf_test_{i}',
                is_active=(i % 2 == 0),
                featured=(i < 5)
            )
        
        # Test efficient queries using indexes
        with self.assertNumQueries(1):
            list(FacebookEvent.objects.filter(is_active=True, start_time__gt=timezone.now())[:5])
        
        with self.assertNumQueries(1):
            list(FacebookEvent.objects.filter(featured=True, start_time__gt=timezone.now())[:3])
    
    def test_model_ordering_and_meta_options(self):
        """Test model Meta options like ordering."""
        # Test FacebookEvent ordering
        event1 = FacebookEvent.objects.create(
            facebook_id='order_test_1',
            name='Later Event',
            description='Test',
            start_time=timezone.now() + timedelta(days=2),
            formatted_date='Later',
            formatted_time='8:00 PM',
            facebook_url='https://facebook.com/events/order_test_1'
        )
        
        event2 = FacebookEvent.objects.create(
            facebook_id='order_test_2',
            name='Earlier Event',
            description='Test',
            start_time=timezone.now() + timedelta(days=1),
            formatted_date='Earlier',
            formatted_time='8:00 PM',
            facebook_url='https://facebook.com/events/order_test_2'
        )
        
        events = list(FacebookEvent.objects.all())
        # Should be ordered by start_time (earlier first)
        self.assertEqual(events[0].name, 'Earlier Event')
        self.assertEqual(events[1].name, 'Later Event')
    
    def test_model_validation_edge_cases(self):
        """Test model validation with edge cases and boundary conditions."""
        # Test extremely long strings
        long_name = 'x' * 200
        with self.assertRaises(Exception):  # ValidationError or DataError
            contact = ContactSubmission(
                name=long_name,
                email='test@example.com',
                interest='classes',
                message='Test message'
            )
            contact.full_clean()
        
        # Test future date validation for bookings
        future_booking = BookingConfirmation(
            customer_name='Future Test',
            customer_email='future@example.com',
            booking_type='class',
            class_name='Future Class',
            booking_date=timezone.now() + timedelta(days=365),  # Far future
            price=Decimal('20.00')
        )
        future_booking.full_clean()  # Should not raise error
        
        # Test edge case for RSVP party size
        rsvp = RSVPSubmission.objects.create(
            name='Edge Case Test',
            email='edge@example.com',
            class_id='scf-choreo',
            class_name='SCF Choreo Team',
            plus_one=True,
            plus_one_name=''  # Plus one but no name
        )
        self.assertEqual(rsvp.get_display_name(), 'Edge Case Test +1')