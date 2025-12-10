"""
Context processors for making settings and configuration available in templates.
"""

from django.conf import settings

def analytics_settings(request):
    """
    Add Google Analytics 4 and business configuration to template context.
    SPEC_05 Group A Task 3 - GA4 Implementation
    """
    return {
        'analytics': {
            'ga4_measurement_id': getattr(settings, 'GA4_MEASUREMENT_ID', ''),
            'ga4_debug_mode': getattr(settings, 'GA4_DEBUG_MODE', False),
            'enable_analytics': getattr(settings, 'ENABLE_ANALYTICS', True),
            'anonymize_ip': getattr(settings, 'GA4_ANONYMIZE_IP', True),
            'respect_dnt': getattr(settings, 'GA4_RESPECT_DNT', True),
        },
        'business_info': getattr(settings, 'BUSINESS_INFO', {}),
        'class_pricing': getattr(settings, 'CLASS_PRICING', {}),
        'debug_mode': settings.DEBUG,
    }

def site_settings(request):
    """
    Add general site settings to template context.
    """
    return {
        'site_settings': {
            'debug': settings.DEBUG,
            'site_name': 'Sabor Con Flow Dance',
            'site_tagline': 'Your premier destination for Latin dance classes',
        }
    }