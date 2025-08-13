"""
Test module for Sabor Con Flow Dance core application.

This module imports all tests from the tests package.
Individual test modules are located in the tests/ directory:

- test_models.py: Model tests for Instructor, Class, Testimonial, Resource
- test_admin.py: Admin interface tests
- test_views.py: View response and template tests
- test_settings.py: Settings and configuration tests

Run tests with: python manage.py test core
"""

# Import all tests from the tests package
from .tests.test_models import *
from .tests.test_admin import *
from .tests.test_views import *
from .tests.test_settings import *
