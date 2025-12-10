# Phase 4: UI Uplift - Animations and Polish

## Technical Specification Document

**Version:** 1.0
**Last Updated:** 2025-12-10
**Status:** Ready for Implementation

---

## Executive Summary

This specification defines the complete animation system for the Sabor Con Flow dance website.
Phase 4 introduces micro-interactions (PR 4.1) and scroll-based animations (PR 4.2) to create
a premium, polished user experience befitting a dance studio brand.

### Key Deliverables

| PR | Focus | Elements |
|----|-------|----------|
| 4.1 | Micro-Interactions | Ripple effects, hover states, link animations, input focus |
| 4.2 | Scroll Animations | Intersection Observer, staggered entrances, parallax, text reveals |

---

## Current State Analysis

### Existing Animations in styles.css

| Element | Current Animation | Duration | Easing |
|---------|-------------------|----------|--------|
| `.menu-toggle` | transform | 0.3s | ease |
| `.menu-toggle span` | rotate/opacity | 0.4s | default |
| `.nav` | left position | 0.3s | ease |
| `.nav a` | opacity/translateX | 0.3s | ease |
| `.nav a span::after` | width underline | 0.3s | ease |
| `.header-logo-link` | scale | 0.3s | ease |
| `.social-link svg` | scale | 0.3s | ease |
| `.video-item` | translateY/shadow | 0.3s | ease |
| `.video-overlay` | opacity | 0.3s | ease |
| `.gallery-item` | translateY/shadow | 0.3s | ease |
| `.gallery-image` | scale | 0.3s | ease |
| `.gallery-overlay` | translateY | 0.3s | ease |
| `.pasos-animation` | scale/shadow | 0.3s | ease |
| `.btn` | all properties | 0.3s | ease |
| `.class-preview` | translateY | 0.3s | ease |
| `.profile-image` | scale | 0.3s | ease |

### Current JavaScript (layout.ejs)

The only JavaScript currently handles hamburger menu toggle:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('.nav');

    menuToggle.addEventListener('click', function() {
        nav.classList.toggle('active');
        menuToggle.classList.toggle('active');
    });

    document.addEventListener('click', function(event) {
        if (!nav.contains(event.target) && !menuToggle.contains(event.target)) {
            nav.classList.remove('active');
            menuToggle.classList.remove('active');
        }
    });
});
```

### Elements Requiring Scroll Animations

| Page | Elements | Animation Type |
|------|----------|----------------|
| Home | `.tagline-container` | Fade-in-up |
| Home | `.video-item` (x2) | Staggered fade-in-up |
| Home | `.gallery-item` (x3) | Staggered fade-in-up |
| Home | `.cta-section` | Fade-in-up |
| About | `.page-header` | Text reveal |
| About | `.instructor-content` | Fade-in-up |
| About | `.mission-item` (x3) | Staggered fade-in-up |
| About | `.class-preview` (x3) | Staggered fade-in-up |
| About | `.about-cta` | Fade-in-up |
| Events | `.event-card` (dynamic) | Staggered fade-in-up |
| Pricing | `.pricing-table` | Fade-in-up |
| Pricing | `.benefits-list li` | Staggered slide-in |
| Contact | `.contact-section` (x3) | Staggered fade-in-up |

---

## PR 4.1: Micro-Interactions

### Design Tokens

```css
/* ==========================================================================
   ANIMATION DESIGN TOKENS
   ========================================================================== */

:root {
    /* Brand Colors (existing) */
    --color-gold: rgb(191, 170, 101);
    --color-gold-rgb: 191, 170, 101;
    --color-black: #000;
    --color-white: #fff;

    /* Animation Durations */
    --duration-instant: 100ms;
    --duration-fast: 200ms;
    --duration-normal: 300ms;
    --duration-slow: 400ms;
    --duration-slower: 600ms;
    --duration-slowest: 800ms;

    /* Easing Functions */
    --ease-out-quad: cubic-bezier(0.25, 0.46, 0.45, 0.94);
    --ease-out-cubic: cubic-bezier(0.215, 0.61, 0.355, 1);
    --ease-out-quart: cubic-bezier(0.165, 0.84, 0.44, 1);
    --ease-out-expo: cubic-bezier(0.19, 1, 0.22, 1);
    --ease-in-out-cubic: cubic-bezier(0.645, 0.045, 0.355, 1);
    --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);

    /* Ripple Effect */
    --ripple-duration: 600ms;
    --ripple-color: rgba(var(--color-gold-rgb), 0.3);

    /* Shadows */
    --shadow-hover: 0 12px 35px rgba(var(--color-gold-rgb), 0.2);
    --shadow-active: 0 6px 20px rgba(var(--color-gold-rgb), 0.15);
}
```

### 1. Button Ripple Effect

#### CSS Implementation

```css
/* ==========================================================================
   BUTTON RIPPLE EFFECT
   ========================================================================== */

.btn {
    position: relative;
    overflow: hidden;
    isolation: isolate;
}

.btn::before {
    content: '';
    position: absolute;
    top: var(--ripple-y, 50%);
    left: var(--ripple-x, 50%);
    width: 0;
    height: 0;
    border-radius: 50%;
    background: var(--ripple-color);
    transform: translate(-50%, -50%);
    opacity: 0;
    pointer-events: none;
    z-index: -1;
}

.btn.ripple-active::before {
    animation: ripple-expand var(--ripple-duration) var(--ease-out-expo) forwards;
}

@keyframes ripple-expand {
    0% {
        width: 0;
        height: 0;
        opacity: 0.5;
    }
    50% {
        opacity: 0.3;
    }
    100% {
        width: 400%;
        height: 400%;
        opacity: 0;
    }
}

/* Primary button ripple - darker for contrast */
.btn-primary::before {
    background: rgba(0, 0, 0, 0.2);
}

/* Secondary button ripple - gold glow */
.btn-secondary::before {
    background: rgba(var(--color-gold-rgb), 0.3);
}

