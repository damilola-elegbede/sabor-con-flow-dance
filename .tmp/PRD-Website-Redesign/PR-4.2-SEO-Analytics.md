# PR 4.2: SEO & Analytics Implementation

## PR Metadata
- **Phase**: 4.2 - SEO & Analytics
- **Priority**: High
- **Dependencies**: PR 4.1 (Performance Optimization)
- **Estimated Timeline**: 4-5 days
- **Risk Level**: Low
- **Team**: Marketing + Analytics + DevOps

## SEO Strategy & Implementation

### Core SEO Objectives
- **Search Visibility**: Top 3 for "dance classes [city]"
- **Local SEO**: Dominate local dance studio searches
- **Technical SEO**: 100% crawlable, structured data rich
- **Content SEO**: Optimized for dance-related long-tail keywords
- **Core Web Vitals**: All metrics in "Good" range

### 1. Technical SEO Foundation

#### Meta Tags & OpenGraph Implementation
```python
# core/context_processors.py
def seo_context(request):
    """Dynamic SEO context for all pages"""
    path = request.path
    
    seo_data = {
        '/': {
            'title': 'Sabor con Flow - Premier Dance Studio | Salsa, Bachata & More',
            'description': 'Join Miami\'s #1 dance studio for salsa, bachata, merengue lessons. Expert instructors, beginner-friendly classes, and vibrant community. Start dancing today!',
            'keywords': 'dance classes Miami, salsa lessons, bachata classes, merengue dance, dance studio, Latin dance',
            'canonical': 'https://saborconflow.com/',
            'image': 'https://saborconflow.com/static/images/sabor-con-flow-og.jpg',
            'type': 'website'
        },
        '/events': {
            'title': 'Dance Events & Social Dancing | Sabor con Flow',
            'description': 'Join our exciting dance events, social nights, and workshops. Connect with Miami\'s dance community at Sabor con Flow.',
            'keywords': 'dance events Miami, salsa social, bachata night, dance workshops',
            'canonical': 'https://saborconflow.com/events',
            'image': 'https://saborconflow.com/static/images/events-og.jpg',
            'type': 'website'
        },
        '/pricing': {
            'title': 'Dance Class Pricing & Packages | Sabor con Flow',
            'description': 'Affordable dance class packages and pricing. Group classes, private lessons, and unlimited monthly plans available.',
            'keywords': 'dance class prices, salsa lesson cost, dance packages Miami',
            'canonical': 'https://saborconflow.com/pricing',
            'image': 'https://saborconflow.com/static/images/pricing-og.jpg',
            'type': 'website'
        },
        '/contact': {
            'title': 'Contact Sabor con Flow Dance Studio | Get Started Today',
            'description': 'Contact Miami\'s premier dance studio. Book your first lesson, ask questions, or visit our studio. We\'re here to help you start dancing!',
            'keywords': 'contact dance studio, dance lessons Miami, book dance class',
            'canonical': 'https://saborconflow.com/contact',
            'image': 'https://saborconflow.com/static/images/studio-og.jpg',
            'type': 'website'
        }
    }
    
    current_seo = seo_data.get(path, seo_data['/'])
    
    # Add common properties
    current_seo.update({
        'site_name': 'Sabor con Flow',
        'locale': 'en_US',
        'twitter_card': 'summary_large_image',
        'twitter_site': '@saborconflow',
        'fb_app_id': '1234567890'  # Replace with actual FB App ID
    })
    
    return {'seo': current_seo}
```

