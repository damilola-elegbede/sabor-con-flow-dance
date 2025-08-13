/**
 * Performance Monitor - Core Web Vitals and Custom Metrics
 * Tracks performance metrics and sends to analytics
 */

export default class PerformanceMonitor {
  constructor(options = {}) {
    this.options = {
      enableWebVitals: true,
      enableCustomMetrics: true,
      enableNavigationTiming: true,
      enableResourceTiming: true,
      enableUserTiming: true,
      sampleRate: 1.0, // 100% sampling by default
      bufferSize: 100,
      sendInterval: 30000, // 30 seconds
      endpoint: '/api/performance', // Custom endpoint for performance data
      ...options,
    };

    this.metrics = new Map();
    this.buffer = [];
    this.observers = new Map();
    this.startTime = performance.now();

    this.init();
  }

  init() {
    // Only monitor if we should sample this session
    if (Math.random() > this.options.sampleRate) {
      return;
    }

    this.setupWebVitals();
    this.setupCustomMetrics();
    this.setupNavigationTiming();
    this.setupResourceTiming();
    this.setupUserTiming();
    this.setupSendInterval();

    console.log('🔍 Performance monitoring started');
  }

  setupWebVitals() {
    if (!this.options.enableWebVitals) return;

    // Track Core Web Vitals
    this.trackCLS();
    this.trackFID();
    this.trackLCP();
    this.trackFCP();
    this.trackTTFB();
  }

