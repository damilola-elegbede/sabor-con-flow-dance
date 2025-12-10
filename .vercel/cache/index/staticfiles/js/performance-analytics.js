/**
 * Advanced Performance Analytics and Core Web Vitals Monitoring
 * SPEC_04 Group D Implementation
 */

class PerformanceAnalytics {
    constructor(options = {}) {
        this.options = {
            enableRealUserMonitoring: true,
            enableResourceTiming: true,
            enableNavigationTiming: true,
            enableCoreWebVitals: true,
            enableNetworkInfo: true,
            sampleRate: 1.0, // 100% sampling by default
            reportingEndpoint: '/api/performance-metrics/',
            batchSize: 10,
            flushInterval: 30000, // 30 seconds
            ...options
        };

        this.metrics = {
            navigation: {},
            resources: [],
            coreWebVitals: {},
            userTiming: [],
            networkInfo: {},
            customMetrics: {},
            errors: []
        };

        this.metricsBatch = [];
        this.observers = [];
        this.startTime = performance.now();

        this.init();
    }

    init() {
        if (Math.random() > this.options.sampleRate) {
            console.log('📊 Performance monitoring disabled (sampling)');
            return;
        }

        console.log('📊 Performance Analytics initialized');

        // Setup Core Web Vitals monitoring
        if (this.options.enableCoreWebVitals) {
            this.setupCoreWebVitals();
        }

        // Setup navigation timing
        if (this.options.enableNavigationTiming) {
            this.setupNavigationTiming();
        }

        // Setup resource timing
        if (this.options.enableResourceTiming) {
            this.setupResourceTiming();
        }

        // Setup network information
        if (this.options.enableNetworkInfo) {
            this.setupNetworkInfo();
        }

        // Setup error tracking
        this.setupErrorTracking();

        // Setup custom metrics
        this.setupCustomMetrics();

        // Setup automatic reporting
        this.setupAutomaticReporting();

        // Setup visibility change handling
        this.setupVisibilityTracking();
    }

    setupCoreWebVitals() {
        // Largest Contentful Paint (LCP)
        this.observePerformanceEntries('largest-contentful-paint', (entries) => {
            const lastEntry = entries[entries.length - 1];
            this.metrics.coreWebVitals.lcp = {
                value: lastEntry.startTime,
                element: lastEntry.element?.tagName || 'unknown',
                url: lastEntry.url || '',
                timestamp: Date.now(),
                rating: this.rateLCP(lastEntry.startTime)
            };

            this.addCustomEvent('core_web_vital_lcp', {
                value: lastEntry.startTime,
                rating: this.metrics.coreWebVitals.lcp.rating
            });
        });

        // First Input Delay (FID)
        this.observePerformanceEntries('first-input', (entries) => {
            const lastEntry = entries[entries.length - 1];
            this.metrics.coreWebVitals.fid = {
                value: lastEntry.processingStart - lastEntry.startTime,
                inputType: lastEntry.name,
                timestamp: Date.now(),
                rating: this.rateFID(lastEntry.processingStart - lastEntry.startTime)
            };

            this.addCustomEvent('core_web_vital_fid', {
                value: this.metrics.coreWebVitals.fid.value,
                rating: this.metrics.coreWebVitals.fid.rating
            });
        });

        // Cumulative Layout Shift (CLS)
        let clsValue = 0;
        let clsEntries = [];

        this.observePerformanceEntries('layout-shift', (entries) => {
            entries.forEach(entry => {
                if (!entry.hadRecentInput) {
                    clsValue += entry.value;
                    clsEntries.push(entry);
                }
            });

            this.metrics.coreWebVitals.cls = {
                value: clsValue,
                entries: clsEntries.length,
                timestamp: Date.now(),
                rating: this.rateCLS(clsValue)
            };
        });

        // Time to First Byte (TTFB)
        this.observePerformanceEntries('navigation', (entries) => {
            const navigationEntry = entries[0];
            if (navigationEntry) {
                const ttfb = navigationEntry.responseStart - navigationEntry.requestStart;
                this.metrics.coreWebVitals.ttfb = {
                    value: ttfb,
                    timestamp: Date.now(),
                    rating: this.rateTTFB(ttfb)
                };
            }
        });
    }

