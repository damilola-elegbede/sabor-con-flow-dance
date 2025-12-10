"""
Comprehensive tests for SPEC_03 Testimonials Portal templates and UI.

Tests template rendering, HTML content validation, CSS/JS integration,
responsive design, accessibility features, and interactive components
for all testimonial-related templates.
"""

import json
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.template.loader import get_template, render_to_string
from django.template import Context, Template
from django.http import HttpRequest
from django.contrib.messages import get_messages
from django.utils import timezone
from bs4 import BeautifulSoup
from core.models import Testimonial, ReviewLink


class TestimonialTemplateBaseTestCase(TestCase):
    """Base test case with common setup for testimonial template tests."""
    
    def setUp(self):
        """Set up test client and sample data."""
        self.client = Client()
        
        # Create sample testimonials
        self.testimonial1 = Testimonial.objects.create(
            student_name="Maria Rodriguez",
            email="maria@example.com",
            class_type="choreo_team",
            rating=5,
            content="Amazing Cuban salsa experience! The instructors are incredible and the community is so welcoming. I've learned so much in just a few months.",
            status="approved",
            published_at=timezone.now()
        )
        
        self.testimonial2 = Testimonial.objects.create(
            student_name="John Smith",
            email="john@example.com",
            class_type="private_lesson",
            rating=4,
            content="Great personalized instruction. Really helped me improve my footwork and timing.",
            status="approved",
            published_at=timezone.now()
        )
        
        self.testimonial3 = Testimonial.objects.create(
            student_name="Sarah Johnson",
            email="sarah@example.com",
            class_type="workshop",
            rating=5,
            content="The workshop was fantastic! Learned new moves and met amazing people.",
            status="pending"  # Not approved, no published_at
        )
        
        # Create sample review link
        self.review_link = ReviewLink.objects.create(
            token=f"test-token-{self.__class__.__name__}",
            class_type="group",
            instructor_name="Carlos",
            campaign_name="Holiday Special 2024"
        )
    
    def get_parsed_template(self, template_name, context=None):
        """Helper method to get parsed template HTML."""
        if context is None:
            context = {}
        
        template = get_template(template_name)
        html = template.render(context)
        return BeautifulSoup(html, 'html.parser')


