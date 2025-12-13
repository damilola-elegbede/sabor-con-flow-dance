"""
Vite integration template tags for Django
Reads the Vite manifest to get hashed asset URLs for cache-busting
"""

import json
import logging
from pathlib import Path
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()
logger = logging.getLogger(__name__)

# Cache the manifest in memory
_manifest_cache = None
_manifest_loaded = False


def get_manifest():
    """Load and cache the Vite manifest."""
    global _manifest_cache, _manifest_loaded

    if _manifest_loaded and not settings.DEBUG:
        return _manifest_cache or {}

    # In production on Vercel, try the generated Python module first
    try:
        from core.vite_manifest_data import MANIFEST
        _manifest_cache = MANIFEST
        _manifest_loaded = True
        return _manifest_cache
    except ImportError:
        pass  # Fall through to file-based lookup

    # Check multiple locations for the manifest
    possible_paths = [
        Path(settings.BASE_DIR) / 'static' / 'dist' / '.vite' / 'manifest.json',
        Path(settings.BASE_DIR) / 'static' / 'dist' / 'vite-manifest' / 'manifest.json',
        Path(settings.BASE_DIR) / 'staticfiles' / 'dist' / 'vite-manifest' / 'manifest.json',
        Path(settings.BASE_DIR) / 'staticfiles' / 'dist' / '.vite' / 'manifest.json',
    ]

    for path in possible_paths:
        if path.exists():
            try:
                with open(path, 'r') as f:
                    _manifest_cache = json.load(f)
                    _manifest_loaded = True
                    return _manifest_cache
            except (IOError, json.JSONDecodeError) as e:
                logger.warning(f"Failed to load manifest from {path}: {e}")

    # Manifest not found - log warning and return empty dict
    # This allows the site to work with fallback CSS instead of crashing
    _manifest_loaded = True
    _manifest_cache = None
    if not settings.DEBUG:
        logger.warning(
            f"Vite manifest not found. Searched: {[str(p) for p in possible_paths]}. "
            "Using fallback CSS."
        )
    return {}


@register.simple_tag
def vite_asset(entry_name):
    """
    Get the URL for a Vite-processed asset.

    Usage: {% vite_asset 'static/js/app.js' %}
    Returns: /static/dist/js/main-abc123.js
    """
    if settings.DEBUG:
        return f"/static/{entry_name.replace('static/', '')}"

    manifest = get_manifest()

    if entry_name not in manifest:
        # Fallback to development path
        return f"/static/{entry_name.replace('static/', '')}"

    asset_info = manifest[entry_name]
    return f"/static/dist/{asset_info['file']}"


@register.simple_tag
def vite_css(entry_name):
    """
    Get CSS link tags for a Vite entry point.

    Usage: {% vite_css 'static/js/app.js' %}
    Returns: <link rel="stylesheet" href="/static/dist/css/style-abc123.css">
    """
    if settings.DEBUG:
        return mark_safe('<link rel="stylesheet" href="/static/css/main.css">')

    manifest = get_manifest()

    # If no manifest, fall back to serving main.css directly
    if not manifest:
        return mark_safe('<link rel="stylesheet" href="/static/css/main.css">')

    links = []

    # Check if entry has embedded CSS files
    if entry_name in manifest:
        asset_info = manifest[entry_name]
        css_files = asset_info.get('css', [])
        for css_file in css_files:
            links.append(f'<link rel="stylesheet" href="/static/dist/{css_file}">')

    # Also check for standalone style.css entry (Vite creates this when cssCodeSplit: false)
    if 'style.css' in manifest:
        style_info = manifest['style.css']
        links.append(f'<link rel="stylesheet" href="/static/dist/{style_info["file"]}">')

    # If nothing found in manifest, use fallback
    if not links:
        return mark_safe('<link rel="stylesheet" href="/static/css/main.css">')

    return mark_safe('\n'.join(links))


@register.simple_tag
def vite_js(entry_name):
    """
    Get JS script tag for a Vite entry point.

    Usage: {% vite_js 'static/js/app.js' %}
    Returns: <script type="module" src="/static/dist/js/main-abc123.js"></script>
    """
    if settings.DEBUG:
        return ''

    manifest = get_manifest()

    if not manifest or entry_name not in manifest:
        # No bundled JS available - return empty (inline scripts handle functionality)
        return ''

    asset_info = manifest[entry_name]
    return mark_safe(
        f'<script type="module" src="/static/dist/{asset_info["file"]}"></script>'
    )


@register.simple_tag
def vite_preload(entry_name):
    """
    Get preload link tags for a Vite entry point's critical assets.

    Usage: {% vite_preload 'static/js/app.js' %}
    Returns: <link rel="modulepreload" href="/static/dist/js/main-abc123.js">
    """
    if settings.DEBUG:
        return ''

    manifest = get_manifest()

    if not manifest or entry_name not in manifest:
        return ''

    asset_info = manifest[entry_name]
    preloads = []

    # Preload the main JS file
    preloads.append(
        f'<link rel="modulepreload" href="/static/dist/{asset_info["file"]}">'
    )

    # Preload CSS files
    for css_file in asset_info.get('css', []):
        preloads.append(
            f'<link rel="preload" href="/static/dist/{css_file}" as="style">'
        )

    return mark_safe('\n'.join(preloads))
