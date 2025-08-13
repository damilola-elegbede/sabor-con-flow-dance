/**
 * Home Page Specific JavaScript
 * Route-based code splitting for homepage functionality
 */

export default class HomePage {
  constructor() {
    this.modules = new Map();
    this.init();
  }

  async init() {
    // Load only modules needed for home page
    await this.loadCriticalModules();
    this.setupHomePageFeatures();
    this.setupIntersectionObservers();
    
    // Home page enhanced
  }

  async loadCriticalModules() {
    const criticalModules = [
      'lazy-load',
      'mobile-nav'
    ];

    const loadPromises = criticalModules.map(async (moduleName) => {
      try {
        const module = await this.dynamicImport(moduleName);
        this.modules.set(moduleName, module);
      } catch (error) {
        console.warn(`Failed to load ${moduleName}:`, error);
      }
    });

    await Promise.allSettled(loadPromises);
  }

  async dynamicImport(moduleName) {
    const moduleMap = {
      'lazy-load': () => import('../features/lazy-load.js'),
      'mobile-nav': () => import('../features/mobile-nav.js'),
      'gallery': () => import('../features/gallery.js'),
      'analytics': () => import('../features/analytics.js')
    };

    const importFn = moduleMap[moduleName];
    if (!importFn) {
      throw new Error(`Unknown module: ${moduleName}`);
    }

    const module = await importFn();
    return module.default || module;
  }

  setupHomePageFeatures() {
    // Setup hero section enhancements
    this.enhanceHeroSection();
    
    // Setup classes preview section
    this.enhanceClassesSection();
    
    // Setup testimonials
    this.enhanceTestimonialsSection();
    
    // Setup call-to-action buttons
    this.enhanceCTAButtons();
  }

  enhanceHeroSection() {
    const heroSection = document.querySelector('.hero-section');
    if (!heroSection) return;

    // Progressive enhancement for hero video/image
    const heroMedia = heroSection.querySelector('[data-hero-media]');
    if (heroMedia) {
      this.setupHeroMediaLoading(heroMedia);
    }

    // Enhance hero CTA button
    const heroCTA = heroSection.querySelector('.hero-cta');
    if (heroCTA) {
      this.enhanceButton(heroCTA, 'hero_cta_clicked');
    }

    // Add parallax effect for capable devices
    if (this.shouldUseParallax()) {
      this.setupParallaxEffect(heroSection);
    }
  }

  setupHeroMediaLoading(mediaElement) {
    // Prioritize hero media loading
    if (mediaElement.tagName === 'IMG') {
      mediaElement.loading = 'eager';
      mediaElement.fetchPriority = 'high';
    } else if (mediaElement.tagName === 'VIDEO') {
      mediaElement.preload = 'metadata';
    }

    // Add loading state
    mediaElement.classList.add('hero-media-loading');
    
    const handleLoad = () => {
      mediaElement.classList.remove('hero-media-loading');
      mediaElement.classList.add('hero-media-loaded');
    };

    if (mediaElement.complete || mediaElement.readyState >= 2) {
      handleLoad();
    } else {
      mediaElement.addEventListener('load', handleLoad);
      mediaElement.addEventListener('loadeddata', handleLoad);
    }
  }

  shouldUseParallax() {
    // Only use parallax on capable devices
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const isTouch = 'ontouchstart' in window;
    const isSlowConnection = navigator.connection?.effectiveType === 'slow-2g' || 
                            navigator.connection?.effectiveType === '2g';

    return !prefersReducedMotion && !isTouch && !isSlowConnection;
  }

  setupParallaxEffect(heroSection) {
    let ticking = false;
    
    const updateParallax = () => {
      const scrolled = window.pageYOffset;
      const parallaxElement = heroSection.querySelector('.parallax-element');
      
      if (parallaxElement) {
        const yPos = -(scrolled * 0.5);
        parallaxElement.style.transform = `translateY(${yPos}px)`;
      }
      
      ticking = false;
    };

    const scrollHandler = () => {
      if (!ticking) {
        requestAnimationFrame(updateParallax);
        ticking = true;
      }
    };

    window.addEventListener('scroll', scrollHandler, { passive: true });
  }

  enhanceClassesSection() {
    const classesSection = document.querySelector('#classes, .classes-section');
    if (!classesSection) return;

    // Setup intersection observer for animation
    const classCards = classesSection.querySelectorAll('.class-card');
    
    if (classCards.length > 0) {
      this.setupCardAnimations(classCards);
    }

    // Enhance class booking buttons
    const bookingButtons = classesSection.querySelectorAll('.book-class-btn');
    bookingButtons.forEach(button => {
      this.enhanceButton(button, 'class_booking_clicked', {
        class_type: button.dataset.classType || 'unknown'
      });
    });
  }

