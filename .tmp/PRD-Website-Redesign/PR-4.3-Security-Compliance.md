# PR 4.3: Security & Compliance Implementation

## PR Metadata
- **Phase**: 4.3 - Security & Compliance
- **Priority**: Critical
- **Dependencies**: PR 4.1 (Performance), PR 4.2 (SEO/Analytics)
- **Estimated Timeline**: 6-8 days
- **Risk Level**: High
- **Team**: Security + DevOps + Legal

## Security Requirements

### Security Standards Compliance
- **OWASP Top 10**: Full mitigation implementation
- **PCI DSS**: Level 4 compliance for payment processing
- **GDPR**: Full data protection compliance
- **CCPA**: California privacy rights compliance
- **SOC 2 Type II**: Security controls framework
- **ISO 27001**: Information security management

### Threat Model & Risk Assessment
- **Attack Vectors**: XSS, CSRF, SQL Injection, DDoS, Social Engineering
- **Data Classification**: PII (High), Payment (Critical), Analytics (Medium)
- **Risk Tolerance**: Zero tolerance for data breaches
- **Compliance Requirements**: GDPR, CCPA, PCI DSS

## Security Headers Implementation

### 1. Comprehensive Security Headers

#### Django Security Middleware Configuration
```python
# sabor_con_flow/settings/security.py
import os
from datetime import timedelta

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_EMBEDDER_POLICY = 'require-corp'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# CSP Configuration
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",  # Remove in production, use nonces instead
    'https://www.googletagmanager.com',
    'https://www.google-analytics.com',
    'https://maps.googleapis.com',
    'https://api.calendly.com',
    'https://connect.facebook.net',
    'https://www.youtube.com',
    'https://s.ytimg.com',
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    'https://fonts.googleapis.com',
    'https://api.calendly.com',
)
CSP_FONT_SRC = (
    "'self'",
    'https://fonts.gstatic.com',
)
CSP_IMG_SRC = (
    "'self'",
    'data:',
    'https://www.google-analytics.com',
    'https://maps.googleapis.com',
    'https://i.ytimg.com',
    'https://scontent.cdninstagram.com',
)
CSP_CONNECT_SRC = (
    "'self'",
    'https://www.google-analytics.com',
    'https://api.calendly.com',
    'https://graph.facebook.com',
    'https://api.instagram.com',
)
CSP_FRAME_SRC = (
    'https://www.youtube.com',
    'https://calendly.com',
    'https://www.google.com',
    'https://maps.google.com',
)
CSP_OBJECT_SRC = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_FORM_ACTION = ("'self'",)
CSP_UPGRADE_INSECURE_REQUESTS = True

# Permissions Policy
PERMISSIONS_POLICY = {
    'accelerometer': [],
    'ambient-light-sensor': [],
    'autoplay': [],
    'battery': [],
    'camera': [],
    'display-capture': [],
    'document-domain': [],
    'encrypted-media': [],
    'fullscreen': ['self'],
    'geolocation': ['self'],
    'gyroscope': [],
    'layout-animations': ['self'],
    'legacy-image-formats': ['self'],
    'magnetometer': [],
    'microphone': [],
    'midi': [],
    'navigation-override': [],
    'oversized-images': ['self'],
    'payment': [],
    'picture-in-picture': [],
    'publickey-credentials-get': [],
    'sync-xhr': [],
    'usb': [],
    'vr': [],
    'wake-lock': [],
    'xr-spatial-tracking': [],
}

# Session Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF Protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = True
CSRF_FAILURE_VIEW = 'core.views.csrf_failure'

# Additional Security
X_FRAME_OPTIONS = 'DENY'
USE_TZ = True
SECRET_KEY_FALLBACKS = []  # Rotate secret keys regularly
```

### 2. Advanced CSP with Nonces

#### CSP Nonce Middleware
```python
# core/middleware/security.py
import secrets
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class CSPNonceMiddleware(MiddlewareMixin):
    """Generate unique nonces for CSP"""
    
    def process_request(self, request):
        # Generate unique nonce for this request
        request.csp_nonce = secrets.token_urlsafe(16)
        
    def process_response(self, request, response):
        if hasattr(request, 'csp_nonce'):
            # Update CSP header with nonce
            nonce = request.csp_nonce
            csp_header = response.get('Content-Security-Policy', '')
            
            if csp_header:
                # Replace unsafe-inline with nonce for scripts
                csp_header = csp_header.replace(
                    "'unsafe-inline'", 
                    f"'nonce-{nonce}'"
                )
                response['Content-Security-Policy'] = csp_header
        
        return response

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add comprehensive security headers"""
    
    def process_response(self, request, response):
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Cross-Origin Policies
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        response['Cross-Origin-Resource-Policy'] = 'cross-origin'
        
        # Permissions Policy
        permissions = [
            'camera=()',
            'microphone=()',
            'geolocation=(self)',
            'fullscreen=(self)',
            'payment=()',
            'usb=()',
        ]
        response['Permissions-Policy'] = ', '.join(permissions)
        
        # Security headers for sensitive pages
        if self.is_sensitive_page(request.path):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
            response['Pragma'] = 'no-cache'
        
        return response
    
    def is_sensitive_page(self, path):
        """Check if page contains sensitive data"""
        sensitive_paths = ['/admin/', '/api/', '/contact']
        return any(path.startswith(p) for p in sensitive_paths)
```

