/**
 * Image Performance Monitor
 * Tracks Core Web Vitals and image loading performance metrics
 */

class ImagePerformanceMonitor {
    constructor(options = {}) {
        this.options = {
            enableCLS: true,
            enableLCP: true,
            enableFID: true,
            enableTTFB: true,
            reportingEndpoint: null,
            reportingInterval: 30000, // 30 seconds
            enableConsoleLogging: true,
            enableLocalStorage: true,
            ...options
        };
        
        this.metrics = {
            cls: [],
            lcp: null,
            fid: null,
            ttfb: null,
            imageMetrics: {
                totalImages: 0,
                loadedImages: 0,
                failedImages: 0,
                averageLoadTime: 0,
                slowestImage: null,
                fastestImage: null,
                imageLoadTimes: []
            }
        };
        
        this.observers = [];
        this.init();
    }
    
    init() {
        if (!('PerformanceObserver' in window)) {
            console.warn('PerformanceObserver not supported');
            return;
        }
        
        this.setupCoreWebVitals();
        this.setupImageTracking();
        this.setupReporting();
        this.setupEventListeners();
    }
    
    setupCoreWebVitals() {
        // Cumulative Layout Shift (CLS)
        if (this.options.enableCLS) {
            this.observeCLS();
        }
        
        // Largest Contentful Paint (LCP)
        if (this.options.enableLCP) {
            this.observeLCP();
        }
        
        // First Input Delay (FID)
        if (this.options.enableFID) {
            this.observeFID();
        }
        
        // Time to First Byte (TTFB)
        if (this.options.enableTTFB) {
            this.measureTTFB();
        }
    }
    
    observeCLS() {
        try {
            const clsObserver = new PerformanceObserver((entryList) => {
                for (const entry of entryList.getEntries()) {
                    if (!entry.hadRecentInput) {
                        this.metrics.cls.push({
                            value: entry.value,
                            startTime: entry.startTime,
                            sources: entry.sources?.map(source => ({
                                element: source.node?.tagName || 'unknown',
                                className: source.node?.className || '',
                                currentRect: source.currentRect,
                                previousRect: source.previousRect
                            })) || []
                        });
                        
                        this.logMetric('CLS', entry.value);
                    }
                }
            });
            
            clsObserver.observe({ entryTypes: ['layout-shift'] });
            this.observers.push(clsObserver);
        } catch (e) {
            console.warn('CLS monitoring failed:', e);
        }
    }
    
    observeLCP() {
        try {
            const lcpObserver = new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                const lastEntry = entries[entries.length - 1];
                
                this.metrics.lcp = {
                    value: lastEntry.startTime,
                    element: lastEntry.element?.tagName || 'unknown',
                    elementId: lastEntry.element?.id || '',
                    elementClass: lastEntry.element?.className || '',
                    url: lastEntry.url || '',
                    loadTime: lastEntry.loadTime || 0,
                    renderTime: lastEntry.renderTime || 0
                };
                
                this.logMetric('LCP', lastEntry.startTime);
            });
            
            lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
            this.observers.push(lcpObserver);
        } catch (e) {
            console.warn('LCP monitoring failed:', e);
        }
    }
    
    observeFID() {
        try {
            const fidObserver = new PerformanceObserver((entryList) => {
                for (const entry of entryList.getEntries()) {
                    this.metrics.fid = {
                        value: entry.processingStart - entry.startTime,
                        startTime: entry.startTime,
                        processingStart: entry.processingStart,
                        processingEnd: entry.processingEnd
                    };
                    
                    this.logMetric('FID', this.metrics.fid.value);
                }
            });
            
            fidObserver.observe({ entryTypes: ['first-input'] });
            this.observers.push(fidObserver);
        } catch (e) {
            console.warn('FID monitoring failed:', e);
        }
    }
    
    measureTTFB() {
        try {
            const navigationEntries = performance.getEntriesByType('navigation');
            if (navigationEntries.length > 0) {
                const navEntry = navigationEntries[0];
                this.metrics.ttfb = navEntry.responseStart - navEntry.requestStart;
                this.logMetric('TTFB', this.metrics.ttfb);
            }
        } catch (e) {
            console.warn('TTFB measurement failed:', e);
        }
    }
    
    setupImageTracking() {
        // Track resource loading
        try {
            const resourceObserver = new PerformanceObserver((entryList) => {
                for (const entry of entryList.getEntries()) {
                    if (entry.initiatorType === 'img' || 
                        entry.name.match(/\.(jpg|jpeg|png|webp|gif|svg)(\?|$)/i)) {
                        this.trackImageLoad(entry);
                    }
                }
            });
            
            resourceObserver.observe({ entryTypes: ['resource'] });
            this.observers.push(resourceObserver);
        } catch (e) {
            console.warn('Image tracking failed:', e);
        }
        
        // Listen for custom lazy load events
        document.addEventListener('lazyImageLoad', (event) => {
            this.trackLazyImageLoad(event.detail);
        });
    }
    
    trackImageLoad(entry) {
        const loadTime = entry.responseEnd - entry.startTime;
        const imageData = {
            url: entry.name,
            loadTime: loadTime,
            transferSize: entry.transferSize || 0,
            encodedBodySize: entry.encodedBodySize || 0,
            decodedBodySize: entry.decodedBodySize || 0,
            timestamp: Date.now()
        };
        
        this.metrics.imageMetrics.totalImages++;
        this.metrics.imageMetrics.loadedImages++;
        this.metrics.imageMetrics.imageLoadTimes.push(imageData);
        
        // Update fastest/slowest
        if (!this.metrics.imageMetrics.fastestImage || 
            loadTime < this.metrics.imageMetrics.fastestImage.loadTime) {
            this.metrics.imageMetrics.fastestImage = imageData;
        }
        
        if (!this.metrics.imageMetrics.slowestImage || 
            loadTime > this.metrics.imageMetrics.slowestImage.loadTime) {
            this.metrics.imageMetrics.slowestImage = imageData;
        }
        
        // Update average
        this.metrics.imageMetrics.averageLoadTime = 
            this.metrics.imageMetrics.imageLoadTimes.reduce((sum, img) => sum + img.loadTime, 0) / 
            this.metrics.imageMetrics.imageLoadTimes.length;
        
        this.logMetric('Image Load', loadTime, entry.name);
    }
    
    trackLazyImageLoad(detail) {
        if (detail.success) {
            const imageData = {
                element: detail.element.tagName,
                loadTime: detail.loadTime,
                src: detail.element.src,
                lazy: true,
                timestamp: Date.now()
            };
            
            this.metrics.imageMetrics.imageLoadTimes.push(imageData);
            this.logMetric('Lazy Image Load', detail.loadTime, detail.element.src);
        } else {
            this.metrics.imageMetrics.failedImages++;
            this.logMetric('Lazy Image Failed', 0, detail.element.dataset.src);
        }
    }
    
    setupReporting() {
        if (this.options.reportingInterval > 0) {
            setInterval(() => {
                this.reportMetrics();
            }, this.options.reportingInterval);
        }
        
        // Report on page unload
        window.addEventListener('beforeunload', () => {
            this.reportMetrics(true);
        });
        
        // Report on visibility change (for SPAs)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.reportMetrics();
            }
        });
    }
    
    setupEventListeners() {
        // Track image errors
        document.addEventListener('error', (event) => {
            if (event.target.tagName === 'IMG') {
                this.metrics.imageMetrics.failedImages++;
                this.logMetric('Image Error', 0, event.target.src || event.target.dataset.src);
            }
        }, true);
        
        // Track viewport changes
        window.addEventListener('resize', () => {
            this.logMetric('Viewport Resize', window.innerWidth + 'x' + window.innerHeight);
        });
    }
    
    logMetric(name, value, details = '') {
        if (!this.options.enableConsoleLogging) return;
        
        const message = `[Performance] ${name}: ${value}${typeof value === 'number' ? 'ms' : ''}`;
        console.log(message, details ? `(${details})` : '');
    }
    
    reportMetrics(isFinal = false) {
        const report = this.generateReport();
        
        // Save to localStorage
        if (this.options.enableLocalStorage) {
            try {
                localStorage.setItem('imagePerformanceMetrics', JSON.stringify(report));
            } catch (e) {
                console.warn('Failed to save metrics to localStorage:', e);
            }
        }
        
        // Send to reporting endpoint
        if (this.options.reportingEndpoint) {
            this.sendReport(report, isFinal);
        }
        
        // Log summary
        if (this.options.enableConsoleLogging) {
            console.group('Performance Report');
            console.table(this.getMetricsSummary());
            console.groupEnd();
        }
        
        return report;
    }
    
    generateReport() {
        const clsTotal = this.metrics.cls.reduce((sum, entry) => sum + entry.value, 0);
        
        return {
            timestamp: Date.now(),
            url: window.location.href,
            userAgent: navigator.userAgent,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            coreWebVitals: {
                cls: clsTotal,
                lcp: this.metrics.lcp?.value || null,
                fid: this.metrics.fid?.value || null,
                ttfb: this.metrics.ttfb
            },
            imageMetrics: {
                ...this.metrics.imageMetrics,
                successRate: this.metrics.imageMetrics.totalImages > 0 ? 
                    (this.metrics.imageMetrics.loadedImages / this.metrics.imageMetrics.totalImages) * 100 : 0
            }
        };
    }
    
    getMetricsSummary() {
        const clsTotal = this.metrics.cls.reduce((sum, entry) => sum + entry.value, 0);
        
        return {
            'CLS': clsTotal.toFixed(3),
            'LCP (ms)': this.metrics.lcp?.value?.toFixed(0) || 'N/A',
            'FID (ms)': this.metrics.fid?.value?.toFixed(0) || 'N/A',
            'TTFB (ms)': this.metrics.ttfb?.toFixed(0) || 'N/A',
            'Images Loaded': this.metrics.imageMetrics.loadedImages,
            'Images Failed': this.metrics.imageMetrics.failedImages,
            'Avg Load Time (ms)': this.metrics.imageMetrics.averageLoadTime.toFixed(0),
            'Success Rate (%)': this.metrics.imageMetrics.totalImages > 0 ? 
                ((this.metrics.imageMetrics.loadedImages / this.metrics.imageMetrics.totalImages) * 100).toFixed(1) : '0'
        };
    }
    
    async sendReport(report, isFinal) {
        if (!this.options.reportingEndpoint) return;
        
        try {
            const response = await fetch(this.options.reportingEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ...report,
                    isFinal
                }),
                keepalive: isFinal // Ensure final reports are sent even during page unload
            });
            
            if (!response.ok) {
                throw new Error(`Report failed: ${response.status}`);
            }
        } catch (e) {
            console.warn('Failed to send performance report:', e);
        }
    }
    
    // Public API
    getMetrics() {
        return this.metrics;
    }
    
    getReport() {
        return this.generateReport();
    }
    
    getSummary() {
        return this.getMetricsSummary();
    }
    
    clearMetrics() {
        this.metrics = {
            cls: [],
            lcp: null,
            fid: null,
            ttfb: null,
            imageMetrics: {
                totalImages: 0,
                loadedImages: 0,
                failedImages: 0,
                averageLoadTime: 0,
                slowestImage: null,
                fastestImage: null,
                imageLoadTimes: []
            }
        };
    }
    
    destroy() {
        this.observers.forEach(observer => observer.disconnect());
        this.observers = [];
    }
}

// Auto-initialize performance monitoring
document.addEventListener('DOMContentLoaded', () => {
    window.imagePerformanceMonitor = new ImagePerformanceMonitor({
        enableConsoleLogging: true,
        enableLocalStorage: true,
        reportingInterval: 30000
    });
    
    // Expose methods globally for debugging
    window.getPerformanceReport = () => window.imagePerformanceMonitor.getReport();
    window.getPerformanceSummary = () => window.imagePerformanceMonitor.getSummary();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ImagePerformanceMonitor;
}