/**
 * Dynamic Module Loader with Performance Optimization
 * Handles intelligent loading of JavaScript modules based on device capabilities
 */

export class ModuleLoader {
  constructor() {
    this.loadedModules = new Map();
    this.pendingModules = new Map();
    this.retryAttempts = new Map();
    this.maxRetries = 3;
    this.timeouts = new Map();
    this.performanceMetrics = new Map();
  }

  async loadModule(moduleName, options = {}) {
    const {
      timeout = 10000,
      retry = true,
      priority = 'normal',
      preload = false,
      fallback = null
    } = options;

    // Return cached module if already loaded
    if (this.loadedModules.has(moduleName)) {
      return this.loadedModules.get(moduleName);
    }

    // Wait for pending module if currently loading
    if (this.pendingModules.has(moduleName)) {
      return this.pendingModules.get(moduleName);
    }

    // Create loading promise
    const loadingPromise = this.createLoadingPromise(moduleName, {
      timeout,
      retry,
      priority,
      preload,
      fallback
    });

    this.pendingModules.set(moduleName, loadingPromise);

    try {
      const module = await loadingPromise;
      this.loadedModules.set(moduleName, module);
      this.pendingModules.delete(moduleName);
      return module;
    } catch (error) {
      this.pendingModules.delete(moduleName);
      
      if (retry && this.shouldRetry(moduleName)) {
        return this.retryLoad(moduleName, options);
      }
      
      if (fallback) {
        return this.loadFallback(moduleName, fallback);
      }
      
      throw error;
    }
  }

  async createLoadingPromise(moduleName, options) {
    const startTime = performance.now();
    
    try {
      // Determine the best loading strategy
      const strategy = this.getLoadingStrategy(moduleName, options);
      
      let module;
      switch (strategy) {
        case 'dynamic-import':
          module = await this.loadWithDynamicImport(moduleName, options);
          break;
        case 'fetch-eval':
          module = await this.loadWithFetchEval(moduleName, options);
          break;
        case 'script-tag':
          module = await this.loadWithScriptTag(moduleName, options);
          break;
        default:
          throw new Error(`Unknown loading strategy: ${strategy}`);
      }

      // Track performance metrics
      const loadTime = performance.now() - startTime;
      this.performanceMetrics.set(moduleName, {
        loadTime,
        strategy,
        timestamp: Date.now(),
        success: true
      });

      console.log(`✅ Module ${moduleName} loaded in ${loadTime.toFixed(2)}ms using ${strategy}`);
      
      return module;
    } catch (error) {
      const loadTime = performance.now() - startTime;
      this.performanceMetrics.set(moduleName, {
        loadTime,
        strategy: 'failed',
        timestamp: Date.now(),
        success: false,
        error: error.message
      });

      throw error;
    }
  }

  getLoadingStrategy(moduleName, options) {
    // Check browser capabilities
    const hasModuleSupport = 'noModule' in document.createElement('script');
    const hasFetch = 'fetch' in window;
    
    // Prefer dynamic imports for modern browsers
    if (hasModuleSupport && !options.forceLegacy) {
      return 'dynamic-import';
    }
    
    // Use fetch for capable browsers
    if (hasFetch && !options.forceScriptTag) {
      return 'fetch-eval';
    }
    
    // Fallback to script tag injection
    return 'script-tag';
  }

