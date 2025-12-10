/**
 * Calendly Widget Integration - SPEC_05 Group A Task 1
 * Enhanced with Sabor con Flow branding, mobile optimization, and comprehensive error handling
 */

class CalendlyIntegration {
    constructor() {
        this.isCalendlyLoaded = false;
        this.loadPromise = null;
        this.initializationQueue = [];
        this.eventHandlers = new Map();
        this.config = {
            defaultUrl: 'https://calendly.com/saborconflowdance',
            retryAttempts: 3,
            retryDelay: 1000,
            loadTimeout: 10000,
            theme: {
                backgroundColor: '#000000',
                textColor: '#C7B375',
                primaryColor: '#C7B375'
            }
        };
        
        // Track analytics
        this.analytics = {
            widgetLoads: 0,
            bookingAttempts: 0,
            completedBookings: 0,
            errors: []
        };
        
        this.init();
    }
    
    /**
     * Initialize the Calendly integration
     */
    async init() {
        try {
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.setup());
            } else {
                this.setup();
            }
        } catch (error) {
            this.handleError('Initialization failed', error);
        }
    }
    
    /**
     * Setup after DOM is ready
     */
    async setup() {
        try {
            // Load Calendly if not already loaded
            await this.loadCalendlyScript();
            
            // Initialize existing widgets
            this.initializeWidgets();
            
            // Setup mutation observer for dynamically added widgets
            this.setupMutationObserver();
            
            // Setup global event listeners
            this.setupEventListeners();
            
            console.log('✅ Calendly integration initialized successfully');
        } catch (error) {
            this.handleError('Setup failed', error);
        }
    }
    
    /**
     * Load Calendly external script
     */
    async loadCalendlyScript() {
        if (this.isCalendlyLoaded || window.Calendly) {
            this.isCalendlyLoaded = true;
            return Promise.resolve();
        }
        
        if (this.loadPromise) {
            return this.loadPromise;
        }
        
        this.loadPromise = new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://assets.calendly.com/assets/external/widget.js';
            script.async = true;
            script.defer = true;
            
            const timeoutId = setTimeout(() => {
                reject(new Error('Calendly script load timeout'));
            }, this.config.loadTimeout);
            
            script.onload = () => {
                clearTimeout(timeoutId);
                this.isCalendlyLoaded = true;
                console.log('📅 Calendly script loaded successfully');
                resolve();
            };
            
            script.onerror = () => {
                clearTimeout(timeoutId);
                reject(new Error('Failed to load Calendly script'));
            };
            
            document.head.appendChild(script);
        });
        
        return this.loadPromise;
    }
    
    /**
     * Initialize all Calendly widgets on the page
     */
    initializeWidgets() {
        const widgets = document.querySelectorAll('.calendly-widget-container');
        
        widgets.forEach((widget, index) => {
            this.initializeWidget(widget, index);
        });
    }
    
    /**
     * Initialize a single widget
     */
    async initializeWidget(container, index = 0) {
        try {
            const widgetType = container.dataset.widgetType || 'inline';
            const calendlyUrl = container.dataset.calendlyUrl || this.config.defaultUrl;
            
            // Parse prefill data if provided
            let prefillData = {};
            if (container.dataset.prefill) {
                try {
                    prefillData = JSON.parse(container.dataset.prefill);
                } catch (e) {
                    console.warn('Invalid prefill data:', container.dataset.prefill);
                }
            }
            
            // Add URL parameters as prefill data
            const urlParams = this.getUrlParameters();
            prefillData = { ...prefillData, ...urlParams };
            
            switch (widgetType) {
                case 'inline':
                    await this.initializeInlineWidget(container, calendlyUrl, prefillData, index);
                    break;
                case 'popup':
                    this.initializePopupWidget(container, calendlyUrl, prefillData);
                    break;
                case 'badge':
                    this.initializeBadgeWidget(container, calendlyUrl, prefillData);
                    break;
                default:
                    console.warn('Unknown widget type:', widgetType);
            }
            
            this.analytics.widgetLoads++;
            
        } catch (error) {
            this.handleError(`Widget initialization failed for container ${index}`, error);
        }
    }
    
    /**
     * Initialize inline widget
     */
    async initializeInlineWidget(container, url, prefillData, index) {
        const inlineWidget = container.querySelector('.calendly-inline-widget');
        if (!inlineWidget) return;
        
        const loadingState = inlineWidget.querySelector('.calendly-loading-state');
        
        try {
            // Ensure Calendly is loaded
            await this.loadCalendlyScript();
            
            // Build widget options
            const options = this.buildWidgetOptions(inlineWidget, prefillData);
            
            // Initialize Calendly inline widget
            window.Calendly.initInlineWidget({
                url: url,
                parentElement: inlineWidget,
                ...options
            });
            
            // Hide loading state after a delay
            setTimeout(() => {
                if (loadingState) {
                    loadingState.classList.add('hidden');
                    setTimeout(() => {
                        loadingState.style.display = 'none';
                    }, 300);
                }
            }, 1500);
            
            // Setup event tracking
            this.setupWidgetEventTracking(inlineWidget, 'inline');
            
        } catch (error) {
            this.showWidgetError(inlineWidget, error);
        }
    }
    
    /**
     * Initialize popup widget
     */
    initializePopupWidget(container, url, prefillData) {
        const button = container.querySelector('.calendly-popup-button');
        if (!button) return;
        
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            
            try {
                await this.loadCalendlyScript();
                
                const options = this.buildWidgetOptions(button, prefillData);
                
                window.Calendly.initPopupWidget({
                    url: url,
                    ...options
                });
                
                this.analytics.bookingAttempts++;
                this.setupWidgetEventTracking(button, 'popup');
                
            } catch (error) {
                this.handleError('Popup widget failed to open', error);
                this.showUserFriendlyError('Unable to open booking calendar. Please try again.');
            }
        });
    }
    
    /**
     * Initialize badge widget
     */
    async initializeBadgeWidget(container, url, prefillData) {
        try {
            await this.loadCalendlyScript();
            
            const badgeWidget = container.querySelector('.calendly-badge-widget');
            const text = badgeWidget.dataset.text || 'Schedule time with me';
            const color = badgeWidget.dataset.color || '#C7B375';
            const textColor = badgeWidget.dataset.textColor || '#000000';
            const branding = badgeWidget.dataset.branding !== 'false';
            
            const options = this.buildWidgetOptions(badgeWidget, prefillData);
            
            window.Calendly.initBadgeWidget({
                url: url,
                text: text,
                color: color,
                textColor: textColor,
                branding: branding,
                ...options
            });
            
            this.setupWidgetEventTracking(badgeWidget, 'badge');
            
        } catch (error) {
            this.handleError('Badge widget initialization failed', error);
        }
    }
    
    /**
     * Build widget options from data attributes
     */
    buildWidgetOptions(element, prefillData = {}) {
        const options = {};
        
        // Theme customization
        if (element.dataset.backgroundColor) {
            options.backgroundColor = element.dataset.backgroundColor;
        } else {
            options.backgroundColor = this.config.theme.backgroundColor;
        }
        
        if (element.dataset.textColor) {
            options.textColor = element.dataset.textColor;
        } else {
            options.textColor = this.config.theme.textColor;
        }
        
        if (element.dataset.primaryColor) {
            options.primaryColor = element.dataset.primaryColor;
        } else {
            options.primaryColor = this.config.theme.primaryColor;
        }
        
        // Widget behavior
        if (element.dataset.hideGdprBanner === 'true') {
            options.hideGdprBanner = true;
        }
        
        if (element.dataset.hideLandingPageDetails === 'true') {
            options.hideLandingPageDetails = true;
        }
        
        // Prefill data
        if (Object.keys(prefillData).length > 0) {
            options.prefill = this.sanitizePrefillData(prefillData);
        }
        
        // Mobile optimization
        if (this.isMobile()) {
            options.embedType = 'Inline';
            if (element.classList.contains('calendly-inline-widget')) {
                const height = parseInt(element.dataset.height) || 630;
                const mobileHeight = Math.min(height, window.innerHeight - 100);
                element.style.height = `${mobileHeight}px`;
            }
        }
        
        return options;
    }
    
    /**
     * Setup event tracking for widgets
     */
    setupWidgetEventTracking(element, type) {
        // Listen for Calendly events
        window.addEventListener('message', (e) => {
            if (e.origin !== 'https://calendly.com') return;
            
            const data = e.data;
            if (data.event) {
                this.handleCalendlyEvent(data.event, data.payload, type, element);
            }
        });
    }
    
    /**
     * Handle Calendly events
     */
    handleCalendlyEvent(eventName, payload, widgetType, element) {
        console.log(`📅 Calendly Event: ${eventName}`, { payload, widgetType });
        
        switch (eventName) {
            case 'calendly.event_scheduled':
                this.handleBookingCompleted(payload, widgetType, element);
                break;
            case 'calendly.profile_page_viewed':
                this.handleProfileViewed(payload, widgetType, element);
                break;
            case 'calendly.event_type_viewed':
                this.handleEventTypeViewed(payload, widgetType, element);
                break;
            case 'calendly.date_and_time_selected':
                this.handleDateTimeSelected(payload, widgetType, element);
                break;
        }
        
        // Trigger custom events for external analytics
        this.triggerCustomEvent('calendly:' + eventName, {
            payload,
            widgetType,
            element
        });
    }
    
    /**
     * Handle completed booking
     */
    handleBookingCompleted(payload, widgetType, element) {
        this.analytics.completedBookings++;
        
        // Show success message
        this.showSuccessMessage('Booking confirmed! Check your email for details.');
        
        // Track conversion
        this.trackConversion(payload, widgetType);
        
        // Custom success actions
        this.triggerCustomEvent('calendly:booking_completed', {
            payload,
            widgetType,
            element,
            analytics: this.analytics
        });
        
        console.log('✅ Booking completed successfully', payload);
    }
    
    /**
     * Handle profile viewed
     */
    handleProfileViewed(payload, widgetType, element) {
        this.triggerCustomEvent('calendly:profile_viewed', { payload, widgetType, element });
    }
    
    /**
     * Handle event type viewed
     */
    handleEventTypeViewed(payload, widgetType, element) {
        this.triggerCustomEvent('calendly:event_type_viewed', { payload, widgetType, element });
    }
    
    /**
     * Handle date and time selected
     */
    handleDateTimeSelected(payload, widgetType, element) {
        this.triggerCustomEvent('calendly:datetime_selected', { payload, widgetType, element });
    }
    
    /**
     * Get URL parameters for prefilling
     */
    getUrlParameters() {
        const params = {};
        const urlParams = new URLSearchParams(window.location.search);
        
        // Map common URL parameters to Calendly prefill fields
        const mapping = {
            'name': 'name',
            'first_name': 'firstName',
            'last_name': 'lastName',
            'email': 'email',
            'phone': 'phone',
            'lesson_type': 'customAnswers.a1',
            'experience_level': 'customAnswers.a2',
            'preferred_time': 'customAnswers.a3'
        };
        
        for (const [urlParam, calendlyField] of Object.entries(mapping)) {
            const value = urlParams.get(urlParam);
            if (value) {
                if (calendlyField.includes('.')) {
                    const [parent, child] = calendlyField.split('.');
                    if (!params[parent]) params[parent] = {};
                    params[parent][child] = value;
                } else {
                    params[calendlyField] = value;
                }
            }
        }
        
        return params;
    }
    
    /**
     * Sanitize prefill data
     */
    sanitizePrefillData(data) {
        const sanitized = {};
        
        // Only allow safe fields
        const allowedFields = [
            'name', 'firstName', 'lastName', 'email', 'phone',
            'customAnswers', 'salesforceUuid', 'utmCampaign',
            'utmSource', 'utmMedium', 'utmContent', 'utmTerm'
        ];
        
        for (const field of allowedFields) {
            if (data[field]) {
                if (typeof data[field] === 'string') {
                    sanitized[field] = data[field].substring(0, 255); // Limit length
                } else if (typeof data[field] === 'object') {
                    sanitized[field] = data[field];
                }
            }
        }
        
        return sanitized;
    }
    
    /**
     * Setup mutation observer for dynamic content
     */
    setupMutationObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const widgets = node.querySelectorAll ? 
                            node.querySelectorAll('.calendly-widget-container') : [];
                        
                        if (node.classList && node.classList.contains('calendly-widget-container')) {
                            this.initializeWidget(node);
                        } else {
                            widgets.forEach((widget, index) => {
                                this.initializeWidget(widget, index);
                            });
                        }
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        // Handle resize for mobile optimization
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));
        
        // Handle visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.handlePageHidden();
            } else {
                this.handlePageVisible();
            }
        });
    }
    
    /**
     * Handle window resize
     */
    handleResize() {
        const inlineWidgets = document.querySelectorAll('.calendly-inline-widget');
        
        inlineWidgets.forEach((widget) => {
            if (this.isMobile()) {
                const height = parseInt(widget.dataset.height) || 630;
                const mobileHeight = Math.min(height, window.innerHeight - 100);
                widget.style.height = `${mobileHeight}px`;
            } else {
                const originalHeight = widget.dataset.height || '630';
                widget.style.height = `${originalHeight}px`;
            }
        });
    }
    
    /**
     * Handle page hidden
     */
    handlePageHidden() {
        // Optional: Pause any ongoing processes
    }
    
    /**
     * Handle page visible
     */
    handlePageVisible() {
        // Optional: Resume any paused processes
    }
    
    /**
     * Show widget error
     */
    showWidgetError(widget, error) {
        const loadingState = widget.querySelector('.calendly-loading-state');
        if (loadingState) {
            loadingState.innerHTML = `
                <div class="calendly-error-state">
                    <i class="fas fa-exclamation-triangle" style="font-size: 24px; color: #ff6b6b; margin-bottom: 16px;"></i>
                    <h3>Unable to Load Calendar</h3>
                    <p>Please try refreshing the page or visit our Calendly page directly.</p>
                    <a href="${this.config.defaultUrl}" target="_blank" class="btn btn-primary" style="margin-top: 16px;">
                        Open in New Tab
                    </a>
                </div>
            `;
        }
        
        this.handleError('Widget display error', error);
    }
    
    /**
     * Show user-friendly error message
     */
    showUserFriendlyError(message) {
        // Create a temporary notification
        const notification = document.createElement('div');
        notification.className = 'calendly-error-notification';
        notification.innerHTML = `
            <div class="error-content">
                <i class="fas fa-exclamation-circle"></i>
                <span>${message}</span>
                <button class="close-btn" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            .calendly-error-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: #ff6b6b;
                color: white;
                padding: 16px;
                border-radius: 8px;
                z-index: 10000;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                animation: slideIn 0.3s ease-out;
            }
            .error-content {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            .close-btn {
                background: none;
                border: none;
                color: white;
                font-size: 18px;
                cursor: pointer;
                margin-left: auto;
            }
            @keyframes slideIn {
                from { transform: translateX(100%); }
                to { transform: translateX(0); }
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    /**
     * Show success message
     */
    showSuccessMessage(message) {
        const notification = document.createElement('div');
        notification.className = 'calendly-success-notification';
        notification.innerHTML = `
            <div class="success-content">
                <i class="fas fa-check-circle"></i>
                <span>${message}</span>
                <button class="close-btn" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            .calendly-success-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: #51cf66;
                color: white;
                padding: 16px;
                border-radius: 8px;
                z-index: 10000;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                animation: slideIn 0.3s ease-out;
            }
            .success-content {
                display: flex;
                align-items: center;
                gap: 12px;
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 4000);
    }
    
    /**
     * Track conversion for analytics
     */
    trackConversion(payload, widgetType) {
        // Google Analytics 4
        if (typeof gtag === 'function') {
            gtag('event', 'booking_completed', {
                'event_category': 'calendly',
                'event_label': widgetType,
                'value': 1
            });
        }
        
        // Facebook Pixel
        if (typeof fbq === 'function') {
            fbq('track', 'Schedule', {
                content_name: 'Private Lesson Booking',
                content_category: 'Dance Lessons'
            });
        }
        
        // Custom analytics
        this.triggerCustomEvent('calendly:conversion', {
            payload,
            widgetType,
            timestamp: new Date().toISOString()
        });
    }
    
    /**
     * Trigger custom event
     */
    triggerCustomEvent(eventName, detail) {
        const event = new CustomEvent(eventName, { detail });
        document.dispatchEvent(event);
    }
    
    /**
     * Handle errors
     */
    handleError(message, error) {
        console.error(`❌ Calendly Integration Error: ${message}`, error);
        
        this.analytics.errors.push({
            message,
            error: error.message || error,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent
        });
        
        // Report to external error tracking
        this.triggerCustomEvent('calendly:error', {
            message,
            error,
            analytics: this.analytics
        });
    }
    
    /**
     * Utility: Check if mobile
     */
    isMobile() {
        return window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
    
    /**
     * Utility: Debounce function
     */
    debounce(func, wait) {
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
    
    /**
     * Get analytics data
     */
    getAnalytics() {
        return { ...this.analytics };
    }
    
    /**
     * Public API methods
     */
    
    /**
     * Manually open popup widget
     */
    async openPopup(url = null, options = {}) {
        try {
            await this.loadCalendlyScript();
            
            const calendlyUrl = url || this.config.defaultUrl;
            const widgetOptions = {
                ...this.buildWidgetOptions(document.body, options.prefill || {}),
                ...options
            };
            
            window.Calendly.initPopupWidget({
                url: calendlyUrl,
                ...widgetOptions
            });
            
            this.analytics.bookingAttempts++;
            
        } catch (error) {
            this.handleError('Manual popup open failed', error);
            throw error;
        }
    }
    
    /**
     * Destroy all widgets
     */
    destroy() {
        // Remove event listeners
        window.removeEventListener('resize', this.handleResize);
        document.removeEventListener('visibilitychange', this.handlePageVisible);
        
        // Clear analytics
        this.analytics = {
            widgetLoads: 0,
            bookingAttempts: 0,
            completedBookings: 0,
            errors: []
        };
        
        console.log('🗑️ Calendly integration destroyed');
    }
}

// Initialize when script loads
const calendlyIntegration = new CalendlyIntegration();

// Export for global access
window.CalendlyIntegration = CalendlyIntegration;
window.calendlyIntegration = calendlyIntegration;

// Expose public API
window.calendlyAPI = {
    openPopup: (url, options) => calendlyIntegration.openPopup(url, options),
    getAnalytics: () => calendlyIntegration.getAnalytics(),
    destroy: () => calendlyIntegration.destroy()
};