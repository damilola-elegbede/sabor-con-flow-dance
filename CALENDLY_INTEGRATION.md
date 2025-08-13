# Calendly Widget Integration - SPEC_05 Group A Task 1

## Overview

This document provides complete implementation details for the Calendly booking widget integration, featuring Sabor con Flow brand customization, mobile optimization, and comprehensive error handling.

## Features Implemented

### ✅ Core Features
- **Inline Widget**: Full calendar view embedded directly in pages
- **Popup Widget**: Calendar opens in overlay modal
- **Badge Widget**: Floating button for persistent access
- **Custom Branding**: Sabor con Flow colors (#000000, #C7B375)
- **Mobile Responsive**: Optimized heights and touch interactions
- **Prefill Support**: URL parameters auto-populate booking forms
- **Event Tracking**: Analytics integration and conversion tracking
- **Error Handling**: Graceful degradation with fallback options

### ✅ Advanced Features
- **Loading States**: Branded loading animations
- **Accessibility**: ARIA labels, keyboard navigation, screen reader support
- **Performance**: Lazy loading, script optimization, error recovery
- **Analytics Integration**: Google Analytics, Facebook Pixel tracking
- **Custom Events**: JavaScript events for external integrations

## File Structure

```
├── templates/components/
│   └── calendly_widget.html          # Reusable widget component
├── static/js/
│   └── calendly.js                    # Widget initialization & management
├── templates/
│   ├── private_lessons.html           # Private lessons with booking
│   └── contact.html                   # Contact page with quick booking
├── .env.example                       # Environment variables template
└── CALENDLY_INTEGRATION.md            # This documentation
```

## Usage Examples

### Basic Inline Widget
```django
{% include 'components/calendly_widget.html' with type='inline' %}
```

### Popup with Custom Text
```django
{% include 'components/calendly_widget.html' with type='popup' text='Book Your Lesson' %}
```

### Badge Widget (Floating)
```django
{% include 'components/calendly_widget.html' with type='badge' text='Schedule Now' %}
```

### Advanced Configuration
```django
{% include 'components/calendly_widget.html' with 
   type='inline' 
   height=700 
   background_color='#000000'
   text_color='#C7B375'
   primary_color='#C7B375'
   hide_gdpr_banner=true 
%}
```

### Prefill Data Example
```django
{% include 'components/calendly_widget.html' with 
   type='popup' 
   prefill='{"name":"John Doe","email":"john@example.com","customAnswers":{"a1":"Private Lesson"}}'
%}
```

## URL Parameter Prefilling

The integration automatically maps URL parameters to Calendly fields:

| URL Parameter | Calendly Field | Example |
|---------------|----------------|---------|
| `name` | `name` | `?name=John%20Doe` |
| `first_name` | `firstName` | `?first_name=John` |
| `last_name` | `lastName` | `?last_name=Doe` |
| `email` | `email` | `?email=john@example.com` |
| `phone` | `phone` | `?phone=555-1234` |
| `lesson_type` | `customAnswers.a1` | `?lesson_type=Private%20Lesson` |
| `experience_level` | `customAnswers.a2` | `?experience_level=Beginner` |
| `preferred_time` | `customAnswers.a3` | `?preferred_time=Evening` |

### Example URLs with Prefill
```
/private-lessons/?name=Maria%20Garcia&email=maria@email.com&lesson_type=Private%20Lesson&experience_level=Intermediate

/contact/?first_name=Carlos&last_name=Rodriguez&phone=555-0123&preferred_time=Weekends
```

## Environment Variables

Add these variables to your `.env` file:

```env
# Calendly Integration - SPEC_05 Group A
CALENDLY_URL=https://calendly.com/saborconflowdance
CALENDLY_API_KEY=your-calendly-api-key-here
CALENDLY_ORGANIZATION_UUID=your-calendly-organization-uuid-here
CALENDLY_USER_UUID=your-calendly-user-uuid-here
CALENDLY_WEBHOOK_SECRET=your-calendly-webhook-secret-here
```

### Getting Calendly API Credentials

1. **Calendly URL**: Your public booking page URL
   - Format: `https://calendly.com/your-username`
   - Found in: Calendly Dashboard → Event Types

2. **API Key**: For webhook verification and API calls
   - Get from: Calendly Dashboard → Integrations → API & Webhooks
   - Generate: Personal Access Token

3. **Organization/User UUIDs**: For advanced API integration
   - Get via: Calendly API `/users/me` endpoint
   - Documentation: https://developer.calendly.com/api-docs

## JavaScript API

### Global Methods
```javascript
// Open popup manually
window.calendlyAPI.openPopup('https://calendly.com/saborconflowdance', {
    prefill: { name: 'John Doe', email: 'john@example.com' }
});

// Get analytics data
const stats = window.calendlyAPI.getAnalytics();
console.log(stats); // { widgetLoads: 5, bookingAttempts: 3, completedBookings: 1 }

// Clean up
window.calendlyAPI.destroy();
```

### Event Listeners
```javascript
// Listen for booking completion
document.addEventListener('calendly:booking_completed', function(event) {
    console.log('Booking completed!', event.detail);
    // Custom success actions
});

// Listen for errors
document.addEventListener('calendly:error', function(event) {
    console.log('Calendly error:', event.detail);
    // Custom error handling
});

// Listen for profile/event views
document.addEventListener('calendly:profile_viewed', function(event) {
    console.log('Profile viewed:', event.detail);
});
```

## Customization Options

### Widget Component Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | String | `'inline'` | Widget type: 'inline', 'popup', 'badge' |
| `url` | String | Settings value | Calendly booking URL |
| `text` | String | `'Schedule a Lesson'` | Button text for popup/badge |
| `height` | Number | `630` | Height for inline widget |
| `prefill` | Object | `{}` | Prefill data object |
| `hide_gdpr_banner` | Boolean | `true` | Hide GDPR consent banner |
| `hide_landing_page_details` | Boolean | `false` | Hide landing page details |
| `background_color` | String | `'#000000'` | Widget background color |
| `text_color` | String | `'#C7B375'` | Widget text color |
| `primary_color` | String | `'#C7B375'` | Primary button color |

### Theme Customization

The integration uses Sabor con Flow brand colors by default:

```css
:root {
    --calendly-background: #000000;    /* Black background */
    --calendly-text: #C7B375;          /* Gold text */
    --calendly-primary: #C7B375;       /* Gold buttons */
    --calendly-secondary: #BFAA65;     /* Light gold accents */
}
```

## Mobile Optimization

### Responsive Behavior
- **Inline widgets**: Auto-adjust height based on screen size
- **Popup widgets**: Full-screen modal on mobile devices  
- **Badge widgets**: Optimized positioning for mobile interactions
- **Touch targets**: Minimum 44px touch targets for accessibility

### Performance Features
- **Lazy loading**: Scripts load only when needed
- **Preconnect**: DNS prefetch for Calendly domains in base template
- **Error recovery**: Automatic retry with exponential backoff
- **Network awareness**: Adapts to slow connections

## Error Handling & Fallbacks

### Graceful Degradation
1. **JavaScript disabled**: Shows direct Calendly link
2. **Script load failure**: Displays fallback booking options
3. **Network errors**: Automatic retry with user feedback
4. **Widget errors**: User-friendly error messages with alternatives

### Error Recovery
```javascript
// Automatic retry logic
maxRetries: 3,
retryDelay: 1000,    // 1 second initial delay
loadTimeout: 10000   // 10 second timeout
```

### Fallback Content
When JavaScript fails:
```html
<noscript>
    <div class="calendly-fallback">
        <h3>Schedule Your Dance Lesson</h3>
        <p>JavaScript is required to use our booking system...</p>
        <a href="https://calendly.com/saborconflowdance" 
           target="_blank" class="btn btn-primary">
            Open Calendly in New Tab
        </a>
    </div>
</noscript>
```

## Analytics Integration

### Conversion Tracking
```javascript
// Google Analytics 4
gtag('event', 'booking_completed', {
    'event_category': 'calendly',
    'event_label': 'private_lesson',
    'value': 1
});

// Facebook Pixel
fbq('track', 'Schedule', {
    content_name: 'Private Lesson Booking',
    content_category: 'Dance Lessons'
});
```

### Custom Analytics
```javascript
// Built-in analytics tracking
{
    widgetLoads: 5,           // Widgets successfully loaded
    bookingAttempts: 3,       // Users clicked to book
    completedBookings: 1,     // Successful bookings
    errors: []                // Error log with timestamps
}
```

## Security Features

### Data Sanitization
- **Input validation**: All prefill data sanitized
- **XSS prevention**: Proper escaping of user inputs
- **CSRF protection**: Django CSRF tokens in forms
- **Content Security Policy**: Strict CSP for external scripts

### Privacy Compliance
- **GDPR banner**: Can be hidden if organization handles consent
- **Data minimization**: Only necessary data passed to Calendly
- **Secure transmission**: All data sent over HTTPS
- **Cookie policy**: Follows Calendly's privacy policy

## Testing Guidelines

### Manual Testing Checklist
- [ ] Inline widget loads and displays correctly
- [ ] Popup widget opens on button click
- [ ] Badge widget appears as floating button
- [ ] Mobile responsive behavior works
- [ ] Loading states show appropriate branding
- [ ] Error states display fallback options
- [ ] Prefill parameters populate correctly
- [ ] Analytics events fire on booking completion

### Browser Testing
- [ ] Chrome (desktop & mobile)
- [ ] Safari (desktop & mobile)
- [ ] Firefox (desktop & mobile)
- [ ] Edge (desktop)

### Network Testing
- [ ] Slow 3G connection
- [ ] Offline behavior
- [ ] Script loading failures
- [ ] CDN unavailability

## Deployment Steps

1. **Add Environment Variables**
   ```bash
   # In Vercel dashboard or deployment platform
   CALENDLY_URL=https://calendly.com/saborconflowdance
   ```

2. **Verify DNS Prefetch**
   - Ensure `//assets.calendly.com` is in base template preconnect

3. **Test Widget Loading**
   - Check all three widget types on staging
   - Verify mobile responsiveness
   - Test error scenarios

4. **Configure Analytics**
   - Update Google Analytics conversion IDs
   - Set up Facebook Pixel events
   - Test event firing

5. **Monitor Performance**
   - Check Core Web Vitals impact
   - Monitor script loading times
   - Track booking conversion rates

## Troubleshooting

### Common Issues

**Widget not loading**
- Check console for JavaScript errors
- Verify Calendly URL is accessible
- Ensure script loads from CDN

**Mobile display issues**
- Check viewport meta tag
- Verify CSS media queries
- Test touch interactions

**Prefill not working**
- Verify URL parameter encoding
- Check JavaScript console for parsing errors
- Ensure parameter mapping is correct

**Analytics not tracking**
- Verify Google Analytics is loaded
- Check event names match configuration
- Ensure tracking IDs are correct

### Debug Mode
```javascript
// Enable debug logging
localStorage.setItem('calendly_debug', 'true');

// View analytics
console.log(window.calendlyAPI.getAnalytics());
```

## Support & Maintenance

### Regular Tasks
- **Monthly**: Review booking analytics and conversion rates
- **Quarterly**: Update Calendly API integration if needed
- **Annually**: Review and update prefill field mapping

### Monitoring
- **Performance**: Core Web Vitals impact
- **Errors**: JavaScript console errors and user reports
- **Conversions**: Booking completion rates
- **User Experience**: Mobile usability metrics

## Future Enhancements

### Planned Features
- [ ] Multi-language support for widget text
- [ ] Advanced prefill from user accounts
- [ ] Integration with CRM systems
- [ ] Custom booking confirmation pages
- [ ] Automated email sequences
- [ ] SMS reminder integration

### API Extensions
- [ ] Calendly webhook handling for booking updates
- [ ] Custom availability checking
- [ ] Dynamic pricing based on booking time
- [ ] Group lesson booking support

---

## Quick Reference

### Widget Types
```django
{# Inline calendar view #}
{% include 'components/calendly_widget.html' with type='inline' %}

{# Popup button #}
{% include 'components/calendly_widget.html' with type='popup' text='Book Now' %}

{# Floating badge #}
{% include 'components/calendly_widget.html' with type='badge' text='Schedule' %}
```

### JavaScript Events
```javascript
calendly:booking_completed    // Booking successful
calendly:profile_viewed       // Calendar page viewed
calendly:datetime_selected    // Date/time chosen
calendly:error               // Error occurred
```

### Required Files
- `templates/components/calendly_widget.html`
- `static/js/calendly.js`
- Environment variables in `.env`
- Calendly CSS preloaded in `base.html`

For questions or issues, refer to the Calendly Developer Documentation: https://developer.calendly.com/