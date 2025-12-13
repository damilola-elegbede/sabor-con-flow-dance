"""
Vite integration template tags for Django
Reads the Vite manifest to get hashed asset URLs for cache-busting
"""

import json
from pathlib import Path
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

# Cache the manifest in memory
_manifest_cache = None


def get_manifest():
    """Load and cache the Vite manifest."""
    global _manifest_cache

    if _manifest_cache is not None and not settings.DEBUG:
        return _manifest_cache

    # Check multiple locations for the manifest
    # 1. Source location (during development/build)
    # 2. Non-hidden copy (collectstatic ignores hidden dirs like .vite/)
    # 3. Collected static files location (production on Vercel)
    possible_paths = [
        Path(settings.BASE_DIR) / 'static' / 'dist' / '.vite' / 'manifest.json',
        Path(settings.BASE_DIR) / 'static' / 'dist' / 'vite-manifest' / 'manifest.json',
        Path(settings.BASE_DIR) / 'staticfiles' / 'dist' / 'vite-manifest' / 'manifest.json',
        Path(settings.BASE_DIR) / 'staticfiles' / 'dist' / '.vite' / 'manifest.json',
    ]

    manifest_path = None
    for path in possible_paths:
        if path.exists():
            manifest_path = path
            break

    if manifest_path is None:
        if settings.DEBUG:
            return {}
        raise FileNotFoundError(
            f"Vite manifest not found. Searched: {[str(p) for p in possible_paths]}"
        )

    with open(manifest_path, 'r') as f:
        _manifest_cache = json.load(f)

    return _manifest_cache


@register.simple_tag
def vite_asset(entry_name):
    """
    Get the URL for a Vite-processed asset.

    Usage: {% vite_asset 'static/js/app.js' %}
    Returns: /static/dist/js/main-abc123.js
    """
    if settings.DEBUG:
        # In development, serve files directly (no Vite build)
        return f"/static/{entry_name.replace('static/', '')}"

    manifest = get_manifest()

    if entry_name not in manifest:
        raise KeyError(f"Asset '{entry_name}' not found in Vite manifest")

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
        # In development, serve CSS directly
        return mark_safe('<link rel="stylesheet" href="/static/css/main.css">')

    manifest = get_manifest()

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

    return mark_safe('\n'.join(links))


@register.simple_tag
def vite_js(entry_name):
    """
    Get JS script tag for a Vite entry point.

    Usage: {% vite_js 'static/js/app.js' %}
    Returns: <script type="module" src="/static/dist/js/main-abc123.js"></script>
    """
    if settings.DEBUG:
        # In development, no bundled JS - inline scripts handle functionality
        return ''

    manifest = get_manifest()

    if entry_name not in manifest:
        raise KeyError(f"Entry '{entry_name}' not found in Vite manifest")

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

    if entry_name not in manifest:
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