/* Button press feedback */
.btn:active {
    transform: scale(0.98);
    box-shadow: var(--shadow-active);
}
```

#### JavaScript Implementation

```javascript
/**
 * Ripple Effect Module
 * Creates Material Design-inspired ripple on button click
 */
const RippleEffect = {
    /**
     * Initialize ripple effect on all buttons
     */
    init() {
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => this.attachRipple(button));
    },

    /**
     * Attach ripple event listener to a button
     * @param {HTMLElement} button - Button element
     */
    attachRipple(button) {
        button.addEventListener('click', (e) => this.createRipple(e, button));
        button.addEventListener('mousedown', (e) => this.setRipplePosition(e, button));
    },

    /**
     * Set CSS custom properties for ripple position
     * @param {MouseEvent} e - Mouse event
     * @param {HTMLElement} button - Button element
     */
    setRipplePosition(e, button) {
        const rect = button.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        button.style.setProperty('--ripple-x', `${x}px`);
        button.style.setProperty('--ripple-y', `${y}px`);
    },

    /**
     * Create and animate ripple effect
     * @param {MouseEvent} e - Click event
     * @param {HTMLElement} button - Button element
     */
    createRipple(e, button) {
        // Remove existing ripple class
        button.classList.remove('ripple-active');

        // Force reflow to restart animation
        void button.offsetWidth;

        // Add ripple class
        button.classList.add('ripple-active');

        // Remove class after animation completes
        setTimeout(() => {
            button.classList.remove('ripple-active');
        }, 600);
    }
};
```

### 2. Card Hover Lift with Progressive Shadow

```css
/* ==========================================================================
   CARD HOVER LIFT EFFECT
   ========================================================================== */

/* Base card hover styles - enhanced from existing */
.video-item,
.gallery-item,
.mission-item,
.class-preview,
.event-card,
.cta-section {
    transition:
        transform var(--duration-normal) var(--ease-out-cubic),
        box-shadow var(--duration-normal) var(--ease-out-cubic);
    will-change: transform, box-shadow;
}

/* Progressive shadow levels */
.video-item:hover,
.gallery-item:hover {
    transform: translateY(-8px);
    box-shadow:
        0 4px 8px rgba(0, 0, 0, 0.1),
        0 8px 16px rgba(0, 0, 0, 0.1),
        0 16px 32px rgba(var(--color-gold-rgb), 0.15);
}

.mission-item:hover,
.class-preview:hover {
    transform: translateY(-6px);
    box-shadow:
        0 4px 6px rgba(0, 0, 0, 0.1),
        0 8px 15px rgba(var(--color-gold-rgb), 0.12);
}

.event-card:hover {
    transform: translateY(-4px);
    box-shadow:
        0 4px 12px rgba(0, 0, 0, 0.15),
        0 8px 24px rgba(var(--color-gold-rgb), 0.1);
}

/* Card hover glow effect for premium feel */
.video-item::after,
.gallery-item::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    opacity: 0;
    transition: opacity var(--duration-normal) var(--ease-out-cubic);
    pointer-events: none;
    box-shadow:
        inset 0 0 0 1px rgba(var(--color-gold-rgb), 0.3),
        0 0 20px rgba(var(--color-gold-rgb), 0.1);
}

.video-item:hover::after,
.gallery-item:hover::after {
    opacity: 1;
}
```

### 3. Menu Item Slide-In Animation Refinements

```css
/* ==========================================================================
   ENHANCED MENU ANIMATIONS
   ========================================================================== */

/* Enhanced staggered entrance with spring easing */
.nav a {
    display: block;
    margin: 15px 0;
    color: var(--color-gold);
    text-decoration: none;
    font-size: 1.2rem;
    opacity: 0;
    transform: translateX(-30px) scale(0.95);
    transition:
        opacity var(--duration-slow) var(--ease-out-expo),
        transform var(--duration-slow) var(--ease-spring);
}

.nav.active a {
    opacity: 1;
    transform: translateX(0) scale(1);
}

/* Refined stagger delays with acceleration curve */
.nav a:nth-child(1) { transition-delay: 0.05s; }
.nav a:nth-child(2) { transition-delay: 0.1s; }
.nav a:nth-child(3) { transition-delay: 0.15s; }
.nav a:nth-child(4) { transition-delay: 0.2s; }
.nav a:nth-child(5) { transition-delay: 0.25s; }
.nav a:nth-child(6) { transition-delay: 0.3s; }

/* Exit animation - faster, no stagger */
.nav:not(.active) a {
    transition-delay: 0s;
    transition-duration: var(--duration-fast);
}

/* Menu item hover effect */
.nav a:hover {
    transform: translateX(8px);
}
```

### 4. Link Underline Reveal Animation

```css
/* ==========================================================================
   LINK UNDERLINE REVEAL ANIMATION
   ========================================================================== */

/* Enhanced nav link underline */
.nav a span {
    display: inline-block;
    position: relative;
    padding: 2px 0;
}

.nav a span::after {
    content: '';
    position: absolute;
    width: 0;
    height: 2px;
    bottom: -2px;
    left: 0;
    background: linear-gradient(
        90deg,
        var(--color-gold) 0%,
        rgba(var(--color-gold-rgb), 0.6) 100%
    );
    transition: width var(--duration-normal) var(--ease-out-expo);
    transform-origin: left center;
}

.nav a:hover span::after {
    width: 100%;
}

/* Content link underline animation */
.content-link,
.contact-link,
.instagram-link,
a[href^="http"]:not(.btn):not(.social-link) {
    position: relative;
    text-decoration: none;
    color: var(--color-gold);
}

.content-link::after,
.contact-link::after,
.instagram-link::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    width: 100%;
    height: 1px;
    background: var(--color-gold);
    transform: scaleX(0);
    transform-origin: right center;
    transition: transform var(--duration-normal) var(--ease-out-cubic);
}

.content-link:hover::after,
.contact-link:hover::after,
.instagram-link:hover::after {
    transform: scaleX(1);
    transform-origin: left center;
}

/* Reveal from center variant */
.link-reveal-center::after {
    left: 50%;
    transform: scaleX(0) translateX(-50%);
    transform-origin: center center;
}

