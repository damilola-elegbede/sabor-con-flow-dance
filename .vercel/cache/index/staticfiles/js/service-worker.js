/**
 * Service Worker for Sabor Con Flow Dance PWA
 * Implements offline functionality, caching strategies, and performance optimization
 * Version: 2.0.0
 */

const CACHE_VERSION = '2.0.0';
const CACHE_PREFIX = 'sabor-con-flow-v';
const CACHE_NAME = `${CACHE_PREFIX}${CACHE_VERSION}`;

// Cache names for different content types
const CACHE_NAMES = {
    static: `${CACHE_PREFIX}static-${CACHE_VERSION}`,
    images: `${CACHE_PREFIX}images-${CACHE_VERSION}`,
    pages: `${CACHE_PREFIX}pages-${CACHE_VERSION}`,
    api: `${CACHE_PREFIX}api-${CACHE_VERSION}`,
    fonts: `${CACHE_PREFIX}fonts-${CACHE_VERSION}`
};

// Static assets to cache on install
const STATIC_ASSETS = [
    '/',
    '/static/css/styles.css',
    '/static/css/navigation.css',
    '/static/css/hero.css',
    '/static/css/pricing.css',
    '/static/css/schedule.css',
    '/static/js/mobile-nav.js',
    '/static/js/lazy-load.js',
    '/static/js/performance-monitor.js',
    '/static/js/pricing-calculator.js',
    '/static/images/sabor-con-flow-logo.webp',
    '/static/images/sabor-con-flow-logo.png',
    '/static/images/favicon/favicon.webp',
    '/static/images/favicon/favicon.png',
    '/offline/',
    '/manifest.json'
];

// Essential pages to cache for offline access
const ESSENTIAL_PAGES = [
    '/',
    '/pricing/',
    '/schedule/',
    '/contact/',
    '/private-lessons/',
    '/events/'
];

// Background sync tags
const SYNC_TAGS = {
    CONTACT_FORM: 'contact-form-submission',
    TESTIMONIAL: 'testimonial-submission',
    NEWSLETTER: 'newsletter-signup',
    ANALYTICS: 'analytics-data'
};

// IndexedDB configuration for background sync
const DB_NAME = 'SaborConFlowSW';
const DB_VERSION = 1;
const STORES = {
    SYNC_QUEUE: 'syncQueue',
    ANALYTICS: 'analytics'
};

/**
 * Service Worker Installation
 * Pre-cache essential static assets
 */
self.addEventListener('install', event => {
    console.log('[SW] Installing service worker v' + CACHE_VERSION);
    
    event.waitUntil(
        Promise.all([
            // Cache static assets
            caches.open(CACHE_NAMES.static)
                .then(cache => {
                    console.log('[SW] Caching static assets');
                    return cache.addAll(STATIC_ASSETS);
                }),
            
            // Cache essential pages
            caches.open(CACHE_NAMES.pages)
                .then(cache => {
                    console.log('[SW] Caching essential pages');
                    return cache.addAll(ESSENTIAL_PAGES);
                }),
            
            // Initialize IndexedDB
            initializeIndexedDB()
        ])
        .then(() => {
            console.log('[SW] Installation complete');
            // Skip waiting to activate immediately
            return self.skipWaiting();
        })
        .catch(error => {
            console.error('[SW] Installation failed:', error);
        })
    );
});

/**
 * Service Worker Activation
 * Clean up old caches and claim clients
 */
self.addEventListener('activate', event => {
    console.log('[SW] Activating service worker v' + CACHE_VERSION);
    
    event.waitUntil(
        Promise.all([
            // Clean up old caches
            cleanupOldCaches(),
            
            // Claim all clients immediately
            self.clients.claim(),
            
            // Set up background sync
            setupBackgroundSync()
        ])
        .then(() => {
            console.log('[SW] Activation complete');
            // Notify clients of successful activation
            notifyClientsOfUpdate();
        })
        .catch(error => {
            console.error('[SW] Activation failed:', error);
        })
    );
});

/**
 * Fetch Event Handler
 * Implements caching strategies based on content type
 */
