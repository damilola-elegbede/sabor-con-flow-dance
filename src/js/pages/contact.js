/**
 * Contact Page Specific JavaScript
 * Route-based code splitting for contact page functionality
 */

export default class ContactPage {
  constructor() {
    this.modules = new Map();
    this.init();
  }

  async init() {
    await this.loadContactModules();
    this.setupContactForm();
    this.setupMap();
    this.setupScheduleIntegration();
    
    // Contact page enhanced
  }

  async loadContactModules() {
    const contactModules = [
      'contact-form',
      'analytics'
    ];

    const loadPromises = contactModules.map(async (moduleName) => {
      try {
        const module = await this.dynamicImport(moduleName);
        this.modules.set(moduleName, module);
      } catch (error) {
        console.warn(`Failed to load ${moduleName}:`, error);
      }
    });

    await Promise.allSettled(loadPromises);
  }

  async dynamicImport(moduleName) {
    const moduleMap = {
      'contact-form': () => import('../features/contact-form.js'),
      'analytics': () => import('../features/analytics.js'),
      'google-maps': () => import('../features/google-maps.js'),
      'calendly': () => import('../features/calendly.js')
    };

    const importFn = moduleMap[moduleName];
    if (!importFn) {
      throw new Error(`Unknown module: ${moduleName}`);
    }

    const module = await importFn();
    return module.default || module;
  }

  setupContactForm() {
    const contactForm = document.querySelector('.contact-form, #contact-form');
    if (!contactForm) return;

    // Progressive enhancement for contact form
    this.enhanceContactFormValidation(contactForm);
    this.setupFormSubmission(contactForm);
    this.setupFormAnalytics(contactForm);
  }

