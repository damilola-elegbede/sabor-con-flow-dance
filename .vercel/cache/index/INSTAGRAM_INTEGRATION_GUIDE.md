# Instagram Integration Setup Guide

This guide covers the complete setup and configuration of Instagram integration features for the Sabor con Flow Dance website.

## Overview

The Instagram integration includes:
- Instagram Basic Display API connection
- Automatic post synchronization
- Gallery integration with filtering
- Social follow components
- Real-time webhook updates
- Rate limiting and error handling

## Prerequisites

1. **Instagram Business Account**: Convert your Instagram account to a business account
2. **Facebook Developer Account**: Required for Instagram Basic Display API
3. **SSL Certificate**: Instagram webhooks require HTTPS endpoints
4. **Domain Access**: For webhook verification

## 1. Instagram App Setup

### Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "Create App" → "Business" → "Next"
3. Enter app details:
   - App Name: "Sabor Con Flow Dance Website"
   - Contact Email: Your email
   - Purpose: "Yourself or your own business"

### Step 2: Add Instagram Basic Display

1. In your Facebook app dashboard
2. Click "Add Product" → Find "Instagram Basic Display" → "Set Up"
3. Go to Instagram Basic Display → Basic Display
4. Add Instagram Testers (your Instagram account)

### Step 3: Configure OAuth Redirect URIs

Add these redirect URIs in Instagram Basic Display settings:
```
https://yourdomain.com/auth/instagram/callback/
https://localhost:8000/auth/instagram/callback/  (for development)
```

### Step 4: Get App Credentials

From Basic Display settings, note down:
- Instagram App ID
- Instagram App Secret
- Client OAuth URI

## 2. Environment Configuration

Update your `.env` file with Instagram credentials:

```bash
# Instagram Integration
INSTAGRAM_ACCESS_TOKEN=your-long-lived-access-token-here
INSTAGRAM_CLIENT_ID=your-instagram-app-client-id-here
INSTAGRAM_CLIENT_SECRET=your-instagram-app-client-secret-here
INSTAGRAM_WEBHOOK_VERIFY_TOKEN=your-custom-webhook-verify-token-here

# Social Media Links
INSTAGRAM_URL=https://instagram.com/saborconflowdance
FACEBOOK_URL=https://facebook.com/saborconflowdance
WHATSAPP_NUMBER=1234567890
WHATSAPP_MESSAGE=Hi%20Sabor%20Con%20Flow!%20I'm%20interested%20in%20your%20dance%20classes.
```

## 3. Getting Access Token

### Method 1: Manual Authorization (Recommended for initial setup)

1. **Authorization URL**: 
```
https://api.instagram.com/oauth/authorize
  ?client_id={your-instagram-app-id}
  &redirect_uri=https://yourdomain.com/auth/instagram/callback/
  &scope=user_profile,user_media
  &response_type=code
```

2. **Exchange Code for Token**:
```bash
curl -X POST \
  https://api.instagram.com/oauth/access_token \
  -F client_id={your-instagram-app-id} \
  -F client_secret={your-instagram-app-secret} \
  -F grant_type=authorization_code \
  -F redirect_uri=https://yourdomain.com/auth/instagram/callback/ \
  -F code={authorization-code-from-step-1}
```

3. **Exchange for Long-Lived Token**:
```bash
curl -X GET \
  "https://graph.instagram.com/access_token
  ?grant_type=ig_exchange_token
  &client_secret={your-instagram-app-secret}
  &access_token={short-lived-access-token}"
```

### Method 2: Using Django Management Command

After setting up basic credentials:

```bash
# This command will guide you through the OAuth flow
python manage.py setup_instagram_auth
```

## 4. Database Migration

Run the Instagram integration migration:

```bash
python manage.py migrate
```

This adds the following fields to MediaGallery:
- `source` (local/url/instagram)
- `instagram_id`
- `instagram_permalink`
- `instagram_username`
- `instagram_timestamp`

## 5. Initial Instagram Sync

Sync your Instagram posts with the gallery:

```bash
# Sync latest 12 posts
python manage.py sync_instagram

# Sync with custom options
python manage.py sync_instagram --limit 20 --category instagram --featured

# Dry run to see what would be synced
python manage.py sync_instagram --dry-run

# Force refresh (ignore cache)
python manage.py sync_instagram --force

# Delete posts no longer on Instagram
python manage.py sync_instagram --delete-removed
```

### Sync Options

- `--limit N`: Number of posts to fetch (default: 12)
- `--force`: Ignore cache, fetch fresh data
- `--dry-run`: Show what would be done without making changes
- `--delete-removed`: Delete posts no longer on Instagram
- `--category CAT`: Category to assign to Instagram posts
- `--featured`: Mark synced posts as featured

## 6. Webhook Setup (Optional but Recommended)

Webhooks enable real-time updates when you post new content.

### Step 1: Configure Webhook in Facebook App

1. Go to Instagram Basic Display → Webhooks
2. Add webhook URL: `https://yourdomain.com/webhooks/instagram/`
3. Verify token: Use the token from your `.env` file
4. Subscribe to: `media` (for new posts/updates)

### Step 2: Test Webhook

