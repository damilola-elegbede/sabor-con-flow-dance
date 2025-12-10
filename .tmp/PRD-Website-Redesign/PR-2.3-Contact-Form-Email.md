# PR 2.3: Contact Form & Email System Implementation

## PR Metadata

**Title:** feat: Implement contact form with SendGrid email integration  
**Branch:** `feature/contact-email`  
**Base:** `feature/class-schedule`  
**Dependencies:**
- PR 1.1 (Project Setup)
- PR 1.5 (Environment Configuration)
- PR 2.1 (Homepage & Navigation)

## Overview

This PR implements a fully functional contact form with email notifications using SendGrid, form validation, spam protection, and auto-response capabilities through Vercel Serverless Functions.

## File Structure

```
/
├── contact.html
├── api/
│   ├── contact/
│   │   ├── submit.js
│   │   ├── validate.js
│   │   └── spam-check.js
│   └── email/
│       ├── send.js
│       ├── templates.js
│       └── queue.js
├── lib/
│   ├── sendgrid.js
│   ├── validation.js
│   └── rate-limit.js
├── static/
│   ├── css/
│   │   ├── contact.css
│   │   └── forms.css
│   ├── js/
│   │   ├── contact-form.js
│   │   ├── form-validation.js
│   │   └── recaptcha.js
└── tests/
    ├── contact.test.js
    └── email.test.js
```

## Implementation Details

