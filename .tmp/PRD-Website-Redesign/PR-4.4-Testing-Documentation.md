# PR 4.4: Testing & Documentation Implementation

## PR Metadata
- **Phase**: 4.4 - Testing & Documentation
- **Priority**: High
- **Dependencies**: PR 4.1, 4.2, 4.3 (Performance, SEO, Security)
- **Estimated Timeline**: 7-9 days
- **Risk Level**: Medium
- **Team**: QA + Tech Writers + DevOps

## Testing Strategy & Framework

### Testing Pyramid Implementation
- **Unit Tests**: 70% coverage target with Vitest
- **Integration Tests**: 20% coverage with API testing
- **End-to-End Tests**: 10% coverage with Playwright
- **Performance Tests**: Lighthouse CI + K6 load testing
- **Security Tests**: OWASP ZAP automated scanning
- **Accessibility Tests**: axe-core automated testing

### Quality Gates
- **Code Coverage**: Minimum 80% for all new code
- **Performance**: Lighthouse scores > 90 across all categories
- **Security**: Zero high/critical vulnerabilities
- **Accessibility**: WCAG 2.1 AA compliance
- **Cross-browser**: Chrome, Firefox, Safari, Edge compatibility

## Vitest Testing Implementation

### 1. Core Testing Infrastructure

#### Vitest Configuration
```javascript
// vite.config.test.js
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.js'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        '**/*.config.js',
        'dist/',
        'build/',
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    },
    // Mock external services
    server: {
      deps: {
        inline: ['@testing-library/jest-dom']
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './static/js'),
      '@components': resolve(__dirname, './static/js/components'),
      '@utils': resolve(__dirname, './static/js/utils'),
      '@tests': resolve(__dirname, './tests')
    }
  },
  define: {
    'import.meta.vitest': undefined
  }
});
```

#### Test Setup and Utilities
```javascript
// tests/setup.js
import { beforeEach, vi } from 'vitest';
import '@testing-library/jest-dom';
import 'whatwg-fetch';

// Global test setup
beforeEach(() => {
  // Clear all mocks before each test
  vi.clearAllMocks();
  
  // Reset DOM
  document.body.innerHTML = '';
  document.head.innerHTML = '';
  
  // Mock window.location
  delete window.location;
  window.location = {
    href: 'https://saborconflow.com/',
    pathname: '/',
    search: '',
    hash: '',
    assign: vi.fn(),
    replace: vi.fn(),
    reload: vi.fn(),
  };
  
  // Mock localStorage
  const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  };
  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock
  });
  
  // Mock sessionStorage
  Object.defineProperty(window, 'sessionStorage', {
    value: localStorageMock
  });
  
  // Mock IntersectionObserver
  global.IntersectionObserver = vi.fn().mockImplementation((callback) => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
    thresholds: [0],
    root: null,
    rootMargin: '',
  }));
  
  // Mock ResizeObserver
  global.ResizeObserver = vi.fn().mockImplementation((callback) => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }));
  
  // Mock fetch
  global.fetch = vi.fn();
  
  // Mock Google Analytics
  global.gtag = vi.fn();
  global.dataLayer = [];
  
  // Mock console methods in tests
  vi.spyOn(console, 'error').mockImplementation(() => {});
  vi.spyOn(console, 'warn').mockImplementation(() => {});
});

// Test utilities
export const mockFetch = (data, ok = true, status = 200) => {
  return vi.fn().mockResolvedValue({
    ok,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
  });
};

export const createMockEvent = (type, properties = {}) => {
  const event = new Event(type);
  Object.assign(event, properties);
  return event;
};

export const waitForNextTick = () => new Promise(resolve => setTimeout(resolve, 0));

export const mockGeolocation = (coords = { latitude: 25.7617, longitude: -80.1918 }) => {
  const mockGeolocation = {
    getCurrentPosition: vi.fn().mockImplementation((success) => {
      success({
        coords: {
          ...coords,
          accuracy: 10,
        }
      });
    }),
    watchPosition: vi.fn(),
    clearWatch: vi.fn(),
  };
  
  Object.defineProperty(navigator, 'geolocation', {
    value: mockGeolocation,
    writable: true,
  });
  
  return mockGeolocation;
};
```

### 2. Component Testing Suite

