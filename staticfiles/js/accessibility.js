/**
 * Accessibility Enhancement Script for Sabor Con Flow Dance
 * WCAG 2.1 AA Compliance Implementation
 * SPEC_06 Group C Task 8
 */

class AccessibilityManager {
    constructor() {
        this.isHighContrast = false;
        this.isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        this.focusableElements = [
            'a[href]',
            'button:not([disabled])',
            'input:not([disabled])',
            'select:not([disabled])',
            'textarea:not([disabled])',
            '[tabindex]:not([tabindex="-1"])',
            'details',
            'summary'
        ].join(', ');
        
        this.init();
    }

    init() {
        this.setupSkipLinks();
        this.enhanceFocusManagement();
        this.setupKeyboardNavigation();
        this.setupAriaLiveRegions();
        this.enhanceFormAccessibility();
        this.setupHighContrastToggle();
        this.setupReducedMotionSupport();
        this.monitorDynamicContent();
        
        // Initialize after DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeComponents());
        } else {
            this.initializeComponents();
        }
    }

    /**
     * Skip Links Enhancement
     */
    setupSkipLinks() {
        const skipLink = document.querySelector('.skip-link');
        if (skipLink) {
            skipLink.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(skipLink.getAttribute('href'));
                if (target) {
                    target.focus();
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    
                    // Announce to screen readers
                    this.announceToScreenReader('Navigated to main content');
                }
            });
        }

        // Add skip links if missing
        this.ensureSkipLinks();
    }

    ensureSkipLinks() {
        if (!document.querySelector('.skip-link')) {
            const skipLink = document.createElement('a');
            skipLink.href = '#main-content';
            skipLink.className = 'skip-link';
            skipLink.textContent = 'Skip to main content';
            skipLink.setAttribute('aria-label', 'Skip to main content');
            
            // Insert as first element in body
            document.body.insertBefore(skipLink, document.body.firstChild);
        }
    }

    /**
     * Focus Management Enhancement
     */
    enhanceFocusManagement() {
        // Improve focus visibility
        this.addFocusStyles();
        
        // Track focus for accessibility tools
        document.addEventListener('focusin', this.handleFocusIn.bind(this));
        document.addEventListener('focusout', this.handleFocusOut.bind(this));
        
        // Handle focus traps in modals
        this.setupModalFocusTraps();
    }

    addFocusStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Enhanced focus indicators for accessibility */
            .accessibility-focus {
                outline: 3px solid #C7B375 !important;
                outline-offset: 2px !important;
                border-radius: 4px !important;
                box-shadow: 0 0 0 6px rgba(199, 179, 117, 0.3) !important;
            }
            
            /* High contrast mode adjustments */
            .high-contrast .accessibility-focus {
                outline: 3px solid #FFFF00 !important;
                background-color: #000000 !important;
                color: #FFFF00 !important;
            }
            
            /* Skip link enhancement */
            .skip-link:focus {
                position: fixed !important;
                top: 10px !important;
                left: 50% !important;
                transform: translateX(-50%) !important;
                z-index: 10000 !important;
                padding: 12px 24px !important;
                background: #000000 !important;
                color: #C7B375 !important;
                text-decoration: none !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
                border: 2px solid #C7B375 !important;
            }
        `;
        document.head.appendChild(style);
    }

    handleFocusIn(event) {
        const element = event.target;
        element.classList.add('accessibility-focus');
        
        // Announce focus changes to screen readers when needed
        if (element.hasAttribute('aria-label') || element.hasAttribute('aria-labelledby')) {
            // Screen reader will handle this
            return;
        }
        
        // Add context for complex interactive elements
        if (element.matches('[role="button"], [role="tab"], [role="menuitem"]')) {
            this.announceElementContext(element);
        }
    }

    handleFocusOut(event) {
        event.target.classList.remove('accessibility-focus');
    }

    setupModalFocusTraps() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                const modal = document.querySelector('[aria-modal="true"]:not([aria-hidden="true"])');
                if (modal) {
                    this.trapFocusInModal(e, modal);
                }
            }
        });
    }

    trapFocusInModal(event, modal) {
        const focusableElements = modal.querySelectorAll(this.focusableElements);
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (event.shiftKey) {
            if (document.activeElement === firstElement) {
                event.preventDefault();
                lastElement.focus();
            }
        } else {
            if (document.activeElement === lastElement) {
                event.preventDefault();
                firstElement.focus();
            }
        }
    }

    /**
     * Keyboard Navigation Enhancement
     */
    setupKeyboardNavigation() {
        // Arrow key navigation for menus
        this.setupMenuNavigation();
        
        // Tab/carousel navigation
        this.setupTabNavigation();
        
        // Escape key handling
        this.setupEscapeHandling();
        
        // Enter/Space key handling for custom buttons
        this.setupCustomButtonHandling();
    }

    setupMenuNavigation() {
        const menus = document.querySelectorAll('[role="menu"], [role="menubar"]');
        
        menus.forEach(menu => {
            menu.addEventListener('keydown', (e) => {
                const items = menu.querySelectorAll('[role="menuitem"]');
                const currentIndex = Array.from(items).indexOf(e.target);
                
                switch (e.key) {
                    case 'ArrowDown':
                        e.preventDefault();
                        const nextIndex = (currentIndex + 1) % items.length;
                        items[nextIndex].focus();
                        break;
                    case 'ArrowUp':
                        e.preventDefault();
                        const prevIndex = (currentIndex - 1 + items.length) % items.length;
                        items[prevIndex].focus();
                        break;
                    case 'Home':
                        e.preventDefault();
                        items[0].focus();
                        break;
                    case 'End':
                        e.preventDefault();
                        items[items.length - 1].focus();
                        break;
                }
            });
        });
    }

    setupTabNavigation() {
        const tabLists = document.querySelectorAll('[role="tablist"]');
        
        tabLists.forEach(tabList => {
            tabList.addEventListener('keydown', (e) => {
                const tabs = tabList.querySelectorAll('[role="tab"]');
                const currentIndex = Array.from(tabs).indexOf(e.target);
                
                switch (e.key) {
                    case 'ArrowLeft':
                        e.preventDefault();
                        const prevTab = currentIndex > 0 ? tabs[currentIndex - 1] : tabs[tabs.length - 1];
                        this.activateTab(prevTab);
                        break;
                    case 'ArrowRight':
                        e.preventDefault();
                        const nextTab = currentIndex < tabs.length - 1 ? tabs[currentIndex + 1] : tabs[0];
                        this.activateTab(nextTab);
                        break;
                    case 'Home':
                        e.preventDefault();
                        this.activateTab(tabs[0]);
                        break;
                    case 'End':
                        e.preventDefault();
                        this.activateTab(tabs[tabs.length - 1]);
                        break;
                }
            });
        });
    }

    activateTab(tab) {
        const tabList = tab.closest('[role="tablist"]');
        const tabs = tabList.querySelectorAll('[role="tab"]');
        
        // Deactivate all tabs
        tabs.forEach(t => {
            t.setAttribute('aria-selected', 'false');
            t.setAttribute('tabindex', '-1');
        });
        
        // Activate selected tab
        tab.setAttribute('aria-selected', 'true');
        tab.setAttribute('tabindex', '0');
        tab.focus();
        
        // Show corresponding panel
        const panelId = tab.getAttribute('aria-controls');
        if (panelId) {
            const panels = document.querySelectorAll('[role="tabpanel"]');
            panels.forEach(p => p.hidden = true);
            
            const activePanel = document.getElementById(panelId);
            if (activePanel) {
                activePanel.hidden = false;
            }
        }
        
        this.announceToScreenReader(`Tab ${tab.textContent} selected`);
    }

    setupEscapeHandling() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                // Close modals
                const modal = document.querySelector('[aria-modal="true"]:not([aria-hidden="true"])');
                if (modal) {
                    this.closeModal(modal);
                    return;
                }
                
                // Close dropdowns
                const expandedButton = document.querySelector('[aria-expanded="true"]');
                if (expandedButton) {
                    this.collapseDropdown(expandedButton);
                    expandedButton.focus();
                }
            }
        });
    }

    setupCustomButtonHandling() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                const target = e.target;
                
                // Handle custom buttons with role="button"
                if (target.getAttribute('role') === 'button' && !target.matches('button, input, a')) {
                    e.preventDefault();
                    target.click();
                }
            }
        });
    }

    /**
     * ARIA Live Regions Setup
     */
    setupAriaLiveRegions() {
        // Create live regions if they don't exist
        this.ensureLiveRegions();
        
        // Monitor form validation
        this.setupFormValidationAnnouncements();
        
        // Monitor dynamic content changes
        this.setupContentChangeAnnouncements();
    }

    setupFormValidationAnnouncements() {
        // Listen for form validation events and announce them to screen readers
        document.addEventListener('invalid', (event) => {
            const input = event.target;
            if (input.validationMessage) {
                this.announceToScreenReader(
                    `Validation error: ${input.validationMessage}`, 
                    'assertive'
                );
            }
        }, true);

        // Listen for successful form submissions
        document.addEventListener('submit', (event) => {
            const form = event.target;
            if (form.checkValidity()) {
                this.announceToScreenReader('Form submitted successfully', 'polite');
            }
        });

        // Listen for input changes that clear validation errors
        document.addEventListener('input', (event) => {
            const input = event.target;
            if (input.getAttribute('aria-invalid') === 'true' && input.validity.valid) {
                this.announceToScreenReader(
                    `${input.getAttribute('aria-label') || 'Field'} is now valid`, 
                    'polite'
                );
            }
        });
    }

    setupContentChangeAnnouncements() {
        // Monitor for content changes that should be announced
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                // Announce when new content is added to live regions
                if (mutation.type === 'childList' && mutation.target.getAttribute('aria-live')) {
                    // Content will be automatically announced by screen readers
                    return;
                }

                // Announce when important content changes
                if (mutation.target.matches('[data-announce-changes]')) {
                    const announcement = mutation.target.getAttribute('data-announcement') || 
                                      'Content has been updated';
                    this.announceToScreenReader(announcement, 'polite');
                }

                // Announce when alerts or error messages appear
                if (mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            if (node.matches('[role="alert"], .alert, .error-message')) {
                                const message = node.textContent.trim();
                                if (message) {
                                    this.announceToScreenReader(message, 'assertive');
                                }
                            }
                        }
                    });
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['aria-live', 'role']
        });
    }

    ensureLiveRegions() {
        // Polite announcements
        if (!document.getElementById('aria-live-polite')) {
            const politeRegion = document.createElement('div');
            politeRegion.id = 'aria-live-polite';
            politeRegion.setAttribute('aria-live', 'polite');
            politeRegion.setAttribute('aria-atomic', 'true');
            politeRegion.className = 'sr-only';
            document.body.appendChild(politeRegion);
        }
        
        // Assertive announcements
        if (!document.getElementById('aria-live-assertive')) {
            const assertiveRegion = document.createElement('div');
            assertiveRegion.id = 'aria-live-assertive';
            assertiveRegion.setAttribute('aria-live', 'assertive');
            assertiveRegion.setAttribute('aria-atomic', 'true');
            assertiveRegion.className = 'sr-only';
            document.body.appendChild(assertiveRegion);
        }
    }

    announceToScreenReader(message, priority = 'polite') {
        const regionId = priority === 'assertive' ? 'aria-live-assertive' : 'aria-live-polite';
        const region = document.getElementById(regionId);
        
        if (region) {
            // Clear previous message
            region.textContent = '';
            
            // Announce new message after a brief delay
            setTimeout(() => {
                region.textContent = message;
            }, 100);
            
            // Clear message after 5 seconds to prevent clutter
            setTimeout(() => {
                region.textContent = '';
            }, 5000);
        }
    }

    /**
     * Form Accessibility Enhancement
     */
    enhanceFormAccessibility() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            this.enhanceFormLabels(form);
            this.enhanceFormValidation(form);
            this.enhanceFormErrorHandling(form);
            this.addFormInstructions(form);
        });
    }

    enhanceFormLabels(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            // Ensure every input has a label
            if (!input.getAttribute('aria-label') && !input.getAttribute('aria-labelledby')) {
                const label = form.querySelector(`label[for="${input.id}"]`);
                if (!label && input.id) {
                    // Create implicit label if missing
                    const wrapper = input.closest('.form-group, .field-wrapper');
                    if (wrapper) {
                        const labelText = wrapper.querySelector('.form-label, .field-label');
                        if (labelText) {
                            labelText.setAttribute('for', input.id);
                        }
                    }
                }
            }
            
            // Add required field indicators
            if (input.required) {
                input.setAttribute('aria-required', 'true');
                
                // Add visual indicator if missing
                const label = form.querySelector(`label[for="${input.id}"]`);
                if (label && !label.querySelector('.required-indicator')) {
                    const indicator = document.createElement('span');
                    indicator.className = 'required-indicator';
                    indicator.textContent = ' *';
                    indicator.setAttribute('aria-label', 'required');
                    label.appendChild(indicator);
                }
            }
            
            // Associate help text
            const helpText = input.getAttribute('data-help') || 
                            form.querySelector(`[data-help-for="${input.id}"]`)?.textContent;
            if (helpText) {
                const helpId = `${input.id}-help`;
                let helpElement = document.getElementById(helpId);
                
                if (!helpElement) {
                    helpElement = document.createElement('div');
                    helpElement.id = helpId;
                    helpElement.className = 'form-help';
                    helpElement.textContent = helpText;
                    input.parentNode.appendChild(helpElement);
                }
                
                const describedBy = input.getAttribute('aria-describedby') || '';
                if (!describedBy.includes(helpId)) {
                    input.setAttribute('aria-describedby', `${describedBy} ${helpId}`.trim());
                }
            }
        });
    }

    enhanceFormValidation(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.addEventListener('invalid', (e) => {
                e.target.setAttribute('aria-invalid', 'true');
                this.showValidationError(e.target);
            });
            
            input.addEventListener('input', (e) => {
                if (e.target.getAttribute('aria-invalid') === 'true') {
                    if (e.target.validity.valid) {
                        e.target.setAttribute('aria-invalid', 'false');
                        this.clearValidationError(e.target);
                    }
                }
            });
        });
    }

    showValidationError(input) {
        const errorId = `${input.id}-error`;
        let errorElement = document.getElementById(errorId);
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.id = errorId;
            errorElement.className = 'form-error';
            errorElement.setAttribute('role', 'alert');
            input.parentNode.appendChild(errorElement);
        }
        
        errorElement.textContent = input.validationMessage;
        errorElement.style.display = 'block';
        
        // Associate with input
        const describedBy = input.getAttribute('aria-describedby') || '';
        if (!describedBy.includes(errorId)) {
            input.setAttribute('aria-describedby', `${describedBy} ${errorId}`.trim());
        }
        
        // Announce error
        this.announceToScreenReader(`Error: ${input.validationMessage}`, 'assertive');
    }

    clearValidationError(input) {
        const errorId = `${input.id}-error`;
        const errorElement = document.getElementById(errorId);
        
        if (errorElement) {
            errorElement.style.display = 'none';
            
            // Remove from aria-describedby
            const describedBy = input.getAttribute('aria-describedby') || '';
            const newDescribedBy = describedBy.replace(errorId, '').replace(/\s+/g, ' ').trim();
            if (newDescribedBy) {
                input.setAttribute('aria-describedby', newDescribedBy);
            } else {
                input.removeAttribute('aria-describedby');
            }
        }
    }

    /**
     * High Contrast Mode Support
     */
    setupHighContrastToggle() {
        // Create high contrast toggle button
        const toggleButton = document.createElement('button');
        toggleButton.id = 'high-contrast-toggle';
        toggleButton.className = 'accessibility-control';
        toggleButton.textContent = 'Toggle High Contrast';
        toggleButton.setAttribute('aria-label', 'Toggle high contrast mode');
        toggleButton.setAttribute('aria-pressed', 'false');
        
        toggleButton.addEventListener('click', () => {
            this.toggleHighContrast();
        });
        
        // Add to accessibility controls area or header
        const header = document.querySelector('header, .navbar');
        if (header) {
            header.appendChild(toggleButton);
        }
    }

    toggleHighContrast() {
        this.isHighContrast = !this.isHighContrast;
        document.body.classList.toggle('high-contrast', this.isHighContrast);
        
        const button = document.getElementById('high-contrast-toggle');
        if (button) {
            button.setAttribute('aria-pressed', this.isHighContrast.toString());
        }
        
        // Save preference
        localStorage.setItem('high-contrast', this.isHighContrast.toString());
        
        this.announceToScreenReader(
            `High contrast mode ${this.isHighContrast ? 'enabled' : 'disabled'}`
        );
    }

    /**
     * Reduced Motion Support
     */
    setupReducedMotionSupport() {
        if (this.isReducedMotion) {
            document.body.classList.add('reduced-motion');
            
            // Disable animations
            const style = document.createElement('style');
            style.textContent = `
                .reduced-motion *,
                .reduced-motion *::before,
                .reduced-motion *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                    scroll-behavior: auto !important;
                }
            `;
            document.head.appendChild(style);
        }
        
        // Listen for changes
        window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
            this.isReducedMotion = e.matches;
            document.body.classList.toggle('reduced-motion', this.isReducedMotion);
        });
    }

    /**
     * Dynamic Content Monitoring
     */
    monitorDynamicContent() {
        // Monitor for new elements added to DOM
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.enhanceNewElement(node);
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    enhanceNewElement(element) {
        // Enhance forms
        if (element.matches('form') || element.querySelector('form')) {
            const forms = element.matches('form') ? [element] : element.querySelectorAll('form');
            forms.forEach(form => this.enhanceFormAccessibility(form));
        }
        
        // Enhance interactive elements
        const interactiveElements = element.querySelectorAll(this.focusableElements);
        interactiveElements.forEach(el => {
            if (!el.hasAttribute('aria-label') && !el.hasAttribute('aria-labelledby')) {
                this.addMissingLabels(el);
            }
        });
    }

    addMissingLabels(element) {
        // Add basic accessibility attributes to unlabeled interactive elements
        if (element.matches('button') && !element.textContent.trim()) {
            element.setAttribute('aria-label', 'Button');
        }
        
        if (element.matches('a') && !element.textContent.trim()) {
            element.setAttribute('aria-label', 'Link');
        }
        
        // Add role if missing
        if (element.matches('div[onclick], span[onclick]') && !element.getAttribute('role')) {
            element.setAttribute('role', 'button');
            element.setAttribute('tabindex', '0');
        }
    }

    /**
     * Component Initialization
     */
    initializeComponents() {
        // Initialize mobile menu accessibility
        this.initializeMobileMenu();
        
        // Initialize carousel accessibility
        this.initializeCarousels();
        
        // Initialize modal accessibility
        this.initializeModals();
        
        // Load saved preferences
        this.loadAccessibilityPreferences();
    }

    initializeMobileMenu() {
        const mobileToggle = document.getElementById('navbar-toggle');
        const mobileMenu = document.getElementById('navbar-mobile');
        
        if (mobileToggle && mobileMenu) {
            mobileToggle.addEventListener('click', () => {
                const isExpanded = mobileToggle.getAttribute('aria-expanded') === 'true';
                mobileToggle.setAttribute('aria-expanded', (!isExpanded).toString());
                mobileMenu.setAttribute('aria-hidden', isExpanded.toString());
                
                if (!isExpanded) {
                    // Focus first menu item when opening
                    const firstMenuItem = mobileMenu.querySelector('a, button');
                    if (firstMenuItem) {
                        setTimeout(() => firstMenuItem.focus(), 100);
                    }
                }
            });
        }
    }

    initializeCarousels() {
        const carousels = document.querySelectorAll('.carousel, .testimonial-carousel');
        
        carousels.forEach(carousel => {
            carousel.setAttribute('role', 'region');
            carousel.setAttribute('aria-label', 'Carousel');
            
            // Add live region for slide announcements
            const liveRegion = document.createElement('div');
            liveRegion.className = 'sr-only';
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            carousel.appendChild(liveRegion);
            
            // Enhance controls
            const controls = carousel.querySelectorAll('.carousel-btn, .carousel-dot');
            controls.forEach((control, index) => {
                if (!control.getAttribute('aria-label')) {
                    if (control.matches('.carousel-dot')) {
                        control.setAttribute('aria-label', `Go to slide ${index + 1}`);
                    } else if (control.textContent.includes('prev')) {
                        control.setAttribute('aria-label', 'Previous slide');
                    } else if (control.textContent.includes('next')) {
                        control.setAttribute('aria-label', 'Next slide');
                    }
                }
            });
        });
    }

    initializeModals() {
        const modals = document.querySelectorAll('.modal, [role="dialog"]');
        
        modals.forEach(modal => {
            if (!modal.getAttribute('role')) {
                modal.setAttribute('role', 'dialog');
            }
            modal.setAttribute('aria-modal', 'true');
            
            // Ensure modal has accessible name
            if (!modal.getAttribute('aria-label') && !modal.getAttribute('aria-labelledby')) {
                const title = modal.querySelector('h1, h2, h3, .modal-title');
                if (title) {
                    if (!title.id) {
                        title.id = `modal-title-${Date.now()}`;
                    }
                    modal.setAttribute('aria-labelledby', title.id);
                }
            }
        });
    }

    loadAccessibilityPreferences() {
        // Load high contrast preference
        const highContrastPref = localStorage.getItem('high-contrast');
        if (highContrastPref === 'true') {
            this.toggleHighContrast();
        }
    }

    /**
     * Utility Methods
     */
    closeModal(modal) {
        modal.setAttribute('aria-hidden', 'true');
        modal.style.display = 'none';
        
        // Return focus to trigger element
        const trigger = document.querySelector(`[aria-controls="${modal.id}"]`);
        if (trigger) {
            trigger.focus();
        }
        
        this.announceToScreenReader('Modal closed');
    }

    collapseDropdown(button) {
        button.setAttribute('aria-expanded', 'false');
        const menuId = button.getAttribute('aria-controls');
        if (menuId) {
            const menu = document.getElementById(menuId);
            if (menu) {
                menu.hidden = true;
            }
        }
    }

    announceElementContext(element) {
        const role = element.getAttribute('role');
        const label = element.getAttribute('aria-label') || element.textContent;
        
        if (role && label) {
            this.announceToScreenReader(`${role}: ${label}`);
        }
    }
}

// Initialize accessibility manager
const accessibilityManager = new AccessibilityManager();

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AccessibilityManager;
}