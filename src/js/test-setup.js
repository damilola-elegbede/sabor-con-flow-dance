/**
 * Vitest Test Setup for Sabor Con Flow Dance
 * Configures testing environment for bundled JavaScript
 */

import { vi } from 'vitest';

// Mock DOM APIs not available in Node
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
  log: vi.fn(),
  warn: vi.fn(),
  error: vi.fn(),
  info: vi.fn()
};

// Mock window.matchMedia (for Node environment)
if (typeof window !== 'undefined') {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
}

// Mock localStorage for Node environment
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage
global.sessionStorage = localStorageMock;

// Mock fetch
global.fetch = vi.fn(() =>
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

// Mock navigator for Node environment
if (typeof navigator === 'undefined') {
  global.navigator = {};
}

Object.defineProperty(navigator, 'connection', {
  writable: true,
  value: {
    effectiveType: '4g',
    saveData: false,
    downlink: 10,
    rtt: 100
  }
});

// Add custom matchers for Vitest
if (typeof expect !== 'undefined') {
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
      // Only test if we have DOM environment
      if (typeof document === 'undefined') {
        return {
          message: () => `DOM not available for progressive enhancement test`,
          pass: true,
        };
      }
      
      const hasNoJSFallback = received.classList?.contains('no-js-fallback') ||
                             received.querySelector?.('.no-js-fallback');
      const hasJSEnhancement = received.classList?.contains('js-enhanced') ||
                              received.querySelector?.('.js-enhanced');
      
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
}

// Helper functions for tests (only in DOM environments)
if (typeof document !== 'undefined') {
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
      canvas.toDataURL = vi.fn(() => 
        supported ? 'data:image/webp' : 'data:image/png'
      );
      document.createElement = vi.fn((tag) => {
        if (tag === 'canvas') return canvas;
        return document.createElement.bind(document)(tag);
      });
    }
  };
}

console.log('🧪 Vitest test environment setup complete');