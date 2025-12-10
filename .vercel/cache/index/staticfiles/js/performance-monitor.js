/**
 * Performance Monitoring for Core Web Vitals
 * Tracks LCP, FID, CLS and other metrics
 */

(function() {
    'use strict';

    // Configuration
    const DEBUG = true; // Set to false in production
    const METRICS_ENDPOINT = '/api/metrics'; // Endpoint to send metrics

    // Store performance metrics
    const metrics = {
        LCP: null,
        FID: null,
        CLS: null,
        FCP: null,
        TTFB: null,
        INP: null,
        loadTime: null,
        domReady: null
    };

    /**
     * Log performance metric
     */
    function logMetric(name, value, rating) {
        if (DEBUG) {
            const color = rating === 'good' ? 'green' : rating === 'needs-improvement' ? 'orange' : 'red';
            console.log(`%c[Performance] ${name}: ${value}ms (${rating})`, `color: ${color}`);
        }
        
        metrics[name] = { value, rating, timestamp: Date.now() };
    }

    /**
     * Get rating for Core Web Vitals
     */
    function getRating(metric, value) {
        const thresholds = {
            LCP: { good: 2500, poor: 4000 },
            FID: { good: 100, poor: 300 },
            CLS: { good: 0.1, poor: 0.25 },
            FCP: { good: 1800, poor: 3000 },
            TTFB: { good: 800, poor: 1800 },
            INP: { good: 200, poor: 500 }
        };

        const threshold = thresholds[metric];
        if (!threshold) return 'unknown';

        if (value <= threshold.good) return 'good';
        if (value <= threshold.poor) return 'needs-improvement';
        return 'poor';
    }

    /**
     * Observe Largest Contentful Paint (LCP)
     */
    function observeLCP() {
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    const value = lastEntry.renderTime || lastEntry.loadTime;
                    const rating = getRating('LCP', value);
                    logMetric('LCP', value, rating);
                    
                    // Display warning if LCP is poor
                    if (rating === 'poor' && DEBUG) {
                        console.warn('⚠️ LCP is above 4s. Consider optimizing large images or render-blocking resources.');
                    }
                });
                observer.observe({ entryTypes: ['largest-contentful-paint'] });
            } catch (e) {
                console.error('LCP observation failed:', e);
            }
        }
    }

    /**
     * Observe First Input Delay (FID)
     */
    function observeFID() {
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    entries.forEach((entry) => {
                        const value = entry.processingStart - entry.startTime;
                        const rating = getRating('FID', value);
                        logMetric('FID', value, rating);
                        
                        if (rating === 'poor' && DEBUG) {
                            console.warn('⚠️ FID is above 300ms. Consider optimizing JavaScript execution.');
                        }
                    });
                });
                observer.observe({ entryTypes: ['first-input'] });
            } catch (e) {
                console.error('FID observation failed:', e);
            }
        }
    }

    /**
     * Observe Cumulative Layout Shift (CLS)
     */
    function observeCLS() {
        if ('PerformanceObserver' in window) {
            let clsValue = 0;
            let clsEntries = [];

            try {
                const observer = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    entries.forEach((entry) => {
                        if (!entry.hadRecentInput) {
                            clsValue += entry.value;
                            clsEntries.push(entry);
                        }
                    });
                    
                    const rating = getRating('CLS', clsValue);
                    logMetric('CLS', clsValue.toFixed(3), rating);
                    
                    if (rating === 'poor' && DEBUG) {
                        console.warn('⚠️ CLS is above 0.25. Consider adding dimensions to images/videos or avoiding dynamic content insertion.');
                    }
                });
                observer.observe({ entryTypes: ['layout-shift'] });
            } catch (e) {
                console.error('CLS observation failed:', e);
            }
        }
    }

    /**
     * Observe First Contentful Paint (FCP)
     */
    function observeFCP() {
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    entries.forEach((entry) => {
                        const value = entry.startTime;
                        const rating = getRating('FCP', value);
                        logMetric('FCP', value, rating);
                    });
                });
                observer.observe({ entryTypes: ['paint'] });
            } catch (e) {
                // Use fallback method
                if (window.performance && window.performance.getEntriesByType) {
                    const paintEntries = performance.getEntriesByType('paint');
                    paintEntries.forEach((entry) => {
                        if (entry.name === 'first-contentful-paint') {
                            const rating = getRating('FCP', entry.startTime);
                            logMetric('FCP', entry.startTime, rating);
                        }
                    });
                }
            }
        }
    }

    /**
     * Measure Time to First Byte (TTFB)
     */
    function measureTTFB() {
        if (window.performance && window.performance.timing) {
            const timing = window.performance.timing;
            const ttfb = timing.responseStart - timing.navigationStart;
            const rating = getRating('TTFB', ttfb);
            logMetric('TTFB', ttfb, rating);
            
            if (rating === 'poor' && DEBUG) {
                console.warn('⚠️ TTFB is above 1.8s. Consider optimizing server response time or using a CDN.');
            }
        }
    }

    /**
     * Measure page load time
     */
    function measureLoadTime() {
        window.addEventListener('load', () => {
            if (window.performance && window.performance.timing) {
                const timing = window.performance.timing;
                const loadTime = timing.loadEventEnd - timing.navigationStart;
                const domReady = timing.domContentLoadedEventEnd - timing.navigationStart;
                
                metrics.loadTime = loadTime;
                metrics.domReady = domReady;
                
                if (DEBUG) {
                    console.log(`%c[Performance] Page Load: ${loadTime}ms`, 'color: blue');
                    console.log(`%c[Performance] DOM Ready: ${domReady}ms`, 'color: blue');
                }
            }
        });
    }

    /**
     * Send metrics to server (optional)
     */
    function sendMetrics() {
        if (METRICS_ENDPOINT && Object.keys(metrics).some(key => metrics[key] !== null)) {
            // Only send if we have metrics and an endpoint configured
            const data = {
                url: window.location.href,
                userAgent: navigator.userAgent,
                timestamp: Date.now(),
                metrics: metrics
            };
            
            // Use sendBeacon if available for reliability
            if (navigator.sendBeacon) {
                navigator.sendBeacon(METRICS_ENDPOINT, JSON.stringify(data));
            } else {
                // Fallback to fetch
                fetch(METRICS_ENDPOINT, {
                    method: 'POST',
                    body: JSON.stringify(data),
                    headers: { 'Content-Type': 'application/json' },
                    keepalive: true
                }).catch(() => {
                    // Silently fail - don't impact user experience
                });
            }
        }
    }

    /**
     * Display performance summary
     */
    function displaySummary() {
        if (DEBUG) {
            setTimeout(() => {
                console.group('%c📊 Performance Summary', 'font-size: 14px; font-weight: bold; color: blue');
                
                // Core Web Vitals
                console.group('Core Web Vitals');
                if (metrics.LCP) console.log(`LCP: ${metrics.LCP.value}ms (${metrics.LCP.rating})`);
                if (metrics.FID) console.log(`FID: ${metrics.FID.value}ms (${metrics.FID.rating})`);
                if (metrics.CLS) console.log(`CLS: ${metrics.CLS.value} (${metrics.CLS.rating})`);
                console.groupEnd();
                
                // Other metrics
                console.group('Additional Metrics');
                if (metrics.FCP) console.log(`FCP: ${metrics.FCP.value}ms (${metrics.FCP.rating})`);
                if (metrics.TTFB) console.log(`TTFB: ${metrics.TTFB.value}ms (${metrics.TTFB.rating})`);
                if (metrics.loadTime) console.log(`Total Load Time: ${metrics.loadTime}ms`);
                if (metrics.domReady) console.log(`DOM Ready: ${metrics.domReady}ms`);
                console.groupEnd();
                
                // Recommendations
                const recommendations = [];
                if (metrics.LCP && metrics.LCP.rating !== 'good') {
                    recommendations.push('• Optimize images and videos');
                    recommendations.push('• Reduce render-blocking resources');
                }
                if (metrics.FID && metrics.FID.rating !== 'good') {
                    recommendations.push('• Reduce JavaScript execution time');
                    recommendations.push('• Break up long tasks');
                }
                if (metrics.CLS && metrics.CLS.rating !== 'good') {
                    recommendations.push('• Add size attributes to images/videos');
                    recommendations.push('• Avoid inserting content dynamically');
                }
                
                if (recommendations.length > 0) {
                    console.group('💡 Recommendations');
                    recommendations.forEach(rec => console.log(rec));
                    console.groupEnd();
                }
                
                console.groupEnd();
            }, 5000); // Wait 5 seconds to ensure all metrics are collected
        }
    }

    /**
     * Initialize performance monitoring
     */
    function init() {
        // Start observers
        observeLCP();
        observeFID();
        observeCLS();
        observeFCP();
        
        // Measure additional metrics
        measureTTFB();
        measureLoadTime();
        
        // Display summary after page load
        window.addEventListener('load', () => {
            displaySummary();
            
            // Send metrics when page is about to unload
            window.addEventListener('beforeunload', sendMetrics);
        });
        
        // Log initialization
        if (DEBUG) {
            console.log('%c✅ Performance monitoring initialized', 'color: green; font-weight: bold');
        }
    }

    // Start monitoring when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose API for manual checks
    window.PerformanceMonitor = {
        getMetrics: () => metrics,
        displaySummary: displaySummary,
        sendMetrics: sendMetrics
    };

})();