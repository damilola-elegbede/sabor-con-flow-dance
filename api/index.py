import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Django and configure it
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sabor_con_flow.settings')

import django
django.setup()

from django.core.handlers.wsgi import WSGIHandler

# Create the WSGI application
app = WSGIHandler()

# Vercel expects a callable named 'handler'
handler = app