/**
 * Google Analytics 4 Implementation for Sabor Con Flow Dance
 * Privacy-compliant analytics with enhanced ecommerce tracking
 * 
 * Features:
 * - GDPR compliant cookie consent management
 * - Enhanced ecommerce for class bookings
 * - Custom event tracking for all interactions
 * - Performance monitoring integration
 * - Debug mode for development
 */

class SaborAnalytics {
    constructor() {
        this.config = {
            measurementId: window.GA4_MEASUREMENT_ID || 'G-XXXXXXXXXX',
            debugMode: window.location.hostname === 'localhost' || window.location.search.includes('debug=1'),
            consentKey: 'scf_analytics_consent',
            consentExpiry: 365 * 24 * 60 * 60 * 1000, // 1 year
            enhancedEcommerce: true,
            currency: 'USD',
            businessInfo: {
                name: 'Sabor Con Flow Dance',
                category: 'Dance Studio',
                location: 'Boulder, CO'
            }
        };

        this.consentGiven = false;
        this.eventsQueue = [];
        this.initialized = false;

        this.init();
    }

    /**
     * Initialize analytics system with consent check
     */
    init() {
        this.log('Initializing Sabor Analytics...');
        
        // Check existing consent
        this.checkExistingConsent();
        
        // Show consent banner if needed
        if (!this.consentGiven && !this.hasConsentChoice()) {
            this.showConsentBanner();
        } else if (this.consentGiven) {
            this.initializeGA4();
        }

        // Set up event listeners
        this.setupEventListeners();
        
        // Track page view
        this.trackPageView();
    }

    /**
     * Check for existing consent from localStorage
     */
    checkExistingConsent() {
        try {
            const consent = localStorage.getItem(this.config.consentKey);
            if (consent) {
                const consentData = JSON.parse(consent);
                const isExpired = Date.now() > consentData.timestamp + this.config.consentExpiry;
                
                if (!isExpired) {
                    this.consentGiven = consentData.accepted;
                    this.log(`Existing consent found: ${this.consentGiven}`);
                    return;
                }
            }
        } catch (error) {
            this.log('Error checking existing consent:', error);
        }
        this.consentGiven = false;
    }

    /**
     * Check if user has made a consent choice
     */
    hasConsentChoice() {
        try {
            return localStorage.getItem(this.config.consentKey) !== null;
        } catch (error) {
            return false;
        }
    }

    /**
     * Initialize Google Analytics 4
     */
    initializeGA4() {
        if (this.initialized || !this.consentGiven) return;

        this.log('Initializing GA4...');

        // Load gtag script
        const script = document.createElement('script');
        script.async = true;
        script.src = `https://www.googletagmanager.com/gtag/js?id=${this.config.measurementId}`;
        document.head.appendChild(script);

        // Initialize gtag
        window.dataLayer = window.dataLayer || [];
        window.gtag = function() {
            dataLayer.push(arguments);
        };

        gtag('js', new Date());
        
        // Configure GA4 with enhanced ecommerce
        gtag('config', this.config.measurementId, {
            debug_mode: this.config.debugMode,
            send_page_view: false, // We'll handle page views manually
            enhanced_ecommerce: this.config.enhancedEcommerce,
            currency: this.config.currency,
            custom_map: {
                'custom_parameter_1': 'dance_class_type',
                'custom_parameter_2': 'instructor_name',
                'custom_parameter_3': 'booking_source'
            }
        });

        this.initialized = true;
        this.processQueuedEvents();
        this.log('GA4 initialized successfully');
    }