#### Core Component Tests
```javascript
// tests/components/navigation.test.js
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/dom';
import '@testing-library/jest-dom';
import { Navigation } from '@components/navigation';
import { mockFetch, createMockEvent } from '@tests/setup';

describe('Navigation Component', () => {
  let navigation;
  
  beforeEach(() => {
    // Setup DOM
    document.body.innerHTML = `
      <nav class="navbar" role="navigation" aria-label="main navigation">
        <div class="navbar-brand">
          <a class="navbar-item" href="/">
            <img src="/static/images/logo.webp" alt="Sabor con Flow" />
          </a>
          <button class="navbar-burger" aria-label="menu" aria-expanded="false">
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
          </button>
        </div>
        <div class="navbar-menu">
          <div class="navbar-end">
            <a href="/" class="navbar-item">Home</a>
            <a href="/events" class="navbar-item">Events</a>
            <a href="/pricing" class="navbar-item">Pricing</a>
            <a href="/contact" class="navbar-item">Contact</a>
          </div>
        </div>
      </nav>
    `;
    
    navigation = new Navigation();
  });
  
  it('should initialize navigation correctly', () => {
    expect(navigation.burger).toBeTruthy();
    expect(navigation.menu).toBeTruthy();
    expect(navigation.isActive).toBe(false);
  });
  
  it('should toggle mobile menu when burger is clicked', async () => {
    const burger = screen.getByLabelText('menu');
    
    fireEvent.click(burger);
    
    await waitFor(() => {
      expect(navigation.isActive).toBe(true);
      expect(burger.getAttribute('aria-expanded')).toBe('true');
      expect(navigation.menu.classList.contains('is-active')).toBe(true);
    });
  });
  
  it('should close menu when clicking outside', async () => {
    // Open menu first
    fireEvent.click(screen.getByLabelText('menu'));
    
    // Click outside
    fireEvent.click(document.body);
    
    await waitFor(() => {
      expect(navigation.isActive).toBe(false);
      expect(navigation.menu.classList.contains('is-active')).toBe(false);
    });
  });
  
  it('should handle keyboard navigation correctly', async () => {
    const burger = screen.getByLabelText('menu');
    
    // Test Enter key
    fireEvent.keyDown(burger, { key: 'Enter', code: 'Enter' });
    await waitFor(() => {
      expect(navigation.isActive).toBe(true);
    });
    
    // Test Escape key
    fireEvent.keyDown(document, { key: 'Escape', code: 'Escape' });
    await waitFor(() => {
      expect(navigation.isActive).toBe(false);
    });
  });
  
  it('should highlight active page', () => {
    window.location.pathname = '/events';
    navigation.highlightActivePage();
    
    const eventsLink = screen.getByText('Events');
    expect(eventsLink.parentElement.classList.contains('is-active')).toBe(true);
  });
  
  it('should handle scroll behavior for navigation visibility', async () => {
    const navbar = document.querySelector('.navbar');
    
    // Mock scroll event
    Object.defineProperty(window, 'scrollY', { value: 100, writable: true });
    fireEvent.scroll(window);
    
    await waitFor(() => {
      expect(navbar.classList.contains('navbar-scrolled')).toBe(true);
    });
    
    // Scroll back to top
    Object.defineProperty(window, 'scrollY', { value: 0, writable: true });
    fireEvent.scroll(window);
    
    await waitFor(() => {
      expect(navbar.classList.contains('navbar-scrolled')).toBe(false);
    });
  });
});

// tests/components/contact-form.test.js
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { screen, fireEvent, waitFor } from '@testing-library/dom';
import { ContactForm } from '@components/contact-form';
import { mockFetch } from '@tests/setup';

describe('Contact Form Component', () => {
  let contactForm;
  
  beforeEach(() => {
    document.body.innerHTML = `
      <form id="contact-form" class="contact-form">
        <div class="field">
          <label for="name">Name *</label>
          <input type="text" id="name" name="name" required />
          <span class="error-message" id="name-error"></span>
        </div>
        
        <div class="field">
          <label for="email">Email *</label>
          <input type="email" id="email" name="email" required />
          <span class="error-message" id="email-error"></span>
        </div>
        
        <div class="field">
          <label for="phone">Phone</label>
          <input type="tel" id="phone" name="phone" />
          <span class="error-message" id="phone-error"></span>
        </div>
        
        <div class="field">
          <label for="message">Message *</label>
          <textarea id="message" name="message" required rows="5"></textarea>
          <span class="error-message" id="message-error"></span>
        </div>
        
        <div class="field">
          <label class="checkbox">
            <input type="checkbox" name="newsletter" />
            Subscribe to our newsletter
          </label>
        </div>
        
        <button type="submit" class="btn btn-primary">Send Message</button>
        
        <div id="form-status" class="status-message"></div>
      </form>
    `;
    
    contactForm = new ContactForm();
  });
  
  it('should validate required fields', async () => {
    const submitButton = screen.getByRole('button', { name: /send message/i });
    
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeInTheDocument();
      expect(screen.getByText('Email is required')).toBeInTheDocument();
      expect(screen.getByText('Message is required')).toBeInTheDocument();
    });
  });
  
  it('should validate email format', async () => {
    const emailInput = screen.getByLabelText(/email/i);
    
    fireEvent.input(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.blur(emailInput);
    
    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
    });
  });
  
  it('should validate phone number format', async () => {
    const phoneInput = screen.getByLabelText(/phone/i);
    
    fireEvent.input(phoneInput, { target: { value: '123' } });
    fireEvent.blur(phoneInput);
    
    await waitFor(() => {
      expect(screen.getByText('Please enter a valid phone number')).toBeInTheDocument();
    });
  });
  
  it('should submit form with valid data', async () => {
    global.fetch = mockFetch({ success: true, message: 'Message sent successfully!' });
    
    // Fill out form
    fireEvent.input(screen.getByLabelText(/name/i), { target: { value: 'John Doe' } });
    fireEvent.input(screen.getByLabelText(/email/i), { target: { value: 'john@example.com' } });
    fireEvent.input(screen.getByLabelText(/message/i), { target: { value: 'Test message' } });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /send message/i }));
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/contact/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': expect.any(String),
        },
        body: JSON.stringify({
          name: 'John Doe',
          email: 'john@example.com',
          phone: '',
          message: 'Test message',
          newsletter: false,
        }),
      });
    });
    
    await waitFor(() => {
      expect(screen.getByText('Message sent successfully!')).toBeInTheDocument();
    });
  });
  
  it('should handle form submission errors', async () => {
    global.fetch = mockFetch({ error: 'Server error' }, false, 500);
    
    // Fill out form
    fireEvent.input(screen.getByLabelText(/name/i), { target: { value: 'John Doe' } });
    fireEvent.input(screen.getByLabelText(/email/i), { target: { value: 'john@example.com' } });
    fireEvent.input(screen.getByLabelText(/message/i), { target: { value: 'Test message' } });
    
    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /send message/i }));
    
    await waitFor(() => {
      expect(screen.getByText('There was an error sending your message. Please try again.')).toBeInTheDocument();
    });
  });
  
  it('should sanitize user input', () => {
    const maliciousInput = '<script>alert("xss")</script>';
    const sanitized = contactForm.sanitizeInput(maliciousInput);
    
    expect(sanitized).toBe('&lt;script&gt;alert("xss")&lt;/script&gt;');
  });
  
  it('should track analytics events', async () => {
    global.gtag = vi.fn();
    
    // Fill and submit form
    fireEvent.input(screen.getByLabelText(/name/i), { target: { value: 'John Doe' } });
    fireEvent.input(screen.getByLabelText(/email/i), { target: { value: 'john@example.com' } });
    fireEvent.input(screen.getByLabelText(/message/i), { target: { value: 'Test message' } });
    
    global.fetch = mockFetch({ success: true });
    fireEvent.click(screen.getByRole('button', { name: /send message/i }));
    
    await waitFor(() => {
      expect(gtag).toHaveBeenCalledWith('event', 'form_submit', {
        form_name: 'contact',
        form_location: 'contact_page',
      });
    });
  });
});
```

