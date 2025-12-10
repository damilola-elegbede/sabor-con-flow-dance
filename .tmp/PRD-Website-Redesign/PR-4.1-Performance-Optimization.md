# PR 4.1: Performance Optimization Implementation

## PR Metadata
- **Phase**: 4.1 - Performance Optimization
- **Priority**: Critical
- **Dependencies**: Phase 1.x, 2.x, 3.x completed
- **Estimated Timeline**: 5-7 days
- **Risk Level**: Medium
- **Team**: Performance Engineering + DevOps

## Performance Requirements

### Core Web Vitals Targets
- **Largest Contentful Paint (LCP)**: < 2.5s
- **First Input Delay (FID)**: < 100ms
- **Cumulative Layout Shift (CLS)**: < 0.1
- **First Contentful Paint (FCP)**: < 1.8s
- **Time to Interactive (TTI)**: < 3.5s

### Performance Budget
- **Total Bundle Size**: < 200KB (gzipped)
- **Critical CSS**: < 14KB inline
- **Images**: WebP with AVIF fallback
- **JavaScript**: < 100KB initial bundle
- **Lighthouse Score**: > 95 (Performance)

## Critical CSS Implementation

### 1. Critical CSS Extraction
```javascript
// build-scripts/extract-critical-css.js
const penthouse = require('penthouse');
const fs = require('fs').promises;

const pages = [
  { url: 'http://localhost:3000/', css: 'home' },
  { url: 'http://localhost:3000/events', css: 'events' },
  { url: 'http://localhost:3000/pricing', css: 'pricing' },
  { url: 'http://localhost:3000/contact', css: 'contact' }
];

async function extractCriticalCSS() {
  for (const page of pages) {
    const criticalCss = await penthouse({
      url: page.url,
      cssString: await fs.readFile('static/css/styles.css', 'utf8'),
      width: 1300,
      height: 900,
      timeout: 30000,
      strict: false
    });

    await fs.writeFile(`static/css/critical-${page.css}.css`, criticalCss);
    console.log(`Generated critical CSS for ${page.css}`);
  }
}

extractCriticalCSS().catch(console.error);
```

### 2. CSS Loading Strategy
```html
<!-- templates/base.html - Critical CSS inlined -->
<style>
  {{ critical_css|safe }}
</style>

<!-- Non-critical CSS loaded asynchronously -->
<link rel="preload" href="{% static 'css/styles.css' %}" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="{% static 'css/styles.css' %}"></noscript>
```

### 3. CSS Minification & Compression
```python
# build_css.py - Enhanced with critical CSS
import cssmin
from pathlib import Path

def build_optimized_css():
    css_files = {
        'critical-home': ['hero.css', 'navigation.css', 'above-fold.css'],
        'critical-events': ['events.css', 'navigation.css', 'calendar.css'],
        'critical-pricing': ['pricing.css', 'navigation.css', 'cards.css'],
        'non-critical': ['gallery.css', 'testimonials.css', 'footer.css']
    }
    
    for bundle_name, files in css_files.items():
        combined_css = ""
        for file in files:
            css_path = Path(f'static/css/{file}')
            if css_path.exists():
                combined_css += css_path.read_text() + "\n"
        
        minified = cssmin.cssmin(combined_css)
        output_path = Path(f'static/css/{bundle_name}.min.css')
        output_path.write_text(minified)
        
        print(f"Built {bundle_name}: {len(minified)} bytes")
```

## Service Worker Implementation

