# Google Maps Integration Implementation
## SPEC_05 Group D Task 11 - Complete Implementation

### Overview
Professional Google Maps integration for Sabor con Flow Dance studio contact page featuring:
- Custom dark theme matching site branding
- Interactive map with custom marker
- Business info window with contact details
- Responsive design for all devices
- Error handling and accessibility features
- Performance optimization and analytics tracking

### Implementation Components

#### 1. Core JavaScript (`/static/js/google-maps.js`)
**Features:**
- `SaborMapsManager` class for complete map lifecycle management
- Dark theme styling with custom color palette
- Custom gold marker (#C7B375) matching brand colors
- Interactive info window with business details
- Responsive design handlers
- Error state management
- Performance monitoring and analytics integration

**Key Methods:**
- `initializeMap()` - Main initialization with error handling
- `createCustomMarker()` - Gold-colored marker with brand styling
- `createInfoWindow()` - Professional info popup with contact details
- `showMapError()` - Graceful fallback for API failures
- `handleResize()` - Responsive behavior management

#### 2. CSS Styling (`/static/css/google-maps.css`)
**Features:**
- Dark theme integration with black/gold branding
- Responsive grid layout with breakpoints at 768px and 480px
- Professional info window styling
- Loading states with animated spinner
- Error state styling with fallback information
- Print media queries
- High contrast and reduced motion accessibility support

**Responsive Design:**
- Desktop: 450px height, full-width container
- Tablet: 350px height, optimized touch targets
- Mobile: 300px height, compact info windows

#### 3. Django Integration

**Settings Configuration (`sabor_con_flow/settings.py`):**
```python
# Google Maps Configuration - SPEC_05 Group D Task 11
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
GOOGLE_MAPS_ZOOM_LEVEL = int(os.environ.get('GOOGLE_MAPS_ZOOM_LEVEL', '16'))
STUDIO_COORDINATES = {
    'latitude': float(os.environ.get('STUDIO_LATITUDE', '40.0150')),
    'longitude': float(os.environ.get('STUDIO_LONGITUDE', '-105.2705'))
}
ENABLE_GOOGLE_MAPS = os.environ.get('ENABLE_GOOGLE_MAPS', 'True').lower() in ('true', '1', 't')
```

**Environment Variables (`.env.example`):**
```bash
# Google Maps Configuration - SPEC_05 Group D Task 11
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here
GOOGLE_MAPS_ZOOM_LEVEL=16
STUDIO_LATITUDE=40.0150
STUDIO_LONGITUDE=-105.2705
ENABLE_GOOGLE_MAPS=True
```

**View Integration (`core/views.py`):**
```python
context = {
    'form': form,
    'page_title': 'Contact Us',
    # Google Maps configuration - SPEC_05 Group D Task 11
    'ENABLE_GOOGLE_MAPS': getattr(settings, 'ENABLE_GOOGLE_MAPS', False),
    'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    'GOOGLE_MAPS_ZOOM_LEVEL': getattr(settings, 'GOOGLE_MAPS_ZOOM_LEVEL', 16),
    'STUDIO_COORDINATES': getattr(settings, 'STUDIO_COORDINATES', {}),
    'BUSINESS_INFO': getattr(settings, 'BUSINESS_INFO', {}),
}
```

#### 4. Template Integration (`templates/contact.html`)

**Map Section:**
```html
<!-- Google Maps Section -->
{% if ENABLE_GOOGLE_MAPS and GOOGLE_MAPS_API_KEY %}
<div class="sabor-map-section">
    <div class="sabor-map-header">
        <h2>Visit Our Studio</h2>
        <p>Find us at Avalon Ballroom in the heart of Boulder</p>
    </div>
    <div id="sabor-google-map" class="loading" 
         role="application" 
         aria-label="Interactive map showing Sabor con Flow Dance studio location"
         tabindex="0">
        <!-- Map will be loaded here -->
    </div>
</div>
{% endif %}
```

**JavaScript Configuration:**
```html
<script>
window.SABOR_MAP_CONFIG = {
    apiKey: '{{ GOOGLE_MAPS_API_KEY }}',
    studioLocation: {
        lat: {{ STUDIO_COORDINATES.latitude }},
        lng: {{ STUDIO_COORDINATES.longitude }}
    },
    zoomLevel: {{ GOOGLE_MAPS_ZOOM_LEVEL }},
    businessInfo: {
        name: '{{ BUSINESS_INFO.name }}',
        address: '{{ BUSINESS_INFO.address }}',
        phone: '{{ BUSINESS_INFO.phone }}',
        email: '{{ BUSINESS_INFO.email }}'
    }
};
</script>
```

### Security & Performance Features

#### Security
- API key validation and error handling
- XSS protection through Django template escaping
- CSRF protection maintained on contact forms
- Secure HTTPS API calls

#### Performance
- Lazy loading with `async defer` script loading
- Response caching for map data
- Optimized marker rendering
- Progressive enhancement (graceful degradation)
- Performance monitoring integration

#### Accessibility
- ARIA labels for screen readers
- Keyboard navigation support
- High contrast mode support
- Reduced motion preferences
- Alternative text for all interactive elements

### Analytics Integration

**Event Tracking:**
- Map load success/failure
- Info window interactions
- Directions button clicks
- Error state triggers
- Performance metrics collection

**Google Analytics 4 Events:**
```javascript
gtag('event', 'map_loaded', {
    'event_category': 'google_maps',
    'event_label': 'contact_page_map',
    'value': 1
});
```

### Error Handling & Fallbacks

#### API Failure Handling
- Professional error message display
- Fallback location information
- External Google Maps link
- Graceful degradation without JavaScript

#### Network Issues
- Timeout handling for slow connections
- Retry mechanisms for transient failures
- Loading state indicators
- User-friendly error messages

### Business Configuration

**Studio Location:**
- **Address:** Avalon Ballroom, Boulder, CO
- **Coordinates:** 40.0150, -105.2705 (Boulder, Colorado)
- **Zoom Level:** 16 (neighborhood view)

**Contact Information:**
- **Phone:** (555) 123-4567
- **Email:** saborconflowdance@gmail.com
- **Website:** https://saborconflowdance.com

### Testing & Validation

#### Test File
- `test_google_maps.html` - Standalone testing page
- Manual API key input for development testing
- Visual verification of all features
- Mobile responsiveness testing

#### Key Test Points
1. Map loads with correct location and zoom
2. Dark theme applies correctly
3. Custom marker appears in gold color
4. Info window displays business information
5. Directions link opens Google Maps
6. Error states display properly
7. Mobile layout works correctly
8. Analytics events fire correctly

### Deployment Instructions

#### 1. Environment Setup
```bash
# Add to .env file
GOOGLE_MAPS_API_KEY=your-actual-api-key-here
GOOGLE_MAPS_ZOOM_LEVEL=16
STUDIO_LATITUDE=40.0150
STUDIO_LONGITUDE=-105.2705
ENABLE_GOOGLE_MAPS=True
```

#### 2. Google Cloud Console Setup
1. Enable Google Maps JavaScript API
2. Create API key with domain restrictions
3. Configure billing account (required for Maps API)
4. Set up quota limits and monitoring

#### 3. Domain Restrictions (Production)
```
https://saborconflowdance.com/*
https://www.saborconflowdance.com/*
https://*.vercel.app/*  (for staging)
```

#### 4. File Deployment
- Upload `/static/js/google-maps.js`
- Upload `/static/css/google-maps.css`
- Update `templates/contact.html`
- Deploy Django settings changes
- Collect static files: `python manage.py collectstatic`

### Monitoring & Maintenance

#### Performance Monitoring
- Core Web Vitals tracking
- Map load time analysis
- Error rate monitoring
- User interaction analytics

#### Regular Maintenance
- API quota monitoring
- Error log review
- Performance optimization
- Mobile compatibility testing

### Files Created/Modified

#### New Files
- `/static/js/google-maps.js` - Complete maps integration
- `/static/css/google-maps.css` - Professional styling
- `/test_google_maps.html` - Testing interface

#### Modified Files
- `/templates/contact.html` - Map integration
- `/sabor_con_flow/settings.py` - Configuration
- `/core/views.py` - Context variables
- `/.env.example` - Environment documentation

### Performance Metrics Target

#### Core Web Vitals Goals
- **LCP (Largest Contentful Paint):** < 2.0s
- **FID (First Input Delay):** < 50ms
- **CLS (Cumulative Layout Shift):** < 0.05

#### Additional Metrics
- Map initialization: < 1.5s
- API response time: < 500ms
- Mobile touch response: < 100ms

This implementation provides a professional, accessible, and performant Google Maps integration that enhances the user experience while maintaining the site's dark theme branding and mobile-first design principles.