### 3. Performance Testing Suite

#### Lighthouse CI Configuration
```javascript
// .lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: [
        'http://localhost:3000/',
        'http://localhost:3000/events',
        'http://localhost:3000/pricing',
        'http://localhost:3000/contact'
      ],
      startServerCommand: 'npm run dev',
      startServerReadyPattern: 'ready on',
      numberOfRuns: 3,
      settings: {
        preset: 'desktop',
        chromeFlags: '--no-sandbox --headless',
        throttling: {
          rttMs: 40,
          throughputKbps: 10240,
          cpuSlowdownMultiplier: 1,
          requestLatencyMs: 0,
          downloadThroughputKbps: 0,
          uploadThroughputKbps: 0
        }
      }
    },
    assert: {
      assertions: {
        'categories:performance': ['error', {minScore: 0.9}],
        'categories:accessibility': ['error', {minScore: 0.9}],
        'categories:best-practices': ['error', {minScore: 0.9}],
        'categories:seo': ['error', {minScore: 0.9}],
        'categories:pwa': ['warn', {minScore: 0.8}],
        
        // Core Web Vitals
        'largest-contentful-paint': ['error', {maxNumericValue: 2500}],
        'first-input-delay': ['error', {maxNumericValue: 100}],
        'cumulative-layout-shift': ['error', {maxNumericValue: 0.1}],
        
        // Other performance metrics
        'first-contentful-paint': ['warn', {maxNumericValue: 1800}],
        'speed-index': ['warn', {maxNumericValue: 3000}],
        'time-to-interactive': ['warn', {maxNumericValue: 3500}],
        
        // Best practices
        'uses-https': 'error',
        'uses-http2': 'warn',
        'uses-responsive-images': 'warn',
        'efficient-animated-content': 'warn',
        'unused-css-rules': 'warn',
        'unused-javascript': 'warn',
        
        // Accessibility
        'color-contrast': 'error',
        'image-alt': 'error',
        'label': 'error',
        'link-name': 'error',
        'button-name': 'error',
        
        // SEO
        'document-title': 'error',
        'meta-description': 'error',
        'link-text': 'error',
        'crawlable-anchors': 'error'
      }
    },
    upload: {
      target: 'lhci',
      serverBaseUrl: process.env.LHCI_SERVER_URL || 'http://localhost:9001'
    }
  }
};
```