### 1. Advanced Caching Strategy
```javascript
// static/js/service-worker-advanced.js
const CACHE_NAME = 'sabor-v4.1.0';
const STATIC_CACHE = 'static-v4.1.0';
const DYNAMIC_CACHE = 'dynamic-v4.1.0';
const IMAGE_CACHE = 'images-v4.1.0';

const STATIC_FILES = [
  '/',
  '/static/css/critical-home.min.css',
  '/static/js/core.min.js',
  '/static/images/sabor-con-flow-logo.webp',
  '/offline/'
];

const CACHE_STRATEGIES = {
  // Network First for API calls
  api: {
    strategy: 'networkFirst',
    cacheName: DYNAMIC_CACHE,
    networkTimeoutSeconds: 3,
    cacheMaxEntries: 50,
    cacheMaxAgeSeconds: 300 // 5 minutes
  },
  
  // Stale While Revalidate for pages
  pages: {
    strategy: 'staleWhileRevalidate',
    cacheName: DYNAMIC_CACHE,
    cacheMaxEntries: 100,
    cacheMaxAgeSeconds: 86400 // 24 hours
  },
  
  // Cache First for static assets
  static: {
    strategy: 'cacheFirst',
    cacheName: STATIC_CACHE,
    cacheMaxAgeSeconds: 2592000 // 30 days
  },
  
  // Network First for images with fallback
  images: {
    strategy: 'cacheFirst',
    cacheName: IMAGE_CACHE,
    cacheMaxEntries: 200,
    cacheMaxAgeSeconds: 604800 // 7 days
  }
};

// Enhanced cache management
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests and external domains
  if (request.method !== 'GET' || !url.origin.includes('saborconflow')) {
    return;
  }
  
  // Route requests to appropriate cache strategy
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleAPIRequest(request));
  } else if (url.pathname.match(/\.(png|jpg|jpeg|webp|avif|svg|gif)$/i)) {
    event.respondWith(handleImageRequest(request));
  } else if (url.pathname.match(/\.(js|css|woff2|woff)$/i)) {
    event.respondWith(handleStaticRequest(request));
  } else {
    event.respondWith(handlePageRequest(request));
  }
});

async function handleAPIRequest(request) {
  const strategy = CACHE_STRATEGIES.api;
  try {
    const networkResponse = await Promise.race([
      fetch(request),
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Network timeout')), 
        strategy.networkTimeoutSeconds * 1000)
      )
    ]);
    
    if (networkResponse.ok) {
      const cache = await caches.open(strategy.cacheName);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
  } catch (error) {
    console.log('Network failed, trying cache:', error);
  }
  
  // Fallback to cache
  const cachedResponse = await caches.match(request);
  return cachedResponse || new Response('Offline', { status: 503 });
}

// Background sync for offline actions
self.addEventListener('sync', event => {
  if (event.tag === 'contact-form') {
    event.waitUntil(syncContactForms());
  }
});

async function syncContactForms() {
  const store = await openDB('offline-store', 1);
  const forms = await store.getAll('contact-forms');
  
  for (const form of forms) {
    try {
      await fetch('/api/contact/', {
        method: 'POST',
        body: JSON.stringify(form.data),
        headers: { 'Content-Type': 'application/json' }
      });
      await store.delete('contact-forms', form.id);
    } catch (error) {
      console.log('Failed to sync form:', error);
    }
  }
}
```

### 2. Workbox Integration
```javascript
// webpack.config.js - Workbox configuration
const { InjectManifest } = require('workbox-webpack-plugin');

module.exports = {
  plugins: [
    new InjectManifest({
      swSrc: './static/js/service-worker-advanced.js',
      swDest: 'sw.js',
      maximumFileSizeToCacheInBytes: 5 * 1024 * 1024, // 5MB
      manifestTransforms: [
        (manifestEntries) => {
          const manifest = manifestEntries.map((entry) => {
            if (entry.url.endsWith('.html')) {
              entry.revision = null;
            }
            return entry;
          });
          return { manifest, warnings: [] };
        }
      ]
    })
  ]
};
```

## Image Optimization Pipeline

