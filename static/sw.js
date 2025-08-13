/**
 * Service Worker for Advanced Caching and Performance
 * SPEC_04 Group D Implementation
 */

const CACHE_NAME = 'sabor-con-flow-v1.2';
const STATIC_CACHE = `${CACHE_NAME}-static`;
const DYNAMIC_CACHE = `${CACHE_NAME}-dynamic`;
const IMAGE_CACHE = `${CACHE_NAME}-images`;

// Resources to cache immediately
const STATIC_ASSETS = [
    '/',
    '/static/css/styles.css',
    '/static/css/navigation.css',
    '/static/css/hero.css',
    '/static/js/advanced-lazy-load.js',
    '/static/js/performance-analytics.js',
    '/static/js/mobile-nav.js',
    '/static/images/sabor-con-flow-logo.webp',
    '/static/images/sabor-con-flow-logo.png',
    'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&display=swap',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap'
];

// Cache strategies for different resource types
const CACHE_STRATEGIES = {
    static: 'cache-first',
    dynamic: 'network-first',
    images: 'cache-first-fallback'
};

// Performance monitoring
let performanceMetrics = {
    cacheHits: 0,
    cacheMisses: 0,
    networkRequests: 0,
    offlineRequests: 0
};

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('🔧 Service Worker installing...');
    
    event.waitUntil(
        Promise.all([
            caches.open(STATIC_CACHE).then(cache => {
                console.log('📦 Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            }),
            self.skipWaiting()
        ])
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('✅ Service Worker activated');
    
    event.waitUntil(
        Promise.all([
            // Clean up old caches
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName.startsWith('sabor-con-flow-') && 
                            !cacheName.includes('v1.2')) {
                            console.log('🗑️ Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),
            // Take control of all clients
            self.clients.claim()
        ])
    );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
    const request = event.request;
    const url = new URL(request.url);
    
    // Skip non-GET requests and Chrome extension requests
    if (request.method !== 'GET' || url.protocol === 'chrome-extension:') {
        return;
    }
    
    // Choose strategy based on resource type
    if (isStaticAsset(url)) {
        event.respondWith(cacheFirstStrategy(request, STATIC_CACHE));
    } else if (isImage(url)) {
        event.respondWith(imageStrategy(request));
    } else if (isAPI(url)) {
        event.respondWith(networkFirstStrategy(request, DYNAMIC_CACHE));
    } else if (isPage(url)) {
        event.respondWith(staleWhileRevalidateStrategy(request, DYNAMIC_CACHE));
    } else {
        event.respondWith(networkFirstStrategy(request, DYNAMIC_CACHE));
    }
});

// Cache-first strategy for static assets
async function cacheFirstStrategy(request, cacheName) {
    try {
        const cache = await caches.open(cacheName);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            performanceMetrics.cacheHits++;
            return cachedResponse;
        }
        
        performanceMetrics.cacheMisses++;
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        console.error('Cache-first strategy failed:', error);
        return handleOfflineRequest(request);
    }
}

// Network-first strategy for dynamic content
async function networkFirstStrategy(request, cacheName) {
    try {
        performanceMetrics.networkRequests++;
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        console.log('Network failed, trying cache:', request.url);
        
        const cache = await caches.open(cacheName);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            performanceMetrics.cacheHits++;
            return cachedResponse;
        }
        
        return handleOfflineRequest(request);
    }
}

// Stale-while-revalidate strategy for pages
async function staleWhileRevalidateStrategy(request, cacheName) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    // Fetch in background to update cache
    const fetchPromise = fetch(request).then(response => {
        if (response.ok) {
            cache.put(request, response.clone());
        }
        return response;
    }).catch(() => {
        // Network failed, but we might have cached version
    });
    
    if (cachedResponse) {
        performanceMetrics.cacheHits++;
        // Return cached version immediately
        return cachedResponse;
    }
    
    // If no cached version, wait for network
    try {
        performanceMetrics.networkRequests++;
        return await fetchPromise;
    } catch (error) {
        return handleOfflineRequest(request);
    }
}

// Advanced image caching strategy
async function imageStrategy(request) {
    try {
        const cache = await caches.open(IMAGE_CACHE);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            performanceMetrics.cacheHits++;
            return cachedResponse;
        }
        
        // Try network
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // Only cache successful responses
            cache.put(request, networkResponse.clone());
            
            // Implement cache size management
            manageCacheSize(IMAGE_CACHE, 50); // Keep max 50 images
        }
        
        return networkResponse;
        
    } catch (error) {
        // Try to find a fallback image
        return handleOfflineImageRequest(request);
    }
}

