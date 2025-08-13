/**
 * Enhanced Mobile Navigation with Progressive Enhancement
 * Works without JavaScript and enhances with JS features
 */

export default class MobileNav {
  constructor(options = {}) {
    this.options = {
      toggleSelector: '#navbar-toggle',
      menuSelector: '#navbar-mobile',
      overlaySelector: '#mobile-menu-overlay',
      closeSelector: '#mobile-menu-close',
      breakpoint: 768,
      animationDuration: 300,
      enableSwipeGestures: true,
      enableKeyboardNavigation: true,
      ...options
    };

    this.isOpen = false;
    this.lastFocusedElement = null;
    this.touchStartX = 0;
    this.touchStartY = 0;
    this.swipeThreshold = 50;
    
    this.elements = {};
    this.init();
  }

  init() {
    this.cacheElements();
    
    if (!this.elements.toggle || !this.elements.menu) {
      console.warn('Mobile nav: Required elements not found');
      return;
    }

    this.setupEventListeners();
    this.setupAccessibility();
    this.setupProgressiveEnhancement();
    
    // Handle initial state
    this.updateState();
    
    // Mobile navigation enhanced
  }

  cacheElements() {
    this.elements = {
      toggle: document.querySelector(this.options.toggleSelector),
      menu: document.querySelector(this.options.menuSelector),
      overlay: document.querySelector(this.options.overlaySelector),
      close: document.querySelector(this.options.closeSelector),
      menuItems: document.querySelectorAll(`${this.options.menuSelector} a`),
      body: document.body
    };
  }

