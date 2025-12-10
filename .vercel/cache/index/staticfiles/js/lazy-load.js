/**
 * Lazy Loading Implementation for Sabor Con Flow Dance
 * Implements Intersection Observer API with fallback support
 * Optimized for Core Web Vitals compliance
 */

(function() {
    'use strict';

    // Configuration
    const config = {
        rootMargin: '50px 0px', // Start loading 50px before entering viewport
        threshold: 0.01, // Trigger when 1% of image is visible
        fadeInDuration: 300, // Fade-in animation duration
        placeholderClass: 'lazy-placeholder',
        loadedClass: 'lazy-loaded',
        errorClass: 'lazy-error'
    };

    // Check for native lazy loading support
    const hasNativeLazyLoad = 'loading' in HTMLImageElement.prototype;

    // Check for Intersection Observer support
    const hasIntersectionObserver = 'IntersectionObserver' in window;

    /**
     * Preload an image and return a promise
     */
    function preloadImage(img) {
        return new Promise((resolve, reject) => {
            const tempImg = new Image();
            
            tempImg.onload = () => {
                // Set the actual image source
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                }
                
                // Handle srcset for responsive images
                if (img.dataset.srcset) {
                    img.srcset = img.dataset.srcset;
                }
                
                // Handle sizes attribute
                if (img.dataset.sizes) {
                    img.sizes = img.dataset.sizes;
                }
                
                // Handle WebP with fallback
                if (img.dataset.webp && supportsWebP()) {
                    img.src = img.dataset.webp;
                } else if (img.dataset.fallback) {
                    img.src = img.dataset.fallback;
                }
                
                resolve(img);
            };
            
            tempImg.onerror = () => {
                reject(new Error(`Failed to load image: ${img.dataset.src}`));
            };
            
            // Start loading
            tempImg.src = img.dataset.src || img.dataset.webp || img.dataset.fallback;
        });
    }

    /**
     * Check WebP support
     */
    function supportsWebP() {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        return canvas.toDataURL('image/webp').indexOf('image/webp') === 0;
    }

    /**
     * Load image with animation
     */
    function loadImage(img) {
        // Add loading state
        img.classList.add('lazy-loading');
        
        preloadImage(img)
            .then(() => {
                // Remove placeholder background
                img.classList.remove(config.placeholderClass);
                img.classList.remove('lazy-loading');
                img.classList.add(config.loadedClass);
                
                // Trigger custom event
                img.dispatchEvent(new CustomEvent('lazyloaded', {
                    detail: { img }
                }));
            })
            .catch((error) => {
                console.error('Lazy load error:', error);
                img.classList.add(config.errorClass);
                
                // Try fallback image if available
                if (img.dataset.fallback && img.src !== img.dataset.fallback) {
                    img.src = img.dataset.fallback;
                }
                
                // Trigger error event
                img.dispatchEvent(new CustomEvent('lazyloaderror', {
                    detail: { img, error }
                }));
            });
    }

    /**
     * Intersection Observer implementation
     */
    function initIntersectionObserver() {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    loadImage(img);
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: config.rootMargin,
            threshold: config.threshold
        });

        return imageObserver;
    }

    /**
     * Fallback for browsers without Intersection Observer
     */
    function lazyLoadFallback() {
        const images = document.querySelectorAll('img[data-src], img[data-webp]');
        const imageArray = Array.from(images);

        function checkImages() {
            imageArray.forEach((img, index) => {
                if (img.classList.contains(config.loadedClass)) {
                    return;
                }

                const rect = img.getBoundingClientRect();
                const inViewport = rect.top <= window.innerHeight + 50 && 
                                  rect.bottom >= -50;

                if (inViewport) {
                    loadImage(img);
                    imageArray.splice(index, 1);
                }
            });

            if (imageArray.length === 0) {
                window.removeEventListener('scroll', throttledCheck);
                window.removeEventListener('resize', throttledCheck);
            }
        }

        // Throttle function for performance
        let ticking = false;
        function throttledCheck() {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    checkImages();
                    ticking = false;
                });
                ticking = true;
            }
        }

        // Initial check
        checkImages();

        // Add event listeners
        window.addEventListener('scroll', throttledCheck, { passive: true });
        window.addEventListener('resize', throttledCheck, { passive: true });
        window.addEventListener('orientationchange', throttledCheck, { passive: true });
    }

    /**
     * Initialize lazy loading for background images
     */
    function initBackgroundImages() {
        const elements = document.querySelectorAll('[data-bg-src]');
        
        if (hasIntersectionObserver) {
            const bgObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const elem = entry.target;
                        const bgSrc = elem.dataset.bgSrc;
                        
                        // Check WebP support for background images
                        if (elem.dataset.bgWebp && supportsWebP()) {
                            elem.style.backgroundImage = `url(${elem.dataset.bgWebp})`;
                        } else {
                            elem.style.backgroundImage = `url(${bgSrc})`;
                        }
                        
                        elem.classList.add('bg-loaded');
                        observer.unobserve(elem);
                    }
                });
            }, {
                rootMargin: config.rootMargin,
                threshold: config.threshold
            });

            elements.forEach(elem => bgObserver.observe(elem));
        } else {
            // Fallback for older browsers
            elements.forEach(elem => {
                const bgSrc = elem.dataset.bgSrc;
                elem.style.backgroundImage = `url(${bgSrc})`;
                elem.classList.add('bg-loaded');
            });
        }
    }

    /**
     * Initialize video lazy loading
     */
    function initVideoLazyLoad() {
        const videos = document.querySelectorAll('video[data-src]');
        
        if (hasIntersectionObserver) {
            const videoObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const video = entry.target;
                        
                        // Set video source
                        if (video.dataset.src) {
                            video.src = video.dataset.src;
                        }
                        
                        // Handle multiple sources
                        const sources = video.querySelectorAll('source[data-src]');
                        sources.forEach(source => {
                            source.src = source.dataset.src;
                        });
                        
                        // Load video
                        video.load();
                        video.classList.add('video-loaded');
                        
                        observer.unobserve(video);
                    }
                });
            }, {
                rootMargin: '100px 0px', // Load videos earlier
                threshold: 0.01
            });

            videos.forEach(video => videoObserver.observe(video));
        }
    }

    /**
     * Add placeholder styles
     */
    function addPlaceholderStyles() {
        const style = document.createElement('style');
        style.textContent = `
            img.lazy-placeholder {
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
            }
            
            img.lazy-loading {
                opacity: 0;
                transition: opacity ${config.fadeInDuration}ms ease-in-out;
            }
            
            img.lazy-loaded {
                opacity: 1;
                animation: fadeIn ${config.fadeInDuration}ms ease-in-out;
            }
            
            img.lazy-error {
                opacity: 0.5;
                filter: grayscale(100%);
            }
            
            .bg-loaded {
                transition: opacity ${config.fadeInDuration}ms ease-in-out;
            }
            
            @keyframes loading {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: scale(0.95); }
                to { opacity: 1; transform: scale(1); }
            }
            
            /* Aspect ratio placeholders */
            .aspect-ratio-16-9 {
                padding-bottom: 56.25%;
                position: relative;
            }
            
            .aspect-ratio-4-3 {
                padding-bottom: 75%;
                position: relative;
            }
            
            .aspect-ratio-1-1 {
                padding-bottom: 100%;
                position: relative;
            }
            
            .aspect-ratio-16-9 > img,
            .aspect-ratio-4-3 > img,
            .aspect-ratio-1-1 > img {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Main initialization function
     */
    function init() {
        // Add placeholder styles
        addPlaceholderStyles();

        // Get all lazy images
        const lazyImages = document.querySelectorAll('img[data-src], img[data-webp], img.lazy');
        
        if (lazyImages.length === 0) {
            return; // No lazy images found
        }

        // Use native lazy loading if supported
        if (hasNativeLazyLoad) {
            lazyImages.forEach(img => {
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                }
                img.loading = 'lazy';
                img.classList.add(config.loadedClass);
            });
        } 
        // Use Intersection Observer if supported
        else if (hasIntersectionObserver) {
            const imageObserver = initIntersectionObserver();
            lazyImages.forEach(img => {
                img.classList.add(config.placeholderClass);
                imageObserver.observe(img);
            });
        } 
        // Fallback for older browsers
        else {
            lazyLoadFallback();
        }

        // Initialize background images
        initBackgroundImages();

        // Initialize video lazy loading
        initVideoLazyLoad();

        // Expose API for manual lazy loading
        window.LazyLoad = {
            load: loadImage,
            loadAll: function() {
                const images = document.querySelectorAll('img[data-src]:not(.lazy-loaded)');
                images.forEach(loadImage);
            },
            update: function() {
                init();
            }
        };
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Reinitialize on dynamic content changes
    if (window.MutationObserver) {
        const observer = new MutationObserver((mutations) => {
            let shouldUpdate = false;
            
            mutations.forEach(mutation => {
                if (mutation.addedNodes.length) {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1 && (
                            node.matches('img[data-src]') ||
                            node.querySelector('img[data-src]')
                        )) {
                            shouldUpdate = true;
                        }
                    });
                }
            });
            
            if (shouldUpdate) {
                init();
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

})();