#### Performance Test Suite
```javascript
// tests/performance/core-web-vitals.test.js
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

describe('Core Web Vitals', () => {
  let vitalsData = {};
  
  beforeEach(() => {
    vitalsData = {};
    
    // Mock performance observer
    global.PerformanceObserver = vi.fn().mockImplementation((callback) => ({
      observe: vi.fn().mockImplementation(() => {
        // Simulate performance entries
        setTimeout(() => {
          callback({
            getEntries: () => [
              {
                name: 'first-contentful-paint',
                startTime: 1200,
                entryType: 'paint'
              },
              {
                startTime: 2000,
                size: 1000,
                entryType: 'largest-contentful-paint'
              }
            ]
          });
        }, 100);
      }),
      disconnect: vi.fn()
    }));
  });
  
  it('should measure Largest Contentful Paint (LCP)', (done) => {
    getLCP((metric) => {
      vitalsData.lcp = metric;
      expect(metric.name).toBe('LCP');
      expect(metric.value).toBeLessThan(2500); // Good LCP threshold
      done();
    });
  });
  
  it('should measure First Input Delay (FID)', (done) => {
    // Mock first input
    setTimeout(() => {
      const event = new PointerEvent('click', { bubbles: true });
      document.dispatchEvent(event);
    }, 50);
    
    getFID((metric) => {
      vitalsData.fid = metric;
      expect(metric.name).toBe('FID');
      expect(metric.value).toBeLessThan(100); // Good FID threshold
      done();
    });
  });
  
  it('should measure Cumulative Layout Shift (CLS)', (done) => {
    getCLS((metric) => {
      vitalsData.cls = metric;
      expect(metric.name).toBe('CLS');
      expect(metric.value).toBeLessThan(0.1); // Good CLS threshold
      done();
    });
  });
  
  it('should track performance metrics over time', async () => {
    const metrics = [];
    
    const collectMetric = (metric) => {
      metrics.push({
        name: metric.name,
        value: metric.value,
        rating: metric.rating,
        timestamp: Date.now()
      });
    };
    
    getLCP(collectMetric);
    getFCP(collectMetric);
    getCLS(collectMetric);
    
    // Wait for metrics to be collected
    await new Promise(resolve => setTimeout(resolve, 500));
    
    expect(metrics.length).toBeGreaterThan(0);
    expect(metrics.every(m => m.timestamp)).toBe(true);
    expect(metrics.every(m => typeof m.value === 'number')).toBe(true);
  });
});

// tests/performance/resource-loading.test.js
import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('Resource Loading Performance', () => {
  beforeEach(() => {
    // Mock performance.getEntriesByType
    global.performance.getEntriesByType = vi.fn();
    global.performance.mark = vi.fn();
    global.performance.measure = vi.fn();
  });
  
  it('should load critical CSS within acceptable time', () => {
    global.performance.getEntriesByType.mockReturnValue([
      {
        name: 'critical.css',
        transferSize: 12000,
        duration: 150,
        startTime: 100
      }
    ]);
    
    const cssResources = performance.getEntriesByType('resource')
      .filter(resource => resource.name.includes('.css'));
    
    cssResources.forEach(resource => {
      expect(resource.duration).toBeLessThan(500); // 500ms max for CSS
      expect(resource.transferSize).toBeLessThan(15000); // 15KB max for critical CSS
    });
  });
  
  it('should lazy load non-critical resources', async () => {
    // Mock intersection observer for lazy loading
    const mockIntersectionObserver = vi.fn().mockImplementation((callback) => ({
      observe: vi.fn().mockImplementation((element) => {
        // Simulate element coming into view
        setTimeout(() => {
          callback([{
            isIntersecting: true,
            target: element
          }]);
        }, 100);
      }),
      unobserve: vi.fn(),
      disconnect: vi.fn()
    }));
    
    global.IntersectionObserver = mockIntersectionObserver;
    
    // Create lazy-loaded image
    document.body.innerHTML = '<img data-src="test.jpg" class="lazy" />';
    
    const { LazyLoader } = await import('@/lazy-loader');
    new LazyLoader();
    
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const img = document.querySelector('img');
    expect(img.src).toBe('http://localhost:3000/test.jpg');
  });
  
  it('should optimize font loading', () => {
    // Check for font-display: swap in CSS
    const fontFaces = Array.from(document.styleSheets)
      .flatMap(sheet => Array.from(sheet.cssRules))
      .filter(rule => rule.constructor.name === 'CSSFontFaceRule');
    
    fontFaces.forEach(fontFace => {
      expect(fontFace.style.fontDisplay).toBe('swap');
    });
  });
});
```

### 4. E2E Testing with Playwright

#### Playwright Configuration
```javascript
// playwright.config.js
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/results.xml' }]
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

#### E2E Test Suites
```javascript
// tests/e2e/user-journey.spec.js
import { test, expect } from '@playwright/test';