self.addEventListener('fetch', event => {
    const request = event.request;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip chrome-extension and other non-http(s) schemes
    if (!url.protocol.startsWith('http')) {
        return;
    }
    
    // Choose strategy based on request type
    if (isImageRequest(request)) {
        event.respondWith(cacheFirstStrategy(request, CACHE_NAMES.images));
    } else if (isCSSRequest(request)) {
        event.respondWith(cacheFirstStrategy(request, CACHE_NAMES.static));
    } else if (isJSRequest(request)) {
        event.respondWith(cacheFirstStrategy(request, CACHE_NAMES.static));
    } else if (isFontRequest(request)) {
        event.respondWith(cacheFirstStrategy(request, CACHE_NAMES.fonts));
    } else if (isAPIRequest(request)) {
        event.respondWith(networkFirstStrategy(request, CACHE_NAMES.api));
    } else if (isHTMLRequest(request)) {
        event.respondWith(networkFirstStrategy(request, CACHE_NAMES.pages));
    } else {
        // Default to network first for other requests
        event.respondWith(networkFirstStrategy(request, CACHE_NAMES.static));
    }
});

/**
 * Background Sync Event Handler
 * Handle background synchronization for offline form submissions
 */
self.addEventListener('sync', event => {
    console.log('[SW] Background sync triggered:', event.tag);
    
    switch (event.tag) {
        case SYNC_TAGS.CONTACT_FORM:
            event.waitUntil(syncContactForms());
            break;
        case SYNC_TAGS.TESTIMONIAL:
            event.waitUntil(syncTestimonials());
            break;
        case SYNC_TAGS.NEWSLETTER:
            event.waitUntil(syncNewsletterSignups());
            break;
        case SYNC_TAGS.ANALYTICS:
            event.waitUntil(syncAnalyticsData());
            break;
        default:
            console.log('[SW] Unknown sync tag:', event.tag);
    }
});

/**
 * Message Event Handler
 * Handle messages from the main thread
 */
self.addEventListener('message', event => {
    const { type, data } = event.data;
    
    switch (type) {
        case 'SKIP_WAITING':
            self.skipWaiting();
            break;
        case 'GET_VERSION':
            event.ports[0].postMessage({ version: CACHE_VERSION });
            break;
        case 'CACHE_ANALYTICS':
            cacheAnalyticsData(data);
            break;
        case 'QUEUE_SYNC':
            queueSyncData(data.tag, data.payload);
            break;
        case 'CLEAR_CACHE':
            clearSpecificCache(data.cacheName);
            break;
        default:
            console.log('[SW] Unknown message type:', type);
    }
});

/**
 * Push Event Handler
 * Handle push notifications (future implementation)
 */
self.addEventListener('push', event => {
    console.log('[SW] Push received');
    
    if (event.data) {
        const options = {
            body: event.data.text(),
            icon: '/static/images/favicon/favicon.png',
            badge: '/static/images/favicon/favicon_small.png',
            vibrate: [100, 50, 100],
            data: {
                dateOfArrival: Date.now(),
                primaryKey: 1
            },
            actions: [
                {
                    action: 'explore',
                    title: 'View Details',
                    icon: '/static/images/favicon/favicon_small.png'
                },
                {
                    action: 'close',
                    title: 'Close',
                    icon: '/static/images/favicon/favicon_small.png'
                }
            ]
        };
        
        event.waitUntil(
            self.registration.showNotification('Sabor Con Flow Dance', options)
        );
    }
});

/**
 * Notification Click Handler
 */
self.addEventListener('notificationclick', event => {
    console.log('[SW] Notification click received');
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// =====================================
// CACHING STRATEGIES
// =====================================

/**
 * Cache First Strategy
 * Try cache first, fallback to network
 */
async function cacheFirstStrategy(request, cacheName) {
    try {
        const cache = await caches.open(cacheName);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            // Update cache in background
            updateCacheInBackground(request, cache);
            return cachedResponse;
        }
        
        // Fetch from network and cache
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('[SW] Cache first strategy failed:', error);
        return getOfflineFallback(request);
    }
}

/**
 * Network First Strategy
 * Try network first, fallback to cache
 */
async function networkFirstStrategy(request, cacheName) {
    try {
        const cache = await caches.open(cacheName);
        
        try {
            const networkResponse = await fetch(request);
            
            if (networkResponse.ok) {
                cache.put(request, networkResponse.clone());
            }
            
            return networkResponse;
        } catch (networkError) {
            console.log('[SW] Network failed, trying cache');
            
            const cachedResponse = await cache.match(request);
            
            if (cachedResponse) {
                return cachedResponse;
            }
            
            return getOfflineFallback(request);
        }
    } catch (error) {
        console.error('[SW] Network first strategy failed:', error);
        return getOfflineFallback(request);
    }
}

/**
 * Stale While Revalidate Strategy
 * Return cached version while updating in background
 */
async function staleWhileRevalidateStrategy(request, cacheName) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    const fetchPromise = fetch(request).then(networkResponse => {
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    });
    
    return cachedResponse || fetchPromise;
}