```bash
# Test webhook verification
curl -X GET \
  "https://yourdomain.com/webhooks/instagram/
  ?hub.mode=subscribe
  &hub.verify_token=your-webhook-verify-token
  &hub.challenge=test-challenge"
```

Should return: `test-challenge`

### Step 3: Webhook Events

The webhook will automatically:
- Add new Instagram posts to your gallery
- Update existing posts if content changes
- Mark posts as inactive if deleted from Instagram

## 7. Gallery Integration

### Template Usage

The Instagram integration is automatically included in the gallery:

```html
<!-- In templates/gallery/index.html -->
{% if selected_category == 'instagram' and instagram_posts %}
    {% include 'components/instagram_feed.html' %}
{% endif %}
```

### URL Parameters

- `?category=instagram`: Show only Instagram posts
- `?type=image`: Filter by media type
- `?instagram=false`: Disable Instagram loading

### Custom Integration

Include Instagram feed in any template:

```html
{% load static %}

<!-- Load Instagram posts in view context -->
<!-- In your view: instagram_posts = get_instagram_posts(limit=8) -->

{% include 'components/instagram_feed.html' %}
```

## 8. Social Follow Integration

Add social follow buttons to any page:

```html
{% include 'components/social_follow_section.html' %}
```

This component includes:
- Instagram follow button with gradient styling
- Facebook and WhatsApp links
- Hashtag promotion
- Responsive design

## 9. API Rate Limiting

The integration includes automatic rate limiting:

- **Rate Limit**: 200 requests/hour (Instagram limit)
- **Cache Duration**: 30 minutes for posts
- **Retry Logic**: Exponential backoff for failed requests
- **Error Handling**: Graceful degradation when API unavailable

### Manual Rate Limit Check

```python
from core.utils.instagram_api import InstagramAPI

api = InstagramAPI()
can_make_request = api._check_rate_limit()
```

## 10. Monitoring and Maintenance

### Access Token Refresh

Long-lived tokens last 60 days and can be refreshed:

```bash
# Manual refresh
python manage.py refresh_instagram_token

# Or programmatically
from core.utils.instagram_api import refresh_instagram_token
success, new_token = refresh_instagram_token()
```

### Monitoring

Check logs for Instagram integration issues:

```bash
# Check recent Instagram API calls
tail -f logs/django.log | grep instagram

# Check webhook deliveries
tail -f logs/django.log | grep webhook
```

### Common Issues

1. **"Invalid access token"**
   - Token expired (refresh needed)
   - Account permissions changed
   - App was reset

2. **"Rate limit exceeded"**
   - Too many API calls
   - Check cache settings
   - Reduce sync frequency

3. **"Webhook verification failed"**
   - Wrong verify token
   - HTTPS not properly configured
   - App configuration mismatch

## 11. Customization

### Custom Instagram Post Processing

Extend the sync command for custom processing:

```python
# In core/management/commands/sync_instagram.py
def _process_instagram_post(self, post_data, existing_post, category, mark_featured, dry_run):
    # Add your custom logic here
    # e.g., auto-tag posts based on hashtags
    # e.g., set different categories based on content
    pass
```

### Custom Styling

Instagram components use CSS custom properties:

```css
/* Custom Instagram gradient */
:root {
    --instagram-gradient: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
}

.instagram-btn {
    background: var(--instagram-gradient);
}
```

## 12. Security Considerations

1. **Environment Variables**: Never commit real tokens to git
2. **HTTPS Only**: Instagram webhooks require SSL
3. **Token Rotation**: Refresh tokens regularly
4. **Rate Limiting**: Respect Instagram's API limits
5. **Error Handling**: Don't expose API errors to users

## 13. Production Deployment

### Vercel Environment Variables

In Vercel dashboard, add environment variables:
- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_CLIENT_ID` 
- `INSTAGRAM_CLIENT_SECRET`
- `INSTAGRAM_WEBHOOK_VERIFY_TOKEN`

### Automated Sync

Set up a cron job or scheduled task:

```bash
# Every 6 hours
0 */6 * * * /path/to/python /path/to/manage.py sync_instagram --limit 12
```

### Webhook Monitoring

Monitor webhook delivery success in Facebook Developer tools.

## 14. Troubleshooting

### Debug Mode

Enable debug logging:

```python
# In settings.py
LOGGING = {
    'loggers': {
        'core.utils.instagram_api': {
            'level': 'DEBUG',
        },
    },
}
```

### Test Commands

```bash
# Test API connection
python manage.py shell
>>> from core.utils.instagram_api import InstagramAPI
>>> api = InstagramAPI()
>>> posts = api.get_user_media(limit=1)
>>> print(posts)

# Test webhook endpoint
curl -X POST https://yourdomain.com/webhooks/instagram/ \
  -H "Content-Type: application/json" \
  -d '{"object":"instagram","entry":[{"id":"test"}]}'
```

## Support

For additional support:
1. Check Instagram Basic Display API documentation
2. Review Django logs for error details
3. Test API endpoints manually
4. Verify webhook configuration

The integration is designed to be robust and handle API failures gracefully, ensuring your website continues to function even when Instagram services are unavailable.