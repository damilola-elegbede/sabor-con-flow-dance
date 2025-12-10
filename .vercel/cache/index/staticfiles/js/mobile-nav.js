/**
 * Mobile Navigation Controller
 * Handles hamburger menu toggle, overlay interactions, and accessibility
 */

(function() {
    'use strict';

    // Cache DOM elements
    const elements = {
        hamburger: null,
        mobileMenu: null,
        overlay: null,
        closeButton: null,
        menuLinks: [],
        body: document.body,
        focusableElements: []
    };

    // State management
    let isMenuOpen = false;
    let lastFocusedElement = null;
    let scrollPosition = 0;

    /**
     * Initialize mobile navigation
     */
    function init() {
        // Get DOM elements
        elements.hamburger = document.getElementById('navbar-toggle');
        elements.mobileMenu = document.getElementById('navbar-mobile');
        elements.overlay = document.getElementById('mobile-menu-overlay');
        elements.closeButton = document.getElementById('mobile-menu-close');
        
        if (!elements.hamburger || !elements.mobileMenu) {
            return; // Exit if required elements don't exist
        }

        // Get menu links
        elements.menuLinks = elements.mobileMenu.querySelectorAll('.navbar-item');
        
        // Get all focusable elements in mobile menu
        elements.focusableElements = elements.mobileMenu.querySelectorAll(
            'button, a[href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        // Attach event listeners
        attachEventListeners();
    }

    /**
     * Attach all event listeners
     */
    function attachEventListeners() {
        // Hamburger menu click
        elements.hamburger.addEventListener('click', toggleMenu);
        
        // Close button click
        if (elements.closeButton) {
            elements.closeButton.addEventListener('click', closeMenu);
        }
        
        // Overlay click
        if (elements.overlay) {
            elements.overlay.addEventListener('click', closeMenu);
        }
        
        // Menu links click
        elements.menuLinks.forEach(link => {
            link.addEventListener('click', handleLinkClick);
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', handleKeyboard);
        
        // Window resize
        let resizeTimer;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                if (window.innerWidth >= 768 && isMenuOpen) {
                    closeMenu();
                }
            }, 250);
        });
        
        // Prevent focus trap when menu is closed
        elements.mobileMenu.addEventListener('focusin', function(e) {
            if (!isMenuOpen) {
                e.preventDefault();
                elements.hamburger.focus();
            }
        });
    }

    /**
     * Toggle mobile menu
     */
    function toggleMenu(event) {
        event.preventDefault();
        event.stopPropagation();
        
        if (isMenuOpen) {
            closeMenu();
        } else {
            openMenu();
        }
    }

    /**
     * Open mobile menu
     */
    function openMenu() {
        if (isMenuOpen) return;
        
        isMenuOpen = true;
        lastFocusedElement = document.activeElement;
        
        // Save scroll position and prevent body scroll
        scrollPosition = window.pageYOffset;
        elements.body.classList.add('menu-open');
        elements.body.style.top = `-${scrollPosition}px`;
        
        // Add active classes with slight delay for animation
        elements.hamburger.classList.add('active');
        elements.overlay.classList.add('active');
        
        setTimeout(() => {
            elements.mobileMenu.classList.add('active');
        }, 10);
        
        // Update ARIA attributes
        elements.hamburger.setAttribute('aria-expanded', 'true');
        elements.mobileMenu.setAttribute('aria-hidden', 'false');
        elements.overlay.setAttribute('aria-hidden', 'false');
        
        // Focus management
        setTimeout(() => {
            if (elements.closeButton) {
                elements.closeButton.focus();
            } else if (elements.focusableElements.length > 0) {
                elements.focusableElements[0].focus();
            }
        }, 300);
        
        // Announce menu opened for screen readers
        announceToScreenReader('Navigation menu opened');
    }

    /**
     * Close mobile menu
     */
    function closeMenu() {
        if (!isMenuOpen) return;
        
        isMenuOpen = false;
        
        // Remove active classes
        elements.hamburger.classList.remove('active');
        elements.mobileMenu.classList.remove('active');
        elements.overlay.classList.remove('active');
        
        // Update ARIA attributes
        elements.hamburger.setAttribute('aria-expanded', 'false');
        elements.mobileMenu.setAttribute('aria-hidden', 'true');
        elements.overlay.setAttribute('aria-hidden', 'true');
        
        // Restore body scroll
        elements.body.classList.remove('menu-open');
        elements.body.style.top = '';
        window.scrollTo(0, scrollPosition);
        
        // Restore focus
        if (lastFocusedElement) {
            lastFocusedElement.focus();
        }
        
        // Announce menu closed for screen readers
        announceToScreenReader('Navigation menu closed');
    }

    /**
     * Handle menu link clicks
     */
    function handleLinkClick(event) {
        // Check if it's an anchor link
        const href = event.currentTarget.getAttribute('href');
        if (href && href.startsWith('#')) {
            // Allow default anchor behavior but close menu
            setTimeout(closeMenu, 100);
        } else {
            // For regular links, close menu immediately
            closeMenu();
        }
    }

    /**
     * Handle keyboard navigation
     */
    function handleKeyboard(event) {
        if (!isMenuOpen) return;
        
        const key = event.key;
        
        // Close menu on Escape
        if (key === 'Escape') {
            event.preventDefault();
            closeMenu();
            return;
        }
        
        // Tab trapping
        if (key === 'Tab') {
            trapFocus(event);
        }
    }

    /**
     * Trap focus within mobile menu
     */
    function trapFocus(event) {
        if (elements.focusableElements.length === 0) return;
        
        const firstFocusable = elements.focusableElements[0];
        const lastFocusable = elements.focusableElements[elements.focusableElements.length - 1];
        
        if (event.shiftKey) {
            // Shift + Tab
            if (document.activeElement === firstFocusable) {
                event.preventDefault();
                lastFocusable.focus();
            }
        } else {
            // Tab
            if (document.activeElement === lastFocusable) {
                event.preventDefault();
                firstFocusable.focus();
            }
        }
    }

    /**
     * Announce message to screen readers
     */
    function announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.classList.add('sr-only');
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    /**
     * Check if user prefers reduced motion
     */
    function prefersReducedMotion() {
        return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }

    /**
     * Initialize when DOM is ready
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Public API (optional, for external control)
    window.mobileNav = {
        open: openMenu,
        close: closeMenu,
        toggle: toggleMenu,
        isOpen: () => isMenuOpen
    };

})();