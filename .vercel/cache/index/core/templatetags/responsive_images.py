"""
Template tags for responsive image handling with WebP support and lazy loading.
"""

import os
from pathlib import Path
from urllib.parse import urljoin
from typing import Dict, List, Optional

from django import template
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def responsive_image(image_path: str, alt_text: str = '', css_class: str = '', 
                    lazy: bool = True, placeholder: bool = True, 
                    sizes: str = '100vw') -> str:
    """
    Generate responsive image with WebP support, lazy loading, and blur placeholder.
    
    Usage:
        {% responsive_image 'images/hero.jpg' 'Hero image' 'hero-img' %}
        {% responsive_image 'images/logo.png' 'Logo' lazy=False %}
    """
    
    # Get base name and extension
    base_name = Path(image_path).stem
    image_dir = Path(image_path).parent
    
    # Generate srcset for different sizes
    webp_srcset = _generate_srcset(image_dir, base_name, 'webp')
    jpeg_srcset = _generate_srcset(image_dir, base_name, 'jpg')
    
    # Generate placeholder if requested
    placeholder_src = ''
    if placeholder and lazy:
        placeholder_src = _get_placeholder_src(image_dir, base_name)
    
    # Build CSS classes
    classes = ['responsive-image']
    if css_class:
        classes.append(css_class)
    if lazy:
        classes.append('lazy-load')
    
    # Build the picture element
    picture_html = f'<picture class="{" ".join(classes)}">'
    
    # WebP source
    if webp_srcset:
        picture_html += f'''
            <source srcset="{webp_srcset}" 
                    type="image/webp" 
                    sizes="{sizes}">'''
    
    # JPEG/PNG fallback source
    if jpeg_srcset:
        picture_html += f'''
            <source srcset="{jpeg_srcset}" 
                    type="image/jpeg" 
                    sizes="{sizes}">'''
    
    # Main img element
    img_attributes = {
        'alt': alt_text,
        'class': 'responsive-img',
        'width': '100%',
        'height': 'auto'
    }
    
    if lazy:
        img_attributes['loading'] = 'lazy'
        img_attributes['decoding'] = 'async'
        
        if placeholder_src:
            img_attributes['src'] = placeholder_src
            img_attributes['data-src'] = static(image_path)
        else:
            img_attributes['data-src'] = static(image_path)
            img_attributes['src'] = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMSIgaGVpZ2h0PSIxIiB2aWV3Qm94PSIwIDAgMSAxIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxIiBoZWlnaHQ9IjEiIGZpbGw9IiNGNUY1RjUiLz48L3N2Zz4='
    else:
        img_attributes['src'] = static(image_path)
    
    # Build img tag
    img_attrs = ' '.join([f'{k}="{v}"' for k, v in img_attributes.items()])
    picture_html += f'<img {img_attrs}>'
    picture_html += '</picture>'
    
    return mark_safe(picture_html)


@register.simple_tag
def responsive_bg_image(image_path: str, css_class: str = '', 
                       breakpoints: Optional[Dict[str, str]] = None) -> str:
    """
    Generate CSS for responsive background images with WebP support.
    
    Usage:
        {% responsive_bg_image 'images/hero.jpg' 'hero-bg' %}
    """
    
    base_name = Path(image_path).stem
    image_dir = Path(image_path).parent
    
    # Default breakpoints if none provided
    if not breakpoints:
        breakpoints = {
            '320': '320w',
            '640': '640w', 
            '1024': '1024w',
            '1920': '1920w'
        }
    
    css_rules = []
    
    # Generate CSS for each breakpoint
    for breakpoint, size in breakpoints.items():
        webp_url = _get_optimized_url(image_dir, base_name, size, 'webp')
        jpeg_url = _get_optimized_url(image_dir, base_name, size, 'jpg')
        
        if webp_url and jpeg_url:
            css_rules.append(f'''
                @media (max-width: {breakpoint}px) {{
                    .{css_class} {{
                        background-image: url('{jpeg_url}');
                    }}
                    .webp .{css_class} {{
                        background-image: url('{webp_url}');
                    }}
                }}
            ''')
    
    return mark_safe(''.join(css_rules))