    observePerformanceEntries(entryType, callback) {
        try {
            const observer = new PerformanceObserver((list) => {
                callback(list.getEntries());
            });

            observer.observe({ entryTypes: [entryType] });
            this.observers.push(observer);
        } catch (error) {
            console.warn(`Performance Observer not supported for ${entryType}:`, error);
        }
    }

    setupNavigationTiming() {
        window.addEventListener('load', () => {
            const navigation = performance.getEntriesByType('navigation')[0];
            if (navigation) {
                this.metrics.navigation = {
                    dns: navigation.domainLookupEnd - navigation.domainLookupStart,
                    tcp: navigation.connectEnd - navigation.connectStart,
                    ssl: navigation.secureConnectionStart > 0 ? 
                         navigation.connectEnd - navigation.secureConnectionStart : 0,
                    ttfb: navigation.responseStart - navigation.requestStart,
                    download: navigation.responseEnd - navigation.responseStart,
                    dom: navigation.domContentLoadedEventStart - navigation.responseEnd,
                    load: navigation.loadEventStart - navigation.domContentLoadedEventStart,
                    total: navigation.loadEventEnd - navigation.navigationStart,
                    timestamp: Date.now()
                };

                this.addCustomEvent('navigation_timing', this.metrics.navigation);
            }
        });
    }

    setupResourceTiming() {
        // Monitor resource loading performance
        const processResourceEntries = () => {
            const resources = performance.getEntriesByType('resource');
            
            resources.forEach(resource => {
                if (!this.metrics.resources.find(r => r.name === resource.name)) {
                    const resourceMetric = {
                        name: resource.name,
                        type: this.getResourceType(resource.name),
                        size: resource.transferSize || resource.encodedBodySize,
                        duration: resource.responseEnd - resource.startTime,
                        cached: resource.transferSize === 0,
                        timestamp: Date.now()
                    };

                    this.metrics.resources.push(resourceMetric);

                    // Track slow resources
                    if (resourceMetric.duration > 2000) { // 2 seconds
                        this.addCustomEvent('slow_resource', resourceMetric);
                    }
                }
            });
        };

        // Process resources on load and periodically
        window.addEventListener('load', processResourceEntries);
        setInterval(processResourceEntries, 10000); // Every 10 seconds
    }

    setupNetworkInfo() {
        if ('connection' in navigator) {
            const connection = navigator.connection;
            this.metrics.networkInfo = {
                effectiveType: connection.effectiveType,
                downlink: connection.downlink,
                rtt: connection.rtt,
                saveData: connection.saveData,
                timestamp: Date.now()
            };

            // Monitor network changes
            connection.addEventListener('change', () => {
                this.metrics.networkInfo = {
                    effectiveType: connection.effectiveType,
                    downlink: connection.downlink,
                    rtt: connection.rtt,
                    saveData: connection.saveData,
                    timestamp: Date.now()
                };

                this.addCustomEvent('network_change', this.metrics.networkInfo);
            });
        }
    }

