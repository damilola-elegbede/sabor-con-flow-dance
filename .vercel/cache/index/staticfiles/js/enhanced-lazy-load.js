/**
 * Enhanced Lazy Loading with WebP Support and Performance Monitoring
 * Implements Intersection Observer with fallbacks and Core Web Vitals optimization
 */

class EnhancedLazyLoader {
    constructor(options = {}) {
        this.options = {
            rootMargin: '50px 0px',
            threshold: 0.01,
            enableWebP: true,
            enableBlurUp: true,
            enablePerformanceMonitoring: true,
            retryAttempts: 3,
            retryDelay: 1000,
            ...options
        };
        
        this.observer = null;
        this.loadedImages = new Set();
        this.failedImages = new Map();
        this.performanceData = {
            totalImages: 0,
            loadedImages: 0,
            failedImages: 0,
            averageLoadTime: 0,
            totalLoadTime: 0
        };
        
        this.init();
    }
    
    init() {
        // Check WebP support
        if (this.options.enableWebP) {
            this.checkWebPSupport();
        }
        
        // Initialize Intersection Observer
        this.initIntersectionObserver();
        
        // Find and observe images
        this.observeImages();
        
        // Setup performance monitoring
        if (this.options.enablePerformanceMonitoring) {
            this.setupPerformanceMonitoring();
        }
        
        // Setup event listeners
        this.setupEventListeners();
    }
    
    checkWebPSupport() {
        return new Promise((resolve) => {
            const webP = new Image();
            webP.onload = webP.onerror = function () {
                const hasWebPSupport = webP.height === 2;
                document.documentElement.classList.add(hasWebPSupport ? 'webp' : 'no-webp');
                resolve(hasWebPSupport);
            };
            webP.src = "data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA";
        });
    }
    
