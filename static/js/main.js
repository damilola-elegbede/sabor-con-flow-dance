/**
 * Main JavaScript
 * Sabor Con Flow Dance Studio
 *
 * Contains utility functions and interactive behaviors for the site.
 * Includes: ButtonLoader, RippleEffect, lazy loading fallback, mobile menu toggle.
 */

/* ==========================================================================
   RIPPLE EFFECT MODULE
   ========================================================================== */

/**
 * RippleEffect - Creates Material Design-inspired ripple on button click
 *
 * Usage:
 *   Automatically initialized on all .btn elements
 *   Or manually: RippleEffect.attachRipple(buttonElement);
 */
const RippleEffect = {
    /**
     * Check if user prefers reduced motion
     * @returns {boolean}
     */
    prefersReducedMotion() {
        return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    },

    /**
     * Initialize ripple effect on all buttons
     */
    init() {
        // Respect reduced motion preference
        if (this.prefersReducedMotion()) {
            return;
        }

        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => this.attachRipple(button));
    },

    /**
     * Attach ripple event listener to a button
     * @param {HTMLElement} button - Button element
     */
    attachRipple(button) {
        button.addEventListener('mousedown', (e) => this.setRipplePosition(e, button));
        button.addEventListener('click', (e) => this.createRipple(e, button));
    },

    /**
     * Set CSS custom properties for ripple position
     * @param {MouseEvent} e - Mouse event
     * @param {HTMLElement} button - Button element
     */
    setRipplePosition(e, button) {
        const rect = button.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        button.style.setProperty('--ripple-x', `${x}px`);
        button.style.setProperty('--ripple-y', `${y}px`);
    },

    /**
     * Create and animate ripple effect
     * @param {MouseEvent} e - Click event
     * @param {HTMLElement} button - Button element
     */
    createRipple(e, button) {
        // Remove existing ripple class
        button.classList.remove('ripple-active');

        // Force reflow to restart animation
        void button.offsetWidth;

        // Add ripple class
        button.classList.add('ripple-active');

        // Remove class after animation completes
        setTimeout(() => {
            button.classList.remove('ripple-active');
        }, 600);
    }
};

// Make RippleEffect available globally
window.RippleEffect = RippleEffect;

/* ==========================================================================
   BUTTON LOADING STATE MANAGER
   ========================================================================== */

/**
 * ButtonLoader - Manages button loading states with accessibility support
 *
 * Usage:
 *   ButtonLoader.start(buttonElement, 'Submitting...');
 *   // ... async operation
 *   ButtonLoader.stop(buttonElement);
 */
const ButtonLoader = {
    /**
     * Set button to loading state
     * @param {HTMLElement} button - The button element
     * @param {string} loadingText - Text for screen readers (default: 'Loading...')
     */
    start(button, loadingText = 'Loading...') {
        if (!button || button.classList.contains('btn--loading')) return;

        // Add loading class (child elements preserved - CSS handles visual hiding)
        button.classList.add('btn--loading');
        button.setAttribute('aria-busy', 'true');

        // Add screen reader text
        const srText = document.createElement('span');
        srText.className = 'btn-loading-text';
        srText.textContent = loadingText;
        button.appendChild(srText);
    },

    /**
     * Remove loading state from button
     * @param {HTMLElement} button - The button element
     */
    stop(button) {
        if (!button || !button.classList.contains('btn--loading')) return;

        button.classList.remove('btn--loading');
        button.setAttribute('aria-busy', 'false');

        // Remove screen reader text (child elements preserved automatically)
        const srText = button.querySelector('.btn-loading-text');
        if (srText) {
            srText.remove();
        }
    },

    /**
     * Toggle loading state
     * @param {HTMLElement} button - The button element
     * @param {boolean} isLoading - Whether to show loading state
     * @param {string} loadingText - Text for screen readers
     */
    toggle(button, isLoading, loadingText = 'Loading...') {
        if (isLoading) {
            this.start(button, loadingText);
        } else {
            this.stop(button);
        }
    }
};

// Make ButtonLoader available globally
window.ButtonLoader = ButtonLoader;

/* ==========================================================================
   LAZY LOADING FALLBACK
   ========================================================================== */

/**
 * Lazy Loading Fallback for browsers without native support
 * Uses Intersection Observer API as fallback
 */
(function initLazyLoading() {
    // Check for native lazy loading support
    if ('loading' in HTMLImageElement.prototype) {
        // Native support - add loaded class for CSS transitions
        const lazyImages = document.querySelectorAll('img[loading="lazy"]');
        lazyImages.forEach(function(img) {
            if (img.complete) {
                img.classList.add('lazy-loaded');
            } else {
                img.addEventListener('load', function() {
                    img.classList.add('lazy-loaded');
                });
            }
        });
        return;
    }

    // Fallback using Intersection Observer
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');

    if (!lazyImages.length) return;

    // Check for Intersection Observer support
    if (!('IntersectionObserver' in window)) {
        // Ultimate fallback - load all images immediately
        lazyImages.forEach(function(img) {
            img.classList.add('lazy-loaded');
        });
        return;
    }

    const imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                var img = entry.target;
                img.classList.add('lazy-loaded');
                observer.unobserve(img);
            }
        });
    }, {
        rootMargin: '50px 0px',
        threshold: 0.01
    });

    lazyImages.forEach(function(img) {
        imageObserver.observe(img);
    });

    // Cleanup observer on page unload to prevent memory leaks
    window.addEventListener('beforeunload', function() {
        if (imageObserver) {
            imageObserver.disconnect();
        }
    });
})();

/* ==========================================================================
   DOM READY INITIALIZATION
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize ripple effect on all buttons
    RippleEffect.init();

    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('.nav');
    const overlay = document.querySelector('.menu-overlay');

    if (menuToggle && nav && overlay) {
        menuToggle.addEventListener('click', function() {
            nav.classList.toggle('active');
        });

        overlay.addEventListener('click', function() {
            menuToggle.classList.remove('active');
            nav.classList.remove('active');
            overlay.classList.remove('active');
        });
    }

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    // Form validation with loading state
    // Note: For traditional form submissions, the page navigates away.
    // For AJAX forms, call ButtonLoader.stop() in your success/error handlers.
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');

            // Add loading state to submit button if form is valid
            if (form.checkValidity()) {
                const submitBtn = form.querySelector('[type="submit"]');
                if (submitBtn && submitBtn.classList.contains('btn')) {
                    ButtonLoader.start(submitBtn, 'Submitting...');

                    // Clear loading state on page navigation (back/forward)
                    window.addEventListener('pageshow', function clearOnPageShow() {
                        ButtonLoader.stop(submitBtn);
                        window.removeEventListener('pageshow', clearOnPageShow);
                    });
                }
            }
        });
    });
});