  setupEventListeners() {
    // Toggle button
    if (this.elements.toggle) {
      this.elements.toggle.addEventListener('click', this.handleToggle.bind(this));
    }

    // Close button
    if (this.elements.close) {
      this.elements.close.addEventListener('click', this.handleClose.bind(this));
    }

    // Overlay click
    if (this.elements.overlay) {
      this.elements.overlay.addEventListener('click', this.handleOverlayClick.bind(this));
    }

    // Menu item clicks
    this.elements.menuItems.forEach(item => {
      item.addEventListener('click', this.handleMenuItemClick.bind(this));
    });

    // Keyboard navigation
    if (this.options.enableKeyboardNavigation) {
      document.addEventListener('keydown', this.handleKeyDown.bind(this));
    }

    // Window resize
    let resizeTimer;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        this.handleResize();
      }, 150);
    });

    // Swipe gestures on mobile
    if (this.options.enableSwipeGestures) {
      this.setupSwipeGestures();
    }

    // Focus management
    this.setupFocusManagement();
  }

  setupSwipeGestures() {
    if (this.elements.menu) {
      this.elements.menu.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
      this.elements.menu.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: true });
    }

    // Also allow swiping from edge to open menu
    document.addEventListener('touchstart', this.handleEdgeSwipeStart.bind(this), { passive: true });
    document.addEventListener('touchend', this.handleEdgeSwipeEnd.bind(this), { passive: true });
  }

  setupAccessibility() {
    // Ensure proper ARIA attributes
    if (this.elements.toggle) {
      this.elements.toggle.setAttribute('aria-expanded', 'false');
      this.elements.toggle.setAttribute('aria-controls', this.elements.menu.id);
    }

    if (this.elements.menu) {
      this.elements.menu.setAttribute('aria-hidden', 'true');
      this.elements.menu.setAttribute('role', 'dialog');
      this.elements.menu.setAttribute('aria-modal', 'true');
    }

    if (this.elements.overlay) {
      this.elements.overlay.setAttribute('aria-hidden', 'true');
    }
  }

  setupFocusManagement() {
    // Get all focusable elements in menu
    this.focusableElements = this.elements.menu.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    // Prevent focus entering menu when closed
    this.elements.menu.addEventListener('focusin', (e) => {
      if (!this.isOpen) {
        e.preventDefault();
        this.elements.toggle.focus();
      }
    });
  }

  setupProgressiveEnhancement() {
    // Add enhanced classes for CSS targeting
    document.documentElement.classList.add('js-mobile-nav');
    
    // Remove CSS-only fallback styles
    const style = document.createElement('style');
    style.textContent = `
      .js-mobile-nav .mobile-menu-css-fallback {
        display: none !important;
      }
    `;
    document.head.appendChild(style);

    // Add loading state
    this.elements.menu.classList.add('mobile-nav-enhanced');
  }

  handleToggle(event) {
    event.preventDefault();
    event.stopPropagation();
    
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }

  handleClose(event) {
    event.preventDefault();
    this.close();
  }

  handleOverlayClick(event) {
    if (event.target === this.elements.overlay) {
      this.close();
    }
  }

  handleMenuItemClick(event) {
    const link = event.currentTarget;
    const href = link.getAttribute('href');
    
    // If it's an anchor link, allow default behavior and close menu
    if (href && href.startsWith('#')) {
      setTimeout(() => this.close(), 100);
    } else {
      // For regular links, close menu immediately
      this.close();
    }
  }

  handleKeyDown(event) {
    if (!this.isOpen) return;

    switch (event.key) {
      case 'Escape':
        event.preventDefault();
        this.close();
        break;
      case 'Tab':
        this.handleTabKey(event);
        break;
    }
  }

  handleTabKey(event) {
    if (this.focusableElements.length === 0) return;

    const firstFocusable = this.focusableElements[0];
    const lastFocusable = this.focusableElements[this.focusableElements.length - 1];

    if (event.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstFocusable) {
        event.preventDefault();
        lastFocusable.focus();
      }
    } else {
      // Tab
      if (document.activeElement === lastFocusable) {
        event.preventDefault();
        firstFocusable.focus();
      }
    }
  }

  handleResize() {
    // Close menu if window becomes wider than breakpoint
    if (window.innerWidth >= this.options.breakpoint && this.isOpen) {
      this.close();
    }
  }

  handleTouchStart(event) {
    this.touchStartX = event.touches[0].clientX;
    this.touchStartY = event.touches[0].clientY;
  }

  handleTouchEnd(event) {
    const touchEndX = event.changedTouches[0].clientX;
    const touchEndY = event.changedTouches[0].clientY;
    
    const deltaX = this.touchStartX - touchEndX;
    const deltaY = Math.abs(this.touchStartY - touchEndY);
    
    // Only process horizontal swipes (not vertical scrolling)
    if (deltaY < this.swipeThreshold && Math.abs(deltaX) > this.swipeThreshold) {
      if (deltaX > 0) {
        // Swipe left to close menu
        this.close();
      }
    }
  }

  handleEdgeSwipeStart(event) {
    // Only process if menu is closed and swipe starts from left edge
    if (!this.isOpen && event.touches[0].clientX < 20) {
      this.touchStartX = event.touches[0].clientX;
      this.touchStartY = event.touches[0].clientY;
    }
  }

  handleEdgeSwipeEnd(event) {
    if (this.isOpen) return;

    const touchEndX = event.changedTouches[0].clientX;
    const touchEndY = event.changedTouches[0].clientY;
    
    const deltaX = touchEndX - this.touchStartX;
    const deltaY = Math.abs(touchEndY - this.touchStartY);
    
    // Open menu with right swipe from edge
    if (deltaY < this.swipeThreshold && deltaX > this.swipeThreshold) {
      this.open();
    }
  }

  open() {
    if (this.isOpen) return;

    this.isOpen = true;
    this.lastFocusedElement = document.activeElement;

    // Add classes for animation
    this.elements.body.classList.add('mobile-menu-open');
    this.elements.menu.classList.add('active');
    
    if (this.elements.overlay) {
      this.elements.overlay.classList.add('active');
    }

    // Update ARIA attributes
    this.updateARIAAttributes();

    // Prevent body scroll
    this.preventBodyScroll();

    // Focus management
    setTimeout(() => {
      if (this.elements.close) {
        this.elements.close.focus();
      } else if (this.focusableElements.length > 0) {
        this.focusableElements[0].focus();
      }
    }, this.options.animationDuration);

    // Announce to screen readers
    this.announceToScreenReader('Navigation menu opened');

    // Track analytics
    this.trackEvent('mobile_menu_opened');
  }

  close() {
    if (!this.isOpen) return;

    this.isOpen = false;

    // Remove classes
    this.elements.body.classList.remove('mobile-menu-open');
    this.elements.menu.classList.remove('active');
    
    if (this.elements.overlay) {
      this.elements.overlay.classList.remove('active');
    }

    // Update ARIA attributes
    this.updateARIAAttributes();

    // Restore body scroll
    this.restoreBodyScroll();

    // Restore focus
    if (this.lastFocusedElement) {
      this.lastFocusedElement.focus();
    }

    // Announce to screen readers
    this.announceToScreenReader('Navigation menu closed');

    // Track analytics
    this.trackEvent('mobile_menu_closed');
  }

  updateARIAAttributes() {
    if (this.elements.toggle) {
      this.elements.toggle.setAttribute('aria-expanded', this.isOpen.toString());
    }

    if (this.elements.menu) {
      this.elements.menu.setAttribute('aria-hidden', (!this.isOpen).toString());
    }

    if (this.elements.overlay) {
      this.elements.overlay.setAttribute('aria-hidden', (!this.isOpen).toString());
    }
  }

  updateState() {
    // Set initial state based on current classes (for server-side rendering)
    this.isOpen = this.elements.menu.classList.contains('active');
    this.updateARIAAttributes();
  }

  preventBodyScroll() {
    const scrollY = window.pageYOffset;
    this.elements.body.style.position = 'fixed';
    this.elements.body.style.top = `-${scrollY}px`;
    this.elements.body.style.width = '100%';
  }

  restoreBodyScroll() {
    const scrollY = this.elements.body.style.top;
    this.elements.body.style.position = '';
    this.elements.body.style.top = '';
    this.elements.body.style.width = '';
    window.scrollTo(0, parseInt(scrollY || '0') * -1);
  }

  announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.classList.add('sr-only');
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }

  trackEvent(action) {
    if (window.gtag) {
      window.gtag('event', action, {
        event_category: 'navigation',
        event_label: 'mobile_menu'
      });
    }
  }

  // Public API
  toggle() {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }

  isMenuOpen() {
    return this.isOpen;
  }

  destroy() {
    // Remove event listeners and cleanup
    this.elements.toggle?.removeEventListener('click', this.handleToggle);
    this.elements.close?.removeEventListener('click', this.handleClose);
    this.elements.overlay?.removeEventListener('click', this.handleOverlayClick);
    
    this.elements.menuItems.forEach(item => {
      item.removeEventListener('click', this.handleMenuItemClick);
    });

    document.removeEventListener('keydown', this.handleKeyDown);
    
    // Remove enhanced classes
    document.documentElement.classList.remove('js-mobile-nav');
    this.elements.menu.classList.remove('mobile-nav-enhanced');
  }

  // Static factory method
  static init(options = {}) {
    return new MobileNav(options);
  }
}

// Auto-initialize if not using module system
if (typeof window !== 'undefined' && !window.moduleSystem) {
  document.addEventListener('DOMContentLoaded', () => {
    MobileNav.init();
  });
}