// Manage cache size to prevent storage bloat
async function manageCacheSize(cacheName, maxEntries) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    
    if (keys.length > maxEntries) {
        // Remove oldest entries (FIFO)
        const entriesToDelete = keys.slice(0, keys.length - maxEntries);
        await Promise.all(entriesToDelete.map(key => cache.delete(key)));
    }
}

// Handle offline requests
function handleOfflineRequest(request) {
    performanceMetrics.offlineRequests++;
    
    if (isPage(new URL(request.url))) {
        return caches.match('/') || new Response(
            '<!DOCTYPE html><html><head><title>Offline</title></head><body><h1>You are offline</h1><p>Please check your internet connection.</p></body></html>',
            { headers: { 'Content-Type': 'text/html' } }
        );
    }
    
    return new Response('Offline', { 
        status: 503, 
        statusText: 'Service Unavailable' 
    });
}

// Handle offline image requests with placeholder
function handleOfflineImageRequest(request) {
    // Return a placeholder SVG
    const svg = `
        <svg xmlns="http://www.w3.org/2000/svg" width="300" height="200" viewBox="0 0 300 200">
            <rect width="100%" height="100%" fill="#f0f0f0"/>
            <text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" 
                  font-family="Arial" font-size="14" fill="#999">
                Image unavailable offline
            </text>
        </svg>
    `;
    
    return new Response(svg, {
        headers: {
            'Content-Type': 'image/svg+xml',
            'Cache-Control': 'no-cache'
        }
    });
}

// Utility functions to identify resource types
function isStaticAsset(url) {
    return url.pathname.startsWith('/static/') || 
           url.hostname === 'fonts.googleapis.com' ||
           url.hostname === 'fonts.gstatic.com' ||
           url.hostname === 'cdnjs.cloudflare.com';
}

function isImage(url) {
    return /\.(jpg|jpeg|png|gif|webp|svg|ico)$/i.test(url.pathname);
}

function isAPI(url) {
    return url.pathname.startsWith('/api/');
}

function isPage(url) {
    return url.origin === self.location.origin && 
           !url.pathname.startsWith('/static/') &&
           !url.pathname.startsWith('/api/') &&
           !isImage(url);
}

// Background sync for performance data
self.addEventListener('sync', (event) => {
    if (event.tag === 'performance-sync') {
        event.waitUntil(syncPerformanceData());
    }
});

async function syncPerformanceData() {
    try {
        // Send performance metrics to server when back online
        const response = await fetch('/api/performance-metrics/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: 'service_worker_metrics',
                data: performanceMetrics,
                timestamp: Date.now()
            })
        });
        
        if (response.ok) {
            // Reset metrics after successful sync
            performanceMetrics = {
                cacheHits: 0,
                cacheMisses: 0,
                networkRequests: 0,
                offlineRequests: 0
            };
        }
    } catch (error) {
        console.log('Performance sync failed:', error);
    }
}

// Handle messages from the main thread
self.addEventListener('message', (event) => {
    const { type, data } = event.data;
    
    switch (type) {
        case 'PERFORMANCE_DATA':
            // Store performance data from main thread
            break;
            
        case 'SKIP_WAITING':
            self.skipWaiting();
            break;
            
        case 'GET_CACHE_INFO':
            getCacheInfo().then(info => {
                event.ports[0].postMessage(info);
            });
            break;
            
        case 'CLEAR_CACHE':
            clearCache(data.cacheName).then(() => {
                event.ports[0].postMessage({ success: true });
            });
            break;
    }
});

// Get cache information
async function getCacheInfo() {
    const cacheNames = await caches.keys();
    const cacheInfo = {};
    
    for (const cacheName of cacheNames) {
        const cache = await caches.open(cacheName);
        const keys = await cache.keys();
        cacheInfo[cacheName] = {
            size: keys.length,
            urls: keys.map(key => key.url).slice(0, 10) // First 10 URLs
        };
    }
    
    return {
        caches: cacheInfo,
        metrics: performanceMetrics
    };
}

// Clear specific cache
async function clearCache(cacheName) {
    if (cacheName) {
        return caches.delete(cacheName);
    } else {
        // Clear all caches
        const cacheNames = await caches.keys();
        return Promise.all(cacheNames.map(name => caches.delete(name)));
    }
}

// Periodic cache maintenance
setInterval(() => {
    // Clean up old cache entries periodically
    manageCacheSize(IMAGE_CACHE, 50);
    manageCacheSize(DYNAMIC_CACHE, 30);
}, 60000 * 60); // Every hour

console.log('🚀 Service Worker loaded - SPEC_04 Group D Performance Optimizations');