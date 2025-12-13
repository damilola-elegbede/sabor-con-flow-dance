"""
Tests for the contact form functionality.

Note: Uses SimpleTestCase since this site doesn't use a database.
"""
import json
from django.test import SimpleTestCase, Client
from django.urls import reverse

from core.forms import ContactForm


class ContactFormValidationTest(SimpleTestCase):
    """Test ContactForm validation."""

    def test_valid_form(self):
        """Test form with valid data."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'general',
            'message': 'This is a test message for the form.',
        }
        form = ContactForm(data=data)
        self.assertTrue(form.is_valid())

    def test_empty_name_rejected(self):
        """Test that empty name is rejected."""
        data = {
            'name': '',
            'email': 'test@example.com',
            'subject': 'general',
            'message': 'This is a test message.',
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_short_name_rejected(self):
        """Test that name with less than 2 characters is rejected."""
        data = {
            'name': 'A',
            'email': 'test@example.com',
            'subject': 'general',
            'message': 'This is a test message.',
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_invalid_email_rejected(self):
        """Test that invalid email is rejected."""
        data = {
            'name': 'Test User',
            'email': 'not-an-email',
            'subject': 'general',
            'message': 'This is a test message.',
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_empty_email_rejected(self):
        """Test that empty email is rejected."""
        data = {
            'name': 'Test User',
            'email': '',
            'subject': 'general',
            'message': 'This is a test message.',
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_short_message_rejected(self):
        """Test that message with less than 10 characters is rejected."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'general',
            'message': 'Short',
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_empty_message_rejected(self):
        """Test that empty message is rejected."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'general',
            'message': '',
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_invalid_subject_rejected(self):
        """Test that invalid subject choice is rejected."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'invalid_subject',
            'message': 'This is a test message.',
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('subject', form.errors)

    def test_honeypot_detected(self):
        """Test that honeypot field marks submission as spam."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'general',
            'message': 'This is a test message.',
            'website': 'http://spam.com',  # Honeypot filled
        }
        form = ContactForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data.get('is_spam'))

    def test_honeypot_empty_not_spam(self):
        """Test that empty honeypot field is not marked as spam."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'general',
            'message': 'This is a test message.',
            'website': '',  # Honeypot empty
        }
        form = ContactForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data.get('is_spam'))


class ContactPageTest(SimpleTestCase):
    """Test contact page rendering."""

    def setUp(self):
        self.client = Client()

    def test_contact_page_loads(self):
        """Test that contact page loads successfully."""
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)

    def test_contact_page_has_form(self):
        """Test that contact page contains the form."""
        response = self.client.get(reverse('core:contact'))
        self.assertContains(response, 'contact-form')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contact_page_has_title(self):
        """Test that contact page has the correct title."""
        response = self.client.get(reverse('core:contact'))
        self.assertContains(response, 'Get In Touch')


class ContactSubmitViewTest(SimpleTestCase):
    """Test contact form submission endpoint."""

    def setUp(self):
        self.client = Client()
        self.submit_url = reverse('core:contact_submit')

    def test_valid_submission(self):
        """Test successful form submission."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'general',
            'message': 'This is a test message for the contact form.',
        }
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['success'])
        self.assertIn('Thank you', result['message'])

    def test_empty_name_rejected(self):
        """Test that submission with empty name is rejected."""
        data = {
            'name': '',
            'email': 'test@example.com',
            'subject': 'general',
            'message': 'This is a test message.',
        }
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertFalse(result['success'])

    def test_invalid_email_rejected(self):
        """Test that submission with invalid email is rejected."""
        data = {
            'name': 'Test User',
            'email': 'not-an-email',
            'subject': 'general',
            'message': 'This is a test message.',
        }
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertFalse(result['success'])

    def test_short_message_rejected(self):
        """Test that submission with short message is rejected."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'general',
            'message': 'Short',
        }
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertFalse(result['success'])

    def test_honeypot_silently_succeeds(self):
        """Test that spam submissions appear successful but don't process."""
        data = {
            'name': 'Spam Bot',
            'email': 'spam@example.com',
            'subject': 'general',
            'message': 'Buy cheap products at spam.com now!',
            'website': 'http://spam.com',  # Honeypot filled
        }
        response = self.client.post(
            self.submit_url,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['success'])  # Appears successful to bot

    def test_invalid_json_rejected(self):
        """Test that invalid JSON is rejected."""
        response = self.client.post(
            self.submit_url,
            data='not valid json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertFalse(result['success'])
        self.assertIn('Invalid request format', result['message'])

    def test_get_method_not_allowed(self):
        """Test that GET requests are not allowed."""
        response = self.client.get(self.submit_url)
        self.assertEqual(response.status_code, 405)

    def test_all_subject_choices_valid(self):
        """Test that all defined subject choices are accepted."""
        subject_choices = ['general', 'classes', 'private', 'events', 'other']
        for subject in subject_choices:
            data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': subject,
                'message': 'This is a test message for the form.',
            }
            response = self.client.post(
                self.submit_url,
                data=json.dumps(data),
                content_type='application/json',
            )
            self.assertEqual(
                response.status_code, 200,
                f'Subject "{subject}" should be valid'
            )