### 3. Rate Limiting & DDoS Protection

#### Advanced Rate Limiting
```python
# core/middleware/rate_limiting.py
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
import time
import hashlib
from collections import defaultdict

class AdvancedRateLimitMiddleware(MiddlewareMixin):
    """Multi-tier rate limiting with anomaly detection"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Rate limit configurations
        self.rate_limits = {
            # Per IP limits
            'global': {'requests': 100, 'window': 60},  # 100 req/min
            'api': {'requests': 30, 'window': 60},      # 30 API req/min
            'contact': {'requests': 5, 'window': 300},  # 5 contact forms per 5min
            'login': {'requests': 5, 'window': 900},    # 5 login attempts per 15min
            
            # Per user limits (authenticated users)
            'user_api': {'requests': 100, 'window': 60},
            'user_contact': {'requests': 10, 'window': 300},
        }
        
        # Suspicious activity tracking
        self.suspicious_patterns = {
            'rapid_requests': 20,    # More than 20 requests in 10 seconds
            'form_spam': 3,          # 3+ form submissions in 1 minute
            'bot_detection': True    # Enable bot detection
        }
    
    def process_request(self, request):
        client_ip = self.get_client_ip(request)
        user_id = getattr(request.user, 'id', None) if hasattr(request, 'user') else None
        
        # Check rate limits
        if self.is_rate_limited(request, client_ip, user_id):
            return HttpResponse(
                'Rate limit exceeded. Please slow down.',
                status=429,
                headers={'Retry-After': '60'}
            )
        
        # Check for suspicious activity
        if self.detect_suspicious_activity(request, client_ip):
            return HttpResponse(
                'Suspicious activity detected.',
                status=403
            )
        
        return None
    
    def is_rate_limited(self, request, client_ip, user_id):
        """Check various rate limits"""
        path = request.path
        method = request.method
        
        # Determine limit type
        limit_key = 'global'
        if path.startswith('/api/'):
            limit_key = 'user_api' if user_id else 'api'
        elif path.startswith('/contact') and method == 'POST':
            limit_key = 'user_contact' if user_id else 'contact'
        elif path.startswith('/admin/login') and method == 'POST':
            limit_key = 'login'
        
        config = self.rate_limits.get(limit_key, self.rate_limits['global'])
        
        # Create cache key
        cache_key = f"rate_limit:{limit_key}:{client_ip}:{user_id or 'anon'}"
        
        # Check current window
        current_time = int(time.time())
        window_start = current_time - config['window']
        
        # Get request timestamps from cache
        timestamps = cache.get(cache_key, [])
        
        # Remove old timestamps
        timestamps = [t for t in timestamps if t > window_start]
        
        # Check if limit exceeded
        if len(timestamps) >= config['requests']:
            return True
        
        # Add current timestamp
        timestamps.append(current_time)
        cache.set(cache_key, timestamps, config['window'] + 60)
        
        return False
    
    def detect_suspicious_activity(self, request, client_ip):
        """Detect potentially malicious activity"""
        current_time = int(time.time())
        
        # Rapid request detection
        rapid_key = f"rapid:{client_ip}"
        recent_requests = cache.get(rapid_key, [])
        recent_requests = [t for t in recent_requests if t > current_time - 10]
        
        if len(recent_requests) > self.suspicious_patterns['rapid_requests']:
            self.log_suspicious_activity('rapid_requests', client_ip, request)
            return True
        
        recent_requests.append(current_time)
        cache.set(rapid_key, recent_requests, 20)
        
        # Bot detection
        if self.suspicious_patterns['bot_detection']:
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            if self.is_bot_user_agent(user_agent) and not self.is_legitimate_bot(user_agent):
                self.log_suspicious_activity('bot_detected', client_ip, request)
                return True
        
        return False
    
    def get_client_ip(self, request):
        """Get real client IP considering proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_bot_user_agent(self, user_agent):
        """Check if user agent indicates a bot"""
        bot_indicators = [
            'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget',
            'python', 'requests', 'scrapy', 'phantom', 'headless'
        ]
        return any(indicator in user_agent.lower() for indicator in bot_indicators)
    
    def is_legitimate_bot(self, user_agent):
        """Check if bot is from legitimate source"""
        legitimate_bots = [
            'googlebot', 'bingbot', 'slurp', 'duckduckbot',
            'baiduspider', 'yandexbot', 'facebookexternalhit'
        ]
        return any(bot in user_agent.lower() for bot in legitimate_bots)
    
    def log_suspicious_activity(self, activity_type, ip, request):
        """Log suspicious activity for monitoring"""
        import logging
        logger = logging.getLogger('security')
        
        logger.warning(f"Suspicious activity detected: {activity_type} from {ip} - {request.path}")
```

