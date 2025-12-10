"""
Template tags for critical CSS optimization
SPEC_06 Group A Task 2
"""

from django import template
from django.utils.safestring import mark_safe
from django.conf import settings
from pathlib import Path
import os

register = template.Library()


@register.simple_tag
def get_critical_css(page_name='home'):
    """
    Get critical CSS content for a specific page
    
    Args:
        page_name: Name of the page template (default: 'home')
        
    Returns:
        Critical CSS as safe HTML string
    """
    try:
        # Path to critical CSS file
        static_dir = Path(settings.STATICFILES_DIRS[0]) if settings.STATICFILES_DIRS else Path(settings.BASE_DIR) / 'static'
        critical_css_path = static_dir / 'css' / 'critical.css'
        
        if critical_css_path.exists():
            with open(critical_css_path, 'r', encoding='utf-8') as f:
                critical_css = f.read()
                
            # Add page-specific optimizations
            if page_name == 'home':
                # For home page, ensure hero styles are prioritized
                critical_css += '\n/* Home page optimizations */\n.hero-section { will-change: transform; }'
            elif page_name == 'pricing':
                # For pricing page, add pricing-specific styles
                critical_css += '\n/* Pricing page optimizations */\n.pricing-section { contain: layout; }'
            
            return mark_safe(critical_css)
    except Exception as e:
        if settings.DEBUG:
            return mark_safe(f'/* Critical CSS loading error: {str(e)} */')
    
    # Fallback critical CSS
    return mark_safe("""
    /* Fallback Critical CSS */
    :root {
        --color-gold: #C7B375;
        --color-black: #000000;
        --color-white: #FFFFFF;
        --font-heading: 'Playfair Display', serif;
        --font-body: 'Inter', sans-serif;
    }
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: var(--font-body); margin: 0; }
    .navbar { background: var(--color-black); position: sticky; top: 0; z-index: 1000; }
    .hero-section { min-height: 100vh; background: var(--color-black); }
    """)


@register.simple_tag
def get_async_css_loader():
    """
    Generate JavaScript for async CSS loading
    
    Returns:
        JavaScript code as safe HTML string
    """
    css_files = [
        {'url': '/static/css/navigation.css', 'priority': 'high'},
        {'url': '/static/css/hero.css', 'priority': 'high'},
        {'url': '/static/css/styles.css', 'priority': 'medium'},
        {'url': '/static/css/forms.css', 'priority': 'medium'},
        {'url': '/static/css/pricing.css', 'priority': 'medium'},
        {'url': '/static/css/whatsapp.css', 'priority': 'low'},
        {'url': '/static/css/social_links.css', 'priority': 'low'},
        {'url': '/static/css/gallery.css', 'priority': 'low'},
        {'url': '/static/css/testimonials.css', 'priority': 'low'},
        {'url': '/static/css/instructors.css', 'priority': 'low'},
        {'url': '/static/css/schedule.css', 'priority': 'low'},
        {'url': '/static/css/spotify-playlists.css', 'priority': 'low'},
        {'url': '/static/css/google-maps.css', 'priority': 'low'},
        {'url': '/static/css/video-player.css', 'priority': 'low'}
    ]
    
    js_code = """
// Async CSS Loader - SPEC_06 Group A Task 2
(function() {
    var cssFiles = """ + str(css_files).replace("'", '"') + """;
    var loadedCount = 0;
    
    function loadCSS(file) {
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = file.url;
        link.media = 'all';
        
        if (file.priority === 'high') {
            link.setAttribute('importance', 'high');
        } else if (file.priority === 'low') {
            link.setAttribute('importance', 'low');
        }
        
        link.onload = function() {
            loadedCount++;
            console.log('CSS loaded:', file.url, 'Priority:', file.priority);
            
            if (loadedCount === cssFiles.length) {
                document.dispatchEvent(new CustomEvent('allCSSLoaded'));
            }
        };
        
        document.head.appendChild(link);
    }
    
    // Load high priority CSS immediately
    cssFiles.filter(f => f.priority === 'high').forEach(loadCSS);
    
    // Load medium priority after 100ms
    setTimeout(() => {
        cssFiles.filter(f => f.priority === 'medium').forEach(loadCSS);
    }, 100);
    
    // Load low priority after 500ms
    setTimeout(() => {
        cssFiles.filter(f => f.priority === 'low').forEach(loadCSS);
    }, 500);
})();
"""
    
    return mark_safe(js_code)


