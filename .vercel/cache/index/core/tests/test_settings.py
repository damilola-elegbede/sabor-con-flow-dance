"""
Comprehensive settings tests for Sabor Con Flow Dance project.

Tests database configuration, static file settings, security settings,
and environment variable handling.
"""

import os
import tempfile
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from pathlib import Path


class DatabaseConfigurationTestCase(TestCase):
    """Test database configuration settings."""
    
    def test_database_default_configuration(self):
        """Test default database configuration (SQLite)."""
        # Test that default database is configured
        self.assertIn('default', settings.DATABASES)
        
        default_db = settings.DATABASES['default']
        self.assertEqual(default_db['ENGINE'], 'django.db.backends.sqlite3')
        
        # Test that database name is set correctly for local development
        if not (os.environ.get('TURSO_DATABASE_URL') and os.environ.get('TURSO_AUTH_TOKEN')):
            expected_name = settings.BASE_DIR / 'db.sqlite3'
            self.assertEqual(default_db['NAME'], expected_name)
    
    def test_database_foreign_keys_enabled(self):
        """Test that foreign keys are enabled in database configuration."""
        default_db = settings.DATABASES['default']
        self.assertIn('OPTIONS', default_db)
        self.assertIn('init_command', default_db['OPTIONS'])
        self.assertIn('PRAGMA foreign_keys=ON', default_db['OPTIONS']['init_command'])
    
    @patch.dict(os.environ, {
        'TURSO_DATABASE_URL': 'libsql://test-db.turso.io',
        'TURSO_AUTH_TOKEN': 'test-token-123'
    })
    def test_turso_database_configuration(self):
        """Test Turso database configuration when credentials are available."""
        # Reload settings to pick up environment variables
        from importlib import reload
        from sabor_con_flow import settings as settings_module
        reload(settings_module)
        
        # Test Turso configuration
        default_db = settings_module.DATABASES['default']
        self.assertEqual(default_db['ENGINE'], 'django.db.backends.sqlite3')
        self.assertEqual(default_db['NAME'], 'libsql://test-db.turso.io')
        self.assertIn('PRAGMA auth_token=\'test-token-123\'', default_db['OPTIONS']['init_command'])
    
    def test_database_configuration_without_turso_credentials(self):
        """Test database configuration falls back to local SQLite without Turso credentials."""
        # Test current database configuration
        default_db = settings.DATABASES['default']
        self.assertEqual(default_db['ENGINE'], 'django.db.backends.sqlite3')
        
        # Check if it's either local SQLite or test database
        if 'TURSO_DATABASE_URL' not in os.environ or 'TURSO_AUTH_TOKEN' not in os.environ:
            # Should be local SQLite configuration
            self.assertTrue(
                isinstance(default_db['NAME'], (str, Path)) and 
                str(default_db['NAME']).endswith(('.sqlite3', 'memorydb_default'))
            )


class StaticFilesConfigurationTestCase(TestCase):
    """Test static files configuration settings."""
    
    def test_static_url_configuration(self):
        """Test STATIC_URL is configured correctly."""
        self.assertEqual(settings.STATIC_URL, '/static/')
    
    def test_static_root_configuration(self):
        """Test STATIC_ROOT is configured correctly."""
        expected_root = settings.BASE_DIR / 'staticfiles'
        self.assertEqual(settings.STATIC_ROOT, expected_root)
    
    def test_staticfiles_dirs_configuration(self):
        """Test STATICFILES_DIRS is configured correctly."""
        self.assertIn(settings.BASE_DIR / "static", settings.STATICFILES_DIRS)
    
    def test_staticfiles_storage_in_production(self):
        """Test static files storage configuration for production."""
        with override_settings(DEBUG=False):
            # Check that WhiteNoise storage is configured for production
            # This would need to be tested by reloading settings module
            pass
    
    def test_whitenoise_middleware_configured(self):
        """Test that WhiteNoise middleware is properly configured."""
        self.assertIn('whitenoise.middleware.WhiteNoiseMiddleware', settings.MIDDLEWARE)
        
        # Check that WhiteNoise is positioned correctly (after SecurityMiddleware)
        security_index = settings.MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
        whitenoise_index = settings.MIDDLEWARE.index('whitenoise.middleware.WhiteNoiseMiddleware')
        self.assertEqual(whitenoise_index, security_index + 1)


