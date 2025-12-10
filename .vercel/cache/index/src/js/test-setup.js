/**
 * Jest Test Setup for Sabor Con Flow Dance
 * Configures testing environment for bundled JavaScript
 */

// Mock DOM APIs not available in Jest
global.IntersectionObserver = class {
  constructor(callback, options) {
    this.callback = callback;
    this.options = options;
  }
  
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock Performance API
global.performance = global.performance || {
  now: () => Date.now(),
  mark: () => {},
  measure: () => ({ duration: 100 }),
  getEntriesByType: () => [],
  getEntriesByName: () => [],
  clearMarks: () => {},
  clearMeasures: () => {}
};

// Mock console methods for tests
global.console = {
  ...console,
  log: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
  info: jest.fn()
};

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage
global.sessionStorage = localStorageMock;

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(''),
  })
);

// Mock Image constructor
global.Image = class {
  constructor() {
    setTimeout(() => {
      if (this.onload) this.onload();
    }, 100);
  }
};

// Mock navigator
Object.defineProperty(navigator, 'connection', {
  writable: true,
  value: {
    effectiveType: '4g',
    saveData: false,
    downlink: 10,
    rtt: 100
  }
});

// Setup DOM testing utilities
import 'jest-dom/extend-expect';

// Add custom matchers
expect.extend({
  toBeWithinBudget(received, budget) {
    const pass = received <= budget;
    if (pass) {
      return {
        message: () => `expected ${received} not to be within budget ${budget}`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected ${received} to be within budget ${budget}`,
        pass: false,
      };
    }
  },
  
  toBeProgressivelyEnhanced(received) {
    const hasNoJSFallback = received.classList.contains('no-js-fallback') ||
                           received.querySelector('.no-js-fallback');
    const hasJSEnhancement = received.classList.contains('js-enhanced') ||
                            received.querySelector('.js-enhanced');
    
    const pass = hasNoJSFallback || hasJSEnhancement;
    if (pass) {
      return {
        message: () => `expected element not to be progressively enhanced`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected element to be progressively enhanced`,
        pass: false,
      };
    }
  }
});

// Helper functions for tests
global.testHelpers = {
  createMockElement: (tag = 'div', attributes = {}) => {
    const element = document.createElement(tag);
    Object.keys(attributes).forEach(key => {
      element.setAttribute(key, attributes[key]);
    });
    return element;
  },
  
  simulateIntersection: (element, isIntersecting = true) => {
    const observer = element._intersectionObserver;
    if (observer && observer.callback) {
      observer.callback([{
        target: element,
        isIntersecting,
        intersectionRatio: isIntersecting ? 1 : 0
      }]);
    }
  },
  
  waitForAsync: () => new Promise(resolve => setTimeout(resolve, 0)),
  
  mockWebPSupport: (supported = true) => {
    const canvas = document.createElement('canvas');
    canvas.toDataURL = jest.fn(() => 
      supported ? 'data:image/webp' : 'data:image/png'
    );
    document.createElement = jest.fn((tag) => {
      if (tag === 'canvas') return canvas;
      return document.createElement.bind(document)(tag);
    });
  }
};

// Global test configuration
beforeEach(() => {
  // Clear all mocks before each test
  jest.clearAllMocks();
  
  // Reset DOM
  document.body.innerHTML = '';
  document.head.innerHTML = '';
  
  // Reset classes
  document.documentElement.className = '';
  
  // Reset window properties
  delete window.saborConFlowApp;
  delete window.bundleManifest;
  delete window.performanceAnalytics;
});

afterEach(() => {
  // Clean up any timers
  jest.runOnlyPendingTimers();
  jest.useRealTimers();
});

console.log('🧪 Test environment setup complete');