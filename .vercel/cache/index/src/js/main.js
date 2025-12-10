/**
 * Main Entry Point - Progressive Enhancement Architecture
 * Sabor Con Flow Dance - SPEC_06 Group A Task 3
 */

import { PerformanceMonitor } from '@features/performance-monitor';
import { ProgressiveEnhancement } from '@utils/progressive-enhancement';
import { FeatureDetection } from '@utils/feature-detection';
import { ModuleLoader } from '@utils/module-loader';

class SaborConFlowApp {
  constructor() {
    this.modules = new Map();
    this.loadingModules = new Set();
    this.performanceMonitor = null;
    
    // Core configuration
    this.config = {
      enableAnalytics: window.ENABLE_ANALYTICS || false,
      enablePerformanceMonitoring: true,
      lazyLoadThreshold: '50px',
      moduleTimeout: 5000,
      retryAttempts: 3
    };
    
    this.init();
  }

  async init() {
    try {
      // Initialize performance monitoring first
      if (this.config.enablePerformanceMonitoring) {
        this.performanceMonitor = new PerformanceMonitor();
        this.performanceMonitor.start();
      }

      // Feature detection and progressive enhancement
      FeatureDetection.detect();
      ProgressiveEnhancement.init();

      // Load critical modules immediately
      await this.loadCriticalModules();

      // Set up lazy loading for non-critical modules
      this.setupLazyLoading();

      // Initialize core functionality that works without JS
      this.enhanceBasicFunctionality();

      // Set up module loading based on user interactions
      this.setupInteractionBasedLoading();

      console.log('✅ Sabor Con Flow app initialized successfully');
      
    } catch (error) {
      console.error('❌ Failed to initialize app:', error);
      this.handleInitializationError(error);
    }
  }

  async loadCriticalModules() {
    const criticalModules = [
      'mobile-nav',
      'lazy-load'
    ];

    const loadPromises = criticalModules.map(module => 
      this.loadModule(module, { critical: true })
    );

    try {
      await Promise.allSettled(loadPromises);
    } catch (error) {
      console.warn('Some critical modules failed to load:', error);
    }
  }

  async loadModule(moduleName, options = {}) {
    if (this.modules.has(moduleName)) {
      return this.modules.get(moduleName);
    }

    if (this.loadingModules.has(moduleName)) {
      // Wait for existing load to complete
      while (this.loadingModules.has(moduleName)) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      return this.modules.get(moduleName);
    }

    this.loadingModules.add(moduleName);

    try {
      const moduleInstance = await this.dynamicImport(moduleName, options);
      this.modules.set(moduleName, moduleInstance);
      this.loadingModules.delete(moduleName);
      
      // Track module load performance
      if (this.performanceMonitor) {
        this.performanceMonitor.trackCustomEvent('module_loaded', {
          module: moduleName,
          critical: options.critical || false
        });
      }

      return moduleInstance;
    } catch (error) {
      this.loadingModules.delete(moduleName);
      console.error(`Failed to load module ${moduleName}:`, error);
      throw error;
    }
  }