    initIntersectionObserver() {
        if ('IntersectionObserver' in window) {
            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.loadImage(entry.target);
                        this.observer.unobserve(entry.target);
                    }
                });
            }, {
                rootMargin: this.options.rootMargin,
                threshold: this.options.threshold
            });
        }
    }
    
    observeImages() {
        const images = document.querySelectorAll('img[data-src], picture source[data-srcset]');
        this.performanceData.totalImages = images.length;
        
        if (this.observer) {
            // Use Intersection Observer for modern browsers
            images.forEach(img => {
                if (img.tagName === 'IMG') {
                    this.observer.observe(img);
                } else {
                    // For source elements, observe the parent picture's img
                    const parentImg = img.closest('picture').querySelector('img');
                    if (parentImg && !this.observer.root && !parentImg.dataset.observed) {
                        parentImg.dataset.observed = 'true';
                        this.observer.observe(parentImg);
                    }
                }
            });
        } else {
            // Fallback for older browsers
            images.forEach(img => {
                if (img.tagName === 'IMG') {
                    this.loadImage(img);
                }
            });
        }
    }
    
    loadImage(img) {
        if (this.loadedImages.has(img) || !img.dataset.src) {
            return;
        }
        
        const startTime = performance.now();
        const container = img.closest('.lazy-image-container, .responsive-image');
        const picture = img.closest('picture');
        
        // Load picture sources first
        if (picture) {
            picture.querySelectorAll('source[data-srcset]').forEach(source => {
                source.srcset = source.dataset.srcset;
                source.removeAttribute('data-srcset');
            });
        }
        
        // Preload the image
        const imageLoader = new Image();
        
        imageLoader.onload = () => {
            this.onImageLoad(img, imageLoader, container, startTime);
        };
        
        imageLoader.onerror = () => {
            this.onImageError(img, container);
        };
        
        // Set loading state
        this.setLoadingState(img, container, true);
        
        // Start loading
        imageLoader.src = img.dataset.src;
    }
    
    onImageLoad(img, imageLoader, container, startTime) {
        const loadTime = performance.now() - startTime;
        
        // Update image source
        img.src = imageLoader.src;
        img.removeAttribute('data-src');
        
        // Update performance data
        this.updatePerformanceData(loadTime, true);
        
        // Add loaded state
        img.classList.add('loaded');
        this.loadedImages.add(img);
        
        // Handle blur-up placeholder
        if (this.options.enableBlurUp && container) {
            this.fadeOutPlaceholder(container);
        }
        
        // Remove loading state
        this.setLoadingState(img, container, false);
        
        // Trigger custom event
        this.dispatchLoadEvent(img, { loadTime, success: true });
    }
    
    onImageError(img, container) {
        const retryCount = this.failedImages.get(img) || 0;
        
        if (retryCount < this.options.retryAttempts) {
            // Retry loading
            this.failedImages.set(img, retryCount + 1);
            setTimeout(() => {
                this.loadImage(img);
            }, this.options.retryDelay * (retryCount + 1));
        } else {
            // Final failure
            this.updatePerformanceData(0, false);
            img.classList.add('load-error');
            this.setLoadingState(img, container, false);
            
            // Trigger error event
            this.dispatchLoadEvent(img, { success: false, retryCount });
        }
    }
    
    setLoadingState(img, container, isLoading) {
        const loadingIndicator = container?.querySelector('.lazy-loading-indicator');
        
        if (isLoading) {
            img.classList.add('loading');
            loadingIndicator?.classList.remove('hidden');
        } else {
            img.classList.remove('loading');
            loadingIndicator?.classList.add('hidden');
        }
    }
    
    fadeOutPlaceholder(container) {
        const placeholder = container.querySelector('.lazy-placeholder');
        if (placeholder) {
            placeholder.style.transition = 'opacity 0.3s ease';
            placeholder.style.opacity = '0';
            
            setTimeout(() => {
                placeholder.style.display = 'none';
            }, 300);
        }
    }
    
    updatePerformanceData(loadTime, success) {
        if (success) {
            this.performanceData.loadedImages++;
            this.performanceData.totalLoadTime += loadTime;
            this.performanceData.averageLoadTime = 
                this.performanceData.totalLoadTime / this.performanceData.loadedImages;
        } else {
            this.performanceData.failedImages++;
        }
    }
    
    dispatchLoadEvent(img, details) {
        const event = new CustomEvent('lazyImageLoad', {
            detail: {
                element: img,
                ...details
            }
        });
        document.dispatchEvent(event);
    }
    
    setupPerformanceMonitoring() {
        // Monitor Largest Contentful Paint (LCP)
        if ('PerformanceObserver' in window) {
            try {
                const lcpObserver = new PerformanceObserver((entryList) => {
                    const entries = entryList.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    
                    // Report LCP if it involves an image
                    if (lastEntry.element && lastEntry.element.tagName === 'IMG') {
                        console.log('LCP Image:', {
                            element: lastEntry.element,
                            loadTime: lastEntry.loadTime,
                            renderTime: lastEntry.renderTime,
                            startTime: lastEntry.startTime
                        });
                    }
                });
                
                lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
            } catch (e) {
                console.warn('LCP monitoring not available:', e);
            }
        }
    }
    
    setupEventListeners() {
        // Handle dynamic content
        document.addEventListener('DOMContentLoaded', () => {
            this.observeImages();
        });
        
        // Handle viewport changes
        window.addEventListener('resize', () => {
            // Re-observe images that might have come into view
            setTimeout(() => this.observeImages(), 100);
        });
        
        // Handle orientation change on mobile
        window.addEventListener('orientationchange', () => {
            setTimeout(() => this.observeImages(), 300);
        });
    }
    
    // Public API methods
    loadAllImages() {
        const images = document.querySelectorAll('img[data-src]');
        images.forEach(img => this.loadImage(img));
    }
    
    getPerformanceData() {
        return {
            ...this.performanceData,
            successRate: this.performanceData.totalImages > 0 
                ? (this.performanceData.loadedImages / this.performanceData.totalImages) * 100 
                : 0
        };
    }
    
    refreshImages() {
        this.loadedImages.clear();
        this.failedImages.clear();
        this.observeImages();
    }
    
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
        this.loadedImages.clear();
        this.failedImages.clear();
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.lazyLoader = new EnhancedLazyLoader({
        rootMargin: '100px 0px', // Load images 100px before they come into view
        threshold: 0.01,
        enableWebP: true,
        enableBlurUp: true,
        enablePerformanceMonitoring: true
    });
    
    // Expose performance data globally for debugging
    window.getLazyLoadPerformance = () => window.lazyLoader.getPerformanceData();
});

// Handle page visibility changes (pause/resume loading)
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, pause aggressive loading
        if (window.lazyLoader) {
            window.lazyLoader.options.rootMargin = '0px';
        }
    } else {
        // Page is visible, resume normal loading
        if (window.lazyLoader) {
            window.lazyLoader.options.rootMargin = '100px 0px';
        }
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedLazyLoader;
}