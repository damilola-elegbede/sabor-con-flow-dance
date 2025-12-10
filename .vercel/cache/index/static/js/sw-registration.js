/**
 * Service Worker Registration and Management
 * Handles SW lifecycle, updates, and communication
 */

class ServiceWorkerManager {
    constructor() {
        this.swRegistration = null;
        this.isUpdateAvailable = false;
        this.deferredPrompt = null;
        this.isInstallable = false;
        
        this.init();
    }

    async init() {
        if ('serviceWorker' in navigator) {
            try {
                await this.registerServiceWorker();
                this.setupInstallPrompt();
                this.setupUpdateChecking();
                this.setupBackgroundSync();
                this.monitorNetworkStatus();
            } catch (error) {
                console.error('Service Worker initialization failed:', error);
            }
        } else {
            console.log('Service Worker not supported in this browser');
            this.showFallbackMessage();
        }
    }

    async registerServiceWorker() {
        try {
            console.log('Registering Service Worker...');
            
            this.swRegistration = await navigator.serviceWorker.register('/static/js/service-worker.js', {
                scope: '/',
                updateViaCache: 'none'
            });

            console.log('Service Worker registered successfully:', this.swRegistration);

            // Set up event listeners
            this.swRegistration.addEventListener('updatefound', () => {
                console.log('Service Worker update found');
                this.handleUpdateFound();
            });

            // Check for updates on page load
            if (this.swRegistration.waiting) {
                this.handleWaitingServiceWorker();
            }

            // Listen for messages from service worker
            navigator.serviceWorker.addEventListener('message', event => {
                this.handleServiceWorkerMessage(event);
            });

            // Check for updates periodically
            this.scheduleUpdateChecks();

        } catch (error) {
            console.error('Service Worker registration failed:', error);
            throw error;
        }
    }

