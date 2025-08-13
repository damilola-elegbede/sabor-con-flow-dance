/**
 * Service Worker Performance Monitoring
 * Monitors SW performance, cache hit rates, and offline functionality
 */

class ServiceWorkerPerformance {
    constructor() {
        this.metrics = {
            cacheHits: 0,
            cacheMisses: 0,
            offlineRequests: 0,
            syncOperations: 0,
            errors: 0
        };
        
        this.performanceObserver = null;
        this.startTime = performance.now();
        
        this.init();
    }

    init() {
        // Monitor service worker messages
        this.setupServiceWorkerMonitoring();
        
        // Monitor network performance
        this.setupNetworkMonitoring();
        
        // Monitor cache performance
        this.setupCacheMonitoring();
        
        // Track Core Web Vitals improvements
        this.setupCoreWebVitalsTracking();
        
        // Report metrics periodically
        this.scheduleMetricsReporting();
    }

    setupServiceWorkerMonitoring() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.addEventListener('message', event => {
                this.handleServiceWorkerMessage(event.data);
            });

            // Monitor service worker lifecycle
            navigator.serviceWorker.ready.then(registration => {
                console.log('[SW Performance] Service Worker ready');
                this.trackServiceWorkerReady();
                
                registration.addEventListener('updatefound', () => {
                    console.log('[SW Performance] Service Worker update found');
                    this.trackServiceWorkerUpdate();
                });
            });
        }
    }

    handleServiceWorkerMessage(data) {
        const { type, metrics: swMetrics } = data;
        
        switch (type) {
            case 'CACHE_HIT':
                this.metrics.cacheHits++;
                this.trackCachePerformance('hit', swMetrics);
                break;
            case 'CACHE_MISS':
                this.metrics.cacheMisses++;
                this.trackCachePerformance('miss', swMetrics);
                break;
            case 'OFFLINE_REQUEST':
                this.metrics.offlineRequests++;
                this.trackOfflineUsage(swMetrics);
                break;
            case 'SYNC_COMPLETE':
                this.metrics.syncOperations++;
                this.trackSyncPerformance(swMetrics);
                break;
            case 'SW_ERROR':
                this.metrics.errors++;
                this.trackServiceWorkerError(swMetrics);
                break;
            case 'PERFORMANCE_METRICS':
                this.analyzeServiceWorkerPerformance(swMetrics);
                break;
        }
    }

    setupNetworkMonitoring() {
        // Monitor fetch events for performance analysis
        const originalFetch = window.fetch;
        
        window.fetch = async (...args) => {
            const startTime = performance.now();
            const url = args[0];
            
            try {
                const response = await originalFetch(...args);
                const endTime = performance.now();
                const duration = endTime - startTime;
                
                this.trackFetchPerformance(url, duration, response.status, 'success');
                return response;
            } catch (error) {
                const endTime = performance.now();
                const duration = endTime - startTime;
                
                this.trackFetchPerformance(url, duration, 0, 'error');
                throw error;
            }
        };
    }

    setupCacheMonitoring() {
        // Monitor cache API usage
        if ('caches' in window) {
            const originalOpen = caches.open;
            const originalMatch = Cache.prototype.match;
            const originalAdd = Cache.prototype.add;
            const originalPut = Cache.prototype.put;

            // Monitor cache open operations
            caches.open = async (cacheName) => {
                const startTime = performance.now();
                try {
                    const cache = await originalOpen.call(caches, cacheName);
                    const duration = performance.now() - startTime;
                    
                    this.trackCacheOperation('open', cacheName, duration, true);
                    return cache;
                } catch (error) {
                    const duration = performance.now() - startTime;
                    this.trackCacheOperation('open', cacheName, duration, false);
                    throw error;
                }
            };

            // Monitor cache match operations
            Cache.prototype.match = async function(request) {
                const startTime = performance.now();
                try {
                    const response = await originalMatch.call(this, request);
                    const duration = performance.now() - startTime;
                    
                    window.swPerformance.trackCacheOperation('match', request.url || request, duration, !!response);
                    return response;
                } catch (error) {
                    const duration = performance.now() - startTime;
                    window.swPerformance.trackCacheOperation('match', request.url || request, duration, false);
                    throw error;
                }
            };
        }
    }

    setupCoreWebVitalsTracking() {
        // Track improvements in Core Web Vitals due to service worker
        if (window.performanceAnalytics) {
            const originalAddMetric = window.performanceAnalytics.addMetric;
            
            window.performanceAnalytics.addMetric = (metric) => {
                // Call original method
                originalAddMetric.call(window.performanceAnalytics, metric);
                
                // Analyze if service worker contributed to performance
                this.analyzeCoreWebVitalImpact(metric);
            };
        }
    }

    scheduleMetricsReporting() {
        // Report metrics every 5 minutes
        setInterval(() => {
            this.reportMetrics();
        }, 5 * 60 * 1000);

        // Report on page unload
        window.addEventListener('beforeunload', () => {
            this.reportMetrics(true);
        });

        // Report when page becomes hidden
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.reportMetrics();
            }
        });
    }

    // =====================================
    // TRACKING METHODS
    // =====================================

    trackServiceWorkerReady() {
        const readyTime = performance.now() - this.startTime;
        
        this.logMetric('sw_ready_time', readyTime);
        
        if (window.gtag) {
            gtag('event', 'sw_ready', {
                event_category: 'Performance',
                value: Math.round(readyTime)
            });
        }
    }

    trackServiceWorkerUpdate() {
        this.logMetric('sw_update_detected', 1);
        
        if (window.gtag) {
            gtag('event', 'sw_update', {
                event_category: 'Performance'
            });
        }
    }

    trackCachePerformance(type, metrics) {
        const cacheHitRate = this.metrics.cacheHits / (this.metrics.cacheHits + this.metrics.cacheMisses);
        
        this.logMetric(`cache_${type}`, 1);
        this.logMetric('cache_hit_rate', cacheHitRate);
        
        // Track cache performance by content type
        if (metrics?.contentType) {
            this.logMetric(`cache_${type}_${metrics.contentType}`, 1);
        }
    }

    trackOfflineUsage(metrics) {
        this.logMetric('offline_request', 1);
        
        if (metrics?.resourceType) {
            this.logMetric(`offline_${metrics.resourceType}`, 1);
        }
        
        if (window.gtag) {
            gtag('event', 'offline_usage', {
                event_category: 'PWA',
                event_label: metrics?.resourceType || 'unknown'
            });
        }
    }

    trackSyncPerformance(metrics) {
        this.logMetric('background_sync', 1);
        
        if (metrics?.syncType) {
            this.logMetric(`sync_${metrics.syncType}`, 1);
        }
        
        if (metrics?.duration) {
            this.logMetric('sync_duration', metrics.duration);
        }
    }

    trackServiceWorkerError(metrics) {
        this.logMetric('sw_error', 1);
        
        console.error('[SW Performance] Service Worker error:', metrics);
        
        if (window.gtag) {
            gtag('event', 'sw_error', {
                event_category: 'Error',
                event_label: metrics?.error || 'unknown'
            });
        }
    }

    trackFetchPerformance(url, duration, status, result) {
        // Only track meaningful requests (not chrome-extension, etc.)
        if (!url || typeof url !== 'string' || !url.startsWith('http')) {
            return;
        }

        this.logMetric('fetch_duration', duration);
        this.logMetric(`fetch_${result}`, 1);
        
        // Track by resource type
        const resourceType = this.getResourceType(url);
        this.logMetric(`fetch_${resourceType}_duration`, duration);
        
        // Track slow requests
        if (duration > 1000) {
            this.logMetric('slow_fetch', 1);
            console.warn(`[SW Performance] Slow fetch detected: ${url} took ${duration}ms`);
        }
    }

    trackCacheOperation(operation, resource, duration, success) {
        this.logMetric(`cache_${operation}_duration`, duration);
        this.logMetric(`cache_${operation}_${success ? 'success' : 'failure'}`, 1);
        
        if (duration > 100) {
            console.warn(`[SW Performance] Slow cache ${operation}: ${resource} took ${duration}ms`);
        }
    }

    analyzeCoreWebVitalImpact(metric) {
        // Analyze if service worker contributed to Core Web Vitals improvements
        if (metric.name === 'LCP' && metric.value < 2500) {
            this.logMetric('lcp_good_with_sw', 1);
        }
        
        if (metric.name === 'FID' && metric.value < 100) {
            this.logMetric('fid_good_with_sw', 1);
        }
        
        if (metric.name === 'CLS' && metric.value < 0.1) {
            this.logMetric('cls_good_with_sw', 1);
        }
    }

    analyzeServiceWorkerPerformance(metrics) {
        // Analyze comprehensive service worker performance data
        if (metrics.cacheHitRate) {
            this.logMetric('sw_cache_hit_rate', metrics.cacheHitRate);
        }
        
        if (metrics.averageResponseTime) {
            this.logMetric('sw_avg_response_time', metrics.averageResponseTime);
        }
        
        if (metrics.offlineCapability) {
            this.logMetric('sw_offline_capability', metrics.offlineCapability);
        }
    }

    // =====================================
    // UTILITY METHODS
    // =====================================

    getResourceType(url) {
        if (url.includes('.css')) return 'css';
        if (url.includes('.js')) return 'js';
        if (url.match(/\.(jpg|jpeg|png|gif|webp|svg)$/i)) return 'image';
        if (url.match(/\.(woff|woff2|ttf|eot)$/i)) return 'font';
        if (url.includes('/api/')) return 'api';
        return 'html';
    }

    logMetric(name, value) {
        // Store in local metrics object
        if (!this.metrics[name]) {
            this.metrics[name] = [];
        }
        
        this.metrics[name].push({
            value,
            timestamp: Date.now()
        });
        
        // Keep only last 100 entries per metric
        if (this.metrics[name].length > 100) {
            this.metrics[name] = this.metrics[name].slice(-100);
        }
    }

    // =====================================
    // REPORTING
    // =====================================

    reportMetrics(isBeforeUnload = false) {
        const report = this.generatePerformanceReport();
        
        // Send to analytics endpoint
        this.sendMetricsToServer(report, isBeforeUnload);
        
        // Log summary to console
        console.log('[SW Performance] Metrics Report:', report.summary);
    }

    generatePerformanceReport() {
        const now = Date.now();
        const sessionDuration = now - this.startTime;
        
        // Calculate cache hit rate
        const totalCacheRequests = this.metrics.cacheHits + this.metrics.cacheMisses;
        const cacheHitRate = totalCacheRequests > 0 ? this.metrics.cacheHits / totalCacheRequests : 0;
        
        // Calculate average fetch duration
        const fetchDurations = this.metrics.fetch_duration || [];
        const avgFetchDuration = fetchDurations.length > 0 
            ? fetchDurations.reduce((sum, item) => sum + item.value, 0) / fetchDurations.length 
            : 0;
        
        const summary = {
            sessionDuration,
            cacheHitRate: Math.round(cacheHitRate * 100) / 100,
            totalCacheHits: this.metrics.cacheHits,
            totalCacheMisses: this.metrics.cacheMisses,
            offlineRequests: this.metrics.offlineRequests,
            syncOperations: this.metrics.syncOperations,
            errors: this.metrics.errors,
            avgFetchDuration: Math.round(avgFetchDuration),
            timestamp: now
        };
        
        return {
            summary,
            detailed: this.metrics,
            userAgent: navigator.userAgent,
            connection: navigator.connection ? {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                saveData: navigator.connection.saveData
            } : null
        };
    }

    async sendMetricsToServer(report, isBeforeUnload = false) {
        try {
            const method = isBeforeUnload ? 'sendBeacon' : 'fetch';
            
            if (method === 'sendBeacon' && navigator.sendBeacon) {
                navigator.sendBeacon('/api/sw-performance-metrics/', JSON.stringify(report));
            } else {
                fetch('/api/sw-performance-metrics/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(report),
                    keepalive: isBeforeUnload
                }).catch(error => {
                    console.warn('[SW Performance] Failed to send metrics:', error);
                });
            }
        } catch (error) {
            console.warn('[SW Performance] Error sending metrics to server:', error);
        }
    }

    // =====================================
    // PUBLIC API
    // =====================================

    getCacheHitRate() {
        const total = this.metrics.cacheHits + this.metrics.cacheMisses;
        return total > 0 ? this.metrics.cacheHits / total : 0;
    }

    getOfflineUsageCount() {
        return this.metrics.offlineRequests;
    }

    getSyncOperationCount() {
        return this.metrics.syncOperations;
    }

    getErrorCount() {
        return this.metrics.errors;
    }

    getMetrics() {
        return this.generatePerformanceReport();
    }

    reset() {
        this.metrics = {
            cacheHits: 0,
            cacheMisses: 0,
            offlineRequests: 0,
            syncOperations: 0,
            errors: 0
        };
        this.startTime = performance.now();
        console.log('[SW Performance] Metrics reset');
    }
}

// Initialize Service Worker Performance Monitoring
let swPerformance;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        swPerformance = new ServiceWorkerPerformance();
    });
} else {
    swPerformance = new ServiceWorkerPerformance();
}

// Export for global access
window.swPerformance = swPerformance;