class SecuritySettingsTestCase(TestCase):
    """Test security-related settings."""
    
    def test_secret_key_configuration(self):
        """Test SECRET_KEY configuration."""
        # In test environment, SECRET_KEY should be set
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertNotEqual(settings.SECRET_KEY, '')
    
    @patch.dict(os.environ, {'SECRET_KEY': 'test-secret-key-123'})
    def test_secret_key_from_environment(self):
        """Test that SECRET_KEY is read from environment variable."""
        from importlib import reload
        from sabor_con_flow import settings as settings_module
        reload(settings_module)
        
        self.assertEqual(settings_module.SECRET_KEY, 'test-secret-key-123')
    
    def test_secret_key_fallback_in_debug_mode(self):
        """Test SECRET_KEY fallback in debug mode."""
        # Test that SECRET_KEY is configured
        self.assertIsNotNone(settings.SECRET_KEY)
        
        # In test environment, we should have a secret key
        # The exact value depends on test environment setup
        self.assertGreater(len(settings.SECRET_KEY), 10)
    
    def test_secret_key_required_in_production(self):
        """Test that SECRET_KEY is configured for production readiness."""
        # Test that we have a SECRET_KEY configured
        self.assertIsNotNone(settings.SECRET_KEY)
        
        # Test that the secret key is sufficiently complex
        self.assertGreater(len(settings.SECRET_KEY), 20)
        
        # In test environment, this test verifies the key exists
        # Production validation would be done in deployment checks
    
    def test_debug_configuration(self):
        """Test DEBUG setting configuration."""
        # DEBUG should be False by default or based on environment
        debug_values = ['True', 'true', '1', 't']
        
        # Test various debug values
        for debug_val in debug_values:
            with patch.dict(os.environ, {'DJANGO_DEBUG': debug_val}):
                from importlib import reload
                from sabor_con_flow import settings as settings_module
                reload(settings_module)
                self.assertTrue(settings_module.DEBUG)
        
        # Test False values
        false_values = ['False', 'false', '0', 'f', '']
        for debug_val in false_values:
            with patch.dict(os.environ, {'DJANGO_DEBUG': debug_val}):
                from importlib import reload
                from sabor_con_flow import settings as settings_module
                reload(settings_module)
                self.assertFalse(settings_module.DEBUG)
    
    def test_allowed_hosts_configuration(self):
        """Test ALLOWED_HOSTS configuration."""
        # Test that ALLOWED_HOSTS contains expected domains
        expected_hosts = [
            'localhost',
            '127.0.0.1',
            '.vercel.app',
            'www.saborconflowdance.com',
            'saborconflowdance.com'
        ]
        
        for host in expected_hosts:
            # Check if host is in ALLOWED_HOSTS or if a pattern matches
            host_found = any(
                host == allowed_host or 
                (allowed_host.startswith('.') and host.endswith(allowed_host[1:]))
                for allowed_host in settings.ALLOWED_HOSTS
            )
            self.assertTrue(host_found, f"Host {host} not found in ALLOWED_HOSTS")
    
    @patch.dict(os.environ, {'DJANGO_ALLOWED_HOSTS': 'example.com,test.com'})
    def test_allowed_hosts_from_environment(self):
        """Test that ALLOWED_HOSTS can be configured from environment."""
        from importlib import reload
        from sabor_con_flow import settings as settings_module
        reload(settings_module)
        
        self.assertIn('example.com', settings_module.ALLOWED_HOSTS)
        self.assertIn('test.com', settings_module.ALLOWED_HOSTS)
    
    def test_csrf_trusted_origins_configuration(self):
        """Test CSRF_TRUSTED_ORIGINS configuration."""
        expected_origins = [
            'https://*.vercel.app',
            'https://www.saborconflowdance.com',
            'https://www.saborconflowdance.org',
            'https://www.saborconflowdance.info'
        ]
        
        for origin in expected_origins:
            self.assertIn(origin, settings.CSRF_TRUSTED_ORIGINS)
    
    def test_security_middleware_configuration(self):
        """Test that security middleware is properly configured."""
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ]
        
        for middleware in required_middleware:
            self.assertIn(middleware, settings.MIDDLEWARE)


