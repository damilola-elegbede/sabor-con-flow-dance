/**
 * Progressive Web App Features
 * Enhanced PWA functionality including push notifications, shortcuts, and sharing
 */

class PWAFeatures {
    constructor() {
        this.isStandalone = window.matchMedia('(display-mode: standalone)').matches;
        this.hasNotificationPermission = false;
        this.pushSubscription = null;
        
        this.init();
    }

    async init() {
        // Check if running as PWA
        this.detectPWAMode();
        
        // Set up push notifications
        await this.initializePushNotifications();
        
        // Set up web share API
        this.initializeWebShare();
        
        // Set up keyboard shortcuts
        this.initializeKeyboardShortcuts();
        
        // Set up app shortcuts
        this.initializeAppShortcuts();
        
        // Monitor app usage
        this.initializeUsageTracking();
        
        // Set up periodic background sync
        this.initializePeriodicSync();
    }

    detectPWAMode() {
        const isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
                           window.navigator.standalone ||
                           document.referrer.includes('android-app://');
        
        if (isStandalone) {
            document.body.classList.add('pwa-standalone');
            console.log('[PWA] Running in standalone mode');
            
            // Track PWA usage
            if (window.gtag) {
                gtag('event', 'pwa_launched', {
                    event_category: 'PWA',
                    value: 1
                });
            }
        }
    }

    async initializePushNotifications() {
        if (!('Notification' in window) || !('serviceWorker' in navigator)) {
            console.log('[PWA] Push notifications not supported');
            return;
        }

        // Check current permission
        this.hasNotificationPermission = Notification.permission === 'granted';
        
        // Set up notification handlers
        this.setupNotificationHandlers();
        
        // Register for push if permission already granted
        if (this.hasNotificationPermission) {
            await this.registerForPush();
        }
    }

    async requestNotificationPermission() {
        if (!('Notification' in window)) {
            return false;
        }

        try {
            const permission = await Notification.requestPermission();
            this.hasNotificationPermission = permission === 'granted';
            
            if (this.hasNotificationPermission) {
                await this.registerForPush();
                this.showPermissionGrantedMessage();
            } else {
                this.showPermissionDeniedMessage();
            }
            
            return this.hasNotificationPermission;
        } catch (error) {
            console.error('[PWA] Error requesting notification permission:', error);
            return false;
        }
    }

    async registerForPush() {
        if (!window.swManager?.swRegistration) {
            console.log('[PWA] Service worker not available for push');
            return;
        }

        try {
            // Check if already subscribed
            this.pushSubscription = await window.swManager.swRegistration.pushManager.getSubscription();
            
            if (!this.pushSubscription) {
                // Generate VAPID key (in production, this should come from server)
                const vapidPublicKey = 'your-vapid-public-key-here';
                
                this.pushSubscription = await window.swManager.swRegistration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: this.urlBase64ToUint8Array(vapidPublicKey)
                });
                
                // Send subscription to server
                await this.sendSubscriptionToServer(this.pushSubscription);
            }
            