  setupCardAnimations(cards) {
    if (!('IntersectionObserver' in window)) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.2,
      rootMargin: '50px'
    });

    cards.forEach(card => {
      card.classList.add('animate-ready');
      observer.observe(card);
    });
  }

  enhanceTestimonialsSection() {
    const testimonialsSection = document.querySelector('#testimonials, .testimonials-section');
    if (!testimonialsSection) return;

    // Setup testimonial carousel if exists
    const carousel = testimonialsSection.querySelector('.testimonial-carousel');
    if (carousel) {
      this.setupTestimonialCarousel(carousel);
    }

    // Load testimonial form module when needed
    const addTestimonialBtn = testimonialsSection.querySelector('.add-testimonial-btn');
    if (addTestimonialBtn) {
      this.setupLazyModuleLoad(addTestimonialBtn, 'testimonial-form', 'testimonial_form_opened');
    }
  }

  setupTestimonialCarousel(carousel) {
    const slides = carousel.querySelectorAll('.testimonial-slide');
    const prevBtn = carousel.querySelector('.carousel-prev');
    const nextBtn = carousel.querySelector('.carousel-next');
    
    if (slides.length <= 1) return;

    let currentSlide = 0;
    let autoPlayInterval;

    const showSlide = (index) => {
      slides.forEach((slide, i) => {
        slide.classList.toggle('active', i === index);
      });
      currentSlide = index;
    };

    const nextSlide = () => {
      const next = (currentSlide + 1) % slides.length;
      showSlide(next);
    };

    const prevSlide = () => {
      const prev = (currentSlide - 1 + slides.length) % slides.length;
      showSlide(prev);
    };

    const startAutoPlay = () => {
      autoPlayInterval = setInterval(nextSlide, 5000);
    };

    const stopAutoPlay = () => {
      clearInterval(autoPlayInterval);
    };

    // Event listeners
    nextBtn?.addEventListener('click', () => {
      nextSlide();
      stopAutoPlay();
      setTimeout(startAutoPlay, 10000); // Restart after pause
    });

    prevBtn?.addEventListener('click', () => {
      prevSlide();
      stopAutoPlay();
      setTimeout(startAutoPlay, 10000);
    });

    // Pause on hover
    carousel.addEventListener('mouseenter', stopAutoPlay);
    carousel.addEventListener('mouseleave', startAutoPlay);

    // Initialize
    showSlide(0);
    startAutoPlay();
  }

  enhanceCTAButtons() {
    const ctaButtons = document.querySelectorAll('.cta-button, .btn-primary[data-cta]');
    
    ctaButtons.forEach(button => {
      const ctaType = button.dataset.cta || 'general';
      this.enhanceButton(button, 'cta_clicked', { cta_type: ctaType });
    });
  }

  enhanceButton(button, eventName, additionalData = {}) {
    // Add loading state on click
    button.addEventListener('click', (e) => {
      // Track analytics
      this.trackEvent(eventName, additionalData);
      
      // Add loading state for buttons that submit forms or navigate
      if (button.type === 'submit' || button.dataset.loading === 'true') {
        button.classList.add('loading');
        button.disabled = true;
        
        const originalText = button.textContent;
        button.textContent = 'Loading...';
        
        // Reset after timeout as fallback
        setTimeout(() => {
          button.classList.remove('loading');
          button.disabled = false;
          button.textContent = originalText;
        }, 5000);
      }
    });

    // Add ripple effect for better UX
    this.addRippleEffect(button);
  }

  addRippleEffect(button) {
    button.addEventListener('click', (e) => {
      const ripple = document.createElement('span');
      ripple.classList.add('ripple');
      
      const rect = button.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
      ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
      
      button.appendChild(ripple);
      
      setTimeout(() => {
        ripple.remove();
      }, 600);
    });

    // Add ripple styles
    if (!document.querySelector('#ripple-styles')) {
      const style = document.createElement('style');
      style.id = 'ripple-styles';
      style.textContent = `
        .ripple {
          position: absolute;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.6);
          transform: scale(0);
          animation: ripple-animation 0.6s linear;
          pointer-events: none;
        }
        
        @keyframes ripple-animation {
          to {
            transform: scale(4);
            opacity: 0;
          }
        }
        
        .btn, .cta-button {
          position: relative;
          overflow: hidden;
        }
      `;
      document.head.appendChild(style);
    }
  }

  setupLazyModuleLoad(trigger, moduleName, eventName) {
    const loadModule = async () => {
      try {
        const module = await this.dynamicImport(moduleName);
        this.modules.set(moduleName, module);
        
        if (eventName) {
          this.trackEvent(eventName);
        }
        
        // Initialize module if it has an init method
        if (module && typeof module.init === 'function') {
          module.init();
        }
      } catch (error) {
        console.warn(`Failed to load ${moduleName}:`, error);
      }
    };

    // Load on various interaction types
    trigger.addEventListener('mouseenter', loadModule, { once: true, passive: true });
    trigger.addEventListener('touchstart', loadModule, { once: true, passive: true });
    trigger.addEventListener('focus', loadModule, { once: true, passive: true });
  }

  setupIntersectionObservers() {
    // Setup observers for different sections
    this.observeSection('#about', 'about_section_viewed');
    this.observeSection('#classes', 'classes_section_viewed');
    this.observeSection('#testimonials', 'testimonials_section_viewed');
  }

  observeSection(selector, eventName) {
    const section = document.querySelector(selector);
    if (!section) return;

    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this.trackEvent(eventName);
            observer.unobserve(entry.target);
          }
        });
      }, {
        threshold: 0.5
      });

      observer.observe(section);
    }
  }

  trackEvent(eventName, parameters = {}) {
    if (window.gtag) {
      window.gtag('event', eventName, {
        event_category: 'homepage',
        ...parameters
      });
    }
  }

  // Public API
  static init() {
    return new HomePage();
  }
}

// Auto-initialize if not using module system
if (typeof window !== 'undefined' && !window.moduleSystem) {
  // Only initialize on home page
  if (document.body.classList.contains('page-home') || 
      document.querySelector('.hero-section') ||
      window.location.pathname === '/') {
    document.addEventListener('DOMContentLoaded', () => {
      HomePage.init();
    });
  }
}