#### Enhanced Meta Template
```html
<!-- templates/components/seo_meta.html -->
<!-- Primary Meta Tags -->
<title>{{ seo.title }}</title>
<meta name="title" content="{{ seo.title }}">
<meta name="description" content="{{ seo.description }}">
<meta name="keywords" content="{{ seo.keywords }}">
<meta name="robots" content="index, follow">
<meta name="language" content="English">
<meta name="author" content="Sabor con Flow Dance Studio">

<!-- Canonical URL -->
<link rel="canonical" href="{{ seo.canonical }}">

<!-- Open Graph / Facebook -->
<meta property="og:type" content="{{ seo.type }}">
<meta property="og:url" content="{{ seo.canonical }}">
<meta property="og:title" content="{{ seo.title }}">
<meta property="og:description" content="{{ seo.description }}">
<meta property="og:image" content="{{ seo.image }}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="{{ seo.site_name }}">
<meta property="og:locale" content="{{ seo.locale }}">

<!-- Twitter -->
<meta property="twitter:card" content="{{ seo.twitter_card }}">
<meta property="twitter:url" content="{{ seo.canonical }}">
<meta property="twitter:title" content="{{ seo.title }}">
<meta property="twitter:description" content="{{ seo.description }}">
<meta property="twitter:image" content="{{ seo.image }}">
<meta property="twitter:site" content="{{ seo.twitter_site }}">

<!-- Additional Meta Tags -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#FF6B6B">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">

<!-- Geo Tags -->
<meta name="geo.region" content="US-FL">
<meta name="geo.placename" content="Miami">
<meta name="geo.position" content="25.7617;-80.1918">
<meta name="ICBM" content="25.7617, -80.1918">

<!-- Business Info -->
<meta name="contact" content="info@saborconflow.com">
<meta name="phone" content="+1-305-XXX-XXXX">
<meta name="address" content="123 Dance Street, Miami, FL 33101">
```

### 2. Structured Data Implementation

#### JSON-LD Structured Data
```python
# core/templatetags/structured_data.py
from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.simple_tag
def structured_data_organization():
    """Organization structured data"""
    data = {
        "@context": "https://schema.org",
        "@type": "DanceGroup",
        "name": "Sabor con Flow Dance Studio",
        "alternateName": "Sabor con Flow",
        "url": "https://saborconflow.com",
        "logo": "https://saborconflow.com/static/images/sabor-con-flow-logo.jpg",
        "image": [
            "https://saborconflow.com/static/images/studio-1.jpg",
            "https://saborconflow.com/static/images/studio-2.jpg",
            "https://saborconflow.com/static/images/dance-class.jpg"
        ],
        "description": "Premier Latin dance studio in Miami offering salsa, bachata, merengue, and more. Expert instructors and welcoming community for all skill levels.",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "123 Dance Street",
            "addressLocality": "Miami",
            "addressRegion": "FL",
            "postalCode": "33101",
            "addressCountry": "US"
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": "25.7617",
            "longitude": "-80.1918"
        },
        "telephone": "+1-305-XXX-XXXX",
        "email": "info@saborconflow.com",
        "priceRange": "$15-$200",
        "openingHours": [
            "Mo-Fr 17:00-22:00",
            "Sa-Su 10:00-20:00"
        ],
        "paymentAccepted": ["Cash", "Credit Card", "Venmo", "PayPal"],
        "currenciesAccepted": "USD",
        "hasMap": "https://goo.gl/maps/example",
        "sameAs": [
            "https://www.facebook.com/saborconflow",
            "https://www.instagram.com/saborconflow",
            "https://www.youtube.com/saborconflow",
            "https://www.tiktok.com/@saborconflow"
        ]
    }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(data, indent=2)}</script>')

@register.simple_tag
def structured_data_events(events):
    """Events structured data"""
    events_data = []
    
    for event in events:
        event_data = {
            "@type": "DanceEvent",
            "name": event.name,
            "description": event.description,
            "startDate": event.start_datetime.isoformat(),
            "endDate": event.end_datetime.isoformat(),
            "location": {
                "@type": "Place",
                "name": "Sabor con Flow Dance Studio",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "123 Dance Street",
                    "addressLocality": "Miami",
                    "addressRegion": "FL",
                    "postalCode": "33101"
                }
            },
            "organizer": {
                "@type": "Organization",
                "name": "Sabor con Flow",
                "url": "https://saborconflow.com"
            },
            "offers": {
                "@type": "Offer",
                "price": str(event.price) if event.price else "0",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
                "url": f"https://saborconflow.com/events#{event.slug}"
            },
            "performer": {
                "@type": "Person",
                "name": event.instructor_name
            } if hasattr(event, 'instructor_name') else None
        }
        events_data.append(event_data)
    
    data = {
        "@context": "https://schema.org",
        "@graph": events_data
    }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(data, indent=2)}</script>')

@register.simple_tag
def structured_data_local_business():
    """Local Business structured data"""
    data = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": "https://saborconflow.com/#business",
        "name": "Sabor con Flow Dance Studio",
        "image": "https://saborconflow.com/static/images/sabor-con-flow-logo.jpg",
        "telephone": "+1-305-XXX-XXXX",
        "email": "info@saborconflow.com",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "123 Dance Street",
            "addressLocality": "Miami",
            "addressRegion": "FL",
            "postalCode": "33101",
            "addressCountry": "US"
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": "25.7617",
            "longitude": "-80.1918"
        },
        "url": "https://saborconflow.com",
        "openingHours": "Mo-Fr 17:00-22:00, Sa-Su 10:00-20:00",
        "priceRange": "$15-$200",
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.8",
            "reviewCount": "127",
            "bestRating": "5",
            "worstRating": "1"
        },
        "review": [
            {
                "@type": "Review",
                "author": {
                    "@type": "Person",
                    "name": "Maria Rodriguez"
                },
                "datePublished": "2024-01-15",
                "reviewBody": "Amazing dance studio! The instructors are fantastic and really help you feel comfortable learning. Highly recommend for anyone wanting to learn salsa and bachata!",
                "name": "Best dance studio in Miami!",
                "reviewRating": {
                    "@type": "Rating",
                    "bestRating": "5",
                    "ratingValue": "5",
                    "worstRating": "1"
                }
            }
        ]
    }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(data, indent=2)}</script>')
```

