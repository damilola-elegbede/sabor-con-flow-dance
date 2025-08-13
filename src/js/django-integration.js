/**
 * Django Template Integration for Bundled JavaScript
 * Provides utilities for loading the correct bundles in Django templates
 */

class DjangoBundleLoader {
  constructor() {
    this.bundleManifest = null;
    this.loadedBundles = new Set();
    this.init();
  }

  async init() {
    await this.loadManifest();
    this.setupDynamicLoading();
  }

  async loadManifest() {
    try {
      const response = await fetch('/static/js/dist/manifest.json');
      this.bundleManifest = await response.json();
    } catch (error) {
      console.warn('Could not load bundle manifest:', error);
      // Fallback to development bundle names
      this.bundleManifest = this.getDevManifest();
    }
  }

  getDevManifest() {
    return {
      main: 'main.bundle.js',
      vendor: 'vendor.bundle.js',
      mobile: 'mobile.bundle.js',
      gallery: 'gallery.bundle.js',
      analytics: 'analytics.bundle.js',
      home: 'home.bundle.js',
      contact: 'contact.bundle.js',
      pricing: 'pricing.bundle.js',
      'lazy-load': 'lazy-load.bundle.js',
      'performance-monitor': 'performance-monitor.bundle.js',
      'social-features': 'social-features.bundle.js',
      'whatsapp-chat': 'whatsapp-chat.bundle.js',
    };
  }

  getBundlePath(bundleName) {
    if (!this.bundleManifest) {
      return `/static/js/dist/${bundleName}.bundle.js`;
    }

    const bundleFile = this.bundleManifest[bundleName];
    if (!bundleFile) {
      console.warn(`Bundle ${bundleName} not found in manifest`);
      return `/static/js/dist/${bundleName}.bundle.js`;
    }

    return `/static/js/dist/${bundleFile}`;
  }

  async loadBundle(bundleName, options = {}) {
    if (this.loadedBundles.has(bundleName)) {
      return Promise.resolve();
    }

    const bundlePath = this.getBundlePath(bundleName);

    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = bundlePath;
      script.async = true;

      if (options.defer) {
        script.defer = true;
      }

      script.onload = () => {
        this.loadedBundles.add(bundleName);
        resolve();
      };

      script.onerror = () => {
        reject(new Error(`Failed to load bundle: ${bundleName}`));
      };

      document.head.appendChild(script);
    });
  }

  async loadPageBundle() {
    const pageClass = document.body.className;
    const currentPath = window.location.pathname;

    // Determine page-specific bundle to load
    let pageBundle = null;

    if (pageClass.includes('page-home') || currentPath === '/') {
      pageBundle = 'home';
    } else if (pageClass.includes('page-contact') || currentPath.includes('/contact')) {
      pageBundle = 'contact';
    } else if (pageClass.includes('page-pricing') || currentPath.includes('/pricing')) {
      pageBundle = 'pricing';
    }

    if (pageBundle) {
      try {
        await this.loadBundle(pageBundle);
        // Page bundle loaded: ${pageBundle}
      } catch (error) {
        console.warn(`Failed to load page bundle ${pageBundle}:`, error);
      }
    }
  }

  async loadFeatureBundle(feature) {
    const featureBundles = {
      gallery: 'gallery',
      analytics: 'analytics',
      whatsapp: 'whatsapp-chat',
      social: 'social-features',
      performance: 'performance-monitor',
    };

    const bundleName = featureBundles[feature];
    if (bundleName) {
      try {
        await this.loadBundle(bundleName);
        // Feature bundle loaded: ${feature}
      } catch (error) {
        console.warn(`Failed to load feature bundle ${feature}:`, error);
      }
    }
  }

  setupDynamicLoading() {
    // Load bundles based on data attributes
    document.querySelectorAll('[data-requires-bundle]').forEach(element => {
      const bundleName = element.dataset.requiresBundle;

      // Load on interaction
      const loadOnInteraction = () => {
        this.loadBundle(bundleName);
      };

      element.addEventListener('mouseenter', loadOnInteraction, { once: true, passive: true });
      element.addEventListener('touchstart', loadOnInteraction, { once: true, passive: true });
      element.addEventListener('focus', loadOnInteraction, { once: true, passive: true });
    });

    // Load bundles based on intersection observer
    if ('IntersectionObserver' in window) {
      const bundleObserver = new IntersectionObserver(
        entries => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const bundleName = entry.target.dataset.lazyBundle;
              if (bundleName) {
                this.loadBundle(bundleName);
                bundleObserver.unobserve(entry.target);
              }
            }
          });
        },
        {
          rootMargin: '50px',
        }
      );

      document.querySelectorAll('[data-lazy-bundle]').forEach(element => {
        bundleObserver.observe(element);
      });
    }
  }

  // Public API for Django templates
  static async loadCriticalBundles() {
    const loader = new DjangoBundleLoader();

    // Load vendor bundle first
    await loader.loadBundle('vendor');

    // Load main bundle
    await loader.loadBundle('main');

    // Load page-specific bundle
    await loader.loadPageBundle();

    return loader;
  }

  static async loadFeature(feature) {
    const loader = window.djangoBundleLoader || new DjangoBundleLoader();
    await loader.loadFeatureBundle(feature);
  }
}

// Initialize and expose globally for Django templates
if (typeof window !== 'undefined') {
  window.DjangoBundleLoader = DjangoBundleLoader;

  // Auto-initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', async () => {
      window.djangoBundleLoader = await DjangoBundleLoader.loadCriticalBundles();
    });
  } else {
    DjangoBundleLoader.loadCriticalBundles().then(loader => {
      window.djangoBundleLoader = loader;
    });
  }
}

export default DjangoBundleLoader;