  trackCLS() {
    if (!('PerformanceObserver' in window)) return;

    try {
      const clsObserver = new PerformanceObserver(list => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) {
            this.recordMetric('CLS', {
              value: entry.value,
              sources:
                entry.sources?.map(source => ({
                  element: source.node?.tagName || 'unknown',
                  previousRect: source.previousRect,
                  currentRect: source.currentRect,
                })) || [],
            });
          }
        }
      });

      clsObserver.observe({ entryTypes: ['layout-shift'] });
      this.observers.set('cls', clsObserver);
    } catch (e) {
      console.warn('CLS tracking not supported');
    }
  }

  trackFID() {
    if (!('PerformanceObserver' in window)) return;

    try {
      const fidObserver = new PerformanceObserver(list => {
        for (const entry of list.getEntries()) {
          this.recordMetric('FID', {
            value: entry.processingStart - entry.startTime,
            startTime: entry.startTime,
            processingStart: entry.processingStart,
            processingEnd: entry.processingEnd,
          });
        }
      });

      fidObserver.observe({ entryTypes: ['first-input'] });
      this.observers.set('fid', fidObserver);
    } catch (e) {
      console.warn('FID tracking not supported');
    }
  }

  trackLCP() {
    if (!('PerformanceObserver' in window)) return;

    try {
      const lcpObserver = new PerformanceObserver(list => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];

        this.recordMetric('LCP', {
          value: lastEntry.startTime,
          element: lastEntry.element?.tagName || 'unknown',
          url: lastEntry.url || '',
          size: lastEntry.size || 0,
        });
      });

      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      this.observers.set('lcp', lcpObserver);
    } catch (e) {
      console.warn('LCP tracking not supported');
    }
  }

  trackFCP() {
    if (!('PerformanceObserver' in window)) return;

    try {
      const fcpObserver = new PerformanceObserver(list => {
        for (const entry of list.getEntries()) {
          if (entry.name === 'first-contentful-paint') {
            this.recordMetric('FCP', {
              value: entry.startTime,
            });
          }
        }
      });

      fcpObserver.observe({ entryTypes: ['paint'] });
      this.observers.set('fcp', fcpObserver);
    } catch (e) {
      console.warn('FCP tracking not supported');
    }
  }

  trackTTFB() {
    if (!('PerformanceObserver' in window)) return;

    try {
      const navigationObserver = new PerformanceObserver(list => {
        for (const entry of list.getEntries()) {
          this.recordMetric('TTFB', {
            value: entry.responseStart - entry.requestStart,
            dns: entry.domainLookupEnd - entry.domainLookupStart,
            tcp: entry.connectEnd - entry.connectStart,
            request: entry.responseStart - entry.requestStart,
            response: entry.responseEnd - entry.responseStart,
          });
        }
      });

      navigationObserver.observe({ entryTypes: ['navigation'] });
      this.observers.set('navigation', navigationObserver);
    } catch (e) {
      console.warn('Navigation timing not supported');
    }
  }

  setupCustomMetrics() {
    if (!this.options.enableCustomMetrics) return;

    // Track JavaScript bundle load times
    this.trackBundleLoadTimes();

    // Track critical resource loading
    this.trackCriticalResources();

    // Track user interactions
    this.trackUserInteractions();

    // Track memory usage
    this.trackMemoryUsage();
  }

  trackBundleLoadTimes() {
    // Track when main bundle loads
    const _bundleStart = performance.mark('bundle-start');

    window.addEventListener('load', () => {
      performance.mark('bundle-end');
      const bundleTime = performance.measure('bundle-load', 'bundle-start', 'bundle-end');

      this.recordMetric('Bundle Load Time', {
        value: bundleTime.duration,
        bundles: this.getLoadedBundles(),
      });
    });
  }

  getLoadedBundles() {
    const scripts = Array.from(document.querySelectorAll('script[src]'));
    return scripts.map(script => ({
      src: script.src,
      async: script.async,
      defer: script.defer,
    }));
  }

  trackCriticalResources() {
    // Track hero image/video loading
    const heroMedia = document.querySelector('.hero img, .hero video');
    if (heroMedia) {
      const startTime = performance.now();

      const trackLoad = () => {
        const loadTime = performance.now() - startTime;
        this.recordMetric('Hero Media Load', {
          value: loadTime,
          type: heroMedia.tagName.toLowerCase(),
          src: heroMedia.src || heroMedia.currentSrc,
        });
      };

      if (heroMedia.complete || heroMedia.readyState >= 2) {
        trackLoad();
      } else {
        heroMedia.addEventListener('load', trackLoad);
        heroMedia.addEventListener('loadeddata', trackLoad);
      }
    }

    // Track font loading
    if ('fonts' in document) {
      document.fonts.ready.then(() => {
        this.recordMetric('Fonts Loaded', {
          value: performance.now() - this.startTime,
          count: document.fonts.size,
        });
      });
    }
  }

  trackUserInteractions() {
    // Track time to first interaction
    let firstInteraction = null;

    const interactions = ['click', 'touchstart', 'keydown', 'scroll'];

    const trackFirstInteraction = event => {
      if (!firstInteraction) {
        firstInteraction = performance.now();
        this.recordMetric('Time to First Interaction', {
          value: firstInteraction - this.startTime,
          type: event.type,
        });

        // Remove listeners after first interaction
        interactions.forEach(type => {
          document.removeEventListener(type, trackFirstInteraction);
        });
      }
    };

    interactions.forEach(type => {
      document.addEventListener(type, trackFirstInteraction, {
        passive: true,
        once: true,
      });
    });

    // Track scroll depth
    this.trackScrollDepth();
  }

  trackScrollDepth() {
    let maxScrollDepth = 0;
    let scrollTimer = null;

    const trackScroll = () => {
      const scrollTop = window.pageYOffset;
      const documentHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrollPercent = Math.round((scrollTop / documentHeight) * 100);

      if (scrollPercent > maxScrollDepth) {
        maxScrollDepth = scrollPercent;
      }

      // Debounce scroll tracking
      clearTimeout(scrollTimer);
      scrollTimer = setTimeout(() => {
        this.recordMetric('Scroll Depth', {
          value: maxScrollDepth,
          timestamp: performance.now(),
        });
      }, 500);
    };

    window.addEventListener('scroll', trackScroll, { passive: true });

    // Track final scroll depth on page unload
    window.addEventListener('beforeunload', () => {
      this.recordMetric('Final Scroll Depth', {
        value: maxScrollDepth,
      });
    });
  }

  trackMemoryUsage() {
    if ('memory' in performance) {
      const trackMemory = () => {
        this.recordMetric('Memory Usage', {
          used: performance.memory.usedJSHeapSize,
          total: performance.memory.totalJSHeapSize,
          limit: performance.memory.jsHeapSizeLimit,
        });
      };

      // Track initial memory
      trackMemory();

      // Track memory periodically
      setInterval(trackMemory, 60000); // Every minute
    }
  }

  setupNavigationTiming() {
    if (!this.options.enableNavigationTiming) return;

    window.addEventListener('load', () => {
      const navigation = performance.getEntriesByType('navigation')[0];
      if (navigation) {
        this.recordMetric('Navigation Timing', {
          dns: navigation.domainLookupEnd - navigation.domainLookupStart,
          tcp: navigation.connectEnd - navigation.connectStart,
          ttfb: navigation.responseStart - navigation.requestStart,
          download: navigation.responseEnd - navigation.responseStart,
          domParsing: navigation.domContentLoadedEventStart - navigation.responseEnd,
          resourceLoading: navigation.loadEventStart - navigation.domContentLoadedEventStart,
        });
      }
    });
  }

  setupResourceTiming() {
    if (!this.options.enableResourceTiming) return;

    // Track slow resources
    const slowResourceThreshold = 1000; // 1 second

    const checkResources = () => {
      const resources = performance.getEntriesByType('resource');
      const slowResources = resources.filter(resource => resource.duration > slowResourceThreshold);

      if (slowResources.length > 0) {
        this.recordMetric('Slow Resources', {
          count: slowResources.length,
          resources: slowResources.map(resource => ({
            name: resource.name,
            duration: resource.duration,
            size: resource.transferSize,
            type: resource.initiatorType,
          })),
        });
      }
    };

    window.addEventListener('load', () => {
      setTimeout(checkResources, 1000);
    });
  }

  setupUserTiming() {
    if (!this.options.enableUserTiming) return;

    // Track custom performance marks and measures
    const checkUserTiming = () => {
      const marks = performance.getEntriesByType('mark');
      const measures = performance.getEntriesByType('measure');

      if (marks.length > 0 || measures.length > 0) {
        this.recordMetric('User Timing', {
          marks: marks.map(mark => ({
            name: mark.name,
            startTime: mark.startTime,
          })),
          measures: measures.map(measure => ({
            name: measure.name,
            duration: measure.duration,
            startTime: measure.startTime,
          })),
        });
      }
    };

    window.addEventListener('load', () => {
      setTimeout(checkUserTiming, 2000);
    });
  }

  recordMetric(name, data) {
    const metric = {
      name,
      data,
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      connection: this.getConnectionInfo(),
    };

    this.metrics.set(name, metric);
    this.buffer.push(metric);

    // Log in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`📊 ${name}:`, data);
    }

    // Send immediately for critical metrics
    if (this.isCriticalMetric(name)) {
      this.sendMetrics([metric]);
    }
  }

  getConnectionInfo() {
    if ('connection' in navigator) {
      const conn = navigator.connection;
      return {
        effectiveType: conn.effectiveType,
        downlink: conn.downlink,
        rtt: conn.rtt,
        saveData: conn.saveData,
      };
    }
    return null;
  }

  isCriticalMetric(name) {
    const criticalMetrics = ['CLS', 'FID', 'LCP'];
    return criticalMetrics.includes(name);
  }

  setupSendInterval() {
    // Send metrics periodically
    setInterval(() => {
      if (this.buffer.length > 0) {
        this.sendBufferedMetrics();
      }
    }, this.options.sendInterval);

    // Send metrics on page unload
    window.addEventListener('beforeunload', () => {
      this.sendBufferedMetrics(true);
    });

    // Send metrics when buffer is full
    this.checkBufferSize();
  }

  checkBufferSize() {
    if (this.buffer.length >= this.options.bufferSize) {
      this.sendBufferedMetrics();
    }
  }

  sendBufferedMetrics(useBeacon = false) {
    if (this.buffer.length === 0) return;

    const metrics = [...this.buffer];
    this.buffer = [];

    this.sendMetrics(metrics, useBeacon);
  }

  async sendMetrics(metrics, useBeacon = false) {
    const payload = {
      metrics,
      session: this.getSessionId(),
      page: {
        url: window.location.href,
        title: document.title,
        referrer: document.referrer,
      },
      timestamp: Date.now(),
    };

    try {
      if (useBeacon && 'sendBeacon' in navigator) {
        // Use sendBeacon for reliable delivery on page unload
        navigator.sendBeacon(this.options.endpoint, JSON.stringify(payload));
      } else {
        // Send to analytics
        this.sendToAnalytics(metrics);

        // Send to custom endpoint if configured
        if (this.options.endpoint) {
          await fetch(this.options.endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
            keepalive: true,
          });
        }
      }
    } catch (error) {
      console.warn('Failed to send performance metrics:', error);
    }
  }

  sendToAnalytics(metrics) {
    if (!window.gtag) return;

    metrics.forEach(metric => {
      if (metric.data.value !== undefined) {
        window.gtag('event', 'web_vitals', {
          name: metric.name,
          value: Math.round(metric.data.value),
          metric_id: this.generateMetricId(metric),
          custom_parameters: metric.data,
        });
      }
    });
  }

  generateMetricId(metric) {
    return `${metric.name}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  getSessionId() {
    if (!this.sessionId) {
      this.sessionId = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    return this.sessionId;
  }

  // Public API methods
  trackCustomEvent(name, data = {}) {
    this.recordMetric(`Custom: ${name}`, data);
  }

  mark(name) {
    performance.mark(name);
  }

  measure(name, startMark, endMark) {
    const measure = performance.measure(name, startMark, endMark);
    this.recordMetric(`Measure: ${name}`, {
      value: measure.duration,
      startTime: measure.startTime,
    });
    return measure;
  }

  getMetrics() {
    return Object.fromEntries(this.metrics);
  }

  start() {
    this.init();
  }

  stop() {
    // Disconnect all observers
    this.observers.forEach(observer => observer.disconnect());
    this.observers.clear();

    // Send remaining buffered metrics
    this.sendBufferedMetrics();
  }

  // Static factory method
  static init(options = {}) {
    return new PerformanceMonitor(options);
  }
}

// Auto-initialize if not using module system
if (typeof window !== 'undefined' && !window.moduleSystem) {
  document.addEventListener('DOMContentLoaded', () => {
    PerformanceMonitor.init();
  });
}