@register.simple_tag 
def get_performance_script():
    """
    Generate performance monitoring script
    
    Returns:
        JavaScript code for performance monitoring
    """
    js_code = """
// Performance Monitoring - SPEC_06 Group A Task 2
(function() {
    var startTime = performance.now();
    var metrics = {};
    
    // Monitor Core Web Vitals
    if ('PerformanceObserver' in window) {
        // First Paint and First Contentful Paint
        var paintObserver = new PerformanceObserver(function(list) {
            list.getEntries().forEach(function(entry) {
                metrics[entry.name.replace('-', '_')] = entry.startTime;
                console.log('🎨 ' + entry.name + ':', entry.startTime + 'ms');
                
                if (entry.name === 'first-contentful-paint') {
                    if (entry.startTime < 1000) {
                        console.log('✅ Sub-1s first paint achieved!');
                    } else {
                        console.warn('⚠️ First paint target missed');
                    }
                }
            });
        });
        paintObserver.observe({entryTypes: ['paint']});
        
        // Largest Contentful Paint
        var lcpObserver = new PerformanceObserver(function(list) {
            var entries = list.getEntries();
            var lastEntry = entries[entries.length - 1];
            metrics.largest_contentful_paint = lastEntry.startTime;
            console.log('🖼️ Largest Contentful Paint:', lastEntry.startTime + 'ms');
        });
        lcpObserver.observe({entryTypes: ['largest-contentful-paint']});
    }
    
    // Report when all CSS is loaded
    document.addEventListener('allCSSLoaded', function() {
        var totalTime = performance.now() - startTime;
        console.log('🎯 All CSS loaded in:', totalTime + 'ms');
        
        // Generate report
        setTimeout(function() {
            console.group('📊 CSS Performance Report');
            console.table(metrics);
            console.log('Total CSS Load Time:', totalTime + 'ms');
            console.groupEnd();
        }, 100);
    });
    
    // Expose metrics globally
    window.cssPerformanceMetrics = metrics;
})();
"""
    
    return mark_safe(js_code)


@register.simple_tag
def critical_css_size():
    """
    Get the size of critical CSS file for monitoring
    
    Returns:
        Size in bytes
    """
    try:
        static_dir = Path(settings.STATICFILES_DIRS[0]) if settings.STATICFILES_DIRS else Path(settings.BASE_DIR) / 'static'
        critical_css_path = static_dir / 'css' / 'critical.css'
        
        if critical_css_path.exists():
            return critical_css_path.stat().st_size
    except:
        pass
    
    return 0


@register.simple_tag
def css_budget_check():
    """
    Check if CSS files are within performance budget
    
    Returns:
        Budget status information
    """
    try:
        static_dir = Path(settings.STATICFILES_DIRS[0]) if settings.STATICFILES_DIRS else Path(settings.BASE_DIR) / 'static'
        css_dir = static_dir / 'css'
        
        total_size = 0
        critical_size = 0
        
        for css_file in css_dir.glob('*.css'):
            size = css_file.stat().st_size
            total_size += size
            
            if css_file.name == 'critical.css':
                critical_size = size
        
        # Performance budgets (bytes)
        critical_budget = 14000  # 14KB
        total_budget = 50000     # 50KB
        
        return {
            'critical_size': critical_size,
            'critical_budget': critical_budget,
            'critical_within_budget': critical_size <= critical_budget,
            'total_size': total_size,
            'total_budget': total_budget,
            'total_within_budget': total_size <= total_budget
        }
    except:
        return {}