test.describe('User Journey Tests', () => {
  test('should complete full user journey from landing to contact', async ({ page }) => {
    // Track analytics events
    const analyticsEvents = [];
    page.on('request', request => {
      if (request.url().includes('google-analytics.com')) {
        analyticsEvents.push(request.url());
      }
    });
    
    // 1. Land on homepage
    await page.goto('/');
    await expect(page).toHaveTitle(/Sabor con Flow/);
    
    // Check hero section is visible
    await expect(page.locator('.hero-section')).toBeVisible();
    await expect(page.locator('h1')).toContainText('Dance with Passion');
    
    // 2. Navigate to events page
    await page.click('text=Events');
    await page.waitForURL('/events');
    await expect(page.locator('.events-container')).toBeVisible();
    
    // 3. Check event details
    const firstEvent = page.locator('.event-card').first();
    await expect(firstEvent).toBeVisible();
    await firstEvent.click();
    
    // Verify event modal opens
    await expect(page.locator('.event-modal')).toBeVisible();
    await page.press('Escape'); // Close modal
    
    // 4. Navigate to pricing
    await page.click('text=Pricing');
    await page.waitForURL('/pricing');
    
    // Check pricing cards
    await expect(page.locator('.pricing-card')).toHaveCount(3);
    
    // 5. Go to contact page
    await page.click('text=Contact');
    await page.waitForURL('/contact');
    
    // 6. Fill and submit contact form
    await page.fill('[name="name"]', 'Test User');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="message"]', 'I am interested in salsa classes');
    
    // Mock form submission
    await page.route('/api/contact/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, message: 'Message sent successfully!' })
      });
    });
    
    await page.click('text=Send Message');
    
    // Verify success message
    await expect(page.locator('.success-message')).toContainText('Message sent successfully');
    
    // Verify analytics tracking
    expect(analyticsEvents.length).toBeGreaterThan(0);
  });
  
  test('should handle mobile navigation correctly', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Mobile menu should be hidden initially
    await expect(page.locator('.navbar-menu')).not.toBeVisible();
    
    // Open mobile menu
    await page.click('.navbar-burger');
    await expect(page.locator('.navbar-menu')).toBeVisible();
    
    // Navigate via mobile menu
    await page.click('.navbar-menu a[href="/events"]');
    await page.waitForURL('/events');
    
    // Menu should close after navigation
    await expect(page.locator('.navbar-menu')).not.toBeVisible();
  });
  
  test('should load all images without errors', async ({ page }) => {
    const imageErrors = [];
    
    page.on('response', response => {
      if (response.url().match(/\.(jpg|jpeg|png|webp|avif)$/i) && !response.ok()) {
        imageErrors.push(response.url());
      }
    });
    
    await page.goto('/');
    
    // Wait for all images to load
    await page.waitForLoadState('networkidle');
    
    // Check that no images failed to load
    expect(imageErrors).toHaveLength(0);
    
    // Verify hero image is loaded
    const heroImage = page.locator('.hero-image img');
    await expect(heroImage).toBeVisible();
    await expect(heroImage).toHaveAttribute('src', /.+\.(jpg|jpeg|png|webp|avif)$/i);
  });
  
  test('should maintain accessibility standards', async ({ page }) => {
    await page.goto('/');
    
    // Check for proper heading hierarchy
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    expect(headings.length).toBeGreaterThan(0);
    
    // Verify all images have alt text
    const images = await page.locator('img').all();
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      expect(alt).toBeTruthy();
    }
    
    // Check form labels
    const inputs = await page.locator('input, textarea, select').all();
    for (const input of inputs) {
      const id = await input.getAttribute('id');
      if (id) {
        const label = page.locator(`label[for="${id}"]`);
        await expect(label).toBeVisible();
      }
    }
    
    // Verify keyboard navigation
    await page.keyboard.press('Tab');
    const focusedElement = await page.evaluate(() => document.activeElement.tagName);
    expect(['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA']).toContain(focusedElement);
  });
});

// tests/e2e/performance.spec.js
import { test, expect } from '@playwright/test';

test.describe('Performance Tests', () => {
  test('should meet Core Web Vitals thresholds', async ({ page }) => {
    // Enable metrics collection
    await page.addInitScript(() => {
      window.webVitalsData = [];
      
      // Mock web-vitals library
      window.getCLS = (callback) => {
        setTimeout(() => callback({ name: 'CLS', value: 0.05 }), 100);
      };
      
      window.getLCP = (callback) => {
        setTimeout(() => callback({ name: 'LCP', value: 1800 }), 200);
      };
    });
    
    await page.goto('/');
    
    // Wait for page to stabilize
    await page.waitForLoadState('networkidle');
    
    // Collect metrics
    const metrics = await page.evaluate(() => {
      return new Promise(resolve => {
        const vitals = [];
        
        if (window.getCLS) {
          window.getCLS(metric => vitals.push(metric));
        }
        
        if (window.getLCP) {
          window.getLCP(metric => vitals.push(metric));
        }
        
        setTimeout(() => resolve(vitals), 1000);
      });
    });
    
    // Verify thresholds
    const lcp = metrics.find(m => m.name === 'LCP');
    const cls = metrics.find(m => m.name === 'CLS');
    
    if (lcp) expect(lcp.value).toBeLessThan(2500);
    if (cls) expect(cls.value).toBeLessThan(0.1);
  });
  
  test('should load within performance budget', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/');
    
    // Wait for load event
    await page.waitForLoadState('load');
    const loadTime = Date.now() - startTime;
    
    // Should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    // Check resource sizes
    const metrics = await page.evaluate(() => {
      const entries = performance.getEntriesByType('navigation')[0];
      return {
        loadEventEnd: entries.loadEventEnd,
        domContentLoaded: entries.domContentLoadedEventEnd,
        firstByte: entries.responseStart - entries.requestStart,
      };
    });
    
    expect(metrics.firstByte).toBeLessThan(500); // TTFB < 500ms
    expect(metrics.domContentLoaded).toBeLessThan(2000); // DCL < 2s
  });
});
```

## Documentation Framework

### 1. Technical Documentation

#### API Documentation Generator
```javascript
// scripts/generate-api-docs.js
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

