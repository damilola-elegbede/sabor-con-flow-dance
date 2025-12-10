/**
 * Feature Detection Utilities
 * Detects browser capabilities and adds appropriate classes/fallbacks
 */

export class FeatureDetection {
  static features = new Map();

  static detect() {
    // Core feature detection
    this.detectIntersectionObserver();
    this.detectWebP();
    this.detectServiceWorker();
    this.detectLocalStorage();
    this.detectTouchSupport();
    this.detectNetworkInformation();
    this.detectPreferredMotion();
    this.detectModuleSupport();
    this.detectCSSGrid();
    this.detectLazyLoading();
    this.detectWebGL();
    this.detectBatteryAPI();

    // Add feature classes to document
    this.addFeatureClasses();

    // Log detected features in development
    if (process.env.NODE_ENV === 'development') {
      console.log('🔍 Feature Detection Results:', Object.fromEntries(this.features));
    }
  }

  static detectIntersectionObserver() {
    const supported = 'IntersectionObserver' in window;
    this.features.set('intersection-observer', supported);
    
    if (!supported) {
      // Load polyfill if needed
      this.loadPolyfill('intersection-observer');
    }
  }

  static detectWebP() {
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    const supported = canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    this.features.set('webp', supported);
  }

  static detectServiceWorker() {
    const supported = 'serviceWorker' in navigator;
    this.features.set('service-worker', supported);
  }

  static detectLocalStorage() {
    let supported = false;
    try {
      const test = 'localStorage-test';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      supported = true;
    } catch (e) {
      supported = false;
    }
    this.features.set('local-storage', supported);
  }

  static detectTouchSupport() {
    const supported = 'ontouchstart' in window || 
                     navigator.maxTouchPoints > 0 || 
                     navigator.msMaxTouchPoints > 0;
    this.features.set('touch', supported);
  }

  static detectNetworkInformation() {
    const supported = 'connection' in navigator;
    this.features.set('network-information', supported);
    
    if (supported) {
      const connection = navigator.connection;
      this.features.set('connection-type', connection.effectiveType);
      this.features.set('save-data', connection.saveData || false);
    }
  }

  static detectPreferredMotion() {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.features.set('prefers-reduced-motion', prefersReduced);
  }

  static detectModuleSupport() {
    const script = document.createElement('script');
    const supported = 'noModule' in script;
    this.features.set('es-modules', supported);
  }

  static detectCSSGrid() {
    const supported = CSS.supports('display', 'grid');
    this.features.set('css-grid', supported);
  }

  static detectLazyLoading() {
    const supported = 'loading' in HTMLImageElement.prototype;
    this.features.set('native-lazy-loading', supported);
  }

  static detectWebGL() {
    let supported = false;
    try {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      supported = !!context;
    } catch (e) {
      supported = false;
    }
    this.features.set('webgl', supported);
  }

  static detectBatteryAPI() {
    const supported = 'getBattery' in navigator;
    this.features.set('battery-api', supported);
  }

  static addFeatureClasses() {
    const html = document.documentElement;
    
    this.features.forEach((supported, feature) => {
      if (typeof supported === 'boolean') {
        html.classList.add(supported ? feature : `no-${feature}`);
      } else {
        html.classList.add(`${feature}-${supported}`);
      }
    });

    // Add special classes for common combinations
    if (this.features.get('touch') && !this.features.get('css-grid')) {
      html.classList.add('legacy-mobile');
    }

    if (!this.features.get('es-modules')) {
      html.classList.add('legacy-browser');
    }

    if (this.features.get('save-data')) {
      html.classList.add('data-saver');
    }
  }

  static async loadPolyfill(feature) {
    const polyfills = {
      'intersection-observer': () => {
        return import('intersection-observer');
      }
    };

    const polyfillLoader = polyfills[feature];
    if (polyfillLoader) {
      try {
        await polyfillLoader();
        console.log(`✅ Polyfill loaded for ${feature}`);
      } catch (error) {
        console.warn(`❌ Failed to load polyfill for ${feature}:`, error);
      }
    }
  }

  static hasFeature(feature) {
    return this.features.get(feature) || false;
  }

  static getFeature(feature) {
    return this.features.get(feature);
  }

  static getAllFeatures() {
    return Object.fromEntries(this.features);
  }

  // Get device capabilities score (0-100)
  static getDeviceScore() {
    const weights = {
      'es-modules': 20,
      'intersection-observer': 15,
      'service-worker': 15,
      'webp': 10,
      'css-grid': 10,
      'native-lazy-loading': 10,
      'local-storage': 10,
      'webgl': 5,
      'network-information': 5
    };

    let score = 0;
    this.features.forEach((supported, feature) => {
      if (supported && weights[feature]) {
        score += weights[feature];
      }
    });

    return Math.min(score, 100);
  }

  // Determine if device should receive enhanced experience
  static shouldUseEnhancedExperience() {
    const score = this.getDeviceScore();
    const hasSlowConnection = this.features.get('connection-type') === 'slow-2g' || 
                             this.features.get('connection-type') === '2g';
    const saveData = this.features.get('save-data');

    // Don't enhance for very low-end devices or slow connections
    if (score < 40 || hasSlowConnection || saveData) {
      return false;
    }

    return true;
  }

  // Get recommended bundle strategy
  static getRecommendedBundleStrategy() {
    const score = this.getDeviceScore();
    const esModules = this.features.get('es-modules');
    const slowConnection = this.features.get('connection-type') === 'slow-2g' || 
                          this.features.get('connection-type') === '2g';

    if (slowConnection || this.features.get('save-data')) {
      return 'minimal'; // Load only critical features
    }

    if (score >= 80 && esModules) {
      return 'modern'; // Use ES modules and latest features
    }

    if (score >= 60) {
      return 'enhanced'; // Use transpiled bundles with most features
    }

    return 'basic'; // Use basic bundles with polyfills
  }

  // Monitor feature support changes (for PWAs)
  static startMonitoring() {
    // Monitor network changes
    if ('connection' in navigator) {
      navigator.connection.addEventListener('change', () => {
        this.detectNetworkInformation();
        this.addFeatureClasses();
      });
    }

    // Monitor reduced motion preference changes
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    motionQuery.addListener(() => {
      this.detectPreferredMotion();
      this.addFeatureClasses();
    });

    // Monitor orientation changes for mobile
    window.addEventListener('orientationchange', () => {
      setTimeout(() => {
        // Re-detect touch capabilities after orientation change
        this.detectTouchSupport();
        this.addFeatureClasses();
      }, 100);
    });
  }
}