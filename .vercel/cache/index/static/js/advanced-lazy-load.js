/**
 * Advanced Lazy Loading with WebP Support and Performance Monitoring
 * SPEC_04 Group D Implementation
 */

class AdvancedLazyLoader {
    constructor(options = {}) {
        this.options = {
            root: null,
            rootMargin: '50px',
            threshold: 0.1,
            enableWebP: true,
            enableProgressiveLoading: true,
            enablePreloading: true,
            preloadCount: 2,
            retryAttempts: 3,
            retryDelay: 1000,
            enablePerformanceTracking: true,
            ...options
        };

        this.observer = null;
        this.webpSupported = null;
        this.loadedImages = new Set();
        this.loadingImages = new Set();
        this.performanceMetrics = {
            totalImages: 0,
            loadedImages: 0,
            failedImages: 0,
            averageLoadTime: 0,
            totalLoadTime: 0,
            webpUsage: 0
        };

        this.init();
    }

    async init() {
        // Check WebP support
        this.webpSupported = await this.checkWebPSupport();
        
        // Initialize Intersection Observer
        this.setupIntersectionObserver();
        
        // Setup performance monitoring
        if (this.options.enablePerformanceTracking) {
            this.setupPerformanceMonitoring();
        }

        // Start observing images
        this.observeImages();
        
        // Setup preloading for critical images
        if (this.options.enablePreloading) {
            this.preloadCriticalImages();
        }

        // Log initial metrics
        console.log('🖼️ Advanced Lazy Loader initialized', {
            webpSupported: this.webpSupported,
            totalImages: document.querySelectorAll('[data-src], [data-srcset]').length
        });
    }

    async checkWebPSupport() {
        if (this.webpSupported !== null) return this.webpSupported;

        return new Promise(resolve => {
            const webp = new Image();
            webp.onload = webp.onerror = () => {
                resolve(webp.height === 2);
            };
            webp.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
        });
    }

