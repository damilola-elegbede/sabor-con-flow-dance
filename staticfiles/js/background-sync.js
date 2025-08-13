/**
 * Background Sync Utility for Offline Form Submissions
 * Handles form submission queuing and synchronization when online
 */

class BackgroundSyncManager {
    constructor() {
        this.isOnline = navigator.onLine;
        this.syncQueue = [];
        this.syncInProgress = false;
        
        this.init();
    }

    init() {
        // Listen for online/offline events
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());
        
        // Set up form listeners
        this.setupFormListeners();
        
        // Try to sync existing queue on load
        if (this.isOnline) {
            this.syncPendingSubmissions();
        }
    }

    handleOnline() {
        console.log('[BackgroundSync] Connection restored');
        this.isOnline = true;
        
        // Update UI
        document.body.classList.remove('offline');
        document.body.classList.add('online');
        
        // Try to sync pending submissions
        this.syncPendingSubmissions();
        
        // Hide offline notifications
        this.hideOfflineNotifications();
    }

    handleOffline() {
        console.log('[BackgroundSync] Connection lost');
        this.isOnline = false;
        
        // Update UI
        document.body.classList.remove('online');
        document.body.classList.add('offline');
        
        // Show offline notification
        this.showOfflineNotification();
    }

    setupFormListeners() {
        // Contact forms
        const contactForms = document.querySelectorAll('form[action*="contact"]');
        contactForms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!this.isOnline) {
                    event.preventDefault();
                    this.queueFormSubmission(form, 'contact');
                }
            });
        });

        // Testimonial forms
        const testimonialForms = document.querySelectorAll('form[action*="testimonial"]');
        testimonialForms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!this.isOnline) {
                    event.preventDefault();
                    this.queueFormSubmission(form, 'testimonial');
                }
            });
        });

        // Newsletter forms
        const newsletterForms = document.querySelectorAll('form[data-type="newsletter"]');
        newsletterForms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!this.isOnline) {
                    event.preventDefault();
                    this.queueFormSubmission(form, 'newsletter');
                }
            });
        });

        // RSVP forms
        const rsvpForms = document.querySelectorAll('form[data-type="rsvp"]');
        rsvpForms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!this.isOnline) {
                    event.preventDefault();
                    this.queueFormSubmission(form, 'rsvp');
                }
            });
        });
    }

    queueFormSubmission(form, type) {
        try {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            // Add metadata
            const submission = {
                id: Date.now() + Math.random(),
                type: type,
                url: form.action,
                method: form.method || 'POST',
                data: data,
                timestamp: Date.now(),
                retries: 0
            };

            // Store in queue
            this.syncQueue.push(submission);
            this.saveQueueToStorage();

            // Send to service worker if available
            if (window.swManager && window.swManager.swRegistration?.active) {
                window.swManager.swRegistration.active.postMessage({
                    type: 'QUEUE_SYNC',
                    data: { tag: `${type}-submission`, payload: submission }
                });
            }

            // Show confirmation
            this.showOfflineSubmissionMessage(type);

            console.log(`[BackgroundSync] Queued ${type} submission:`, submission.id);
        } catch (error) {
            console.error('[BackgroundSync] Failed to queue submission:', error);
            this.showErrorMessage('Failed to save submission for later. Please try again.');
        }
    }

    async syncPendingSubmissions() {
        if (this.syncInProgress || this.syncQueue.length === 0) {
            return;
        }

        this.syncInProgress = true;
        console.log(`[BackgroundSync] Syncing ${this.syncQueue.length} pending submissions`);

        const synced = [];
        const failed = [];

        for (const submission of this.syncQueue) {
            try {
                const success = await this.submitForm(submission);
                if (success) {
                    synced.push(submission);
                } else {
                    submission.retries = (submission.retries || 0) + 1;
                    if (submission.retries >= 3) {
                        failed.push(submission);
                    }
                }
            } catch (error) {
                console.error('[BackgroundSync] Sync failed for submission:', submission.id, error);
                submission.retries = (submission.retries || 0) + 1;
                if (submission.retries >= 3) {
                    failed.push(submission);
                }
            }
        }

        // Remove synced and failed submissions
        this.syncQueue = this.syncQueue.filter(sub => 
            !synced.includes(sub) && !failed.includes(sub)
        );

        this.saveQueueToStorage();

        if (synced.length > 0) {
            this.showSyncCompleteMessage(synced.length);
        }

        if (failed.length > 0) {
            console.warn(`[BackgroundSync] ${failed.length} submissions failed permanently`);
        }

        this.syncInProgress = false;
    }

    async submitForm(submission) {
        try {
            const formData = new FormData();
            
            // Add form data
            for (const [key, value] of Object.entries(submission.data)) {
                formData.append(key, value);
            }

            const response = await fetch(submission.url, {
                method: submission.method,
                body: formData,
                credentials: 'same-origin'
            });

            if (response.ok) {
                console.log(`[BackgroundSync] Successfully synced ${submission.type}:`, submission.id);
                return true;
            } else {
                console.error(`[BackgroundSync] Sync failed for ${submission.type}:`, response.status);
                return false;
            }
        } catch (error) {
            console.error(`[BackgroundSync] Network error syncing ${submission.type}:`, error);
            return false;
        }
    }

    saveQueueToStorage() {
        try {
            localStorage.setItem('backgroundSyncQueue', JSON.stringify(this.syncQueue));
        } catch (error) {
            console.error('[BackgroundSync] Failed to save queue to storage:', error);
        }
    }

    loadQueueFromStorage() {
        try {
            const stored = localStorage.getItem('backgroundSyncQueue');
            if (stored) {
                this.syncQueue = JSON.parse(stored);
                console.log(`[BackgroundSync] Loaded ${this.syncQueue.length} items from storage`);
            }
        } catch (error) {
            console.error('[BackgroundSync] Failed to load queue from storage:', error);
            this.syncQueue = [];
        }
    }

    // =====================================
    // USER NOTIFICATIONS
    // =====================================

    showOfflineNotification() {
        this.showNotification({
            id: 'offline-status',
            title: 'You\'re Offline',
            message: 'Form submissions will be saved and sent when you\'re back online.',
            type: 'info',
            persistent: true,
            icon: 'fas fa-wifi-slash'
        });
    }

    hideOfflineNotifications() {
        this.hideNotification('offline-status');
    }

    showOfflineSubmissionMessage(type) {
        const typeNames = {
            contact: 'contact form',
            testimonial: 'testimonial',
            newsletter: 'newsletter signup',
            rsvp: 'RSVP'
        };

        this.showNotification({
            id: `offline-${type}`,
            title: 'Saved for Later',
            message: `Your ${typeNames[type] || type} has been saved and will be submitted when you're back online.`,
            type: 'success',
            duration: 4000,
            icon: 'fas fa-clock'
        });
    }

    showSyncCompleteMessage(count) {
        this.showNotification({
            id: 'sync-complete',
            title: 'Submissions Sent',
            message: `${count} form submission${count > 1 ? 's' : ''} successfully sent!`,
            type: 'success',
            duration: 3000,
            icon: 'fas fa-check-circle'
        });
    }

    showErrorMessage(message) {
        this.showNotification({
            id: 'sync-error',
            title: 'Error',
            message: message,
            type: 'error',
            duration: 5000,
            icon: 'fas fa-exclamation-triangle'
        });
    }

    showNotification(options) {
        const {
            id,
            title,
            message,
            type = 'info',
            duration = null,
            persistent = false,
            icon = null
        } = options;

        // Remove existing notification with same ID
        this.hideNotification(id);

        const notification = document.createElement('div');
        notification.id = `bg-sync-notification-${id}`;
        notification.className = `bg-sync-notification bg-sync-notification-${type}`;
        
        const iconHtml = icon ? `<i class="${icon}"></i>` : '';
        
        notification.innerHTML = `
            <div class="bg-sync-notification-content">
                <div class="bg-sync-notification-header">
                    ${iconHtml}
                    <strong>${title}</strong>
                    <button class="bg-sync-notification-close" onclick="backgroundSync.hideNotification('${id}')">&times;</button>
                </div>
                <div class="bg-sync-notification-message">${message}</div>
            </div>
        `;

        // Add styles if not already added
        this.ensureNotificationStyles();

        // Position notification
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.4;
        `;

        document.body.appendChild(notification);

        // Auto-hide if not persistent
        if (!persistent && duration) {
            setTimeout(() => this.hideNotification(id), duration);
        }
    }

    hideNotification(id) {
        const notification = document.getElementById(`bg-sync-notification-${id}`);
        if (notification) {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
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

    ensureNotificationStyles() {
        if (document.getElementById('bg-sync-notification-styles')) {
            return;
        }

        const styles = document.createElement('style');
        styles.id = 'bg-sync-notification-styles';
        styles.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
            
            .bg-sync-notification-content {
                padding: 16px;
            }
            
            .bg-sync-notification-header {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 8px;
            }
            
            .bg-sync-notification-header i {
                color: inherit;
            }
            
            .bg-sync-notification-close {
                background: none;
                border: none;
                font-size: 18px;
                cursor: pointer;
                padding: 0;
                color: #666;
                margin-left: auto;
            }
            
            .bg-sync-notification-message {
                color: #555;
            }
            
            /* Offline indicator */
            .offline::after {
                content: 'Offline Mode';
                position: fixed;
                bottom: 20px;
                left: 20px;
                background: #f59e0b;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 9999;
                animation: slideInLeft 0.3s ease-out;
            }
            
            @keyframes slideInLeft {
                from { transform: translateX(-100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;

        document.head.appendChild(styles);
    }

    // =====================================
    // PUBLIC API
    // =====================================

    getPendingCount() {
        return this.syncQueue.length;
    }

    clearQueue() {
        this.syncQueue = [];
        this.saveQueueToStorage();
        console.log('[BackgroundSync] Queue cleared');
    }

    getQueueStatus() {
        return {
            isOnline: this.isOnline,
            pendingCount: this.syncQueue.length,
            syncInProgress: this.syncInProgress,
            queue: this.syncQueue.map(item => ({
                id: item.id,
                type: item.type,
                timestamp: item.timestamp,
                retries: item.retries
            }))
        };
    }

    forcSync() {
        if (this.isOnline) {
            this.syncPendingSubmissions();
        } else {
            this.showErrorMessage('Cannot sync while offline');
        }
    }
}

// Initialize Background Sync Manager
let backgroundSync;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        backgroundSync = new BackgroundSyncManager();
        backgroundSync.loadQueueFromStorage();
    });
} else {
    backgroundSync = new BackgroundSyncManager();
    backgroundSync.loadQueueFromStorage();
}

// Export for global access
window.backgroundSync = backgroundSync;