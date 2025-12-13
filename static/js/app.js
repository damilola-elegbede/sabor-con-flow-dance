/**
 * Sabor Con Flow - Main Application JavaScript
 * This file bundles all client-side functionality and CSS imports
 */

// Import styles (Vite will process these)
import '../css/main.css';

// Initialization guard to prevent double initialization
// (inline script in base.html also initializes navigation in development mode)
const alreadyInitialized = window.__SABOR_APP_INITIALIZED__;
window.__SABOR_APP_INITIALIZED__ = true;

/**
 * Mobile Navigation Module
 * Handles menu toggle, close button, keyboard navigation, focus trap, and scroll effects
 */
function initMobileNavigation() {
  'use strict';

  // DOM Elements
  const menuToggle = document.querySelector('.menu-toggle');
  const nav = document.getElementById('site-nav');
  const navClose = document.querySelector('.nav-close');
  const header = document.querySelector('.header');
  const announcer = document.getElementById('nav-announcer');

  if (!menuToggle || !nav) return;

  // State
  let isOpen = false;
  let focusableElements = [];
  let firstFocusable = null;
  let lastFocusable = null;

  // Update focusable elements list
  function updateFocusableElements() {
    focusableElements = nav.querySelectorAll(
      'button:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])'
    );
    if (focusableElements.length > 0) {
      firstFocusable = focusableElements[0];
      lastFocusable = focusableElements[focusableElements.length - 1];
    }
  }

  // Announce to screen readers
  function announce(message) {
    if (announcer) {
      announcer.textContent = '';
      setTimeout(() => {
        announcer.textContent = message;
      }, 100);
    }
  }

  // Open menu
  function openMenu() {
    isOpen = true;
    nav.classList.add('active');
    menuToggle.classList.add('active');
    menuToggle.setAttribute('aria-expanded', 'true');
    nav.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    announce('Navigation menu opened');
    updateFocusableElements();

    // Focus close button after animation
    setTimeout(() => {
      if (navClose) navClose.focus();
    }, 350);
  }

  // Close menu
  function closeMenu(returnFocus = true) {
    isOpen = false;
    nav.classList.remove('active');
    menuToggle.classList.remove('active');
    menuToggle.setAttribute('aria-expanded', 'false');
    nav.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';

    announce('Navigation menu closed');

    if (returnFocus) {
      menuToggle.focus();
    }
  }

  // Toggle menu
  function toggleMenu() {
    if (isOpen) {
      closeMenu();
    } else {
      openMenu();
    }
  }

  // Handle Tab key for focus trap
  function handleTabKey(e) {
    if (!isOpen || !firstFocusable || !lastFocusable) return;

    if (e.shiftKey) {
      if (document.activeElement === firstFocusable) {
        e.preventDefault();
        lastFocusable.focus();
      }
    } else {
      if (document.activeElement === lastFocusable) {
        e.preventDefault();
        firstFocusable.focus();
      }
    }
  }

  // Event Listeners
  menuToggle.addEventListener('click', toggleMenu);

  if (navClose) {
    navClose.addEventListener('click', () => closeMenu(true));
  }

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (isOpen && !nav.contains(e.target) && !menuToggle.contains(e.target)) {
      closeMenu(false);
    }
  });

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOpen) {
      e.preventDefault();
      closeMenu(true);
    }
    if (e.key === 'Tab' && isOpen) {
      handleTabKey(e);
    }
  });

  // Header Scroll Blur Effect
  const SCROLL_THRESHOLD = 50;
  let ticking = false;
  let lastScrollY = 0;

  function updateHeaderScroll() {
    if (lastScrollY > SCROLL_THRESHOLD) {
      header.classList.add('header--scrolled');
    } else {
      header.classList.remove('header--scrolled');
    }
    ticking = false;
  }

  function onScroll() {
    lastScrollY = window.scrollY;
    if (!ticking) {
      window.requestAnimationFrame(updateHeaderScroll);
      ticking = true;
    }
  }

  if (header) {
    window.addEventListener('scroll', onScroll, { passive: true });
    // Check initial scroll position
    lastScrollY = window.scrollY;
    updateHeaderScroll();
  }
}

/**
 * Lazy loading fallback for images
 * Native lazy loading is used when supported, with IntersectionObserver fallback
 */
function initLazyLoading() {
  // Check for native lazy loading support
  if ('loading' in HTMLImageElement.prototype) {
    // Native lazy loading supported - nothing to do
    return;
  }

  // Fallback for browsers without native lazy loading
  const lazyImages = document.querySelectorAll('img[loading="lazy"]');

  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
          }
          imageObserver.unobserve(img);
        }
      });
    });

    lazyImages.forEach((img) => imageObserver.observe(img));
  }
}

// Initialize all modules when DOM is ready (unless already initialized by inline script)
if (!alreadyInitialized) {
  document.addEventListener('DOMContentLoaded', () => {
    initMobileNavigation();
    initLazyLoading();
  });
}

// Export for potential module usage
export { initMobileNavigation, initLazyLoading };
