"""
Critical CSS Extraction and Optimization Utility
SPEC_06 Group A Task 2

This module provides tools for extracting critical CSS, analyzing above-fold content,
and optimizing CSS delivery for sub-1s first paint performance.
"""

import os
import re
import json
import gzip
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from django.template.loader import render_to_string
import csscompressor


class CriticalCSSExtractor:
    """
    Advanced critical CSS extraction and optimization system
    """
    
    def __init__(self):
        self.static_dir = Path(settings.STATICFILES_DIRS[0]) if settings.STATICFILES_DIRS else Path(settings.BASE_DIR) / 'static'
        self.css_dir = self.static_dir / 'css'
        self.critical_css_path = self.css_dir / 'critical.css'
        
        # Critical selectors that should always be included
        self.critical_selectors = {
            # Base elements
            'html', 'body', '*', '::before', '::after',
            
            # CSS Variables
            ':root',
            
            # Critical layout
            '.container', '.navbar', '.navbar-container', '.navbar-brand', '.navbar-menu', '.navbar-item',
            '.navbar-toggle', '.hamburger-line',
            
            # Hero section (above-fold)
            '.hero-section', '.hero-video-container', '.hero-video', '.hero-overlay',
            '.hero-content', '.hero-text', '.hero-headline', '.hero-subheadline',
            '.hero-trust', '.trust-badge', '.hero-cta',
            '.btn-hero-primary', '.btn-hero-secondary',
            
            # Accessibility
            '.skip-link', '.sr-only',
            
            # Critical utilities
            '.above-fold', '.text-center', 'main',
            
            # Font loading optimization
            '.font-loading', '.font-loaded'
        }
        
        # CSS files that contain critical styles
        self.critical_files = [
            'critical.css',  # Our pre-extracted critical CSS
            'styles.css',    # May contain additional critical styles
            'hero.css',      # Hero section styles
            'navigation.css' # Navigation styles
        ]
        
        # Performance budgets (bytes)
        self.critical_css_budget = 14000  # 14KB for critical CSS
        self.total_css_budget = 50000     # 50KB total CSS budget
    
    def extract_critical_css(self, page_template: str = 'home.html') -> str:
        """
        Extract critical CSS for a specific page template
        
        Args:
            page_template: Template name to analyze for critical CSS
            
        Returns:
            Minified critical CSS string
        """
        cache_key = f'critical_css_{page_template}'
        cached_css = cache.get(cache_key)
        
        if cached_css and not settings.DEBUG:
            return cached_css
        
        critical_css_parts = []
        
        # 1. Load pre-extracted critical CSS
        if self.critical_css_path.exists():
            with open(self.critical_css_path, 'r', encoding='utf-8') as f:
                critical_css_parts.append(f.read())
        
        # 2. Extract additional critical styles from other CSS files
        for css_file in self.critical_files:
            css_path = self.css_dir / css_file
            if css_path.exists() and css_file != 'critical.css':
                additional_critical = self._extract_from_file(css_path, page_template)
                if additional_critical:
                    critical_css_parts.append(additional_critical)
        
        # 3. Combine and optimize
        combined_css = '\n'.join(critical_css_parts)
        optimized_css = self._optimize_css(combined_css)
        
        # 4. Validate against performance budget
        css_size = len(optimized_css.encode('utf-8'))
        if css_size > self.critical_css_budget:
            print(f"Warning: Critical CSS ({css_size} bytes) exceeds budget ({self.critical_css_budget} bytes)")
            optimized_css = self._trim_to_budget(optimized_css)
        
        # Cache the result
        cache.set(cache_key, optimized_css, 3600)  # Cache for 1 hour
        
        return optimized_css
    
    def _extract_from_file(self, css_path: Path, template: str) -> str:
        """Extract critical CSS rules from a specific file"""
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        critical_rules = []
        
        # Extract rules that match critical selectors
        for selector in self.critical_selectors:
            pattern = rf'{re.escape(selector)}\s*{{[^}}]*}}'
            matches = re.findall(pattern, css_content, re.MULTILINE | re.DOTALL)
            critical_rules.extend(matches)
        
        # Extract media queries for responsive design
        media_queries = re.findall(r'@media[^{]*{[^{}]*{[^}]*}[^}]*}', css_content, re.MULTILINE | re.DOTALL)
        critical_rules.extend(media_queries)
        
        return '\n'.join(critical_rules)
    
    def _optimize_css(self, css: str) -> str:
        """Optimize CSS for critical delivery"""
        # Remove comments (except special ones)
        css = re.sub(r'/\*(?!\!)[^*]*\*+(?:[^/*][^*]*\*+)*/', '', css)
        
        # Remove unnecessary whitespace
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r';\s*}', '}', css)
        css = re.sub(r'{\s*', '{', css)
        css = re.sub(r'}\s*', '}', css)
        css = re.sub(r':\s*', ':', css)
        css = re.sub(r';\s*', ';', css)
        
        # Use CSS compressor for further optimization
        try:
            css = csscompressor.compress(css)
        except:
            pass  # Fallback to manual optimization if compressor fails
        
        return css.strip()
    
    def _trim_to_budget(self, css: str) -> str:
        """Trim CSS to fit within performance budget"""
        target_size = self.critical_css_budget
        current_size = len(css.encode('utf-8'))
        
        if current_size <= target_size:
            return css
        
        # Priority order for CSS rules (keep these first)
        priority_patterns = [
            r':root\s*{[^}]*}',  # CSS variables
            r'html\s*{[^}]*}',   # HTML element
            r'body\s*{[^}]*}',   # Body element
            r'\*\s*{[^}]*}',     # Universal selector
            r'\.navbar[^{]*{[^}]*}',  # Navigation
            r'\.hero-[^{]*{[^}]*}',   # Hero section
            r'\.container[^{]*{[^}]*}', # Layout container
        ]
        
        # Extract priority rules first
        priority_css = []
        remaining_css = css
        
        for pattern in priority_patterns:
            matches = re.findall(pattern, remaining_css, re.MULTILINE | re.DOTALL)
            priority_css.extend(matches)
            remaining_css = re.sub(pattern, '', remaining_css, flags=re.MULTILINE | re.DOTALL)
        
        # Add priority CSS first
        result = '\n'.join(priority_css)
        
        # Add remaining CSS until budget is reached
        remaining_rules = re.findall(r'[^{}]*{[^}]*}', remaining_css)
        for rule in remaining_rules:
            test_css = result + '\n' + rule
            if len(test_css.encode('utf-8')) > target_size:
                break
            result = test_css
        
        return result
    
    def generate_async_css_loader(self, css_files: List[str]) -> str:
        """Generate JavaScript code for async CSS loading"""
        loader_template = """
// Async CSS Loader - SPEC_06 Group A Task 2
(function() {
    var cssFiles = {css_files};
    var loadedFiles = [];
    
    function loadCSS(href, before, media, attributes) {{
        var doc = window.document;
        var ss = doc.createElement("link");
        var ref;
        if (before) {{
            ref = before;
        }} else {{
            var refs = (doc.body || doc.getElementsByTagName("head")[0]).childNodes;
            ref = refs[refs.length - 1];
        }}
        
        var sheets = doc.styleSheets;
        if (attributes) {{
            for (var key in attributes) {{
                if (attributes.hasOwnProperty(key)) {{
                    ss.setAttribute(key, attributes[key]);
                }}
            }}
        }}
        
        ss.rel = "stylesheet";
        ss.href = href;
        ss.media = "only x";
        
        var startTime = performance.now();
        
        function ready(cb) {{
            if (doc.body) return cb();
            setTimeout(function() {{
                ready(cb);
            }});
        }}
        
        ready(function() {{
            ref.parentNode.insertBefore(ss, (before ? ref : ref.nextSibling));
        }});
        
        var onloadcssdefined = function(cb) {{
            var resolvedHref = ss.href;
            var i = sheets.length;
            while (i--) {{
                if (sheets[i].href === resolvedHref) {{
                    return cb();
                }}
            }}
            setTimeout(function() {{
                onloadcssdefined(cb);
            }});
        }};
        
        function loadCB() {{
            if (ss.addEventListener) {{
                ss.removeEventListener("load", loadCB);
            }}
            ss.media = media || "all";
            
            var loadTime = performance.now() - startTime;
            console.log('CSS loaded:', href, 'in', loadTime + 'ms');
            
            // Track performance
            if (window.performanceAnalytics) {{
                window.performanceAnalytics.addCustomEvent('css_load', {{
                    url: href,
                    loadTime: loadTime
                }});
            }}
            
            loadedFiles.push(href);
            
            // Trigger custom event when all CSS is loaded
            if (loadedFiles.length === cssFiles.length) {{
                var event = new CustomEvent('allCSSLoaded', {{
                    detail: {{ loadedFiles: loadedFiles }}
                }});
                document.dispatchEvent(event);
            }}
        }}
        
        if (ss.addEventListener) {{
            ss.addEventListener("load", loadCB);
        }}
        ss.onloadcssdefined = onloadcssdefined;
        onloadcssdefined(loadCB);
        
        return ss;
    }}
    
    // Load CSS files with staggered timing for optimal performance
    cssFiles.forEach(function(file, index) {{
        setTimeout(function() {{
            loadCSS(file.url, null, 'all', file.attributes || {{}});
        }}, index * 50); // Stagger by 50ms
    }});
}})();
"""
        
        js_css_files = json.dumps([
            {
                'url': f'/static/css/{file}',
                'attributes': {'importance': 'low' if 'gallery' in file or 'spotify' in file else 'medium'}
            }
            for file in css_files
        ])
        
        return loader_template.format(css_files=js_css_files)
    
    def create_css_splitting_strategy(self) -> Dict[str, List[str]]:
        """
        Create a strategy for splitting CSS into critical and non-critical bundles
        
        Returns:
            Dictionary with CSS file groupings
        """
        strategy = {
            'critical': [
                'critical.css'  # Our extracted critical CSS
            ],
            'high_priority': [
                'navigation.css',  # Loaded async but high priority
                'hero.css'         # Additional hero styles
            ],
            'medium_priority': [
                'styles.css',      # Main stylesheet
                'forms.css',       # Form styles
                'pricing.css'      # Pricing page styles
            ],
            'low_priority': [
                'gallery.css',     # Gallery page
                'testimonials.css', # Testimonials
                'instructors.css', # Instructors page
                'schedule.css',    # Schedule page
                'spotify-playlists.css', # Spotify integration
                'whatsapp.css',    # WhatsApp chat
                'social_links.css', # Social links
                'google-maps.css', # Maps
                'video-player.css' # Video player
            ]
        }
        
        return strategy
    
    def analyze_css_performance(self) -> Dict[str, any]:
        """Analyze CSS performance metrics"""
        analysis = {
            'critical_css_size': 0,
            'total_css_size': 0,
            'file_count': 0,
            'files': {},
            'recommendations': []
        }
        
        # Analyze each CSS file
        for css_file in self.css_dir.glob('*.css'):
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
                size = len(content.encode('utf-8'))
                
                analysis['files'][css_file.name] = {
                    'size': size,
                    'size_human': self._format_bytes(size),
                    'rules_count': len(re.findall(r'{[^}]*}', content)),
                    'selectors_count': len(re.findall(r'[^{}]+{', content))
                }
                
                analysis['total_css_size'] += size
                analysis['file_count'] += 1
                
                if css_file.name == 'critical.css':
                    analysis['critical_css_size'] = size
        
        # Generate recommendations
        if analysis['critical_css_size'] > self.critical_css_budget:
            analysis['recommendations'].append(
                f"Critical CSS ({self._format_bytes(analysis['critical_css_size'])}) "
                f"exceeds budget ({self._format_bytes(self.critical_css_budget)})"
            )
        
        if analysis['total_css_size'] > self.total_css_budget:
            analysis['recommendations'].append(
                f"Total CSS ({self._format_bytes(analysis['total_css_size'])}) "
                f"exceeds budget ({self._format_bytes(self.total_css_budget)})"
            )
        
        if analysis['file_count'] > 10:
            analysis['recommendations'].append(
                f"Consider consolidating CSS files ({analysis['file_count']} files)"
            )
        
        return analysis
    
    def _format_bytes(self, bytes_count: int) -> str:
        """Format bytes in human readable format"""
        for unit in ['B', 'KB', 'MB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} GB"
    
    def generate_performance_measurement_script(self) -> str:
        """Generate JavaScript for measuring CSS performance"""
        return """
// CSS Performance Measurement - SPEC_06 Group A Task 2
(function() {
    var cssMetrics = {
        startTime: performance.now(),
        criticalCSSLoaded: false,
        allCSSLoaded: false,
        firstPaint: null,
        firstContentfulPaint: null,
        largestContentfulPaint: null
    };
    
    // Measure critical CSS load time
    function markCriticalCSSLoaded() {
        cssMetrics.criticalCSSLoaded = true;
        cssMetrics.criticalLoadTime = performance.now() - cssMetrics.startTime;
        
        console.log('Critical CSS loaded in:', cssMetrics.criticalLoadTime + 'ms');
        
        // Track with analytics
        if (window.performanceAnalytics) {
            window.performanceAnalytics.addCustomEvent('critical_css_loaded', {
                loadTime: cssMetrics.criticalLoadTime
            });
        }
    }
    
    // Listen for all CSS loaded event
    document.addEventListener('allCSSLoaded', function(e) {
        cssMetrics.allCSSLoaded = true;
        cssMetrics.totalLoadTime = performance.now() - cssMetrics.startTime;
        
        console.log('All CSS loaded in:', cssMetrics.totalLoadTime + 'ms');
        console.log('Loaded files:', e.detail.loadedFiles);
        
        // Track with analytics
        if (window.performanceAnalytics) {
            window.performanceAnalytics.addCustomEvent('all_css_loaded', {
                loadTime: cssMetrics.totalLoadTime,
                fileCount: e.detail.loadedFiles.length
            });
        }
    });
    
    // Measure Core Web Vitals
    if ('PerformanceObserver' in window) {
        // First Paint and First Contentful Paint
        var paintObserver = new PerformanceObserver(function(list) {
            list.getEntries().forEach(function(entry) {
                if (entry.name === 'first-paint') {
                    cssMetrics.firstPaint = entry.startTime;
                } else if (entry.name === 'first-contentful-paint') {
                    cssMetrics.firstContentfulPaint = entry.startTime;
                }
            });
        });
        paintObserver.observe({entryTypes: ['paint']});
        
        // Largest Contentful Paint
        var lcpObserver = new PerformanceObserver(function(list) {
            var entries = list.getEntries();
            var lastEntry = entries[entries.length - 1];
            cssMetrics.largestContentfulPaint = lastEntry.startTime;
        });
        lcpObserver.observe({entryTypes: ['largest-contentful-paint']});
    }
    
    // Mark critical CSS as loaded when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', markCriticalCSSLoaded);
    } else {
        markCriticalCSSLoaded();
    }
    
    // Expose metrics globally for debugging
    window.cssPerformanceMetrics = cssMetrics;
    
    // Report metrics after page load
    window.addEventListener('load', function() {
        setTimeout(function() {
            var report = {
                criticalCSS: cssMetrics.criticalLoadTime,
                totalCSS: cssMetrics.totalLoadTime,
                firstPaint: cssMetrics.firstPaint,
                firstContentfulPaint: cssMetrics.firstContentfulPaint,
                largestContentfulPaint: cssMetrics.largestContentfulPaint,
                target: 'Sub-1s first paint'
            };
            
            console.group('CSS Performance Report');
            console.table(report);
            console.groupEnd();
            
            // Check if we met our performance targets
            if (cssMetrics.firstContentfulPaint && cssMetrics.firstContentfulPaint < 1000) {
                console.log('✅ First Contentful Paint target met (<1s)');
            } else {
                console.warn('⚠️ First Contentful Paint target missed (>1s)');
            }
        }, 100);
    });
})();
"""


# Utility functions for template usage
def get_critical_css(page_template: str = 'home.html') -> str:
    """Template function to get critical CSS"""
    extractor = CriticalCSSExtractor()
    return extractor.extract_critical_css(page_template)


def get_async_css_loader(exclude_critical: bool = True) -> str:
    """Template function to get async CSS loader"""
    extractor = CriticalCSSExtractor()
    strategy = extractor.create_css_splitting_strategy()
    
    # Get non-critical CSS files
    css_files = []
    if not exclude_critical:
        css_files.extend(strategy['critical'])
    css_files.extend(strategy['high_priority'])
    css_files.extend(strategy['medium_priority'])
    css_files.extend(strategy['low_priority'])
    
    return extractor.generate_async_css_loader(css_files)


def get_performance_script() -> str:
    """Template function to get performance measurement script"""
    extractor = CriticalCSSExtractor()
    return extractor.generate_performance_measurement_script()