  enhanceContactFormValidation(form) {
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
      // Real-time validation
      input.addEventListener('blur', () => {
        this.validateField(input);
      });

      input.addEventListener('input', () => {
        // Clear error state on input
        if (input.classList.contains('is-invalid')) {
          input.classList.remove('is-invalid');
          this.clearFieldError(input);
        }
      });
    });

    // Enhanced form submission
    form.addEventListener('submit', (e) => {
      if (!this.validateForm(form)) {
        e.preventDefault();
        this.trackEvent('contact_form_validation_error');
      } else {
        this.trackEvent('contact_form_submitted');
      }
    });
  }

  validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';

    // Required field validation
    if (field.required && !value) {
      isValid = false;
      errorMessage = 'This field is required';
    }

    // Email validation
    if (field.type === 'email' && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid email address';
      }
    }

    // Phone validation
    if (field.type === 'tel' && value) {
      const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
      if (!phoneRegex.test(value.replace(/[\s\-\(\)]/g, ''))) {
        isValid = false;
        errorMessage = 'Please enter a valid phone number';
      }
    }

    // Custom validation based on field name
    if (field.name === 'message' && value.length < 10) {
      isValid = false;
      errorMessage = 'Message must be at least 10 characters long';
    }

    // Update field state
    if (isValid) {
      field.classList.remove('is-invalid');
      field.classList.add('is-valid');
      this.clearFieldError(field);
    } else {
      field.classList.remove('is-valid');
      field.classList.add('is-invalid');
      this.showFieldError(field, errorMessage);
    }

    return isValid;
  }

  validateForm(form) {
    const fields = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isFormValid = true;

    fields.forEach(field => {
      if (!this.validateField(field)) {
        isFormValid = false;
      }
    });

    return isFormValid;
  }

  showFieldError(field, message) {
    let errorElement = field.parentNode.querySelector('.field-error');
    
    if (!errorElement) {
      errorElement = document.createElement('div');
      errorElement.className = 'field-error';
      field.parentNode.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    errorElement.style.display = 'block';
  }

  clearFieldError(field) {
    const errorElement = field.parentNode.querySelector('.field-error');
    if (errorElement) {
      errorElement.style.display = 'none';
    }
  }

  setupFormSubmission(form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      if (!this.validateForm(form)) {
        return;
      }

      const submitButton = form.querySelector('button[type="submit"]');
      const originalText = submitButton.textContent;
      
      try {
        // Show loading state
        submitButton.disabled = true;
        submitButton.textContent = 'Sending...';
        
        // Get form data
        const formData = new FormData(form);
        
        // Submit form
        const response = await fetch(form.action || '/contact/', {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          }
        });

        if (response.ok) {
          this.showSuccessMessage(form);
          this.trackEvent('contact_form_success');
          form.reset();
        } else {
          throw new Error('Form submission failed');
        }

      } catch (error) {
        console.error('Form submission error:', error);
        this.showErrorMessage(form, 'There was an error sending your message. Please try again.');
        this.trackEvent('contact_form_error');
      } finally {
        // Reset button state
        submitButton.disabled = false;
        submitButton.textContent = originalText;
      }
    });
  }

  showSuccessMessage(form) {
    const message = document.createElement('div');
    message.className = 'alert alert-success';
    message.innerHTML = `
      <strong>Thank you!</strong> Your message has been sent successfully. 
      We'll get back to you within 24 hours.
    `;
    
    form.parentNode.insertBefore(message, form);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
      message.remove();
    }, 10000);
  }

  showErrorMessage(form, errorText) {
    const message = document.createElement('div');
    message.className = 'alert alert-danger';
    message.innerHTML = `<strong>Error:</strong> ${errorText}`;
    
    form.parentNode.insertBefore(message, form);
    
    // Auto-remove after 8 seconds
    setTimeout(() => {
      message.remove();
    }, 8000);
  }

  setupFormAnalytics(form) {
    // Track form interactions
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
      let interactionTracked = false;
      
      const trackInteraction = () => {
        if (!interactionTracked) {
          this.trackEvent('contact_form_interaction', {
            field: input.name || input.type
          });
          interactionTracked = true;
        }
      };

      input.addEventListener('focus', trackInteraction, { once: true });
      input.addEventListener('input', trackInteraction, { once: true });
    });
  }

  setupMap() {
    const mapContainer = document.querySelector('#map, .map-container');
    if (!mapContainer) return;

    // Load map module on interaction
    this.setupLazyModuleLoad(mapContainer, 'google-maps', 'map_loaded');
  }

  setupScheduleIntegration() {
    const scheduleButtons = document.querySelectorAll('.schedule-consultation, .book-lesson');
    
    scheduleButtons.forEach(button => {
      this.setupLazyModuleLoad(button, 'calendly', 'calendly_opened');
      
      button.addEventListener('click', (e) => {
        e.preventDefault();
        this.trackEvent('schedule_consultation_clicked');
      });
    });
  }

  setupLazyModuleLoad(trigger, moduleName, eventName) {
    const loadModule = async () => {
      try {
        const module = await this.dynamicImport(moduleName);
        this.modules.set(moduleName, module);
        
        if (eventName) {
          this.trackEvent(eventName);
        }
        
        // Initialize module
        if (module && typeof module.init === 'function') {
          module.init();
        }
      } catch (error) {
        console.warn(`Failed to load ${moduleName}:`, error);
      }
    };

    // Load on various interaction types
    trigger.addEventListener('mouseenter', loadModule, { once: true, passive: true });
    trigger.addEventListener('touchstart', loadModule, { once: true, passive: true });
    trigger.addEventListener('focus', loadModule, { once: true, passive: true });
    trigger.addEventListener('click', loadModule, { once: true });
  }

  trackEvent(eventName, parameters = {}) {
    if (window.gtag) {
      window.gtag('event', eventName, {
        event_category: 'contact',
        ...parameters
      });
    }
  }

  // Public API
  static init() {
    return new ContactPage();
  }
}

// Auto-initialize if not using module system
if (typeof window !== 'undefined' && !window.moduleSystem) {
  // Only initialize on contact page
  if (document.body.classList.contains('page-contact') || 
      window.location.pathname.includes('/contact') ||
      document.querySelector('.contact-form')) {
    document.addEventListener('DOMContentLoaded', () => {
      ContactPage.init();
    });
  }
}