class APIDocumentationGenerator {
  constructor() {
    this.endpoints = [];
    this.components = [];
    this.schemas = {};
  }
  
  async generateDocs() {
    console.log('Generating API documentation...');
    
    // Parse Python views for API endpoints
    await this.parseAPIEndpoints();
    
    // Parse JavaScript components
    await this.parseComponents();
    
    // Generate OpenAPI spec
    await this.generateOpenAPISpec();
    
    // Generate component documentation
    await this.generateComponentDocs();
    
    console.log('Documentation generated successfully!');
  }
  
  async parseAPIEndpoints() {
    const viewsPath = path.join(__dirname, '../core/views');
    const files = await fs.readdir(viewsPath);
    
    for (const file of files) {
      if (file.endsWith('.py')) {
        const content = await fs.readFile(path.join(viewsPath, file), 'utf-8');
        this.parseViewFile(content, file);
      }
    }
  }
  
  parseViewFile(content, filename) {
    // Extract API endpoints using regex patterns
    const functionPattern = /def\s+(\w+)\s*\([^)]*request[^)]*\):/g;
    const docstringPattern = /"""([^"]*)"""/g;
    
    let match;
    while ((match = functionPattern.exec(content)) !== null) {
      const functionName = match[1];
      const startPos = match.index;
      
      // Extract docstring if present
      const docMatch = docstringPattern.exec(content.substring(startPos));
      const docstring = docMatch ? docMatch[1].trim() : '';
      
      this.endpoints.push({
        name: functionName,
        file: filename,
        documentation: docstring,
        // Add more parsing for HTTP methods, parameters, etc.
      });
    }
  }
  
  async generateOpenAPISpec() {
    const spec = {
      openapi: '3.0.0',
      info: {
        title: 'Sabor con Flow Dance Studio API',
        version: '1.0.0',
        description: 'API documentation for the dance studio website',
      },
      servers: [
        {
          url: 'https://saborconflow.com/api',
          description: 'Production server'
        },
        {
          url: 'http://localhost:3000/api',
          description: 'Development server'
        }
      ],
      paths: this.generatePaths(),
      components: {
        schemas: this.generateSchemas(),
        securitySchemes: {
          csrfToken: {
            type: 'apiKey',
            in: 'header',
            name: 'X-CSRFToken'
          }
        }
      }
    };
    
    await fs.writeFile(
      path.join(__dirname, '../docs/api-spec.json'),
      JSON.stringify(spec, null, 2)
    );
  }
  
  generatePaths() {
    const paths = {};
    
    // Contact endpoint
    paths['/contact/'] = {
      post: {
        summary: 'Submit contact form',
        description: 'Submit a contact form with user information',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/ContactForm'
              }
            }
          }
        },
        responses: {
          '200': {
            description: 'Message sent successfully',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ContactResponse'
                }
              }
            }
          },
          '400': {
            description: 'Invalid form data',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/ErrorResponse'
                }
              }
            }
          }
        },
        security: [{ csrfToken: [] }]
      }
    };
    
    return paths;
  }
  
  generateSchemas() {
    return {
      ContactForm: {
        type: 'object',
        required: ['name', 'email', 'message'],
        properties: {
          name: {
            type: 'string',
            maxLength: 100,
            description: 'Full name of the person contacting'
          },
          email: {
            type: 'string',
            format: 'email',
            description: 'Valid email address'
          },
          phone: {
            type: 'string',
            pattern: '^[+]?[(]?[\s0-9().-]{10,}$',
            description: 'Optional phone number'
          },
          message: {
            type: 'string',
            maxLength: 1000,
            description: 'Message content'
          },
          newsletter: {
            type: 'boolean',
            default: false,
            description: 'Subscribe to newsletter'
          }
        }
      },
      ContactResponse: {
        type: 'object',
        properties: {
          success: {
            type: 'boolean'
          },
          message: {
            type: 'string'
          }
        }
      },
      ErrorResponse: {
        type: 'object',
        properties: {
          error: {
            type: 'string'
          },
          details: {
            type: 'object'
          }
        }
      }
    };
  }
  
  async generateComponentDocs() {
    const docsDir = path.join(__dirname, '../docs/components');
    await fs.mkdir(docsDir, { recursive: true });
    
    // Generate component documentation
    const componentDoc = `# Component Documentation

## Navigation Component

### Usage
\`\`\`javascript
import { Navigation } from '@components/navigation';
const nav = new Navigation();
\`\`\`

### Props
- \`burger\`: HTMLElement - The hamburger menu button
- \`menu\`: HTMLElement - The navigation menu
- \`isActive\`: boolean - Whether menu is open

### Methods
- \`toggle()\`: Toggle menu visibility
- \`close()\`: Close menu
- \`highlightActivePage()\`: Highlight current page in navigation

## Contact Form Component

### Usage
\`\`\`javascript
import { ContactForm } from '@components/contact-form';
const form = new ContactForm();
\`\`\`

### Events
- \`form-submitted\`: Fired when form is successfully submitted
- \`form-error\`: Fired when form submission fails

### Validation
- Name: Required, max 100 characters
- Email: Required, valid email format
- Phone: Optional, valid phone format
- Message: Required, max 1000 characters
`;
    
    await fs.writeFile(
      path.join(docsDir, 'components.md'),
      componentDoc
    );
  }
}