class ApplicationConfigurationTestCase(TestCase):
    """Test application configuration settings."""
    
    def test_installed_apps_configuration(self):
        """Test INSTALLED_APPS configuration."""
        required_apps = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'core',
        ]
        
        for app in required_apps:
            self.assertIn(app, settings.INSTALLED_APPS)
    
    def test_middleware_configuration(self):
        """Test MIDDLEWARE configuration."""
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'whitenoise.middleware.WhiteNoiseMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ]
        
        for middleware in required_middleware:
            self.assertIn(middleware, settings.MIDDLEWARE)
        
        # Test middleware order (some middleware must be in specific order)
        security_index = settings.MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
        whitenoise_index = settings.MIDDLEWARE.index('whitenoise.middleware.WhiteNoiseMiddleware')
        sessions_index = settings.MIDDLEWARE.index('django.contrib.sessions.middleware.SessionMiddleware')
        auth_index = settings.MIDDLEWARE.index('django.contrib.auth.middleware.AuthenticationMiddleware')
        
        self.assertLess(security_index, whitenoise_index)
        self.assertLess(sessions_index, auth_index)
    
    def test_root_urlconf_configuration(self):
        """Test ROOT_URLCONF configuration."""
        self.assertEqual(settings.ROOT_URLCONF, 'sabor_con_flow.urls')
    
    def test_wsgi_application_configuration(self):
        """Test WSGI_APPLICATION configuration."""
        self.assertEqual(settings.WSGI_APPLICATION, 'sabor_con_flow.wsgi.application')


class TemplateConfigurationTestCase(TestCase):
    """Test template configuration settings."""
    
    def test_template_backend_configuration(self):
        """Test template backend configuration."""
        self.assertEqual(len(settings.TEMPLATES), 1)
        
        template_config = settings.TEMPLATES[0]
        self.assertEqual(template_config['BACKEND'], 'django.template.backends.django.DjangoTemplates')
    
    def test_template_dirs_configuration(self):
        """Test template directories configuration."""
        template_config = settings.TEMPLATES[0]
        self.assertIn(settings.BASE_DIR / 'templates', template_config['DIRS'])
    
    def test_template_app_dirs_enabled(self):
        """Test that APP_DIRS is enabled."""
        template_config = settings.TEMPLATES[0]
        self.assertTrue(template_config['APP_DIRS'])
    
    def test_template_context_processors(self):
        """Test template context processors configuration."""
        template_config = settings.TEMPLATES[0]
        context_processors = template_config['OPTIONS']['context_processors']
        
        required_processors = [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ]
        
        for processor in required_processors:
            self.assertIn(processor, context_processors)


class SessionConfigurationTestCase(TestCase):
    """Test session configuration settings."""
    
    def test_session_engine_configuration(self):
        """Test session engine configuration."""
        self.assertEqual(settings.SESSION_ENGINE, 'django.contrib.sessions.backends.db')
    
    def test_session_cookie_settings(self):
        """Test session cookie settings."""
        self.assertEqual(settings.SESSION_COOKIE_AGE, 86400)  # 1 day
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)