    setupErrorTracking() {
        // JavaScript errors
        window.addEventListener('error', (event) => {
            this.metrics.errors.push({
                type: 'javascript',
                message: event.message,
                filename: event.filename,
                line: event.lineno,
                column: event.colno,
                stack: event.error?.stack,
                timestamp: Date.now()
            });
        });

        // Promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.metrics.errors.push({
                type: 'promise_rejection',
                message: event.reason?.message || 'Unhandled promise rejection',
                stack: event.reason?.stack,
                timestamp: Date.now()
            });
        });

        // Resource errors
        window.addEventListener('error', (event) => {
            if (event.target !== window) {
                this.metrics.errors.push({
                    type: 'resource',
                    element: event.target.tagName,
                    source: event.target.src || event.target.href,
                    timestamp: Date.now()
                });
            }
        }, true);
    }

    setupCustomMetrics() {
        // Track page visibility and engagement
        let visibilityStart = Date.now();
        let totalVisibleTime = 0;

        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                totalVisibleTime += Date.now() - visibilityStart;
            } else {
                visibilityStart = Date.now();
            }

            this.metrics.customMetrics.visibleTime = totalVisibleTime;
        });

        // Track scroll depth
        let maxScrollDepth = 0;
        const updateScrollDepth = () => {
            const scrollPercent = Math.round(
                (window.scrollY + window.innerHeight) / document.documentElement.scrollHeight * 100
            );
            maxScrollDepth = Math.max(maxScrollDepth, scrollPercent);
            this.metrics.customMetrics.maxScrollDepth = maxScrollDepth;
        };

        window.addEventListener('scroll', this.throttle(updateScrollDepth, 250));

        // Track click events and interactions
        let interactionCount = 0;
        document.addEventListener('click', (event) => {
            interactionCount++;
            this.metrics.customMetrics.interactions = interactionCount;

            // Track specific UI interactions
            if (event.target.matches('a, button, .btn')) {
                this.addCustomEvent('ui_interaction', {
                    element: event.target.tagName.toLowerCase(),
                    class: event.target.className,
                    text: event.target.textContent?.slice(0, 50)
                });
            }
        });
    }

    setupAutomaticReporting() {
        // Batch and send metrics periodically
        setInterval(() => {
            this.flushMetrics();
        }, this.options.flushInterval);

        // Send metrics before page unload
        window.addEventListener('beforeunload', () => {
            this.flushMetrics(true);
        });

        // Send metrics when page becomes hidden
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.flushMetrics();
            }
        });
    }

    setupVisibilityTracking() {
        let pageVisible = !document.hidden;
        let lastVisibilityChange = Date.now();

        document.addEventListener('visibilitychange', () => {
            const now = Date.now();
            const duration = now - lastVisibilityChange;

            this.addCustomEvent('visibility_change', {
                previousState: pageVisible ? 'visible' : 'hidden',
                currentState: document.hidden ? 'hidden' : 'visible',
                duration: duration
            });

            pageVisible = !document.hidden;
            lastVisibilityChange = now;
        });
    }

    // Rating functions for Core Web Vitals
    rateLCP(value) {
        if (value <= 2500) return 'good';
        if (value <= 4000) return 'needs-improvement';
        return 'poor';
    }

    rateFID(value) {
        if (value <= 100) return 'good';
        if (value <= 300) return 'needs-improvement';
        return 'poor';
    }

    rateCLS(value) {
        if (value <= 0.1) return 'good';
        if (value <= 0.25) return 'needs-improvement';
        return 'poor';
    }

    rateTTFB(value) {
        if (value <= 800) return 'good';
        if (value <= 1800) return 'needs-improvement';
        return 'poor';
    }

    getResourceType(url) {
        if (url.match(/\.(css)$/i)) return 'css';
        if (url.match(/\.(js)$/i)) return 'javascript';
        if (url.match(/\.(png|jpg|jpeg|gif|webp|svg)$/i)) return 'image';
        if (url.match(/\.(woff|woff2|ttf|otf)$/i)) return 'font';
        if (url.match(/\.(mp4|webm|ogg)$/i)) return 'video';
        return 'other';
    }

    addCustomEvent(eventName, data) {
        this.metricsBatch.push({
            type: 'event',
            name: eventName,
            data: data,
            timestamp: Date.now(),
            url: window.location.href,
            userAgent: navigator.userAgent
        });

        if (this.metricsBatch.length >= this.options.batchSize) {
            this.flushMetrics();
        }
    }

    markUserTiming(name, detail = {}) {
        const now = performance.now();
        this.metrics.userTiming.push({
            name: name,
            startTime: now,
            detail: detail,
            timestamp: Date.now()
        });

        // Also use native performance API if available
        if (performance.mark) {
            performance.mark(name);
        }
    }

    measureUserTiming(name, startMark, endMark) {
        if (performance.measure) {
            try {
                performance.measure(name, startMark, endMark);
                const measure = performance.getEntriesByName(name, 'measure').pop();
                
                this.addCustomEvent('user_timing', {
                    name: name,
                    duration: measure.duration,
                    startTime: measure.startTime
                });
            } catch (error) {
                console.warn('Failed to measure user timing:', error);
            }
        }
    }

    async flushMetrics(sync = false) {
        if (this.metricsBatch.length === 0) return;

        const payload = {
            batch: [...this.metricsBatch],
            session: this.getSessionInfo(),
            metrics: this.metrics,
            timestamp: Date.now()
        };

        this.metricsBatch = [];

        try {
            if (sync && navigator.sendBeacon) {
                // Use sendBeacon for synchronous sending during page unload
                navigator.sendBeacon(
                    this.options.reportingEndpoint,
                    JSON.stringify(payload)
                );
            } else {
                // Use fetch for asynchronous sending
                await fetch(this.options.reportingEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
            }

            console.log('📊 Performance metrics sent successfully');
        } catch (error) {
            console.error('❌ Failed to send performance metrics:', error);
            // Re-add metrics to batch for retry
            this.metricsBatch.unshift(...payload.batch);
        }
    }

    getSessionInfo() {
        return {
            url: window.location.href,
            referrer: document.referrer,
            userAgent: navigator.userAgent,
            screen: {
                width: screen.width,
                height: screen.height,
                devicePixelRatio: window.devicePixelRatio
            },
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            connection: this.metrics.networkInfo
        };
    }

    throttle(func, delay) {
        let timeoutId;
        let lastExecTime = 0;
        return function (...args) {
            const currentTime = Date.now();
            
            if (currentTime - lastExecTime > delay) {
                func.apply(this, args);
                lastExecTime = currentTime;
            } else {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => {
                    func.apply(this, args);
                    lastExecTime = Date.now();
                }, delay - (currentTime - lastExecTime));
            }
        };
    }

    // Public API
    getMetrics() {
        return { ...this.metrics };
    }

    getCoreWebVitals() {
        return { ...this.metrics.coreWebVitals };
    }

    generateReport() {
        const report = {
            summary: {
                loadTime: this.metrics.navigation.total || 0,
                resources: this.metrics.resources.length,
                errors: this.metrics.errors.length,
                coreWebVitals: this.metrics.coreWebVitals
            },
            recommendations: this.generateRecommendations(),
            timestamp: Date.now()
        };

        console.table(report.summary);
        console.log('💡 Performance Recommendations:', report.recommendations);

        return report;
    }

    generateRecommendations() {
        const recommendations = [];
        const { lcp, fid, cls, ttfb } = this.metrics.coreWebVitals;

        if (lcp && lcp.rating !== 'good') {
            recommendations.push(`Improve LCP: Current ${lcp.value}ms, target <2500ms`);
        }

        if (fid && fid.rating !== 'good') {
            recommendations.push(`Improve FID: Current ${fid.value}ms, target <100ms`);
        }

        if (cls && cls.rating !== 'good') {
            recommendations.push(`Improve CLS: Current ${cls.value}, target <0.1`);
        }

        if (ttfb && ttfb.rating !== 'good') {
            recommendations.push(`Improve TTFB: Current ${ttfb.value}ms, target <800ms`);
        }

        // Resource-based recommendations
        const slowResources = this.metrics.resources.filter(r => r.duration > 2000);
        if (slowResources.length > 0) {
            recommendations.push(`Optimize ${slowResources.length} slow-loading resources`);
        }

        const largeResources = this.metrics.resources.filter(r => r.size > 500000); // 500KB
        if (largeResources.length > 0) {
            recommendations.push(`Compress ${largeResources.length} large resources`);
        }

        return recommendations;
    }

    destroy() {
        this.observers.forEach(observer => observer.disconnect());
        this.flushMetrics(true);
    }
}

// Initialize Performance Analytics
window.addEventListener('DOMContentLoaded', () => {
    window.performanceAnalytics = new PerformanceAnalytics({
        enableRealUserMonitoring: true,
        enableCoreWebVitals: true,
        sampleRate: 1.0,
        flushInterval: 30000
    });

    // Export to global scope for debugging
    window.getPerformanceReport = () => window.performanceAnalytics.generateReport();
    window.getPerformanceMetrics = () => window.performanceAnalytics.getMetrics();
});