"""
Test suite for Hero section implementation (SPEC-02)

Tests the Hero section on the home page including:
- Home view functionality
- Template rendering
- Hero content elements
- CTA buttons
- Trust indicators
- Video background
- CSS styling
- Mobile responsiveness
- SEO meta tags
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from django.template.loader import get_template
from django.test.utils import override_settings
from bs4 import BeautifulSoup
import os
import re


class HeroSectionBasicTests(TestCase):
    """Basic functional tests for the Hero section"""

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')

    def test_home_view_returns_200_status(self):
        """Test that home view returns 200 status code"""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)

    def test_homepage_uses_correct_template(self):
        """Test that homepage uses the correct template (home.html)"""
        response = self.client.get(self.home_url)
        self.assertTemplateUsed(response, 'home.html')
        self.assertTemplateUsed(response, 'base.html')  # Extended template

    def test_home_view_with_get_request(self):
        """Test home view handles GET requests properly"""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('upcoming_events', response.context)

    def test_home_view_context_data(self):
        """Test that home view provides correct context data"""
        response = self.client.get(self.home_url)
        self.assertIn('upcoming_events', response.context)
        upcoming_events = response.context['upcoming_events']
        self.assertIsInstance(upcoming_events, list)
        self.assertGreater(len(upcoming_events), 0)


class HeroContentTests(TestCase):
    """Tests for Hero section content elements"""

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')

    def get_soup(self):
        """Helper method to get BeautifulSoup object from home page"""
        response = self.client.get(self.home_url)
        return BeautifulSoup(response.content, 'html.parser')

    def test_hero_section_contains_correct_headline_text(self):
        """Test that hero section contains the correct headline text"""
        soup = self.get_soup()
        
        # Find the hero headline
        hero_headline = soup.find('h1', class_='hero-headline')
        self.assertIsNotNone(hero_headline, "Hero headline element not found")
        
        # Check headline text (allowing for emoji and text variations)
        headline_text = hero_headline.get_text(strip=True)
        expected_text = "Sabor in every step, flow in every move"
        self.assertIn(expected_text, headline_text)

    def test_hero_section_structure(self):
        """Test that hero section has correct HTML structure"""
        soup = self.get_soup()
        
        # Check hero section exists
        hero_section = soup.find('section', class_='hero-section')
        self.assertIsNotNone(hero_section, "Hero section not found")
        
        # Check hero content container
        hero_content = soup.find('div', class_='hero-content')
        self.assertIsNotNone(hero_content, "Hero content container not found")
        
        # Check hero text container
        hero_text = soup.find('div', class_='hero-text')
        self.assertIsNotNone(hero_text, "Hero text container not found")

    def test_hero_subheadline_present(self):
        """Test that hero subheadline is present and correct"""
        soup = self.get_soup()
        
        subheadline = soup.find('p', class_='hero-subheadline')
        self.assertIsNotNone(subheadline, "Hero subheadline not found")
        
        subheadline_text = subheadline.get_text(strip=True)
        expected_text = "Discover the rhythm within. Join our passionate community of dancers."
        self.assertEqual(subheadline_text, expected_text)


class HeroCTAButtonTests(TestCase):
    """Tests for Hero section CTA buttons"""

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')

    def get_soup(self):
        """Helper method to get BeautifulSoup object from home page"""
        response = self.client.get(self.home_url)
        return BeautifulSoup(response.content, 'html.parser')

    def test_two_cta_buttons_are_present(self):
        """Test that two CTA buttons are present"""
        soup = self.get_soup()
        
        # Find CTA container
        cta_container = soup.find('div', class_='hero-cta')
        self.assertIsNotNone(cta_container, "CTA container not found")
        
        # Find all CTA buttons
        cta_buttons = cta_container.find_all('a', class_=['btn-hero-primary', 'btn-hero-secondary'])
        self.assertEqual(len(cta_buttons), 2, "Expected exactly 2 CTA buttons")

    def test_cta_buttons_have_correct_text(self):
        """Test that CTA buttons have correct text"""
        soup = self.get_soup()
        
        # Find primary CTA button
        primary_btn = soup.find('a', class_='btn-hero-primary')
        self.assertIsNotNone(primary_btn, "Primary CTA button not found")
        primary_text = primary_btn.get_text(strip=True)
        self.assertEqual(primary_text, "Book Your Class")
        
        # Find secondary CTA button
        secondary_btn = soup.find('a', class_='btn-hero-secondary')
        self.assertIsNotNone(secondary_btn, "Secondary CTA button not found")
        secondary_text = secondary_btn.get_text(strip=True)
        self.assertEqual(secondary_text, "View Schedule")

    def test_cta_buttons_have_correct_attributes(self):
        """Test that CTA buttons have correct href attributes"""
        soup = self.get_soup()
        
        # Test primary button
        primary_btn = soup.find('a', class_='btn-hero-primary')
        self.assertEqual(primary_btn.get('href'), '#book')
        
        # Test secondary button  
        secondary_btn = soup.find('a', class_='btn-hero-secondary')
        self.assertEqual(secondary_btn.get('href'), '#schedule')

    def test_cta_buttons_styling_classes(self):
        """Test that CTA buttons have correct CSS classes"""
        soup = self.get_soup()
        
        # Find all CTA buttons
        primary_btn = soup.find('a', class_='btn-hero-primary')
        secondary_btn = soup.find('a', class_='btn-hero-secondary')
        
        # Check classes
        self.assertIn('btn-hero-primary', primary_btn.get('class', []))
        self.assertIn('btn-hero-secondary', secondary_btn.get('class', []))


class HeroTrustIndicatorTests(TestCase):
    """Tests for Hero section trust indicator"""

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')

    def get_soup(self):
        """Helper method to get BeautifulSoup object from home page"""
        response = self.client.get(self.home_url)
        return BeautifulSoup(response.content, 'html.parser')

    def test_trust_indicator_shows_correct_text(self):
        """Test that trust indicator shows '200+ Happy Dancers'"""
        soup = self.get_soup()
        
        # Find trust indicator
        trust_badge = soup.find('span', class_='trust-badge')
        self.assertIsNotNone(trust_badge, "Trust badge not found")
        
        # Check text content
        trust_text = trust_badge.get_text(strip=True)
        self.assertIn("200+ Happy Dancers", trust_text)

    def test_trust_indicator_structure(self):
        """Test that trust indicator has correct structure"""
        soup = self.get_soup()
        
        # Find trust container
        trust_container = soup.find('div', class_='hero-trust')
        self.assertIsNotNone(trust_container, "Trust container not found")
        
        # Find trust badge
        trust_badge = soup.find('span', class_='trust-badge')
        self.assertIsNotNone(trust_badge, "Trust badge not found")
        
        # Check for icon
        icon = trust_badge.find('i', class_='fas fa-users')
        self.assertIsNotNone(icon, "Trust indicator icon not found")


class HeroVideoTests(TestCase):
    """Tests for Hero section video background"""

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')

    def get_soup(self):
        """Helper method to get BeautifulSoup object from home page"""
        response = self.client.get(self.home_url)
        return BeautifulSoup(response.content, 'html.parser')

    def test_video_element_has_correct_attributes(self):
        """Test that video element has correct attributes (autoplay, loop, muted)"""
        soup = self.get_soup()
        
        # Find video element
        video = soup.find('video', class_='hero-video')
        self.assertIsNotNone(video, "Hero video element not found")
        
        # Check required attributes
        self.assertTrue(video.has_attr('autoplay'), "Video missing autoplay attribute")
        self.assertTrue(video.has_attr('loop'), "Video missing loop attribute")
        self.assertTrue(video.has_attr('muted'), "Video missing muted attribute")
        self.assertTrue(video.has_attr('playsinline'), "Video missing playsinline attribute")

    def test_video_source_element(self):
        """Test that video has correct source element"""
        soup = self.get_soup()
        
        # Find video element
        video = soup.find('video', class_='hero-video')
        self.assertIsNotNone(video, "Hero video element not found")
        
        # Find source element
        source = video.find('source')
        self.assertIsNotNone(source, "Video source element not found")
        
        # Check source attributes
        self.assertEqual(source.get('type'), 'video/mp4')
        self.assertIn('hero-loop.mp4', source.get('src', ''))

    def test_video_container_structure(self):
        """Test that video container has correct structure"""
        soup = self.get_soup()
        
        # Find video container
        video_container = soup.find('div', class_='hero-video-container')
        self.assertIsNotNone(video_container, "Video container not found")
        
        # Find video element within container
        video = video_container.find('video', class_='hero-video')
        self.assertIsNotNone(video, "Video element not found in container")


class HeroOverlayTests(TestCase):
    """Tests for Hero section overlay"""

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')

    def get_soup(self):
        """Helper method to get BeautifulSoup object from home page"""
        response = self.client.get(self.home_url)
        return BeautifulSoup(response.content, 'html.parser')

    def test_overlay_div_is_present(self):
        """Test that overlay div is present"""
        soup = self.get_soup()
        
        # Find overlay element
        overlay = soup.find('div', class_='hero-overlay')
        self.assertIsNotNone(overlay, "Hero overlay not found")

    def test_overlay_within_video_container(self):
        """Test that overlay is within video container"""
        soup = self.get_soup()
        
        # Find video container
        video_container = soup.find('div', class_='hero-video-container')
        self.assertIsNotNone(video_container, "Video container not found")
        
        # Find overlay within container
        overlay = video_container.find('div', class_='hero-overlay')
        self.assertIsNotNone(overlay, "Overlay not found within video container")


class HeroCSSTests(TestCase):
    """Tests for Hero section CSS file inclusion"""

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')

    def get_soup(self):
        """Helper method to get BeautifulSoup object from home page"""
        response = self.client.get(self.home_url)
        return BeautifulSoup(response.content, 'html.parser')

    def test_hero_css_file_is_linked(self):
        """Test that hero.css file is linked in the page"""
        soup = self.get_soup()
        
        # Find link tags
        link_tags = soup.find_all('link')
        hero_css_found = False
        
        for link in link_tags:
            href = link.get('href', '')
            if 'hero.css' in href:
                hero_css_found = True
                break
        
        self.assertTrue(hero_css_found, "hero.css file not found in page links")

    def test_hero_css_file_exists(self):
        """Test that hero.css file exists in static directory"""
        css_path = os.path.join(settings.BASE_DIR, 'static', 'css', 'hero.css')
        self.assertTrue(os.path.exists(css_path), f"hero.css file not found at {css_path}")


class HeroMobileResponsivenessTests(TestCase):
    """Tests for Hero section mobile responsiveness"""

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')

    def get_soup(self):
        """Helper method to get BeautifulSoup object from home page"""
        response = self.client.get(self.home_url)
        return BeautifulSoup(response.content, 'html.parser')

    def test_mobile_responsiveness_classes_are_present(self):
        """Test that mobile responsiveness classes are present"""
        soup = self.get_soup()
        
        # Check for container class
        container = soup.find('div', class_='container')
        self.assertIsNotNone(container, "Container class not found")
        
        # Check for responsive hero elements
        hero_content = soup.find('div', class_='hero-content')
        self.assertIsNotNone(hero_content, "Hero content class not found")
        
        hero_text = soup.find('div', class_='hero-text')
        self.assertIsNotNone(hero_text, "Hero text class not found")

    def test_hero_css_contains_mobile_media_queries(self):
        """Test that hero.css contains mobile media queries"""
        css_path = os.path.join(settings.BASE_DIR, 'static', 'css', 'hero.css')
        
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            # Check for mobile media queries
            mobile_queries = [
                '@media (max-width: 767px)',
                '@media (min-width: 768px)',
                '@media (min-width: 1024px)'
            ]
            
            for query in mobile_queries:
                self.assertIn(query, css_content, f"Mobile media query '{query}' not found in hero.css")


class HeroSEOTests(TestCase):
    """Tests for Hero section SEO meta tags"""

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')

    def get_soup(self):
        """Helper method to get BeautifulSoup object from home page"""
        response = self.client.get(self.home_url)
        return BeautifulSoup(response.content, 'html.parser')

    def test_seo_meta_tags_are_properly_set(self):
        """Test that SEO meta tags are properly set"""
        soup = self.get_soup()
        
        # Check title tag
        title = soup.find('title')
        self.assertIsNotNone(title, "Title tag not found")
        title_text = title.get_text()
        self.assertIn("Sabor con Flow Dance", title_text)
        self.assertIn("Cuban Salsa Classes", title_text)
        self.assertIn("Boulder", title_text)

    def test_meta_description_tag(self):
        """Test that meta description tag is present and correct"""
        soup = self.get_soup()
        
        meta_description = soup.find('meta', attrs={'name': 'description'})
        self.assertIsNotNone(meta_description, "Meta description tag not found")
        
        description_content = meta_description.get('content', '')
        self.assertIn("cuban salsa dance studio", description_content.lower())
        self.assertIn("Boulder", description_content)

    def test_meta_keywords_tag(self):
        """Test that meta keywords tag is present"""
        soup = self.get_soup()
        
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        self.assertIsNotNone(meta_keywords, "Meta keywords tag not found")
        
        keywords_content = meta_keywords.get('content', '')
        expected_keywords = ['Cuban salsa', 'Boulder', 'dance classes', 'salsa lessons']
        
        for keyword in expected_keywords:
            self.assertIn(keyword, keywords_content)

    def test_canonical_url_tag(self):
        """Test that canonical URL tag is present"""
        soup = self.get_soup()
        
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        self.assertIsNotNone(canonical, "Canonical URL tag not found")
        
        canonical_href = canonical.get('href', '')
        self.assertIsNotNone(canonical_href, "Canonical URL href is empty")

    def test_open_graph_tags(self):
        """Test that Open Graph meta tags are present"""
        soup = self.get_soup()
        
        # Check for essential OG tags
        og_tags = {
            'og:title': soup.find('meta', attrs={'property': 'og:title'}),
            'og:description': soup.find('meta', attrs={'property': 'og:description'}),
            'og:type': soup.find('meta', attrs={'property': 'og:type'})
        }
        
        for tag_name, tag_element in og_tags.items():
            self.assertIsNotNone(tag_element, f"Open Graph {tag_name} tag not found")
            content = tag_element.get('content', '')
            self.assertIsNotNone(content, f"Open Graph {tag_name} content is empty")

    def test_structured_data_present(self):
        """Test that structured data (JSON-LD) is present"""
        soup = self.get_soup()
        
        # Find JSON-LD script tag
        json_ld = soup.find('script', attrs={'type': 'application/ld+json'})
        self.assertIsNotNone(json_ld, "Structured data (JSON-LD) script not found")
        
        # Check content contains expected schema
        json_content = json_ld.string
        self.assertIn('"@context"', json_content)
        self.assertIn('"@type"', json_content)
        self.assertIn('DanceGroup', json_content)


class HeroScrollIndicatorTests(TestCase):
    """Tests for Hero section scroll indicator"""

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')

    def get_soup(self):
        """Helper method to get BeautifulSoup object from home page"""
        response = self.client.get(self.home_url)
        return BeautifulSoup(response.content, 'html.parser')

    def test_scroll_indicator_is_present(self):
        """Test that scroll indicator is present"""
        soup = self.get_soup()
        
        scroll_indicator = soup.find('div', class_='hero-scroll-indicator')
        self.assertIsNotNone(scroll_indicator, "Scroll indicator not found")
        
        # Check for chevron icon
        chevron_icon = scroll_indicator.find('i', class_='fas fa-chevron-down')
        self.assertIsNotNone(chevron_icon, "Chevron icon not found in scroll indicator")


class HeroEdgeCaseTests(TestCase):
    """Edge case tests for Hero section"""

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')

    def test_hero_section_with_invalid_url(self):
        """Test that invalid URLs return 404, not breaking hero section"""
        response = self.client.get('/invalid-url/')
        self.assertEqual(response.status_code, 404)

    def test_hero_section_with_post_request(self):
        """Test hero section with POST request (should still work for GET data)"""
        # POST requests to home should still return the page (though not typical)
        response = self.client.post(self.home_url)
        # Home view only handles GET, so this might return 405 Method Not Allowed
        # or still return the page - depends on Django's handling
        self.assertIn(response.status_code, [200, 405])

    def test_hero_section_accessibility_attributes(self):
        """Test that hero section has proper accessibility attributes"""
        soup = self.get_soup()
        
        # Check for proper heading structure
        h1 = soup.find('h1', class_='hero-headline')
        self.assertIsNotNone(h1, "H1 heading not found")
        
        # Check video has proper attributes for accessibility
        video = soup.find('video', class_='hero-video')
        if video:
            # Video should be muted for autoplay accessibility
            self.assertTrue(video.has_attr('muted'), "Autoplay video should be muted for accessibility")

    def test_hero_section_fallback_content(self):
        """Test that hero section has fallback content for video"""
        soup = self.get_soup()
        
        video = soup.find('video', class_='hero-video')
        if video:
            # Check for fallback image within video element
            fallback_img = video.find('img')
            if fallback_img:
                self.assertTrue(fallback_img.has_attr('alt'), "Fallback image should have alt attribute")

    def get_soup(self):
        """Helper method to get BeautifulSoup object from home page"""
        response = self.client.get(self.home_url)
        return BeautifulSoup(response.content, 'html.parser')


class HeroPerformanceTests(TestCase):
    """Performance-related tests for Hero section"""

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')

    def test_hero_video_preload_attribute(self):
        """Test that hero video has preload attribute for performance"""
        soup = self.get_soup()
        
        video = soup.find('video', class_='hero-video')
        if video:
            # Check for preload attribute
            preload = video.get('preload')
            self.assertIsNotNone(preload, "Video should have preload attribute for performance")
            self.assertEqual(preload, 'auto', "Video preload should be set to 'auto'")

    def test_hero_css_preload_link(self):
        """Test that hero CSS is preloaded for performance"""
        soup = self.get_soup()
        
        # Find preload links
        preload_links = soup.find_all('link', attrs={'rel': 'preload'})
        hero_css_preloaded = False
        
        for link in preload_links:
            href = link.get('href', '')
            if 'hero.css' in href:
                hero_css_preloaded = True
                self.assertEqual(link.get('as'), 'style', "Hero CSS preload should specify as='style'")
                break
        
        self.assertTrue(hero_css_preloaded, "Hero CSS should be preloaded for performance")

    def get_soup(self):
        """Helper method to get BeautifulSoup object from home page"""
        response = self.client.get(self.home_url)
        return BeautifulSoup(response.content, 'html.parser')