            console.log('[PWA] Push subscription active');
        } catch (error) {
            console.error('[PWA] Failed to register for push:', error);
        }
    }

    setupNotificationHandlers() {
        // Handle notification clicks
        navigator.serviceWorker.addEventListener('message', event => {
            if (event.data.type === 'NOTIFICATION_CLICK') {
                const data = event.data.data;
                this.handleNotificationClick(data);
            }
        });
    }

    handleNotificationClick(data) {
        // Navigate to relevant page based on notification data
        const routes = {
            'new_class': '/schedule/',
            'event_reminder': '/events/',
            'pricing_update': '/pricing/',
            'general': '/'
        };
        
        const route = routes[data.category] || '/';
        window.location.href = route;
        
        // Track notification interaction
        if (window.gtag) {
            gtag('event', 'notification_click', {
                event_category: 'PWA',
                event_label: data.category,
                value: 1
            });
        }
    }

    initializeWebShare() {
        if (!navigator.share) {
            console.log('[PWA] Web Share API not supported');
            return;
        }

        // Add share buttons where needed
        const shareButtons = document.querySelectorAll('[data-share]');
        shareButtons.forEach(button => {
            button.addEventListener('click', () => this.shareContent(button));
        });
    }

    async shareContent(element) {
        const title = element.dataset.shareTitle || document.title;
        const text = element.dataset.shareText || 'Check out Sabor Con Flow Dance!';
        const url = element.dataset.shareUrl || window.location.href;

        try {
            if (navigator.canShare && navigator.canShare({ title, text, url })) {
                await navigator.share({ title, text, url });
                
                // Track share
                if (window.gtag) {
                    gtag('event', 'share', {
                        method: 'web_share_api',
                        content_type: 'page',
                        item_id: url
                    });
                }
            }
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('[PWA] Error sharing content:', error);
                this.fallbackShare(title, url);
            }
        }
    }

    fallbackShare(title, url) {
        // Fallback to clipboard copy
        if (navigator.clipboard) {
            navigator.clipboard.writeText(url).then(() => {
                this.showShareSuccessMessage();
            });
        } else {
            // Create temporary input for copying
            const input = document.createElement('input');
            input.value = url;
            document.body.appendChild(input);
            input.select();
            document.execCommand('copy');
            document.body.removeChild(input);
            this.showShareSuccessMessage();
        }
    }

    initializeKeyboardShortcuts() {
        document.addEventListener('keydown', (event) => {
            // Only handle shortcuts with Ctrl/Cmd
            if (!(event.ctrlKey || event.metaKey)) return;
            
            const shortcuts = {
                'h': () => window.location.href = '/',
                's': () => window.location.href = '/schedule/',
                'p': () => window.location.href = '/pricing/',
                'c': () => window.location.href = '/contact/',
                'g': () => window.location.href = '/gallery/'
            };
            
            const action = shortcuts[event.key.toLowerCase()];
            if (action) {
                event.preventDefault();
                action();
                
                // Track shortcut usage
                if (window.gtag) {
                    gtag('event', 'keyboard_shortcut', {
                        event_category: 'PWA',
                        event_label: event.key.toLowerCase(),
                        value: 1
                    });
                }
            }
        });
    }

    initializeAppShortcuts() {
        // Handle app shortcut navigation
        const urlParams = new URLSearchParams(window.location.search);
        const shortcut = urlParams.get('shortcut');
        
        if (shortcut) {
            // Track shortcut usage
            if (window.gtag) {
                gtag('event', 'app_shortcut', {
                    event_category: 'PWA',
                    event_label: shortcut,
                    value: 1
                });
            }
        }
    }

    initializeUsageTracking() {
        // Track how long user spends in app
        let startTime = Date.now();
        let isVisible = !document.hidden;
        
        const trackSession = () => {
            if (isVisible) {
                const duration = Date.now() - startTime;
                
                // Track session duration
                if (window.gtag && duration > 30000) { // Only track if > 30 seconds
                    gtag('event', 'pwa_session_duration', {
                        event_category: 'PWA',
                        value: Math.round(duration / 1000) // in seconds
                    });
                }
            }
        };
        
        // Track visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                trackSession();
                isVisible = false;
            } else {
                startTime = Date.now();
                isVisible = true;
            }
        });
        
        // Track on page unload
        window.addEventListener('beforeunload', trackSession);
        
        // Track page views in PWA mode
        if (this.isStandalone && window.gtag) {
            gtag('event', 'page_view', {
                event_category: 'PWA',
                page_title: document.title,
                page_location: window.location.href
            });
        }
    }

    async initializePeriodicSync() {
        if (!window.swManager?.swRegistration || !('periodicSync' in window.ServiceWorkerRegistration.prototype)) {
            console.log('[PWA] Periodic Background Sync not supported');
            return;
        }

        try {
            // Request permission for periodic sync
            const status = await navigator.permissions.query({ name: 'periodic-background-sync' });
            
            if (status.state === 'granted') {
                // Register periodic sync for content updates
                await window.swManager.swRegistration.periodicSync.register('content-sync', {
                    minInterval: 24 * 60 * 60 * 1000 // 24 hours
                });
                
                console.log('[PWA] Periodic sync registered');
            }
        } catch (error) {
            console.error('[PWA] Periodic sync registration failed:', error);
        }
    }

    // =====================================
    // NOTIFICATION TEMPLATES
    // =====================================

    async sendClassReminderNotification(classInfo) {
        if (!this.hasNotificationPermission) return;

        const options = {
            body: `${classInfo.name} starts in 1 hour at ${classInfo.location}`,
            icon: '/static/images/favicon/favicon.png',
            badge: '/static/images/favicon/favicon_small.png',
            tag: 'class-reminder',
            renotify: true,
            vibrate: [200, 100, 200],
            data: {
                type: 'class_reminder',
                classId: classInfo.id,
                url: '/schedule/'
            },
            actions: [
                {
                    action: 'view',
                    title: 'View Schedule',
                    icon: '/static/images/favicon/favicon_small.png'
                },
                {
                    action: 'dismiss',
                    title: 'Dismiss',
                    icon: '/static/images/favicon/favicon_small.png'
                }
            ]
        };

        if ('serviceWorker' in navigator && window.swManager?.swRegistration) {
            // Send via service worker for better reliability
            window.swManager.swRegistration.active?.postMessage({
                type: 'SHOW_NOTIFICATION',
                title: 'Class Reminder',
                options: options
            });
        } else {
            // Fallback to direct notification
            new Notification('Class Reminder', options);
        }
    }

    async sendEventNotification(eventInfo) {
        if (!this.hasNotificationPermission) return;

        const options = {
            body: `New event: ${eventInfo.title} on ${eventInfo.date}`,
            icon: '/static/images/favicon/favicon.png',
            badge: '/static/images/favicon/favicon_small.png',
            tag: 'new-event',
            data: {
                type: 'new_event',
                eventId: eventInfo.id,
                url: '/events/'
            }
        };

        new Notification('New Event', options);
    }

    // =====================================
    // USER INTERFACE
    // =====================================

    showNotificationPermissionPrompt() {
        const prompt = document.createElement('div');
        prompt.className = 'pwa-notification-prompt';
        prompt.innerHTML = `
            <div class="pwa-prompt-content">
                <div class="pwa-prompt-header">
                    <i class="fas fa-bell"></i>
                    <h3>Enable Notifications</h3>
                </div>
                <p>Get notified about upcoming classes, events, and important updates.</p>
                <div class="pwa-prompt-actions">
                    <button class="btn btn-primary" onclick="pwaFeatures.requestNotificationPermission(); this.closest('.pwa-notification-prompt').remove();">
                        Enable Notifications
                    </button>
                    <button class="btn btn-secondary" onclick="this.closest('.pwa-notification-prompt').remove();">
                        Maybe Later
                    </button>
                </div>
            </div>
        `;

        prompt.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            right: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            animation: slideInUp 0.3s ease-out;
            max-width: 400px;
            margin: 0 auto;
        `;

        document.body.appendChild(prompt);

        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (prompt.parentNode) {
                prompt.remove();
            }
        }, 10000);
    }

    showPermissionGrantedMessage() {
        this.showToast('Notifications enabled! You\'ll receive updates about classes and events.', 'success');
    }

    showPermissionDeniedMessage() {
        this.showToast('Notifications disabled. You can enable them later in your browser settings.', 'info');
    }

    showShareSuccessMessage() {
        this.showToast('Link copied to clipboard!', 'success');
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `pwa-toast pwa-toast-${type}`;
        toast.textContent = message;
        
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10B981' : '#3B82F6'};
            color: white;
            padding: 12px 20px;
            border-radius: 4px;
            z-index: 10001;
            animation: slideInRight 0.3s ease-out;
            max-width: 300px;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // =====================================
    // UTILITY FUNCTIONS
    // =====================================

    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    async sendSubscriptionToServer(subscription) {
        try {
            const response = await fetch('/api/push-subscription/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value
                },
                body: JSON.stringify({
                    subscription: subscription,
                    user_agent: navigator.userAgent
                })
            });

            if (response.ok) {
                console.log('[PWA] Push subscription sent to server');
            } else {
                console.error('[PWA] Failed to send subscription to server');
            }
        } catch (error) {
            console.error('[PWA] Error sending subscription to server:', error);
        }
    }

    // =====================================
    // PUBLIC API
    // =====================================

    async enableNotifications() {
        return await this.requestNotificationPermission();
    }

    async disableNotifications() {
        if (this.pushSubscription) {
            await this.pushSubscription.unsubscribe();
            this.pushSubscription = null;
            this.hasNotificationPermission = false;
            console.log('[PWA] Push subscription disabled');
        }
    }

    getNotificationStatus() {
        return {
            supported: 'Notification' in window,
            permission: Notification.permission,
            hasSubscription: !!this.pushSubscription
        };
    }

    isRunningAsApp() {
        return this.isStandalone;
    }

    canShare() {
        return !!navigator.share;
    }

    // Auto-prompt for notifications after some interaction
    scheduleNotificationPrompt() {
        // Wait for user interaction before prompting
        let interactionCount = 0;
        const checkInteraction = () => {
            interactionCount++;
            if (interactionCount >= 3 && !this.hasNotificationPermission && Notification.permission === 'default') {
                this.showNotificationPermissionPrompt();
                document.removeEventListener('click', checkInteraction);
            }
        };

        document.addEventListener('click', checkInteraction);
    }
}

// Add required styles
const pwaStyles = document.createElement('style');
pwaStyles.textContent = `
    @keyframes slideInUp {
        from { transform: translateY(100%); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .pwa-prompt-content {
        padding: 20px;
    }
    
    .pwa-prompt-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
    }
    
    .pwa-prompt-header i {
        color: #C7B375;
        font-size: 1.2rem;
    }
    
    .pwa-prompt-header h3 {
        margin: 0;
        color: #333;
    }
    
    .pwa-prompt-actions {
        display: flex;
        gap: 10px;
        margin-top: 16px;
    }
    
    .pwa-prompt-actions .btn {
        flex: 1;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 500;
    }
    
    /* PWA standalone mode adjustments */
    .pwa-standalone .navbar {
        padding-top: env(safe-area-inset-top);
    }
    
    .pwa-standalone .footer {
        padding-bottom: env(safe-area-inset-bottom);
    }
`;

document.head.appendChild(pwaStyles);

// Initialize PWA Features
let pwaFeatures;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        pwaFeatures = new PWAFeatures();
    });
} else {
    pwaFeatures = new PWAFeatures();
}

// Export for global access
window.pwaFeatures = pwaFeatures;