    handleUpdateFound() {
        const newWorker = this.swRegistration.installing;
        
        newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed') {
                if (navigator.serviceWorker.controller) {
                    // New update available
                    this.isUpdateAvailable = true;
                    this.showUpdateNotification();
                } else {
                    // First install
                    console.log('Service Worker installed for the first time');
                    this.showInstallNotification();
                }
            }
        });
    }

    handleWaitingServiceWorker() {
        this.isUpdateAvailable = true;
        this.showUpdateNotification();
    }

    handleServiceWorkerMessage(event) {
        const { type, data } = event.data;
        
        switch (type) {
            case 'SW_UPDATED':
                console.log('Service Worker updated to version:', data.version);
                break;
            case 'CACHE_UPDATED':
                console.log('Cache updated:', data);
                break;
            case 'SYNC_COMPLETE':
                console.log('Background sync completed:', data);
                this.showSyncCompleteNotification(data);
                break;
            case 'OFFLINE_READY':
                this.showOfflineReadyNotification();
                break;
            default:
                console.log('Unknown message from SW:', type, data);
        }
    }

    async activateUpdate() {
        if (!this.swRegistration?.waiting) {
            return;
        }

        // Tell the waiting service worker to become active
        this.swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
        
        // Reload the page to ensure new SW takes control
        window.location.reload();
    }

    scheduleUpdateChecks() {
        // Check for updates every 30 minutes
        setInterval(() => {
            if (this.swRegistration) {
                this.swRegistration.update();
            }
        }, 30 * 60 * 1000);

        // Check for updates when page becomes visible
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.swRegistration) {
                this.swRegistration.update();
            }
        });
    }

    // =====================================
    // PWA INSTALL PROMPT
    // =====================================

    setupInstallPrompt() {
        window.addEventListener('beforeinstallprompt', event => {
            console.log('PWA install prompt available');
            event.preventDefault();
            this.deferredPrompt = event;
            this.isInstallable = true;
            this.showInstallButton();
        });

        window.addEventListener('appinstalled', () => {
            console.log('PWA was installed');
            this.deferredPrompt = null;
            this.isInstallable = false;
            this.hideInstallButton();
            this.trackInstallEvent();
        });
    }

    async promptInstall() {
        if (!this.deferredPrompt) {
            return false;
        }

        try {
            this.deferredPrompt.prompt();
            const { outcome } = await this.deferredPrompt.userChoice;
            
            console.log('Install prompt outcome:', outcome);
            
            if (outcome === 'accepted') {
                this.trackInstallEvent('accepted');
            } else {
                this.trackInstallEvent('dismissed');
            }
            
            this.deferredPrompt = null;
            return outcome === 'accepted';
        } catch (error) {
            console.error('Install prompt failed:', error);
            return false;
        }
    }

    // =====================================
    // BACKGROUND SYNC
    // =====================================

    setupBackgroundSync() {
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            console.log('Background Sync is supported');
            
            // Listen for form submissions to queue for sync
            this.setupFormSyncHandlers();
        } else {
            console.log('Background Sync not supported');
        }
    }

    setupFormSyncHandlers() {
        // Contact form sync
        const contactForms = document.querySelectorAll('form[data-sync="contact"]');
        contactForms.forEach(form => {
            form.addEventListener('submit', event => {
                if (!navigator.onLine) {
                    event.preventDefault();
                    this.queueFormForSync(form, 'contact-form-submission');
                }
            });
        });

        // Newsletter signup sync
        const newsletterForms = document.querySelectorAll('form[data-sync="newsletter"]');
        newsletterForms.forEach(form => {
            form.addEventListener('submit', event => {
                if (!navigator.onLine) {
                    event.preventDefault();
                    this.queueFormForSync(form, 'newsletter-signup');
                }
            });
        });
    }

    async queueFormForSync(form, syncTag) {
        try {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            // Add CSRF token if available
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            if (csrfToken) {
                data.csrfToken = csrfToken;
            }

            // Send to service worker for queuing
            if (this.swRegistration?.active) {
                this.swRegistration.active.postMessage({
                    type: 'QUEUE_SYNC',
                    data: { tag: syncTag, payload: data }
                });
            }

            this.showOfflineSubmissionNotification();
        } catch (error) {
            console.error('Failed to queue form for sync:', error);
        }
    }

    // =====================================
    // NETWORK STATUS MONITORING
    // =====================================

    monitorNetworkStatus() {
        const updateNetworkStatus = () => {
            const isOnline = navigator.onLine;
            document.body.classList.toggle('offline', !isOnline);
            document.body.classList.toggle('online', isOnline);
            
            if (isOnline) {
                this.hideOfflineNotification();
                this.triggerSync();
            } else {
                this.showOfflineNotification();
            }
        };

        window.addEventListener('online', updateNetworkStatus);
        window.addEventListener('offline', updateNetworkStatus);
        
        // Initial status
        updateNetworkStatus();

        // Monitor connection quality
        if ('connection' in navigator) {
            const connection = navigator.connection;
            
            const updateConnectionInfo = () => {
                document.body.className = document.body.className.replace(/\bconnection-\w+/g, '');
                document.body.classList.add(`connection-${connection.effectiveType}`);
                
                // Add data saver class
                if (connection.saveData) {
                    document.body.classList.add('save-data');
                }
            };

            connection.addEventListener('change', updateConnectionInfo);
            updateConnectionInfo();
        }
    }

    triggerSync() {
        if (this.swRegistration?.sync) {
            // Trigger all sync types
            const syncTags = ['contact-form-submission', 'newsletter-signup', 'analytics-data'];
            syncTags.forEach(tag => {
                this.swRegistration.sync.register(tag).catch(console.error);
            });
        }
    }

    // =====================================
    // USER NOTIFICATIONS
    // =====================================

    showUpdateNotification() {
        this.showNotification({
            id: 'sw-update',
            title: 'App Update Available',
            message: 'A new version of the app is available. Reload to update?',
            actions: [
                {
                    text: 'Update Now',
                    action: () => this.activateUpdate(),
                    primary: true
                },
                {
                    text: 'Later',
                    action: () => this.hideNotification('sw-update')
                }
            ],
            persistent: true
        });
    }

    showInstallNotification() {
        this.showNotification({
            id: 'sw-install',
            title: 'App Ready',
            message: 'Sabor Con Flow Dance is ready to work offline!',
            duration: 5000
        });
    }

    showInstallButton() {
        let installButton = document.getElementById('pwa-install-btn');
        
        if (!installButton) {
            installButton = document.createElement('button');
            installButton.id = 'pwa-install-btn';
            installButton.className = 'btn btn-primary install-btn';
            installButton.innerHTML = '<i class="fas fa-download"></i> Install App';
            installButton.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 1000;
                border-radius: 25px;
                padding: 12px 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                animation: slideInUp 0.3s ease-out;
            `;
            
            installButton.addEventListener('click', () => this.promptInstall());
            document.body.appendChild(installButton);
        }
        
        installButton.style.display = 'block';
    }

    hideInstallButton() {
        const installButton = document.getElementById('pwa-install-btn');
        if (installButton) {
            installButton.style.display = 'none';
        }
    }

    showOfflineNotification() {
        this.showNotification({
            id: 'offline',
            title: 'You\'re Offline',
            message: 'Some features may be limited while offline.',
            type: 'warning',
            persistent: true
        });
    }

    hideOfflineNotification() {
        this.hideNotification('offline');
    }

    showOfflineSubmissionNotification() {
        this.showNotification({
            id: 'offline-submit',
            title: 'Queued for Later',
            message: 'Your submission will be sent when you\'re back online.',
            type: 'info',
            duration: 4000
        });
    }

    showSyncCompleteNotification(data) {
        this.showNotification({
            id: 'sync-complete',
            title: 'Sync Complete',
            message: `Your ${data.type} has been submitted successfully.`,
            type: 'success',
            duration: 3000
        });
    }

    showOfflineReadyNotification() {
        this.showNotification({
            id: 'offline-ready',
            title: 'Ready for Offline',
            message: 'The app is now ready to work offline!',
            type: 'success',
            duration: 3000
        });
    }

    showFallbackMessage() {
        this.showNotification({
            id: 'no-sw',
            title: 'Limited Offline Support',
            message: 'Your browser doesn\'t support advanced offline features.',
            type: 'info',
            duration: 5000
        });
    }

    // =====================================
    // NOTIFICATION SYSTEM
    // =====================================

    showNotification(options) {
        const {
            id,
            title,
            message,
            type = 'info',
            actions = [],
            duration = null,
            persistent = false
        } = options;

        // Remove existing notification with same ID
        this.hideNotification(id);

        const notification = document.createElement('div');
        notification.id = `notification-${id}`;
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-header">
                    <strong>${title}</strong>
                    <button class="notification-close" onclick="swManager.hideNotification('${id}')">&times;</button>
                </div>
                <div class="notification-message">${message}</div>
                ${actions.length > 0 ? `
                    <div class="notification-actions">
                        ${actions.map((action, index) => `
                            <button class="btn ${action.primary ? 'btn-primary' : 'btn-secondary'}" 
                                    onclick="swManager.executeNotificationAction('${id}', ${index})">
                                ${action.text}
                            </button>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;

        // Store actions for later execution
        notification._actions = actions;

        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            max-width: 350px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            animation: slideInRight 0.3s ease-out;
            border-left: 4px solid ${this.getNotificationColor(type)};
        `;

        document.body.appendChild(notification);

        // Auto-hide if not persistent
        if (!persistent && duration) {
            setTimeout(() => this.hideNotification(id), duration);
        }
    }

    hideNotification(id) {
        const notification = document.getElementById(`notification-${id}`);
        if (notification) {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        }
    }

    executeNotificationAction(id, actionIndex) {
        const notification = document.getElementById(`notification-${id}`);
        if (notification && notification._actions && notification._actions[actionIndex]) {
            notification._actions[actionIndex].action();
        }
    }

    getNotificationColor(type) {
        const colors = {
            success: '#10B981',
            error: '#EF4444',
            warning: '#F59E0B',
            info: '#3B82F6'
        };
        return colors[type] || colors.info;
    }

    // =====================================
    // ANALYTICS INTEGRATION
    // =====================================

    trackInstallEvent(outcome = 'installed') {
        if (window.gtag) {
            gtag('event', 'pwa_install', {
                event_category: 'PWA',
                event_label: outcome,
                value: 1
            });
        }

        // Also track with custom analytics
        if (window.performanceAnalytics) {
            window.performanceAnalytics.addCustomEvent('pwa_install', {
                outcome,
                timestamp: Date.now()
            });
        }
    }

    // =====================================
    // PUBLIC API
    // =====================================

    async getServiceWorkerVersion() {
        if (this.swRegistration?.active) {
            return new Promise(resolve => {
                const messageChannel = new MessageChannel();
                messageChannel.port1.onmessage = event => {
                    resolve(event.data.version);
                };
                this.swRegistration.active.postMessage(
                    { type: 'GET_VERSION' },
                    [messageChannel.port2]
                );
            });
        }
        return null;
    }

    async clearCache(cacheName = null) {
        if (this.swRegistration?.active) {
            this.swRegistration.active.postMessage({
                type: 'CLEAR_CACHE',
                data: { cacheName }
            });
        }
    }

    isOfflineReady() {
        return this.swRegistration?.active && 'serviceWorker' in navigator;
    }

    getNetworkStatus() {
        return {
            online: navigator.onLine,
            connection: navigator.connection ? {
                effectiveType: navigator.connection.effectiveType,
                saveData: navigator.connection.saveData,
                downlink: navigator.connection.downlink
            } : null
        };
    }
}

// Add notification styles
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    @keyframes slideInUp {
        from { transform: translateY(100%); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .notification {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        line-height: 1.4;
    }
    
    .notification-content {
        padding: 16px;
    }
    
    .notification-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    
    .notification-close {
        background: none;
        border: none;
        font-size: 18px;
        cursor: pointer;
        padding: 0;
        color: #666;
    }
    
    .notification-message {
        color: #555;
        margin-bottom: 12px;
    }
    
    .notification-actions {
        display: flex;
        gap: 8px;
        justify-content: flex-end;
    }
    
    .notification-actions .btn {
        padding: 6px 12px;
        font-size: 12px;
        border-radius: 4px;
        border: none;
        cursor: pointer;
    }
    
    .notification-actions .btn-primary {
        background: #C7B375;
        color: white;
    }
    
    .notification-actions .btn-secondary {
        background: #f0f0f0;
        color: #333;
    }
    
    .install-btn {
        transition: all 0.3s ease;
    }
    
    .install-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.4);
    }
    
    /* Offline indicator styles */
    .offline .navbar::after {
        content: 'Offline Mode';
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: #f59e0b;
        color: white;
        text-align: center;
        padding: 4px;
        font-size: 12px;
        z-index: 999;
    }
`;

document.head.appendChild(notificationStyles);

// Initialize Service Worker Manager
let swManager;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        swManager = new ServiceWorkerManager();
    });
} else {
    swManager = new ServiceWorkerManager();
}

// Export for global access
window.swManager = swManager;