### 1. Contact Page HTML (`contact.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Contact Sabor con Flow Dance - Get in touch for dance classes, private lessons, and events">
    <title>Contact Us - Sabor con Flow Dance</title>
    
    <!-- Critical CSS -->
    <style>
        :root {
            --form-max-width: 600px;
            --input-padding: 0.75rem;
            --input-radius: 8px;
            --success-color: #4CAF50;
            --error-color: #F44336;
        }
        
        .contact-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }
        
        .contact-form {
            max-width: var(--form-max-width);
            margin: 0 auto;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-input,
        .form-textarea {
            width: 100%;
            padding: var(--input-padding);
            border: 1px solid #ddd;
            border-radius: var(--input-radius);
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .form-input:focus,
        .form-textarea:focus {
            outline: none;
            border-color: var(--primary-color);
        }
    </style>
    
    <!-- Async CSS -->
    <link rel="preload" href="/static/css/contact.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <link rel="preload" href="/static/css/forms.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <noscript>
        <link rel="stylesheet" href="/static/css/contact.css">
        <link rel="stylesheet" href="/static/css/forms.css">
    </noscript>
    
    <!-- reCAPTCHA v3 -->
    <script src="https://www.google.com/recaptcha/api.js?render=YOUR_SITE_KEY" async defer></script>
</head>
<body>
    <!-- Navigation -->
    <nav class="main-nav"><!-- ... --></nav>
    
    <main id="main-content">
        <!-- Page Header -->
        <header class="page-header">
            <div class="container">
                <h1>Get in Touch</h1>
                <p>We'd love to hear from you! Reach out with any questions or to book your first class.</p>
            </div>
        </header>
        
        <!-- Contact Section -->
        <section class="contact-section">
            <div class="contact-container">
                <div class="contact-content">
                    <!-- Contact Information -->
                    <aside class="contact-info">
                        <h2>Contact Information</h2>
                        
                        <div class="info-item">
                            <svg class="info-icon" width="24" height="24" aria-hidden="true">
                                <use href="#icon-location"></use>
                            </svg>
                            <div>
                                <h3>Studio Location</h3>
                                <address>
                                    123 Dance Street<br>
                                    San Francisco, CA 94102<br>
                                    United States
                                </address>
                            </div>
                        </div>
                        
                        <div class="info-item">
                            <svg class="info-icon" width="24" height="24" aria-hidden="true">
                                <use href="#icon-phone"></use>
                            </svg>
                            <div>
                                <h3>Phone</h3>
                                <a href="tel:+14155551234">(415) 555-1234</a>
                            </div>
                        </div>
                        
                        <div class="info-item">
                            <svg class="info-icon" width="24" height="24" aria-hidden="true">
                                <use href="#icon-email"></use>
                            </svg>
                            <div>
                                <h3>Email</h3>
                                <a href="mailto:info@saborconflowdance.com">info@saborconflowdance.com</a>
                            </div>
                        </div>
                        
                        <div class="info-item">
                            <svg class="info-icon" width="24" height="24" aria-hidden="true">
                                <use href="#icon-clock"></use>
                            </svg>
                            <div>
                                <h3>Studio Hours</h3>
                                <dl class="hours-list">
                                    <dt>Monday - Friday</dt>
                                    <dd>6:00 PM - 10:00 PM</dd>
                                    <dt>Saturday</dt>
                                    <dd>10:00 AM - 8:00 PM</dd>
                                    <dt>Sunday</dt>
                                    <dd>12:00 PM - 6:00 PM</dd>
                                </dl>
                            </div>
                        </div>
                        
                        <!-- Social Links -->
                        <div class="social-links">
                            <h3>Follow Us</h3>
                            <div class="social-icons">
                                <a href="#" aria-label="Facebook" class="social-link">
                                    <svg><use href="#icon-facebook"></use></svg>
                                </a>
                                <a href="#" aria-label="Instagram" class="social-link">
                                    <svg><use href="#icon-instagram"></use></svg>
                                </a>
                                <a href="#" aria-label="YouTube" class="social-link">
                                    <svg><use href="#icon-youtube"></use></svg>
                                </a>
                            </div>
                        </div>
                    </aside>
                    
                    <!-- Contact Form -->
                    <div class="contact-form-wrapper">
                        <h2>Send Us a Message</h2>
                        
                        <!-- Success Message -->
                        <div id="form-success" class="alert alert-success" hidden role="alert">
                            <svg class="alert-icon" width="24" height="24" aria-hidden="true">
                                <use href="#icon-check-circle"></use>
                            </svg>
                            <div>
                                <strong>Thank you for your message!</strong>
                                <p>We'll get back to you within 24 hours.</p>
                            </div>
                        </div>
                        
                        <!-- Error Message -->
                        <div id="form-error" class="alert alert-error" hidden role="alert">
                            <svg class="alert-icon" width="24" height="24" aria-hidden="true">
                                <use href="#icon-error"></use>
                            </svg>
                            <div>
                                <strong>Oops! Something went wrong.</strong>
                                <p id="error-message">Please try again or contact us directly.</p>
                            </div>
                        </div>
                        
                        <form id="contact-form" class="contact-form" novalidate>
                            <!-- Name Fields -->
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="first-name" class="form-label">
                                        First Name <span class="required" aria-label="required">*</span>
                                    </label>
                                    <input type="text" 
                                           id="first-name" 
                                           name="firstName" 
                                           class="form-input"
                                           required
                                           aria-required="true"
                                           aria-describedby="first-name-error">
                                    <span id="first-name-error" class="error-message" role="alert"></span>
                                </div>
                                
                                <div class="form-group">
                                    <label for="last-name" class="form-label">
                                        Last Name <span class="required" aria-label="required">*</span>
                                    </label>
                                    <input type="text" 
                                           id="last-name" 
                                           name="lastName" 
                                           class="form-input"
                                           required
                                           aria-required="true"
                                           aria-describedby="last-name-error">
                                    <span id="last-name-error" class="error-message" role="alert"></span>
                                </div>
                            </div>
                            
                            <!-- Email -->
                            <div class="form-group">
                                <label for="email" class="form-label">
                                    Email Address <span class="required" aria-label="required">*</span>
                                </label>
                                <input type="email" 
                                       id="email" 
                                       name="email" 
                                       class="form-input"
                                       required
                                       aria-required="true"
                                       aria-describedby="email-error"
                                       autocomplete="email">
                                <span id="email-error" class="error-message" role="alert"></span>
                            </div>
                            
                            <!-- Phone -->
                            <div class="form-group">
                                <label for="phone" class="form-label">
                                    Phone Number
                                </label>
                                <input type="tel" 
                                       id="phone" 
                                       name="phone" 
                                       class="form-input"
                                       aria-describedby="phone-error"
                                       autocomplete="tel">
                                <span id="phone-error" class="error-message" role="alert"></span>
                            </div>
                            
                            <!-- Subject -->
                            <div class="form-group">
                                <label for="subject" class="form-label">
                                    Subject <span class="required" aria-label="required">*</span>
                                </label>
                                <select id="subject" 
                                        name="subject" 
                                        class="form-input"
                                        required
                                        aria-required="true"
                                        aria-describedby="subject-error">
                                    <option value="">Select a subject</option>
                                    <option value="general">General Inquiry</option>
                                    <option value="classes">Class Information</option>
                                    <option value="private">Private Lessons</option>
                                    <option value="events">Events & Performances</option>
                                    <option value="corporate">Corporate Classes</option>
                                    <option value="feedback">Feedback</option>
                                    <option value="other">Other</option>
                                </select>
                                <span id="subject-error" class="error-message" role="alert"></span>
                            </div>
                            
                            <!-- Message -->
                            <div class="form-group">
                                <label for="message" class="form-label">
                                    Message <span class="required" aria-label="required">*</span>
                                </label>
                                <textarea id="message" 
                                          name="message" 
                                          class="form-textarea"
                                          rows="6"
                                          required
                                          aria-required="true"
                                          aria-describedby="message-error"
                                          placeholder="Tell us how we can help you..."></textarea>
                                <span id="message-error" class="error-message" role="alert"></span>
                                <div class="character-count">
                                    <span id="char-count">0</span> / 1000 characters
                                </div>
                            </div>
                            
                            <!-- Newsletter Opt-in -->
                            <div class="form-group">
                                <label class="checkbox-label">
                                    <input type="checkbox" 
                                           name="newsletter" 
                                           id="newsletter"
                                           value="yes">
                                    <span>Send me updates about classes and events</span>
                                </label>
                            </div>
                            
                            <!-- Honeypot field for spam protection -->
                            <div class="form-group" style="position: absolute; left: -9999px;">
                                <label for="website">Website</label>
                                <input type="text" 
                                       id="website" 
                                       name="website" 
                                       tabindex="-1" 
                                       autocomplete="off">
                            </div>
                            
                            <!-- Form Actions -->
                            <div class="form-actions">
                                <button type="submit" class="btn btn-primary btn-large" id="submit-btn">
                                    <span class="btn-text">Send Message</span>
                                    <span class="btn-loading" hidden>
                                        <svg class="spinner" width="20" height="20" aria-hidden="true">
                                            <use href="#icon-spinner"></use>
                                        </svg>
                                        Sending...
                                    </span>
                                </button>
                                <button type="reset" class="btn btn-secondary">
                                    Clear Form
                                </button>
                            </div>
                            
                            <!-- reCAPTCHA Badge -->
                            <div class="recaptcha-notice">
                                This site is protected by reCAPTCHA and the Google 
                                <a href="https://policies.google.com/privacy" target="_blank" rel="noopener">Privacy Policy</a> and
                                <a href="https://policies.google.com/terms" target="_blank" rel="noopener">Terms of Service</a> apply.
                            </div>
                        </form>
                    </div>
                </div>
                
                <!-- Map Section -->
                <div class="map-section">
                    <h2>Find Us</h2>
                    <div id="map" class="map-container" aria-label="Studio location map">
                        <!-- Map will be loaded here -->
                        <noscript>
                            <img src="/static/images/studio-map.jpg" 
                                 alt="Map showing Sabor con Flow Dance studio location">
                        </noscript>
                    </div>
                    <div class="map-directions">
                        <a href="https://maps.google.com/?q=123+Dance+Street+San+Francisco+CA" 
                           target="_blank" 
                           rel="noopener"
                           class="btn btn-secondary">
                            Get Directions
                        </a>
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <!-- SVG Icons -->
    <svg style="display: none;">
        <defs>
            <symbol id="icon-location" viewBox="0 0 24 24">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
            </symbol>
            <!-- More icons... -->
        </defs>
    </svg>
    
    <!-- JavaScript Modules -->
    <script type="module" src="/static/js/contact-form.js"></script>
    <script type="module" src="/static/js/form-validation.js"></script>
</body>
</html>
```

### 2. Contact Form JavaScript (`static/js/contact-form.js`)

```javascript
/**
 * Contact Form Handler
 * Manages form submission, validation, and user feedback
 */

import FormValidator from './form-validation.js';

class ContactForm {
    constructor() {
        this.form = document.getElementById('contact-form');
        this.submitBtn = document.getElementById('submit-btn');
        this.successAlert = document.getElementById('form-success');
        this.errorAlert = document.getElementById('form-error');
        this.errorMessage = document.getElementById('error-message');
        
        this.validator = new FormValidator(this.form);
        this.isSubmitting = false;
        
        this.init();
    }
    
    init() {
        if (!this.form) return;
        
        // Set up form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Set up form reset
        this.form.addEventListener('reset', () => this.handleReset());
        
        // Character counter for message
        this.setupCharacterCounter();
        
        // Set up real-time validation
        this.setupRealtimeValidation();
        
        // Initialize reCAPTCHA
        this.initRecaptcha();
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        // Prevent double submission
        if (this.isSubmitting) return;
        
        // Hide any existing alerts
        this.hideAlerts();
        
        // Validate form
        if (!this.validator.validate()) {
            this.focusFirstError();
            return;
        }
        
        // Check honeypot
        if (this.form.website.value) {
            console.warn('Honeypot triggered');
            return;
        }
        
        this.isSubmitting = true;
        this.showLoadingState();
        
        try {
            // Get reCAPTCHA token
            const recaptchaToken = await this.getRecaptchaToken();
            
            // Prepare form data
            const formData = new FormData(this.form);
            const data = Object.fromEntries(formData.entries());
            
            // Add reCAPTCHA token
            data.recaptchaToken = recaptchaToken;
            
            // Send to API
            const response = await fetch('/api/contact/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Failed to send message');
            }
            
            // Success
            this.handleSuccess(result);
            
        } catch (error) {
            console.error('Form submission error:', error);
            this.handleError(error.message);
        } finally {
            this.isSubmitting = false;
            this.hideLoadingState();
        }
    }
    
    handleSuccess(result) {
        // Show success message
        this.showAlert(this.successAlert);
        
        // Reset form
        this.form.reset();
        
        // Track conversion
        if (typeof gtag !== 'undefined') {
            gtag('event', 'contact_form_submission', {
                event_category: 'engagement',
                event_label: this.form.subject.value
            });
        }
        
        // Scroll to success message
        this.successAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Hide success message after 10 seconds
        setTimeout(() => {
            this.hideAlert(this.successAlert);
        }, 10000);
    }
    
    handleError(message) {
        // Update error message
        this.errorMessage.textContent = message || 'Please try again or contact us directly.';
        
        // Show error alert
        this.showAlert(this.errorAlert);
        
        // Scroll to error
        this.errorAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    handleReset() {
        // Clear validation states
        this.validator.clearErrors();
        
        // Hide alerts
        this.hideAlerts();
        
        // Reset character counter
        this.updateCharacterCount(0);
    }
    
    setupCharacterCounter() {
        const messageField = this.form.message;
        const charCount = document.getElementById('char-count');
        
        if (!messageField || !charCount) return;
        
        const maxLength = 1000;
        
        messageField.addEventListener('input', () => {
            const length = messageField.value.length;
            this.updateCharacterCount(length);
            
            // Add warning class when near limit
            if (length > maxLength * 0.9) {
                charCount.parentElement.classList.add('warning');
            } else {
                charCount.parentElement.classList.remove('warning');
            }
            
            // Prevent exceeding limit
            if (length > maxLength) {
                messageField.value = messageField.value.substring(0, maxLength);
                this.updateCharacterCount(maxLength);
            }
        });
    }
    
    updateCharacterCount(count) {
        const charCount = document.getElementById('char-count');
        if (charCount) {
            charCount.textContent = count;
        }
    }
    
    setupRealtimeValidation() {
        const fields = this.form.querySelectorAll('.form-input, .form-textarea');
        
        fields.forEach(field => {
            // Validate on blur
            field.addEventListener('blur', () => {
                this.validator.validateField(field);
            });
            
            // Clear error on input
            field.addEventListener('input', () => {
                if (field.classList.contains('error')) {
                    this.validator.clearFieldError(field);
                }
            });
        });
    }
    
    async initRecaptcha() {
        // Wait for reCAPTCHA to load
        if (typeof grecaptcha === 'undefined') {
            setTimeout(() => this.initRecaptcha(), 100);
            return;
        }
        
        // reCAPTCHA v3 is already initialized via script tag
        console.log('reCAPTCHA initialized');
    }
    
    async getRecaptchaToken() {
        if (typeof grecaptcha === 'undefined') {
            throw new Error('reCAPTCHA not loaded');
        }
        
        return new Promise((resolve, reject) => {
            grecaptcha.ready(() => {
                grecaptcha.execute('YOUR_SITE_KEY', { action: 'contact' })
                    .then(token => resolve(token))
                    .catch(error => reject(error));
            });
        });
    }
    
    showLoadingState() {
        this.submitBtn.disabled = true;
        this.submitBtn.querySelector('.btn-text').hidden = true;
        this.submitBtn.querySelector('.btn-loading').hidden = false;
    }
    
    hideLoadingState() {
        this.submitBtn.disabled = false;
        this.submitBtn.querySelector('.btn-text').hidden = false;
        this.submitBtn.querySelector('.btn-loading').hidden = true;
    }
    
    showAlert(alert) {
        alert.hidden = false;
        alert.classList.add('show');
    }
    
    hideAlert(alert) {
        alert.classList.remove('show');
        setTimeout(() => {
            alert.hidden = true;
        }, 300);
    }
    
    hideAlerts() {
        this.hideAlert(this.successAlert);
        this.hideAlert(this.errorAlert);
    }
    
    focusFirstError() {
        const firstError = this.form.querySelector('.error');
        if (firstError) {
            firstError.focus();
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new ContactForm());
} else {
    new ContactForm();
}

export default ContactForm;
```

### 3. Form Validation Module (`static/js/form-validation.js`)

```javascript
/**
 * Form Validation Module
 * Reusable validation logic for all forms
 */

class FormValidator {
    constructor(form) {
        this.form = form;
        this.validators = {
            required: this.validateRequired,
            email: this.validateEmail,
            phone: this.validatePhone,
            minLength: this.validateMinLength,
            maxLength: this.validateMaxLength,
            pattern: this.validatePattern
        };
    }
    
    validate() {
        let isValid = true;
        const fields = this.form.querySelectorAll('[required], [data-validate]');
        
        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    validateField(field) {
        const rules = this.getValidationRules(field);
        let isValid = true;
        
        for (const rule of rules) {
            const validator = this.validators[rule.type];
            if (validator && !validator.call(this, field, rule.value)) {
                this.showFieldError(field, rule.message);
                isValid = false;
                break;
            }
        }
        
        if (isValid) {
            this.clearFieldError(field);
        }
        
        return isValid;
    }
    
    getValidationRules(field) {
        const rules = [];
        
        // Required
        if (field.hasAttribute('required')) {
            rules.push({
                type: 'required',
                message: 'This field is required'
            });
        }
        
        // Email
        if (field.type === 'email') {
            rules.push({
                type: 'email',
                message: 'Please enter a valid email address'
            });
        }
        
        // Phone
        if (field.type === 'tel') {
            rules.push({
                type: 'phone',
                message: 'Please enter a valid phone number'
            });
        }
        
        // Min length
        if (field.hasAttribute('minlength')) {
            rules.push({
                type: 'minLength',
                value: parseInt(field.getAttribute('minlength')),
                message: `Must be at least ${field.getAttribute('minlength')} characters`
            });
        }
        
        // Max length
        if (field.hasAttribute('maxlength')) {
            rules.push({
                type: 'maxLength',
                value: parseInt(field.getAttribute('maxlength')),
                message: `Must be no more than ${field.getAttribute('maxlength')} characters`
            });
        }
        
        // Pattern
        if (field.hasAttribute('pattern')) {
            rules.push({
                type: 'pattern',
                value: new RegExp(field.getAttribute('pattern')),
                message: field.getAttribute('data-pattern-message') || 'Invalid format'
            });
        }
        
        // Custom validation rules from data attributes
        if (field.hasAttribute('data-validate')) {
            const customRules = JSON.parse(field.getAttribute('data-validate'));
            rules.push(...customRules);
        }
        
        return rules;
    }
    
    validateRequired(field) {
        const value = field.value.trim();
        
        if (field.type === 'checkbox') {
            return field.checked;
        }
        
        if (field.type === 'radio') {
            const name = field.name;
            return this.form.querySelector(`input[name="${name}"]:checked`) !== null;
        }
        
        return value !== '';
    }
    
    validateEmail(field) {
        const value = field.value.trim();
        if (!value && !field.hasAttribute('required')) return true;
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(value);
    }
    
    validatePhone(field) {
        const value = field.value.trim();
        if (!value && !field.hasAttribute('required')) return true;
        
        // Remove common formatting characters
        const cleaned = value.replace(/[\s\-\(\)\.]/g, '');
        
        // Check if it's a valid phone number (10-15 digits)
        const phoneRegex = /^\+?\d{10,15}$/;
        return phoneRegex.test(cleaned);
    }
    
    validateMinLength(field, minLength) {
        const value = field.value.trim();
        if (!value && !field.hasAttribute('required')) return true;
        
        return value.length >= minLength;
    }
    
    validateMaxLength(field, maxLength) {
        const value = field.value.trim();
        return value.length <= maxLength;
    }
    
    validatePattern(field, pattern) {
        const value = field.value.trim();
        if (!value && !field.hasAttribute('required')) return true;
        
        return pattern.test(value);
    }
    
    showFieldError(field, message) {
        // Add error class to field
        field.classList.add('error');
        field.setAttribute('aria-invalid', 'true');
        
        // Find or create error message element
        const errorId = field.getAttribute('aria-describedby');
        let errorElement = errorId ? document.getElementById(errorId) : null;
        
        if (!errorElement) {
            errorElement = document.createElement('span');
            errorElement.className = 'error-message';
            errorElement.setAttribute('role', 'alert');
            errorElement.id = `${field.id}-error`;
            field.parentNode.appendChild(errorElement);
            field.setAttribute('aria-describedby', errorElement.id);
        }
        
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
    
    clearFieldError(field) {
        field.classList.remove('error');
        field.removeAttribute('aria-invalid');
        
        const errorId = field.getAttribute('aria-describedby');
        if (errorId) {
            const errorElement = document.getElementById(errorId);
            if (errorElement) {
                errorElement.textContent = '';
                errorElement.style.display = 'none';
            }
        }
    }
    
    clearErrors() {
        const fields = this.form.querySelectorAll('.error');
        fields.forEach(field => this.clearFieldError(field));
    }
}

export default FormValidator;
```

### 4. Vercel Serverless API (`api/contact/submit.js`)

```javascript
/**
 * Contact Form Submission API
 * Handles form processing and email sending
 */

import { sendEmail } from '../../lib/sendgrid.js';
import { validateRecaptcha } from '../../lib/recaptcha.js';
import { rateLimit } from '../../lib/rate-limit.js';
import { sanitizeInput } from '../../lib/validation.js';

// Rate limiting: 5 submissions per hour per IP
const limiter = rateLimit({
    windowMs: 60 * 60 * 1000, // 1 hour
    max: 5
});

export default async function handler(req, res) {
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    if (req.method !== 'POST') {
        res.status(405).json({ error: 'Method not allowed' });
        return;
    }
    
    try {
        // Apply rate limiting
        await limiter(req, res);
        
        // Parse and validate request body
        const {
            firstName,
            lastName,
            email,
            phone,
            subject,
            message,
            newsletter,
            website, // Honeypot field
            recaptchaToken
        } = req.body;
        
        // Check honeypot
        if (website) {
            console.warn('Honeypot triggered from IP:', req.headers['x-forwarded-for']);
            // Silently reject but return success to avoid revealing honeypot
            res.status(200).json({ success: true, message: 'Message sent successfully' });
            return;
        }
        
        // Validate required fields
        if (!firstName || !lastName || !email || !subject || !message) {
            res.status(400).json({
                success: false,
                error: 'Please fill in all required fields'
            });
            return;
        }
        
        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            res.status(400).json({
                success: false,
                error: 'Please enter a valid email address'
            });
            return;
        }
        
        // Verify reCAPTCHA
        const recaptchaValid = await validateRecaptcha(recaptchaToken, req.headers['x-forwarded-for']);
        if (!recaptchaValid) {
            res.status(400).json({
                success: false,
                error: 'reCAPTCHA verification failed. Please try again.'
            });
            return;
        }
        
        // Sanitize inputs
        const sanitized = {
            firstName: sanitizeInput(firstName),
            lastName: sanitizeInput(lastName),
            email: sanitizeInput(email),
            phone: sanitizeInput(phone || ''),
            subject: sanitizeInput(subject),
            message: sanitizeInput(message),
            newsletter: newsletter === 'yes'
        };
        
        // Prepare email data
        const emailData = {
            to: process.env.CONTACT_EMAIL || 'info@saborconflowdance.com',
            from: {
                email: process.env.SENDGRID_FROM_EMAIL || 'noreply@saborconflowdance.com',
                name: 'Sabor con Flow Contact Form'
            },
            replyTo: {
                email: sanitized.email,
                name: `${sanitized.firstName} ${sanitized.lastName}`
            },
            subject: `[Contact Form] ${sanitized.subject}`,
            html: generateEmailHtml(sanitized),
            text: generateEmailText(sanitized)
        };
        
        // Send notification email to admin
        await sendEmail(emailData);
        
        // Send auto-response to user
        const autoResponseData = {
            to: sanitized.email,
            from: {
                email: process.env.SENDGRID_FROM_EMAIL || 'noreply@saborconflowdance.com',
                name: 'Sabor con Flow Dance'
            },
            subject: 'Thank you for contacting Sabor con Flow Dance',
            html: generateAutoResponseHtml(sanitized),
            text: generateAutoResponseText(sanitized)
        };
        
        await sendEmail(autoResponseData);
        
        // Store in database (optional)
        // await saveContactSubmission(sanitized);
        
        // Add to newsletter if opted in
        if (sanitized.newsletter) {
            // await addToNewsletter(sanitized.email, sanitized.firstName, sanitized.lastName);
        }
        
        res.status(200).json({
            success: true,
            message: 'Thank you for your message! We\'ll get back to you within 24 hours.'
        });
        
    } catch (error) {
        console.error('Contact form error:', error);
        
        // Don't expose internal errors to client
        res.status(500).json({
            success: false,
            error: 'An error occurred while sending your message. Please try again later.'
        });
    }
}

function generateEmailHtml(data) {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #E63946; color: white; padding: 20px; text-align: center; }
                .content { background: #f9f9f9; padding: 20px; margin-top: 20px; }
                .field { margin-bottom: 15px; }
                .label { font-weight: bold; color: #555; }
                .value { margin-top: 5px; }
                .footer { margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>New Contact Form Submission</h2>
                </div>
                <div class="content">
                    <div class="field">
                        <div class="label">Name:</div>
                        <div class="value">${data.firstName} ${data.lastName}</div>
                    </div>
                    <div class="field">
                        <div class="label">Email:</div>
                        <div class="value"><a href="mailto:${data.email}">${data.email}</a></div>
                    </div>
                    ${data.phone ? `
                    <div class="field">
                        <div class="label">Phone:</div>
                        <div class="value">${data.phone}</div>
                    </div>
                    ` : ''}
                    <div class="field">
                        <div class="label">Subject:</div>
                        <div class="value">${data.subject}</div>
                    </div>
                    <div class="field">
                        <div class="label">Message:</div>
                        <div class="value">${data.message.replace(/\n/g, '<br>')}</div>
                    </div>
                    <div class="field">
                        <div class="label">Newsletter:</div>
                        <div class="value">${data.newsletter ? 'Yes' : 'No'}</div>
                    </div>
                </div>
                <div class="footer">
                    <p>This message was sent from the contact form at saborconflowdance.com</p>
                </div>
            </div>
        </body>
        </html>
    `;
}

function generateEmailText(data) {
    return `
New Contact Form Submission

Name: ${data.firstName} ${data.lastName}
Email: ${data.email}
${data.phone ? `Phone: ${data.phone}` : ''}
Subject: ${data.subject}

Message:
${data.message}

Newsletter: ${data.newsletter ? 'Yes' : 'No'}

---
This message was sent from the contact form at saborconflowdance.com
    `.trim();
}

function generateAutoResponseHtml(data) {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #E63946; color: white; padding: 30px; text-align: center; }
                .content { padding: 30px; }
                .button { display: inline-block; background: #E63946; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-top: 20px; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Thank You for Contacting Us!</h1>
                </div>
                <div class="content">
                    <p>Dear ${data.firstName},</p>
                    <p>Thank you for reaching out to Sabor con Flow Dance! We've received your message and will get back to you within 24 hours.</p>
                    <p>In the meantime, feel free to:</p>
                    <ul>
                        <li>Check out our <a href="https://saborconflowdance.com/schedule">class schedule</a></li>
                        <li>Follow us on <a href="https://instagram.com/saborconflow">Instagram</a> for updates</li>
                        <li>Call us at (415) 555-1234 if you need immediate assistance</li>
                    </ul>
                    <p>We look forward to helping you on your dance journey!</p>
                    <p>Best regards,<br>The Sabor con Flow Team</p>
                    <a href="https://saborconflowdance.com" class="button">Visit Our Website</a>
                </div>
                <div class="footer">
                    <p>Sabor con Flow Dance<br>
                    123 Dance Street, San Francisco, CA 94102<br>
                    (415) 555-1234</p>
                </div>
            </div>
        </body>
        </html>
    `;
}

function generateAutoResponseText(data) {
    return `
Thank You for Contacting Us!

Dear ${data.firstName},

Thank you for reaching out to Sabor con Flow Dance! We've received your message and will get back to you within 24 hours.

In the meantime, feel free to:
- Check out our class schedule at https://saborconflowdance.com/schedule
- Follow us on Instagram @saborconflow for updates
- Call us at (415) 555-1234 if you need immediate assistance

We look forward to helping you on your dance journey!

Best regards,
The Sabor con Flow Team

---
Sabor con Flow Dance
123 Dance Street, San Francisco, CA 94102
(415) 555-1234
https://saborconflowdance.com
    `.trim();
}
```

### 5. SendGrid Integration (`lib/sendgrid.js`)

```javascript
/**
 * SendGrid Email Service
 * Handles email sending through SendGrid API
 */

import sgMail from '@sendgrid/mail';

// Initialize SendGrid
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

export async function sendEmail(emailData) {
    try {
        // Validate API key
        if (!process.env.SENDGRID_API_KEY) {
            throw new Error('SendGrid API key not configured');
        }
        
        // Send email
        const response = await sgMail.send(emailData);
        
        console.log('Email sent successfully:', response[0].statusCode);
        return response;
        
    } catch (error) {
        console.error('SendGrid error:', error);
        
        if (error.response) {
            console.error('SendGrid response error:', error.response.body);
        }
        
        throw error;
    }
}

export async function sendBulkEmails(emails) {
    try {
        const response = await sgMail.send(emails);
        return response;
    } catch (error) {
        console.error('Bulk email error:', error);
        throw error;
    }
}

export async function validateEmailAddress(email) {
    // Basic validation - could integrate with SendGrid validation API
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}
```

### 6. Contact Form CSS (`static/css/contact.css`)

```css
/* Contact Page Styles */

.contact-section {
    padding: 3rem 0;
    background: #f9f9f9;
}

.contact-content {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 3rem;
    margin-bottom: 3rem;
}

/* Contact Information */
.contact-info {
    background: var(--white);
    padding: 2rem;
    border-radius: var(--card-radius);
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.contact-info h2 {
    color: var(--dark-color);
    margin-bottom: 1.5rem;
}

.info-item {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #e0e0e0;
}

.info-item:last-child {
    border-bottom: none;
}

.info-icon {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    fill: var(--primary-color);
}

.info-item h3 {
    font-size: 1rem;
    color: var(--dark-color);
    margin-bottom: 0.5rem;
}

.info-item address {
    font-style: normal;
    line-height: 1.6;
}

.info-item a {
    color: var(--primary-color);
    text-decoration: none;
    transition: color 0.3s ease;
}

.info-item a:hover {
    color: var(--dark-color);
}

.hours-list {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    margin: 0;
}

.hours-list dt {
    font-weight: 500;
}

.hours-list dd {
    margin: 0;
    text-align: right;
}

/* Social Links */
.social-links {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #e0e0e0;
}

.social-links h3 {
    font-size: 1rem;
    margin-bottom: 1rem;
}

.social-icons {
    display: flex;
    gap: 1rem;
}

.social-link {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    background: var(--secondary-color);
    border-radius: 50%;
    transition: all 0.3s ease;
}

.social-link:hover {
    background: var(--primary-color);
    transform: translateY(-2px);
}

.social-link svg {
    width: 20px;
    height: 20px;
    fill: var(--dark-color);
}

.social-link:hover svg {
    fill: var(--white);
}

/* Contact Form */
.contact-form-wrapper {
    background: var(--white);
    padding: 2rem;
    border-radius: var(--card-radius);
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.contact-form-wrapper h2 {
    color: var(--dark-color);
    margin-bottom: 1.5rem;
}

/* Form Styles */
.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: var(--dark-color);
}

.required {
    color: var(--primary-color);
}

.form-input,
.form-textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: var(--input-radius);
    font-size: 1rem;
    transition: all 0.3s ease;
    background: var(--white);
}

.form-input:focus,
.form-textarea:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(230, 57, 70, 0.1);
}

.form-input.error,
.form-textarea.error {
    border-color: var(--error-color);
}

.form-textarea {
    resize: vertical;
    min-height: 120px;
}

/* Character Counter */
.character-count {
    text-align: right;
    font-size: 0.85rem;
    color: #666;
    margin-top: 0.25rem;
}

.character-count.warning {
    color: var(--primary-color);
    font-weight: 500;
}

/* Checkbox */
.checkbox-label {
    display: flex;
    align-items: center;
    cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
    margin-right: 0.5rem;
}

/* Error Messages */
.error-message {
    display: none;
    color: var(--error-color);
    font-size: 0.85rem;
    margin-top: 0.25rem;
}

/* Form Actions */
.form-actions {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
}

.form-actions button {
    min-width: 150px;
}

/* Loading State */
.btn-loading {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.spinner {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Alerts */
.alert {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    border-radius: var(--input-radius);
    margin-bottom: 1.5rem;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.alert.show {
    opacity: 1;
}

.alert-success {
    background: #E8F5E9;
    color: #2E7D32;
    border: 1px solid #A5D6A7;
}

.alert-error {
    background: #FFEBEE;
    color: #C62828;
    border: 1px solid #EF9A9A;
}

.alert-icon {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    fill: currentColor;
}

.alert strong {
    display: block;
    margin-bottom: 0.25rem;
}

/* reCAPTCHA Notice */
.recaptcha-notice {
    font-size: 0.75rem;
    color: #666;
    margin-top: 1rem;
    text-align: center;
}

.recaptcha-notice a {
    color: #666;
    text-decoration: underline;
}

/* Map Section */
.map-section {
    margin-top: 3rem;
}

.map-section h2 {
    text-align: center;
    margin-bottom: 2rem;
}

.map-container {
    height: 400px;
    background: #e0e0e0;
    border-radius: var(--card-radius);
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.map-directions {
    text-align: center;
    margin-top: 1.5rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .contact-content {
        grid-template-columns: 1fr;
    }
    
    .form-row {
        grid-template-columns: 1fr;
    }
    
    .form-actions {
        flex-direction: column;
    }
    
    .form-actions button {
        width: 100%;
    }
    
    .hours-list {
        grid-template-columns: 1fr;
    }
    
    .hours-list dd {
        text-align: left;
        margin-bottom: 0.5rem;
    }
}

/* Print Styles */
@media print {
    .contact-form-wrapper {
        display: none;
    }
    
    .map-section {
        display: none;
    }
    
    .social-links {
        display: none;
    }
}