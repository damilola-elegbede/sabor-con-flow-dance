"""
Development-specific Django settings for optimal local development experience.
Platform Engineering Configuration - Django Dev Server Optimization
"""

from .settings import *
import logging
import sys

# Override DEBUG for development
DEBUG = True

# Development-specific logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'dev': {
            'format': '\033[1;32m[{levelname}]\033[0m {asctime} \033[1;34m{name}\033[0m: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'dev',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'django_dev.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'database_performance': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',  # Set to DEBUG to see all SQL queries
            'propagate': False,
        },
        'core': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Development database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_dev.sqlite3',
        'OPTIONS': {
            'init_command': 'PRAGMA foreign_keys=ON; PRAGMA journal_mode=WAL;',
            'timeout': 20,
        },
    }
}

# Development cache configuration (faster startup)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'page_cache': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'static_cache': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
}

# Static files configuration for development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Development middleware (remove heavy monitoring middleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Add development middleware
    'core.middleware.QueryCountDebugMiddleware',
]

# Add Django Debug Toolbar for development
if DEBUG and os.environ.get('ENABLE_DEBUG_TOOLBAR', 'True').lower() in ('true', '1', 't'):
    try:
        import debug_toolbar
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        
        # Debug Toolbar settings
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
            'SHOW_COLLAPSED': True,
            'PROFILER_MAX_DEPTH': 20,
        }
        
        # Allow Debug Toolbar for all IPs in development
        INTERNAL_IPS = ['127.0.0.1', 'localhost']
        
    except ImportError:
        print("DEBUG: Django Debug Toolbar not installed. Install with: pip install django-debug-toolbar")

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Security settings relaxed for development
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://0.0.0.0:8000',
]

# Disable security middleware redirects
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Development session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 1 day
SESSION_SAVE_EVERY_REQUEST = False

# Disable Sentry for development
if 'sentry_sdk' in sys.modules:
    import sentry_sdk
    sentry_sdk.init()  # Initialize with no DSN to disable

# Hot reload configuration
if DEBUG:
    # Watch for template changes
    TEMPLATES[0]['OPTIONS']['debug'] = True
    
    # Watch for static file changes
    STATICFILES_DIRS = [
        BASE_DIR / "static",
    ]
    
    # Template configuration for development (disable APP_DIRS when loaders are defined)
    TEMPLATES[0]['APP_DIRS'] = False
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]

# Development performance settings
CONN_MAX_AGE = 0  # Disable persistent connections for development

# Print development configuration summary
print(f"""
\033[1;32m{'='*60}\033[0m
\033[1;32mDjango Development Server Configuration\033[0m
\033[1;32m{'='*60}\033[0m
🚀 Environment: \033[1;34mDEVELOPMENT\033[0m
🗄️  Database: \033[1;34m{DATABASES['default']['NAME']}\033[0m
📧 Email Backend: \033[1;34mconsole\033[0m
🔍 Debug Toolbar: \033[1;34m{'enabled' if 'debug_toolbar' in INSTALLED_APPS else 'not available'}\033[0m
🎯 Cache: \033[1;34mdisabled (dummy cache)\033[0m
📊 SQL Queries: \033[1;34m{'logged' if 'django.db.backends' in LOGGING['loggers'] else 'not logged'}\033[0m
\033[1;32m{'='*60}\033[0m
""")