.link-reveal-center:hover::after {
    transform: scaleX(1) translateX(-50%);
}
```

### 5. Input Field Focus Animations

```css
/* ==========================================================================
   INPUT FIELD FOCUS ANIMATIONS
   ========================================================================== */

/* Base input styles with animation setup */
.form-input,
input[type="text"],
input[type="email"],
input[type="tel"],
textarea {
    position: relative;
    background: rgba(var(--color-gold-rgb), 0.05);
    border: 1px solid rgba(var(--color-gold-rgb), 0.2);
    border-radius: 8px;
    padding: 12px 16px;
    color: var(--color-white);
    font-size: 1rem;
    transition:
        border-color var(--duration-fast) var(--ease-out-cubic),
        box-shadow var(--duration-fast) var(--ease-out-cubic),
        background var(--duration-fast) var(--ease-out-cubic);
    outline: none;
}

.form-input:hover,
input[type="text"]:hover,
input[type="email"]:hover,
input[type="tel"]:hover,
textarea:hover {
    border-color: rgba(var(--color-gold-rgb), 0.4);
    background: rgba(var(--color-gold-rgb), 0.08);
}

.form-input:focus,
input[type="text"]:focus,
input[type="email"]:focus,
input[type="tel"]:focus,
textarea:focus {
    border-color: var(--color-gold);
    background: rgba(var(--color-gold-rgb), 0.1);
    box-shadow:
        0 0 0 3px rgba(var(--color-gold-rgb), 0.15),
        0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Floating label animation */
.input-group {
    position: relative;
    margin-bottom: 1.5rem;
}

.input-group .form-input {
    padding-top: 20px;
}

.input-group label {
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%);
    color: rgba(var(--color-gold-rgb), 0.6);
    font-size: 1rem;
    pointer-events: none;
    transition:
        top var(--duration-fast) var(--ease-out-cubic),
        font-size var(--duration-fast) var(--ease-out-cubic),
        color var(--duration-fast) var(--ease-out-cubic);
}

.input-group .form-input:focus ~ label,
.input-group .form-input:not(:placeholder-shown) ~ label {
    top: 8px;
    font-size: 0.75rem;
    color: var(--color-gold);
}

/* Input underline animation variant */
.input-underline {
    border: none;
    border-bottom: 2px solid rgba(var(--color-gold-rgb), 0.3);
    border-radius: 0;
    background: transparent;
    padding: 12px 0;
}

.input-underline::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: var(--color-gold);
    transform: scaleX(0);
    transition: transform var(--duration-normal) var(--ease-out-expo);
}

.input-underline:focus::after {
    transform: scaleX(1);
}
```

### 6. Social Icon Hover Enhancement

```css
/* ==========================================================================
   SOCIAL ICON HOVER ENHANCEMENT
   ========================================================================== */

.social-link {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 8px;
    border-radius: 50%;
    transition:
        transform var(--duration-normal) var(--ease-spring),
        background var(--duration-normal) var(--ease-out-cubic);
}

.social-link::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background: rgba(var(--color-gold-rgb), 0.1);
    opacity: 0;
    transform: scale(0.8);
    transition:
        opacity var(--duration-normal) var(--ease-out-cubic),
        transform var(--duration-normal) var(--ease-spring);
}

.social-link:hover::before {
    opacity: 1;
    transform: scale(1);
}

.social-link:hover {
    transform: translateY(-3px);
}

.social-link svg {
    transition: transform var(--duration-normal) var(--ease-spring);
    position: relative;
    z-index: 1;
}

.social-link:hover svg {
    transform: scale(1.15) rotate(5deg);
}

.social-link:active svg {
    transform: scale(0.95);
}
```

---

## PR 4.2: Scroll Animations

### Intersection Observer Configuration

```javascript
/**
 * Scroll Animation Module
 * Uses Intersection Observer for performant scroll-triggered animations
 */