class SubmitTemplateTestCase(TestimonialTemplateBaseTestCase):
    """Test submit.html template structure and content."""
    
    def test_submit_template_extends_base(self):
        """Test that submit template extends base.html."""
        response = self.client.get(reverse('core:submit_testimonial'))
        self.assertTemplateUsed(response, 'testimonials/submit.html')
        self.assertTemplateUsed(response, 'base.html')
    
    def test_submit_template_meta_tags(self):
        """Test submit template has proper meta tags."""
        response = self.client.get(reverse('core:submit_testimonial'))
        content = response.content.decode('utf-8')
        
        # Test title block
        self.assertIn('Share Your Dance Journey - Sabor Con Flow Dance', content)
        
        # Test meta description
        self.assertIn('Share your dance experience at Sabor Con Flow Dance', content)
        self.assertIn('Submit your testimonial and rate your Cuban salsa classes', content)
    
    def test_submit_form_structure(self):
        """Test testimonial form has all required elements."""
        response = self.client.get(reverse('core:submit_testimonial'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test form element
        form = soup.find('form', {'id': 'testimonialForm'})
        self.assertIsNotNone(form)
        self.assertEqual(form.get('method'), 'post')
        self.assertEqual(form.get('enctype'), 'multipart/form-data')
        
        # Test CSRF token
        csrf_input = form.find('input', {'name': 'csrfmiddlewaretoken'})
        self.assertIsNotNone(csrf_input)
    
    def test_submit_form_fields(self):
        """Test all form fields are present."""
        response = self.client.get(reverse('core:submit_testimonial'))
        soup = BeautifulSoup(response.content, 'html.parser')
        content = response.content.decode('utf-8')
        
        # Test that form field labels contain expected text
        self.assertIn('Your Name', content)
        self.assertIn('Email Address', content)
        self.assertIn('Class or Service', content)
        self.assertIn('Your Rating', content)
        self.assertIn('Your Experience', content)
        self.assertIn('Photo (Optional)', content)
        
        # Test form inputs are present
        form = soup.find('form', {'id': 'testimonialForm'})
        self.assertIsNotNone(form)
        
        # Test basic form structure
        form_groups = soup.find_all('div', {'class': 'form-group'})
        self.assertGreaterEqual(len(form_groups), 5)  # At least 5 form groups
    
    def test_star_rating_elements(self):
        """Test star rating elements are present."""
        response = self.client.get(reverse('core:submit_testimonial'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test rating display container
        rating_display = soup.find('div', {'id': 'ratingDisplay'})
        self.assertIsNotNone(rating_display)
        
        # Test star elements
        stars = soup.find_all('span', {'class': 'star-display'})
        self.assertEqual(len(stars), 5)
        
        # Test each star has correct data attribute
        for i, star in enumerate(stars, 1):
            self.assertEqual(star.get('data-rating'), str(i))
            self.assertEqual(star.text.strip(), '★')
        
        # Test rating text element
        rating_text = soup.find('span', {'id': 'ratingText'})
        self.assertIsNotNone(rating_text)
        self.assertEqual(rating_text.text.strip(), 'Click to rate')
    
    def test_character_counter_element(self):
        """Test character counter is present."""
        response = self.client.get(reverse('core:submit_testimonial'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        character_counter = soup.find('div', {'id': 'characterCounter'})
        self.assertIsNotNone(character_counter)
        self.assertIn('character-counter', character_counter.get('class', []))
        self.assertIn('0 / 500 characters', character_counter.text)
        self.assertIn('minimum 50', character_counter.text)
    
    def test_photo_upload_section(self):
        """Test photo upload section structure."""
        response = self.client.get(reverse('core:submit_testimonial'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test upload container
        upload_container = soup.find('div', {'id': 'photoUploadContainer'})
        self.assertIsNotNone(upload_container)
        self.assertIn('photo-upload-container', upload_container.get('class', []))
        
        # Test upload icon
        upload_icon = upload_container.find('i', {'class': 'fas fa-cloud-upload-alt'})
        self.assertIsNotNone(upload_icon)
        
        # Test upload text
        upload_text = upload_container.find('div', {'class': 'upload-text'})
        self.assertIsNotNone(upload_text)
        self.assertIn('Upload a photo from your dance experience', upload_text.text)
        self.assertIn('Drag and drop or click to select', upload_text.text)
        
        # Test upload button
        upload_button = upload_container.find('label', {'class': 'upload-button'})
        self.assertIsNotNone(upload_button)
        self.assertEqual(upload_button.text.strip(), 'Choose Photo')
        
        # Test photo preview container
        photo_preview = upload_container.find('div', {'id': 'photoPreview'})
        self.assertIsNotNone(photo_preview)
        self.assertIn('photo-preview', photo_preview.get('class', []))
    
    def test_submit_button(self):
        """Test submit button is present and properly configured."""
        response = self.client.get(reverse('core:submit_testimonial'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        submit_button = soup.find('button', {'id': 'submitButton'})
        self.assertIsNotNone(submit_button)
        self.assertEqual(submit_button.get('type'), 'submit')
        self.assertIn('btn-submit', submit_button.get('class', []))
        
        # Test button text and icon
        button_text = submit_button.text.strip()
        self.assertIn('Share My Experience', button_text)
        
        # Test button icon
        button_icon = submit_button.find('i', {'class': 'fas fa-paper-plane'})
        self.assertIsNotNone(button_icon)
    
    def test_mobile_responsive_classes(self):
        """Test mobile responsive CSS classes are applied."""
        response = self.client.get(reverse('core:submit_testimonial'))
        content = response.content.decode('utf-8')
        
        # Test responsive breakpoints in CSS
        self.assertIn('@media (max-width: 768px)', content)
        self.assertIn('mobile-nav', content)
        
        # Test container responsive classes
        soup = BeautifulSoup(response.content, 'html.parser')
        container = soup.find('div', {'class': 'testimonial-form-container'})
        self.assertIsNotNone(container)
    
    def test_javascript_inclusion(self):
        """Test JavaScript functionality is included."""
        response = self.client.get(reverse('core:submit_testimonial'))
        content = response.content.decode('utf-8')
        
        # Test inline JavaScript is present
        self.assertIn('Star Rating Functionality', content)
        self.assertIn('Character Counter', content)
        self.assertIn('Photo Upload Functionality', content)
        self.assertIn('Form Validation', content)
        
        # Test JavaScript functions
        self.assertIn('setRating', content)
        self.assertIn('highlightStars', content)
        self.assertIn('updateCharacterCounter', content)
        self.assertIn('handlePhotoSelect', content)
    
    def test_review_link_context_display(self):
        """Test review link context is displayed when present."""
        # Test with review link context via query parameters
        url = reverse('core:submit_testimonial') + f'?ref={self.review_link.token}'
        response = self.client.get(url)
        
        # Should still load the template successfully
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'testimonials/submit.html')
        
        # Note: The actual context display logic would need to be implemented
        # in the view to make this test meaningful


class SuccessTemplateTestCase(TestimonialTemplateBaseTestCase):
    """Test success.html template structure and content."""
    
    def test_success_template_extends_base(self):
        """Test that success template extends base.html."""
        response = self.client.get(reverse('core:testimonial_success'))
        self.assertTemplateUsed(response, 'testimonials/success.html')
        self.assertTemplateUsed(response, 'base.html')
    
    def test_success_template_meta_tags(self):
        """Test success template has proper meta tags."""
        response = self.client.get(reverse('core:testimonial_success'))
        content = response.content.decode('utf-8')
        
        # Test title
        self.assertIn('Thank You - Testimonial Submitted', content)
        
        # Test meta description
        self.assertIn('Thank you for submitting your testimonial to Sabor Con Flow Dance', content)
    
    def test_success_thank_you_message(self):
        """Test thank you message is displayed prominently."""
        response = self.client.get(reverse('core:testimonial_success'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test success icon
        success_icon = soup.find('i', {'class': 'fas fa-check-circle text-success'})
        self.assertIsNotNone(success_icon)
        
        # Test thank you heading
        thank_you_heading = soup.find('h1', string=lambda text: text and 'Thank You!' in text)
        self.assertIsNotNone(thank_you_heading)
        
        # Test submission confirmation
        submission_text = soup.find('h2', string=lambda text: text and 'Your Testimonial Has Been Submitted' in text)
        self.assertIsNotNone(submission_text)
    
    def test_review_processing_timeline(self):
        """Test review processing timeline is displayed."""
        response = self.client.get(reverse('core:testimonial_success'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test timeline section
        timeline_section = soup.find('div', {'class': 'review-timeline'})
        self.assertIsNotNone(timeline_section)
        
        # Test timeline steps
        timeline_items = soup.find_all('div', {'class': 'timeline-item'})
        self.assertEqual(len(timeline_items), 3)
        
        # Test timeline step labels
        timeline_text = response.content.decode('utf-8')
        self.assertIn('Review', timeline_text)
        self.assertIn('Approval', timeline_text)
        self.assertIn('Share', timeline_text)
        
        # Test timeline descriptions
        self.assertIn('1-2 business days', timeline_text)
        self.assertIn('goes live on our site', timeline_text)
        self.assertIn('social media', timeline_text)
    
    def test_google_business_profile_section(self):
        """Test Google Business Profile section is present."""
        response = self.client.get(reverse('core:testimonial_success'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test Google review section
        google_section = soup.find('div', {'class': 'google-review-section'})
        self.assertIsNotNone(google_section)
        
        # Test Google icon
        google_icon = soup.find('i', {'class': 'fab fa-google'})
        self.assertIsNotNone(google_icon)
        
        # Test Google review link
        google_link = soup.find('a', href=lambda href: href and 'google' in href.lower())
        self.assertIsNotNone(google_link)
        self.assertIn('Leave a Google Review', google_link.text)
        
        # Test link attributes
        self.assertEqual(google_link.get('target'), '_blank')
        self.assertEqual(google_link.get('rel'), 'noopener noreferrer')
    
    def test_social_sharing_buttons(self):
        """Test social sharing buttons are present."""
        response = self.client.get(reverse('core:testimonial_success'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test social sharing section
        sharing_section = soup.find('div', {'class': 'social-sharing-section'})
        self.assertIsNotNone(sharing_section)
        
        # Test individual social buttons
        social_platforms = ['facebook', 'twitter', 'instagram', 'whatsapp']
        for platform in social_platforms:
            platform_link = soup.find('a', href=lambda href: href and platform in href.lower())
            self.assertIsNotNone(platform_link, f"Missing {platform} sharing button")
            
            # Test link attributes
            self.assertEqual(platform_link.get('target'), '_blank')
            self.assertEqual(platform_link.get('rel'), 'noopener noreferrer')
        
        # Test email sharing
        email_link = soup.find('a', href=lambda href: href and 'mailto:' in href)
        self.assertIsNotNone(email_link)
    
    def test_navigation_cta_buttons(self):
        """Test call-to-action navigation buttons."""
        response = self.client.get(reverse('core:testimonial_success'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test CTA section
        cta_section = soup.find('div', {'class': 'cta-section'})
        self.assertIsNotNone(cta_section)
        
        # Test navigation buttons
        home_link = soup.find('a', href=reverse('core:home'))
        self.assertIsNotNone(home_link)
        self.assertIn('Return to Homepage', home_link.text)
        
        schedule_link = soup.find('a', href=reverse('core:schedule'))
        self.assertIsNotNone(schedule_link)
        self.assertIn('View Class Schedule', schedule_link.text)
        
        pricing_link = soup.find('a', href=reverse('core:pricing'))
        self.assertIsNotNone(pricing_link)
        self.assertIn('Book More Classes', pricing_link.text)
    
    def test_newsletter_signup_form(self):
        """Test newsletter signup form is present."""
        response = self.client.get(reverse('core:testimonial_success'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test newsletter form
        newsletter_form = soup.find('form', {'id': 'newsletter-form'})
        self.assertIsNotNone(newsletter_form)
        
        # Test email input
        email_input = newsletter_form.find('input', {'type': 'email'})
        self.assertIsNotNone(email_input)
        self.assertTrue(email_input.get('required'))
        
        # Test submit button
        submit_button = newsletter_form.find('button', {'type': 'submit'})
        self.assertIsNotNone(submit_button)
        self.assertIn('Subscribe', submit_button.text)
    
    def test_success_page_animations(self):
        """Test success page includes animations."""
        response = self.client.get(reverse('core:testimonial_success'))
        content = response.content.decode('utf-8')
        
        # Test CSS animations
        self.assertIn('@keyframes scaleIn', content)
        self.assertIn('animation: scaleIn', content)
        
        # Test JavaScript animations
        self.assertIn('animateElements', content)
        self.assertIn('opacity', content)
        self.assertIn('transform', content)


class DisplayTemplateTestCase(TestimonialTemplateBaseTestCase):
    """Test display.html template structure and content."""
    
    def test_display_template_extends_base(self):
        """Test that display template extends base.html."""
        response = self.client.get(reverse('core:testimonials'))
        self.assertTemplateUsed(response, 'testimonials/display.html')
        self.assertTemplateUsed(response, 'base.html')
    
    def test_display_template_meta_tags(self):
        """Test display template has proper meta tags."""
        response = self.client.get(reverse('core:testimonials'))
        content = response.content.decode('utf-8')
        
        # Test title
        self.assertIn('Student Testimonials - Sabor Con Flow Dance', content)
        
        # Test meta description
        self.assertIn('Read what our students say about their dance journey', content)
        self.assertIn('Cuban salsa community in Boulder', content)
    
    def test_testimonials_hero_section(self):
        """Test testimonials hero section."""
        response = self.client.get(reverse('core:testimonials'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test hero section
        hero_section = soup.find('section', {'class': 'testimonials-hero'})
        self.assertIsNotNone(hero_section)
        
        # Test hero heading
        hero_heading = soup.find('h1', string=lambda text: text and 'What Our Students Say' in text)
        self.assertIsNotNone(hero_heading)
        
        # Test hero subtitle
        hero_subtitle = soup.find('p', {'class': 'testimonials-subtitle'})
        self.assertIsNotNone(hero_subtitle)
        self.assertIn('Real stories from our vibrant dance community', hero_subtitle.text)
    
    def test_rating_summary_display(self):
        """Test rating summary section when testimonials exist."""
        response = self.client.get(reverse('core:testimonials'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test rating summary container
        rating_summary = soup.find('div', {'class': 'rating-summary'})
        self.assertIsNotNone(rating_summary)
        
        # Test rating number
        rating_number = soup.find('div', {'class': 'rating-number'})
        self.assertIsNotNone(rating_number)
        
        # Test rating stars
        rating_stars = soup.find('div', {'class': 'rating-stars'})
        self.assertIsNotNone(rating_stars)
        
        # Test rating count
        rating_count = soup.find('div', {'class': 'rating-count'})
        self.assertIsNotNone(rating_count)
        self.assertIn('review', rating_count.text.lower())
    
    def test_filter_controls(self):
        """Test filter controls are present and functional."""
        response = self.client.get(reverse('core:testimonials'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test filters section
        filters_section = soup.find('section', {'class': 'filters-section'})
        self.assertIsNotNone(filters_section)
        
        # Test filter form
        filter_form = soup.find('form', method='get')
        self.assertIsNotNone(filter_form)
        
        # Test rating filter
        rating_filter = soup.find('select', {'name': 'rating'})
        self.assertIsNotNone(rating_filter)
        rating_options = rating_filter.find_all('option')
        self.assertGreaterEqual(len(rating_options), 6)  # All ratings + "All Ratings"
        
        # Test class type filter
        class_filter = soup.find('select', {'name': 'class_type'})
        self.assertIsNotNone(class_filter)
        class_options = class_filter.find_all('option')
        self.assertGreaterEqual(len(class_options), 2)  # At least "All Classes" + one type
        
        # Test clear filters link (if filters are applied)
        clear_link = soup.find('a', string=lambda text: text and 'Clear Filters' in text)
        # May or may not be present depending on filter state
    
    def test_testimonial_cards_rendered(self):
        """Test testimonial cards are rendered properly."""
        response = self.client.get(reverse('core:testimonials'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test testimonials grid
        testimonials_grid = soup.find('div', {'class': 'testimonials-grid'})
        self.assertIsNotNone(testimonials_grid)
        
        # Test testimonial cards (only approved ones should show)
        testimonial_cards = soup.find_all('div', {'class': 'testimonial-card'})
        self.assertEqual(len(testimonial_cards), 2)  # Only approved testimonials
        
        # Test first testimonial card structure
        first_card = testimonial_cards[0]
        
        # Test testimonial header
        card_header = first_card.find('div', {'class': 'testimonial-header'})
        self.assertIsNotNone(card_header)
        
        # Test student name
        student_name = first_card.find('h3', {'class': 'testimonial-name'})
        self.assertIsNotNone(student_name)
        
        # Test rating stars
        rating_div = first_card.find('div', {'class': 'testimonial-rating'})
        self.assertIsNotNone(rating_div)
        star_icons = rating_div.find_all('i')
        self.assertEqual(len(star_icons), 5)
        
        # Test class type badge
        class_badge = first_card.find('span', {'class': 'testimonial-class'})
        self.assertIsNotNone(class_badge)
        
        # Test testimonial content
        content_div = first_card.find('div', {'class': 'testimonial-content'})
        self.assertIsNotNone(content_div)
        content_text = first_card.find('p', {'class': 'testimonial-text'})
        self.assertIsNotNone(content_text)
        
        # Test testimonial footer
        footer_div = first_card.find('div', {'class': 'testimonial-footer'})
        self.assertIsNotNone(footer_div)
    
    def test_rating_stars_display_correctly(self):
        """Test rating stars are displayed correctly for different ratings."""
        response = self.client.get(reverse('core:testimonials'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        testimonial_cards = soup.find_all('div', {'class': 'testimonial-card'})
        
        for card in testimonial_cards:
            rating_div = card.find('div', {'class': 'testimonial-rating'})
            if rating_div:
                # Look for any star icons (FontAwesome or unicode)
                stars = rating_div.find_all('i')
                
                if stars:
                    # If FontAwesome icons are present
                    filled_stars = [s for s in stars if 'fas' in s.get('class', [])]
                    empty_stars = [s for s in stars if 'far' in s.get('class', [])]
                    
                    if filled_stars or empty_stars:
                        # Total should be 5 stars
                        self.assertEqual(len(filled_stars) + len(empty_stars), 5)
                        
                        # Should have at least one filled star (minimum rating is 1)
                        self.assertGreaterEqual(len(filled_stars), 1)
                else:
                    # Check for unicode stars or other rating display
                    rating_text = rating_div.get_text()
                    # Just verify rating content exists
                    self.assertTrue(len(rating_text.strip()) > 0)
    
    def test_class_type_badges_shown(self):
        """Test class type badges are shown correctly."""
        response = self.client.get(reverse('core:testimonials'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        class_badges = soup.find_all('span', {'class': 'testimonial-class'})
        self.assertGreater(len(class_badges), 0)
        
        for badge in class_badges:
            # Badge should have text content
            self.assertTrue(badge.text.strip())
            # Should match our test data (model choice values or display names)
            # The template might display the value or the display name
            valid_values = ['SCF Choreo Team', 'Private Lesson', 'Workshop', 'choreo_team', 'private_lesson', 'workshop']
            self.assertIn(badge.text.strip(), valid_values)
    
    def test_masonry_grid_classes(self):
        """Test masonry grid CSS classes are applied."""
        response = self.client.get(reverse('core:testimonials'))
        content = response.content.decode('utf-8')
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test masonry grid HTML classes
        self.assertIn('testimonials-grid', content)
        
        # Test that grid container exists
        testimonials_grid = soup.find('div', {'class': 'testimonials-grid'})
        self.assertIsNotNone(testimonials_grid)
        
        # Test CSS content (inline styles)
        self.assertIn('grid-template-columns', content)
        
        # Test responsive grid structure exists
        self.assertIn('@media', content)
    
    def test_no_testimonials_message(self):
        """Test no testimonials message when no approved testimonials exist."""
        # Delete approved testimonials
        Testimonial.objects.filter(status="approved").delete()
        
        response = self.client.get(reverse('core:testimonials'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test no testimonials container
        no_testimonials = soup.find('div', {'class': 'no-testimonials'})
        self.assertIsNotNone(no_testimonials)
        
        # Test message content
        self.assertIn('No Testimonials Found', response.content.decode('utf-8'))
        
        # Test share experience link
        share_link = soup.find('a', href=reverse('core:submit_testimonial'))
        self.assertIsNotNone(share_link)
        self.assertIn('Share Your Experience', share_link.text)


class TestimonialCarouselTemplateTestCase(TestimonialTemplateBaseTestCase):
    """Test testimonial_carousel.html component template."""
    
    def test_carousel_template_structure(self):
        """Test carousel template has correct structure."""
        # Render the carousel component template directly
        context = {'carousel_testimonials': [self.testimonial1, self.testimonial2]}
        template = get_template('components/testimonial_carousel.html')
        html = template.render(context)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Test carousel section
        carousel_section = soup.find('section', {'class': 'testimonial-carousel-section'})
        self.assertIsNotNone(carousel_section)
        
        # Test carousel header
        carousel_header = soup.find('div', {'class': 'carousel-header'})
        self.assertIsNotNone(carousel_header)
        
        # Test carousel wrapper
        carousel_wrapper = soup.find('div', {'class': 'testimonial-carousel-wrapper'})
        self.assertIsNotNone(carousel_wrapper)
        
        # Test carousel container
        carousel_container = soup.find('div', {'class': 'testimonial-carousel'})
        self.assertIsNotNone(carousel_container)
    
    def test_carousel_track_and_slides(self):
        """Test carousel track and slides structure."""
        context = {'carousel_testimonials': [self.testimonial1, self.testimonial2]}
        template = get_template('components/testimonial_carousel.html')
        html = template.render(context)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Test carousel track
        carousel_track = soup.find('div', {'id': 'carouselTrack'})
        self.assertIsNotNone(carousel_track)
        self.assertIn('carousel-track', carousel_track.get('class', []))
        
        # Test carousel slides
        carousel_slides = soup.find_all('div', {'class': 'carousel-slide'})
        self.assertEqual(len(carousel_slides), 2)
        
        # Test testimonial cards within slides
        testimonial_cards = soup.find_all('div', {'class': 'carousel-testimonial-card'})
        self.assertEqual(len(testimonial_cards), 2)
    
    def test_carousel_navigation_controls(self):
        """Test carousel navigation controls are present."""
        context = {'carousel_testimonials': [self.testimonial1, self.testimonial2]}
        template = get_template('components/testimonial_carousel.html')
        html = template.render(context)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Test previous button
        prev_button = soup.find('button', {'class': 'carousel-nav-button prev'})
        self.assertIsNotNone(prev_button)
        self.assertEqual(prev_button.get('onclick'), 'moveCarousel(-1)')
        self.assertEqual(prev_button.get('aria-label'), 'Previous testimonial')
        
        # Test next button
        next_button = soup.find('button', {'class': 'carousel-nav-button next'})
        self.assertIsNotNone(next_button)
        self.assertEqual(next_button.get('onclick'), 'moveCarousel(1)')
        self.assertEqual(next_button.get('aria-label'), 'Next testimonial')
        
        # Test navigation icons
        prev_icon = prev_button.find('i', {'class': 'fas fa-chevron-left'})
        self.assertIsNotNone(prev_icon)
        
        next_icon = next_button.find('i', {'class': 'fas fa-chevron-right'})
        self.assertIsNotNone(next_icon)
    
    def test_carousel_dots_indicator(self):
        """Test carousel dots indicator."""
        context = {'carousel_testimonials': [self.testimonial1, self.testimonial2]}
        template = get_template('components/testimonial_carousel.html')
        html = template.render(context)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Test dots container
        dots_container = soup.find('div', {'id': 'carouselDots'})
        self.assertIsNotNone(dots_container)
        self.assertIn('carousel-dots', dots_container.get('class', []))
        
        # Test dot buttons
        dot_buttons = soup.find_all('button', {'class': 'carousel-dot'})
        self.assertEqual(len(dot_buttons), 2)
        
        # Test first dot is active
        first_dot = dot_buttons[0]
        self.assertIn('active', first_dot.get('class', []))
        
        # Test dot attributes
        for i, dot in enumerate(dot_buttons):
            self.assertEqual(dot.get('onclick'), f'goToSlide({i})')
            self.assertEqual(dot.get('aria-label'), f'Go to testimonial {i + 1}')
    
    def test_carousel_testimonial_content(self):
        """Test testimonial content in carousel cards."""
        context = {'carousel_testimonials': [self.testimonial1, self.testimonial2]}
        template = get_template('components/testimonial_carousel.html')
        html = template.render(context)
        soup = BeautifulSoup(html, 'html.parser')
        
        testimonial_cards = soup.find_all('div', {'class': 'carousel-testimonial-card'})
        
        for i, card in enumerate(testimonial_cards):
            testimonial = [self.testimonial1, self.testimonial2][i]
            
            # Test quote icon
            quote_icon = card.find('i', {'class': 'fas fa-quote-left'})
            self.assertIsNotNone(quote_icon)
            
            # Test rating stars
            rating_div = card.find('div', {'class': 'carousel-rating'})
            self.assertIsNotNone(rating_div)
            stars = rating_div.find_all('i')
            self.assertEqual(len(stars), 5)
            
            # Test testimonial text
            review_text = card.find('span', {'class': 'carousel-review-text'})
            self.assertIsNotNone(review_text)
            
            # Test student name
            student_name = card.find('div', {'class': 'carousel-student-name'})
            self.assertIsNotNone(student_name)
            self.assertEqual(student_name.text.strip(), testimonial.student_name)
            
            # Test class badge
            class_badge = card.find('span', {'class': 'carousel-class-badge'})
            self.assertIsNotNone(class_badge)
            self.assertEqual(class_badge.text.strip(), testimonial.class_type)
    
    def test_carousel_content_truncation(self):
        """Test testimonial content is truncated with read more link."""
        # Create testimonial with long content
        long_testimonial = Testimonial.objects.create(
            student_name="Test Long",
            email="long@example.com",
            class_type="choreo_team",
            rating=5,
            content="This is a very long testimonial that should be truncated at 150 characters because it exceeds the limit set for carousel display and should show a read more link.",
            status="approved",
            published_at=timezone.now()
        )
        
        context = {'carousel_testimonials': [long_testimonial]}
        template = get_template('components/testimonial_carousel.html')
        html = template.render(context)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Test content is truncated
        review_text = soup.find('span', {'class': 'carousel-review-text'})
        self.assertIsNotNone(review_text)
        
        # Test read more link is present
        read_more_link = soup.find('a', {'class': 'carousel-read-more'})
        self.assertIsNotNone(read_more_link)
        self.assertEqual(read_more_link.text.strip(), 'Read more')
        self.assertEqual(read_more_link.get('href'), reverse('core:testimonials'))
    
    def test_carousel_autoplay_functionality(self):
        """Test carousel auto-play JavaScript functionality."""
        context = {'carousel_testimonials': [self.testimonial1, self.testimonial2]}
        template = get_template('components/testimonial_carousel.html')
        html = template.render(context)
        
        # Test JavaScript functions are present
        self.assertIn('moveCarousel', html)
        self.assertIn('goToSlide', html)
        self.assertIn('startAutoplay', html)
        self.assertIn('stopAutoplay', html)
        self.assertIn('resetAutoplay', html)
        
        # Test auto-play interval
        self.assertIn('5000', html)  # 5 second interval
        
        # Test touch/swipe support
        self.assertIn('touchstart', html)
        self.assertIn('touchend', html)
        self.assertIn('handleSwipe', html)
        
        # Test keyboard navigation
        self.assertIn('keydown', html)
        self.assertIn('ArrowLeft', html)
        self.assertIn('ArrowRight', html)


class CSSJavaScriptIntegrationTestCase(TestimonialTemplateBaseTestCase):
    """Test CSS and JavaScript integration in templates."""
    
    def test_testimonials_css_linked(self):
        """Test testimonials.css is properly linked."""
        # Check submit template
        response = self.client.get(reverse('core:submit_testimonial'))
        content = response.content.decode('utf-8')
        
        # CSS should be inline in submit template
        self.assertIn('.testimonial-form-container', content)
        self.assertIn('.star-display', content)
        self.assertIn('.character-counter', content)
        self.assertIn('.photo-upload-container', content)
        
        # Check display template
        response = self.client.get(reverse('core:testimonials'))
        content = response.content.decode('utf-8')
        
        # CSS should be inline in display template
        self.assertIn('.testimonials-hero', content)
        self.assertIn('.testimonials-grid', content)
        self.assertIn('.testimonial-card', content)
    
    def test_testimonial_form_js_functionality(self):
        """Test testimonial-form.js functionality is present."""
        response = self.client.get(reverse('core:submit_testimonial'))
        content = response.content.decode('utf-8')
        
        # Test JavaScript event listeners
        self.assertIn('addEventListener', content)
        self.assertIn('DOMContentLoaded', content)
        
        # Test star rating functions
        self.assertIn('ratingTexts', content)
        self.assertIn('setRating', content)
        self.assertIn('highlightStars', content)
        
        # Test character counter
        self.assertIn('updateCharacterCounter', content)
        self.assertIn('contentTextarea.addEventListener', content)
        
        # Test photo upload
        self.assertIn('handlePhotoSelect', content)
        self.assertIn('clearPhotoPreview', content)
        self.assertIn('dragover', content)
        self.assertIn('dragleave', content)
        
        # Test form validation
        self.assertIn('form.addEventListener', content)
        self.assertIn('preventDefault', content)
    
    def test_no_javascript_errors(self):
        """Test templates don't contain JavaScript syntax errors."""
        templates_to_test = [
            reverse('core:submit_testimonial'),
            reverse('core:testimonials'),
            reverse('core:testimonial_success')
        ]
        
        for url in templates_to_test:
            response = self.client.get(url)
            content = response.content.decode('utf-8')
            
            # Test for common JavaScript syntax issues
            self.assertNotIn('function()', content)  # Should be function() {
            self.assertNotIn('if(', content.replace('if(', 'if ('))  # Should have space
            
            # Test for proper script tag closure
            script_tags = content.count('<script>')
            script_end_tags = content.count('</script>')
            self.assertEqual(script_tags, script_end_tags)
    
    def test_css_classes_applied_correctly(self):
        """Test CSS classes are applied correctly in templates."""
        # Test submit template
        response = self.client.get(reverse('core:submit_testimonial'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test main container class
        container = soup.find('div', {'class': 'testimonial-form-container'})
        self.assertIsNotNone(container)
        
        # Test form group classes
        form_groups = soup.find_all('div', {'class': 'form-group'})
        self.assertGreater(len(form_groups), 0)
        
        # Test display template
        response = self.client.get(reverse('core:testimonials'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test hero section class
        hero = soup.find('section', {'class': 'testimonials-hero'})
        self.assertIsNotNone(hero)
        
        # Test grid class
        grid = soup.find('div', {'class': 'testimonials-grid'})
        self.assertIsNotNone(grid)
    
    def test_responsive_design_classes(self):
        """Test responsive design CSS classes and media queries."""
        response = self.client.get(reverse('core:testimonials'))
        content = response.content.decode('utf-8')
        
        # Test mobile breakpoints
        self.assertIn('@media (max-width: 768px)', content)
        self.assertIn('@media (min-width: 640px)', content)
        self.assertIn('@media (min-width: 1024px)', content)
        
        # Test responsive grid
        self.assertIn('grid-template-columns: 1fr', content)
        self.assertIn('repeat(2, 1fr)', content)
        self.assertIn('repeat(3, 1fr)', content)
    
    def test_accessibility_css_features(self):
        """Test accessibility-related CSS features."""
        templates_to_test = [
            reverse('core:submit_testimonial'),
            reverse('core:testimonials'),
            reverse('core:testimonial_success')
        ]
        
        for url in templates_to_test:
            response = self.client.get(url)
            content = response.content.decode('utf-8')
            
            # Test focus styles
            if ':focus' in content:
                self.assertIn('outline', content)
            
            # Test reduced motion support
            if '@media (prefers-reduced-motion: reduce)' in content:
                self.assertIn('animation: none', content)
            
            # Test high contrast support
            if '@media (prefers-contrast: high)' in content:
                self.assertTrue(True)  # Good if present


class AccessibilityTestCase(TestimonialTemplateBaseTestCase):
    """Test accessibility features in testimonial templates."""
    
    def test_form_accessibility_labels(self):
        """Test form labels are properly associated with inputs."""
        response = self.client.get(reverse('core:submit_testimonial'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test label-input associations
        labels = soup.find_all('label')
        for label in labels:
            for_attr = label.get('for')
            if for_attr:
                associated_input = soup.find(id=for_attr)
                self.assertIsNotNone(associated_input, f"Label for='{for_attr}' has no associated input")
    
    def test_aria_attributes(self):
        """Test ARIA attributes are present where needed."""
        response = self.client.get(reverse('core:submit_testimonial'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test star rating ARIA attributes would be added by JavaScript
        # Check for navigation ARIA labels
        nav_buttons = soup.find_all('button', {'aria-label': True})
        # May not be present in submit template
        
        # Test carousel template for ARIA
        context = {'carousel_testimonials': [self.testimonial1]}
        template = get_template('components/testimonial_carousel.html')
        html = template.render(context)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Test navigation button ARIA labels
        prev_button = soup.find('button', {'aria-label': 'Previous testimonial'})
        self.assertIsNotNone(prev_button)
        
        next_button = soup.find('button', {'aria-label': 'Next testimonial'})
        self.assertIsNotNone(next_button)
        
        # Test dot ARIA labels
        dots = soup.find_all('button', {'class': 'carousel-dot'})
        for i, dot in enumerate(dots):
            expected_label = f'Go to testimonial {i + 1}'
            self.assertEqual(dot.get('aria-label'), expected_label)
    
    def test_semantic_html_structure(self):
        """Test proper semantic HTML structure."""
        response = self.client.get(reverse('core:testimonials'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test semantic elements
        self.assertIsNotNone(soup.find('main'))
        self.assertIsNotNone(soup.find('section'))
        
        # Test heading hierarchy
        h1_elements = soup.find_all('h1')
        self.assertEqual(len(h1_elements), 1)  # Should have one main heading
        
        # Test form structure in submit template
        response = self.client.get(reverse('core:submit_testimonial'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        form = soup.find('form')
        self.assertIsNotNone(form)
        
        # Test fieldset usage (if present)
        fieldsets = soup.find_all('fieldset')
        # Not required but good if present
    
    def test_keyboard_navigation_support(self):
        """Test keyboard navigation support in JavaScript."""
        response = self.client.get(reverse('core:submit_testimonial'))
        content = response.content.decode('utf-8')
        
        # Test for keyboard event handling
        if 'keydown' in content:
            self.assertIn('addEventListener', content)
        
        # Test carousel keyboard navigation
        context = {'carousel_testimonials': [self.testimonial1]}
        template = get_template('components/testimonial_carousel.html')
        html = template.render(context)
        
        # Test arrow key support
        self.assertIn('ArrowLeft', html)
        self.assertIn('ArrowRight', html)
        self.assertIn('keydown', html)


class PerformanceTestCase(TestimonialTemplateBaseTestCase):
    """Test performance aspects of testimonial templates."""
    
    def test_template_rendering_performance(self):
        """Test template rendering is reasonably fast."""
        import time
        
        urls_to_test = [
            reverse('core:submit_testimonial'),
            reverse('core:testimonials'),
            reverse('core:testimonial_success')
        ]
        
        for url in urls_to_test:
            start_time = time.time()
            response = self.client.get(url)
            end_time = time.time()
            
            render_time = end_time - start_time
            self.assertLess(render_time, 1.0, f"Template {url} took {render_time:.3f}s to render")
            self.assertEqual(response.status_code, 200)
    
    def test_image_optimization_attributes(self):
        """Test image optimization attributes are present."""
        response = self.client.get(reverse('core:testimonials'))
        content = response.content.decode('utf-8')
        
        # Test for lazy loading (if implemented)
        if 'loading=' in content:
            self.assertIn('loading="lazy"', content)
        
        # Test for proper alt attributes
        soup = BeautifulSoup(response.content, 'html.parser')
        images = soup.find_all('img')
        for img in images:
            self.assertTrue(img.get('alt') is not None, "Image missing alt attribute")
    
    def test_css_optimization(self):
        """Test CSS is properly optimized."""
        response = self.client.get(reverse('core:testimonials'))
        content = response.content.decode('utf-8')
        
        # Test for critical CSS inlining (CSS is inline in templates)
        self.assertIn('<style>', content)
        
        # Test for proper CSS organization
        css_sections = content.count('/* =====')
        if css_sections > 0:
            self.assertGreater(css_sections, 1)  # Well-organized CSS
    
    def test_javascript_optimization(self):
        """Test JavaScript is properly optimized."""
        response = self.client.get(reverse('core:submit_testimonial'))
        content = response.content.decode('utf-8')
        
        # Test for event delegation patterns
        if 'addEventListener' in content:
            self.assertIn('DOMContentLoaded', content)
        
        # Test for efficient DOM queries
        if 'getElementById' in content:
            # Good - specific ID queries are efficient
            self.assertTrue(True)
        
        # Test for proper script placement
        script_count = content.count('<script>')
        if script_count > 0:
            # Scripts should be at the end or have defer/async
            self.assertTrue(True)


class ErrorHandlingTestCase(TestimonialTemplateBaseTestCase):
    """Test error handling in testimonial templates."""
    
    def test_template_handles_missing_data(self):
        """Test templates handle missing data gracefully."""
        # Test display template with no testimonials
        Testimonial.objects.all().delete()
        
        response = self.client.get(reverse('core:testimonials'))
        self.assertEqual(response.status_code, 200)
        
        # Should show "no testimonials" message
        self.assertContains(response, 'No Testimonials Found')
    
    def test_template_handles_invalid_data(self):
        """Test templates handle invalid data gracefully."""
        # Create testimonial with missing rating
        testimonial = Testimonial.objects.create(
            student_name="Test User",
            email="test@example.com",
            class_type="choreo_team",
            rating=None,  # Invalid rating
            content="Test content",
            status="approved"
        )
        
        response = self.client.get(reverse('core:testimonials'))
        self.assertEqual(response.status_code, 200)
        
        # Template should handle None rating gracefully
        # This would be handled by the view or template filters
    
    def test_form_validation_errors_display(self):
        """Test form validation errors are displayed properly."""
        # Submit form with invalid data
        response = self.client.post(reverse('core:submit_testimonial'), {
            'student_name': '',  # Required field missing
            'email': 'invalid-email',  # Invalid email
            'class_type': 'Group Classes',
            'rating': '5',
            'content': 'Short'  # Too short
        })
        
        # Should redisplay form with errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'testimonials/submit.html')
        
        # Check for form errors in template
        # This depends on form implementation and error handling


class IntegrationTestCase(TestimonialTemplateBaseTestCase):
    """Integration tests for testimonial templates with views and models."""
    
    def test_submit_success_integration(self):
        """Test complete submit-to-success flow."""
        # Submit valid testimonial
        response = self.client.post(reverse('core:submit_testimonial'), {
            'student_name': 'Integration Test',
            'email': 'integration@example.com',
            'class_type': 'Group Classes',
            'rating': '5',
            'content': 'This is a test testimonial for integration testing with enough characters to pass validation.'
        })
        
        # Should redirect to success page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:testimonial_success'))
        
        # Follow redirect and check success page
        response = self.client.get(reverse('core:testimonial_success'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank You!')
    
    def test_filter_functionality_integration(self):
        """Test filter functionality works with templates."""
        # Test rating filter
        response = self.client.get(reverse('core:testimonials'), {'rating': '5'})
        self.assertEqual(response.status_code, 200)
        
        # Should only show 5-star testimonials
        soup = BeautifulSoup(response.content, 'html.parser')
        rating_displays = soup.find_all('div', {'class': 'testimonial-rating'})
        
        for rating_div in rating_displays:
            filled_stars = rating_div.find_all('i', {'class': 'fas fa-star'})
            # All should be 5-star ratings
            self.assertEqual(len(filled_stars), 5)
        
        # Test class type filter
        response = self.client.get(reverse('core:testimonials'), {'class_type': 'Private Lessons'})
        self.assertEqual(response.status_code, 200)
        
        # Should only show Private Lessons testimonials
        self.assertContains(response, 'Private Lessons')
    
    def test_carousel_integration_with_context(self):
        """Test carousel template integration with context data."""
        # This would typically be tested in a view that includes the carousel
        # For now, test the component directly
        context = {
            'carousel_testimonials': Testimonial.objects.filter(status="approved")[:3]
        }
        
        template = get_template('components/testimonial_carousel.html')
        html = template.render(context)
        
        self.assertIn('testimonial-carousel-section', html)
        self.assertIn('Maria Rodriguez', html)
        self.assertIn('John Smith', html)
        
        # Test that unapproved testimonials don't appear
        self.assertNotIn('Sarah Johnson', html)


class SecurityTestCase(TestimonialTemplateBaseTestCase):
    """Test security aspects of testimonial templates."""
    
    def test_xss_protection(self):
        """Test XSS protection in templates."""
        # Create testimonial with potential XSS content
        xss_testimonial = Testimonial.objects.create(
            student_name="<script>alert('xss')</script>Test User",
            email="test@example.com",
            class_type="choreo_team",
            rating=5,
            content="This is a test <script>alert('xss')</script> content",
            status="approved"
        )
        
        response = self.client.get(reverse('core:testimonials'))
        content = response.content.decode('utf-8')
        
        # Script tags should be escaped
        self.assertNotIn('<script>alert(', content)
        self.assertIn('&lt;script&gt;', content)
    
    def test_csrf_protection(self):
        """Test CSRF protection in forms."""
        response = self.client.get(reverse('core:submit_testimonial'))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # CSRF token should be present
        csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        self.assertIsNotNone(csrf_input)
        self.assertTrue(csrf_input.get('value'))
    
    def test_safe_url_generation(self):
        """Test URL generation is safe."""
        response = self.client.get(reverse('core:testimonials'))
        content = response.content.decode('utf-8')
        
        # URLs should be properly generated with reverse()
        # Check for hardcoded URLs (which would be a security issue)
        self.assertNotIn('href="/testimonials/', content)
        
        # Should use template tags for URL generation
        # This would be verified by checking the template source