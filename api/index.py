import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sabor_con_flow.settings')

import django
django.setup()

# Import the WSGI application
from sabor_con_flow.wsgi import application

# Vercel expects an 'app' variable for WSGI applications
app = application