/**
 * Resource Optimization and Intelligent Preloading
 * SPEC_04 Group D Implementation
 */

class ResourceOptimizer {
    constructor(options = {}) {
        this.options = {
            enableIntelligentPreloading: true,
            enableResourceHints: true,
            enableServiceWorker: true,
            preloadCriticalResources: true,
            maxPreloadConnections: 6,
            preloadThreshold: 0.7, // Preload when 70% likely to be visited
            enableAdaptiveLoading: true,
            ...options
        };

        this.preloadedResources = new Set();
        this.resourcePriorities = new Map();
        this.userBehaviorData = {
            visitedPages: new Set(),
            clickPatterns: [],
            scrollPatterns: [],
            timeOnPage: {},
            exitPatterns: []
        };

        this.networkCondition = 'unknown';
        this.deviceCapabilities = this.detectDeviceCapabilities();

        this.init();
    }

    init() {
        console.log('🚀 Resource Optimizer initialized');

        // Detect network conditions
        this.detectNetworkConditions();

        // Setup intelligent preloading
        if (this.options.enableIntelligentPreloading) {
            this.setupIntelligentPreloading();
        }

        // Setup resource hints
        if (this.options.enableResourceHints) {
            this.setupResourceHints();
        }

        // Setup Service Worker
        if (this.options.enableServiceWorker) {
            this.setupServiceWorker();
        }

        // Setup adaptive loading
        if (this.options.enableAdaptiveLoading) {
            this.setupAdaptiveLoading();
        }

        // Preload critical resources
        if (this.options.preloadCriticalResources) {
            this.preloadCriticalResources();
        }

        // Setup user behavior tracking
        this.setupBehaviorTracking();

        // Setup resource priority management
        this.setupResourcePriorities();
    }

    detectDeviceCapabilities() {
        const memory = navigator.deviceMemory || 4; // Default to 4GB
        const cores = navigator.hardwareConcurrency || 4; // Default to 4 cores
        const connection = navigator.connection;

        return {
            memory: memory,
            cores: cores,
            effectiveType: connection?.effectiveType || '4g',
            downlink: connection?.downlink || 10,
            rtt: connection?.rtt || 100,
            saveData: connection?.saveData || false
        };
    }

    detectNetworkConditions() {
        if ('connection' in navigator) {
            const connection = navigator.connection;
            this.networkCondition = connection.effectiveType;

            // Monitor network changes
            connection.addEventListener('change', () => {
                this.networkCondition = connection.effectiveType;
                this.adaptToNetworkConditions();
            });
        }

        // Measure actual network performance
        this.measureNetworkPerformance();
    }

    async measureNetworkPerformance() {
        try {
            const startTime = performance.now();
            
            // Use a small image to test network speed
            const testImage = new Image();
            testImage.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
            
            await new Promise((resolve, reject) => {
                testImage.onload = resolve;
                testImage.onerror = reject;
                setTimeout(reject, 5000); // 5s timeout
            });

            const loadTime = performance.now() - startTime;
            
            // Categorize network speed based on load time
            if (loadTime < 100) {
                this.networkCondition = 'fast';
            } else if (loadTime < 300) {
                this.networkCondition = 'moderate';
            } else {
                this.networkCondition = 'slow';
            }

        } catch (error) {
            console.warn('Network performance test failed:', error);
            this.networkCondition = 'unknown';
        }
    }

    setupIntelligentPreloading() {
        // Track user interactions to predict next page
        this.setupHoverPreloading();
        this.setupScrollPreloading();
        this.setupClickPatternAnalysis();
    }

    setupHoverPreloading() {
        let hoverTimeout;
        const preloadOnHover = (event) => {
            const link = event.target.closest('a[href]');
            if (!link || link.hostname !== window.location.hostname) return;

            clearTimeout(hoverTimeout);
            hoverTimeout = setTimeout(() => {
                this.intelligentPreload(link.href, 'hover');
            }, 100); // 100ms delay to avoid accidental hovers
        };

        const cancelPreload = () => {
            clearTimeout(hoverTimeout);
        };

        document.addEventListener('mouseover', preloadOnHover);
        document.addEventListener('mouseout', cancelPreload);
        document.addEventListener('touchstart', preloadOnHover);
    }