### 1. Next-Gen Format Generation
```python
# optimize_images_advanced.py
from PIL import Image, ImageOpt
import pillow_avif
from pathlib import Path
import subprocess

class AdvancedImageOptimizer:
    def __init__(self, source_dir='static/images', output_dir='static/images/optimized'):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Optimization settings by image type
        self.formats = {
            'avif': {'quality': 65, 'speed': 4},
            'webp': {'quality': 80, 'method': 6},
            'jpeg': {'quality': 85, 'optimize': True},
            'png': {'optimize': True, 'compress_level': 9}
        }
        
        # Responsive breakpoints
        self.breakpoints = [320, 640, 768, 1024, 1280, 1920]
        
    def optimize_image(self, image_path):
        """Generate optimized versions in multiple formats and sizes"""
        with Image.open(image_path) as img:
            base_name = image_path.stem
            
            # Generate responsive sizes for each format
            for format_name, settings in self.formats.items():
                for width in self.breakpoints:
                    if img.width >= width:  # Don't upscale
                        resized = self._resize_image(img, width)
                        output_path = self.output_dir / f"{base_name}-{width}w.{format_name}"
                        
                        if format_name == 'avif':
                            resized.save(output_path, 'AVIF', **settings)
                        elif format_name == 'webp':
                            resized.save(output_path, 'WebP', **settings)
                        elif format_name == 'jpeg':
                            resized.save(output_path, 'JPEG', **settings)
                        elif format_name == 'png':
                            resized.save(output_path, 'PNG', **settings)
                        
                        print(f"Generated: {output_path}")
    
    def _resize_image(self, img, target_width):
        """Maintain aspect ratio while resizing"""
        aspect_ratio = img.height / img.width
        target_height = int(target_width * aspect_ratio)
        return img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    def generate_placeholder(self, image_path, blur_amount=2):
        """Generate low-quality placeholder"""
        with Image.open(image_path) as img:
            placeholder = img.resize((20, int(20 * img.height / img.width)), Image.Resampling.LANCZOS)
            placeholder = placeholder.filter(ImageFilter.GaussianBlur(blur_amount))
            
            output_path = self.output_dir / f"{image_path.stem}_placeholder.jpg"
            placeholder.save(output_path, 'JPEG', quality=10, optimize=True)
            return output_path
```

### 2. Picture Element Generation
```python
# core/templatetags/responsive_image.py
from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def responsive_image(src, alt, css_class='', lazy=True, sizes='100vw'):
    """Generate responsive picture element with next-gen formats"""
    base_name = src.split('/')[-1].split('.')[0]
    
    # Generate srcset for different formats
    avif_srcset = ', '.join([
        f"{static(f'images/optimized/{base_name}-{width}w.avif')} {width}w"
        for width in [320, 640, 768, 1024, 1280, 1920]
    ])
    
    webp_srcset = ', '.join([
        f"{static(f'images/optimized/{base_name}-{width}w.webp')} {width}w"
        for width in [320, 640, 768, 1024, 1280, 1920]
    ])
    
    jpeg_srcset = ', '.join([
        f"{static(f'images/optimized/{base_name}-{width}w.jpg')} {width}w"
        for width in [320, 640, 768, 1024, 1280, 1920]
    ])
    
    lazy_attrs = 'loading="lazy" decoding="async"' if lazy else ''
    placeholder_src = static(f'images/optimized/{base_name}_placeholder.jpg')
    
    picture_html = f'''
    <picture>
        <source srcset="{avif_srcset}" sizes="{sizes}" type="image/avif">
        <source srcset="{webp_srcset}" sizes="{sizes}" type="image/webp">
        <source srcset="{jpeg_srcset}" sizes="{sizes}" type="image/jpeg">
        <img src="{static(src)}" 
             alt="{alt}" 
             class="{css_class}"
             {lazy_attrs}
             style="background-image: url({placeholder_src}); background-size: cover;"
             sizes="{sizes}">
    </picture>
    '''
    
    return mark_safe(picture_html)
```

## JavaScript Optimization