const ScrollAnimations = {
    /**
     * Default configuration
     */
    config: {
        root: null, // viewport
        rootMargin: '0px 0px -10% 0px', // Trigger slightly before element enters
        threshold: [0, 0.1, 0.25], // Multiple thresholds for progressive reveal

        // Animation defaults
        defaultDuration: 600,
        defaultDelay: 0,
        defaultEasing: 'cubic-bezier(0.215, 0.61, 0.355, 1)', // ease-out-cubic

        // Stagger configuration
        staggerDelay: 100, // ms between staggered items
        maxStaggerDelay: 500 // Cap stagger delay
    },

    /**
     * Animation presets
     */
    presets: {
        'fade-up': {
            initial: {
                opacity: '0',
                transform: 'translateY(30px)'
            },
            animate: {
                opacity: '1',
                transform: 'translateY(0)'
            }
        },
        'fade-down': {
            initial: {
                opacity: '0',
                transform: 'translateY(-30px)'
            },
            animate: {
                opacity: '1',
                transform: 'translateY(0)'
            }
        },
        'fade-left': {
            initial: {
                opacity: '0',
                transform: 'translateX(30px)'
            },
            animate: {
                opacity: '1',
                transform: 'translateX(0)'
            }
        },
        'fade-right': {
            initial: {
                opacity: '0',
                transform: 'translateX(-30px)'
            },
            animate: {
                opacity: '1',
                transform: 'translateX(0)'
            }
        },
        'scale-up': {
            initial: {
                opacity: '0',
                transform: 'scale(0.9)'
            },
            animate: {
                opacity: '1',
                transform: 'scale(1)'
            }
        },
        'scale-fade': {
            initial: {
                opacity: '0',
                transform: 'scale(0.95) translateY(20px)'
            },
            animate: {
                opacity: '1',
                transform: 'scale(1) translateY(0)'
            }
        },
        'slide-up': {
            initial: {
                opacity: '0',
                transform: 'translateY(50px)',
                clipPath: 'inset(100% 0 0 0)'
            },
            animate: {
                opacity: '1',
                transform: 'translateY(0)',
                clipPath: 'inset(0 0 0 0)'
            }
        },
        'text-reveal': {
            initial: {
                opacity: '0',
                transform: 'translateY(100%)',
                clipPath: 'inset(0 0 100% 0)'
            },
            animate: {
                opacity: '1',
                transform: 'translateY(0)',
                clipPath: 'inset(0 0 0 0)'
            }
        }
    },

    /**
     * Initialize scroll animations
     */
    init() {
        // Check for reduced motion preference
        if (this.prefersReducedMotion()) {
            this.showAllElements();
            return;
        }

        // Create observer
        this.observer = new IntersectionObserver(
            this.handleIntersection.bind(this),
            {
                root: this.config.root,
                rootMargin: this.config.rootMargin,
                threshold: this.config.threshold
            }
        );

        // Initialize elements
        this.initializeElements();

        // Observe elements
        this.observeElements();
    },

    /**
     * Check if user prefers reduced motion
     * @returns {boolean}
     */
    prefersReducedMotion() {
        return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    },

    /**
     * Show all elements immediately (for reduced motion)
     */
    showAllElements() {
        const elements = document.querySelectorAll('[data-animate]');
        elements.forEach(el => {
            el.style.opacity = '1';
            el.style.transform = 'none';
            el.classList.add('animate-complete');
        });
    },

    /**
     * Initialize elements with starting styles
     */
    initializeElements() {
        const elements = document.querySelectorAll('[data-animate]');

        elements.forEach(el => {
            const preset = el.dataset.animate || 'fade-up';
            const animation = this.presets[preset];

            if (!animation) return;

            // Apply initial styles
            Object.assign(el.style, animation.initial);

            // Set transition properties
            const duration = el.dataset.duration || this.config.defaultDuration;
            const delay = el.dataset.delay || this.config.defaultDelay;
            const easing = el.dataset.easing || this.config.defaultEasing;

            el.style.transition = `
                opacity ${duration}ms ${easing} ${delay}ms,
                transform ${duration}ms ${easing} ${delay}ms,
                clip-path ${duration}ms ${easing} ${delay}ms
            `;

            // Add will-change for GPU acceleration
            el.style.willChange = 'opacity, transform';
        });
    },

    /**
     * Observe all animated elements
     */
    observeElements() {
        const elements = document.querySelectorAll('[data-animate]');
        elements.forEach(el => this.observer.observe(el));
    },

    /**
     * Handle intersection callback
     * @param {IntersectionObserverEntry[]} entries
     */
    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting && entry.intersectionRatio >= 0.1) {
                this.animateElement(entry.target);
                this.observer.unobserve(entry.target);
            }
        });
    },

    /**
     * Animate a single element
     * @param {HTMLElement} el
     */
    animateElement(el) {
        const preset = el.dataset.animate || 'fade-up';
        const animation = this.presets[preset];

        if (!animation) return;

        // Apply animate styles
        requestAnimationFrame(() => {
            Object.assign(el.style, animation.animate);
            el.classList.add('animate-in');

            // Clean up will-change after animation
            const duration = parseInt(el.dataset.duration || this.config.defaultDuration);
            const delay = parseInt(el.dataset.delay || this.config.defaultDelay);

            setTimeout(() => {
                el.style.willChange = 'auto';
                el.classList.add('animate-complete');
            }, duration + delay + 100);
        });
    },

    /**
     * Initialize staggered animations for a container
     * @param {string} containerSelector
     * @param {string} childSelector
     * @param {string} preset
     */
    initStaggeredGroup(containerSelector, childSelector, preset = 'fade-up') {
        const containers = document.querySelectorAll(containerSelector);

        containers.forEach(container => {
            const children = container.querySelectorAll(childSelector);

            children.forEach((child, index) => {
                child.dataset.animate = preset;
                child.dataset.delay = Math.min(
                    index * this.config.staggerDelay,
                    this.config.maxStaggerDelay
                );
            });
        });
    },

    /**
     * Destroy observer and clean up
     */
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
    }
};
```

### CSS for Scroll Animations

```css
/* ==========================================================================
   SCROLL ANIMATION BASE CLASSES
   ========================================================================== */

/* Base state for all animated elements */
[data-animate] {
    opacity: 0;
}

/* Animation complete state */
.animate-complete {
    opacity: 1 !important;
    transform: none !important;
}

/* Stagger animation classes for CSS-only fallback */
.stagger-children > * {
    opacity: 0;
    transform: translateY(30px);
    transition:
        opacity var(--duration-slower) var(--ease-out-cubic),
        transform var(--duration-slower) var(--ease-out-cubic);
}

.stagger-children.in-view > * {
    opacity: 1;
    transform: translateY(0);
}

.stagger-children > *:nth-child(1) { transition-delay: 0ms; }
.stagger-children > *:nth-child(2) { transition-delay: 100ms; }
.stagger-children > *:nth-child(3) { transition-delay: 200ms; }
.stagger-children > *:nth-child(4) { transition-delay: 300ms; }
.stagger-children > *:nth-child(5) { transition-delay: 400ms; }
.stagger-children > *:nth-child(6) { transition-delay: 500ms; }

