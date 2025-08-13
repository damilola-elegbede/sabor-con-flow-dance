"""
Template tags for cache-related functionality.
"""
from django import template
from django.contrib.staticfiles.storage import staticfiles_storage
from django.templatetags.static import static
from django.conf import settings
from django.utils.safestring import mark_safe
from core.utils.cache_utils import CacheBusting
import time
import hashlib

register = template.Library()


@register.simple_tag
def cached_static(path):
    """
    Generate a static URL with cache busting version parameter.
    
    Usage: {% cached_static 'css/styles.css' %}
    Returns: /static/css/styles.css?v=abc123ef
    """
    # Get the base static URL
    static_url = static(path)
    
    # Add version parameter for cache busting
    if not settings.DEBUG:
        # In production, use file-based versioning
        version = CacheBusting.get_static_file_version(path)
        static_url = CacheBusting.add_version_to_url(static_url, version)
    else:
        # In development, use timestamp
        version = str(int(time.time()))
        static_url = CacheBusting.add_version_to_url(static_url, version)
    
    return static_url


@register.simple_tag
def cache_version():
    """
    Get current cache version for manual cache busting.
    
    Usage: {% cache_version %}
    Returns: Current cache version number
    """
    return getattr(settings, 'CACHE_VERSION', 1)


@register.simple_tag
def asset_version(path):
    """
    Generate version hash for any asset path.
    
    Usage: {% asset_version 'css/styles.css' %}
    Returns: Version hash string
    """
    return CacheBusting.generate_version_hash(path)


@register.filter
def add_cache_buster(url):
    """
    Add cache busting parameter to any URL.
    
    Usage: {{ '/some/url/'|add_cache_buster }}
    Returns: /some/url/?v=timestamp
    """
    version = str(int(time.time()))
    return CacheBusting.add_version_to_url(url, version)


@register.inclusion_tag('cache/preload_hints.html')
def cache_preload_hints():
    """
    Generate preload hints for critical cached resources.
    
    Usage: {% cache_preload_hints %}
    """
    # Define critical resources to preload
    critical_resources = [
        {
            'url': cached_static('css/styles.css'),
            'type': 'style',
            'importance': 'high'
        },
        {
            'url': cached_static('js/performance-monitor.js'),
            'type': 'script',
            'importance': 'low'
        },
        {
            'url': cached_static('images/sabor-con-flow-logo.webp'),
            'type': 'image',
            'importance': 'high'
        },
    ]
    
    return {'resources': critical_resources}


@register.simple_tag
def cache_control_meta(content_type='html'):
    """
    Generate cache control meta tags based on content type.
    
    Usage: {% cache_control_meta 'html' %}
    """
    if content_type == 'html':
        cache_control = 'public, max-age=3600'
    elif content_type == 'api':
        cache_control = 'public, max-age=300'
    elif content_type == 'static':
        cache_control = 'public, max-age=31536000, immutable'
    else:
        cache_control = 'no-cache, no-store, must-revalidate'
    
    return mark_safe(f'<meta http-equiv="Cache-Control" content="{cache_control}">')


@register.simple_tag
def etag_meta(content):
    """
    Generate ETag meta tag from content.
    
    Usage: {% etag_meta page_content %}
    """
    if content:
        content_hash = hashlib.md5(str(content).encode()).hexdigest()
        etag = f'"{content_hash}"'
        return mark_safe(f'<meta name="etag" content="{etag}">')
    return ''


@register.simple_tag(takes_context=True)
def page_cache_key(context):
    """
    Generate cache key for current page.
    
    Usage: {% page_cache_key %}
    """
    request = context.get('request')
    if request:
        # Create cache key from path and query parameters
        cache_key_data = f"{request.path}:{request.GET.urlencode()}"
        cache_key = hashlib.md5(cache_key_data.encode()).hexdigest()
        return f"page:{cache_key}"
    return ''


@register.filter  
def cache_bust_url(url, version=None):
    """
    Add version parameter to URL for cache busting.
    
    Usage: {{ url|cache_bust_url:version }}
    """
    if not version:
        version = str(int(time.time()))
    
    return CacheBusting.add_version_to_url(url, version)


@register.simple_tag
def critical_css_inline():
    """
    Generate inline critical CSS for above-the-fold content.
    
    Usage: {% critical_css_inline %}
    """
    # This would typically contain critical CSS
    # For now, return a placeholder that indicates optimization
    critical_css = """
    /* Critical CSS - Above the fold optimization */
    body{font-family:-apple-system,BlinkMacSystemFont,segoe ui,Roboto,sans-serif}
    .hero{min-height:50vh;display:flex;align-items:center}
    .nav{position:sticky;top:0;z-index:100}
    """
    return mark_safe(f'<style>{critical_css}</style>')


@register.simple_tag
def cache_warming_script():
    """
    Generate JavaScript for cache warming critical resources.
    
    Usage: {% cache_warming_script %}
    """
    script = """
    <script>
    // Cache warming for critical resources
    (function() {
        const criticalResources = [
            '{% cached_static "css/styles.css" %}',
            '{% cached_static "js/mobile-nav.js" %}',
            '{% cached_static "images/sabor-con-flow-logo.webp" %}'
        ];
        
        // Preload critical resources
        criticalResources.forEach(function(url) {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = url;
            document.head.appendChild(link);
        });
    })();
    </script>
    """
    return mark_safe(script)


@register.simple_tag
def service_worker_cache_version():
    """
    Get cache version for service worker cache busting.
    
    Usage: {% service_worker_cache_version %}
    """
    # Combine Django cache version with timestamp for service worker
    django_version = getattr(settings, 'CACHE_VERSION', 1)
    timestamp = int(time.time() / 3600)  # Change every hour
    return f"v{django_version}_{timestamp}"