  async loadWithDynamicImport(moduleName, options) {
    const modulePath = this.getModulePath(moduleName, 'esm');
    
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error(`Module ${moduleName} load timeout`));
      }, options.timeout);

      import(modulePath)
        .then(module => {
          clearTimeout(timeoutId);
          resolve(module.default || module);
        })
        .catch(error => {
          clearTimeout(timeoutId);
          reject(error);
        });
    });
  }

  async loadWithFetchEval(moduleName, options) {
    const modulePath = this.getModulePath(moduleName, 'umd');
    
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error(`Module ${moduleName} fetch timeout`));
      }, options.timeout);

      fetch(modulePath)
        .then(response => {
          clearTimeout(timeoutId);
          if (!response.ok) {
            throw new Error(`Failed to fetch ${moduleName}: ${response.status}`);
          }
          return response.text();
        })
        .then(code => {
          // Create a safe evaluation context
          const moduleScope = this.createModuleScope(moduleName);
          const wrappedCode = this.wrapModuleCode(code, moduleName);
          
          // Evaluate the module code
          const moduleFunction = new Function('module', 'exports', 'require', wrappedCode);
          moduleFunction.call(moduleScope, moduleScope.module, moduleScope.exports, moduleScope.require);
          
          resolve(moduleScope.module.exports);
        })
        .catch(error => {
          clearTimeout(timeoutId);
          reject(error);
        });
    });
  }

  async loadWithScriptTag(moduleName, options) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      const modulePath = this.getModulePath(moduleName, 'iife');
      
      const timeoutId = setTimeout(() => {
        script.remove();
        reject(new Error(`Module ${moduleName} script load timeout`));
      }, options.timeout);

      script.onload = () => {
        clearTimeout(timeoutId);
        script.remove();
        
        // Look for the module in global scope
        const globalName = this.getGlobalName(moduleName);
        if (window[globalName]) {
          resolve(window[globalName]);
        } else {
          reject(new Error(`Module ${moduleName} not found in global scope`));
        }
      };

      script.onerror = () => {
        clearTimeout(timeoutId);
        script.remove();
        reject(new Error(`Failed to load script for ${moduleName}`));
      };

      script.src = modulePath;
      script.async = true;
      document.head.appendChild(script);
    });
  }

  getModulePath(moduleName, format = 'esm') {
    const baseUrl = '/static/js/dist/';
    const moduleMap = {
      'mobile-nav': `features/mobile-nav.${format}.js`,
      'lazy-load': `features/lazy-load.${format}.js`,
      'gallery': `features/gallery.${format}.js`,
      'analytics': `features/analytics.${format}.js`,
      'performance-monitor': `features/performance-monitor.${format}.js`,
      'social-features': `features/social-features.${format}.js`,
      'whatsapp-chat': `features/whatsapp-chat.${format}.js`,
      'pricing-calculator': `features/pricing-calculator.${format}.js`,
      'testimonial-form': `features/testimonial-form.${format}.js`,
      'contact-form': `features/contact-form.${format}.js`
    };

    const modulePath = moduleMap[moduleName];
    if (!modulePath) {
      throw new Error(`Unknown module: ${moduleName}`);
    }

    return baseUrl + modulePath;
  }

  getGlobalName(moduleName) {
    const globalMap = {
      'mobile-nav': 'MobileNav',
      'lazy-load': 'LazyLoad',
      'gallery': 'Gallery',
      'analytics': 'Analytics',
      'performance-monitor': 'PerformanceMonitor',
      'social-features': 'SocialFeatures',
      'whatsapp-chat': 'WhatsAppChat',
      'pricing-calculator': 'PricingCalculator',
      'testimonial-form': 'TestimonialForm',
      'contact-form': 'ContactForm'
    };

    return globalMap[moduleName] || moduleName.replace(/-./g, x => x[1].toUpperCase());
  }

  createModuleScope(moduleName) {
    const exports = {};
    const module = { exports };
    
    const require = (name) => {
      if (this.loadedModules.has(name)) {
        return this.loadedModules.get(name);
      }
      throw new Error(`Module ${name} not loaded`);
    };

    return { module, exports, require };
  }

  wrapModuleCode(code, moduleName) {
    return `
      try {
        ${code}
      } catch (error) {
        console.error('Error in module ${moduleName}:', error);
        throw error;
      }
    `;
  }

  shouldRetry(moduleName) {
    const attempts = this.retryAttempts.get(moduleName) || 0;
    return attempts < this.maxRetries;
  }

  async retryLoad(moduleName, options) {
    const attempts = this.retryAttempts.get(moduleName) || 0;
    this.retryAttempts.set(moduleName, attempts + 1);
    
    // Exponential backoff
    const delay = Math.pow(2, attempts) * 1000;
    await new Promise(resolve => setTimeout(resolve, delay));
    
    console.warn(`🔄 Retrying module ${moduleName} (attempt ${attempts + 1})`);
    return this.loadModule(moduleName, options);
  }

  async loadFallback(moduleName, fallback) {
    console.warn(`⚠️ Loading fallback for ${moduleName}: ${fallback.name || fallback}`);
    
    if (typeof fallback === 'string') {
      return this.loadModule(fallback);
    }
    
    if (typeof fallback === 'function') {
      return fallback();
    }
    
    return fallback;
  }

  // Preload modules based on user interaction patterns
  preloadModule(moduleName, options = {}) {
    const link = document.createElement('link');
    link.rel = 'modulepreload';
    link.href = this.getModulePath(moduleName, 'esm');
    
    link.onload = () => {
      console.log(`📦 Preloaded module: ${moduleName}`);
    };
    
    link.onerror = () => {
      console.warn(`❌ Failed to preload module: ${moduleName}`);
    };
    
    document.head.appendChild(link);
  }

  // Preload modules for likely user interactions
  preloadInteractionModules() {
    const interactionMap = {
      gallery: ['gallery'],
      pricing: ['pricing-calculator'],
      contact: ['contact-form'],
      testimonials: ['testimonial-form'],
      whatsapp: ['whatsapp-chat']
    };

    Object.entries(interactionMap).forEach(([trigger, modules]) => {
      const elements = document.querySelectorAll(`[data-preload="${trigger}"]`);
      if (elements.length > 0) {
        modules.forEach(module => this.preloadModule(module));
      }
    });
  }

  // Get performance metrics for monitoring
  getPerformanceMetrics() {
    return Object.fromEntries(this.performanceMetrics);
  }

  // Clean up resources
  cleanup() {
    this.timeouts.forEach(timeoutId => clearTimeout(timeoutId));
    this.timeouts.clear();
    this.retryAttempts.clear();
  }
}