    setupScrollPreloading() {
        const visibleLinks = new Set();
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const link = entry.target;
                if (entry.isIntersecting) {
                    visibleLinks.add(link);
                    // Preload after link is visible for 2 seconds
                    setTimeout(() => {
                        if (visibleLinks.has(link)) {
                            this.intelligentPreload(link.href, 'viewport');
                        }
                    }, 2000);
                } else {
                    visibleLinks.delete(link);
                }
            });
        }, {
            rootMargin: '100px'
        });

        // Observe all internal links
        document.querySelectorAll('a[href]').forEach(link => {
            if (link.hostname === window.location.hostname) {
                observer.observe(link);
            }
        });
    }

    setupClickPatternAnalysis() {
        document.addEventListener('click', (event) => {
            const link = event.target.closest('a[href]');
            if (link && link.hostname === window.location.hostname) {
                this.userBehaviorData.clickPatterns.push({
                    href: link.href,
                    timestamp: Date.now(),
                    position: { x: event.clientX, y: event.clientY },
                    context: this.getElementContext(link)
                });

                // Analyze patterns and preload likely next pages
                this.analyzeClickPatterns();
            }
        });
    }

    getElementContext(element) {
        return {
            tagName: element.tagName,
            className: element.className,
            textContent: element.textContent.slice(0, 50),
            parentTagName: element.parentElement?.tagName,
            section: this.getPageSection(element)
        };
    }

    getPageSection(element) {
        // Determine which section of the page the element is in
        const rect = element.getBoundingClientRect();
        const pageHeight = document.documentElement.scrollHeight;
        const scrollTop = window.pageYOffset;
        const elementTop = rect.top + scrollTop;
        
        const section = elementTop / pageHeight;
        
        if (section < 0.2) return 'header';
        if (section < 0.8) return 'content';
        return 'footer';
    }

    analyzeClickPatterns() {
        const recentPatterns = this.userBehaviorData.clickPatterns
            .filter(pattern => Date.now() - pattern.timestamp < 300000) // Last 5 minutes
            .slice(-10); // Last 10 clicks

        // Find common navigation patterns
        const patterns = {};
        recentPatterns.forEach(pattern => {
            const key = `${pattern.context.section}-${pattern.context.tagName}`;
            patterns[key] = (patterns[key] || 0) + 1;
        });

        // Preload resources that match common patterns
        Object.entries(patterns).forEach(([pattern, frequency]) => {
            if (frequency >= 2) { // Pattern appears at least twice
                this.preloadPatternResources(pattern);
            }
        });
    }

    preloadPatternResources(pattern) {
        // Find links that match the pattern
        const [section, tagName] = pattern.split('-');
        const selector = `${tagName.toLowerCase()}[href]`;
        
        document.querySelectorAll(selector).forEach(link => {
            if (this.getPageSection(link) === section && 
                link.hostname === window.location.hostname) {
                this.intelligentPreload(link.href, 'pattern');
            }
        });
    }

    async intelligentPreload(url, reason) {
        // Check if we should preload based on current conditions
        if (!this.shouldPreload(url, reason)) return;

        if (this.preloadedResources.has(url)) return;

        try {
            // Predict resource priority
            const priority = this.predictResourcePriority(url, reason);
            
            // Preload based on network conditions and device capabilities
            if (this.deviceCapabilities.saveData) {
                // Only preload critical resources on save-data mode
                if (priority < 0.8) return;
            }

            // Adaptive preloading based on network
            const preloadStrategy = this.getPreloadStrategy();
            
            await this.preloadResource(url, preloadStrategy, priority);
            
            this.preloadedResources.add(url);
            
            console.log(`🔄 Preloaded: ${url} (${reason}, priority: ${priority.toFixed(2)})`);

        } catch (error) {
            console.warn('Preload failed:', url, error);
        }
    }

    shouldPreload(url, reason) {
        // Check preload threshold
        const priority = this.predictResourcePriority(url, reason);
        if (priority < this.options.preloadThreshold) return false;

        // Check connection limits
        if (this.preloadedResources.size >= this.options.maxPreloadConnections) return false;

        // Check network conditions
        if (this.networkCondition === 'slow' && reason !== 'critical') return false;

        // Check if already preloaded
        if (this.preloadedResources.has(url)) return false;

        return true;
    }

    predictResourcePriority(url, reason) {
        let priority = 0.5; // Base priority

        // Reason-based priority
        const reasonPriorities = {
            'critical': 1.0,
            'hover': 0.8,
            'viewport': 0.7,
            'pattern': 0.6,
            'predictive': 0.4
        };

        priority = reasonPriorities[reason] || priority;

        // Historical data priority
        const visitCount = this.getPageVisitCount(url);
        priority += Math.min(visitCount * 0.1, 0.3);

        // Time-based priority (recent pages more likely)
        const lastVisit = this.getLastVisitTime(url);
        if (lastVisit) {
            const timeDiff = Date.now() - lastVisit;
            const daysDiff = timeDiff / (1000 * 60 * 60 * 24);
            priority += Math.max(0.2 - daysDiff * 0.05, 0);
        }

        return Math.min(priority, 1.0);
    }

    getPreloadStrategy() {
        const { effectiveType, saveData, downlink } = this.deviceCapabilities;

        if (saveData) return 'minimal';
        if (effectiveType === 'slow-2g' || effectiveType === '2g') return 'minimal';
        if (effectiveType === '3g' || downlink < 1) return 'conservative';
        if (effectiveType === '4g' && downlink > 5) return 'aggressive';
        
        return 'balanced';
    }

    async preloadResource(url, strategy, priority) {
        const strategies = {
            minimal: () => this.preloadPage(url, { priority: 'low' }),
            conservative: () => this.preloadPage(url, { priority: 'low', prefetch: true }),
            balanced: () => this.preloadPage(url, { priority: 'low', preload: true }),
            aggressive: () => this.preloadPageWithAssets(url, priority)
        };

        return strategies[strategy]();
    }

    async preloadPage(url, options = {}) {
        const link = document.createElement('link');
        link.rel = options.preload ? 'preload' : 'prefetch';
        link.href = url;
        link.as = 'document';
        
        if (options.priority) {
            link.setAttribute('importance', options.priority);
        }

        document.head.appendChild(link);

        return new Promise((resolve, reject) => {
            link.onload = resolve;
            link.onerror = reject;
            setTimeout(reject, 10000); // 10s timeout
        });
    }

    async preloadPageWithAssets(url, priority) {
        try {
            // First preload the page
            await this.preloadPage(url, { preload: true, priority: 'high' });

            // If high priority, also preload critical assets
            if (priority > 0.8) {
                await this.preloadPageAssets(url);
            }
        } catch (error) {
            console.warn('Failed to preload page with assets:', error);
        }
    }

    async preloadPageAssets(url) {
        try {
            // Fetch the page to analyze assets
            const response = await fetch(url, { method: 'HEAD' });
            if (!response.ok) return;

            // For now, preload common assets that are likely on every page
            const commonAssets = [
                '/static/css/styles.css',
                '/static/js/main.js',
                '/static/images/sabor-con-flow-logo.webp'
            ];

            commonAssets.forEach(asset => {
                this.preloadStaticAsset(asset);
            });

        } catch (error) {
            console.warn('Failed to preload page assets:', error);
        }
    }

    preloadStaticAsset(url) {
        if (this.preloadedResources.has(url)) return;

        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = url;
        
        // Determine asset type
        if (url.match(/\.css$/)) {
            link.as = 'style';
        } else if (url.match(/\.js$/)) {
            link.as = 'script';
        } else if (url.match(/\.(png|jpg|jpeg|webp|gif)$/)) {
            link.as = 'image';
        } else if (url.match(/\.(woff|woff2)$/)) {
            link.as = 'font';
            link.crossOrigin = 'anonymous';
        }

        document.head.appendChild(link);
        this.preloadedResources.add(url);
    }

    setupResourceHints() {
        // Add DNS prefetch for external domains
        const externalDomains = [
            'fonts.googleapis.com',
            'fonts.gstatic.com',
            'cdnjs.cloudflare.com',
            'assets.calendly.com'
        ];

        externalDomains.forEach(domain => {
            this.addResourceHint('dns-prefetch', `//${domain}`);
        });

        // Add preconnect for critical external resources
        const criticalDomains = [
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com'
        ];

        criticalDomains.forEach(domain => {
            this.addResourceHint('preconnect', domain, { crossorigin: true });
        });
    }

    addResourceHint(rel, href, attributes = {}) {
        const link = document.createElement('link');
        link.rel = rel;
        link.href = href;

        Object.entries(attributes).forEach(([key, value]) => {
            if (value === true) {
                link.setAttribute(key, '');
            } else {
                link.setAttribute(key, value);
            }
        });

        document.head.appendChild(link);
    }

    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js', {
                scope: '/'
            }).then(registration => {
                console.log('✅ Service Worker registered:', registration);
                
                // Setup communication with service worker
                this.setupServiceWorkerCommunication(registration);
                
                // Listen for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            console.log('🔄 New Service Worker available');
                            // Optionally notify user about update
                        }
                    });
                });
                
            }).catch(error => {
                console.warn('❌ Service Worker registration failed:', error);
            });
        } else {
            console.warn('⚠️ Service Worker not supported');
        }
    }

    setupServiceWorkerCommunication(registration) {
        // Send performance data to service worker for caching decisions
        if (registration.active) {
            registration.active.postMessage({
                type: 'PERFORMANCE_DATA',
                data: {
                    networkCondition: this.networkCondition,
                    deviceCapabilities: this.deviceCapabilities,
                    userBehavior: this.userBehaviorData
                }
            });
        }
    }

    setupAdaptiveLoading() {
        // Adjust loading strategies based on device and network conditions
        this.adaptToNetworkConditions();
        
        // Monitor device performance
        this.monitorDevicePerformance();
    }

    adaptToNetworkConditions() {
        const body = document.body;
        
        // Remove existing network classes
        body.classList.remove('network-slow', 'network-fast', 'network-save-data');
        
        // Add appropriate class based on network condition
        if (this.deviceCapabilities.saveData) {
            body.classList.add('network-save-data');
        } else if (this.networkCondition === 'slow' || this.networkCondition === '2g') {
            body.classList.add('network-slow');
        } else if (this.networkCondition === 'fast' || this.networkCondition === '4g') {
            body.classList.add('network-fast');
        }

        // Dispatch event for other components to react
        window.dispatchEvent(new CustomEvent('networkConditionChanged', {
            detail: {
                condition: this.networkCondition,
                capabilities: this.deviceCapabilities
            }
        }));
    }

    monitorDevicePerformance() {
        // Monitor memory usage
        if (performance.memory) {
            const checkMemory = () => {
                const memoryInfo = performance.memory;
                const usagePercent = memoryInfo.usedJSHeapSize / memoryInfo.jsHeapSizeLimit;
                
                if (usagePercent > 0.8) {
                    console.warn('⚠️ High memory usage detected, reducing preloading');
                    this.options.maxPreloadConnections = Math.max(2, this.options.maxPreloadConnections - 1);
                }
            };

            setInterval(checkMemory, 30000); // Check every 30 seconds
        }

        // Monitor frame rate
        let frames = 0;
        let lastTime = performance.now();
        
        const countFrames = () => {
            frames++;
            const currentTime = performance.now();
            
            if (currentTime - lastTime >= 1000) {
                const fps = frames;
                frames = 0;
                lastTime = currentTime;
                
                if (fps < 30) {
                    console.warn('⚠️ Low frame rate detected, reducing resource intensity');
                    this.options.preloadThreshold = Math.min(0.9, this.options.preloadThreshold + 0.1);
                }
            }
            
            requestAnimationFrame(countFrames);
        };
        
        requestAnimationFrame(countFrames);
    }

    preloadCriticalResources() {
        // Preload critical fonts
        this.preloadStaticAsset('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&display=swap');
        this.preloadStaticAsset('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

        // Preload critical images
        const criticalImages = document.querySelectorAll('[data-priority="high"], .hero img, .above-fold img');
        criticalImages.forEach(img => {
            const src = img.getAttribute('data-src') || img.src;
            if (src) {
                this.preloadStaticAsset(src);
            }
        });

        // Preload critical CSS and JS
        this.preloadStaticAsset('/static/css/styles.css');
        this.preloadStaticAsset('/static/js/main.js');
    }

    setupBehaviorTracking() {
        // Track page visits
        this.userBehaviorData.visitedPages.add(window.location.href);
        
        // Track time on page
        const startTime = Date.now();
        window.addEventListener('beforeunload', () => {
            const timeOnPage = Date.now() - startTime;
            this.userBehaviorData.timeOnPage[window.location.href] = timeOnPage;
        });

        // Track scroll behavior
        let maxScroll = 0;
        window.addEventListener('scroll', () => {
            const scrollPercent = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);
            maxScroll = Math.max(maxScroll, scrollPercent);
        });

        window.addEventListener('beforeunload', () => {
            this.userBehaviorData.scrollPatterns.push({
                url: window.location.href,
                maxScroll: maxScroll,
                timestamp: Date.now()
            });
        });
    }

    setupResourcePriorities() {
        // Define resource priority based on type and usage
        const priorityMap = {
            'document': 1.0,
            'style': 0.9,
            'script': 0.8,
            'font': 0.7,
            'image': 0.6,
            'video': 0.4,
            'audio': 0.3
        };

        this.resourcePriorities = new Map(Object.entries(priorityMap));
    }

    getPageVisitCount(url) {
        // This would typically come from localStorage or analytics
        const visits = localStorage.getItem(`visit-count-${url}`);
        return visits ? parseInt(visits, 10) : 0;
    }

    getLastVisitTime(url) {
        const lastVisit = localStorage.getItem(`last-visit-${url}`);
        return lastVisit ? parseInt(lastVisit, 10) : null;
    }

    // Public API
    getOptimizationStatus() {
        return {
            preloadedResources: this.preloadedResources.size,
            networkCondition: this.networkCondition,
            deviceCapabilities: this.deviceCapabilities,
            userBehaviorData: this.userBehaviorData
        };
    }

    forcePreload(url, priority = 1.0) {
        return this.intelligentPreload(url, 'forced');
    }

    clearPreloadCache() {
        this.preloadedResources.clear();
    }
}

// Initialize Resource Optimizer
window.addEventListener('DOMContentLoaded', () => {
    window.resourceOptimizer = new ResourceOptimizer({
        enableIntelligentPreloading: true,
        enableResourceHints: true,
        enableServiceWorker: false, // Disabled until SW is implemented
        preloadCriticalResources: true,
        enableAdaptiveLoading: true
    });
});