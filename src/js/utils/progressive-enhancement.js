/**
 * Progressive Enhancement Utilities
 * Ensures the site works without JavaScript and enhances functionality when available
 */

export class ProgressiveEnhancement {
  static init() {
    this.addNoJSFallbacks();
    this.enhanceFormsWithoutJS();
    this.setupAccessibilityEnhancements();
    this.addPerformanceOptimizations();
  }

  /**
   * Add fallbacks for users without JavaScript
   */
  static addNoJSFallbacks() {
    // Remove .no-js class and add .js class for CSS targeting
    document.documentElement.classList.remove('no-js');
    document.documentElement.classList.add('js');

    // Add noscript alternatives where needed
    this.addNoscriptNavigation();
    this.addNoscriptGallery();
    this.addNoscriptForms();
  }

  static addNoscriptNavigation() {
    // Ensure mobile navigation works without JS by using CSS-only fallback
    const style = document.createElement('style');
    style.textContent = `
      /* CSS-only mobile menu fallback */
      .no-js .mobile-menu-toggle:checked + .mobile-menu {
        display: block !important;
      }
      
      .no-js .mobile-menu {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: #000;
        z-index: 1000;
      }
      
      .no-js .mobile-menu-toggle {
        display: none;
      }
      
      .no-js .mobile-menu-label {
        display: block;
        cursor: pointer;
      }
    `;
    
    // Only add if JavaScript is disabled
    if (!document.documentElement.classList.contains('js')) {
      document.head.appendChild(style);
    }
  }

  static addNoscriptGallery() {
    // Add simple CSS-only lightbox fallback
    const galleryItems = document.querySelectorAll('.media-item');
    galleryItems.forEach(item => {
      const fallbackLink = item.querySelector('a[href*="full-size"]');
      if (fallbackLink) {
        fallbackLink.setAttribute('target', '_blank');
        fallbackLink.setAttribute('rel', 'noopener');
      }
    });
  }