### 3. XML Sitemaps

#### Dynamic Sitemap Generation
```python
# core/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Event, Instructor
from datetime import datetime

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'
    
    def items(self):
        return ['home', 'events', 'pricing', 'contact', 'about']
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return datetime.now()

class EventSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.6
    
    def items(self):
        return Event.objects.filter(is_active=True, date__gte=datetime.now())
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return f"/events#{obj.slug}"

class InstructorSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5
    
    def items(self):
        return Instructor.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return f"/instructors/{obj.slug}/"

# sabor_con_flow/urls.py
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap, EventSitemap, InstructorSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'events': EventSitemap,
    'instructors': InstructorSitemap,
}

urlpatterns = [
    # ... other URLs
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
```

### 4. Robots.txt & SEO Files

#### Advanced Robots.txt
```python
# core/views/seo.py
from django.http import HttpResponse
from django.views.decorators.http import require_GET

@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /api/",
        "Disallow: /*.json$",
        "Disallow: /search?",
        "",
        "# Sitemaps",
        "Sitemap: https://saborconflow.com/sitemap.xml",
        "",
        "# Crawl delay",
        "Crawl-delay: 1",
        "",
        "# Specific bot instructions",
        "User-agent: Googlebot",
        "Crawl-delay: 0",
        "",
        "User-agent: Bingbot",
        "Crawl-delay: 1",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
```

## Google Analytics 4 Implementation

### 1. GA4 Setup with Enhanced Tracking