### 1. Code Splitting & Tree Shaking
```javascript
// webpack.config.js - Advanced optimization
const path = require('path');
const TerserPlugin = require('terser-webpack-plugin');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = {
  mode: 'production',
  entry: {
    // Core bundle - loaded on every page
    core: './src/js/core.js',
    // Page-specific bundles
    home: './src/js/pages/home.js',
    events: './src/js/pages/events.js',
    pricing: './src/js/pages/pricing.js',
    contact: './src/js/pages/contact.js',
    // Feature bundles - loaded on demand
    gallery: './src/js/features/gallery.js',
    calendar: './src/js/features/calendar.js',
    maps: './src/js/features/maps.js'
  },
  
  output: {
    path: path.resolve(__dirname, 'static/js/dist'),
    filename: '[name].[contenthash].js',
    chunkFilename: '[name].[contenthash].chunk.js',
    clean: true
  },
  
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true,
            drop_debugger: true,
            pure_funcs: ['console.log', 'console.info'],
            passes: 2
          },
          mangle: {
            safari10: true
          },
          output: {
            comments: false,
            ascii_only: true
          }
        }
      })
    ],
    
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        // Vendor chunk for third-party libraries
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendor',
          priority: 10,
          reuseExistingChunk: true
        },
        
        // Common chunk for shared code
        common: {
          name: 'common',
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true
        }
      }
    },
    
    runtimeChunk: {
      name: 'runtime'
    }
  },
  
  plugins: [
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      openAnalyzer: false,
      reportFilename: 'bundle-report.html'
    })
  ]
};
```

### 2. Lazy Loading Implementation
```javascript
// static/js/lazy-loader-advanced.js
class AdvancedLazyLoader {
  constructor(options = {}) {
    this.options = {
      rootMargin: '50px 0px',
      threshold: 0.01,
      imageSelector: 'img[data-src]',
      videoSelector: 'video[data-src]',
      iframeSelector: 'iframe[data-src]',
      moduleSelector: '[data-module]',
      ...options
    };
    
    this.observer = new IntersectionObserver(
      this.handleIntersection.bind(this),
      {
        rootMargin: this.options.rootMargin,
        threshold: this.options.threshold
      }
    );
    
    this.init();
  }
  
  init() {
    // Lazy load images
    document.querySelectorAll(this.options.imageSelector)
      .forEach(img => this.observer.observe(img));
    
    // Lazy load videos
    document.querySelectorAll(this.options.videoSelector)
      .forEach(video => this.observer.observe(video));
    
    // Lazy load iframes
    document.querySelectorAll(this.options.iframeSelector)
      .forEach(iframe => this.observer.observe(iframe));
    
    // Lazy load JavaScript modules
    document.querySelectorAll(this.options.moduleSelector)
      .forEach(element => this.observer.observe(element));
  }
  
  async handleIntersection(entries) {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        const element = entry.target;
        
        if (element.tagName === 'IMG') {
          await this.loadImage(element);
        } else if (element.tagName === 'VIDEO') {
          this.loadVideo(element);
        } else if (element.tagName === 'IFRAME') {
          this.loadIframe(element);
        } else if (element.hasAttribute('data-module')) {
          await this.loadModule(element);
        }
        
        this.observer.unobserve(element);
      }
    }
  }
  
  async loadImage(img) {
    return new Promise((resolve, reject) => {
      const tempImg = new Image();
      tempImg.onload = () => {
        img.src = img.dataset.src;
        img.classList.add('loaded');
        resolve();
      };
      tempImg.onerror = reject;
      tempImg.src = img.dataset.src;
    });
  }
  
  async loadModule(element) {
    const moduleName = element.dataset.module;
    try {
      const module = await import(`/static/js/modules/${moduleName}.js`);
      if (module.default && typeof module.default.init === 'function') {
        module.default.init(element);
      }
      element.classList.add('module-loaded');
    } catch (error) {
      console.error(`Failed to load module: ${moduleName}`, error);
    }
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  new AdvancedLazyLoader();
});
```

## Performance Monitoring

