/**
 * Social Links Component JavaScript
 * SPEC_05 Group A Task 4 - Social Media Integration
 * 
 * Handles enhanced interactions, analytics tracking, and accessibility
 * for the social media links component.
 */

(function() {
    'use strict';

    /**
     * Social Links Manager
     */
    class SocialLinksManager {
        constructor() {
            this.socialLinks = document.querySelectorAll('.social-links__item');
            this.container = document.querySelector('.social-links');
            this.analytics = window.gtag || window.ga || null;
            
            this.init();
        }

        /**
         * Initialize the social links functionality
         */
        init() {
            if (!this.socialLinks.length) return;

            this.bindEvents();
            this.setupKeyboardNavigation();
            this.preloadSocialPages();
            this.trackSocialInteractions();
        }

        /**
         * Bind event listeners
         */
        bindEvents() {
            this.socialLinks.forEach(link => {
                // Enhanced click tracking
                link.addEventListener('click', (e) => {
                    this.handleSocialClick(e, link);
                });

                // Keyboard support
                link.addEventListener('keydown', (e) => {
                    this.handleKeydown(e, link);
                });

                // Focus management
                link.addEventListener('focus', () => {
                    this.handleFocus(link);
                });

                link.addEventListener('blur', () => {
                    this.handleBlur(link);
                });

                // Touch support for mobile
                link.addEventListener('touchstart', (e) => {
                    this.handleTouchStart(e, link);
                }, { passive: true });
            });
        }

        /**
         * Handle social media link clicks
         */
        handleSocialClick(event, link) {
            const platform = link.dataset.platform;
            const url = link.href;

            // Track analytics
            this.trackSocialEngagement(platform, 'click', url);

            // Add click feedback
            this.addClickFeedback(link);

            // Handle email links differently
            if (platform === 'email') {
                event.preventDefault();
                this.handleEmailClick(url);
            }
        }

        /**
         * Handle keyboard navigation
         */
        handleKeydown(event, link) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                link.click();
            }
        }

        /**
         * Setup keyboard navigation between social links
         */
        setupKeyboardNavigation() {
            this.socialLinks.forEach((link, index) => {
                link.addEventListener('keydown', (e) => {
                    let targetIndex;
                    
                    switch(e.key) {
                        case 'ArrowRight':
                        case 'ArrowDown':
                            e.preventDefault();
                            targetIndex = (index + 1) % this.socialLinks.length;
                            this.socialLinks[targetIndex].focus();
                            break;
                        case 'ArrowLeft':
                        case 'ArrowUp':
                            e.preventDefault();
                            targetIndex = index === 0 ? this.socialLinks.length - 1 : index - 1;
                            this.socialLinks[targetIndex].focus();
                            break;
                        case 'Home':
                            e.preventDefault();
                            this.socialLinks[0].focus();
                            break;
                        case 'End':
                            e.preventDefault();
                            this.socialLinks[this.socialLinks.length - 1].focus();
                            break;
                    }
                });
            });
        }

        /**
         * Handle focus events
         */
        handleFocus(link) {
            link.setAttribute('aria-expanded', 'true');
            
            // Announce platform to screen readers
            const platform = link.dataset.platform;
            this.announceToScreenReader(`${platform} social media link focused`);
        }

        /**
         * Handle blur events
         */
        handleBlur(link) {
            link.setAttribute('aria-expanded', 'false');
        }

        /**
         * Handle touch events for mobile
         */
        handleTouchStart(event, link) {
            // Add touch feedback
            link.classList.add('social-links__item--touched');
            
            setTimeout(() => {
                link.classList.remove('social-links__item--touched');
            }, 200);
        }

        /**
         * Handle email link clicks
         */
        handleEmailClick(url) {
            // Try to open email client
            window.location.href = url;
            
            // Fallback: show copy to clipboard option
            setTimeout(() => {
                if (document.hasFocus()) {
                    this.showEmailFallback();
                }
            }, 500);
        }

        /**
         * Show email fallback when email client is not available
         */
        showEmailFallback() {
            const email = 'info@saborconflow.com';
            
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(email).then(() => {
                    this.showNotification('Email address copied to clipboard!');
                });
            } else {
                // Fallback for older browsers
                this.showNotification(`Email: ${email}`);
            }
        }

        /**
         * Add visual click feedback
         */
        addClickFeedback(link) {
            link.classList.add('social-links__item--clicked');
            
            setTimeout(() => {
                link.classList.remove('social-links__item--clicked');
            }, 150);
        }

        /**
         * Track social media engagement
         */
        trackSocialEngagement(platform, action, url) {
            // Google Analytics 4
            if (this.analytics && window.ENABLE_ANALYTICS) {
                this.analytics('event', 'social_engagement', {
                    social_network: platform,
                    social_action: action,
                    social_target: url,
                    custom_parameter_1: 'social_links_component'
                });
            }

            // Custom analytics
            if (window.performanceAnalytics) {
                window.performanceAnalytics.addCustomEvent('social_click', {
                    platform: platform,
                    action: action,
                    url: url,
                    timestamp: Date.now(),
                    user_agent: navigator.userAgent,
                    viewport: {
                        width: window.innerWidth,
                        height: window.innerHeight
                    }
                });
            }

            // Console logging for debug mode
            if (window.GA4_DEBUG_MODE) {
                console.log('Social engagement tracked:', {
                    platform: platform,
                    action: action,
                    url: url
                });
            }
        }

        /**
         * Preload social media pages for faster navigation
         */
        preloadSocialPages() {
            // Only preload on desktop and good connections
            if (window.innerWidth > 1024 && navigator.connection) {
                const connection = navigator.connection;
                if (connection.effectiveType === '4g' && !connection.saveData) {
                    this.socialLinks.forEach(link => {
                        const platform = link.dataset.platform;
                        if (platform !== 'email') {
                            const preloadLink = document.createElement('link');
                            preloadLink.rel = 'prefetch';
                            preloadLink.href = link.href;
                            document.head.appendChild(preloadLink);
                        }
                    });
                }
            }
        }

        /**
         * Track social interactions for analytics
         */
        trackSocialInteractions() {
            // Track hover events (desktop only)
            if (window.innerWidth > 1024) {
                this.socialLinks.forEach(link => {
                    link.addEventListener('mouseenter', () => {
                        const platform = link.dataset.platform;
                        this.trackSocialEngagement(platform, 'hover', link.href);
                    });
                });
            }

            // Track visibility when scrolled into view
            if ('IntersectionObserver' in window) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            this.trackSocialEngagement('component', 'view', 'social_links_visible');
                            observer.unobserve(entry.target);
                        }
                    });
                }, { threshold: 0.5 });

                if (this.container) {
                    observer.observe(this.container);
                }
            }
        }

        /**
         * Announce messages to screen readers
         */
        announceToScreenReader(message) {
            const announcement = document.createElement('div');
            announcement.setAttribute('aria-live', 'polite');
            announcement.setAttribute('aria-atomic', 'true');
            announcement.className = 'sr-only';
            announcement.textContent = message;
            
            document.body.appendChild(announcement);
            
            setTimeout(() => {
                document.body.removeChild(announcement);
            }, 1000);
        }

        /**
         * Show user notification
         */
        showNotification(message) {
            // Check if notification system exists
            if (window.showNotification) {
                window.showNotification(message, 'success');
                return;
            }

            // Fallback notification
            const notification = document.createElement('div');
            notification.className = 'social-links-notification';
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--color-gold, #C7B375);
                color: var(--color-black, #000000);
                padding: 12px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 10000;
                font-family: var(--font-body, sans-serif);
                font-size: 14px;
                font-weight: 500;
                transition: all 0.3s ease;
                transform: translateX(100%);
            `;

            document.body.appendChild(notification);

            // Animate in
            requestAnimationFrame(() => {
                notification.style.transform = 'translateX(0)';
            });

            // Remove after delay
            setTimeout(() => {
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        document.body.removeChild(notification);
                    }
                }, 300);
            }, 3000);
        }
    }

    /**
     * Initialize when DOM is ready
     */
    function initSocialLinks() {
        if (document.querySelector('.social-links')) {
            new SocialLinksManager();
        }
    }

    // Initialize immediately if DOM is already loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSocialLinks);
    } else {
        initSocialLinks();
    }

    // Export for potential external use
    window.SocialLinksManager = SocialLinksManager;

})();