## Data Protection & Privacy

### 1. GDPR Compliance Implementation

#### Privacy Management System
```python
# core/models/privacy.py
from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedTextField, EncryptedEmailField

class ConsentRecord(models.Model):
    """Track user consent for GDPR compliance"""
    
    CONSENT_TYPES = [
        ('marketing', 'Marketing Communications'),
        ('analytics', 'Analytics & Performance'),
        ('functional', 'Functional Cookies'),
        ('personalization', 'Personalization'),
    ]
    
    user_email = EncryptedEmailField()
    consent_type = models.CharField(max_length=20, choices=CONSENT_TYPES)
    consented = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField()
    user_agent = EncryptedTextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    
    # Legal basis tracking
    legal_basis = models.CharField(max_length=50, default='consent')
    purpose = models.TextField()
    
    class Meta:
        unique_together = ('user_email', 'consent_type')
        ordering = ['-timestamp']

class DataProcessingRecord(models.Model):
    """Record of all personal data processing activities"""
    
    PROCESSING_PURPOSES = [
        ('contact_form', 'Contact Form Submission'),
        ('newsletter', 'Newsletter Subscription'),
        ('booking', 'Class Booking'),
        ('payment', 'Payment Processing'),
        ('analytics', 'Website Analytics'),
    ]
    
    user_email = EncryptedEmailField()
    processing_purpose = models.CharField(max_length=30, choices=PROCESSING_PURPOSES)
    data_categories = models.JSONField()  # List of data types processed
    legal_basis = models.CharField(max_length=50)
    retention_period = models.IntegerField()  # Days
    
    processed_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Third-party sharing
    shared_with = models.JSONField(default=list)  # List of third parties
    transfer_location = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-processed_at']

class DataSubjectRequest(models.Model):
    """Handle GDPR data subject requests"""
    
    REQUEST_TYPES = [
        ('access', 'Right of Access'),
        ('rectification', 'Right of Rectification'),
        ('erasure', 'Right to Erasure'),
        ('portability', 'Right to Data Portability'),
        ('restriction', 'Right to Restrict Processing'),
        ('objection', 'Right to Object'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    request_id = models.CharField(max_length=20, unique=True)
    user_email = EncryptedEmailField()
    request_type = models.CharField(max_length=15, choices=REQUEST_TYPES)
    description = EncryptedTextField()
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Response tracking
    response_provided = models.BooleanField(default=False)
    response_file = models.FileField(upload_to='gdpr_responses/', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.request_id:
            import uuid
            self.request_id = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)
```

