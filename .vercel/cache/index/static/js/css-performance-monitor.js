/*!
 * CSS Performance Monitor
 * SPEC_06 Group A Task 2 - Critical CSS Performance Monitoring
 * 
 * Comprehensive monitoring for:
 * - Critical CSS loading performance
 * - First Paint / First Contentful Paint
 * - Largest Contentful Paint
 * - CSS loading timeline
 * - Performance budget validation
 * - Real-time performance dashboard
 */

(function(window, document) {
    'use strict';
    
    // Performance configuration
    var config = {
        // Performance targets (milliseconds)
        targets: {
            firstPaint: 1000,           // Sub-1s first paint
            firstContentfulPaint: 1500,  // <1.5s FCP
            largestContentfulPaint: 2000, // <2s LCP
            criticalCSS: 100,           // Critical CSS should be immediate
            totalCSS: 3000              // All CSS loaded within 3s
        },
        
        // Budget monitoring (bytes)
        budgets: {
            critical: 14000,    // 14KB critical CSS
            total: 50000        // 50KB total CSS
        },
        
        // Monitoring options
        enableConsoleReporting: true,
        enableVisualIndicators: true,
        enableAnalytics: true,
        debugMode: false
    };
    
    // Performance state
    var performanceState = {
        startTime: window.performance ? window.performance.now() : Date.now(),
        criticalCSSLoaded: false,
        criticalCSSTime: null,
        allCSSLoaded: false,
        totalCSSTime: null,
        cssFiles: [],
        loadedFiles: new Set(),
        metrics: {},
        budget: {
            critical: 0,
            total: 0
        }
    };
    
    // Performance observers
    var observers = {};
    
    /**
     * Initialize CSS Performance Monitoring
     */
    function init() {
        log('CSS Performance Monitor initialized', config.targets);
        
        // Enable debug mode if requested
        if (window.location.search.includes('css-debug') || window.location.search.includes('perf-debug')) {
            config.debugMode = true;
            config.enableConsoleReporting = true;
            log('Debug mode enabled');
        }
        
        // Initialize observers
        setupPerformanceObservers();
        
        // Monitor critical CSS
        monitorCriticalCSS();
        
        // Setup event listeners
        setupEventListeners();
        
        // Create visual indicators if enabled
        if (config.enableVisualIndicators && config.debugMode) {
            createPerformanceIndicators();
        }
        
        // Setup budget monitoring
        monitorCSSBudgets();
        
        // Start monitoring CSS loading
        startCSSLoadingMonitor();
    }
    
    /**
     * Setup Core Web Vitals observers
     */
    function setupPerformanceObservers() {
        if (!('PerformanceObserver' in window)) {
            log('PerformanceObserver not supported');
            return;
        }
        
        // First Paint and First Contentful Paint
        try {
            observers.paint = new PerformanceObserver(function(list) {
                list.getEntries().forEach(function(entry) {
                    var metricName = entry.name.replace(/-/g, '_');
                    performanceState.metrics[metricName] = entry.startTime;
                    
                    log('🎨 ' + entry.name + ':', entry.startTime.toFixed(1) + 'ms');
                    
                    // Check targets
                    if (entry.name === 'first-paint') {
                        checkTarget('firstPaint', entry.startTime);
                    } else if (entry.name === 'first-contentful-paint') {
                        checkTarget('firstContentfulPaint', entry.startTime);
                    }
                    
                    // Update visual indicators
                    updatePerformanceIndicator(entry.name, entry.startTime);
                    
                    // Track with analytics
                    trackMetric(entry.name, entry.startTime);
                });
            });
            observers.paint.observe({ entryTypes: ['paint'] });
        } catch (e) {
            log('Paint observer setup failed:', e);
        }
        
        // Largest Contentful Paint
        try {
            observers.lcp = new PerformanceObserver(function(list) {
                var entries = list.getEntries();
                var lastEntry = entries[entries.length - 1];
                
                performanceState.metrics.largest_contentful_paint = lastEntry.startTime;
                log('🖼️ Largest Contentful Paint:', lastEntry.startTime.toFixed(1) + 'ms');
                
                checkTarget('largestContentfulPaint', lastEntry.startTime);
                updatePerformanceIndicator('largest-contentful-paint', lastEntry.startTime);
                trackMetric('largest-contentful-paint', lastEntry.startTime);
            });
            observers.lcp.observe({ entryTypes: ['largest-contentful-paint'] });
        } catch (e) {
            log('LCP observer setup failed:', e);
        }
        
        // Layout Shift (for monitoring CSS impact)
        try {
            observers.cls = new PerformanceObserver(function(list) {
                var clsValue = 0;
                list.getEntries().forEach(function(entry) {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                    }
                });
                
                if (clsValue > 0) {
                    performanceState.metrics.cumulative_layout_shift = clsValue;
                    log('📐 Layout Shift detected:', clsValue.toFixed(3));
                    
                    if (clsValue > 0.1) {
                        log('⚠️ High Layout Shift detected (target: <0.1)', clsValue);
                    }
                }
            });
            observers.cls.observe({ entryTypes: ['layout-shift'] });
        } catch (e) {
            log('CLS observer setup failed:', e);
        }
    }
    
    /**
     * Monitor critical CSS loading
     */
    function monitorCriticalCSS() {
        var criticalStart = window.criticalCSSStartTime || performanceState.startTime;
        
        function checkCriticalCSS() {
            if (document.documentElement.classList.contains('critical-css-loaded')) {
                performanceState.criticalCSSLoaded = true;
                performanceState.criticalCSSTime = window.performance.now() - criticalStart;
                
                log('✨ Critical CSS loaded:', performanceState.criticalCSSTime.toFixed(1) + 'ms');
                checkTarget('criticalCSS', performanceState.criticalCSSTime);
                updatePerformanceIndicator('critical-css', performanceState.criticalCSSTime);
                trackMetric('critical-css-loaded', performanceState.criticalCSSTime);
                
                return true;
            }
            return false;
        }
        
        // Check immediately
        if (!checkCriticalCSS()) {
            // Check when DOM is ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', checkCriticalCSS);
            } else {
                // Fallback: assume critical CSS is loaded
                setTimeout(checkCriticalCSS, 0);
            }
        }
    }
    
    /**
     * Setup event listeners for CSS loading
     */
    function setupEventListeners() {
        // Listen for CSS loader events
        document.addEventListener('cssLoaderReady', function() {
            log('📦 CSS Loader ready');
        });
        
        document.addEventListener('allCSSLoaded', function(e) {
            performanceState.allCSSLoaded = true;
            performanceState.totalCSSTime = window.performance.now() - performanceState.startTime;
            
            log('🎯 All CSS loaded:', performanceState.totalCSSTime.toFixed(1) + 'ms');
            checkTarget('totalCSS', performanceState.totalCSSTime);
            updatePerformanceIndicator('all-css', performanceState.totalCSSTime);
            trackMetric('all-css-loaded', performanceState.totalCSSTime);
            
            // Generate final report
            setTimeout(generatePerformanceReport, 100);
        });
        
        // Monitor individual CSS file loads
        document.addEventListener('cssFileLoaded', function(e) {
            if (e.detail && e.detail.url) {
                performanceState.cssFiles.push({
                    url: e.detail.url,
                    loadTime: e.detail.loadTime,
                    priority: e.detail.priority,
                    timestamp: window.performance.now()
                });
                
                performanceState.loadedFiles.add(e.detail.url);
                log('📄 CSS file loaded:', e.detail.url, '(' + e.detail.loadTime.toFixed(1) + 'ms)');
            }
        });
        
        // Window load event for final metrics
        window.addEventListener('load', function() {
            setTimeout(function() {
                generatePerformanceReport();
                
                if (config.enableVisualIndicators && config.debugMode) {
                    showPerformanceSummary();
                }
            }, 1000);
        });
    }
    
    /**
     * Monitor CSS budgets
     */
    function monitorCSSBudgets() {
        // This would typically be populated by the build system
        // For now, we'll estimate based on file sizes if available
        
        function estimateCSSSize() {
            var totalSize = 0;
            var criticalSize = 0;
            
            // Get CSS from style tags
            var styleTags = document.querySelectorAll('style');
            styleTags.forEach(function(style) {
                var size = style.textContent.length;
                totalSize += size;
                
                if (style.id === 'critical-css') {
                    criticalSize = size;
                }
            });
            
            performanceState.budget.critical = criticalSize;
            performanceState.budget.total = totalSize;
            
            log('💰 Estimated CSS size - Critical:', criticalSize + 'B, Total:', totalSize + 'B');
            
            // Check budgets
            if (criticalSize > config.budgets.critical) {
                log('⚠️ Critical CSS exceeds budget:', criticalSize + ' > ' + config.budgets.critical);
            }
        }
        
        // Estimate on DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', estimateCSSSize);
        } else {
            estimateCSSSize();
        }
    }
    
    /**
     * Start monitoring CSS loading timeline
     */
    function startCSSLoadingMonitor() {
        var cssLoadStart = window.performance.now();
        
        // Monitor stylesheet loading
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1 && node.tagName === 'LINK' && node.rel === 'stylesheet') {
                        var startTime = window.performance.now();
                        
                        node.addEventListener('load', function() {
                            var loadTime = window.performance.now() - startTime;
                            
                            // Dispatch custom event
                            var event = new CustomEvent('cssFileLoaded', {
                                detail: {
                                    url: node.href,
                                    loadTime: loadTime,
                                    priority: node.getAttribute('importance') || 'medium'
                                }
                            });
                            document.dispatchEvent(event);
                        });
                    }
                });
            });
        });
        
        observer.observe(document.head, { childList: true, subtree: true });
    }
    
    /**
     * Check performance target
     */
    function checkTarget(targetName, value) {
        var target = config.targets[targetName];
        var passed = value < target;
        
        log('🎯 ' + targetName + ':', value.toFixed(1) + 'ms', 
            '(target: ' + target + 'ms)', passed ? '✅' : '❌');
        
        // Track with analytics
        if (config.enableAnalytics) {
            trackMetric('performance-target-' + targetName, {
                value: value,
                target: target,
                passed: passed
            });
        }
        
        return passed;
    }
    
    /**
     * Create visual performance indicators (debug mode)
     */
    function createPerformanceIndicators() {
        var indicators = document.createElement('div');
        indicators.id = 'css-performance-indicators';
        indicators.style.cssText = [
            'position: fixed',
            'top: 10px',
            'right: 10px',
            'background: rgba(0,0,0,0.8)',
            'color: white',
            'padding: 10px',
            'border-radius: 5px',
            'font-family: monospace',
            'font-size: 12px',
            'z-index: 10000',
            'max-width: 300px'
        ].join(';');
        
        indicators.innerHTML = '<strong>CSS Performance Monitor</strong><div id="perf-metrics"></div>';
        document.body.appendChild(indicators);
    }
    
    /**
     * Update performance indicator
     */
    function updatePerformanceIndicator(metric, value) {
        if (!config.enableVisualIndicators || !config.debugMode) return;
        
        var metricsDiv = document.getElementById('perf-metrics');
        if (!metricsDiv) return;
        
        var metricElement = document.getElementById('metric-' + metric);
        if (!metricElement) {
            metricElement = document.createElement('div');
            metricElement.id = 'metric-' + metric;
            metricsDiv.appendChild(metricElement);
        }
        
        var target = config.targets[metric.replace(/-/g, '_')] || config.targets[metric];
        var passed = target ? value < target : true;
        var color = passed ? '#4CAF50' : '#f44336';
        
        metricElement.innerHTML = '<span style="color:' + color + '">' + 
            metric + ': ' + value.toFixed(1) + 'ms</span>';
    }
    
    /**
     * Show performance summary
     */
    function showPerformanceSummary() {
        if (!config.debugMode) return;
        
        var summary = document.createElement('div');
        summary.style.cssText = [
            'position: fixed',
            'bottom: 10px',
            'left: 10px',
            'background: rgba(0,0,0,0.9)',
            'color: white',
            'padding: 15px',
            'border-radius: 5px',
            'font-family: monospace',
            'font-size: 11px',
            'z-index: 10001',
            'max-width: 400px'
        ].join(';');
        
        var report = generatePerformanceReport();
        var html = '<strong>🎨 CSS Performance Summary</strong><br>';
        
        Object.keys(report.coreWebVitals).forEach(function(key) {
            var value = report.coreWebVitals[key];
            if (value !== null) {
                html += key + ': ' + value.toFixed(1) + 'ms<br>';
            }
        });
        
        html += '<br>CSS Files: ' + report.cssFilesLoaded + '<br>';
        html += 'Critical CSS: ' + (report.criticalCSSTime || 'N/A') + '<br>';
        html += 'Total CSS: ' + (report.totalCSSTime || 'N/A') + '<br>';
        
        summary.innerHTML = html;
        document.body.appendChild(summary);
        
        // Auto-hide after 10 seconds
        setTimeout(function() {
            if (summary.parentNode) {
                summary.parentNode.removeChild(summary);
            }
        }, 10000);
    }
    
    /**
     * Generate comprehensive performance report
     */
    function generatePerformanceReport() {
        var report = {
            timestamp: new Date().toISOString(),
            loadTime: window.performance.now() - performanceState.startTime,
            criticalCSSTime: performanceState.criticalCSSTime,
            totalCSSTime: performanceState.totalCSSTime,
            cssFilesLoaded: performanceState.cssFiles.length,
            coreWebVitals: {
                first_paint: performanceState.metrics.first_paint || null,
                first_contentful_paint: performanceState.metrics.first_contentful_paint || null,
                largest_contentful_paint: performanceState.metrics.largest_contentful_paint || null,
                cumulative_layout_shift: performanceState.metrics.cumulative_layout_shift || 0
            },
            targetChecks: {},
            budget: performanceState.budget,
            cssFiles: performanceState.cssFiles
        };
        
        // Check all targets
        Object.keys(config.targets).forEach(function(target) {
            var value = null;
            
            switch (target) {
                case 'firstPaint':
                    value = report.coreWebVitals.first_paint;
                    break;
                case 'firstContentfulPaint':
                    value = report.coreWebVitals.first_contentful_paint;
                    break;
                case 'largestContentfulPaint':
                    value = report.coreWebVitals.largest_contentful_paint;
                    break;
                case 'criticalCSS':
                    value = report.criticalCSSTime;
                    break;
                case 'totalCSS':
                    value = report.totalCSSTime;
                    break;
            }
            
            if (value !== null) {
                report.targetChecks[target] = {
                    value: value,
                    target: config.targets[target],
                    passed: value < config.targets[target]
                };
            }
        });
        
        // Console reporting
        if (config.enableConsoleReporting) {
            console.group('🎨 CSS Performance Report');
            console.table(report.coreWebVitals);
            console.log('Critical CSS Time:', report.criticalCSSTime ? report.criticalCSSTime.toFixed(1) + 'ms' : 'N/A');
            console.log('Total CSS Time:', report.totalCSSTime ? report.totalCSSTime.toFixed(1) + 'ms' : 'N/A');
            console.log('CSS Files Loaded:', report.cssFilesLoaded);
            
            if (Object.keys(report.targetChecks).length > 0) {
                console.log('Target Checks:', report.targetChecks);
            }
            
            console.groupEnd();
        }
        
        // Expose globally
        window.cssPerformanceReport = report;
        
        // Track with analytics
        if (config.enableAnalytics) {
            trackMetric('css-performance-report', report);
        }
        
        return report;
    }
    
    /**
     * Track metric with analytics
     */
    function trackMetric(name, data) {
        if (!config.enableAnalytics) return;
        
        // Track with GA4 if available
        if (window.gtag) {
            window.gtag('event', 'css_performance_metric', {
                metric_name: name,
                metric_value: typeof data === 'number' ? data : JSON.stringify(data)
            });
        }
        
        // Track with custom analytics if available
        if (window.performanceAnalytics && typeof window.performanceAnalytics.addCustomEvent === 'function') {
            window.performanceAnalytics.addCustomEvent(name, data);
        }
    }
    
    /**
     * Debug logging
     */
    function log() {
        if (config.enableConsoleReporting && window.console) {
            console.log.apply(console, ['[CSS-Perf]'].concat(Array.prototype.slice.call(arguments)));
        }
    }
    
    /**
     * Public API
     */
    var CSSPerformanceMonitor = {
        getReport: function() {
            return generatePerformanceReport();
        },
        getMetrics: function() {
            return performanceState.metrics;
        },
        getConfig: function() {
            return config;
        },
        setConfig: function(newConfig) {
            Object.assign(config, newConfig);
        },
        trackCustomMetric: function(name, value) {
            trackMetric(name, value);
        }
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Expose to global scope
    window.CSSPerformanceMonitor = CSSPerformanceMonitor;
    
})(window, document);