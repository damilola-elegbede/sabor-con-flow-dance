import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sabor_con_flow.settings')

# Set default environment variables if not present (for Vercel)
if not os.environ.get('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'django-insecure-vercel-default-key-please-set-in-vercel-dashboard'

if not os.environ.get('TURSO_DATABASE_URL'):
    os.environ['TURSO_DATABASE_URL'] = 'libsql://localhost:8080'
    
if not os.environ.get('TURSO_AUTH_TOKEN'):
    os.environ['TURSO_AUTH_TOKEN'] = 'dummy-token'

# Set DEBUG to False for production
os.environ['DJANGO_DEBUG'] = os.environ.get('DJANGO_DEBUG', 'False')

import django
django.setup()

# Import the WSGI application
from sabor_con_flow.wsgi import application

# Vercel expects an 'app' variable for WSGI applications
app = application