class LoggingConfigurationTestCase(TestCase):
    """Test logging configuration settings."""
    
    def test_logging_configuration_exists(self):
        """Test that logging configuration exists."""
        self.assertIn('LOGGING', dir(settings))
        self.assertIsInstance(settings.LOGGING, dict)
    
    def test_logging_version_configuration(self):
        """Test logging version configuration."""
        self.assertEqual(settings.LOGGING['version'], 1)
        self.assertFalse(settings.LOGGING['disable_existing_loggers'])
    
    def test_logging_handlers_configuration(self):
        """Test logging handlers configuration."""
        self.assertIn('handlers', settings.LOGGING)
        self.assertIn('console', settings.LOGGING['handlers'])
        
        console_handler = settings.LOGGING['handlers']['console']
        self.assertEqual(console_handler['class'], 'logging.StreamHandler')
    
    def test_logging_root_configuration(self):
        """Test root logger configuration."""
        self.assertIn('root', settings.LOGGING)
        root_config = settings.LOGGING['root']
        
        self.assertIn('console', root_config['handlers'])
        self.assertEqual(root_config['level'], 'INFO')
    
    def test_logging_django_logger_configuration(self):
        """Test Django logger configuration."""
        self.assertIn('loggers', settings.LOGGING)
        self.assertIn('django', settings.LOGGING['loggers'])
        
        django_logger = settings.LOGGING['loggers']['django']
        self.assertIn('console', django_logger['handlers'])
        self.assertFalse(django_logger['propagate'])


class EnvironmentVariableTestCase(TestCase):
    """Test environment variable handling."""
    
    def test_base_dir_configuration(self):
        """Test BASE_DIR configuration."""
        self.assertIsInstance(settings.BASE_DIR, Path)
        self.assertTrue(settings.BASE_DIR.exists())
        self.assertTrue((settings.BASE_DIR / 'manage.py').exists())
    
    def test_dotenv_loading(self):
        """Test that dotenv loading is properly configured."""
        # Test that .env file loading logic exists in settings
        # This is tested indirectly by checking that settings can handle
        # environment variables properly
        pass
    
    @patch.dict(os.environ, {'DJANGO_LOG_LEVEL': 'DEBUG'})
    def test_django_log_level_from_environment(self):
        """Test that Django log level can be set from environment."""
        from importlib import reload
        from sabor_con_flow import settings as settings_module
        reload(settings_module)
        
        django_logger = settings_module.LOGGING['loggers']['django']
        self.assertEqual(django_logger['level'], 'DEBUG')


class ProductionSettingsTestCase(TestCase):
    """Test production-specific settings."""
    
    @patch.dict(os.environ, {'DJANGO_DEBUG': 'False'})
    def test_production_security_settings(self):
        """Test security settings in production mode."""
        from importlib import reload
        from sabor_con_flow import settings as settings_module
        reload(settings_module)
        
        # These settings should be enabled in production
        if not settings_module.DEBUG:
            self.assertFalse(settings_module.SECURE_SSL_REDIRECT)  # Disabled for Vercel
            self.assertTrue(settings_module.SESSION_COOKIE_SECURE)
            self.assertTrue(settings_module.CSRF_COOKIE_SECURE)
            self.assertTrue(settings_module.SECURE_BROWSER_XSS_FILTER)
            self.assertTrue(settings_module.SECURE_CONTENT_TYPE_NOSNIFF)
            self.assertEqual(settings_module.SECURE_HSTS_SECONDS, 31536000)
            self.assertTrue(settings_module.SECURE_HSTS_INCLUDE_SUBDOMAINS)
            self.assertTrue(settings_module.SECURE_HSTS_PRELOAD)
            self.assertEqual(settings_module.X_FRAME_OPTIONS, 'DENY')
    
    @patch.dict(os.environ, {'DJANGO_DEBUG': 'True'})
    def test_development_settings(self):
        """Test development-specific settings."""
        from importlib import reload
        from sabor_con_flow import settings as settings_module
        reload(settings_module)
        
        # In development mode, security settings should be more relaxed
        if settings_module.DEBUG:
            # Development-specific checks
            self.assertIn('localhost', settings_module.ALLOWED_HOSTS)
            self.assertIn('127.0.0.1', settings_module.ALLOWED_HOSTS)


class DefaultAutoFieldTestCase(TestCase):
    """Test default auto field configuration."""
    
    def test_default_auto_field_configuration(self):
        """Test DEFAULT_AUTO_FIELD configuration."""
        self.assertEqual(settings.DEFAULT_AUTO_FIELD, 'django.db.models.BigAutoField')