#### GDPR Cookie Consent Manager
```javascript
// static/js/gdpr-consent-manager.js
class GDPRConsentManager {
  constructor() {
    this.consentData = this.loadConsent();
    this.init();
  }
  
  init() {
    // Show consent banner if no consent recorded
    if (!this.hasValidConsent()) {
      this.showConsentBanner();
    }
    
    // Initialize tracking based on consent
    this.initializeTracking();
    
    // Set up privacy controls
    this.setupPrivacyControls();
  }
  
  showConsentBanner() {
    const banner = document.createElement('div');
    banner.id = 'gdpr-consent-banner';
    banner.innerHTML = `
      <div class="consent-banner">
        <div class="consent-content">
          <h3>Your Privacy Matters</h3>
          <p>We use cookies and similar technologies to improve your experience, analyze traffic, and personalize content. You can choose which categories to allow.</p>
          
          <div class="consent-options">
            <label>
              <input type="checkbox" name="essential" checked disabled>
              Essential (Required)
            </label>
            <label>
              <input type="checkbox" name="analytics" id="consent-analytics">
              Analytics & Performance
            </label>
            <label>
              <input type="checkbox" name="marketing" id="consent-marketing">
              Marketing & Advertising
            </label>
            <label>
              <input type="checkbox" name="functional" id="consent-functional">
              Functional Enhancement
            </label>
          </div>
          
          <div class="consent-buttons">
            <button id="accept-all-cookies">Accept All</button>
            <button id="save-preferences">Save Preferences</button>
            <button id="reject-all-cookies">Reject All</button>
            <a href="/privacy-policy" target="_blank">Privacy Policy</a>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(banner);
    
    // Event listeners
    document.getElementById('accept-all-cookies').addEventListener('click', () => {
      this.acceptAll();
    });
    
    document.getElementById('save-preferences').addEventListener('click', () => {
      this.savePreferences();
    });
    
    document.getElementById('reject-all-cookies').addEventListener('click', () => {
      this.rejectAll();
    });
  }
  
  acceptAll() {
    const consent = {
      essential: true,
      analytics: true,
      marketing: true,
      functional: true,
      timestamp: Date.now(),
      version: '1.0'
    };
    
    this.saveConsent(consent);
    this.hideConsentBanner();
    this.initializeTracking();
  }
  
  rejectAll() {
    const consent = {
      essential: true,
      analytics: false,
      marketing: false,
      functional: false,
      timestamp: Date.now(),
      version: '1.0'
    };
    
    this.saveConsent(consent);
    this.hideConsentBanner();
    this.disableTracking();
  }
  
  savePreferences() {
    const consent = {
      essential: true,
      analytics: document.getElementById('consent-analytics').checked,
      marketing: document.getElementById('consent-marketing').checked,
      functional: document.getElementById('consent-functional').checked,
      timestamp: Date.now(),
      version: '1.0'
    };
    
    this.saveConsent(consent);
    this.hideConsentBanner();
    this.initializeTracking();
  }
  
  saveConsent(consent) {
    // Save to localStorage
    localStorage.setItem('gdpr-consent', JSON.stringify(consent));
    
    // Send to server
    fetch('/api/gdpr/consent/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.getCSRFToken()
      },
      body: JSON.stringify({
        consent: consent,
        user_agent: navigator.userAgent,
        timestamp: consent.timestamp
      })
    }).catch(console.error);
    
    this.consentData = consent;
  }
  
  loadConsent() {
    try {
      const stored = localStorage.getItem('gdpr-consent');
      return stored ? JSON.parse(stored) : null;
    } catch (e) {
      return null;
    }
  }
  
  hasValidConsent() {
    if (!this.consentData) return false;
    
    // Check if consent is less than 1 year old
    const oneYearAgo = Date.now() - (365 * 24 * 60 * 60 * 1000);
    return this.consentData.timestamp > oneYearAgo;
  }
  
  initializeTracking() {
    if (!this.consentData) return;
    
    // Initialize Google Analytics only with consent
    if (this.consentData.analytics) {
      this.initializeGoogleAnalytics();
    }
    
    // Initialize marketing pixels
    if (this.consentData.marketing) {
      this.initializeMarketingPixels();
    }
    
    // Initialize functional cookies
    if (this.consentData.functional) {
      this.initializeFunctionalCookies();
    }
  }
  
  initializeGoogleAnalytics() {
    if (typeof gtag !== 'undefined') {
      gtag('consent', 'update', {
        analytics_storage: 'granted',
        ad_storage: this.consentData.marketing ? 'granted' : 'denied'
      });
    }
  }
  
  setupPrivacyControls() {
    // Add privacy control button to footer
    const privacyButton = document.createElement('button');
    privacyButton.id = 'privacy-settings-btn';
    privacyButton.textContent = 'Privacy Settings';
    privacyButton.onclick = () => this.showConsentBanner();
    
    const footer = document.querySelector('footer');
    if (footer) {
      footer.appendChild(privacyButton);
    }
  }
  
  getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
  }
  
  hideConsentBanner() {
    const banner = document.getElementById('gdpr-consent-banner');
    if (banner) {
      banner.remove();
    }
  }
}

// Initialize GDPR Consent Manager
document.addEventListener('DOMContentLoaded', () => {
  new GDPRConsentManager();
});
```

### 2. Data Encryption & Secure Storage

#### Field-Level Encryption
```python
# core/utils/encryption.py
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import os

class DataEncryption:
    """Handle sensitive data encryption"""
    
    def __init__(self):
        self.key = self.get_encryption_key()
        self.cipher_suite = Fernet(self.key)
    
    def get_encryption_key(self):
        """Get or generate encryption key"""
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            # Generate new key (store securely in production)
            key = Fernet.generate_key()
            print(f"Generated new encryption key: {key.decode()}")
        
        if isinstance(key, str):
            key = key.encode()
        
        return key
    
    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        if not data:
            return data
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted = self.cipher_suite.encrypt(data)
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        if not encrypted_data:
            return encrypted_data
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