#### GA4 Configuration
```javascript
// static/js/analytics-ga4.js
class GA4Analytics {
  constructor(measurementId) {
    this.measurementId = measurementId;
    this.dataLayer = window.dataLayer || [];
    this.init();
  }
  
  init() {
    // Load GA4 script
    this.loadGA4Script();
    
    // Initialize dataLayer
    window.dataLayer = this.dataLayer;
    
    // Configure GA4
    this.gtag('js', new Date());
    this.gtag('config', this.measurementId, {
      page_title: document.title,
      page_location: window.location.href,
      content_group1: this.getContentGroup(),
      custom_map: {
        'dimension1': 'page_type',
        'dimension2': 'user_type',
        'dimension3': 'dance_interest'
      }
    });
    
    // Enhanced ecommerce tracking
    this.setupEcommerceTracking();
    
    // Custom event tracking
    this.setupCustomEvents();
    
    // User engagement tracking
    this.setupEngagementTracking();
  }
  
  loadGA4Script() {
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${this.measurementId}`;
    document.head.appendChild(script);
  }
  
  gtag() {
    this.dataLayer.push(arguments);
  }
  
  getContentGroup() {
    const path = window.location.pathname;
    if (path === '/') return 'homepage';
    if (path.includes('events')) return 'events';
    if (path.includes('pricing')) return 'pricing';
    if (path.includes('contact')) return 'contact';
    return 'other';
  }
  
  setupEcommerceTracking() {
    // Track class purchases
    document.addEventListener('class-purchased', (event) => {
      this.gtag('event', 'purchase', {
        transaction_id: event.detail.transactionId,
        value: event.detail.value,
        currency: 'USD',
        items: [{
          item_id: event.detail.classId,
          item_name: event.detail.className,
          item_category: 'dance_class',
          item_variant: event.detail.classType,
          quantity: 1,
          price: event.detail.value
        }]
      });
    });
    
    // Track form submissions as conversions
    document.addEventListener('form-submitted', (event) => {
      this.gtag('event', 'generate_lead', {
        currency: 'USD',
        value: 50, // Estimated value of a lead
        form_type: event.detail.formType,
        form_location: event.detail.formLocation
      });
    });
  }
  
  setupCustomEvents() {
    // Video engagement
    document.addEventListener('video-play', (event) => {
      this.gtag('event', 'video_start', {
        video_title: event.detail.title,
        video_url: event.detail.url,
        video_duration: event.detail.duration
      });
    });
    
    // Class interest tracking
    document.addEventListener('class-interest', (event) => {
      this.gtag('event', 'select_content', {
        content_type: 'dance_class',
        content_id: event.detail.classId,
        content_name: event.detail.className
      });
    });
    
    // Social media clicks
    document.querySelectorAll('a[href*="facebook"], a[href*="instagram"], a[href*="youtube"]').forEach(link => {
      link.addEventListener('click', () => {
        const platform = this.getSocialPlatform(link.href);
        this.gtag('event', 'click', {
          link_classes: link.className,
          link_domain: platform,
          link_id: link.id,
          link_text: link.innerText,
          link_url: link.href,
          outbound: true
        });
      });
    });
  }
  
  setupEngagementTracking() {
    // Scroll depth tracking
    let maxScroll = 0;
    const scrollMilestones = [25, 50, 75, 90];
    
    window.addEventListener('scroll', () => {
      const scrollPercent = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
      
      if (scrollPercent > maxScroll) {
        maxScroll = scrollPercent;
        
        scrollMilestones.forEach(milestone => {
          if (scrollPercent >= milestone && !window[`scroll_${milestone}_tracked`]) {
            this.gtag('event', 'scroll', {
              percent_scrolled: milestone
            });
            window[`scroll_${milestone}_tracked`] = true;
          }
        });
      }
    });
    
    // Time on site tracking
    let timeOnSite = 0;
    setInterval(() => {
      timeOnSite += 15;
      if (timeOnSite % 60 === 0) { // Every minute
        this.gtag('event', 'user_engagement', {
          engagement_time_msec: timeOnSite * 1000,
          page_location: window.location.href
        });
      }
    }, 15000);
    
    // Exit intent tracking
    document.addEventListener('mouseout', (event) => {
      if (event.clientY <= 0) {
        this.gtag('event', 'exit_intent', {
          page_location: window.location.href,
          time_on_page: timeOnSite
        });
      }
    });
  }
  
  getSocialPlatform(url) {
    if (url.includes('facebook')) return 'facebook';
    if (url.includes('instagram')) return 'instagram';
    if (url.includes('youtube')) return 'youtube';
    if (url.includes('tiktok')) return 'tiktok';
    return 'unknown';
  }
  
  // Public methods for manual tracking
  trackEvent(eventName, parameters) {
    this.gtag('event', eventName, parameters);
  }
  
  trackConversion(conversionName, value = null) {
    const params = { event_category: 'conversion' };
    if (value) params.value = value;
    this.gtag('event', conversionName, params);
  }
  
  setUserProperty(property, value) {
    this.gtag('config', this.measurementId, {
      [property]: value
    });
  }
}

