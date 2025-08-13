"""
Comprehensive tests for the Pricing feature (SPEC02).

This test suite covers:
1. Pricing view returns 200 status
2. Pricing uses correct template (pricing.html)
3. All pricing options are displayed ($20, $70, $120)
4. "Most Popular" badge on 4-class package
5. Private lesson pricing range shown
6. Savings calculator elements present
7. JavaScript file pricing-calculator.js is linked
8. CSS file pricing.css is linked
9. Calculator input and output elements exist
10. Mobile responsive classes applied

Tests both JavaScript enabled and disabled scenarios.
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.http import HttpResponse
from django.template.loader import get_template
from bs4 import BeautifulSoup
import re


@override_settings(
    ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'],
    DEBUG=True
)
class PricingViewTestCase(TestCase):
    """Test suite for the pricing view functionality."""

    def setUp(self):
        """Set up test client and common data."""
        self.client = Client()
        self.pricing_url = reverse('core:pricing')

    def test_pricing_view_returns_200_status(self):
        """Test that the pricing view returns HTTP 200 status."""
        response = self.client.get(self.pricing_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, HttpResponse)

    def test_pricing_uses_correct_template(self):
        """Test that the pricing view uses the correct template."""
        response = self.client.get(self.pricing_url)
        self.assertTemplateUsed(response, 'pricing.html')
        
        # Verify template exists and is accessible
        template = get_template('pricing.html')
        self.assertIsNotNone(template)

    def test_pricing_view_context_data(self):
        """Test that pricing view provides correct context data."""
        response = self.client.get(self.pricing_url)
        self.assertIn('pricing_data', response.context)
        
        pricing_data = response.context['pricing_data']
        
        # Test drop-in pricing
        self.assertIn('drop_in', pricing_data)
        self.assertEqual(pricing_data['drop_in']['price'], 20)
        self.assertEqual(pricing_data['drop_in']['name'], 'Drop-in Class')
        
        # Test 4-class package
        self.assertIn('package_4', pricing_data)
        self.assertEqual(pricing_data['package_4']['price'], 70)
        self.assertEqual(pricing_data['package_4']['name'], '4-Class Package')
        self.assertTrue(pricing_data['package_4']['is_popular'])
        self.assertEqual(pricing_data['package_4']['savings'], 10)
        
        # Test 8-class package
        self.assertIn('package_8', pricing_data)
        self.assertEqual(pricing_data['package_8']['price'], 120)
        self.assertEqual(pricing_data['package_8']['name'], '8-Class Package')
        self.assertEqual(pricing_data['package_8']['savings'], 40)
        
        # Test private lessons
        self.assertIn('private_lessons', pricing_data)
        self.assertEqual(pricing_data['private_lessons']['price_min'], 75)
        self.assertEqual(pricing_data['private_lessons']['price_max'], 120)
        self.assertEqual(pricing_data['private_lessons']['name'], 'Private Lessons')


@override_settings(
    ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'],
    DEBUG=True
)
class PricingTemplateTestCase(TestCase):
    """Test suite for pricing template content and structure."""

    def setUp(self):
        """Set up test client and get pricing page content."""
        self.client = Client()
        self.pricing_url = reverse('core:pricing')
        self.response = self.client.get(self.pricing_url)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')

    def test_all_pricing_options_displayed(self):
        """Test that all pricing options ($20, $70, $120) are displayed."""
        content = self.response.content.decode('utf-8')
        
        # Test drop-in price ($20)
        self.assertIn('$20', content)
        drop_in_price = self.soup.find('span', class_='price-amount', string='20')
        self.assertIsNotNone(drop_in_price, "Drop-in price $20 not found")
        
        # Test 4-class package price ($70)
        self.assertIn('$70', content)
        package_4_price = self.soup.find('span', class_='price-amount', string='70')
        self.assertIsNotNone(package_4_price, "4-class package price $70 not found")
        
        # Test 8-class package price ($120)
        self.assertIn('$120', content)
        package_8_price = self.soup.find('span', class_='price-amount', string='120')
        self.assertIsNotNone(package_8_price, "8-class package price $120 not found")

    def test_most_popular_badge_on_4_class_package(self):
        """Test that the 'Most Popular' badge appears on the 4-class package."""
        # Find the most popular badge
        popular_badge = self.soup.find('div', class_='popular-badge')
        self.assertIsNotNone(popular_badge, "Most Popular badge not found")
        self.assertEqual(popular_badge.get_text().strip(), 'Most Popular')
        
        # Verify it's on the 4-class package card
        popular_card = self.soup.find('div', class_='pricing-card-popular')
        self.assertIsNotNone(popular_card, "Popular pricing card not found")
        
        # Check that the popular card contains the 4-class package
        card_title = popular_card.find('h3', class_='pricing-card-title')
        self.assertIsNotNone(card_title)
        self.assertIn('4-Class Package', card_title.get_text())
        
        # Verify the badge is within the popular card
        badge_in_card = popular_card.find('div', class_='popular-badge')
        self.assertIsNotNone(badge_in_card, "Popular badge not found within the 4-class package card")

    def test_private_lesson_pricing_range_shown(self):
        """Test that private lesson pricing range ($75-$120) is displayed."""
        content = self.response.content.decode('utf-8')
        
        # Test private lesson price range
        private_lessons_section = self.soup.find('div', class_='private-lessons-section')
        self.assertIsNotNone(private_lessons_section, "Private lessons section not found")
        
        # Check for price range elements
        price_range = self.soup.find('span', class_='price-range')
        self.assertIsNotNone(price_range, "Price range element not found")
        
        price_range_text = price_range.get_text().strip()
        self.assertIn('75', price_range_text)
        self.assertIn('120', price_range_text)
        self.assertIn('-', price_range_text)
        
        # Test that "per hour" is displayed
        self.assertIn('per hour', content)

    def test_savings_calculator_elements_present(self):
        """Test that savings calculator elements are present on the page."""
        # Test calculator section
        calculator_section = self.soup.find('div', class_='calculator-section')
        self.assertIsNotNone(calculator_section, "Calculator section not found")
        
        # Test calculator title
        calculator_title = self.soup.find('h2', class_='calculator-title')
        self.assertIsNotNone(calculator_title, "Calculator title not found")
        self.assertEqual(calculator_title.get_text().strip(), 'Savings Calculator')
        
        # Test calculator description
        calculator_description = self.soup.find('p', class_='calculator-description')
        self.assertIsNotNone(calculator_description, "Calculator description not found")
        self.assertIn('save', calculator_description.get_text().lower())

    def test_calculator_input_and_output_elements_exist(self):
        """Test that calculator input and output elements exist."""
        # Test input element
        classes_input = self.soup.find('input', id='classes-per-month')
        self.assertIsNotNone(classes_input, "Classes per month input not found")
        self.assertEqual(classes_input.get('type'), 'number')
        self.assertEqual(classes_input.get('min'), '1')
        self.assertEqual(classes_input.get('max'), '20')
        self.assertEqual(classes_input.get('value'), '4')
        
        # Test input label
        input_label = self.soup.find('label', {'for': 'classes-per-month'})
        self.assertIsNotNone(input_label, "Input label not found")
        self.assertIn('Classes per month', input_label.get_text())
        
        # Test output elements
        drop_in_cost = self.soup.find(id='drop-in-cost')
        self.assertIsNotNone(drop_in_cost, "Drop-in cost output element not found")
        
        package_cost = self.soup.find(id='package-cost')
        self.assertIsNotNone(package_cost, "Package cost output element not found")
        
        savings_amount = self.soup.find(id='savings-amount')
        self.assertIsNotNone(savings_amount, "Savings amount output element not found")
        
        savings_percentage = self.soup.find(id='savings-percentage')
        self.assertIsNotNone(savings_percentage, "Savings percentage output element not found")
        
        recommendation_text = self.soup.find(id='recommendation-text')
        self.assertIsNotNone(recommendation_text, "Recommendation text output element not found")

    def test_javascript_file_pricing_calculator_linked(self):
        """Test that the pricing-calculator.js file is properly linked."""
        content = self.response.content.decode('utf-8')
        
        # Test for JavaScript file inclusion in rendered HTML
        js_pattern = r'<script[^>]*src=["\'][^"\']*pricing-calculator\.js["\'][^>]*></script>'
        js_match = re.search(js_pattern, content)
        self.assertIsNotNone(js_match, "pricing-calculator.js script tag not found")
        
        # Test that the file path contains pricing-calculator.js
        self.assertIn('pricing-calculator.js', content)

    def test_css_file_pricing_linked(self):
        """Test that the pricing.css file is properly linked."""
        content = self.response.content.decode('utf-8')
        
        # Test for CSS file inclusion in rendered HTML
        css_pattern = r'<link[^>]*href=["\'][^"\']*pricing\.css["\'][^>]*>'
        css_match = re.search(css_pattern, content)
        self.assertIsNotNone(css_match, "pricing.css link tag not found")
        
        # Test that the file path contains pricing.css
        self.assertIn('pricing.css', content)

    def test_mobile_responsive_classes_applied(self):
        """Test that mobile responsive classes are applied to elements."""
        # Test main container has responsive classes
        container = self.soup.find('div', class_='container')
        self.assertIsNotNone(container, "Main container not found")
        
        # Test pricing grid has responsive grid classes
        pricing_grid = self.soup.find('div', class_='pricing-grid')
        self.assertIsNotNone(pricing_grid, "Pricing grid not found")
        
        # Test calculator results has responsive grid
        calculator_results = self.soup.find('div', class_='calculator-results')
        self.assertIsNotNone(calculator_results, "Calculator results not found")
        
        # Test info grid has responsive layout
        info_grid = self.soup.find('div', class_='info-grid')
        self.assertIsNotNone(info_grid, "Info grid not found")
        
        # Verify responsive meta tag is present
        viewport_meta = self.soup.find('meta', attrs={'name': 'viewport'})
        if viewport_meta:  # This should be in base template
            self.assertIn('width=device-width', viewport_meta.get('content', ''))


@override_settings(
    ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'],
    DEBUG=True
)
class PricingAccessibilityTestCase(TestCase):
    """Test suite for pricing page accessibility features."""

    def setUp(self):
        """Set up test client and get pricing page content."""
        self.client = Client()
        self.pricing_url = reverse('core:pricing')
        self.response = self.client.get(self.pricing_url)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')

    def test_semantic_html_structure(self):
        """Test that the page uses proper semantic HTML structure."""
        # Test heading hierarchy
        h1 = self.soup.find('h1')
        self.assertIsNotNone(h1, "Main heading (h1) not found")
        
        h2_elements = self.soup.find_all('h2')
        self.assertGreater(len(h2_elements), 0, "No h2 elements found")
        
        h3_elements = self.soup.find_all('h3')
        self.assertGreater(len(h3_elements), 0, "No h3 elements found")

    def test_form_labels_and_accessibility(self):
        """Test that form elements have proper labels and accessibility attributes."""
        # Test input has proper label association
        classes_input = self.soup.find('input', id='classes-per-month')
        self.assertIsNotNone(classes_input, "Classes input not found")
        
        label = self.soup.find('label', {'for': 'classes-per-month'})
        self.assertIsNotNone(label, "Label for classes input not found")
        
        # Test input accessibility attributes
        self.assertEqual(classes_input.get('min'), '1')
        self.assertEqual(classes_input.get('max'), '20')
        self.assertEqual(classes_input.get('type'), 'number')

    def test_button_accessibility(self):
        """Test that buttons have proper accessibility attributes."""
        buttons = self.soup.find_all('button')
        
        # Note: The pricing page may have buttons from the base template (mobile nav, etc.)
        # but not necessarily pricing-specific buttons, so we'll check for any interactive elements
        interactive_elements = self.soup.find_all(['button', 'a']) 
        self.assertGreater(len(interactive_elements), 0, "No interactive elements found on pricing page")
        
        # Check pricing-specific buttons (pricing cards have button-style links)
        pricing_buttons = self.soup.find_all('button', class_='pricing-card-button')
        if pricing_buttons:
            for button in pricing_buttons:
                # Buttons should have text content
                button_text = button.get_text().strip()
                self.assertGreater(len(button_text), 0, f"Button has no text content: {button}")

    def test_link_accessibility(self):
        """Test that links have proper accessibility attributes."""
        # Test private lesson link
        private_lesson_link = self.soup.find('a', class_='private-lessons-button')
        self.assertIsNotNone(private_lesson_link, "Private lessons button link not found")
        
        link_text = private_lesson_link.get_text().strip()
        self.assertGreater(len(link_text), 0, "Private lesson link has no text content")
        
        # Test that link has proper href
        href = private_lesson_link.get('href')
        self.assertIsNotNone(href, "Private lesson link has no href attribute")


@override_settings(
    ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'],
    DEBUG=True
)
class PricingJavaScriptFallbackTestCase(TestCase):
    """Test suite for JavaScript disabled scenarios and graceful degradation."""

    def setUp(self):
        """Set up test client and get pricing page content."""
        self.client = Client()
        self.pricing_url = reverse('core:pricing')
        self.response = self.client.get(self.pricing_url)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')

    def test_calculator_with_javascript_disabled(self):
        """Test that calculator displays default values when JavaScript is disabled."""
        # Test that default values are present in HTML
        drop_in_cost = self.soup.find(id='drop-in-cost')
        self.assertIsNotNone(drop_in_cost, "Drop-in cost element not found")
        self.assertEqual(drop_in_cost.get_text().strip(), '$80')
        
        package_cost = self.soup.find(id='package-cost')
        self.assertIsNotNone(package_cost, "Package cost element not found")
        self.assertEqual(package_cost.get_text().strip(), '$70')
        
        savings_amount = self.soup.find(id='savings-amount')
        self.assertIsNotNone(savings_amount, "Savings amount element not found")
        self.assertEqual(savings_amount.get_text().strip(), '$10')
        
        savings_percentage = self.soup.find(id='savings-percentage')
        self.assertIsNotNone(savings_percentage, "Savings percentage element not found")
        self.assertEqual(savings_percentage.get_text().strip(), '(12.5%)')

    def test_static_content_availability_without_javascript(self):
        """Test that all static content is available without JavaScript."""
        # All pricing information should be visible without JavaScript
        content = self.response.content.decode('utf-8')
        
        # Test that all price points are visible
        self.assertIn('$20', content)
        self.assertIn('$70', content)
        self.assertIn('$120', content)
        
        # Test that features are visible
        self.assertIn('Drop-in Class', content)
        self.assertIn('4-Class Package', content)
        self.assertIn('8-Class Package', content)
        self.assertIn('Private Lessons', content)
        
        # Test that all descriptive content is present
        self.assertIn('Most Popular', content)
        self.assertIn('Save $10', content)
        self.assertIn('Save $40', content)

    def test_form_submission_without_javascript(self):
        """Test that calculator input works without JavaScript (basic HTML form behavior)."""
        # Test that input element has proper attributes for fallback
        classes_input = self.soup.find('input', id='classes-per-month')
        self.assertIsNotNone(classes_input, "Classes input not found")
        
        # Test input has default value
        self.assertEqual(classes_input.get('value'), '4')
        
        # Test input has proper constraints
        self.assertEqual(classes_input.get('min'), '1')
        self.assertEqual(classes_input.get('max'), '20')
        self.assertEqual(classes_input.get('type'), 'number')


@override_settings(
    ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'],
    DEBUG=True
)
class PricingSEOTestCase(TestCase):
    """Test suite for pricing page SEO elements."""

    def setUp(self):
        """Set up test client and get pricing page content."""
        self.client = Client()
        self.pricing_url = reverse('core:pricing')
        self.response = self.client.get(self.pricing_url)
        self.soup = BeautifulSoup(self.response.content, 'html.parser')

    def test_page_title_present(self):
        """Test that the page has a proper title."""
        content = self.response.content.decode('utf-8')
        # Check that the actual title is in the rendered HTML
        self.assertIn('Pricing & Packages - Sabor con Flow Dance', content)
        # Or check the title tag specifically
        title_tag = self.soup.find('title')
        if title_tag:
            self.assertIn('Pricing', title_tag.get_text())

    def test_meta_description_present(self):
        """Test that the page has a meta description."""
        content = self.response.content.decode('utf-8')
        # Check for actual meta description in rendered HTML
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        self.assertIsNotNone(meta_desc, "Meta description tag not found")
        
        # Check content includes pricing info
        desc_content = meta_desc.get('content', '') if meta_desc else ''
        self.assertTrue(
            'dance classes' in desc_content.lower() or 'affordable' in desc_content.lower(),
            "Meta description should mention dance classes or affordability"
        )

    def test_structured_data_present(self):
        """Test that structured data (JSON-LD) is present."""
        content = self.response.content.decode('utf-8')
        self.assertIn('application/ld+json', content)
        self.assertIn('schema.org', content)
        self.assertIn('@type": "WebPage"', content)
        self.assertIn('Cuban Salsa Dance Classes', content)


@override_settings(
    ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'],
    DEBUG=True
)
class PricingPerformanceTestCase(TestCase):
    """Test suite for pricing page performance considerations."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.pricing_url = reverse('core:pricing')

    def test_page_loads_efficiently(self):
        """Test that the pricing page loads without excessive database queries."""
        # The pricing view should use static data, not database queries
        with self.assertNumQueries(0):
            response = self.client.get(self.pricing_url)
            self.assertEqual(response.status_code, 200)

    def test_static_files_referenced_correctly(self):
        """Test that static files are referenced correctly in rendered HTML."""
        response = self.client.get(self.pricing_url)
        content = response.content.decode('utf-8')
        
        # Test CSS file is properly linked in rendered HTML
        self.assertIn('pricing.css', content)
        
        # Test JavaScript file is properly linked in rendered HTML
        self.assertIn('pricing-calculator.js', content)