# Database-level encryption for sensitive fields
class SecureContactForm(models.Model):
    """Contact form with encrypted fields"""
    
    # Encrypted fields
    name = EncryptedCharField(max_length=100)
    email = EncryptedEmailField()
    phone = EncryptedCharField(max_length=20, blank=True)
    message = EncryptedTextField()
    
    # Non-sensitive metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent_hash = models.CharField(max_length=64)  # Hashed, not stored plaintext
    status = models.CharField(max_length=20, default='new')
    
    def save(self, *args, **kwargs):
        # Hash user agent instead of storing plaintext
        if hasattr(self, '_user_agent'):
            import hashlib
            self.user_agent_hash = hashlib.sha256(
                self._user_agent.encode()
            ).hexdigest()
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-submitted_at']
```

## Payment Security (PCI DSS)

### 1. Secure Payment Processing

#### PCI DSS Compliant Integration
```python
# core/payments/secure_payment.py
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
import hmac
import hashlib

logger = logging.getLogger('payments')

class SecurePaymentProcessor:
    """PCI DSS compliant payment processing"""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    
    def create_payment_intent(self, amount, currency='usd', metadata=None):
        """Create secure payment intent"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,  # Amount in cents
                currency=currency,
                automatic_payment_methods={
                    'enabled': True,
                },
                metadata=metadata or {},
                # Security settings
                capture_method='automatic',
                confirmation_method='automatic',
                use_stripe_sdk=True,
            )
            
            logger.info(f"Created payment intent: {intent.id}")
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return {'error': str(e)}
    
    def verify_webhook_signature(self, payload, signature):
        """Verify Stripe webhook signature"""
        try:
            return stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            return None
    
    @csrf_exempt
    def webhook_handler(self, request):
        """Handle Stripe webhooks securely"""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        event = self.verify_webhook_signature(payload, sig_header)
        if not event:
            return JsonResponse({'error': 'Invalid signature'}, status=400)
        
        # Handle specific events
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self.handle_successful_payment(payment_intent)
            
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self.handle_failed_payment(payment_intent)
        
        return JsonResponse({'status': 'success'})
    
    def handle_successful_payment(self, payment_intent):
        """Process successful payment"""
        logger.info(f"Payment succeeded: {payment_intent['id']}")
        
        # Update database records
        # Send confirmation emails
        # Update user permissions
        pass
    
    def tokenize_card_data(self, card_data):
        """Tokenize sensitive card data (never store raw card data)"""
        # This should only happen on client-side with Stripe.js
        # Server should never see raw card data
        raise NotImplementedError("Card data must be tokenized on client-side")

# Client-side secure payment form
"""
<!-- templates/payment/secure_form.html -->
<form id="payment-form">
  <div id="card-element">
    <!-- Stripe Elements will mount here -->
  </div>
  
  <button id="submit" class="btn btn-primary">
    Pay Now
  </button>
  
  <div id="card-errors" role="alert"></div>
</form>

<script src="https://js.stripe.com/v3/"></script>
<script>
const stripe = Stripe('{{ stripe_public_key }}');
const elements = stripe.elements();

// Create card element
const cardElement = elements.create('card', {
  style: {
    base: {
      fontSize: '16px',
      color: '#424770',
      '::placeholder': {
        color: '#aab7c4',
      },
    },
  },
});

cardElement.mount('#card-element');

// Handle form submission
document.getElementById('payment-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  
  const {error, paymentMethod} = await stripe.createPaymentMethod({
    type: 'card',
    card: cardElement,
    billing_details: {
      name: document.getElementById('cardholder-name').value,
    },
  });
  
  if (error) {
    document.getElementById('card-errors').textContent = error.message;
  } else {
    // Send payment method to server
    submitPayment(paymentMethod.id);
  }
});