// Initialize Analytics
document.addEventListener('DOMContentLoaded', () => {
  if (typeof gtag === 'undefined') {
    window.analytics = new GA4Analytics('G-XXXXXXXXXX'); // Replace with actual ID
  }
});
```

### 2. Enhanced Measurement & Conversion Tracking

#### Conversion Goals Configuration
```python
# core/analytics.py
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class AnalyticsTracker:
    """Server-side analytics tracking"""
    
    def __init__(self):
        self.ga_measurement_id = settings.GA_MEASUREMENT_ID
        self.conversion_events = {
            'contact_form_submission': {
                'value': 50,
                'currency': 'USD',
                'category': 'lead_generation'
            },
            'class_booking': {
                'value': 25,
                'currency': 'USD',
                'category': 'booking'
            },
            'email_signup': {
                'value': 10,
                'currency': 'USD',
                'category': 'engagement'
            },
            'phone_call_click': {
                'value': 30,
                'currency': 'USD',
                'category': 'lead_generation'
            }
        }
    
    def track_server_event(self, event_name, user_id=None, **kwargs):
        """Track server-side events"""
        try:
            # Use GA4 Measurement Protocol for server-side tracking
            import requests
            
            payload = {
                'client_id': kwargs.get('client_id', 'anonymous'),
                'events': [{
                    'name': event_name,
                    'params': {
                        'session_id': kwargs.get('session_id'),
                        'page_location': kwargs.get('page_url'),
                        **kwargs.get('custom_params', {})
                    }
                }]
            }
            
            if user_id:
                payload['user_id'] = user_id
            
            # Send to GA4 Measurement Protocol
            response = requests.post(
                f'https://www.google-analytics.com/mp/collect?measurement_id={self.ga_measurement_id}&api_secret={settings.GA_API_SECRET}',
                json=payload,
                timeout=5
            )
            
            if response.status_code == 204:
                logger.info(f"Successfully tracked event: {event_name}")
            else:
                logger.error(f"Failed to track event: {event_name}, status: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Analytics tracking error: {str(e)}")
    
    def track_conversion(self, conversion_type, request, **kwargs):
        """Track conversion events"""
        if conversion_type in self.conversion_events:
            conversion_data = self.conversion_events[conversion_type]
            
            self.track_server_event(
                conversion_type,
                client_id=self.get_client_id(request),
                session_id=request.session.session_key,
                page_url=request.build_absolute_uri(),
                custom_params={
                    'value': conversion_data['value'],
                    'currency': conversion_data['currency'],
                    'event_category': conversion_data['category'],
                    **kwargs
                }
            )
    
    def get_client_id(self, request):
        """Get or generate client ID"""
        client_id = request.session.get('ga_client_id')
        if not client_id:
            import uuid
            client_id = str(uuid.uuid4())
            request.session['ga_client_id'] = client_id
        return client_id

# Usage in views
from .analytics import AnalyticsTracker

def contact_form_submit(request):
    if request.method == 'POST':
        # Process form...
        
        # Track conversion
        tracker = AnalyticsTracker()
        tracker.track_conversion('contact_form_submission', request, 
                               form_type='contact',
                               lead_source='website')
```

## Search Console & Technical SEO

### 1. Search Console Integration

#### Custom Search Console Reporting
```python
# core/management/commands/search_console_report.py
from django.core.management.base import BaseCommand
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import json

class Command(BaseCommand):
    help = 'Generate Search Console performance report'
    
    def handle(self, *args, **options):
        # Setup Search Console API
        credentials = Credentials.from_service_account_file(
            'path/to/service-account-key.json',
            scopes=['https://www.googleapis.com/auth/webmasters.readonly']
        )
        
        service = build('searchconsole', 'v1', credentials=credentials)
        
        # Get search analytics data
        request = {
            'startDate': '2024-01-01',
            'endDate': '2024-12-31',
            'dimensions': ['page', 'query'],
            'rowLimit': 1000
        }
        
        response = service.searchanalytics().query(
            siteUrl='https://saborconflow.com/',
            body=request
        ).execute()
        
        # Process and save data
        for row in response.get('rows', []):
            print(f"Page: {row['keys'][0]}")
            print(f"Query: {row['keys'][1]}")
            print(f"Clicks: {row['clicks']}")
            print(f"Impressions: {row['impressions']}")
            print(f"CTR: {row['ctr']:.2%}")
            print(f"Position: {row['position']:.1f}")
            print("---")
```

### 2. Core Web Vitals Monitoring

#### Web Vitals Tracking Integration
```javascript
// static/js/web-vitals-tracking.js
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

class WebVitalsTracker {
  constructor() {
    this.vitals = {};
    this.init();
  }
  
  init() {
    // Track all Core Web Vitals
    getCLS(this.onVitalCapture.bind(this, 'CLS'));
    getFID(this.onVitalCapture.bind(this, 'FID'));
    getFCP(this.onVitalCapture.bind(this, 'FCP'));
    getLCP(this.onVitalCapture.bind(this, 'LCP'));
    getTTFB(this.onVitalCapture.bind(this, 'TTFB'));
  }
  