@register.simple_tag
def optimized_video(video_path: str, css_class: str = '', autoplay: bool = False,
                   loop: bool = False, muted: bool = False, controls: bool = True,
                   poster: str = '') -> str:
    """
    Generate optimized video tag with fallbacks and proper attributes.
    
    Usage:
        {% optimized_video 'videos/hero.mp4' 'hero-video' autoplay=True loop=True muted=True %}
    """
    
    base_name = Path(video_path).stem
    video_dir = Path(video_path).parent
    
    # Check for optimized version
    optimized_path = video_dir / 'optimized' / f'{base_name}_optimized.mp4'
    video_src = static(str(optimized_path)) if _file_exists(optimized_path) else static(video_path)
    
    # Generate poster if not provided
    if not poster:
        poster_path = video_dir / 'optimized' / f'{base_name}_poster.jpg'
        if _file_exists(poster_path):
            poster = static(str(poster_path))
    
    # Build video attributes
    video_attrs = {
        'class': f'optimized-video {css_class}'.strip(),
        'preload': 'metadata',
        'playsinline': True
    }
    
    if autoplay:
        video_attrs['autoplay'] = True
    if loop:
        video_attrs['loop'] = True
    if muted:
        video_attrs['muted'] = True
    if controls:
        video_attrs['controls'] = True
    if poster:
        video_attrs['poster'] = poster
    
    # Build video tag
    attrs_str = ' '.join([
        f'{k}="{v}"' if v is not True else k 
        for k, v in video_attrs.items()
    ])
    
    video_html = f'''
        <video {attrs_str}>
            <source src="{video_src}" type="video/mp4">
            <p>Your browser doesn't support HTML5 video. 
               <a href="{video_src}">Download the video</a> instead.</p>
        </video>
    '''
    
    return mark_safe(video_html)


@register.inclusion_tag('components/lazy_image.html')
def lazy_image(image_path: str, alt_text: str = '', css_class: str = '',
               aspect_ratio: str = '16/9') -> Dict:
    """
    Render a lazy-loaded image component with aspect ratio preservation.
    
    Usage:
        {% lazy_image 'images/gallery/photo1.jpg' 'Gallery photo' 'gallery-img' %}
    """
    
    base_name = Path(image_path).stem
    image_dir = Path(image_path).parent
    
    return {
        'image_path': image_path,
        'placeholder_src': _get_placeholder_src(image_dir, base_name),
        'webp_srcset': _generate_srcset(image_dir, base_name, 'webp'),
        'jpeg_srcset': _generate_srcset(image_dir, base_name, 'jpg'),
        'alt_text': alt_text,
        'css_class': css_class,
        'aspect_ratio': aspect_ratio
    }


def _generate_srcset(image_dir: Path, base_name: str, format: str) -> str:
    """Generate srcset string for responsive images."""
    
    sizes = [320, 640, 1024, 1920]
    srcset_parts = []
    
    for size in sizes:
        optimized_url = _get_optimized_url(image_dir, base_name, f'{size}w', format)
        if optimized_url:
            srcset_parts.append(f'{optimized_url} {size}w')
    
    return ', '.join(srcset_parts)


def _get_optimized_url(image_dir: Path, base_name: str, size: str, format: str) -> Optional[str]:
    """Get URL for optimized image if it exists."""
    
    optimized_path = image_dir / 'optimized' / f'{base_name}_{size}.{format}'
    
    if _file_exists(optimized_path):
        return static(str(optimized_path))
    
    return None


def _get_placeholder_src(image_dir: Path, base_name: str) -> str:
    """Get placeholder image source."""
    
    placeholder_path = image_dir / 'optimized' / f'{base_name}_placeholder.jpg'
    
    if _file_exists(placeholder_path):
        return static(str(placeholder_path))
    
    # Return base64 encoded 1x1 transparent GIF as fallback
    return 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'


def _file_exists(file_path: Path) -> bool:
    """Check if a static file exists."""
    try:
        # Convert to string and check if static file exists
        full_path = Path(settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT) / file_path
        return full_path.exists()
    except (IndexError, AttributeError):
        return False


@register.filter
def webp_support_check(value: str) -> str:
    """
    Generate JavaScript to check WebP support and add class to html element.
    
    Usage:
        {{ 'webp'|webp_support_check }}
    """
    
    js_code = '''
    <script>
    (function() {
        function supportsWebP(callback) {
            var webP = new Image();
            webP.onload = webP.onerror = function () {
                callback(webP.height == 2);
            };
            webP.src = "data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA";
        }
        
        supportsWebP(function(supported) {
            if (supported) {
                document.documentElement.classList.add('webp');
            } else {
                document.documentElement.classList.add('no-webp');
            }
        });
    })();
    </script>
    '''
    
    return mark_safe(js_code)


@register.simple_tag
def performance_hints() -> str:
    """
    Generate performance-related meta tags and preload hints.
    """
    
    hints = '''
    <!-- Performance hints -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="dns-prefetch" href="//fonts.googleapis.com">
    <meta name="format-detection" content="telephone=no">
    '''
    
    return mark_safe(hints)