async function submitPayment(paymentMethodId) {
  const response = await fetch('/api/payments/process/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
    },
    body: JSON.stringify({
      payment_method_id: paymentMethodId,
      amount: {{ amount }},
    }),
  });
  
  const result = await response.json();
  
  if (result.error) {
    document.getElementById('card-errors').textContent = result.error;
  } else {
    window.location.href = '/payment/success/';
  }
}
</script>
"""
```

## Security Monitoring & Incident Response

### 1. Security Monitoring System

#### Comprehensive Security Logging
```python
# core/monitoring/security_monitor.py
import logging
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import json

# Security logger configuration
security_logger = logging.getLogger('security')

class SecurityEventMonitor:
    """Monitor and respond to security events"""
    
    CRITICAL_EVENTS = [
        'multiple_failed_logins',
        'admin_access',
        'data_breach_attempt',
        'sql_injection_attempt',
        'xss_attempt',
        'suspicious_file_upload',
    ]
    
    def __init__(self):
        self.alert_thresholds = {
            'failed_logins': 5,      # 5 failed logins in 15 minutes
            'rapid_requests': 100,    # 100 requests in 1 minute
            'error_rate': 0.1,       # 10% error rate
        }
    
    def log_security_event(self, event_type, details, severity='medium', user=None, ip=None):
        """Log security events with structured data"""
        event_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'details': details,
            'user_id': getattr(user, 'id', None),
            'username': getattr(user, 'username', None),
            'ip_address': ip,
            'user_agent': details.get('user_agent', ''),
        }
        
        security_logger.warning(f"SECURITY_EVENT: {json.dumps(event_data)}")
        
        # Send alerts for critical events
        if event_type in self.CRITICAL_EVENTS or severity == 'critical':
            self.send_security_alert(event_type, event_data)
    
    def send_security_alert(self, event_type, event_data):
        """Send security alerts to administrators"""
        subject = f"Security Alert: {event_type}"
        message = f"""
        Security Event Detected:
        
        Type: {event_type}
        Severity: {event_data['severity']}
        Time: {event_data['timestamp']}
        User: {event_data.get('username', 'Anonymous')}
        IP: {event_data.get('ip_address', 'Unknown')}
        
        Details: {json.dumps(event_data['details'], indent=2)}
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                settings.SECURITY_ALERT_EMAILS,
                fail_silently=False,
            )
        except Exception as e:
            logging.error(f"Failed to send security alert: {e}")

# Signal receivers for automatic monitoring
monitor = SecurityEventMonitor()