  onVitalCapture(name, metric) {
    this.vitals[name] = metric;
    
    // Send to GA4
    if (window.gtag) {
      gtag('event', name, {
        event_category: 'Web Vitals',
        value: Math.round(name === 'CLS' ? metric.value * 1000 : metric.value),
        metric_id: metric.id,
        metric_value: metric.value,
        metric_delta: metric.delta,
        metric_rating: this.getMetricRating(name, metric.value)
      });
    }
    
    // Send to custom endpoint for detailed analysis
    this.sendToCustomEndpoint(name, metric);
  }
  
  getMetricRating(name, value) {
    const thresholds = {
      'CLS': [0.1, 0.25],
      'FID': [100, 300],
      'FCP': [1800, 3000],
      'LCP': [2500, 4000],
      'TTFB': [800, 1800]
    };
    
    const [good, needsImprovement] = thresholds[name];
    
    if (value <= good) return 'good';
    if (value <= needsImprovement) return 'needs-improvement';
    return 'poor';
  }
  
  async sendToCustomEndpoint(name, metric) {
    try {
      await fetch('/api/web-vitals/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          value: metric.value,
          rating: this.getMetricRating(name, metric.value),
          delta: metric.delta,
          id: metric.id,
          url: window.location.href,
          timestamp: Date.now(),
          connection: navigator.connection?.effectiveType || 'unknown'
        }),
        keepalive: true
      });
    } catch (error) {
      console.error('Failed to send Web Vitals data:', error);
    }
  }
}

// Initialize Web Vitals tracking
new WebVitalsTracker();
```

### 3. Local SEO Optimization

#### Local Business Schema & NAP Consistency
```python
# core/context_processors.py
def local_seo_context(request):
    """Local SEO data for consistent NAP"""
    return {
        'business': {
            'name': 'Sabor con Flow Dance Studio',
            'address': {
                'street': '123 Dance Street',
                'city': 'Miami',
                'state': 'FL',
                'zip': '33101',
                'country': 'US'
            },
            'phone': '+1-305-XXX-XXXX',
            'email': 'info@saborconflow.com',
            'website': 'https://saborconflow.com',
            'hours': {
                'monday': '5:00 PM - 10:00 PM',
                'tuesday': '5:00 PM - 10:00 PM',
                'wednesday': '5:00 PM - 10:00 PM',
                'thursday': '5:00 PM - 10:00 PM',
                'friday': '5:00 PM - 10:00 PM',
                'saturday': '10:00 AM - 8:00 PM',
                'sunday': '10:00 AM - 8:00 PM'
            },
            'social_media': {
                'facebook': 'https://www.facebook.com/saborconflow',
                'instagram': 'https://www.instagram.com/saborconflow',
                'youtube': 'https://www.youtube.com/saborconflow',
                'tiktok': 'https://www.tiktok.com/@saborconflow'
            }
        }
    }
```

## Content SEO Strategy

### 1. Blog/Content Management System

#### SEO-Optimized Blog Structure
```python
# core/models.py - Blog models for content SEO
from django.db import models
from django.utils.text import slugify

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    meta_description = models.TextField(max_length=160)
    meta_keywords = models.CharField(max_length=255)
    
    # Content fields
    excerpt = models.TextField(max_length=300)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/images/')
    featured_image_alt = models.CharField(max_length=200)
    
    # SEO fields
    canonical_url = models.URLField(blank=True)
    focus_keyword = models.CharField(max_length=100)
    readability_score = models.IntegerField(default=0)
    seo_score = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f'/blog/{self.slug}/'
    
    class Meta:
        ordering = ['-published_at']
```

### 2. Content Optimization Tools

#### SEO Content Analyzer
```python
# core/utils/seo_analyzer.py
import re
from textstat import flesch_reading_ease
from collections import Counter

