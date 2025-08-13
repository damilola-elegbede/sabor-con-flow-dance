/**
 * Vendor Bundle - Third-party libraries and polyfills
 * This bundle contains all external dependencies
 */

// Core polyfills for older browsers
import 'intersection-observer';

// Web Vitals for performance monitoring
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

// Export web vitals for use in other modules
export { getCLS, getFID, getFCP, getLCP, getTTFB };

// Utility functions for vendor integration
export const VendorUtils = {
  // Initialize external analytics
  initAnalytics: () => {
    if (typeof gtag === 'function') {
      console.log('✅ Google Analytics initialized');
    }
  },

  // Initialize external chat widgets
  initChat: () => {
    // WhatsApp integration
    if (window.WhatsAppWidget) {
      window.WhatsAppWidget.init();
    }
  },

  // Initialize external social widgets
  initSocial: () => {
    // Facebook SDK
    if (window.FB) {
      window.FB.init({
        appId: process.env.FACEBOOK_APP_ID,
        version: 'v18.0',
      });
    }
  },

  // Initialize external booking widgets
  initBooking: () => {
    // Calendly integration
    if (window.Calendly) {
      console.log('✅ Calendly widget ready');
    }
  },

  // Check if vendor is loaded
  isVendorLoaded: vendor => {
    const vendors = {
      'google-analytics': () => typeof gtag === 'function',
      facebook: () => typeof FB !== 'undefined',
      calendly: () => typeof Calendly !== 'undefined',
      whatsapp: () => typeof WhatsAppWidget !== 'undefined',
    };

    return vendors[vendor] ? vendors[vendor]() : false;
  },
};

// Load external scripts dynamically
export const ExternalLoader = {
  loadScript: (src, attributes = {}) => {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = src;
      script.async = true;

      Object.keys(attributes).forEach(key => {
        script.setAttribute(key, attributes[key]);
      });

      script.onload = resolve;
      script.onerror = reject;

      document.head.appendChild(script);
    });
  },

  // Load Google Analytics
  loadGoogleAnalytics: async measurementId => {
    try {
      await ExternalLoader.loadScript(
        `https://www.googletagmanager.com/gtag/js?id=${measurementId}`
      );

      window.dataLayer = window.dataLayer || [];
      window.gtag = function gtag(...args) {
        window.dataLayer.push(args);
      };
      window.gtag('js', new Date());
      window.gtag('config', measurementId);
      return true;
    } catch (error) {
      console.error('Failed to load Google Analytics:', error);
      return false;
    }
  },

  // Load Facebook SDK
  loadFacebookSDK: async appId => {
    try {
      await ExternalLoader.loadScript('https://connect.facebook.net/en_US/sdk.js');

      window.FB.init({
        appId,
        version: 'v18.0',
        cookie: true,
        xfbml: true,
      });

      return true;
    } catch (error) {
      console.error('Failed to load Facebook SDK:', error);
      return false;
    }
  },

  // Load Calendly
  loadCalendly: async () => {
    try {
      await ExternalLoader.loadScript('https://assets.calendly.com/assets/external/widget.js');
      return true;
    } catch (error) {
      console.error('Failed to load Calendly:', error);
      return false;
    }
  },
};

// Performance monitoring with Web Vitals
export const WebVitalsMonitor = {
  init: () => {
    // Track Core Web Vitals
    getCLS(metric => {
      console.log('CLS:', metric);
      if (window.gtag) {
        window.gtag('event', 'web_vitals', {
          name: metric.name,
          value: Math.round(metric.value * 1000),
          event_label: metric.id,
          non_interaction: true,
        });
      }
    });

    getFID(metric => {
      console.log('FID:', metric);
      if (window.gtag) {
        window.gtag('event', 'web_vitals', {
          name: metric.name,
          value: Math.round(metric.value),
          event_label: metric.id,
          non_interaction: true,
        });
      }
    });

    getFCP(metric => {
      console.log('FCP:', metric);
      if (window.gtag) {
        window.gtag('event', 'web_vitals', {
          name: metric.name,
          value: Math.round(metric.value),
          event_label: metric.id,
          non_interaction: true,
        });
      }
    });

    getLCP(metric => {
      console.log('LCP:', metric);
      if (window.gtag) {
        window.gtag('event', 'web_vitals', {
          name: metric.name,
          value: Math.round(metric.value),
          event_label: metric.id,
          non_interaction: true,
        });
      }
    });

    getTTFB(metric => {
      console.log('TTFB:', metric);
      if (window.gtag) {
        window.gtag('event', 'web_vitals', {
          name: metric.name,
          value: Math.round(metric.value),
          event_label: metric.id,
          non_interaction: true,
        });
      }
    });
  },
};

// Initialize all vendor utilities
export const initVendors = () => {
  VendorUtils.initAnalytics();
  VendorUtils.initChat();
  VendorUtils.initSocial();
  VendorUtils.initBooking();
  WebVitalsMonitor.init();
};

// Auto-initialize if not using module system
if (typeof window !== 'undefined' && !window.moduleSystem) {
  document.addEventListener('DOMContentLoaded', initVendors);
}
