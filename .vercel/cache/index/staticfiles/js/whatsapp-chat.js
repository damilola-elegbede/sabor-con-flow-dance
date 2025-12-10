/**
 * WhatsApp Chat Button with Scroll Behavior - SPEC_05 Group A Task 2
 * Handles show/hide on scroll, smooth animations, and accessibility features
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        showDelay: 1000,           // Show button after 1 second
        scrollThreshold: 100,      // Show after scrolling 100px
        scrollDebounce: 16,        // Debounce scroll events (~60fps)
        hideOnScrollUp: true,      // Hide when scrolling up
        showOnScrollDown: true,    // Show when scrolling down
        animationDuration: 300,    // Animation duration in ms
        trackingEnabled: false,    // Analytics tracking (disabled by default)
        phoneNumber: '17205555555', // WhatsApp phone number (will be read from data attributes)
        defaultMessage: "Hi! I'm interested in Sabor con Flow dance classes." // Will be read from data attributes
    };

    // State management
    let state = {
        isVisible: false,
        lastScrollY: 0,
        scrollDirection: 'down',
        ticking: false,
        initialized: false,
        button: null,
        container: null
    };

    /**
     * Initialize the WhatsApp chat button
     */
    function init() {
        if (state.initialized) return;

        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        state.container = document.getElementById('whatsapp-float');
        if (!state.container) {
            console.warn('WhatsApp button container not found');
            return;
        }

        state.button = state.container.querySelector('.whatsapp-button');
        if (!state.button) {
            console.warn('WhatsApp button element not found');
            return;
        }

        readConfigFromDataAttributes();
        setupEventListeners();
        updateButtonLink();
        
        // Show button after initial delay
        setTimeout(() => {
            if (shouldShowButton()) {
                showButton();
            }
        }, CONFIG.showDelay);

        state.initialized = true;
        console.log('WhatsApp chat button initialized');
    }

    /**
     * Read configuration from button data attributes
     */
    function readConfigFromDataAttributes() {
        if (!state.button) return;

        const phoneNumber = state.button.getAttribute('data-phone');
        const message = state.button.getAttribute('data-message');

        if (phoneNumber) {
            CONFIG.phoneNumber = phoneNumber;
        }

        if (message) {
            CONFIG.defaultMessage = message;
        }

        console.log('WhatsApp config loaded:', {
            phone: CONFIG.phoneNumber,
            message: CONFIG.defaultMessage
        });
    }

    /**
     * Set up all event listeners
     */
    function setupEventListeners() {
        // Scroll event with debouncing
        let scrollTimeout;
        window.addEventListener('scroll', function() {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            scrollTimeout = setTimeout(handleScroll, CONFIG.scrollDebounce);
        }, { passive: true });

        // Resize event
        window.addEventListener('resize', debounce(handleResize, 250), { passive: true });

        // Visibility change (tab focus/blur)
        document.addEventListener('visibilitychange', handleVisibilityChange);

        // Button click tracking
        if (state.button) {
            state.button.addEventListener('click', handleButtonClick);
            
            // Keyboard accessibility
            state.button.addEventListener('keydown', handleKeyDown);
        }

        // Network status (if supported)
        if ('connection' in navigator) {
            window.addEventListener('online', handleNetworkChange);
            window.addEventListener('offline', handleNetworkChange);
        }
    }

    /**
     * Handle scroll events and determine visibility
     */
    function handleScroll() {
        if (!state.ticking) {
            requestAnimationFrame(updateScrollState);
            state.ticking = true;
        }
    }

    /**
     * Update scroll state and button visibility
     */
    function updateScrollState() {
        const currentScrollY = window.pageYOffset || document.documentElement.scrollTop;
        const scrollDifference = currentScrollY - state.lastScrollY;
        
        // Determine scroll direction
        if (Math.abs(scrollDifference) > 5) { // Ignore tiny movements
            state.scrollDirection = scrollDifference > 0 ? 'down' : 'up';
        }

        // Update visibility based on scroll behavior
        if (shouldShowButton()) {
            if (!state.isVisible) {
                showButton();
            }
        } else {
            if (state.isVisible) {
                hideButton();
            }
        }

        state.lastScrollY = currentScrollY;
        state.ticking = false;
    }

    /**
     * Determine if button should be visible
     */
    function shouldShowButton() {
        const scrollY = window.pageYOffset || document.documentElement.scrollTop;
        const isScrolledEnough = scrollY > CONFIG.scrollThreshold;
        
        // Always show if user hasn't scrolled much
        if (!isScrolledEnough) {
            return true;
        }

        // Hide on scroll up, show on scroll down
        if (CONFIG.hideOnScrollUp && state.scrollDirection === 'up') {
            return false;
        }

        if (CONFIG.showOnScrollDown && state.scrollDirection === 'down') {
            return true;
        }

        // Default to current state if no clear direction
        return state.isVisible;
    }

    /**
     * Show the WhatsApp button with animation
     */
    function showButton() {
        if (state.isVisible || !state.container) return;

        state.container.classList.remove('hidden');
        state.container.classList.add('visible');
        state.isVisible = true;

        // Announce to screen readers
        announceToScreenReader('WhatsApp chat button is now available');

        // Track showing (if analytics enabled)
        if (CONFIG.trackingEnabled) {
            trackEvent('whatsapp_button_shown');
        }
    }

    /**
     * Hide the WhatsApp button with animation
     */
    function hideButton() {
        if (!state.isVisible || !state.container) return;

        state.container.classList.remove('visible');
        state.container.classList.add('hidden');
        state.isVisible = false;

        // Track hiding (if analytics enabled)
        if (CONFIG.trackingEnabled) {
            trackEvent('whatsapp_button_hidden');
        }
    }

    /**
     * Handle button click events
     */
    function handleButtonClick(event) {
        // Track click
        if (CONFIG.trackingEnabled) {
            trackEvent('whatsapp_button_clicked', {
                scroll_position: window.pageYOffset,
                page_url: window.location.href
            });
        }

        // Add visual feedback
        state.button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            if (state.button) {
                state.button.style.transform = '';
            }
        }, 150);

        // Announce to screen readers
        announceToScreenReader('Opening WhatsApp chat');
    }

    /**
     * Handle keyboard events for accessibility
     */
    function handleKeyDown(event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            state.button.click();
        }
    }

    /**
     * Handle window resize events
     */
    function handleResize() {
        // Recalculate positioning if needed
        if (state.isVisible && shouldShowButton()) {
            // Button is visible and should remain visible
        } else if (state.isVisible && !shouldShowButton()) {
            hideButton();
        } else if (!state.isVisible && shouldShowButton()) {
            showButton();
        }
    }

    /**
     * Handle page visibility changes
     */
    function handleVisibilityChange() {
        if (document.hidden) {
            // Page is now hidden (user switched tabs)
            if (CONFIG.trackingEnabled) {
                trackEvent('page_hidden');
            }
        } else {
            // Page is now visible (user returned to tab)
            if (CONFIG.trackingEnabled) {
                trackEvent('page_visible');
            }
        }
    }

    /**
     * Handle network connectivity changes
     */
    function handleNetworkChange() {
        const isOnline = navigator.onLine;
        
        if (state.button) {
            if (isOnline) {
                state.button.classList.remove('offline');
                state.button.setAttribute('aria-label', 'Contact us via WhatsApp - Opens in new window');
            } else {
                state.button.classList.add('offline');
                state.button.setAttribute('aria-label', 'WhatsApp unavailable - No internet connection');
            }
        }

        if (CONFIG.trackingEnabled) {
            trackEvent('network_change', { online: isOnline });
        }
    }

    /**
     * Update the WhatsApp button link with proper formatting
     */
    function updateButtonLink() {
        if (!state.button) return;

        const encodedMessage = encodeURIComponent(CONFIG.defaultMessage);
        const whatsappUrl = `https://wa.me/${CONFIG.phoneNumber}?text=${encodedMessage}`;
        
        state.button.setAttribute('href', whatsappUrl);
    }

    /**
     * Announce messages to screen readers
     */
    function announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;

        document.body.appendChild(announcement);

        // Remove after announcement
        setTimeout(() => {
            if (announcement.parentNode) {
                announcement.parentNode.removeChild(announcement);
            }
        }, 1000);
    }

    /**
     * Simple event tracking function
     */
    function trackEvent(eventName, eventData = {}) {
        if (!CONFIG.trackingEnabled) return;

        // Integration point for analytics (Google Analytics, etc.)
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, eventData);
        }

        if (typeof fbq !== 'undefined') {
            fbq('track', 'CustomEvent', { event_name: eventName, ...eventData });
        }

        // Console logging for development
        console.log('WhatsApp Button Event:', eventName, eventData);
    }

    /**
     * Debounce utility function
     */
    function debounce(func, wait, immediate) {
        let timeout;
        return function executedFunction() {
            const context = this;
            const args = arguments;
            
            const later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            
            if (callNow) func.apply(context, args);
        };
    }

    /**
     * Public API for external control
     */
    window.WhatsAppChat = {
        show: showButton,
        hide: hideButton,
        toggle: function() {
            if (state.isVisible) {
                hideButton();
            } else {
                showButton();
            }
        },
        isVisible: function() {
            return state.isVisible;
        },
        updatePhone: function(phoneNumber) {
            CONFIG.phoneNumber = phoneNumber;
            updateButtonLink();
        },
        updateMessage: function(message) {
            CONFIG.defaultMessage = message;
            updateButtonLink();
        },
        enableTracking: function() {
            CONFIG.trackingEnabled = true;
        },
        disableTracking: function() {
            CONFIG.trackingEnabled = false;
        }
    };

    // Initialize when script loads
    init();

    // Fallback initialization for edge cases
    if (document.readyState !== 'loading') {
        setTimeout(init, 100);
    }

})();