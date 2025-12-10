# WhatsApp Chat Integration Setup Guide

## Overview
The WhatsApp floating chat button provides an easy way for visitors to contact Sabor con Flow directly through WhatsApp with a pre-filled message about dance classes.

## Quick Setup

### 1. Update Phone Number
Edit the file: `templates/components/whatsapp_button.html`

Change the `data-phone` attribute to your actual WhatsApp Business number:
```html
data-phone="17205555555"  <!-- Replace with your WhatsApp number -->
```

**Format:** Include country code without + symbol (e.g., 17205555555 for US number)

### 2. Customize Default Message
Edit the `data-message` attribute in the same file:
```html
data-message="Hi! I'm interested in Sabor con Flow dance classes."
```

### 3. WhatsApp Business Account
Ensure you have a WhatsApp Business account set up for the phone number you configure.

## Features

### Visual Design
- ✅ Sabor con Flow brand colors (Gold #C7B375 border on WhatsApp green)
- ✅ Floating button positioned in bottom-right corner
- ✅ Pulse animation to draw attention
- ✅ Hover tooltip showing "Chat with us!"
- ✅ Professional appearance matching site design

### Scroll Behavior
- ✅ Appears after 1-second delay
- ✅ Shows when scrolling down
- ✅ Hides when scrolling up
- ✅ Smooth animations and transitions

### Mobile Optimization
- ✅ Responsive positioning for different screen sizes
- ✅ Touch-friendly button size (50-60px)
- ✅ Proper spacing from mobile browser UI
- ✅ Landscape orientation support

### Accessibility Features
- ✅ WCAG 2.1 AA compliant
- ✅ Keyboard navigation support (Tab to focus)
- ✅ Screen reader announcements
- ✅ Proper ARIA labels and roles
- ✅ High contrast mode support
- ✅ Reduced motion preference respect

### Performance
- ✅ Lightweight CSS and JavaScript
- ✅ No external dependencies (uses existing Font Awesome)
- ✅ Optimized animations for 60fps
- ✅ Lazy initialization
- ✅ Memory efficient scroll handling

## File Structure

```
templates/components/whatsapp_button.html  # WhatsApp button component
static/css/whatsapp.css                   # Button styles and animations
static/js/whatsapp-chat.js               # Scroll behavior and functionality
```

## Configuration Options

The JavaScript provides a public API for advanced configuration:

```javascript
// Show/hide programmatically
WhatsAppChat.show();
WhatsAppChat.hide();
WhatsAppChat.toggle();

// Check visibility
console.log(WhatsAppChat.isVisible());

// Update phone number
WhatsAppChat.updatePhone('17205555555');

// Update default message
WhatsAppChat.updateMessage('New message text');

// Enable analytics tracking
WhatsAppChat.enableTracking();
```

## Testing

A test page is available at `test_whatsapp.html` for verification:

1. Open the test page in a browser
2. Test scroll behavior by scrolling up and down
3. Test mobile responsiveness using browser dev tools
4. Verify accessibility with keyboard navigation
5. Click button to test WhatsApp integration

## Analytics Integration

The component supports analytics tracking for:
- Button show/hide events
- Button clicks
- Scroll behavior
- Network connectivity changes

To enable, call `WhatsAppChat.enableTracking()` after page load.

## Browser Support

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+
- ✅ iOS Safari 12+
- ✅ Android Chrome 60+

## Troubleshooting

### Button Not Appearing
1. Check console for JavaScript errors
2. Verify Font Awesome is loaded
3. Ensure CSS files are properly linked
4. Check if container element exists

### Wrong Phone Number
1. Update `data-phone` attribute in component template
2. Use country code without + symbol
3. Verify WhatsApp Business account is active

### Scroll Behavior Issues
1. Check if page has sufficient scroll height
2. Verify JavaScript is not conflicting with other scroll handlers
3. Test with reduced motion preferences disabled

### Mobile Issues
1. Test on actual device, not just browser emulation
2. Check for viewport meta tag in base template
3. Verify touch events are working properly

## Security Notes

- Uses `rel="noopener noreferrer"` for external link security
- No personal data stored locally
- HTTPS required for optimal performance
- No tracking without explicit enablement

## Support

For issues or customization needs, refer to:
- Browser developer console for JavaScript errors
- CSS validation for styling issues
- Accessibility testing with screen readers
- Mobile testing on actual devices