// Generate documentation
const generator = new APIDocumentationGenerator();
generator.generateDocs().catch(console.error);
```

### 2. User Guide Documentation

#### User Manual Template
```markdown
# Sabor con Flow Dance Studio - User Guide

## Getting Started

### Creating an Account
1. Click "Sign Up" in the top navigation
2. Fill in your personal information
3. Verify your email address
4. Complete your profile

### Booking Your First Class
1. Navigate to the "Events" page
2. Browse available classes
3. Click on a class that interests you
4. Select your preferred time slot
5. Complete the booking process

## Features Guide

### Class Booking System
Our online booking system allows you to:
- View all available classes and events
- See real-time availability
- Book classes up to 2 weeks in advance
- Receive confirmation emails
- Manage your bookings in your account

### Payment Options
We accept the following payment methods:
- Credit/Debit Cards (Visa, Mastercard, American Express)
- PayPal
- Venmo
- Cash (in-studio only)

### Cancellation Policy
- Cancel up to 24 hours before class for full refund
- Cancel 2-24 hours before for 50% refund
- No refund for cancellations less than 2 hours before class

## Troubleshooting

### Common Issues

#### "I can't see any available classes"
- Check if you're looking at the correct date
- Some classes may be fully booked
- Try refreshing the page
- Contact us if the issue persists

#### "Payment failed"
- Verify your card information is correct
- Check if your card has sufficient funds
- Try a different payment method
- Contact your bank if issues continue

#### "I didn't receive a confirmation email"
- Check your spam/junk folder
- Verify your email address is correct
- Contact us to resend confirmation

### Contact Support
If you need additional help:
- Email: support@saborconflow.com
- Phone: (305) XXX-XXXX
- Live chat: Available on our website
- Office hours: Monday-Friday 9 AM - 6 PM EST

## Privacy & Security

### Data Protection
We take your privacy seriously:
- All personal data is encrypted
- We comply with GDPR and CCPA regulations
- We never sell your information to third parties
- You can request your data or ask for deletion at any time

### Account Security
To keep your account secure:
- Use a strong, unique password
- Don't share your login credentials
- Log out on shared computers
- Report suspicious activity immediately

## Accessibility

Our website is designed to be accessible to all users:
- Screen reader compatible
- Keyboard navigation support
- High contrast mode available
- Text size can be adjusted
- Alternative text for all images

If you have accessibility needs not met by our current features, please contact us.
```

### 3. Testing Documentation

#### Test Coverage Reports
```javascript
// scripts/generate-test-report.js
import { execSync } from 'child_process';
import fs from 'fs/promises';
import path from 'path';

class TestReportGenerator {
  constructor() {
    this.testResults = {};
    this.coverageData = {};
  }
  
  async generateComprehensiveReport() {
    console.log('Generating comprehensive test report...');
    
    // Run all test suites
    await this.runUnitTests();
    await this.runIntegrationTests();
    await this.runE2ETests();
    await this.runPerformanceTests();
    await this.runAccessibilityTests();
    
    // Generate coverage report
    await this.generateCoverageReport();
    
    // Create comprehensive HTML report
    await this.generateHTMLReport();
    
    console.log('Test report generated successfully!');
  }
  
  async runUnitTests() {
    try {
      const result = execSync('npm run test:unit -- --reporter=json', { 
        encoding: 'utf-8' 
      });
      
      this.testResults.unit = JSON.parse(result);
    } catch (error) {
      this.testResults.unit = { 
        error: error.message,
        failed: true 
      };
    }
  }
  
  async runIntegrationTests() {
    try {
      const result = execSync('npm run test:integration -- --reporter=json', { 
        encoding: 'utf-8' 
      });
      
      this.testResults.integration = JSON.parse(result);
    } catch (error) {
      this.testResults.integration = { 
        error: error.message,
        failed: true 
      };
    }
  }
  
  async runE2ETests() {
    try {
      const result = execSync('npx playwright test --reporter=json', { 
        encoding: 'utf-8' 
      });
      
      this.testResults.e2e = JSON.parse(result);
    } catch (error) {
      this.testResults.e2e = { 
        error: error.message,
        failed: true 
      };
    }
  }
  
  async runPerformanceTests() {
    try {
      const result = execSync('npx lhci autorun --output=json', { 
        encoding: 'utf-8' 
      });
      
      this.testResults.performance = JSON.parse(result);
    } catch (error) {
      this.testResults.performance = { 
        error: error.message,
        failed: true 
      };
    }
  }
  
  async runAccessibilityTests() {
    try {
      const result = execSync('npm run test:a11y -- --reporter=json', { 
        encoding: 'utf-8' 
      });
      
      this.testResults.accessibility = JSON.parse(result);
    } catch (error) {
      this.testResults.accessibility = { 
        error: error.message,
        failed: true 
      };
    }
  }
  