@override_settings(
    ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'],
    DEBUG=True
)
class PricingIntegrationTestCase(TestCase):
    """Integration tests for pricing page functionality."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.pricing_url = reverse('core:pricing')

    def test_pricing_page_navigation_integration(self):
        """Test that pricing page integrates properly with site navigation."""
        response = self.client.get(self.pricing_url)
        self.assertEqual(response.status_code, 200)
        
        # Test that page has navigation elements (from base template)
        content = response.content.decode('utf-8')
        self.assertIn('navbar', content)
        self.assertIn('Sabor Con Flow', content)

    def test_private_lessons_link_integration(self):
        """Test that private lessons link integrates with the site."""
        response = self.client.get(self.pricing_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find private lessons link
        private_lesson_link = soup.find('a', class_='private-lessons-button')
        self.assertIsNotNone(private_lesson_link, "Private lessons button not found")
        
        # Test that link goes to the correct URL
        href = private_lesson_link.get('href')
        self.assertIsNotNone(href, "Private lessons link has no href")
        self.assertIn('private-lessons', href)  # Should contain private-lessons in URL

    def test_pricing_url_configuration(self):
        """Test that pricing URL is properly configured."""
        # Test URL reverse lookup
        url = reverse('core:pricing')
        self.assertEqual(url, '/pricing/')
        
        # Test URL accessibility
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)