// =====================================
// UTILITY FUNCTIONS
// =====================================

/**
 * Request Type Detection
 */
function isImageRequest(request) {
    return request.destination === 'image' || 
           /\.(jpg|jpeg|png|gif|webp|svg|ico)$/i.test(request.url);
}

function isCSSRequest(request) {
    return request.destination === 'style' || 
           request.url.includes('.css');
}

function isJSRequest(request) {
    return request.destination === 'script' || 
           request.url.includes('.js');
}

function isFontRequest(request) {
    return request.destination === 'font' || 
           /\.(woff|woff2|ttf|eot|otf)$/i.test(request.url);
}

function isAPIRequest(request) {
    return request.url.includes('/api/') || 
           request.url.includes('/ajax/');
}

function isHTMLRequest(request) {
    return request.destination === 'document' || 
           request.headers.get('accept')?.includes('text/html');
}

/**
 * Offline Fallback Handler
 */
async function getOfflineFallback(request) {
    if (isHTMLRequest(request)) {
        const cache = await caches.open(CACHE_NAMES.pages);
        return await cache.match('/offline/') || 
               await cache.match('/') ||
               new Response('Offline - Please check your connection', {
                   status: 503,
                   headers: { 'Content-Type': 'text/plain' }
               });
    }
    
    if (isImageRequest(request)) {
        // Return a placeholder image or cached image
        const cache = await caches.open(CACHE_NAMES.images);
        return await cache.match('/static/images/sabor-con-flow-logo.png') ||
               new Response(createOfflineImageSVG(), {
                   headers: { 'Content-Type': 'image/svg+xml' }
               });
    }
    
    return new Response('Offline', { 
        status: 503,
        headers: { 'Content-Type': 'text/plain' }
    });
}

/**
 * Create offline placeholder image
 */
function createOfflineImageSVG() {
    return `<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
        <rect width="200" height="200" fill="#f0f0f0"/>
        <text x="100" y="100" text-anchor="middle" dy="0.3em" font-family="Arial" font-size="14" fill="#666">
            Offline Image
        </text>
    </svg>`;
}

/**
 * Update cache in background
 */
async function updateCacheInBackground(request, cache) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            await cache.put(request, networkResponse);
        }
    } catch (error) {
        console.log('[SW] Background update failed:', error);
    }
}

/**
 * Clean up old caches
 */
async function cleanupOldCaches() {
    const cacheNames = await caches.keys();
    const oldCaches = cacheNames.filter(name => 
        name.startsWith(CACHE_PREFIX) && 
        !Object.values(CACHE_NAMES).includes(name)
    );
    
    console.log('[SW] Cleaning up old caches:', oldCaches);
    
    return Promise.all(
        oldCaches.map(cacheName => caches.delete(cacheName))
    );
}

/**
 * Clear specific cache
 */
async function clearSpecificCache(cacheName) {
    if (cacheName && await caches.has(cacheName)) {
        await caches.delete(cacheName);
        console.log('[SW] Cleared cache:', cacheName);
    }
}

/**
 * Notify clients of service worker update
 */
async function notifyClientsOfUpdate() {
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
        client.postMessage({
            type: 'SW_UPDATED',
            version: CACHE_VERSION
        });
    });
}

// =====================================
// INDEXEDDB AND BACKGROUND SYNC
// =====================================

/**
 * Initialize IndexedDB for background sync
 */
async function initializeIndexedDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        
        request.onupgradeneeded = event => {
            const db = event.target.result;
            
            // Create sync queue store
            if (!db.objectStoreNames.contains(STORES.SYNC_QUEUE)) {
                const syncStore = db.createObjectStore(STORES.SYNC_QUEUE, {
                    keyPath: 'id',
                    autoIncrement: true
                });
                syncStore.createIndex('tag', 'tag', { unique: false });
                syncStore.createIndex('timestamp', 'timestamp', { unique: false });
            }
            
            // Create analytics store
            if (!db.objectStoreNames.contains(STORES.ANALYTICS)) {
                const analyticsStore = db.createObjectStore(STORES.ANALYTICS, {
                    keyPath: 'id',
                    autoIncrement: true
                });
                analyticsStore.createIndex('timestamp', 'timestamp', { unique: false });
            }
        };
    });
}