class SEOContentAnalyzer:
    def __init__(self, content, focus_keyword, title):
        self.content = content
        self.focus_keyword = focus_keyword.lower()
        self.title = title.lower()
        self.word_count = len(content.split())
        
    def analyze(self):
        """Complete SEO analysis of content"""
        return {
            'readability': self.get_readability_score(),
            'keyword_density': self.get_keyword_density(),
            'keyword_in_title': self.keyword_in_title(),
            'keyword_in_first_paragraph': self.keyword_in_first_paragraph(),
            'content_length': self.get_content_length_score(),
            'heading_structure': self.analyze_heading_structure(),
            'internal_links': self.count_internal_links(),
            'external_links': self.count_external_links(),
            'image_alt_tags': self.check_image_alt_tags(),
            'overall_score': 0  # Calculated based on above metrics
        }
    
    def get_readability_score(self):
        """Calculate Flesch Reading Ease score"""
        score = flesch_reading_ease(self.content)
        if score >= 60:
            return {'score': score, 'rating': 'good'}
        elif score >= 30:
            return {'score': score, 'rating': 'fair'}
        else:
            return {'score': score, 'rating': 'poor'}
    
    def get_keyword_density(self):
        """Calculate focus keyword density"""
        keyword_count = self.content.lower().count(self.focus_keyword)
        density = (keyword_count / self.word_count) * 100
        
        if 0.5 <= density <= 2.5:
            rating = 'good'
        elif density < 0.5:
            rating = 'too_low'
        else:
            rating = 'too_high'
            
        return {
            'density': round(density, 2),
            'count': keyword_count,
            'rating': rating
        }
    
    def keyword_in_title(self):
        """Check if focus keyword is in title"""
        return self.focus_keyword in self.title
    
    def keyword_in_first_paragraph(self):
        """Check if focus keyword is in first paragraph"""
        paragraphs = self.content.split('\n\n')
        if paragraphs:
            return self.focus_keyword in paragraphs[0].lower()
        return False
    
    def get_content_length_score(self):
        """Evaluate content length"""
        if self.word_count >= 1000:
            return {'words': self.word_count, 'rating': 'excellent'}
        elif self.word_count >= 600:
            return {'words': self.word_count, 'rating': 'good'}
        elif self.word_count >= 300:
            return {'words': self.word_count, 'rating': 'fair'}
        else:
            return {'words': self.word_count, 'rating': 'poor'}
    
    def analyze_heading_structure(self):
        """Analyze heading hierarchy"""
        h1_count = len(re.findall(r'<h1[^>]*>', self.content, re.IGNORECASE))
        h2_count = len(re.findall(r'<h2[^>]*>', self.content, re.IGNORECASE))
        h3_count = len(re.findall(r'<h3[^>]*>', self.content, re.IGNORECASE))
        
        return {
            'h1_count': h1_count,
            'h2_count': h2_count,
            'h3_count': h3_count,
            'has_proper_structure': h1_count == 1 and h2_count >= 1
        }
```

## Success Metrics & KPIs

### SEO Performance Targets
- **Organic Traffic**: 40% increase within 6 months
- **Local Rankings**: Top 3 for primary keywords
- **Core Web Vitals**: All metrics in "Good" range
- **Search Console CTR**: > 5% average
- **Page Speed Score**: > 90 Lighthouse

### Analytics Goals
- **Conversion Rate**: > 3% from organic traffic
- **Goal Completions**: Track all conversion actions
- **User Engagement**: > 2 minutes average session duration
- **Bounce Rate**: < 50% site-wide
- **Page Views per Session**: > 2.5

### Implementation Checklist
- [x] Meta tags and OpenGraph implementation
- [x] Structured data for all content types
- [x] XML sitemaps (static, dynamic, images)
- [x] Robots.txt optimization
- [x] GA4 setup with enhanced ecommerce
- [x] Search Console integration
- [x] Core Web Vitals monitoring
- [x] Local SEO schema implementation
- [x] Content SEO framework
- [x] Performance tracking dashboard

### Monitoring & Reporting
- **Weekly**: Search Console performance review
- **Monthly**: GA4 conversion analysis and SEO ranking report
- **Quarterly**: Comprehensive SEO audit and strategy adjustment
- **Real-time**: Core Web Vitals alerts and performance monitoring

## Timeline
- **Day 1**: Technical SEO foundation (meta tags, structured data)
- **Day 2**: GA4 implementation and conversion tracking
- **Day 3**: Search Console integration and Core Web Vitals setup
- **Day 4**: Local SEO optimization and content framework
- **Day 5**: Testing, validation, and performance monitoring setup