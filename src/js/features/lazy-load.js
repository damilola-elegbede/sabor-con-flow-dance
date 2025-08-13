/**
 * Enhanced Lazy Loading with Progressive Enhancement
 * Works as fallback when JavaScript is disabled
 */

export default class LazyLoad {
  constructor(options = {}) {
    this.options = {
      rootMargin: '50px 0px',
      threshold: 0.01,
      imageSelector: 'img[data-src], img[data-lazy], img.lazy',
      backgroundSelector: '[data-bg-src]',
      videoSelector: 'video[data-src]',
      iframeSelector: 'iframe[data-src]',
      loadedClass: 'lazy-loaded',
      loadingClass: 'lazy-loading',
      errorClass: 'lazy-error',
      fadeInDuration: 300,
      retryAttempts: 3,
      retryDelay: 1000,
      enableWebP: true,
      enablePlaceholders: true,
      enableNativeLazyLoading: true,
      ...options,
    };

    this.observer = null;
    this.retryCount = new Map();
    this.loadedItems = new Set();
    this.webPSupported = false;

    this.init();
  }

  init() {
    // Check WebP support
    this.checkWebPSupport();

    // Add progressive enhancement
    this.setupProgressiveEnhancement();

    // Initialize lazy loading strategy
    this.initializeLazyLoading();

    console.log('✅ Enhanced lazy loading initialized');
  }

  checkWebPSupport() {
    if (!this.options.enableWebP) {
      this.webPSupported = false;
      return;
    }

    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    this.webPSupported = canvas.toDataURL('image/webp').indexOf('image/webp') === 0;

    // Add class to document for CSS targeting
    document.documentElement.classList.add(this.webPSupported ? 'webp-supported' : 'no-webp');
  }

  setupProgressiveEnhancement() {
    // Add enhanced class for CSS targeting
    document.documentElement.classList.add('js-lazy-load');

    // Add styles for loading states
    this.addLoadingStyles();

    // Set up placeholder system
    if (this.options.enablePlaceholders) {
      this.setupPlaceholders();
    }
  }

  addLoadingStyles() {
    const style = document.createElement('style');
    style.textContent = `
      .js-lazy-load img.lazy-loading {
        opacity: 0;
        transition: opacity ${this.options.fadeInDuration}ms ease-in-out;
      }
      
      .js-lazy-load img.lazy-loaded {
        opacity: 1;
      }
      
      .js-lazy-load img.lazy-error {
        opacity: 0.5;
        filter: grayscale(100%);
      }
      
      .js-lazy-load .lazy-placeholder {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: loading-shimmer 1.5s infinite;
      }
      
      @keyframes loading-shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
      }
      
      .js-lazy-load .lazy-placeholder.loaded {
        animation: none;
        background: none;
      }
      
      /* Network-aware optimizations */
      .slow-connection .lazy-placeholder {
        animation-duration: 3s;
      }
      
      .save-data img[data-src] {
        background: #f0f0f0;
      }
    `;
    document.head.appendChild(style);
  }

  setupPlaceholders() {
    const images = document.querySelectorAll(this.options.imageSelector);
    images.forEach(img => {
      if (!img.src && img.dataset.src) {
        // Add placeholder class
        img.classList.add('lazy-placeholder');

        // Set low-quality placeholder if available
        if (img.dataset.placeholder) {
          img.src = img.dataset.placeholder;
        } else {
          // Generate simple placeholder
          this.generatePlaceholder(img);
        }
      }
    });
  }

  generatePlaceholder(img) {
    // Get image dimensions from attributes or compute from aspect ratio
    const width = img.getAttribute('width') || 400;
    const height = img.getAttribute('height') || 300;

    // Simple SVG placeholder
    const placeholder = `data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='${width}' height='${height}' viewBox='0 0 ${width} ${height}'%3E%3Crect width='100%25' height='100%25' fill='%23f0f0f0'/%3E%3C/svg%3E`;

    img.src = placeholder;
  }