/**
 * Queue data for background sync
 */
async function queueSyncData(tag, data) {
    try {
        const db = await initializeIndexedDB();
        const transaction = db.transaction([STORES.SYNC_QUEUE], 'readwrite');
        const store = transaction.objectStore(STORES.SYNC_QUEUE);
        
        await store.add({
            tag,
            data,
            timestamp: Date.now(),
            retries: 0
        });
        
        // Register for background sync
        await self.registration.sync.register(tag);
        
        console.log('[SW] Queued sync data for tag:', tag);
    } catch (error) {
        console.error('[SW] Failed to queue sync data:', error);
    }
}

/**
 * Cache analytics data
 */
async function cacheAnalyticsData(data) {
    try {
        const db = await initializeIndexedDB();
        const transaction = db.transaction([STORES.ANALYTICS], 'readwrite');
        const store = transaction.objectStore(STORES.ANALYTICS);
        
        await store.add({
            ...data,
            timestamp: Date.now()
        });
        
        console.log('[SW] Cached analytics data');
    } catch (error) {
        console.error('[SW] Failed to cache analytics data:', error);
    }
}

/**
 * Setup background sync
 */
async function setupBackgroundSync() {
    // Register all sync tags
    try {
        await Promise.all(
            Object.values(SYNC_TAGS).map(tag => 
                self.registration.sync.register(tag)
            )
        );
        console.log('[SW] Background sync registered');
    } catch (error) {
        console.error('[SW] Background sync registration failed:', error);
    }
}

/**
 * Sync queued contact forms
 */
async function syncContactForms() {
    try {
        const db = await initializeIndexedDB();
        const transaction = db.transaction([STORES.SYNC_QUEUE], 'readwrite');
        const store = transaction.objectStore(STORES.SYNC_QUEUE);
        const index = store.index('tag');
        
        const items = await index.getAll(SYNC_TAGS.CONTACT_FORM);
        
        for (const item of items) {
            try {
                const response = await fetch('/contact/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': item.data.csrfToken
                    },
                    body: JSON.stringify(item.data)
                });
                
                if (response.ok) {
                    await store.delete(item.id);
                    console.log('[SW] Synced contact form:', item.id);
                } else {
                    throw new Error('Sync failed');
                }
            } catch (error) {
                console.error('[SW] Failed to sync contact form:', error);
                // Increment retry count
                item.retries = (item.retries || 0) + 1;
                if (item.retries < 3) {
                    await store.put(item);
                } else {
                    await store.delete(item.id);
                    console.log('[SW] Max retries reached, discarding:', item.id);
                }
            }
        }
    } catch (error) {
        console.error('[SW] Contact form sync failed:', error);
    }
}

/**
 * Sync testimonials
 */
async function syncTestimonials() {
    // Similar implementation to syncContactForms
    console.log('[SW] Syncing testimonials...');
    // Implementation would be similar to syncContactForms
}

/**
 * Sync newsletter signups
 */
async function syncNewsletterSignups() {
    // Similar implementation to syncContactForms
    console.log('[SW] Syncing newsletter signups...');
    // Implementation would be similar to syncContactForms
}

/**
 * Sync analytics data
 */
async function syncAnalyticsData() {
    try {
        const db = await initializeIndexedDB();
        const transaction = db.transaction([STORES.ANALYTICS], 'readwrite');
        const store = transaction.objectStore(STORES.ANALYTICS);
        
        const allAnalytics = await store.getAll();
        
        if (allAnalytics.length > 0) {
            // Send analytics data to Google Analytics
            for (const analytics of allAnalytics) {
                try {
                    // Implementation would depend on your analytics setup
                    console.log('[SW] Syncing analytics data:', analytics);
                    await store.delete(analytics.id);
                } catch (error) {
                    console.error('[SW] Failed to sync analytics:', error);
                }
            }
        }
    } catch (error) {
        console.error('[SW] Analytics sync failed:', error);
    }
}

// Performance monitoring
self.addEventListener('fetch', event => {
    const startTime = performance.now();
    
    event.respondWith(
        (async () => {
            const response = await handleFetch(event);
            const endTime = performance.now();
            const duration = endTime - startTime;
            
            // Log slow requests
            if (duration > 1000) {
                console.warn('[SW] Slow request detected:', {
                    url: event.request.url,
                    duration: duration + 'ms'
                });
            }
            
            return response;
        })()
    );
});

async function handleFetch(event) {
    // Your existing fetch handling logic here
    return fetch(event.request);
}