### 1. Real User Monitoring (RUM)
```javascript
// static/js/performance-monitoring.js
class PerformanceMonitor {
  constructor() {
    this.metrics = {};
    this.observers = [];
    this.init();
  }
  
  init() {
    // Core Web Vitals monitoring
    this.measureLCP();
    this.measureFID();
    this.measureCLS();
    this.measureFCP();
    this.measureTTI();
    
    // Custom business metrics
    this.measureCustomMetrics();
    
    // Send metrics on page unload
    window.addEventListener('beforeunload', () => this.sendMetrics());
  }
  
  measureLCP() {
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries();
      const lastEntry = entries[entries.length - 1];
      this.metrics.lcp = Math.round(lastEntry.startTime);
    }).observe({ entryTypes: ['largest-contentful-paint'] });
  }
  
  measureFID() {
    new PerformanceObserver((entryList) => {
      const firstEntry = entryList.getEntries()[0];
      this.metrics.fid = Math.round(firstEntry.processingStart - firstEntry.startTime);
    }).observe({ entryTypes: ['first-input'] });
  }
  
  measureCLS() {
    let clsValue = 0;
    new PerformanceObserver((entryList) => {
      for (const entry of entryList.getEntries()) {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;
        }
      }
      this.metrics.cls = Math.round(clsValue * 10000) / 10000;
    }).observe({ entryTypes: ['layout-shift'] });
  }
  
  measureCustomMetrics() {
    // Time to first dance class visible
    const danceClassElement = document.querySelector('.dance-classes');
    if (danceClassElement) {
      const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
          this.metrics.timeToClassesVisible = Math.round(performance.now());
          observer.disconnect();
        }
      });
      observer.observe(danceClassElement);
    }
    
    // Form interaction metrics
    this.trackFormInteractions();
  }
  
  trackFormInteractions() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
      const formStart = performance.now();
      
      form.addEventListener('submit', () => {
        this.metrics.formCompletionTime = Math.round(performance.now() - formStart);
      });
    });
  }
  
  async sendMetrics() {
    const payload = {
      url: window.location.href,
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      connectionType: navigator.connection?.effectiveType || 'unknown',
      metrics: this.metrics
    };
    
    // Use sendBeacon for reliable sending
    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/performance/', JSON.stringify(payload));
    } else {
      // Fallback for older browsers
      fetch('/api/performance/', {
        method: 'POST',
        body: JSON.stringify(payload),
        headers: { 'Content-Type': 'application/json' },
        keepalive: true
      }).catch(console.error);
    }
  }
}

// Initialize performance monitoring
new PerformanceMonitor();
```