    /**
     * Show GDPR compliant consent banner
     */
    showConsentBanner() {
        // Remove existing banner if present
        const existingBanner = document.getElementById('analytics-consent-banner');
        if (existingBanner) {
            existingBanner.remove();
        }

        const banner = document.createElement('div');
        banner.id = 'analytics-consent-banner';
        banner.className = 'analytics-consent-banner';
        banner.innerHTML = `
            <div class="consent-content">
                <div class="consent-text">
                    <h4>🍪 Cookie Consent</h4>
                    <p>We use cookies and analytics to improve your experience and understand how you interact with our website. This helps us provide better dance classes and events.</p>
                    <details>
                        <summary>What data do we collect?</summary>
                        <ul>
                            <li>Page views and navigation patterns</li>
                            <li>Class booking interactions</li>
                            <li>Video engagement metrics</li>
                            <li>Contact form submissions</li>
                            <li>No personal information is stored</li>
                        </ul>
                    </details>
                </div>
                <div class="consent-actions">
                    <button id="consent-accept" class="btn btn-primary">Accept All</button>
                    <button id="consent-reject" class="btn btn-outline">Decline</button>
                    <button id="consent-customize" class="btn btn-outline">Customize</button>
                </div>
            </div>
        `;

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .analytics-consent-banner {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: rgba(0, 0, 0, 0.95);
                color: white;
                padding: 1.5rem;
                z-index: 10000;
                border-top: 3px solid var(--color-gold, #C7B375);
                backdrop-filter: blur(10px);
                animation: slideUp 0.3s ease-out;
            }
            
            @keyframes slideUp {
                from { transform: translateY(100%); }
                to { transform: translateY(0); }
            }
            
            .consent-content {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                gap: 2rem;
                align-items: center;
                flex-wrap: wrap;
            }
            
            .consent-text {
                flex: 1;
                min-width: 300px;
            }
            
            .consent-text h4 {
                margin: 0 0 0.5rem 0;
                color: var(--color-gold, #C7B375);
            }
            
            .consent-text p {
                margin: 0 0 1rem 0;
                font-size: 0.9rem;
                line-height: 1.4;
            }
            
            .consent-text details {
                font-size: 0.85rem;
            }
            
            .consent-text summary {
                cursor: pointer;
                color: var(--color-gold, #C7B375);
                margin-bottom: 0.5rem;
            }
            
            .consent-text ul {
                margin: 0.5rem 0 0 1rem;
                font-size: 0.8rem;
            }
            
            .consent-actions {
                display: flex;
                gap: 1rem;
                flex-wrap: wrap;
            }
            
            .consent-actions .btn {
                padding: 0.75rem 1.5rem;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.2s ease;
                white-space: nowrap;
            }
            
            .consent-actions .btn-primary {
                background: var(--color-gold, #C7B375);
                color: black;
            }
            
            .consent-actions .btn-primary:hover {
                background: var(--color-gold-dark, #9C8E5A);
                color: white;
            }
            
            .consent-actions .btn-outline {
                background: transparent;
                border: 2px solid var(--color-gold, #C7B375);
                color: var(--color-gold, #C7B375);
            }
            
            .consent-actions .btn-outline:hover {
                background: var(--color-gold, #C7B375);
                color: black;
            }
            
            @media (max-width: 768px) {
                .consent-content {
                    flex-direction: column;
                    text-align: center;
                }
                
                .consent-actions {
                    justify-content: center;
                    width: 100%;
                }
                
                .consent-actions .btn {
                    flex: 1;
                    min-width: 120px;
                }
            }
        `;
        document.head.appendChild(style);

        document.body.appendChild(banner);

        // Add event listeners
        document.getElementById('consent-accept').addEventListener('click', () => this.handleConsent(true));
        document.getElementById('consent-reject').addEventListener('click', () => this.handleConsent(false));
        document.getElementById('consent-customize').addEventListener('click', () => this.showCustomizeModal());

        this.log('Consent banner displayed');
    }

    /**
     * Handle consent choice
     */
    handleConsent(accepted) {
        this.consentGiven = accepted;
        
        // Store consent choice
        try {
            localStorage.setItem(this.config.consentKey, JSON.stringify({
                accepted: accepted,
                timestamp: Date.now(),
                version: '1.0'
            }));
        } catch (error) {
            this.log('Error storing consent:', error);
        }

        // Remove banner
        const banner = document.getElementById('analytics-consent-banner');
        if (banner) {
            banner.style.animation = 'slideDown 0.3s ease-out';
            setTimeout(() => banner.remove(), 300);
        }

        if (accepted) {
            this.initializeGA4();
            this.showConsentThankYou();
        } else {
            this.log('Analytics consent declined');
        }
    }

    /**
     * Show thank you message after consent
     */
    showConsentThankYou() {
        const toast = document.createElement('div');
        toast.className = 'consent-toast';
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-check-circle"></i>
                <span>Thank you! Analytics enabled to improve your experience.</span>
            </div>
        `;

        const style = document.createElement('style');
        style.textContent = `
            .consent-toast {
                position: fixed;
                top: 2rem;
                right: 2rem;
                background: var(--color-gold, #C7B375);
                color: black;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                z-index: 10001;
                animation: slideInRight 0.3s ease-out, fadeOut 0.3s ease-out 2.7s;
            }
            
            .toast-content {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-weight: 600;
            }
            
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
        `;
        document.head.appendChild(style);

        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    /**
     * Set up all event listeners for tracking
     */
    setupEventListeners() {
        // CTA button clicks
        this.setupCTATracking();
        
        // Form submissions
        this.setupFormTracking();
        
        // Video interactions
        this.setupVideoTracking();
        
        // Scroll depth tracking
        this.setupScrollTracking();
        
        // Link clicks and navigation
        this.setupNavigationTracking();
        
        // Booking interactions
        this.setupBookingTracking();
        
        // Social media clicks
        this.setupSocialTracking();
    }

    /**
     * Track CTA button clicks
     */
    setupCTATracking() {
        document.addEventListener('click', (event) => {
            const element = event.target.closest('.btn, .cta-button, [data-cta]');
            if (!element) return;

            const ctaText = element.textContent?.trim() || element.getAttribute('aria-label') || 'Unknown CTA';
            const ctaLocation = this.getElementLocation(element);
            const ctaType = element.getAttribute('data-cta') || this.inferCTAType(ctaText);

            this.trackEvent('cta_click', {
                cta_text: ctaText,
                cta_type: ctaType,
                cta_location: ctaLocation,
                page_path: window.location.pathname
            });

            this.log(`CTA clicked: ${ctaText} (${ctaType}) at ${ctaLocation}`);
        });
    }

    /**
     * Track form submissions
     */
    setupFormTracking() {
        document.addEventListener('submit', (event) => {
            const form = event.target;
            if (!form.tagName || form.tagName.toLowerCase() !== 'form') return;

            const formName = form.getAttribute('name') || form.id || 'unnamed_form';
            const formType = this.inferFormType(form);
            const formData = new FormData(form);
            const fieldCount = Array.from(formData.keys()).length;

            this.trackEvent('form_submit', {
                form_name: formName,
                form_type: formType,
                field_count: fieldCount,
                page_path: window.location.pathname
            });

            // Enhanced ecommerce for testimonial submissions
            if (formType === 'testimonial') {
                this.trackEvent('generate_lead', {
                    currency: this.config.currency,
                    value: 0, // No monetary value for testimonials
                    lead_type: 'testimonial',
                    form_name: formName
                });
            }

            this.log(`Form submitted: ${formName} (${formType})`);
        });

        // Track form field interactions
        document.addEventListener('focus', (event) => {
            if (event.target.tagName?.toLowerCase() === 'input' || 
                event.target.tagName?.toLowerCase() === 'textarea') {
                
                const form = event.target.closest('form');
                const formName = form?.getAttribute('name') || form?.id || 'unnamed_form';
                const fieldName = event.target.name || event.target.id || 'unnamed_field';

                this.trackEvent('form_field_focus', {
                    form_name: formName,
                    field_name: fieldName,
                    field_type: event.target.type || 'text'
                });
            }
        });
    }

    /**
     * Track video interactions
     */
    setupVideoTracking() {
        // Track video elements
        document.querySelectorAll('video').forEach(video => {
            const videoTitle = video.getAttribute('data-title') || video.getAttribute('title') || 'Untitled Video';
            let progressMilestones = [25, 50, 75, 90];
            let milestoneTracked = {};

            video.addEventListener('play', () => {
                this.trackEvent('video_start', {
                    video_title: videoTitle,
                    video_duration: Math.round(video.duration || 0),
                    page_path: window.location.pathname
                });
            });

            video.addEventListener('pause', () => {
                this.trackEvent('video_pause', {
                    video_title: videoTitle,
                    video_current_time: Math.round(video.currentTime || 0),
                    video_duration: Math.round(video.duration || 0),
                    video_percent: Math.round((video.currentTime / video.duration) * 100) || 0
                });
            });

            video.addEventListener('ended', () => {
                this.trackEvent('video_complete', {
                    video_title: videoTitle,
                    video_duration: Math.round(video.duration || 0),
                    page_path: window.location.pathname
                });
            });

            // Progress tracking
            video.addEventListener('timeupdate', () => {
                if (video.duration) {
                    const percent = Math.round((video.currentTime / video.duration) * 100);
                    
                    progressMilestones.forEach(milestone => {
                        if (percent >= milestone && !milestoneTracked[milestone]) {
                            milestoneTracked[milestone] = true;
                            this.trackEvent('video_progress', {
                                video_title: videoTitle,
                                video_percent: milestone,
                                video_current_time: Math.round(video.currentTime),
                                video_duration: Math.round(video.duration)
                            });
                        }
                    });
                }
            });
        });

        // Track YouTube/Vimeo embeds
        this.setupEmbeddedVideoTracking();
    }

    /**
     * Track embedded video interactions (YouTube, Vimeo)
     */
    setupEmbeddedVideoTracking() {
        // YouTube API tracking
        if (window.YT) {
            window.onYouTubeIframeAPIReady = () => {
                document.querySelectorAll('iframe[src*="youtube.com"]').forEach(iframe => {
                    const player = new YT.Player(iframe, {
                        events: {
                            'onStateChange': (event) => {
                                const videoTitle = player.getVideoData()?.title || 'YouTube Video';
                                
                                switch(event.data) {
                                    case YT.PlayerState.PLAYING:
                                        this.trackEvent('video_start', {
                                            video_title: videoTitle,
                                            video_provider: 'youtube',
                                            page_path: window.location.pathname
                                        });
                                        break;
                                    case YT.PlayerState.PAUSED:
                                        this.trackEvent('video_pause', {
                                            video_title: videoTitle,
                                            video_provider: 'youtube',
                                            video_current_time: Math.round(player.getCurrentTime()),
                                            video_duration: Math.round(player.getDuration())
                                        });
                                        break;
                                    case YT.PlayerState.ENDED:
                                        this.trackEvent('video_complete', {
                                            video_title: videoTitle,
                                            video_provider: 'youtube',
                                            page_path: window.location.pathname
                                        });
                                        break;
                                }
                            }
                        }
                    });
                });
            };
        }
    }

    /**
     * Track scroll depth
     */
    setupScrollTracking() {
        let scrollMilestones = [25, 50, 75, 90];
        let milestoneTracked = {};
        let maxScroll = 0;

        const trackScrollDepth = () => {
            const scrollPercent = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
            maxScroll = Math.max(maxScroll, scrollPercent);

            scrollMilestones.forEach(milestone => {
                if (scrollPercent >= milestone && !milestoneTracked[milestone]) {
                    milestoneTracked[milestone] = true;
                    this.trackEvent('scroll_depth', {
                        scroll_depth: milestone,
                        page_path: window.location.pathname,
                        page_title: document.title
                    });
                }
            });
        };

        // Throttled scroll tracking
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(trackScrollDepth, 500);
        });

        // Track max scroll on page unload
        window.addEventListener('beforeunload', () => {
            if (maxScroll > 0) {
                this.trackEvent('page_scroll_complete', {
                    max_scroll_depth: maxScroll,
                    page_path: window.location.pathname,
                    page_title: document.title
                });
            }
        });
    }

    /**
     * Track navigation and link clicks
     */
    setupNavigationTracking() {
        document.addEventListener('click', (event) => {
            const link = event.target.closest('a');
            if (!link || !link.href) return;

            const linkText = link.textContent?.trim() || link.getAttribute('aria-label') || 'Unknown Link';
            const linkUrl = link.href;
            const isExternal = !linkUrl.includes(window.location.hostname);
            const linkType = this.inferLinkType(link);

            this.trackEvent('link_click', {
                link_text: linkText,
                link_url: linkUrl,
                link_type: linkType,
                is_external: isExternal,
                page_path: window.location.pathname
            });

            // Track external link clicks as outbound events
            if (isExternal) {
                this.trackEvent('click', {
                    link_url: linkUrl,
                    outbound: true
                });
            }
        });
    }

    /**
     * Track booking interactions (Calendly)
     */
    setupBookingTracking() {
        // Calendly widget events
        window.addEventListener('message', (event) => {
            if (event.origin !== 'https://calendly.com') return;

            const data = event.data;
            if (data.event && data.event.includes('calendly')) {
                switch(data.event) {
                    case 'calendly.event_scheduled':
                        this.trackBookingComplete(data.payload);
                        break;
                    case 'calendly.date_and_time_selected':
                        this.trackEvent('booking_step', {
                            step: 'time_selected',
                            booking_source: 'calendly',
                            page_path: window.location.pathname
                        });
                        break;
                    case 'calendly.profile_page_viewed':
                        this.trackEvent('booking_step', {
                            step: 'profile_viewed',
                            booking_source: 'calendly',
                            page_path: window.location.pathname
                        });
                        break;
                }
            }
        });

        // Track Calendly button clicks
        document.addEventListener('click', (event) => {
            const calendlyButton = event.target.closest('[href*="calendly.com"], [data-calendly-url]');
            if (calendlyButton) {
                this.trackEvent('booking_initiated', {
                    booking_source: 'calendly',
                    button_text: calendlyButton.textContent?.trim() || 'Calendly Button',
                    page_path: window.location.pathname
                });
            }
        });
    }

    /**
     * Track booking completion with enhanced ecommerce
     */
    trackBookingComplete(payload) {
        const eventData = payload?.event || {};
        const invitee = payload?.invitee || {};
        
        // Enhanced ecommerce purchase event
        this.trackEvent('purchase', {
            transaction_id: eventData.uuid || 'booking_' + Date.now(),
            currency: this.config.currency,
            value: this.getClassPrice(eventData.event_type_name),
            items: [{
                item_id: eventData.event_type_uuid || 'private_lesson',
                item_name: eventData.event_type_name || 'Private Dance Lesson',
                category: 'Dance Class',
                quantity: 1,
                price: this.getClassPrice(eventData.event_type_name)
            }]
        });

        // Custom booking event
        this.trackEvent('booking_complete', {
            class_type: eventData.event_type_name || 'Unknown',
            booking_date: eventData.start_time,
            booking_source: 'calendly',
            student_email: invitee.email,
            page_path: window.location.pathname
        });

        // Lead generation event
        this.trackEvent('generate_lead', {
            currency: this.config.currency,
            value: this.getClassPrice(eventData.event_type_name),
            lead_type: 'booking',
            class_type: eventData.event_type_name
        });

        this.log('Booking completed:', eventData);
    }

    /**
     * Track social media clicks
     */
    setupSocialTracking() {
        document.addEventListener('click', (event) => {
            const socialLink = event.target.closest('[href*="facebook.com"], [href*="instagram.com"], [href*="whatsapp.com"], [href*="youtube.com"], [href*="tiktok.com"]');
            if (socialLink) {
                const platform = this.getSocialPlatform(socialLink.href);
                
                this.trackEvent('social_click', {
                    social_platform: platform,
                    link_url: socialLink.href,
                    page_path: window.location.pathname
                });
            }
        });
    }

    /**
     * Track page views
     */
    trackPageView() {
        const pageData = {
            page_title: document.title,
            page_location: window.location.href,
            page_path: window.location.pathname,
            content_group1: this.getContentGroup(),
            send_to: this.config.measurementId
        };

        this.trackEvent('page_view', pageData);
        this.log('Page view tracked:', pageData);
    }

    /**
     * Track custom events
     */
    trackEvent(eventName, parameters = {}) {
        if (!this.consentGiven) {
            this.eventsQueue.push({ eventName, parameters });
            this.log(`Event queued (no consent): ${eventName}`, parameters);
            return;
        }

        if (!this.initialized) {
            this.eventsQueue.push({ eventName, parameters });
            this.log(`Event queued (not initialized): ${eventName}`, parameters);
            return;
        }

        try {
            // Ensure gtag is available
            if (typeof gtag === 'function') {
                gtag('event', eventName, {
                    ...parameters,
                    custom_parameter_1: parameters.dance_class_type || '',
                    custom_parameter_2: parameters.instructor_name || '',
                    custom_parameter_3: parameters.booking_source || '',
                    send_to: this.config.measurementId
                });

                this.log(`Event tracked: ${eventName}`, parameters);

                // Send to performance analytics if available
                if (window.performanceAnalytics) {
                    window.performanceAnalytics.addCustomEvent('ga4_event', {
                        event_name: eventName,
                        ...parameters
                    });
                }
            } else {
                this.log('gtag not available, queuing event');
                this.eventsQueue.push({ eventName, parameters });
            }
        } catch (error) {
            this.log('Error tracking event:', error);
        }
    }

    /**
     * Process queued events after initialization
     */
    processQueuedEvents() {
        this.log(`Processing ${this.eventsQueue.length} queued events`);
        
        this.eventsQueue.forEach(({ eventName, parameters }) => {
            this.trackEvent(eventName, parameters);
        });
        
        this.eventsQueue = [];
    }

    /**
     * Get class price for ecommerce tracking
     */
    getClassPrice(classType) {
        const prices = {
            'Private Lesson': 80,
            'SCF Choreo Team': 20,
            'Pasos Básicos': 20,
            'Casino Royale': 20,
            'Workshop': 30,
            'Drop-in Class': 20
        };

        return prices[classType] || 20; // Default to drop-in price
    }

    /**
     * Utility methods
     */
    getElementLocation(element) {
        // Determine location context of element
        const section = element.closest('section, header, footer, nav, main');
        if (section) {
            return section.id || section.className.split(' ')[0] || 'unknown_section';
        }
        return 'body';
    }

    inferCTAType(text) {
        const lowercaseText = text.toLowerCase();
        if (lowercaseText.includes('book') || lowercaseText.includes('schedule')) return 'booking';
        if (lowercaseText.includes('contact') || lowercaseText.includes('call')) return 'contact';
        if (lowercaseText.includes('learn') || lowercaseText.includes('more')) return 'information';
        if (lowercaseText.includes('join') || lowercaseText.includes('register')) return 'registration';
        if (lowercaseText.includes('follow') || lowercaseText.includes('social')) return 'social';
        return 'general';
    }

    inferFormType(form) {
        const formClasses = form.className.toLowerCase();
        const formId = form.id.toLowerCase();
        
        if (formClasses.includes('testimonial') || formId.includes('testimonial')) return 'testimonial';
        if (formClasses.includes('contact') || formId.includes('contact')) return 'contact';
        if (formClasses.includes('newsletter') || formId.includes('newsletter')) return 'newsletter';
        if (formClasses.includes('booking') || formId.includes('booking')) return 'booking';
        
        return 'general';
    }

    inferLinkType(link) {
        const href = link.href.toLowerCase();
        const text = link.textContent?.toLowerCase() || '';
        
        if (href.includes('tel:')) return 'phone';
        if (href.includes('mailto:')) return 'email';
        if (href.includes('calendly.com')) return 'booking';
        if (href.includes('facebook.com') || href.includes('instagram.com') || 
            href.includes('whatsapp.com') || href.includes('youtube.com')) return 'social';
        if (text.includes('download') || href.includes('.pdf')) return 'download';
        
        return 'navigation';
    }

    getSocialPlatform(url) {
        if (url.includes('facebook.com')) return 'facebook';
        if (url.includes('instagram.com')) return 'instagram';
        if (url.includes('whatsapp.com')) return 'whatsapp';
        if (url.includes('youtube.com')) return 'youtube';
        if (url.includes('tiktok.com')) return 'tiktok';
        return 'unknown';
    }

    getContentGroup() {
        const path = window.location.pathname;
        if (path.includes('/classes') || path.includes('/schedule')) return 'Classes';
        if (path.includes('/events')) return 'Events';
        if (path.includes('/instructors')) return 'Instructors';
        if (path.includes('/gallery')) return 'Gallery';
        if (path.includes('/pricing')) return 'Pricing';
        if (path.includes('/testimonials')) return 'Testimonials';
        if (path.includes('/contact')) return 'Contact';
        if (path.includes('/private')) return 'Private Lessons';
        if (path === '/') return 'Home';
        return 'Other';
    }

    /**
     * Debug logging
     */
    log(...args) {
        if (this.config.debugMode) {
            console.log('[Sabor Analytics]', ...args);
        }
    }

    /**
     * Public API methods
     */
    
    // Track custom conversion
    trackConversion(conversionType, value = 0, currency = 'USD') {
        this.trackEvent('conversion', {
            conversion_type: conversionType,
            currency: currency,
            value: value
        });
    }

    // Track class interest
    trackClassInterest(classType, action = 'view') {
        this.trackEvent('class_interest', {
            class_type: classType,
            action: action,
            page_path: window.location.pathname
        });
    }

    // Track user engagement
    trackEngagement(engagementType, details = {}) {
        this.trackEvent('user_engagement', {
            engagement_type: engagementType,
            ...details,
            timestamp: Date.now()
        });
    }

    // Get consent status
    getConsentStatus() {
        return {
            given: this.consentGiven,
            initialized: this.initialized,
            hasChoice: this.hasConsentChoice()
        };
    }

    // Revoke consent
    revokeConsent() {
        this.consentGiven = false;
        this.initialized = false;
        
        try {
            localStorage.removeItem(this.config.consentKey);
        } catch (error) {
            this.log('Error removing consent:', error);
        }
        
        this.log('Consent revoked');
    }
}

// Initialize analytics when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.saborAnalytics = new SaborAnalytics();
});

// Export for external use
window.SaborAnalytics = SaborAnalytics;