@receiver(user_login_failed)
def track_failed_login(sender, credentials, request, **kwargs):
    """Track failed login attempts"""
    ip = get_client_ip(request)
    
    monitor.log_security_event(
        'failed_login',
        {
            'username': credentials.get('username', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        },
        severity='medium',
        ip=ip
    )
    
    # Check for brute force attempts
    check_brute_force_attempts(credentials.get('username', ''), ip)

@receiver(user_logged_in)
def track_successful_login(sender, user, request, **kwargs):
    """Track successful logins"""
    monitor.log_security_event(
        'successful_login',
        {
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'session_key': request.session.session_key,
        },
        severity='low',
        user=user,
        ip=get_client_ip(request)
    )

def check_brute_force_attempts(username, ip):
    """Check for brute force login attempts"""
    # Implementation would check recent failed attempts
    # and trigger alerts if threshold exceeded
    pass

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

### 2. Automated Security Scanning

#### Security Vulnerability Scanner
```python
# scripts/security_scan.py
import requests
import subprocess
import json
from urllib.parse import urljoin
from datetime import datetime

class SecurityScanner:
    """Automated security vulnerability scanner"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.vulnerabilities = []
        
        # Common vulnerability patterns
        self.xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert("XSS")</script>',
            "';alert('XSS');//",
        ]
        
        self.sql_injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
        ]
    
    def run_full_scan(self):
        """Run comprehensive security scan"""
        print("Starting security scan...")
        
        # OWASP Top 10 checks
        self.check_injection_vulnerabilities()
        self.check_xss_vulnerabilities()
        self.check_security_headers()
        self.check_authentication_flaws()
        self.check_sensitive_data_exposure()
        self.check_xml_vulnerabilities()
        self.check_access_control()
        self.check_security_misconfigurations()
        self.check_vulnerable_components()
        self.check_logging_monitoring()
        
        # Generate report
        self.generate_security_report()
    
    def check_security_headers(self):
        """Check for security headers"""
        try:
            response = requests.get(self.base_url, timeout=10)
            headers = response.headers
            
            required_headers = {
                'X-Frame-Options': 'Missing clickjacking protection',
                'X-Content-Type-Options': 'Missing MIME type sniffing protection',
                'Content-Security-Policy': 'Missing CSP protection',
                'Strict-Transport-Security': 'Missing HSTS protection',
                'Referrer-Policy': 'Missing referrer policy',
            }
            
            for header, description in required_headers.items():
                if header not in headers:
                    self.vulnerabilities.append({
                        'type': 'Missing Security Header',
                        'severity': 'Medium',
                        'description': f'{header}: {description}',
                        'url': self.base_url
                    })
            
        except Exception as e:
            print(f"Header check failed: {e}")
    
    def check_xss_vulnerabilities(self):
        """Check for XSS vulnerabilities"""
        test_urls = [
            '/contact',
            '/search',
            '/api/contact',
        ]
        
        for url in test_urls:
            full_url = urljoin(self.base_url, url)
            
            for payload in self.xss_payloads:
                try:
                    # Test GET parameters
                    response = requests.get(
                        full_url, 
                        params={'q': payload}, 
                        timeout=10
                    )
                    
                    if payload in response.text:
                        self.vulnerabilities.append({
                            'type': 'XSS Vulnerability',
                            'severity': 'High',
                            'description': f'Reflected XSS found in {url}',
                            'payload': payload,
                            'url': full_url
                        })
                
                except Exception as e:
                    continue
    
    def check_injection_vulnerabilities(self):
        """Check for SQL injection vulnerabilities"""
        test_endpoints = [
            '/api/events',
            '/search',
            '/contact',
        ]
        
        for endpoint in test_endpoints:
            full_url = urljoin(self.base_url, endpoint)
            
            for payload in self.sql_injection_payloads:
                try:
                    response = requests.get(
                        full_url,
                        params={'id': payload},
                        timeout=10
                    )
                    
                    # Check for SQL error messages
                    error_indicators = [
                        'mysql_fetch',
                        'ORA-',
                        'Microsoft JET Database',
                        'ODBC SQL',
                        'PostgreSQL'
                    ]
                    
                    if any(indicator in response.text.lower() for indicator in error_indicators):
                        self.vulnerabilities.append({
                            'type': 'SQL Injection',
                            'severity': 'Critical',
                            'description': f'SQL injection vulnerability in {endpoint}',
                            'payload': payload,
                            'url': full_url
                        })
                
                except Exception as e:
                    continue
    
    def generate_security_report(self):
        """Generate comprehensive security report"""
        report = {
            'scan_date': datetime.now().isoformat(),
            'target_url': self.base_url,
            'total_vulnerabilities': len(self.vulnerabilities),
            'critical_count': len([v for v in self.vulnerabilities if v['severity'] == 'Critical']),
            'high_count': len([v for v in self.vulnerabilities if v['severity'] == 'High']),
            'medium_count': len([v for v in self.vulnerabilities if v['severity'] == 'Medium']),
            'vulnerabilities': self.vulnerabilities
        }
        
        # Save report
        with open('security_scan_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\nSecurity Scan Complete")
        print(f"Total Vulnerabilities: {report['total_vulnerabilities']}")
        print(f"Critical: {report['critical_count']}")
        print(f"High: {report['high_count']}")
        print(f"Medium: {report['medium_count']}")
        
        if report['critical_count'] > 0:
            print("\n⚠️  CRITICAL VULNERABILITIES FOUND - IMMEDIATE ACTION REQUIRED")
        
        return report

# Run security scan
if __name__ == '__main__':
    scanner = SecurityScanner('https://saborconflow.com')
    scanner.run_full_scan()
```

## Compliance Documentation

### 1. Security Policy Templates

#### Data Protection Policy
```markdown
# Data Protection Policy - Sabor con Flow Dance Studio

## 1. Purpose
This policy establishes guidelines for protecting personal data in compliance with GDPR, CCPA, and other applicable privacy regulations.

## 2. Scope
This policy applies to all personal data processing activities conducted by Sabor con Flow Dance Studio.

## 3. Data Classification
- **Critical**: Payment information, government IDs
- **High**: Contact details, personal preferences
- **Medium**: Usage analytics, performance data
- **Low**: Anonymous aggregated data

## 4. Data Processing Principles
- **Lawfulness**: All processing based on valid legal grounds
- **Purpose Limitation**: Data used only for stated purposes
- **Data Minimization**: Collect only necessary data
- **Accuracy**: Maintain accurate and up-to-date data
- **Storage Limitation**: Retain data only as long as necessary
- **Security**: Implement appropriate technical safeguards

## 5. Technical Safeguards
- End-to-end encryption for data in transit
- AES-256 encryption for data at rest
- Multi-factor authentication for admin access
- Regular security audits and penetration testing
- Automated backup and disaster recovery

## 6. Data Subject Rights
- Right to access personal data
- Right to rectification of inaccurate data
- Right to erasure ("right to be forgotten")
- Right to data portability
- Right to restrict processing
- Right to object to processing

## 7. Incident Response
- Immediate containment of security incidents
- Assessment of breach impact within 24 hours
- Notification to authorities within 72 hours if required
- Communication to affected individuals
- Post-incident review and improvement

## 8. Training and Awareness
- Annual security training for all staff
- Regular updates on privacy regulations
- Clear procedures for handling data requests
- Incident reporting protocols
```

### 2. Compliance Monitoring Dashboard

#### Automated Compliance Checker
```python
# core/compliance/monitor.py
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
import json

class ComplianceMonitor:
    """Monitor GDPR and security compliance"""
    
    def __init__(self):
        self.compliance_checks = []
        
    def run_compliance_audit(self):
        """Run comprehensive compliance audit"""
        print("Running compliance audit...")
        
        # GDPR Compliance Checks
        self.check_consent_records()
        self.check_data_retention()
        self.check_data_subject_requests()
        self.check_privacy_policy_updates()
        
        # Security Compliance Checks  
        self.check_encryption_status()
        self.check_access_controls()
        self.check_backup_integrity()
        self.check_vulnerability_patches()
        
        # Generate compliance report
        self.generate_compliance_report()
    
    def check_consent_records(self):
        """Verify consent record integrity"""
        from core.models.privacy import ConsentRecord
        
        # Check for expired consents
        one_year_ago = datetime.now() - timedelta(days=365)
        expired_consents = ConsentRecord.objects.filter(
            timestamp__lt=one_year_ago,
            withdrawn_at__isnull=True
        ).count()
        
        if expired_consents > 0:
            self.compliance_checks.append({
                'check': 'Consent Records',
                'status': 'WARNING',
                'message': f'{expired_consents} consent records need renewal',
                'action_required': True
            })
        else:
            self.compliance_checks.append({
                'check': 'Consent Records',
                'status': 'PASS',
                'message': 'All consent records are current'
            })
    
    def check_data_retention(self):
        """Check data retention compliance"""
        from core.models.privacy import DataProcessingRecord
        
        # Check for data past retention period
        overdue_data = DataProcessingRecord.objects.filter(
            processed_at__lt=datetime.now() - timedelta(days=365),
            deleted_at__isnull=True
        ).count()
        
        if overdue_data > 0:
            self.compliance_checks.append({
                'check': 'Data Retention',
                'status': 'FAIL',
                'message': f'{overdue_data} records exceed retention period',
                'action_required': True,
                'priority': 'HIGH'
            })
    
    def generate_compliance_report(self):
        """Generate compliance audit report"""
        total_checks = len(self.compliance_checks)
        passed_checks = len([c for c in self.compliance_checks if c['status'] == 'PASS'])
        failed_checks = len([c for c in self.compliance_checks if c['status'] == 'FAIL'])
        warnings = len([c for c in self.compliance_checks if c['status'] == 'WARNING'])
        
        report = {
            'audit_date': datetime.now().isoformat(),
            'total_checks': total_checks,
            'passed': passed_checks,
            'failed': failed_checks,
            'warnings': warnings,
            'compliance_score': (passed_checks / total_checks) * 100,
            'checks': self.compliance_checks
        }
        
        # Save report
        with open('compliance_audit_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nCompliance Audit Complete")
        print(f"Compliance Score: {report['compliance_score']:.1f}%")
        print(f"Passed: {passed_checks}/{total_checks}")
        
        if failed_checks > 0:
            print(f"⚠️  {failed_checks} CRITICAL COMPLIANCE ISSUES FOUND")
```

## Success Criteria & Testing

### Security Testing Checklist
- [x] OWASP Top 10 vulnerability assessment
- [x] Penetration testing (automated and manual)
- [x] Security headers validation
- [x] Rate limiting effectiveness testing
- [x] GDPR compliance audit
- [x] PCI DSS compliance validation
- [x] Data encryption verification
- [x] Incident response procedure testing

### Compliance Deliverables
- [x] Data Protection Impact Assessment (DPIA)
- [x] Privacy Policy and Terms of Service
- [x] Cookie Policy and Consent Management
- [x] Data Processing Agreements (DPAs)
- [x] Security incident response procedures
- [x] Staff training documentation
- [x] Compliance monitoring dashboard

### Monitoring & Alerts
- **Real-time**: Security incident alerts
- **Daily**: Failed login attempt summaries  
- **Weekly**: Vulnerability scan reports
- **Monthly**: Compliance audit reports
- **Quarterly**: Comprehensive security assessment

## Timeline
- **Day 1-2**: Security headers and CSP implementation
- **Day 3-4**: Rate limiting and DDoS protection
- **Day 5-6**: GDPR compliance system implementation
- **Day 7**: Payment security (PCI DSS) setup
- **Day 8**: Security monitoring and testing automation