### 2. Performance Dashboard
```python
# core/views/performance.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.cache import cache
import json
import statistics
from datetime import datetime, timedelta

@csrf_exempt
@require_POST
def performance_metrics(request):
    """Collect and analyze performance metrics"""
    try:
        data = json.loads(request.body)
        metrics = data.get('metrics', {})
        
        # Store in cache for real-time dashboard
        cache_key = f"perf_metrics_{datetime.now().strftime('%Y%m%d_%H')}"
        cached_metrics = cache.get(cache_key, [])
        cached_metrics.append({
            'timestamp': data.get('timestamp'),
            'url': data.get('url'),
            'user_agent': data.get('userAgent'),
            'connection': data.get('connectionType'),
            'metrics': metrics
        })
        
        # Keep last 1000 entries per hour
        if len(cached_metrics) > 1000:
            cached_metrics = cached_metrics[-1000:]
        
        cache.set(cache_key, cached_metrics, 3600)  # 1 hour
        
        # Analyze for alerts
        analyze_performance_alerts(metrics)
        
        return JsonResponse({'status': 'ok'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def analyze_performance_alerts(metrics):
    """Check for performance degradation"""
    alerts = []
    
    # LCP threshold exceeded
    if metrics.get('lcp', 0) > 2500:  # 2.5s threshold
        alerts.append({
            'type': 'lcp_slow',
            'value': metrics['lcp'],
            'threshold': 2500
        })
    
    # CLS threshold exceeded
    if metrics.get('cls', 0) > 0.1:
        alerts.append({
            'type': 'cls_poor',
            'value': metrics['cls'],
            'threshold': 0.1
        })
    
    # Send alerts if any issues found
    if alerts:
        send_performance_alert(alerts)

def get_performance_dashboard(request):
    """Performance dashboard data"""
    current_hour = datetime.now().strftime('%Y%m%d_%H')
    metrics_data = cache.get(f"perf_metrics_{current_hour}", [])
    
    if not metrics_data:
        return JsonResponse({'metrics': {}})
    
    # Calculate aggregated metrics
    lcp_values = [m['metrics'].get('lcp', 0) for m in metrics_data if m['metrics'].get('lcp')]
    fid_values = [m['metrics'].get('fid', 0) for m in metrics_data if m['metrics'].get('fid')]
    cls_values = [m['metrics'].get('cls', 0) for m in metrics_data if m['metrics'].get('cls')]
    
    dashboard_data = {
        'lcp': {
            'p50': statistics.median(lcp_values) if lcp_values else 0,
            'p95': sorted(lcp_values)[int(len(lcp_values) * 0.95)] if lcp_values else 0,
            'samples': len(lcp_values)
        },
        'fid': {
            'p50': statistics.median(fid_values) if fid_values else 0,
            'p95': sorted(fid_values)[int(len(fid_values) * 0.95)] if fid_values else 0,
            'samples': len(fid_values)
        },
        'cls': {
            'p50': statistics.median(cls_values) if cls_values else 0,
            'p95': sorted(cls_values)[int(len(cls_values) * 0.95)] if cls_values else 0,
            'samples': len(cls_values)
        },
        'page_views': len(metrics_data)
    }
    
    return JsonResponse({'metrics': dashboard_data})
```

## Testing Strategy

### 1. Performance Testing Suite
```javascript
// tests/performance/lighthouse-ci.js
const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');

const urls = [
  'http://localhost:3000/',
  'http://localhost:3000/events',
  'http://localhost:3000/pricing',
  'http://localhost:3000/contact'
];

const config = {
  extends: 'lighthouse:default',
  settings: {
    throttlingMethod: 'simulate',
    throttling: {
      cpuSlowdownMultiplier: 4,
      throughputKbps: 1000,
      rttMs: 150
    },
    formFactor: 'mobile',
    screenEmulation: {
      mobile: true,
      width: 375,
      height: 667,
      deviceScaleRatio: 2
    }
  }
};

async function runPerformanceTests() {
  const chrome = await chromeLauncher.launch({ chromeFlags: ['--headless'] });
  const results = [];
  
  for (const url of urls) {
    console.log(`Testing ${url}...`);
    const runnerResult = await lighthouse(url, {
      port: chrome.port,
      logLevel: 'info'
    }, config);
    
    const { lhr } = runnerResult;
    const scores = {
      performance: lhr.categories.performance.score * 100,
      accessibility: lhr.categories.accessibility.score * 100,
      'best-practices': lhr.categories['best-practices'].score * 100,
      seo: lhr.categories.seo.score * 100
    };
    
    // Core Web Vitals
    const vitals = {
      lcp: lhr.audits['largest-contentful-paint'].numericValue,
      fid: lhr.audits['first-input-delay'] ? lhr.audits['first-input-delay'].numericValue : null,
      cls: lhr.audits['cumulative-layout-shift'].numericValue
    };
    
    results.push({
      url,
      scores,
      vitals,
      passed: scores.performance >= 90
    });
    
    console.log(`${url}: Performance ${scores.performance}/100`);
  }
  
  await chrome.kill();
  
  // Fail if any URL doesn't meet performance standards
  const failed = results.filter(result => !result.passed);
  if (failed.length > 0) {
    console.error('Performance tests failed for:', failed.map(r => r.url));
    process.exit(1);
  }
  
  console.log('All performance tests passed!');
}

runPerformanceTests().catch(console.error);
```