/* ==========================================================================
   KEYFRAME ANIMATIONS
   ========================================================================== */

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInLeft {
    from {
        opacity: 0;
        transform: translateX(30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes fadeInRight {
    from {
        opacity: 0;
        transform: translateX(-30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes scaleIn {
    from {
        opacity: 0;
        transform: scale(0.9);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes slideReveal {
    from {
        opacity: 0;
        transform: translateY(50px);
        clip-path: inset(100% 0 0 0);
    }
    to {
        opacity: 1;
        transform: translateY(0);
        clip-path: inset(0 0 0 0);
    }
}

@keyframes textReveal {
    from {
        opacity: 0;
        transform: translateY(100%);
        clip-path: inset(0 0 100% 0);
    }
    to {
        opacity: 1;
        transform: translateY(0);
        clip-path: inset(0 0 0 0);
    }
}

@keyframes pulseGlow {
    0%, 100% {
        box-shadow: 0 0 20px rgba(var(--color-gold-rgb), 0.2);
    }
    50% {
        box-shadow: 0 0 40px rgba(var(--color-gold-rgb), 0.4);
    }
}

/* ==========================================================================
   ANIMATION UTILITY CLASSES
   ========================================================================== */

.animate-fade-up {
    animation: fadeInUp var(--duration-slower) var(--ease-out-cubic) forwards;
}

.animate-fade-down {
    animation: fadeInDown var(--duration-slower) var(--ease-out-cubic) forwards;
}

.animate-fade-left {
    animation: fadeInLeft var(--duration-slower) var(--ease-out-cubic) forwards;
}

.animate-fade-right {
    animation: fadeInRight var(--duration-slower) var(--ease-out-cubic) forwards;
}

.animate-scale-in {
    animation: scaleIn var(--duration-slower) var(--ease-out-cubic) forwards;
}

.animate-slide-reveal {
    animation: slideReveal var(--duration-slowest) var(--ease-out-expo) forwards;
}

.animate-text-reveal {
    animation: textReveal var(--duration-slowest) var(--ease-out-expo) forwards;
}

/* Animation delay utilities */
.delay-100 { animation-delay: 100ms; }
.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }
.delay-400 { animation-delay: 400ms; }
.delay-500 { animation-delay: 500ms; }
.delay-600 { animation-delay: 600ms; }
.delay-700 { animation-delay: 700ms; }
.delay-800 { animation-delay: 800ms; }

/* Animation duration utilities */
.duration-fast { animation-duration: var(--duration-fast); }
.duration-normal { animation-duration: var(--duration-normal); }
.duration-slow { animation-duration: var(--duration-slow); }
.duration-slower { animation-duration: var(--duration-slower); }
.duration-slowest { animation-duration: var(--duration-slowest); }
```

### Parallax Effect Implementation

```javascript
/**
 * Parallax Effect Module
 * Subtle parallax for hero video/images
 */
const ParallaxEffect = {
    /**
     * Configuration
     */
    config: {
        factor: 0.15, // Parallax intensity (0-1)
        smoothing: 0.1, // Scroll smoothing factor
        maxOffset: 100 // Maximum pixel offset
    },

    /**
     * State
     */
    state: {
        scrollY: 0,
        targetY: 0,
        rafId: null,
        isRunning: false
    },

    /**
     * Initialize parallax
     */
    init() {
        // Check for reduced motion
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            return;
        }

        // Get parallax elements
        this.elements = document.querySelectorAll('[data-parallax]');

        if (this.elements.length === 0) return;

        // Bind events
        this.handleScroll = this.handleScroll.bind(this);
        this.animate = this.animate.bind(this);

        // Add scroll listener
        window.addEventListener('scroll', this.handleScroll, { passive: true });

        // Start animation loop
        this.startLoop();
    },

    /**
     * Handle scroll event
     */
    handleScroll() {
        this.state.targetY = window.scrollY;
    },

    /**
     * Start animation loop
     */
    startLoop() {
        if (this.state.isRunning) return;
        this.state.isRunning = true;
        this.animate();
    },

    /**
     * Animation loop
     */
    animate() {
        // Smooth scroll interpolation
        this.state.scrollY += (this.state.targetY - this.state.scrollY) * this.config.smoothing;

        // Apply parallax to elements
        this.elements.forEach(el => {
            const factor = parseFloat(el.dataset.parallaxFactor) || this.config.factor;
            const direction = el.dataset.parallaxDirection || 'up';

            // Calculate offset
            let offset = this.state.scrollY * factor;
            offset = Math.min(Math.max(offset, -this.config.maxOffset), this.config.maxOffset);

            // Apply transform based on direction
            const transform = direction === 'up'
                ? `translateY(${offset}px)`
                : `translateY(${-offset}px)`;

            el.style.transform = transform;
        });

        // Continue loop
        this.state.rafId = requestAnimationFrame(this.animate);
    },

    /**
     * Stop animation loop
     */
    stopLoop() {
        if (this.state.rafId) {
            cancelAnimationFrame(this.state.rafId);
            this.state.rafId = null;
        }
        this.state.isRunning = false;
    },

    /**
     * Destroy parallax
     */
    destroy() {
        this.stopLoop();
        window.removeEventListener('scroll', this.handleScroll);

        this.elements.forEach(el => {
            el.style.transform = '';
        });
    }
};

/* CSS for parallax containers */
```

```css
/* ==========================================================================
   PARALLAX EFFECT STYLES
   ========================================================================== */

[data-parallax] {
    will-change: transform;
}

/* Hero section parallax container */
.hero-parallax {
    position: relative;
    overflow: hidden;
}

.hero-parallax .video-item {
    transform: translateZ(0); /* Force GPU layer */
}

/* Parallax background layer */
.parallax-bg {
    position: absolute;
    top: -20%;
    left: 0;
    width: 100%;
    height: 140%;
    object-fit: cover;
    will-change: transform;
}
```

### Text Reveal Animation

```javascript
/**
 * Text Reveal Animation Module
 * Animated text reveal on page load/scroll
 */
const TextReveal = {
    /**
     * Initialize text reveal animations
     */
    init() {
        // Check for reduced motion
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.showAllText();
            return;
        }

        this.splitTextElements();
        this.observeElements();
    },

    /**
     * Show all text immediately (reduced motion)
     */
    showAllText() {
        const elements = document.querySelectorAll('[data-text-reveal]');
        elements.forEach(el => {
            el.style.opacity = '1';
            el.classList.add('text-revealed');
        });
    },

    /**
     * Split text into animatable spans
     */
    splitTextElements() {
        const elements = document.querySelectorAll('[data-text-reveal]');

        elements.forEach(el => {
            const text = el.textContent;
            const type = el.dataset.textReveal || 'chars'; // 'chars', 'words', 'lines'

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

    /**
     * Split text by characters
     */
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

    /**
     * Split text by words
     */
    splitByWords(el, text) {
        const words = text.split(' ');
        words.forEach((word, i) => {
            const span = document.createElement('span');
            span.className = 'reveal-word';
            span.textContent = word;
            span.style.transitionDelay = `${i * 80}ms`;
            span.setAttribute('aria-hidden', 'true');
            el.appendChild(span);

            // Add space between words
            if (i < words.length - 1) {
                el.appendChild(document.createTextNode(' '));
            }
        });
    },

    /**
     * Wrap entire line for reveal
     */
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

    /**
     * Observe elements for viewport entry
     */
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
```

```css
/* ==========================================================================
   TEXT REVEAL ANIMATION STYLES
   ========================================================================== */

[data-text-reveal] {
    overflow: hidden;
}

/* Character reveal */
.reveal-char {
    display: inline-block;
    opacity: 0;
    transform: translateY(100%);
    transition:
        opacity var(--duration-slow) var(--ease-out-cubic),
        transform var(--duration-slow) var(--ease-out-cubic);
}

.text-revealed .reveal-char {
    opacity: 1;
    transform: translateY(0);
}

/* Word reveal */
.reveal-word {
    display: inline-block;
    opacity: 0;
    transform: translateY(20px);
    transition:
        opacity var(--duration-slow) var(--ease-out-cubic),
        transform var(--duration-slow) var(--ease-out-cubic);
}

.text-revealed .reveal-word {
    opacity: 1;
    transform: translateY(0);
}

/* Line reveal */
.reveal-line {
    display: block;
    overflow: hidden;
}

.reveal-line-inner {
    display: block;
    transform: translateY(100%);
    transition: transform var(--duration-slower) var(--ease-out-expo);
}

.text-revealed .reveal-line-inner {
    transform: translateY(0);
}

/* Title reveal animation for page headers */
.page-title[data-text-reveal="lines"] .reveal-line-inner {
    transition-duration: var(--duration-slowest);
}
```

---

## Complete animations.js File

```javascript
/**
 * Sabor Con Flow - Animation System
 * Version: 1.0.0
 *
 * This module provides:
 * - Ripple effects on buttons
 * - Scroll-triggered animations via Intersection Observer
 * - Parallax effects
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
            maxStaggerDelay: 500,
            rippleDuration: 600
        },

        // Easing functions
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
       RIPPLE EFFECT MODULE
       ========================================================================== */

    const RippleEffect = {
        init() {
            const buttons = document.querySelectorAll('.btn');
            buttons.forEach(button => this.attachRipple(button));
        },

        attachRipple(button) {
            button.addEventListener('click', (e) => this.createRipple(e, button));
            button.addEventListener('mousedown', (e) => this.setRipplePosition(e, button));
        },

        setRipplePosition(e, button) {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            button.style.setProperty('--ripple-x', `${x}px`);
            button.style.setProperty('--ripple-y', `${y}px`);
        },

        createRipple(e, button) {
            button.classList.remove('ripple-active');
            void button.offsetWidth; // Force reflow
            button.classList.add('ripple-active');

            setTimeout(() => {
                button.classList.remove('ripple-active');
            }, CONFIG.timing.rippleDuration);
        }
    };

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
                    child.dataset.animate = preset;
                    child.dataset.delay = Math.min(
                        index * CONFIG.timing.staggerDelay,
                        CONFIG.timing.maxStaggerDelay
                    );
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
        // Initialize ripple effects
        RippleEffect.init();

        // Setup staggered groups before initializing scroll animations
        ScrollAnimations.initStaggeredGroup('.gallery-grid', '.gallery-item', 'fade-up');
        ScrollAnimations.initStaggeredGroup('.mission-grid', '.mission-item', 'fade-up');
        ScrollAnimations.initStaggeredGroup('.classes-grid', '.class-preview', 'fade-up');
        ScrollAnimations.initStaggeredGroup('.event-container', '.event-card', 'fade-up');
        ScrollAnimations.initStaggeredGroup('.dual-video-container', '.video-item', 'scale-fade');

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
        RippleEffect,
        ScrollAnimations,
        ParallaxEffect,
        TextReveal,
        config: CONFIG
    };

})();
```

---

## HTML Implementation Guide

### Data Attributes Reference

| Attribute | Values | Description |
|-----------|--------|-------------|
| `data-animate` | `fade-up`, `fade-down`, `fade-left`, `fade-right`, `scale-up`, `scale-fade` | Animation preset |
| `data-duration` | Number (ms) | Animation duration |
| `data-delay` | Number (ms) | Animation delay |
| `data-easing` | CSS easing | Custom easing function |
| `data-parallax` | Boolean | Enable parallax |
| `data-parallax-factor` | Number (0-1) | Parallax intensity |
| `data-parallax-direction` | `up`, `down` | Parallax direction |
| `data-text-reveal` | `chars`, `words`, `lines` | Text reveal type |

### Home Page (home.ejs) Implementation

```html
<div class="container">
    <!-- Tagline Section -->
    <div class="tagline-container" data-animate="fade-up">
        <h2 class="tagline" data-text-reveal="words">
            Sabor in every step, flow in every move
        </h2>
    </div>

    <!-- Side-by-Side Videos Section -->
    <div class="dual-video-container">
        <div class="video-item" data-animate="scale-fade" data-parallax data-parallax-factor="0.1">
            <video class="side-video" autoplay muted loop playsinline>
                <source src="/images/hero-dance-video.mov" type="video/mp4">
            </video>
            <div class="video-overlay">
                <h3>Experience Cuban Dance</h3>
                <p>Boulder's Premier Studio</p>
            </div>
        </div>
        <div class="video-item" data-animate="scale-fade" data-delay="150"
             data-parallax data-parallax-factor="0.1">
            <video class="side-video" autoplay muted loop playsinline>
                <source src="/images/second-dance-video.mov" type="video/mp4">
            </video>
            <div class="video-overlay">
                <h3>Perfect Your Footwork</h3>
                <p>Master Cuban Techniques</p>
            </div>
        </div>
    </div>

    <!-- Dance Gallery Section -->
    <div class="dance-gallery">
        <div class="gallery-grid">
            <div class="gallery-item" data-animate="fade-up">
                <img src="/images/dance-1.jpeg" alt="Technical Precision" class="gallery-image">
                <div class="gallery-overlay">
                    <h3>Technical Precision Focus</h3>
                    <p>Systematic approach to Casino & Afro-Cuban movement</p>
                </div>
            </div>
            <div class="gallery-item" data-animate="fade-up" data-delay="100">
                <img src="/images/dance-3.jpeg" alt="Music Integration" class="gallery-image">
                <div class="gallery-overlay">
                    <h3>Music & Movement Integration</h3>
                    <p>Master salsa-rumba transitions, clave timing</p>
                </div>
            </div>
            <div class="gallery-item" data-animate="fade-up" data-delay="200">
                <img src="/images/dance-4.jpeg" alt="Cuban Dance Training" class="gallery-image">
                <div class="gallery-overlay">
                    <h3>Cuban Dance Training</h3>
                    <p>Fundamentals to advanced flow</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Call to Action -->
    <div class="cta-section" data-animate="fade-up" data-duration="800">
        <h2 data-text-reveal="words">Ready to Dance?</h2>
        <p>Join our classes and discover the joy of Cuban salsa</p>
        <div class="cta-buttons">
            <a href="/events" class="btn btn-primary">View Classes</a>
            <a href="/private-lessons" class="btn btn-secondary">Book Private Lesson</a>
        </div>
    </div>
</div>
```

### About Page (about.ejs) Implementation

```html
<div class="container">
    <div class="about-page">
        <!-- Page Title -->
        <div class="page-header" data-animate="fade-down">
            <h1 class="page-title" data-text-reveal="lines">About Sabor Con Flow</h1>
            <p class="page-subtitle" data-text-reveal="words">
                Where Technical Precision Meets Cuban Soul
            </p>
        </div>

        <!-- Instructor Section -->
        <div class="instructor-section">
            <div class="instructor-content">
                <div class="instructor-photo" data-animate="fade-right" data-duration="700">
                    <img src="/images/sabor-con-flow-logo.png" alt="Instructor" class="profile-image">
                </div>
                <div class="instructor-info" data-animate="fade-left" data-delay="200">
                    <h2 class="instructor-title">Meet Your Instructor</h2>
                    <div class="instructor-bio">
                        <!-- Content -->
                    </div>
                </div>
            </div>
        </div>

        <!-- Mission Section -->
        <div class="mission-section">
            <h2 class="section-title" data-animate="fade-up" data-text-reveal="words">
                Our Mission
            </h2>
            <div class="mission-grid">
                <div class="mission-item" data-animate="fade-up">
                    <h3>Technical Foundation</h3>
                    <p>Build systematic technique through structured footwork drills.</p>
                </div>
                <div class="mission-item" data-animate="fade-up" data-delay="100">
                    <h3>Cultural Authenticity</h3>
                    <p>Honor the rich tradition of Cuban dance.</p>
                </div>
                <div class="mission-item" data-animate="fade-up" data-delay="200">
                    <h3>Congress Preparation</h3>
                    <p>Equip dancers with skills for Cuban salsa congresses.</p>
                </div>
            </div>
        </div>

        <!-- Classes Overview -->
        <div class="classes-overview">
            <h2 class="section-title" data-animate="fade-up">What We Offer</h2>
            <div class="classes-grid">
                <div class="class-preview" data-animate="fade-up">
                    <h3>Pasos Basicos</h3>
                    <p>Master fundamental Cuban salsa footwork.</p>
                </div>
                <div class="class-preview" data-animate="fade-up" data-delay="100">
                    <h3>Casino Royale</h3>
                    <p>Develop flow and connection in casino dancing.</p>
                </div>
                <div class="class-preview" data-animate="fade-up" data-delay="200">
                    <h3>SCF Choreo Team</h3>
                    <p>Advanced choreography with performance artistry.</p>
                </div>
            </div>
        </div>

        <!-- Call to Action -->
        <div class="about-cta" data-animate="scale-fade" data-duration="800">
            <h2>Ready to Start Your Cuban Dance Journey?</h2>
            <p>Join our Boulder community and discover sabor and flow.</p>
            <div class="cta-buttons">
                <a href="/events" class="btn btn-primary">View Class Schedule</a>
                <a href="/private-lessons" class="btn btn-secondary">Book Private Lesson</a>
            </div>
        </div>
    </div>
</div>
```

---

## Performance Considerations

### GPU-Accelerated Properties

Only animate these properties for 60fps performance:

| Property | GPU Accelerated | Notes |
|----------|-----------------|-------|
| `transform` | Yes | Use for all movement |
| `opacity` | Yes | Use for fading |
| `filter` | Yes | Use sparingly |
| `clip-path` | Partial | Triggers paint but not layout |
| `left/top/right/bottom` | No | Avoid - causes layout |
| `width/height` | No | Avoid - causes layout |
| `margin/padding` | No | Avoid - causes layout |

### Animation Frame Budget

```text
Target: 60fps = 16.67ms per frame

Budget breakdown:
- JavaScript execution: < 4ms
- Style recalculation: < 2ms
- Layout: < 2ms (ideally 0)
- Paint: < 4ms
- Composite: < 2ms
- Buffer: ~2ms

Total available: ~14ms for smooth animations
```

### Optimization Techniques

```javascript
// 1. Use will-change judiciously
element.style.willChange = 'transform, opacity';
// Remove after animation
setTimeout(() => element.style.willChange = 'auto', duration);

// 2. Force GPU layer with transform
element.style.transform = 'translateZ(0)';

// 3. Batch DOM reads/writes
const height = element.offsetHeight; // Read
requestAnimationFrame(() => {
    element.style.transform = `translateY(${height}px)`; // Write
});

// 4. Use passive event listeners for scroll
window.addEventListener('scroll', handler, { passive: true });

// 5. Debounce resize handlers
window.addEventListener('resize', debounce(handler, 150));
```

### Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }

    [data-animate] {
        opacity: 1 !important;
        transform: none !important;
    }

    [data-parallax] {
        transform: none !important;
    }
}
```

---

## Timing and Easing Reference

### Duration Guidelines

| Animation Type | Duration | Use Case |
|----------------|----------|----------|
| Instant | 100ms | Micro-feedback (button press) |
| Fast | 200ms | Quick state changes |
| Normal | 300ms | Standard transitions |
| Slow | 400ms | Complex transforms |
| Slower | 600ms | Scroll reveals |
| Slowest | 800ms | Page load animations |

### Easing Function Reference

| Name | Cubic Bezier | Use Case |
|------|--------------|----------|
| ease-out-quad | `(0.25, 0.46, 0.45, 0.94)` | Basic deceleration |
| ease-out-cubic | `(0.215, 0.61, 0.355, 1)` | Smooth deceleration |
| ease-out-quart | `(0.165, 0.84, 0.44, 1)` | Strong deceleration |
| ease-out-expo | `(0.19, 1, 0.22, 1)` | Dramatic deceleration |
| ease-in-out-cubic | `(0.645, 0.045, 0.355, 1)` | Symmetric acceleration |
| spring | `(0.175, 0.885, 0.32, 1.275)` | Overshoot bounce |

### Stagger Delay Patterns

| Grid Size | Delay Pattern | Max Delay |
|-----------|---------------|-----------|
| 3 items | 0, 100ms, 200ms | 200ms |
| 4 items | 0, 100ms, 200ms, 300ms | 300ms |
| 6 items | 0, 80ms, 160ms, 240ms, 320ms, 400ms | 400ms |
| 9+ items | Cap at 500ms total | 500ms |

---

## File Structure

```text
public/
  css/
    styles.css          # Existing styles (to be extended)
    animations.css      # New animation-specific styles
  js/
    animations.js       # New animation JavaScript module

views/
  layout.ejs           # Add script tag for animations.js
  home.ejs             # Add data attributes
  about.ejs            # Add data attributes
  events.ejs           # Add data attributes
  pricing.ejs          # Add data attributes
  contact.ejs          # Add data attributes
  private-lessons.ejs  # Add data attributes
```

---

## Testing Checklist

### PR 4.1 Micro-Interactions

- [ ] Button ripple effect works on all `.btn` elements
- [ ] Ripple originates from click position
- [ ] Card hover lift animates smoothly
- [ ] Progressive shadow appears on hover
- [ ] Menu slide animations use spring easing
- [ ] Menu exit animation is faster than entrance
- [ ] Link underline reveals from left to right
- [ ] Social icons scale and rotate on hover
- [ ] All animations respect reduced motion preference

### PR 4.2 Scroll Animations

- [ ] Elements fade in when scrolling into view
- [ ] Staggered animations work for grids
- [ ] Parallax effect is subtle on hero videos
- [ ] Text reveal works for page titles
- [ ] No jank or stutter during scroll
- [ ] Animations only trigger once per element
- [ ] Mobile performance is acceptable
- [ ] Intersection Observer fallback works
- [ ] Reduced motion shows elements immediately

### Performance Metrics

- [ ] Lighthouse Performance score > 90
- [ ] First Contentful Paint < 1.5s
- [ ] Largest Contentful Paint < 2.5s
- [ ] Time to Interactive < 3.5s
- [ ] No layout shift from animations (CLS < 0.1)
- [ ] Animation frame rate > 55fps average

---

## Implementation Order

### PR 4.1: Micro-Interactions (Priority Order)

1. Add CSS design tokens to `styles.css`
2. Implement button ripple CSS and JavaScript
3. Enhance card hover states
4. Refine menu animations
5. Add link underline animations
6. Add social icon hover effects
7. Test across all pages

### PR 4.2: Scroll Animations (Priority Order)

1. Create `animations.js` with full module
2. Create `animations.css` with all animation styles
3. Add script tag to `layout.ejs`
4. Add data attributes to `home.ejs`
5. Add data attributes to `about.ejs`
6. Add data attributes to remaining pages
7. Implement parallax on hero videos
8. Add text reveal to page titles
9. Performance testing and optimization

---

## Appendix: Complete CSS Variables

```css
:root {
    /* Brand Colors */
    --color-gold: rgb(191, 170, 101);
    --color-gold-rgb: 191, 170, 101;
    --color-black: #000;
    --color-white: #fff;

    /* Animation Durations */
    --duration-instant: 100ms;
    --duration-fast: 200ms;
    --duration-normal: 300ms;
    --duration-slow: 400ms;
    --duration-slower: 600ms;
    --duration-slowest: 800ms;

    /* Easing Functions */
    --ease-out-quad: cubic-bezier(0.25, 0.46, 0.45, 0.94);
    --ease-out-cubic: cubic-bezier(0.215, 0.61, 0.355, 1);
    --ease-out-quart: cubic-bezier(0.165, 0.84, 0.44, 1);
    --ease-out-expo: cubic-bezier(0.19, 1, 0.22, 1);
    --ease-in-out-cubic: cubic-bezier(0.645, 0.045, 0.355, 1);
    --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);

    /* Ripple Effect */
    --ripple-duration: 600ms;
    --ripple-color: rgba(var(--color-gold-rgb), 0.3);

    /* Shadows */
    --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.15);
    --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.2);
    --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.25);
    --shadow-gold: 0 8px 24px rgba(var(--color-gold-rgb), 0.15);
    --shadow-gold-lg: 0 16px 48px rgba(var(--color-gold-rgb), 0.2);

    /* Animation Distances */
    --animate-distance-sm: 20px;
    --animate-distance-md: 30px;
    --animate-distance-lg: 50px;

    /* Parallax */
    --parallax-factor: 0.15;
    --parallax-max-offset: 100px;

    /* Stagger */
    --stagger-delay: 100ms;
    --stagger-max: 500ms;
}
```

---

**Document End**

*This specification provides complete, copy-paste ready code for implementing Phase 4 animations.
All code respects accessibility preferences and follows performance best practices.*
