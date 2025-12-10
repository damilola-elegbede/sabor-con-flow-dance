/*!
 * Advanced Async CSS Loader with Performance Optimization
 * SPEC_06 Group A Task 2 - Critical CSS Implementation
 * 
 * Features:
 * - Intelligent CSS prioritization
 * - Performance monitoring
 * - Network-aware loading
 * - Fallback support
 * - Core Web Vitals optimization
 */

(function(window, document) {
    'use strict';
    
    // Configuration
    var config = {
        // Performance budgets (ms)
        budgets: {
            firstPaint: 1000,      // Target: <1s first paint
            firstContentful: 1500,  // Target: <1.5s FCP
            largestContentful: 2000 // Target: <2s LCP
        },
        
        // CSS loading priorities
        priorities: {
            critical: 0,    // Inline critical CSS (already loaded)
            high: 1,        // Navigation, hero styles
            medium: 2,      // Main content styles
            low: 3          // Non-essential styles
        },
        
        // Network-aware loading
        networkOptimization: true,
        
        // Debugging
        debug: false
    };
    
    // Performance tracking
    var performance = {
        startTime: window.performance ? window.performance.now() : Date.now(),
        metrics: {},
        events: []
    };
    
    // CSS loading queue
    var loadingQueue = {
        high: [],
        medium: [],
        low: []
    };
    
    // Loaded files tracking
    var loadedFiles = new Set();
    var loadingFiles = new Set();
    
    /**
     * Enhanced CSS Loader Function
     */
    function loadCSS(href, priority, media, attributes) {
        if (loadedFiles.has(href) || loadingFiles.has(href)) {
            log('CSS already loaded or loading:', href);
            return null;
        }
        
        loadingFiles.add(href);
        
        var link = document.createElement('link');
        var startTime = getTime();
        
        // Set basic attributes
        link.rel = 'stylesheet';
        link.href = href;
        link.media = media || 'all';
        
        // Set additional attributes
        if (attributes) {
            Object.keys(attributes).forEach(function(key) {
                link.setAttribute(key, attributes[key]);
            });
        }
        
        // Add priority and performance attributes
        if (priority === 'high') {
            link.setAttribute('importance', 'high');
        } else if (priority === 'low') {
            link.setAttribute('importance', 'low');
        }
        
        // Performance tracking
        var onLoad = function() {
            var loadTime = getTime() - startTime;
            loadingFiles.delete(href);
            loadedFiles.add(href);
            
            log('CSS loaded:', href, 'in', loadTime + 'ms', 'Priority:', priority);
            
            // Track performance
            trackCSSLoad(href, loadTime, priority);
            
            // Check if all CSS in priority group is loaded
            checkPriorityGroupComplete(priority);
            
            // Cleanup
            link.removeEventListener('load', onLoad);
            link.removeEventListener('error', onError);
        };
        
        var onError = function() {
            loadingFiles.delete(href);
            log('CSS failed to load:', href);
            
            // Track error
            trackEvent('css_load_error', {
                url: href,
                priority: priority
            });
            
            // Cleanup
            link.removeEventListener('load', onLoad);
            link.removeEventListener('error', onError);
        };
        
        // Event listeners
        link.addEventListener('load', onLoad);
        link.addEventListener('error', onError);
        
        // Insert into DOM
        var insertionPoint = getInsertionPoint();
        insertionPoint.parentNode.insertBefore(link, insertionPoint.nextSibling);
        
        return link;
    }
    
    /**
     * Smart CSS loading with priority and network awareness
     */
    function loadCSSWithPriority(cssFiles) {
        // Sort files by priority
        var prioritizedFiles = {
            high: cssFiles.filter(function(f) { return f.priority === 'high'; }),
            medium: cssFiles.filter(function(f) { return f.priority === 'medium'; }),
            low: cssFiles.filter(function(f) { return f.priority === 'low'; })
        };
        
        // Network-aware loading strategy
        var connection = getNetworkInfo();
        var loadingStrategy = getLoadingStrategy(connection);
        
        log('Loading strategy:', loadingStrategy, 'Connection:', connection);
        
        // Load high priority CSS immediately
        loadPriorityGroup(prioritizedFiles.high, 0);
        
        // Load medium priority CSS with delay based on network
        setTimeout(function() {
            loadPriorityGroup(prioritizedFiles.medium, loadingStrategy.mediumDelay);
        }, loadingStrategy.mediumDelay);
        
        // Load low priority CSS after critical content
        setTimeout(function() {
            loadPriorityGroup(prioritizedFiles.low, loadingStrategy.lowDelay);
        }, loadingStrategy.lowDelay);
    }
    
    /**
     * Load a group of CSS files with staggered timing
     */
    function loadPriorityGroup(files, baseDelay) {
        files.forEach(function(file, index) {
            setTimeout(function() {
                loadCSS(file.url, file.priority, file.media || 'all', file.attributes);
            }, baseDelay + (index * 50)); // Stagger by 50ms
        });
    }
    
    /**
     * Get network-aware loading strategy
     */
    function getLoadingStrategy(connection) {
        var strategies = {
            'slow-2g': { mediumDelay: 1000, lowDelay: 3000 },
            '2g': { mediumDelay: 800, lowDelay: 2500 },
            '3g': { mediumDelay: 400, lowDelay: 1500 },
            '4g': { mediumDelay: 200, lowDelay: 800 },
            'fast': { mediumDelay: 100, lowDelay: 500 }
        };
        
        return strategies[connection.effectiveType] || strategies['4g'];
    }
    
    /**
     * Get network information
     */
    function getNetworkInfo() {
        var connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        
        if (connection) {
            return {
                effectiveType: connection.effectiveType || '4g',
                saveData: connection.saveData || false,
                downlink: connection.downlink || 10
            };
        }
        
        // Fallback estimation based on user agent
        return {
            effectiveType: '4g',
            saveData: false,
            downlink: 10
        };
    }
    
    /**
     * Check if all CSS in a priority group is loaded
     */
    function checkPriorityGroupComplete(priority) {
        var groupFiles = Array.from(loadingFiles).filter(function(href) {
            return href.includes(priority) || (priority === 'high' && 
                   (href.includes('navigation') || href.includes('hero')));
        });
        
        if (groupFiles.length === 0) {
            trackEvent('priority_group_complete', { priority: priority });
            
            if (priority === 'high') {
                dispatchEvent('criticalCSSLoaded');
            } else if (priority === 'low' && loadingFiles.size === 0) {
                dispatchEvent('allCSSLoaded');
            }
        }
    }
    
    /**
     * Get optimal insertion point for CSS
     */
    function getInsertionPoint() {
        // Try to insert after the last stylesheet
        var stylesheets = document.querySelectorAll('link[rel="stylesheet"], style');
        if (stylesheets.length > 0) {
            return stylesheets[stylesheets.length - 1];
        }
        
        // Fallback to head
        var head = document.head || document.getElementsByTagName('head')[0];
        return head.lastChild;
    }
    
    /**
     * Performance tracking
     */
    function trackCSSLoad(url, loadTime, priority) {
        performance.events.push({
            type: 'css_load',
            url: url,
            loadTime: loadTime,
            priority: priority,
            timestamp: getTime()
        });
        
        // Track with external analytics if available
        if (window.performanceAnalytics) {
            window.performanceAnalytics.addCustomEvent('css_load', {
                url: url,
                loadTime: loadTime,
                priority: priority
            });
        }
    }
    
    /**
     * Track custom events
     */
    function trackEvent(eventType, data) {
        performance.events.push({
            type: eventType,
            data: data,
            timestamp: getTime()
        });
        
        if (window.performanceAnalytics) {
            window.performanceAnalytics.addCustomEvent(eventType, data);
        }
    }
    
    /**
     * Dispatch custom DOM events
     */
    function dispatchEvent(eventName, detail) {
        var event = new CustomEvent(eventName, {
            detail: detail || {},
            bubbles: true,
            cancelable: false
        });
        
        document.dispatchEvent(event);
        log('Event dispatched:', eventName, detail);
    }
    
    /**
     * Get high-resolution timestamp
     */
    function getTime() {
        return window.performance ? window.performance.now() : Date.now();
    }
    
    /**
     * Debug logging
     */
    function log() {
        if (config.debug && window.console) {
            console.log.apply(console, ['[CSS-Loader]'].concat(Array.prototype.slice.call(arguments)));
        }
    }
    
    /**
     * Performance monitoring and reporting
     */
    function setupPerformanceMonitoring() {
        // Core Web Vitals monitoring
        if ('PerformanceObserver' in window) {
            // First Paint & First Contentful Paint
            var paintObserver = new PerformanceObserver(function(list) {
                list.getEntries().forEach(function(entry) {
                    performance.metrics[entry.name.replace('-', '_')] = entry.startTime;
                    
                    if (entry.name === 'first-contentful-paint') {
                        checkPerformanceTarget('firstContentful', entry.startTime);
                    }
                });
            });
            paintObserver.observe({ entryTypes: ['paint'] });
            
            // Largest Contentful Paint
            var lcpObserver = new PerformanceObserver(function(list) {
                var entries = list.getEntries();
                var lastEntry = entries[entries.length - 1];
                performance.metrics.largest_contentful_paint = lastEntry.startTime;
                checkPerformanceTarget('largestContentful', lastEntry.startTime);
            });
            lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
        }
        
        // Track when critical CSS is effective
        document.addEventListener('criticalCSSLoaded', function() {
            var time = getTime() - performance.startTime;
            performance.metrics.critical_css_effective = time;
            log('Critical CSS effective at:', time + 'ms');
        });
        
        // Final performance report
        window.addEventListener('load', function() {
            setTimeout(generatePerformanceReport, 1000);
        });
    }
    
    /**
     * Check if performance targets are met
     */
    function checkPerformanceTarget(metric, value) {
        var target = config.budgets[metric];
        var passed = value < target;
        
        log('Performance check:', metric, value + 'ms', 'Target:', target + 'ms', passed ? '✅' : '❌');
        
        trackEvent('performance_check', {
            metric: metric,
            value: value,
            target: target,
            passed: passed
        });
    }
    
    /**
     * Generate comprehensive performance report
     */
    function generatePerformanceReport() {
        var report = {
            loadTime: getTime() - performance.startTime,
            cssFiles: loadedFiles.size,
            metrics: performance.metrics,
            events: performance.events.length,
            targets: {
                firstPaint: performance.metrics.first_paint < config.budgets.firstPaint,
                firstContentful: performance.metrics.first_contentful_paint < config.budgets.firstContentful,
                largestContentful: performance.metrics.largest_contentful_paint < config.budgets.largestContentful
            }
        };
        
        // Log report
        console.group('🎨 CSS Performance Report');
        console.table(report.metrics);
        console.log('CSS Files Loaded:', report.cssFiles);
        console.log('Performance Targets:', report.targets);
        console.groupEnd();
        
        // Expose globally for debugging
        window.cssPerformanceReport = report;
        
        // Track with analytics
        if (window.performanceAnalytics) {
            window.performanceAnalytics.addCustomEvent('css_performance_report', report);
        }
    }
    
    /**
     * Initialize CSS loading system
     */
    function init() {
        log('CSS Async Loader initialized');
        
        // Setup performance monitoring
        setupPerformanceMonitoring();
        
        // Enable debug mode if requested
        if (window.location.search.includes('css-debug')) {
            config.debug = true;
            log('Debug mode enabled');
        }
        
        // Export global interface
        window.CSSLoader = {
            load: loadCSS,
            loadWithPriority: loadCSSWithPriority,
            getReport: function() { return window.cssPerformanceReport; },
            getMetrics: function() { return performance.metrics; },
            config: config
        };
        
        // Mark as ready
        dispatchEvent('cssLoaderReady');
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})(window, document);