    setupIntersectionObserver() {
        if (!('IntersectionObserver' in window)) {
            // Fallback for older browsers
            this.loadAllImages();
            return;
        }

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadImage(entry.target);
                    this.observer.unobserve(entry.target);
                }
            });
        }, {
            root: this.options.root,
            rootMargin: this.options.rootMargin,
            threshold: this.options.threshold
        });
    }

    setupPerformanceMonitoring() {
        // Track Core Web Vitals impact
        if ('PerformanceObserver' in window) {
            // Monitor LCP (Largest Contentful Paint)
            const lcpObserver = new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                entries.forEach(entry => {
                    if (entry.element && entry.element.hasAttribute('data-src')) {
                        console.log('📊 LCP affected by lazy-loaded image:', {
                            element: entry.element,
                            loadTime: entry.startTime,
                            size: entry.size
                        });
                    }
                });
            });

            try {
                lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
            } catch (e) {
                // LCP not supported in this browser
            }

            // Monitor layout shifts caused by image loading
            const clsObserver = new PerformanceObserver((entryList) => {
                const entries = entryList.getEntries();
                let cumulativeScore = 0;
                entries.forEach(entry => {
                    if (!entry.hadRecentInput) {
                        cumulativeScore += entry.value;
                    }
                });
                
                if (cumulativeScore > 0.1) {
                    console.warn('⚠️ Layout shift detected:', cumulativeScore);
                }
            });

            try {
                clsObserver.observe({ entryTypes: ['layout-shift'] });
            } catch (e) {
                // CLS not supported in this browser
            }
        }
    }

    observeImages() {
        const images = document.querySelectorAll('[data-src], [data-srcset]');
        this.performanceMetrics.totalImages = images.length;

        images.forEach(img => {
            // Add loading placeholder
            this.addLoadingPlaceholder(img);
            
            if (this.observer) {
                this.observer.observe(img);
            } else {
                // Fallback: load all images immediately
                this.loadImage(img);
            }
        });
    }

    addLoadingPlaceholder(img) {
        if (!img.style.backgroundColor && !img.classList.contains('placeholder-set')) {
            // Create a subtle loading placeholder
            img.style.backgroundColor = '#f0f0f0';
            img.style.backgroundImage = `
                linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent),
                linear-gradient(#f0f0f0, #f0f0f0)
            `;
            img.style.backgroundSize = '200% 100%, 100% 100%';
            img.style.backgroundRepeat = 'no-repeat';
            img.style.backgroundPosition = '-200% 0, 0 0';
            img.style.animation = 'shimmer 1.5s infinite';
            img.classList.add('placeholder-set');

            // Add shimmer animation if not exists
            if (!document.getElementById('shimmer-animation')) {
                const style = document.createElement('style');
                style.id = 'shimmer-animation';
                style.textContent = `
                    @keyframes shimmer {
                        0% { background-position: -200% 0, 0 0; }
                        100% { background-position: 200% 0, 0 0; }
                    }
                `;
                document.head.appendChild(style);
            }
        }
    }

    removeLoadingPlaceholder(img) {
        img.style.backgroundColor = '';
        img.style.backgroundImage = '';
        img.style.animation = '';
        img.classList.remove('placeholder-set');
    }

    async loadImage(img) {
        if (this.loadingImages.has(img) || this.loadedImages.has(img)) {
            return;
        }

        this.loadingImages.add(img);
        const startTime = performance.now();

        try {
            const src = await this.getOptimalImageSrc(img);
            const srcset = await this.getOptimalImageSrcset(img);

            await this.loadImageWithRetry(img, src, srcset);
            
            // Track successful load
            const loadTime = performance.now() - startTime;
            this.trackImageLoad(img, loadTime, true);
            
            // Remove loading placeholder
            this.removeLoadingPlaceholder(img);
            
            // Add fade-in animation
            this.animateImageLoad(img);
            
        } catch (error) {
            console.error('❌ Failed to load image:', error);
            this.trackImageLoad(img, performance.now() - startTime, false);
            this.handleImageError(img);
        } finally {
            this.loadingImages.delete(img);
        }
    }

    async intelligentPreload(url, reason) {
        // Check if we should preload based on current conditions
        if (!this.shouldPreload(url, reason)) return;

        if (this.preloadedResources.has(url)) return;

        try {
            // Predict resource priority
            const priority = this.predictResourcePriority(url, reason);
            
            // Preload based on network conditions and device capabilities
            if (this.deviceCapabilities && this.deviceCapabilities.saveData) {
                // Only preload critical resources on save-data mode
                if (priority < 0.8) return;
            }

            // Simple preload implementation for images
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = url;
            link.as = 'image';
            document.head.appendChild(link);
            
            this.preloadedResources.add(url);
            
            console.log(`🔄 Preloaded: ${url} (${reason}, priority: ${priority.toFixed(2)})`);

        } catch (error) {
            console.warn('Preload failed:', url, error);
        }
    }

    shouldPreload(url, reason) {
        // Simple preload logic
        return !this.preloadedResources.has(url) && url && reason;
    }

    predictResourcePriority(url, reason) {
        // Simple priority calculation
        const reasonPriorities = {
            'critical': 1.0,
            'hover': 0.8,
            'viewport': 0.7,
            'pattern': 0.6,
            'predictive': 0.4
        };
        return reasonPriorities[reason] || 0.5;
    }

    async getOptimalImageSrc(img) {
        const dataSrc = img.getAttribute('data-src');
        if (!dataSrc) return null;

        if (this.webpSupported && this.options.enableWebP) {
            // Try to get WebP version
            const webpSrc = this.convertToWebP(dataSrc);
            if (await this.imageExists(webpSrc)) {
                this.performanceMetrics.webpUsage++;
                return webpSrc;
            }
        }

        return dataSrc;
    }

    async getOptimalImageSrcset(img) {
        const dataSrcset = img.getAttribute('data-srcset');
        if (!dataSrcset) return null;

        if (this.webpSupported && this.options.enableWebP) {
            // Convert srcset to WebP if supported
            return dataSrcset.split(',').map(src => {
                const [url, descriptor] = src.trim().split(' ');
                const webpUrl = this.convertToWebP(url);
                return descriptor ? `${webpUrl} ${descriptor}` : webpUrl;
            }).join(', ');
        }

        return dataSrcset;
    }

    convertToWebP(src) {
        // Convert image extensions to WebP
        return src.replace(/\.(jpg|jpeg|png)(\?.*)?$/i, '.webp$2');
    }

    async imageExists(src) {
        return new Promise(resolve => {
            const img = new Image();
            img.onload = () => resolve(true);
            img.onerror = () => resolve(false);
            img.src = src;
        });
    }

    async loadImageWithRetry(img, src, srcset, attempt = 1) {
        return new Promise((resolve, reject) => {
            const tempImg = new Image();
            
            tempImg.onload = () => {
                // Set the actual src/srcset on successful load
                if (srcset) img.srcset = srcset;
                if (src) img.src = src;
                
                // Copy other data attributes
                ['alt', 'title', 'class'].forEach(attr => {
                    const dataAttr = img.getAttribute(`data-${attr}`);
                    if (dataAttr) {
                        img.setAttribute(attr, dataAttr);
                    }
                });

                resolve();
            };

            tempImg.onerror = () => {
                if (attempt < this.options.retryAttempts) {
                    setTimeout(() => {
                        this.loadImageWithRetry(img, src, srcset, attempt + 1)
                            .then(resolve)
                            .catch(reject);
                    }, this.options.retryDelay * attempt);
                } else {
                    reject(new Error(`Failed to load image after ${this.options.retryAttempts} attempts`));
                }
            };

            // Start loading
            if (srcset) tempImg.srcset = srcset;
            if (src) tempImg.src = src;
        });
    }

    trackImageLoad(img, loadTime, success) {
        if (success) {
            this.performanceMetrics.loadedImages++;
            this.performanceMetrics.totalLoadTime += loadTime;
            this.performanceMetrics.averageLoadTime = 
                this.performanceMetrics.totalLoadTime / this.performanceMetrics.loadedImages;
            this.loadedImages.add(img);
        } else {
            this.performanceMetrics.failedImages++;
        }

        // Report metrics every 10 images
        if ((this.performanceMetrics.loadedImages + this.performanceMetrics.failedImages) % 10 === 0) {
            this.reportMetrics();
        }
    }

    animateImageLoad(img) {
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.3s ease-in-out';
        
        // Trigger reflow
        img.offsetHeight;
        
        img.style.opacity = '1';
    }

    handleImageError(img) {
        // Set fallback image or placeholder
        const fallback = img.getAttribute('data-fallback') || 
                        'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="200"%3E%3Crect width="100%25" height="100%25" fill="%23f0f0f0"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle" font-family="Arial" font-size="14" fill="%23999"%3EImage unavailable%3C/text%3E%3C/svg%3E';
        
        img.src = fallback;
        img.classList.add('image-error');
    }

    preloadCriticalImages() {
        // Preload images that are likely to be viewed first
        const criticalImages = document.querySelectorAll('[data-src][data-priority="high"], .hero [data-src], .above-fold [data-src]');
        
        Array.from(criticalImages).slice(0, this.options.preloadCount).forEach(img => {
            this.loadImage(img);
        });
    }

    loadAllImages() {
        // Fallback function for browsers without Intersection Observer
        const images = document.querySelectorAll('[data-src], [data-srcset]');
        images.forEach(img => this.loadImage(img));
    }

    reportMetrics() {
        if (!this.options.enablePerformanceTracking) return;

        const metrics = {
            ...this.performanceMetrics,
            loadSuccessRate: (this.performanceMetrics.loadedImages / 
                (this.performanceMetrics.loadedImages + this.performanceMetrics.failedImages) * 100).toFixed(2),
            webpUsageRate: (this.performanceMetrics.webpUsage / 
                this.performanceMetrics.loadedImages * 100).toFixed(2)
        };

        console.log('📊 Lazy Loading Performance Metrics:', metrics);

        // Send to analytics if available
        if (typeof gtag !== 'undefined') {
            gtag('event', 'lazy_load_performance', {
                custom_parameter_1: metrics.loadSuccessRate,
                custom_parameter_2: metrics.averageLoadTime,
                custom_parameter_3: metrics.webpUsageRate
            });
        }
    }

    // Public API methods
    refresh() {
        this.observeImages();
    }

    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
        this.loadedImages.clear();
        this.loadingImages.clear();
    }

    getMetrics() {
        return { ...this.performanceMetrics };
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.lazyLoader = new AdvancedLazyLoader({
        rootMargin: '100px',
        threshold: 0.1,
        enableWebP: true,
        enablePreloading: true,
        preloadCount: 3,
        enablePerformanceTracking: true
    });
});

// Handle dynamic content
const observer = new MutationObserver((mutations) => {
    let hasNewImages = false;
    mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) { // Element node
                if (node.hasAttribute('data-src') || node.querySelector('[data-src]')) {
                    hasNewImages = true;
                }
            }
        });
    });
    
    if (hasNewImages && window.lazyLoader) {
        window.lazyLoader.refresh();
    }
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});