  async dynamicImport(moduleName, options = {}) {
    const moduleMap = {
      'mobile-nav': () => import('@features/mobile-nav'),
      'lazy-load': () => import('@features/lazy-load'),
      'gallery': () => import('@features/gallery'),
      'analytics': () => import('@features/analytics'),
      'performance-monitor': () => import('@features/performance-monitor'),
      'social-features': () => import('@features/social-features'),
      'whatsapp-chat': () => import('@features/whatsapp-chat'),
      'pricing-calculator': () => import('@features/pricing-calculator'),
      'testimonial-form': () => import('@features/testimonial-form'),
      'contact-form': () => import('@features/contact-form')
    };

    const importFunction = moduleMap[moduleName];
    if (!importFunction) {
      throw new Error(`Unknown module: ${moduleName}`);
    }

    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error(`Module ${moduleName} load timeout`)), 
                 options.timeout || this.config.moduleTimeout);
    });

    const modulePromise = importFunction();
    const module = await Promise.race([modulePromise, timeoutPromise]);
    
    // Initialize the module if it has an init method
    if (module.default && typeof module.default.init === 'function') {
      await module.default.init(options);
    }

    return module.default || module;
  }

  setupLazyLoading() {
    // Use Intersection Observer for module lazy loading
    if ('IntersectionObserver' in window) {
      const moduleObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const element = entry.target;
            const requiredModules = element.dataset.requiresModules;
            
            if (requiredModules) {
              const modules = requiredModules.split(',').map(m => m.trim());
              modules.forEach(module => this.loadModule(module));
              moduleObserver.unobserve(element);
            }
          }
        });
      }, {
        rootMargin: this.config.lazyLoadThreshold,
        threshold: 0.1
      });

      // Observe elements that require specific modules
      document.querySelectorAll('[data-requires-modules]').forEach(el => {
        moduleObserver.observe(el);
      });
    }
  }

  setupInteractionBasedLoading() {
    // Load modules based on user interactions
    const interactionMap = {
      'gallery': ['.gallery-trigger', '.media-item'],
      'pricing-calculator': ['.pricing-calculator'],
      'whatsapp-chat': ['.whatsapp-button'],
      'social-features': ['.social-share', '.social-links'],
      'testimonial-form': ['.testimonial-form'],
      'contact-form': ['.contact-form']
    };

    Object.entries(interactionMap).forEach(([module, selectors]) => {
      selectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(element => {
          const loadOnInteraction = () => {
            this.loadModule(module);
            element.removeEventListener('mouseenter', loadOnInteraction);
            element.removeEventListener('touchstart', loadOnInteraction);
            element.removeEventListener('focus', loadOnInteraction);
          };

          // Load on various interaction types
          element.addEventListener('mouseenter', loadOnInteraction, { passive: true });
          element.addEventListener('touchstart', loadOnInteraction, { passive: true });
          element.addEventListener('focus', loadOnInteraction, { passive: true });
        });
      });
    });
  }

  enhanceBasicFunctionality() {
    // Enhance forms that work without JavaScript
    this.enhanceBasicForms();
    
    // Enhance navigation that works without JavaScript
    this.enhanceBasicNavigation();
    
    // Enhance basic interactions
    this.enhanceBasicInteractions();
  }

  enhanceBasicForms() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
      // Add basic validation enhancement
      form.addEventListener('submit', (e) => {
        if (!form.checkValidity()) {
          e.preventDefault();
          form.classList.add('was-validated');
        }
      });

      // Real-time validation for better UX
      const inputs = form.querySelectorAll('input, textarea, select');
      inputs.forEach(input => {
        input.addEventListener('blur', () => {
          if (input.checkValidity()) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
          } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
          }
        });
      });
    });
  }

  enhanceBasicNavigation() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(link => {
      link.addEventListener('click', (e) => {
        const targetId = link.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        
        if (targetElement) {
          e.preventDefault();
          targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  }

  enhanceBasicInteractions() {
    // Add loading states to buttons
    document.querySelectorAll('button[type="submit"]').forEach(button => {
      button.addEventListener('click', () => {
        if (button.form && button.form.checkValidity()) {
          button.disabled = true;
          button.textContent = 'Loading...';
          
          // Re-enable after timeout as fallback
          setTimeout(() => {
            button.disabled = false;
            button.textContent = button.dataset.originalText || 'Submit';
          }, 5000);
        }
      });
    });

    // Auto-dismiss alerts
    document.querySelectorAll('.alert[data-auto-dismiss]').forEach(alert => {
      const delay = parseInt(alert.dataset.autoDismiss) || 5000;
      setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
      }, delay);
    });
  }

  handleInitializationError(error) {
    // Fallback: ensure basic functionality still works
    console.error('App initialization failed, falling back to basic functionality');
    
    // Send error to analytics if available
    if (window.gtag) {
      window.gtag('event', 'exception', {
        description: error.message,
        fatal: false
      });
    }

    // Ensure critical features still work
    this.enhanceBasicFunctionality();
  }

  // Public API for external module loading
  static async loadModule(moduleName, options = {}) {
    if (!window.saborConFlowApp) {
      console.warn('Main app not initialized, creating temporary loader');
      const app = new SaborConFlowApp();
      return app.loadModule(moduleName, options);
    }
    return window.saborConFlowApp.loadModule(moduleName, options);
  }

  // Public API for feature detection
  static hasFeature(feature) {
    return FeatureDetection.hasFeature(feature);
  }
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.saborConFlowApp = new SaborConFlowApp();
  });
} else {
  window.saborConFlowApp = new SaborConFlowApp();
}

// Export for use in other modules
export default SaborConFlowApp;