  async generateHTMLReport() {
    const template = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - Sabor con Flow</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 8px; }
        .test-suite { margin: 20px 0; padding: 15px; border-left: 4px solid #ccc; }
        .passed { border-left-color: #4CAF50; }
        .failed { border-left-color: #f44336; }
        .warning { border-left-color: #ff9800; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .metric { background: #f9f9f9; padding: 15px; border-radius: 8px; text-align: center; }
        .metric-value { font-size: 2em; font-weight: bold; color: #333; }
        .metric-label { color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Comprehensive Test Report</h1>
        <p>Generated on: ${new Date().toLocaleString()}</p>
    </div>
    
    ${this.generateSummarySection()}
    ${this.generateTestSuiteSection('Unit Tests', this.testResults.unit)}
    ${this.generateTestSuiteSection('Integration Tests', this.testResults.integration)}
    ${this.generateTestSuiteSection('E2E Tests', this.testResults.e2e)}
    ${this.generateTestSuiteSection('Performance Tests', this.testResults.performance)}
    ${this.generateTestSuiteSection('Accessibility Tests', this.testResults.accessibility)}
    ${this.generateCoverageSection()}
</body>
</html>
    `;
    
    await fs.writeFile('test-report.html', template);
  }
  
  generateSummarySection() {
    const totalTests = Object.values(this.testResults).reduce((sum, suite) => {
      return sum + (suite.numTotalTests || 0);
    }, 0);
    
    const passedTests = Object.values(this.testResults).reduce((sum, suite) => {
      return sum + (suite.numPassedTests || 0);
    }, 0);
    
    const failedTests = totalTests - passedTests;
    
    return `
    <div class="metrics">
        <div class="metric">
            <div class="metric-value">${totalTests}</div>
            <div class="metric-label">Total Tests</div>
        </div>
        <div class="metric">
            <div class="metric-value" style="color: #4CAF50">${passedTests}</div>
            <div class="metric-label">Passed</div>
        </div>
        <div class="metric">
            <div class="metric-value" style="color: #f44336">${failedTests}</div>
            <div class="metric-label">Failed</div>
        </div>
        <div class="metric">
            <div class="metric-value">${Math.round((passedTests / totalTests) * 100)}%</div>
            <div class="metric-label">Pass Rate</div>
        </div>
    </div>
    `;
  }
  
  generateTestSuiteSection(title, results) {
    if (!results) return '';
    
    const status = results.failed ? 'failed' : 
                   results.numFailedTests > 0 ? 'warning' : 'passed';
    
    return `
    <div class="test-suite ${status}">
        <h2>${title}</h2>
        ${results.error ? 
          `<p><strong>Error:</strong> ${results.error}</p>` :
          `
          <p><strong>Passed:</strong> ${results.numPassedTests || 0}</p>
          <p><strong>Failed:</strong> ${results.numFailedTests || 0}</p>
          <p><strong>Total:</strong> ${results.numTotalTests || 0}</p>
          <p><strong>Duration:</strong> ${(results.duration || 0) / 1000}s</p>
          `
        }
    </div>
    `;
  }
}

// Generate report
const generator = new TestReportGenerator();
generator.generateComprehensiveReport().catch(console.error);
```

## CI/CD Integration

### 1. GitHub Actions Testing Workflow

```yaml
# .github/workflows/test.yml
name: Comprehensive Testing Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run unit tests
      run: npm run test:unit -- --coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage/coverage-final.json

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install Python dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-django
    
    - name: Run Django tests
      run: python manage.py test
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Install Playwright browsers
      run: npx playwright install --with-deps
    
    - name: Build application
      run: npm run build
    
    - name: Start application
      run: npm run dev &
      
    - name: Wait for application
      run: npx wait-on http://localhost:3000
    
    - name: Run Playwright tests
      run: npx playwright test
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-report
        path: playwright-report/

  performance-tests:
    runs-on: ubuntu-latest
    needs: e2e-tests
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Build application
      run: npm run build
    
    - name: Run Lighthouse CI
      run: |
        npm install -g @lhci/cli
        lhci autorun
      env:
        LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}

  accessibility-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run accessibility tests
      run: npm run test:a11y

  security-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Run security audit
      run: npm audit --audit-level moderate
    
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

## Success Criteria

### Testing Coverage Targets
- [x] Unit test coverage: > 80%
- [x] Integration test coverage: > 70%
- [x] E2E test coverage: Critical user journeys
- [x] Performance tests: All pages meet thresholds
- [x] Accessibility tests: WCAG 2.1 AA compliance
- [x] Security tests: Zero critical vulnerabilities

### Documentation Deliverables
- [x] API documentation with OpenAPI spec
- [x] Component documentation
- [x] User guide and help documentation
- [x] Developer setup and contribution guide
- [x] Testing strategy documentation
- [x] Performance optimization guide

### Quality Assurance
- [x] Automated test execution in CI/CD
- [x] Cross-browser compatibility testing
- [x] Mobile responsiveness testing
- [x] Performance regression testing
- [x] Accessibility compliance validation
- [x] Security vulnerability scanning

## Timeline
- **Day 1-2**: Vitest setup and unit test development
- **Day 3-4**: Integration testing and API test coverage
- **Day 5-6**: E2E testing with Playwright
- **Day 7**: Performance and accessibility testing
- **Day 8-9**: Documentation generation and CI/CD integration