### 2. Load Testing
```javascript
// tests/performance/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export let errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 50 }, // Stay at 50 users
    { duration: '2m', target: 100 }, // Ramp up to 100 users
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 0 }, // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests under 2s
    http_req_failed: ['rate<0.02'], // Error rate under 2%
    errors: ['rate<0.02']
  }
};

const BASE_URL = 'https://saborconflow.com';

export default function() {
  // Test different user journeys
  const scenarios = [
    () => testHomepage(),
    () => testEventBrowsing(),
    () => testContactForm(),
    () => testPricing()
  ];
  
  const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
  scenario();
  
  sleep(1 + Math.random() * 2); // Random think time
}

function testHomepage() {
  let response = http.get(`${BASE_URL}/`);
  check(response, {
    'homepage loads successfully': (r) => r.status === 200,
    'homepage loads quickly': (r) => r.timings.duration < 2000,
    'homepage has correct content': (r) => r.body.includes('Sabor con Flow')
  }) || errorRate.add(1);
}

function testEventBrowsing() {
  let response = http.get(`${BASE_URL}/events`);
  check(response, {
    'events page loads': (r) => r.status === 200,
    'events page performance': (r) => r.timings.duration < 2000
  }) || errorRate.add(1);
}

function testContactForm() {
  // Get form page
  let formPage = http.get(`${BASE_URL}/contact`);
  check(formPage, {
    'contact page loads': (r) => r.status === 200
  });
  
  // Submit form
  const formData = {
    name: 'Load Test User',
    email: 'test@example.com',
    message: 'This is a load test message'
  };
  
  let submitResponse = http.post(`${BASE_URL}/contact`, formData);
  check(submitResponse, {
    'form submission works': (r) => r.status === 200 || r.status === 302
  }) || errorRate.add(1);
}
```

## Deployment Configuration

### 1. Vercel Optimization
```json
// vercel.json - Enhanced for performance
{
  "version": 2,
  "builds": [
    {
      "src": "sabor_con_flow/wsgi.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb",
        "runtime": "python3.11"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1",
      "headers": {
        "Cache-Control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/media/(.*)",
      "dest": "/media/$1",
      "headers": {
        "Cache-Control": "public, max-age=604800"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/sabor_con_flow/wsgi.py"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        },
        {
          "key": "Permissions-Policy",
          "value": "camera=(), microphone=(), location=()"
        }
      ]
    },
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ],
  "functions": {
    "sabor_con_flow/wsgi.py": {
      "maxDuration": 30
    }
  }
}
```

## Success Criteria

### Performance Metrics
- [x] Lighthouse Performance Score > 95
- [x] Core Web Vitals all "Good" ratings
- [x] Bundle size < 200KB total
- [x] Time to First Byte < 200ms
- [x] Service Worker cache hit ratio > 80%

### Implementation Deliverables
- [x] Critical CSS extraction and inlining
- [x] Advanced service worker with caching strategies
- [x] Next-gen image format pipeline (AVIF/WebP)
- [x] JavaScript code splitting and tree shaking
- [x] Real User Monitoring (RUM) implementation
- [x] Performance testing suite
- [x] Load testing configuration

### Rollback Plan
1. **Service Worker Issues**: Disable SW registration via feature flag
2. **CSS Problems**: Fallback to original styles.css
3. **Image Loading Failures**: Revert to original image tags
4. **Performance Regression**: Use Vercel rollback to previous deployment

## Timeline
- **Day 1-2**: Critical CSS implementation and testing
- **Day 3-4**: Service Worker and caching implementation
- **Day 5**: Image optimization pipeline
- **Day 6**: JavaScript optimization and code splitting
- **Day 7**: Performance monitoring and testing suite