  static addNoscriptForms() {
    // Ensure forms work without JavaScript validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
      // Add server-side validation hints
      const submitButton = form.querySelector('button[type="submit"]');
      if (submitButton && !submitButton.hasAttribute('formnovalidate')) {
        // Form will use HTML5 validation as fallback
        form.setAttribute('novalidate', 'false');
      }

      // Add loading indicator for form submissions
      form.addEventListener('submit', () => {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'form-loading';
        loadingDiv.innerHTML = '<p>Submitting form, please wait...</p>';
        loadingDiv.style.cssText = `
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(255,255,255,0.9);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 100;
        `;
        
        // Make form container relative
        form.style.position = 'relative';
        form.appendChild(loadingDiv);
      });
    });
  }

  /**
   * Enhance forms to work better without JavaScript
   */
  static enhanceFormsWithoutJS() {
    // Add HTML5 validation attributes
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
      if (!input.hasAttribute('pattern')) {
        input.setAttribute('pattern', '[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}$');
      }
    });

    // Add better labels and hints
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
      // Ensure all inputs have proper labels
      if (!input.getAttribute('aria-label') && !input.getAttribute('aria-labelledby')) {
        const label = document.querySelector(`label[for="${input.id}"]`);
        if (!label && input.placeholder) {
          input.setAttribute('aria-label', input.placeholder);
        }
      }

      // Add validation hints
      if (input.required && !input.getAttribute('aria-describedby')) {
        const hintId = `${input.id || 'field'}-hint`;
        const hint = document.createElement('div');
        hint.id = hintId;
        hint.className = 'field-hint sr-only';
        hint.textContent = 'This field is required';
        input.parentNode.insertBefore(hint, input.nextSibling);
        input.setAttribute('aria-describedby', hintId);
      }
    });
  }

  /**
   * Setup accessibility enhancements
   */
  static setupAccessibilityEnhancements() {
    // Add skip links
    this.addSkipLinks();
    
    // Enhance keyboard navigation
    this.enhanceKeyboardNavigation();
    
    // Add ARIA attributes
    this.addARIAAttributes();
    
    // Setup focus management
    this.setupFocusManagement();
  }

  static addSkipLinks() {
    const skipLinks = [
      { href: '#main-content', text: 'Skip to main content' },
      { href: '#navigation', text: 'Skip to navigation' },
      { href: '#footer', text: 'Skip to footer' }
    ];

    const skipNav = document.createElement('nav');
    skipNav.className = 'skip-navigation';
    skipNav.setAttribute('aria-label', 'Skip navigation');

    skipLinks.forEach(link => {
      const skipLink = document.createElement('a');
      skipLink.href = link.href;
      skipLink.textContent = link.text;
      skipLink.className = 'skip-link';
      skipNav.appendChild(skipLink);
    });

    document.body.insertBefore(skipNav, document.body.firstChild);
  }

  static enhanceKeyboardNavigation() {
    // Add visible focus indicators
    const style = document.createElement('style');
    style.textContent = `
      .js-focus-visible :focus:not(.focus-visible) {
        outline: none;
      }
      
      .js-focus-visible .focus-visible {
        outline: 2px solid #C7B375;
        outline-offset: 2px;
      }
    `;
    document.head.appendChild(style);

    // Track keyboard usage
    let hadKeyboardEvent = true;
    const keyboardThrottledEvent = this.throttle(() => {
      hadKeyboardEvent = true;
    }, 100);

    document.addEventListener('keydown', keyboardThrottledEvent);
    document.addEventListener('mousedown', () => {
      hadKeyboardEvent = false;
    });

    // Add focus-visible polyfill behavior
    document.addEventListener('focusin', (e) => {
      if (hadKeyboardEvent) {
        e.target.classList.add('focus-visible');
      }
    });

    document.addEventListener('focusout', (e) => {
      e.target.classList.remove('focus-visible');
    });

    document.documentElement.classList.add('js-focus-visible');
  }

  static addARIAAttributes() {
    // Add ARIA landmarks
    const main = document.querySelector('main');
    if (main && !main.getAttribute('role')) {
      main.setAttribute('role', 'main');
    }

    const nav = document.querySelector('nav');
    if (nav && !nav.getAttribute('role')) {
      nav.setAttribute('role', 'navigation');
    }

    // Add ARIA labels to buttons without text
    const iconButtons = document.querySelectorAll('button:not([aria-label])');
    iconButtons.forEach(button => {
      const icon = button.querySelector('i[class*="fa-"]');
      if (icon && !button.textContent.trim()) {
        const iconClass = icon.className;
        let label = 'Button';
        
        if (iconClass.includes('fa-menu') || iconClass.includes('fa-bars')) {
          label = 'Open menu';
        } else if (iconClass.includes('fa-close') || iconClass.includes('fa-times')) {
          label = 'Close';
        } else if (iconClass.includes('fa-search')) {
          label = 'Search';
        }
        
        button.setAttribute('aria-label', label);
      }
    });

    // Add ARIA expanded states
    const dropdownToggles = document.querySelectorAll('[data-toggle="dropdown"]');
    dropdownToggles.forEach(toggle => {
      if (!toggle.hasAttribute('aria-expanded')) {
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  static setupFocusManagement() {
    // Trap focus in modals
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        const modal = document.querySelector('.modal.active, .lightbox.active');
        if (modal) {
          this.trapFocus(e, modal);
        }
      }
    });

    // Close modals on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const modal = document.querySelector('.modal.active, .lightbox.active');
        if (modal) {
          const closeButton = modal.querySelector('.close, .modal-close, .lightbox-close');
          if (closeButton) {
            closeButton.click();
          }
        }
      }
    });
  }

  static trapFocus(event, container) {
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];

    if (event.shiftKey) {
      if (document.activeElement === firstFocusable) {
        event.preventDefault();
        lastFocusable.focus();
      }
    } else {
      if (document.activeElement === lastFocusable) {
        event.preventDefault();
        firstFocusable.focus();
      }
    }
  }

  /**
   * Add performance optimizations
   */
  static addPerformanceOptimizations() {
    // Reduce motion for users who prefer it
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      document.documentElement.classList.add('reduced-motion');
    }

    // Network-aware optimizations
    if ('connection' in navigator) {
      const connection = navigator.connection;
      if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
        document.documentElement.classList.add('slow-connection');
      }
      
      if (connection.saveData) {
        document.documentElement.classList.add('save-data');
      }
    }

    // Add performance observer for Core Web Vitals
    if ('PerformanceObserver' in window) {
      this.setupPerformanceObserver();
    }
  }

  static setupPerformanceObserver() {
    // Observe layout shifts
    try {
      const clsObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) {
            console.log('CLS detected:', entry.value);
          }
        }
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });
    } catch (e) {
      // Silently fail if not supported
    }

    // Observe largest contentful paint
    try {
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        console.log('LCP:', lastEntry.startTime);
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
    } catch (e) {
      // Silently fail if not supported
    }
  }

  // Utility function
  static throttle(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
}