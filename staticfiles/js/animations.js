/**
 * Sabor Con Flow - Scroll Animation System
 * Version: 1.0.0
 *
 * This module provides:
 * - Scroll-triggered animations via Intersection Observer
 * - Staggered entrance animations for grids
 * - Parallax effects for hero elements
 * - Text reveal animations
 *
 * All animations respect prefers-reduced-motion preference.
 */

(function() {
  'use strict';

  /* ==========================================================================
     CONFIGURATION
     ========================================================================== */

  const CONFIG = {
    // Intersection Observer settings
    observer: {
      root: null,
      rootMargin: '0px 0px -10% 0px',
      threshold: [0, 0.1, 0.25]
    },

    // Animation timing
    timing: {
      defaultDuration: 600,
      defaultDelay: 0,
      staggerDelay: 100,
      maxStaggerDelay: 500
    },

    // Easing functions (matching CSS variables)
    easing: {
      default: 'cubic-bezier(0.215, 0.61, 0.355, 1)',
      spring: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
      expo: 'cubic-bezier(0.19, 1, 0.22, 1)'
    },

    // Parallax settings
    parallax: {
      factor: 0.15,
      smoothing: 0.1,
      maxOffset: 100
    }
  };

  /* ==========================================================================
     UTILITY FUNCTIONS
     ========================================================================== */

  /**
   * Check if user prefers reduced motion
   * @returns {boolean}
   */
  function prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  /**
   * Debounce function for performance
   * @param {Function} func
   * @param {number} wait
   * @returns {Function}
   */
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  /* ==========================================================================
     SCROLL ANIMATIONS MODULE
     ========================================================================== */

  const ScrollAnimations = {
    observer: null,

    presets: {
      'fade-up': {
        initial: { opacity: '0', transform: 'translateY(30px)' },
        animate: { opacity: '1', transform: 'translateY(0)' }
      },
      'fade-down': {
        initial: { opacity: '0', transform: 'translateY(-30px)' },
        animate: { opacity: '1', transform: 'translateY(0)' }
      },
      'fade-left': {
        initial: { opacity: '0', transform: 'translateX(30px)' },
        animate: { opacity: '1', transform: 'translateX(0)' }
      },
      'fade-right': {
        initial: { opacity: '0', transform: 'translateX(-30px)' },
        animate: { opacity: '1', transform: 'translateX(0)' }
      },
      'scale-up': {
        initial: { opacity: '0', transform: 'scale(0.9)' },
        animate: { opacity: '1', transform: 'scale(1)' }
      },
      'scale-fade': {
        initial: { opacity: '0', transform: 'scale(0.95) translateY(20px)' },
        animate: { opacity: '1', transform: 'scale(1) translateY(0)' }
      }
    },

    init() {
      if (prefersReducedMotion()) {
        this.showAllElements();
        return;
      }

      this.observer = new IntersectionObserver(
        this.handleIntersection.bind(this),
        CONFIG.observer
      );

      this.initializeElements();
      this.observeElements();
    },

    showAllElements() {
      const elements = document.querySelectorAll('[data-animate]');
      elements.forEach(el => {
        el.style.opacity = '1';
        el.style.transform = 'none';
        el.classList.add('animate-complete');
      });
    },

    initializeElements() {
      const elements = document.querySelectorAll('[data-animate]');

      elements.forEach(el => {
        const preset = el.dataset.animate || 'fade-up';
        const animation = this.presets[preset];

        if (!animation) return;

        Object.assign(el.style, animation.initial);

        const duration = el.dataset.duration || CONFIG.timing.defaultDuration;
        const delay = el.dataset.delay || CONFIG.timing.defaultDelay;
        const easing = el.dataset.easing || CONFIG.easing.default;

        el.style.transition = `
          opacity ${duration}ms ${easing} ${delay}ms,
          transform ${duration}ms ${easing} ${delay}ms
        `;

        el.style.willChange = 'opacity, transform';
      });
    },

    observeElements() {
      const elements = document.querySelectorAll('[data-animate]');
      elements.forEach(el => this.observer.observe(el));
    },

    handleIntersection(entries) {
      entries.forEach(entry => {
        if (entry.isIntersecting && entry.intersectionRatio >= 0.1) {
          this.animateElement(entry.target);
          this.observer.unobserve(entry.target);
        }
      });
    },

    animateElement(el) {
      const preset = el.dataset.animate || 'fade-up';
      const animation = this.presets[preset];

      if (!animation) return;

      requestAnimationFrame(() => {
        Object.assign(el.style, animation.animate);
        el.classList.add('animate-in');

        const duration = parseInt(el.dataset.duration || CONFIG.timing.defaultDuration);
        const delay = parseInt(el.dataset.delay || CONFIG.timing.defaultDelay);

        setTimeout(() => {
          el.style.willChange = 'auto';
          el.classList.add('animate-complete');
        }, duration + delay + 100);
      });
    },

    initStaggeredGroup(containerSelector, childSelector, preset = 'fade-up') {
      const containers = document.querySelectorAll(containerSelector);

      containers.forEach(container => {
        const children = container.querySelectorAll(childSelector);

        children.forEach((child, index) => {
          // Only set if not already set
          if (!child.dataset.animate) {
            child.dataset.animate = preset;
          }
          if (!child.dataset.delay) {
            child.dataset.delay = Math.min(
              index * CONFIG.timing.staggerDelay,
              CONFIG.timing.maxStaggerDelay
            );
          }
        });
      });
    },

    destroy() {
      if (this.observer) {
        this.observer.disconnect();
      }
    }
  };

  /* ==========================================================================
     PARALLAX EFFECT MODULE
     ========================================================================== */

  const ParallaxEffect = {
    elements: [],
    state: {
      scrollY: 0,
      targetY: 0,
      rafId: null,
      isRunning: false
    },

    init() {
      if (prefersReducedMotion()) return;

      this.elements = document.querySelectorAll('[data-parallax]');
      if (this.elements.length === 0) return;

      this.handleScroll = this.handleScroll.bind(this);
      this.animate = this.animate.bind(this);

      window.addEventListener('scroll', this.handleScroll, { passive: true });
      this.startLoop();
    },

    handleScroll() {
      this.state.targetY = window.scrollY;
    },

    startLoop() {
      if (this.state.isRunning) return;
      this.state.isRunning = true;
      this.animate();
    },

    animate() {
      this.state.scrollY += (this.state.targetY - this.state.scrollY) * CONFIG.parallax.smoothing;

      this.elements.forEach(el => {
        const factor = parseFloat(el.dataset.parallaxFactor) || CONFIG.parallax.factor;
        const direction = el.dataset.parallaxDirection || 'up';

        let offset = this.state.scrollY * factor;
        offset = Math.min(Math.max(offset, -CONFIG.parallax.maxOffset), CONFIG.parallax.maxOffset);

        const transform = direction === 'up'
          ? `translateY(${offset}px)`
          : `translateY(${-offset}px)`;

        el.style.transform = transform;
      });

      this.state.rafId = requestAnimationFrame(this.animate);
    },

    destroy() {
      if (this.state.rafId) {
        cancelAnimationFrame(this.state.rafId);
      }
      window.removeEventListener('scroll', this.handleScroll);
    }
  };

  /* ==========================================================================
     TEXT REVEAL MODULE
     ========================================================================== */

  const TextReveal = {
    init() {
      if (prefersReducedMotion()) {
        this.showAllText();
        return;
      }

      this.splitTextElements();
      this.observeElements();
    },

    showAllText() {
      const elements = document.querySelectorAll('[data-text-reveal]');
      elements.forEach(el => {
        el.style.opacity = '1';
        el.classList.add('text-revealed');
      });
    },

    splitTextElements() {
      const elements = document.querySelectorAll('[data-text-reveal]');

      elements.forEach(el => {
        const text = el.textContent;
        const type = el.dataset.textReveal || 'words';

        el.innerHTML = '';
        el.setAttribute('aria-label', text);

        if (type === 'chars') {
          this.splitByChars(el, text);
        } else if (type === 'words') {
          this.splitByWords(el, text);
        } else if (type === 'lines') {
          this.wrapLine(el, text);
        }
      });
    },

    splitByChars(el, text) {
      const chars = text.split('');
      chars.forEach((char, i) => {
        const span = document.createElement('span');
        span.className = 'reveal-char';
        span.textContent = char === ' ' ? '\u00A0' : char;
        span.style.transitionDelay = `${i * 30}ms`;
        span.setAttribute('aria-hidden', 'true');
        el.appendChild(span);
      });
    },

    splitByWords(el, text) {
      const words = text.split(' ');
      words.forEach((word, i) => {
        const span = document.createElement('span');
        span.className = 'reveal-word';
        span.textContent = word;
        span.style.transitionDelay = `${i * 80}ms`;
        span.setAttribute('aria-hidden', 'true');
        el.appendChild(span);

        if (i < words.length - 1) {
          el.appendChild(document.createTextNode(' '));
        }
      });
    },

    wrapLine(el, text) {
      const wrapper = document.createElement('span');
      wrapper.className = 'reveal-line-inner';
      wrapper.textContent = text;
      wrapper.setAttribute('aria-hidden', 'true');

      const outer = document.createElement('span');
      outer.className = 'reveal-line';
      outer.appendChild(wrapper);

      el.appendChild(outer);
    },

    observeElements() {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              entry.target.classList.add('text-revealed');
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.2, rootMargin: '0px 0px -50px 0px' }
      );

      const elements = document.querySelectorAll('[data-text-reveal]');
      elements.forEach(el => observer.observe(el));
    }
  };

  /* ==========================================================================
     INITIALIZATION
     ========================================================================== */

  /**
   * Initialize all animation modules
   */
  function initAnimations() {
    // Setup staggered groups before initializing scroll animations
    ScrollAnimations.initStaggeredGroup('.gallery-grid', '.gallery-item', 'fade-up');
    ScrollAnimations.initStaggeredGroup('.mission-grid', '.mission-item', 'fade-up');
    ScrollAnimations.initStaggeredGroup('.classes-grid', '.class-preview', 'fade-up');
    ScrollAnimations.initStaggeredGroup('.event-container', '.event-card', 'fade-up');
    ScrollAnimations.initStaggeredGroup('.dual-video-container', '.video-item', 'scale-fade');
    ScrollAnimations.initStaggeredGroup('.benefits-list', 'li', 'fade-up');
    ScrollAnimations.initStaggeredGroup('.contact-methods', '.contact-method', 'fade-up');

    // Initialize scroll animations
    ScrollAnimations.init();

    // Initialize parallax
    ParallaxEffect.init();

    // Initialize text reveal
    TextReveal.init();
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAnimations);
  } else {
    initAnimations();
  }

  // Expose modules globally for debugging/extension
  window.SaborAnimations = {
    ScrollAnimations,
    ParallaxEffect,
    TextReveal,
    config: CONFIG,
    reinit: initAnimations
  };

})();