  initializeLazyLoading() {
    // Use native lazy loading if supported and enabled
    if (this.options.enableNativeLazyLoading && 'loading' in HTMLImageElement.prototype) {
      this.initNativeLazyLoading();
    }
    // Use Intersection Observer if supported
    else if ('IntersectionObserver' in window) {
      this.initIntersectionObserver();
    }
    // Fallback to scroll-based lazy loading
    else {
      this.initScrollBasedLazyLoading();
    }
  }

  initNativeLazyLoading() {
    const images = document.querySelectorAll(this.options.imageSelector);
    images.forEach(img => {
      if (img.dataset.src) {
        img.src = this.getOptimalImageSource(img);
        img.loading = 'lazy';
        img.classList.add(this.options.loadedClass);
        this.handleImageLoad(img);
      }
    });

    // Still use observer for other elements
    this.initIntersectionObserver();
  }

  initIntersectionObserver() {
    this.observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this.loadElement(entry.target);
            this.observer.unobserve(entry.target);
          }
        });
      },
      {
        rootMargin: this.options.rootMargin,
        threshold: this.options.threshold,
      }
    );

    // Observe all lazy load elements
    this.observeElements();
  }

  observeElements() {
    const elements = document.querySelectorAll(`
      ${this.options.imageSelector},
      ${this.options.backgroundSelector},
      ${this.options.videoSelector},
      ${this.options.iframeSelector}
    `);

    elements.forEach(element => {
      if (!this.loadedItems.has(element)) {
        this.observer.observe(element);
      }
    });
  }

  initScrollBasedLazyLoading() {
    const elements = document.querySelectorAll(`
      ${this.options.imageSelector},
      ${this.options.backgroundSelector},
      ${this.options.videoSelector},
      ${this.options.iframeSelector}
    `);

    const checkElements = () => {
      elements.forEach(element => {
        if (!this.loadedItems.has(element) && this.isInViewport(element)) {
          this.loadElement(element);
        }
      });
    };

    // Throttled scroll handler
    let ticking = false;
    const scrollHandler = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          checkElements();
          ticking = false;
        });
        ticking = true;
      }
    };

    // Initial check
    checkElements();

    // Add event listeners
    window.addEventListener('scroll', scrollHandler, { passive: true });
    window.addEventListener('resize', scrollHandler, { passive: true });
    window.addEventListener('orientationchange', scrollHandler, { passive: true });
  }

  isInViewport(element) {
    const rect = element.getBoundingClientRect();
    const margin = parseInt(this.options.rootMargin);

    return (
      rect.top <= window.innerHeight + margin &&
      rect.bottom >= -margin &&
      rect.left <= window.innerWidth + margin &&
      rect.right >= -margin
    );
  }

  async loadElement(element) {
    if (this.loadedItems.has(element)) return;

    this.loadedItems.add(element);
    element.classList.add(this.options.loadingClass);

    try {
      if (element.tagName === 'IMG') {
        await this.loadImage(element);
      } else if (element.tagName === 'VIDEO') {
        await this.loadVideo(element);
      } else if (element.tagName === 'IFRAME') {
        await this.loadIframe(element);
      } else if (element.dataset.bgSrc) {
        await this.loadBackgroundImage(element);
      }

      element.classList.remove(this.options.loadingClass);
      element.classList.add(this.options.loadedClass);

      // Dispatch custom event
      element.dispatchEvent(
        new CustomEvent('lazyloaded', {
          detail: { element },
        })
      );
    } catch (error) {
      this.handleLoadError(element, error);
    }
  }

  loadImage(img) {
    return new Promise((resolve, reject) => {
      const tempImg = new Image();

      tempImg.onload = () => {
        // Set optimal source
        const optimalSrc = this.getOptimalImageSource(img);
        img.src = optimalSrc;

        // Handle srcset and sizes
        if (img.dataset.srcset) {
          img.srcset = img.dataset.srcset;
        }
        if (img.dataset.sizes) {
          img.sizes = img.dataset.sizes;
        }

        this.handleImageLoad(img);
        resolve();
      };

      tempImg.onerror = () => {
        reject(new Error(`Failed to load image: ${img.dataset.src}`));
      };

      // Start loading
      tempImg.src = this.getOptimalImageSource(img);
    });
  }

  getOptimalImageSource(img) {
    const originalSrc = img.dataset.src;

    // Use WebP if supported and available
    if (this.webPSupported && img.dataset.webp) {
      return img.dataset.webp;
    }

    // Use fallback if available
    if (!this.webPSupported && img.dataset.fallback) {
      return img.dataset.fallback;
    }

    return originalSrc;
  }

  handleImageLoad(img) {
    // Remove placeholder class
    img.classList.remove('lazy-placeholder');

    // Remove any background placeholder
    img.style.background = '';

    // Add fade-in effect
    if (this.options.fadeInDuration > 0) {
      img.style.transition = `opacity ${this.options.fadeInDuration}ms ease-in-out`;
    }
  }

  loadVideo(video) {
    return new Promise((resolve, reject) => {
      // Set video source
      if (video.dataset.src) {
        video.src = video.dataset.src;
      }

      // Handle multiple sources
      const sources = video.querySelectorAll('source[data-src]');
      sources.forEach(source => {
        source.src = source.dataset.src;
        source.removeAttribute('data-src');
      });

      // Load video
      video.load();

      video.addEventListener('loadeddata', () => resolve(), { once: true });
      video.addEventListener('error', () => reject(new Error('Video load failed')), { once: true });
    });
  }

  loadIframe(iframe) {
    return new Promise((resolve, reject) => {
      iframe.onload = () => resolve();
      iframe.onerror = () => reject(new Error('Iframe load failed'));

      iframe.src = iframe.dataset.src;
    });
  }

  loadBackgroundImage(element) {
    return new Promise((resolve, reject) => {
      const tempImg = new Image();

      tempImg.onload = () => {
        const bgSrc =
          this.webPSupported && element.dataset.bgWebp
            ? element.dataset.bgWebp
            : element.dataset.bgSrc;

        element.style.backgroundImage = `url(${bgSrc})`;
        element.classList.add('bg-loaded');
        resolve();
      };

      tempImg.onerror = () => {
        reject(new Error(`Failed to load background image: ${element.dataset.bgSrc}`));
      };

      tempImg.src = element.dataset.bgSrc;
    });
  }

  handleLoadError(element, error) {
    console.warn('Lazy load error:', error);

    element.classList.remove(this.options.loadingClass);
    element.classList.add(this.options.errorClass);

    // Retry logic
    const retryCount = this.retryCount.get(element) || 0;
    if (retryCount < this.options.retryAttempts) {
      this.retryCount.set(element, retryCount + 1);

      setTimeout(
        () => {
          this.loadedItems.delete(element);
          element.classList.remove(this.options.errorClass);
          this.loadElement(element);
        },
        this.options.retryDelay * (retryCount + 1)
      );
    } else {
      // Try fallback image for images
      if (element.tagName === 'IMG' && element.dataset.fallback) {
        element.src = element.dataset.fallback;
        element.classList.remove(this.options.errorClass);
        element.classList.add(this.options.loadedClass);
      }

      // Dispatch error event
      element.dispatchEvent(
        new CustomEvent('lazyloaderror', {
          detail: { element, error },
        })
      );
    }
  }

  // Public API methods
  loadAll() {
    const elements = document.querySelectorAll(`
      ${this.options.imageSelector}:not(.${this.options.loadedClass}),
      ${this.options.backgroundSelector}:not(.${this.options.loadedClass}),
      ${this.options.videoSelector}:not(.${this.options.loadedClass}),
      ${this.options.iframeSelector}:not(.${this.options.loadedClass})
    `);

    elements.forEach(element => this.loadElement(element));
  }

  update() {
    if (this.observer) {
      this.observeElements();
    }
  }

  destroy() {
    if (this.observer) {
      this.observer.disconnect();
    }

    // Clear retry counts
    this.retryCount.clear();
    this.loadedItems.clear();

    // Remove enhanced class
    document.documentElement.classList.remove('js-lazy-load');
  }

  // Static factory method
  static init(options = {}) {
    return new LazyLoad(options);
  }
}

// Auto-initialize if not using module system
if (typeof window !== 'undefined' && !window.moduleSystem) {
  document.addEventListener('DOMContentLoaded', () => {
    LazyLoad.init();
  });
}
