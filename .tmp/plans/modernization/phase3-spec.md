# Phase 3: UI Uplift - Components Technical Specification

## Document Metadata

| Property | Value |
|----------|-------|
| Phase | 3 of 5 |
| Status | Draft |
| Author | Principal Architect |
| Created | 2024-12-10 |
| Target | Post-Phase 2 CSS Modularization |

## Executive Summary

Phase 3 modernizes the Sabor Con Flow Dance website's interactive components through three
focused PRs: navigation enhancements, card and button system upgrades, and gallery/media
improvements. This specification provides production-ready code implementing glassmorphism
effects, accessibility improvements, and modern CSS features with appropriate fallbacks.

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [PR 3.1: Navigation Enhancements](#pr-31-navigation-enhancements)
3. [PR 3.2: Card and Button System](#pr-32-card-and-button-system)
4. [PR 3.3: Gallery and Media Enhancements](#pr-33-gallery-and-media-enhancements)
5. [Browser Support Matrix](#browser-support-matrix)
6. [Accessibility Compliance](#accessibility-compliance)
7. [Testing Requirements](#testing-requirements)
8. [Implementation Checklist](#implementation-checklist)

---

## Current State Analysis

### Navigation Structure (layout.ejs)

```html
<!-- Current markup - lines 24-41 -->
<header class="header">
    <button class="menu-toggle" aria-label="Toggle navigation">
        <span></span>
        <span></span>
        <span></span>
    </button>
    <a href="/" class="header-logo-link">
        <img src="/images/sabor-con-flow-logo.png" alt="Sabor Con Flow" class="header-logo">
    </a>
    <nav class="nav">
        <a href="/"><span>Home</span></a>
        <a href="/about"><span>About</span></a>
        <a href="/events"><span>Events</span></a>
        <a href="/pricing"><span>Pricing</span></a>
        <a href="/private-lessons"><span>Private Lessons</span></a>
        <a href="/contact"><span>Contact</span></a>
    </nav>
</header>
```

### Current Navigation CSS

- Fixed position hamburger menu at `top: 20px; left: 20px`
- Nav slides in from left (`left: -250px` to `left: 0`)
- Links animate with staggered `transition-delay`
- Gold underline on hover via `::after` pseudo-element
- No visible close button
- No keyboard navigation support
- No backdrop blur effect

### Current Card Patterns

**Event Cards** (events.ejs):

- Simple black background with gold top border
- No elevation or shadow effects
- Basic pricing section with `rgba(191, 170, 101, 0.1)` background

**Mission/Class Cards** (about.ejs):

- `.mission-item`: Gold tinted background, 12px border-radius
- `.class-preview`: Left border accent, hover lift effect
- No glassmorphism or layered shadows

### Current Button Styles

```css
.btn-primary {
    background-color: rgb(191, 170, 101);
    color: #000;
    border-color: rgb(191, 170, 101);
}

.btn-secondary {
    background-color: transparent;
    color: rgb(191, 170, 101);
    border-color: rgb(191, 170, 101);
}
```

- Basic hover state toggles fill
- No focus ring enhancement
- No loading state
- No icon button variants

### Current Gallery/Video Structure

```html
<!-- Video items with overlay -->
<div class="video-item">
    <video class="side-video" autoplay muted loop playsinline>
        <source src="/images/hero-dance-video.mov" type="video/mp4">
    </video>
    <div class="video-overlay">
        <h3>Experience Cuban Dance</h3>
        <p>Boulder's Premier Studio</p>
    </div>
</div>

<!-- Gallery items with overlay -->
<div class="gallery-item">
    <img src="/images/dance-1.jpeg" alt="..." class="gallery-image">
    <div class="gallery-overlay">
        <h3>Technical Precision Focus</h3>
        <p>Systematic approach...</p>
    </div>
</div>
```

- Videos have no poster frames
- No lazy loading implemented
- No grain texture overlay
- Overlays use simple gradients

---

## PR 3.1: Navigation Enhancements

### 3.1.1 Close Button Implementation

#### HTML Changes (layout.ejs)

Replace lines 33-40 with enhanced navigation:

```html
<nav class="nav" id="main-nav" role="navigation" aria-label="Main navigation">
    <!-- Close button - visible only on mobile -->
    <button class="nav-close" aria-label="Close navigation menu" type="button">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
             xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor"
                  stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </button>

    <a href="/" data-page="home"><span>Home</span></a>
    <a href="/about" data-page="about"><span>About</span></a>
    <a href="/events" data-page="events"><span>Events</span></a>
    <a href="/pricing" data-page="pricing"><span>Pricing</span></a>
    <a href="/private-lessons" data-page="private-lessons"><span>Private Lessons</span></a>
    <a href="/contact" data-page="contact"><span>Contact</span></a>
</nav>
```

#### Close Button CSS

```css
/* Navigation Close Button */
.nav-close {
    position: absolute;
    top: 20px;
    right: 20px;
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: 2px solid rgb(191, 170, 101);
    border-radius: 50%;
    color: rgb(191, 170, 101);
    cursor: pointer;
    opacity: 0;
    transform: rotate(-90deg);
    transition: opacity 0.3s ease 0.2s, transform 0.3s ease 0.2s,
                background-color 0.2s ease, border-color 0.2s ease;
    z-index: 1001;
}

.nav.active .nav-close {
    opacity: 1;
    transform: rotate(0deg);
}

.nav-close:hover {
    background-color: rgb(191, 170, 101);
    color: #000;
}

.nav-close:focus {
    outline: 2px solid rgb(191, 170, 101);
    outline-offset: 2px;
}

.nav-close:focus:not(:focus-visible) {
    outline: none;
}

.nav-close:focus-visible {
    outline: 2px solid rgb(191, 170, 101);
    outline-offset: 2px;
}

/* Hide on desktop if nav becomes horizontal */
@media (min-width: 1024px) {
    .nav-close {
        display: none;
    }
}
```

### 3.1.2 Backdrop Blur on Header Scroll

#### Enhanced Header CSS

```css
/* Header with scroll-triggered backdrop blur */
.header {
    background-color: rgba(0, 0, 0, 0.95);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 998;
    height: 60px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    transition: background-color 0.3s ease, backdrop-filter 0.3s ease;
}

/* Scrolled state - applied via JavaScript */
.header.header--scrolled {
    background-color: rgba(0, 0, 0, 0.85);
    -webkit-backdrop-filter: blur(12px);
    backdrop-filter: blur(12px);
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.3);
}

/* Fallback for browsers without backdrop-filter support */
@supports not (backdrop-filter: blur(12px)) {
    .header.header--scrolled {
        background-color: rgba(0, 0, 0, 0.98);
    }
}
```

#### Scroll Detection JavaScript

Add to `public/js/main.js`:

```javascript
/**
 * Header Scroll Blur Effect
 * Applies backdrop blur when user scrolls past threshold
 */
(function initHeaderScroll() {
    const header = document.querySelector('.header');
    if (!header) return;

    const SCROLL_THRESHOLD = 50;
    let ticking = false;
    let lastScrollY = 0;

    function updateHeader() {
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
            window.requestAnimationFrame(updateHeader);
            ticking = true;
        }
    }

    window.addEventListener('scroll', onScroll, { passive: true });

    // Check initial scroll position
    lastScrollY = window.scrollY;
    updateHeader();
})();
```

### 3.1.3 Active Page Indicator

#### Server-Side: Pass Current Page (layout.ejs)

Update the nav links to include active state detection. In layout.ejs, modify the nav:

```html
<nav class="nav" id="main-nav" role="navigation" aria-label="Main navigation">
    <button class="nav-close" aria-label="Close navigation menu" type="button">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
             xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor"
                  stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </button>

    <a href="/" class="<%= typeof currentPage !== 'undefined' && currentPage === 'home' ? 'nav-link--active' : '' %>">
        <span>Home</span>
    </a>
    <a href="/about" class="<%= typeof currentPage !== 'undefined' && currentPage === 'about' ? 'nav-link--active' : '' %>">
        <span>About</span>
    </a>
    <a href="/events" class="<%= typeof currentPage !== 'undefined' && currentPage === 'events' ? 'nav-link--active' : '' %>">
        <span>Events</span>
    </a>
    <a href="/pricing" class="<%= typeof currentPage !== 'undefined' && currentPage === 'pricing' ? 'nav-link--active' : '' %>">
        <span>Pricing</span>
    </a>
    <a href="/private-lessons" class="<%= typeof currentPage !== 'undefined' && currentPage === 'private-lessons' ? 'nav-link--active' : '' %>">
        <span>Private Lessons</span>
    </a>
    <a href="/contact" class="<%= typeof currentPage !== 'undefined' && currentPage === 'contact' ? 'nav-link--active' : '' %>">
        <span>Contact</span>
    </a>
</nav>
```

#### Django View Updates (core/views.py)

Each view must pass `currentPage` in the context:

```python
from django.shortcuts import render

def home(request):
    return render(request, 'home.html', {'currentPage': 'home'})

def about(request):
    return render(request, 'about.html', {'currentPage': 'about'})

def events(request):
    return render(request, 'events.html', {
        'currentPage': 'events',
        'events': get_events_data()
    })

def pricing(request):
    return render(request, 'pricing.html', {'currentPage': 'pricing'})

def private_lessons(request):
    return render(request, 'private-lessons.html', {'currentPage': 'private-lessons'})

def contact(request):
    return render(request, 'contact.html', {'currentPage': 'contact'})
```

#### Active Link CSS

```css
/* Active page indicator */
.nav a.nav-link--active {
    position: relative;
}

.nav a.nav-link--active span::after {
    width: 100%;
    background-color: rgb(191, 170, 101);
}

.nav a.nav-link--active::before {
    content: '';
    position: absolute;
    left: -15px;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 4px;
    background-color: rgb(191, 170, 101);
    border-radius: 50%;
}
```

### 3.1.4 Keyboard Navigation

#### Enhanced JavaScript (public/js/main.js)

Replace the existing navigation code with this comprehensive solution:

```javascript
/**
 * Mobile Navigation Module
 * Handles menu toggle, close button, keyboard navigation, and focus trap
 */
const MobileNav = (function() {
    'use strict';

    // DOM Elements
    let menuToggle;
    let nav;
    let navClose;
    let navLinks;
    let focusableElements;
    let firstFocusable;
    let lastFocusable;

    // State
    let isOpen = false;

    /**
     * Initialize navigation
     */
    function init() {
        menuToggle = document.querySelector('.menu-toggle');
        nav = document.querySelector('.nav');
        navClose = document.querySelector('.nav-close');

        if (!menuToggle || !nav) {
            console.warn('Navigation elements not found');
            return;
        }

        // Get all focusable elements within nav
        updateFocusableElements();

        // Event listeners
        menuToggle.addEventListener('click', toggle);

        if (navClose) {
            navClose.addEventListener('click', close);
        }

        // Keyboard event listener
        document.addEventListener('keydown', handleKeydown);

        // Close when clicking outside
        document.addEventListener('click', handleOutsideClick);

        // Update focusable elements on window resize
        window.addEventListener('resize', debounce(updateFocusableElements, 100));
    }

    /**
     * Update list of focusable elements
     */
    function updateFocusableElements() {
        if (!nav) return;

        focusableElements = nav.querySelectorAll(
            'a[href], button:not([disabled]), textarea:not([disabled]), ' +
            'input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );

        navLinks = nav.querySelectorAll('a');

        if (focusableElements.length > 0) {
            firstFocusable = focusableElements[0];
            lastFocusable = focusableElements[focusableElements.length - 1];
        }
    }

    /**
     * Toggle menu open/closed
     */
    function toggle() {
        if (isOpen) {
            close();
        } else {
            open();
        }
    }

    /**
     * Open menu
     */
    function open() {
        isOpen = true;
        nav.classList.add('active');
        menuToggle.classList.add('active');
        menuToggle.setAttribute('aria-expanded', 'true');
        nav.setAttribute('aria-hidden', 'false');

        // Announce to screen readers
        announceToScreenReader('Navigation menu opened');

        // Focus first element after animation
        setTimeout(() => {
            if (navClose) {
                navClose.focus();
            } else if (firstFocusable) {
                firstFocusable.focus();
            }
        }, 350);

        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }

    /**
     * Close menu
     */
    function close() {
        isOpen = false;
        nav.classList.remove('active');
        menuToggle.classList.remove('active');
        menuToggle.setAttribute('aria-expanded', 'false');
        nav.setAttribute('aria-hidden', 'true');

        // Announce to screen readers
        announceToScreenReader('Navigation menu closed');

        // Return focus to menu toggle
        menuToggle.focus();

        // Restore body scroll
        document.body.style.overflow = '';
    }

    /**
     * Handle keyboard events
     * @param {KeyboardEvent} event
     */
    function handleKeydown(event) {
        // Escape closes menu
        if (event.key === 'Escape' && isOpen) {
            event.preventDefault();
            close();
            return;
        }

        // Tab trapping when menu is open
        if (event.key === 'Tab' && isOpen) {
            handleTabKey(event);
        }
    }

    /**
     * Handle Tab key for focus trap
     * @param {KeyboardEvent} event
     */
    function handleTabKey(event) {
        if (!firstFocusable || !lastFocusable) return;

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

    /**
     * Handle clicks outside menu
     * @param {MouseEvent} event
     */
    function handleOutsideClick(event) {
        if (!isOpen) return;

        if (!nav.contains(event.target) && !menuToggle.contains(event.target)) {
            close();
        }
    }

    /**
     * Announce message to screen readers
     * @param {string} message
     */
    function announceToScreenReader(message) {
        let announcer = document.getElementById('nav-announcer');

        if (!announcer) {
            announcer = document.createElement('div');
            announcer.id = 'nav-announcer';
            announcer.setAttribute('role', 'status');
            announcer.setAttribute('aria-live', 'polite');
            announcer.setAttribute('aria-atomic', 'true');
            announcer.className = 'sr-only';
            document.body.appendChild(announcer);
        }

        // Clear and set message (triggers announcement)
        announcer.textContent = '';
        setTimeout(() => {
            announcer.textContent = message;
        }, 100);
    }

    /**
     * Debounce utility
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

    // Public API
    return {
        init,
        open,
        close,
        toggle
    };
})();

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    MobileNav.init();
});
```

#### Screen Reader Only Utility Class

```css
/* Screen reader only - for announcements */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}
```

### 3.1.5 Updated Menu Toggle ARIA

Update the menu toggle button in layout.ejs:

```html
<button class="menu-toggle"
        aria-label="Open navigation menu"
        aria-expanded="false"
        aria-controls="main-nav"
        type="button">
    <span></span>
    <span></span>
    <span></span>
</button>
```

---

## PR 3.2: Card and Button System

### 3.2.1 Glassmorphism Card Effect

#### CSS Custom Properties (Design Tokens)

```css
/* Design Tokens for Cards */
:root {
    /* Brand Colors */
    --color-gold: rgb(191, 170, 101);
    --color-gold-light: rgba(191, 170, 101, 0.8);
    --color-gold-10: rgba(191, 170, 101, 0.1);
    --color-gold-20: rgba(191, 170, 101, 0.2);
    --color-black: #000;
    --color-white: #fff;

    /* Glassmorphism */
    --glass-bg: rgba(0, 0, 0, 0.4);
    --glass-bg-hover: rgba(0, 0, 0, 0.5);
    --glass-blur: 16px;
    --glass-border: rgba(191, 170, 101, 0.15);
    --glass-border-hover: rgba(191, 170, 101, 0.3);

    /* Shadows */
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.2);
    --shadow-md: 0 8px 25px rgba(0, 0, 0, 0.3);
    --shadow-lg: 0 15px 40px rgba(0, 0, 0, 0.4);
    --shadow-gold: 0 8px 30px rgba(191, 170, 101, 0.15);
    --shadow-gold-lg: 0 12px 40px rgba(191, 170, 101, 0.25);

    /* Transitions */
    --transition-fast: 0.2s ease;
    --transition-normal: 0.3s ease;
    --transition-slow: 0.4s ease;

    /* Border Radius */
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
}
```

#### Glassmorphism Card Base

```css
/* Base Glass Card */
.card-glass {
    position: relative;
    background: var(--glass-bg);
    -webkit-backdrop-filter: blur(var(--glass-blur));
    backdrop-filter: blur(var(--glass-blur));
    border-radius: var(--radius-md);
    border: 1px solid var(--glass-border);
    padding: 1.5rem;
    transition: transform var(--transition-normal),
                box-shadow var(--transition-normal),
                border-color var(--transition-normal),
                background var(--transition-normal);
}

.card-glass:hover {
    transform: translateY(-4px);
    background: var(--glass-bg-hover);
    border-color: var(--glass-border-hover);
    box-shadow: var(--shadow-lg), var(--shadow-gold);
}

/* Fallback for browsers without backdrop-filter */
@supports not (backdrop-filter: blur(16px)) {
    .card-glass {
        background: rgba(0, 0, 0, 0.85);
    }

    .card-glass:hover {
        background: rgba(0, 0, 0, 0.9);
    }
}
```

### 3.2.2 Layered Shadow System

```css
/* Elevation Levels */
.elevation-0 {
    box-shadow: none;
}

.elevation-1 {
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12),
                0 1px 2px rgba(0, 0, 0, 0.24);
}

.elevation-2 {
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15),
                0 2px 4px rgba(0, 0, 0, 0.12);
}

.elevation-3 {
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15),
                0 3px 6px rgba(0, 0, 0, 0.10);
}

.elevation-4 {
    box-shadow: 0 15px 25px rgba(0, 0, 0, 0.15),
                0 5px 10px rgba(0, 0, 0, 0.05);
}

.elevation-5 {
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

/* Interactive Elevation - rises on hover */
.elevation-interactive {
    box-shadow: var(--shadow-md);
    transition: box-shadow var(--transition-normal),
                transform var(--transition-normal);
}

.elevation-interactive:hover {
    box-shadow: var(--shadow-lg), var(--shadow-gold);
    transform: translateY(-4px);
}

/* Gold Glow Elevation */
.elevation-gold {
    box-shadow: var(--shadow-md);
    transition: box-shadow var(--transition-normal);
}

.elevation-gold:hover {
    box-shadow: var(--shadow-md),
                0 0 30px rgba(191, 170, 101, 0.3),
                0 0 60px rgba(191, 170, 101, 0.1);
}
```

### 3.2.3 Gradient Border Accents

```css
/* Gradient Border Card */
.card-gradient-border {
    position: relative;
    background: var(--color-black);
    border-radius: var(--radius-md);
    padding: 1.5rem;
}

.card-gradient-border::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: var(--radius-md);
    padding: 1px;
    background: linear-gradient(
        135deg,
        rgba(191, 170, 101, 0.6) 0%,
        rgba(191, 170, 101, 0.1) 50%,
        rgba(191, 170, 101, 0.6) 100%
    );
    -webkit-mask: linear-gradient(#fff 0 0) content-box,
                  linear-gradient(#fff 0 0);
    mask: linear-gradient(#fff 0 0) content-box,
          linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
    transition: background var(--transition-normal);
}

.card-gradient-border:hover::before {
    background: linear-gradient(
        135deg,
        rgba(191, 170, 101, 1) 0%,
        rgba(191, 170, 101, 0.3) 50%,
        rgba(191, 170, 101, 1) 100%
    );
}

/* Top Border Accent Variant */
.card-top-accent {
    position: relative;
    overflow: hidden;
}

.card-top-accent::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(
        90deg,
        transparent 0%,
        var(--color-gold) 50%,
        transparent 100%
    );
    transform: scaleX(0.3);
    transition: transform var(--transition-normal);
}

.card-top-accent:hover::before {
    transform: scaleX(1);
}
```

### 3.2.4 Apply Glass Effect to Existing Cards

#### Updated Event Card

```css
/* Enhanced Event Card with Glassmorphism */
.event-card {
    position: relative;
    background: var(--glass-bg);
    -webkit-backdrop-filter: blur(var(--glass-blur));
    backdrop-filter: blur(var(--glass-blur));
    border-radius: var(--radius-md);
    padding: 1.5rem;
    border: 1px solid var(--glass-border);
    display: flex;
    flex-direction: column;
    color: var(--color-gold);
    transition: transform var(--transition-normal),
                box-shadow var(--transition-normal),
                border-color var(--transition-normal);
}

/* Gradient top accent */
.event-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(
        90deg,
        transparent 0%,
        var(--color-gold) 20%,
        var(--color-gold) 80%,
        transparent 100%
    );
    border-radius: var(--radius-md) var(--radius-md) 0 0;
}

.event-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-lg), var(--shadow-gold);
    border-color: var(--glass-border-hover);
}

/* Fallback */
@supports not (backdrop-filter: blur(16px)) {
    .event-card {
        background: rgba(0, 0, 0, 0.9);
        border-top: 4px solid var(--color-gold);
    }

    .event-card::before {
        display: none;
    }
}
```

#### Updated Mission Item

```css
/* Enhanced Mission Item */
.mission-item {
    position: relative;
    background: var(--glass-bg);
    -webkit-backdrop-filter: blur(var(--glass-blur));
    backdrop-filter: blur(var(--glass-blur));
    padding: 2rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--glass-border);
    text-align: center;
    transition: transform var(--transition-normal),
                box-shadow var(--transition-normal),
                border-color var(--transition-normal);
}

.mission-item:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg), var(--shadow-gold);
    border-color: var(--glass-border-hover);
}

/* Fallback */
@supports not (backdrop-filter: blur(16px)) {
    .mission-item {
        background: rgba(191, 170, 101, 0.1);
    }
}
```

#### Updated Class Preview

```css
/* Enhanced Class Preview */
.class-preview {
    position: relative;
    background: var(--glass-bg);
    -webkit-backdrop-filter: blur(12px);
    backdrop-filter: blur(12px);
    padding: 2rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--glass-border);
    transition: transform var(--transition-normal),
                box-shadow var(--transition-normal),
                border-color var(--transition-normal);
    overflow: hidden;
}

/* Left border accent */
.class-preview::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: linear-gradient(
        180deg,
        var(--color-gold) 0%,
        rgba(191, 170, 101, 0.3) 100%
    );
}

.class-preview:hover {
    transform: translateY(-4px) translateX(2px);
    box-shadow: var(--shadow-lg), var(--shadow-gold);
    border-color: var(--glass-border-hover);
}

/* Fallback */
@supports not (backdrop-filter: blur(12px)) {
    .class-preview {
        background: rgba(0, 0, 0, 0.7);
        border-left: 4px solid var(--color-gold);
    }

    .class-preview::before {
        display: none;
    }
}
```

### 3.2.5 Enhanced Button States

```css
/* Button Base Reset */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 1rem 2rem;
    text-decoration: none;
    border-radius: var(--radius-sm);
    font-weight: 600;
    font-size: 1rem;
    border: 2px solid transparent;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: all var(--transition-normal);
}

/* Primary Button */
.btn-primary {
    background-color: var(--color-gold);
    color: var(--color-black);
    border-color: var(--color-gold);
}

.btn-primary:hover {
    background-color: transparent;
    color: var(--color-gold);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(191, 170, 101, 0.3);
}

.btn-primary:active {
    transform: translateY(0);
    box-shadow: 0 2px 8px rgba(191, 170, 101, 0.2);
}

/* Focus state */
.btn-primary:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(191, 170, 101, 0.4);
}

.btn-primary:focus:not(:focus-visible) {
    box-shadow: none;
}

.btn-primary:focus-visible {
    outline: none;
    box-shadow: 0 0 0 3px rgba(191, 170, 101, 0.4);
}

/* Secondary Button */
.btn-secondary {
    background-color: transparent;
    color: var(--color-gold);
    border-color: var(--color-gold);
}

.btn-secondary:hover {
    background-color: var(--color-gold);
    color: var(--color-black);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(191, 170, 101, 0.3);
}

.btn-secondary:active {
    transform: translateY(0);
    box-shadow: 0 2px 8px rgba(191, 170, 101, 0.2);
}

.btn-secondary:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(191, 170, 101, 0.4);
}

.btn-secondary:focus:not(:focus-visible) {
    box-shadow: none;
}

.btn-secondary:focus-visible {
    outline: none;
    box-shadow: 0 0 0 3px rgba(191, 170, 101, 0.4);
}

/* Disabled State */
.btn:disabled,
.btn.btn--disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
}
```

### 3.2.6 Button Loading Spinner

#### CSS Loading Spinner

```css
/* Button Loading State */
.btn--loading {
    color: transparent !important;
    pointer-events: none;
    position: relative;
}

.btn--loading::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    top: 50%;
    left: 50%;
    margin-left: -10px;
    margin-top: -10px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: btn-spinner 0.8s linear infinite;
}

.btn-primary.btn--loading::after {
    border-top-color: var(--color-black);
}

.btn-secondary.btn--loading::after {
    border-top-color: var(--color-gold);
}

.btn-primary:hover.btn--loading::after {
    border-top-color: var(--color-gold);
}

.btn-secondary:hover.btn--loading::after {
    border-top-color: var(--color-black);
}

@keyframes btn-spinner {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

/* Loading text for screen readers */
.btn--loading .btn-loading-text {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}
```

#### JavaScript Loading State Helper

```javascript
/**
 * Button Loading State Manager
 */
const ButtonLoader = {
    /**
     * Set button to loading state
     * @param {HTMLElement} button
     * @param {string} loadingText - Text for screen readers
     */
    start(button, loadingText = 'Loading...') {
        if (!button || button.classList.contains('btn--loading')) return;

        // Store original text
        button.dataset.originalText = button.textContent;

        // Add loading class
        button.classList.add('btn--loading');
        button.setAttribute('aria-busy', 'true');

        // Add screen reader text
        const srText = document.createElement('span');
        srText.className = 'btn-loading-text';
        srText.textContent = loadingText;
        button.appendChild(srText);
    },

    /**
     * Remove loading state from button
     * @param {HTMLElement} button
     */
    stop(button) {
        if (!button || !button.classList.contains('btn--loading')) return;

        button.classList.remove('btn--loading');
        button.setAttribute('aria-busy', 'false');

        // Remove screen reader text
        const srText = button.querySelector('.btn-loading-text');
        if (srText) {
            srText.remove();
        }

        // Restore original text if needed
        if (button.dataset.originalText) {
            button.textContent = button.dataset.originalText;
            delete button.dataset.originalText;
        }
    }
};
```

### 3.2.7 Icon Button Variants

#### HTML Structure for Icon Buttons

```html
<!-- Icon only button -->
<button class="btn btn-icon" aria-label="Close">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M18 6L6 18M6 6L18 18" stroke="currentColor"
              stroke-width="2" stroke-linecap="round"/>
    </svg>
</button>

<!-- Button with icon and text -->
<button class="btn btn-primary btn-with-icon">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor"
              stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <span>Continue</span>
</button>

<!-- Icon trailing -->
<button class="btn btn-secondary btn-with-icon btn-icon-trailing">
    <span>Learn More</span>
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor"
              stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
</button>
```

#### Icon Button CSS

```css
/* Icon Only Button */
.btn-icon {
    width: 44px;
    height: 44px;
    padding: 0;
    border-radius: 50%;
    background: transparent;
    border: 2px solid var(--color-gold);
    color: var(--color-gold);
}

.btn-icon:hover {
    background: var(--color-gold);
    color: var(--color-black);
    transform: scale(1.05);
}

.btn-icon:active {
    transform: scale(0.98);
}

.btn-icon svg {
    width: 20px;
    height: 20px;
}

/* Button with Icon */
.btn-with-icon {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.btn-with-icon svg {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    transition: transform var(--transition-fast);
}

.btn-with-icon:hover svg {
    transform: translateX(3px);
}

/* Icon Trailing (icon after text) */
.btn-icon-trailing {
    flex-direction: row;
}

.btn-icon-trailing:hover svg {
    transform: translateX(3px);
}

/* Small Icon Button */
.btn-icon-sm {
    width: 36px;
    height: 36px;
}

.btn-icon-sm svg {
    width: 16px;
    height: 16px;
}

/* Large Icon Button */
.btn-icon-lg {
    width: 56px;
    height: 56px;
}

.btn-icon-lg svg {
    width: 24px;
    height: 24px;
}
```

---

## PR 3.3: Gallery and Media Enhancements

### 3.3.1 Video Poster Frames

#### Updated Video HTML (home.ejs)

```html
<div class="dual-video-container">
    <div class="video-item">
        <video class="side-video"
               autoplay muted loop playsinline
               poster="/images/video-poster-1.jpg"
               aria-label="Cuban dance demonstration video">
            <source src="/images/hero-dance-video.mov" type="video/mp4">
            <source src="/images/hero-dance-video.webm" type="video/webm">
            Your browser does not support the video tag.
        </video>
        <div class="video-overlay">
            <h3>Experience Cuban Dance</h3>
            <p>Boulder's Premier Studio</p>
        </div>
    </div>
    <div class="video-item">
        <video class="side-video"
               autoplay muted loop playsinline
               poster="/images/video-poster-2.jpg"
               aria-label="Cuban footwork demonstration video">
            <source src="/images/second-dance-video.mov" type="video/mp4">
            <source src="/images/second-dance-video.webm" type="video/webm">
            Your browser does not support the video tag.
        </video>
        <div class="video-overlay">
            <h3>Perfect Your Footwork</h3>
            <p>Master Cuban Techniques</p>
        </div>
    </div>
</div>
```

#### Video CSS Enhancements

```css
/* Enhanced Video Styles */
.side-video {
    width: 100%;
    height: auto;
    display: block;
    object-fit: cover;
    background-color: var(--color-black);
}

/* Ensure poster displays correctly */
.side-video[poster] {
    object-fit: cover;
}

/* Play button overlay for non-autoplay scenarios */
.video-item {
    position: relative;
}

.video-play-button {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 72px;
    height: 72px;
    background: rgba(191, 170, 101, 0.9);
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity var(--transition-normal), transform var(--transition-normal);
    z-index: 10;
}

.video-item:hover .video-play-button {
    opacity: 1;
}

.video-play-button:hover {
    transform: translate(-50%, -50%) scale(1.1);
    background: var(--color-gold);
}

.video-play-button svg {
    width: 28px;
    height: 28px;
    fill: var(--color-black);
    margin-left: 4px; /* Optical centering for play icon */
}
```

### 3.3.2 Lazy Loading Implementation

#### Native Lazy Loading HTML

```html
<!-- Gallery images with native lazy loading -->
<div class="gallery-item">
    <img src="/images/dance-1.jpeg"
         alt="Technical Precision Cuban Dance"
         class="gallery-image"
         loading="lazy"
         decoding="async"
         width="600"
         height="400">
    <div class="gallery-overlay">
        <h3>Technical Precision Focus</h3>
        <p>Systematic approach to Casino & Afro-Cuban movement</p>
    </div>
</div>

<div class="gallery-item">
    <img src="/images/dance-3.jpeg"
         alt="Music Integration Cuban Dance"
         class="gallery-image"
         loading="lazy"
         decoding="async"
         width="600"
         height="400">
    <div class="gallery-overlay">
        <h3>Music & Movement Integration</h3>
        <p>Master salsa-rumba transitions, clave timing & musical connection</p>
    </div>
</div>

<div class="gallery-item">
    <img src="/images/dance-4.jpeg"
         alt="Cuban Dance Training Boulder"
         class="gallery-image"
         loading="lazy"
         decoding="async"
         width="600"
         height="400">
    <div class="gallery-overlay">
        <h3>Cuban Dance Training</h3>
        <p>Fundamentals to advanced flow in every Boulder class</p>
    </div>
</div>
```

#### Intersection Observer Fallback

```javascript
/**
 * Lazy Loading Fallback for browsers without native support
 */
(function initLazyLoading() {
    // Check for native lazy loading support
    if ('loading' in HTMLImageElement.prototype) {
        // Native support - images with loading="lazy" will work automatically
        return;
    }

    // Fallback using Intersection Observer
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');

    if (!lazyImages.length) return;

    // Check for Intersection Observer support
    if (!('IntersectionObserver' in window)) {
        // Ultimate fallback - load all images immediately
        lazyImages.forEach(img => {
            if (img.dataset.src) {
                img.src = img.dataset.src;
            }
        });
        return;
    }

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;

                // If using data-src pattern
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                }

                img.classList.add('lazy-loaded');
                observer.unobserve(img);
            }
        });
    }, {
        rootMargin: '50px 0px',
        threshold: 0.01
    });

    lazyImages.forEach(img => {
        imageObserver.observe(img);
    });
})();
```

#### Lazy Loading CSS

```css
/* Lazy loading fade-in effect */
img[loading="lazy"] {
    opacity: 0;
    transition: opacity var(--transition-normal);
}

img[loading="lazy"].lazy-loaded,
img[loading="lazy"]:not([data-src]) {
    opacity: 1;
}

/* Native lazy loading - images load with opacity 1 */
@supports (loading: lazy) {
    img[loading="lazy"] {
        opacity: 1;
    }
}
```

### 3.3.3 Grain Texture Overlay

#### CSS Grain Texture

```css
/* Grain Texture Overlay */
.hero-grain,
.grain-overlay {
    position: relative;
}

.hero-grain::after,
.grain-overlay::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    opacity: 0.03;
    pointer-events: none;
    z-index: 1;
    mix-blend-mode: overlay;
}

/* Subtle grain for dark backgrounds */
.grain-subtle::after {
    opacity: 0.02;
}

/* Heavier grain for artistic effect */
.grain-heavy::after {
    opacity: 0.06;
}

/* Animated grain (optional - for video-like feel) */
.grain-animated::after {
    animation: grain 0.5s steps(10) infinite;
}

@keyframes grain {
    0%, 100% {
        transform: translate(0, 0);
    }
    10% {
        transform: translate(-1%, -1%);
    }
    20% {
        transform: translate(1%, 1%);
    }
    30% {
        transform: translate(-1%, 1%);
    }
    40% {
        transform: translate(1%, -1%);
    }
    50% {
        transform: translate(-1%, 0%);
    }
    60% {
        transform: translate(1%, 0%);
    }
    70% {
        transform: translate(0%, -1%);
    }
    80% {
        transform: translate(0%, 1%);
    }
    90% {
        transform: translate(-1%, -1%);
    }
}
```

#### Apply Grain to Video Section (home.ejs)

```html
<div class="dual-video-container hero-grain">
    <!-- Video items remain the same -->
</div>
```

#### Alternative: CSS-Only Grain with Pseudo-Element

```css
/* Pure CSS grain texture using gradients */
.grain-css::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
        repeating-radial-gradient(
            circle at 17% 32%,
            rgba(255, 255, 255, 0) 0px,
            rgba(255, 255, 255, 0.015) 1px,
            rgba(255, 255, 255, 0) 2px
        ),
        repeating-radial-gradient(
            circle at 71% 83%,
            rgba(255, 255, 255, 0) 0px,
            rgba(255, 255, 255, 0.01) 1px,
            rgba(255, 255, 255, 0) 2px
        ),
        repeating-radial-gradient(
            circle at 43% 56%,
            rgba(255, 255, 255, 0) 0px,
            rgba(255, 255, 255, 0.012) 1px,
            rgba(255, 255, 255, 0) 2px
        );
    opacity: 1;
    pointer-events: none;
    z-index: 1;
}
```

### 3.3.4 Enhanced Gallery Hover Overlays

```css
/* Enhanced Gallery Overlay */
.gallery-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(
        to top,
        rgba(0, 0, 0, 0.95) 0%,
        rgba(0, 0, 0, 0.7) 40%,
        transparent 100%
    );
    color: white;
    padding: 3rem 1.5rem 1.5rem;
    transform: translateY(100%);
    transition: transform var(--transition-normal);
}

.gallery-item:hover .gallery-overlay {
    transform: translateY(0);
}

/* Glass effect on overlay */
.gallery-overlay-glass {
    background: linear-gradient(
        to top,
        rgba(0, 0, 0, 0.8) 0%,
        rgba(0, 0, 0, 0.4) 100%
    );
    -webkit-backdrop-filter: blur(8px);
    backdrop-filter: blur(8px);
}

/* Overlay content animation */
.gallery-overlay h3 {
    color: var(--color-gold);
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    margin: 0 0 0.5rem 0;
    transform: translateY(20px);
    opacity: 0;
    transition: transform var(--transition-normal) 0.1s,
                opacity var(--transition-normal) 0.1s;
}

.gallery-overlay p {
    margin: 0;
    font-size: 0.9rem;
    opacity: 0;
    transform: translateY(20px);
    transition: transform var(--transition-normal) 0.2s,
                opacity var(--transition-normal) 0.2s;
}

.gallery-item:hover .gallery-overlay h3,
.gallery-item:hover .gallery-overlay p {
    transform: translateY(0);
    opacity: 1;
}

/* Overlay icon indicator */
.gallery-overlay::before {
    content: '';
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 32px;
    height: 32px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23bfaa65' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7'/%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
    opacity: 0;
    transform: scale(0.8);
    transition: opacity var(--transition-normal),
                transform var(--transition-normal);
}

.gallery-item:hover .gallery-overlay::before {
    opacity: 0.8;
    transform: scale(1);
}

/* Fallback for no backdrop-filter */
@supports not (backdrop-filter: blur(8px)) {
    .gallery-overlay-glass {
        background: linear-gradient(
            to top,
            rgba(0, 0, 0, 0.95) 0%,
            rgba(0, 0, 0, 0.8) 100%
        );
    }
}
```

### 3.3.5 Video Overlay Enhancements

```css
/* Enhanced Video Overlay */
.video-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(
        to top,
        rgba(0, 0, 0, 0.9) 0%,
        rgba(0, 0, 0, 0.5) 50%,
        transparent 100%
    );
    -webkit-backdrop-filter: blur(4px);
    backdrop-filter: blur(4px);
    color: white;
    padding: 2rem 1.5rem 1.5rem;
    text-align: center;
    opacity: 0;
    transition: opacity var(--transition-normal);
}

.video-item:hover .video-overlay {
    opacity: 1;
}

.video-overlay h3 {
    color: var(--color-gold);
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    margin: 0 0 0.5rem 0;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
}

.video-overlay p {
    margin: 0;
    font-size: 1rem;
    opacity: 0.95;
    text-shadow: 0 1px 5px rgba(0, 0, 0, 0.5);
}

/* Fallback */
@supports not (backdrop-filter: blur(4px)) {
    .video-overlay {
        background: linear-gradient(
            to top,
            rgba(0, 0, 0, 0.95) 0%,
            rgba(0, 0, 0, 0.7) 50%,
            transparent 100%
        );
    }
}
```

---

## Browser Support Matrix

### Feature Support Table

| Feature | Chrome | Firefox | Safari | Edge | iOS Safari |
|---------|--------|---------|--------|------|------------|
| backdrop-filter | 76+ | 103+ | 9+ | 79+ | 9+ |
| loading="lazy" | 77+ | 75+ | 15.4+ | 79+ | 15.4+ |
| :focus-visible | 86+ | 85+ | 15.4+ | 86+ | 15.4+ |
| CSS mask | 120+ | 53+ | 15.4+ | 120+ | 15.4+ |
| IntersectionObserver | 58+ | 55+ | 12.1+ | 16+ | 12.2+ |
| requestAnimationFrame | 24+ | 23+ | 6.1+ | 12+ | 7+ |

### Fallback Strategy

#### backdrop-filter Fallback

```css
/* Progressive enhancement pattern */
.glass-element {
    /* Fallback - solid background */
    background: rgba(0, 0, 0, 0.9);
}

/* Enhanced - with blur */
@supports (backdrop-filter: blur(16px)) {
    .glass-element {
        background: rgba(0, 0, 0, 0.4);
        -webkit-backdrop-filter: blur(16px);
        backdrop-filter: blur(16px);
    }
}
```

#### Lazy Loading Fallback

```javascript
// Feature detection
if (!('loading' in HTMLImageElement.prototype)) {
    // Load polyfill or implement IntersectionObserver fallback
    // See section 3.3.2 for implementation
}
```

#### Focus-Visible Fallback

```css
/* Fallback for browsers without :focus-visible */
.btn:focus {
    outline: 2px solid var(--color-gold);
    outline-offset: 2px;
}

/* Remove outline for mouse users in supporting browsers */
.btn:focus:not(:focus-visible) {
    outline: none;
}

/* Restore for keyboard users */
.btn:focus-visible {
    outline: 2px solid var(--color-gold);
    outline-offset: 2px;
}
```

### Polyfill Recommendations

| Feature | Polyfill | Size | When to Use |
|---------|----------|------|-------------|
| focus-visible | focus-visible | 1.5KB | IE11, older Safari |
| IntersectionObserver | intersection-observer | 2.5KB | IE11, Safari <12.1 |
| loading="lazy" | lazysizes | 3.4KB | Safari <15.4 |

**Recommendation**: For this project, native features with CSS fallbacks are sufficient.
No polyfills required given the target audience (dance studio visitors using modern devices).

---

## Accessibility Compliance

### WCAG 2.1 AA Requirements

#### 1.4.3 Contrast (Minimum)

- Gold on black: `#bfaa65` on `#000000` = **9.47:1** (AAA compliant)
- Black on gold: `#000000` on `#bfaa65` = **9.47:1** (AAA compliant)
- White on black: `#ffffff` on `#000000` = **21:1** (AAA compliant)

#### 2.1.1 Keyboard

All interactive elements must be operable via keyboard:

- Navigation links: Focusable, activatable with Enter
- Close button: Focusable, activatable with Enter/Space
- Buttons: Focusable, activatable with Enter/Space
- Menu toggle: Focusable, activatable with Enter/Space

#### 2.1.2 No Keyboard Trap

Focus trap is only applied when menu is open and is removable via Escape key.

#### 2.4.3 Focus Order

Navigation focus order follows visual order:

1. Menu toggle button
2. Close button (when menu open)
3. Navigation links (Home -> About -> Events -> Pricing -> Private Lessons -> Contact)

#### 2.4.7 Focus Visible

All focusable elements have visible focus indicators:

```css
/* Minimum focus indicator */
:focus-visible {
    outline: 2px solid var(--color-gold);
    outline-offset: 2px;
}
```

### ARIA Implementation

#### Navigation ARIA

```html
<button class="menu-toggle"
        aria-label="Open navigation menu"
        aria-expanded="false"
        aria-controls="main-nav">

<nav id="main-nav"
     role="navigation"
     aria-label="Main navigation"
     aria-hidden="true">
```

#### Active Link ARIA

```html
<a href="/about" class="nav-link--active" aria-current="page">
    <span>About</span>
</a>
```

#### Button Loading State ARIA

```html
<button class="btn btn-primary btn--loading" aria-busy="true">
    <span class="btn-loading-text">Submitting form...</span>
    Submit
</button>
```

### Screen Reader Announcements

```javascript
// Live region for navigation state changes
function announceToScreenReader(message) {
    const announcer = document.getElementById('nav-announcer');
    announcer.textContent = message;
}

// Usage
announceToScreenReader('Navigation menu opened');
announceToScreenReader('Navigation menu closed');
```

### Reduced Motion Support

```css
/* Respect user preference for reduced motion */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }

    .nav-close {
        transition: none;
    }

    .gallery-overlay {
        transform: none;
        opacity: 1;
    }

    .video-overlay {
        opacity: 1;
    }
}
```

---

## Testing Requirements

### Unit Tests

#### Navigation Module Tests

```javascript
// tests/navigation.test.js
describe('MobileNav', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <button class="menu-toggle"></button>
            <nav class="nav">
                <button class="nav-close"></button>
                <a href="/">Home</a>
                <a href="/about">About</a>
            </nav>
        `;
        MobileNav.init();
    });

    test('opens menu on toggle click', () => {
        const toggle = document.querySelector('.menu-toggle');
        toggle.click();
        expect(document.querySelector('.nav').classList.contains('active')).toBe(true);
    });

    test('closes menu on close button click', () => {
        MobileNav.open();
        const closeBtn = document.querySelector('.nav-close');
        closeBtn.click();
        expect(document.querySelector('.nav').classList.contains('active')).toBe(false);
    });

    test('closes menu on Escape key', () => {
        MobileNav.open();
        const event = new KeyboardEvent('keydown', { key: 'Escape' });
        document.dispatchEvent(event);
        expect(document.querySelector('.nav').classList.contains('active')).toBe(false);
    });

    test('traps focus within open menu', () => {
        MobileNav.open();
        const links = document.querySelectorAll('.nav a');
        const lastLink = links[links.length - 1];
        lastLink.focus();

        const tabEvent = new KeyboardEvent('keydown', { key: 'Tab' });
        document.dispatchEvent(tabEvent);

        // Focus should wrap to first focusable element
        expect(document.activeElement).toBe(document.querySelector('.nav-close'));
    });
});
```

#### Button Loading Tests

```javascript
// tests/button-loader.test.js
describe('ButtonLoader', () => {
    let button;

    beforeEach(() => {
        button = document.createElement('button');
        button.className = 'btn btn-primary';
        button.textContent = 'Submit';
        document.body.appendChild(button);
    });

    afterEach(() => {
        document.body.removeChild(button);
    });

    test('adds loading class', () => {
        ButtonLoader.start(button);
        expect(button.classList.contains('btn--loading')).toBe(true);
    });

    test('sets aria-busy to true', () => {
        ButtonLoader.start(button);
        expect(button.getAttribute('aria-busy')).toBe('true');
    });

    test('removes loading class on stop', () => {
        ButtonLoader.start(button);
        ButtonLoader.stop(button);
        expect(button.classList.contains('btn--loading')).toBe(false);
    });
});
```

### Visual Regression Tests

Using Playwright:

```javascript
// tests/visual/navigation.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Navigation Visual Tests', () => {
    test('header without scroll', async ({ page }) => {
        await page.goto('/');
        await expect(page.locator('.header')).toHaveScreenshot('header-default.png');
    });

    test('header with scroll blur', async ({ page }) => {
        await page.goto('/');
        await page.evaluate(() => window.scrollTo(0, 100));
        await expect(page.locator('.header')).toHaveScreenshot('header-scrolled.png');
    });

    test('mobile menu open', async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
        await page.goto('/');
        await page.click('.menu-toggle');
        await page.waitForTimeout(400); // Wait for animation
        await expect(page.locator('.nav')).toHaveScreenshot('nav-open.png');
    });

    test('close button visible', async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
        await page.goto('/');
        await page.click('.menu-toggle');
        await page.waitForTimeout(400);
        await expect(page.locator('.nav-close')).toBeVisible();
    });
});
```

### Accessibility Tests

```javascript
// tests/a11y/navigation.spec.js
const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test.describe('Navigation Accessibility', () => {
    test('should have no accessibility violations', async ({ page }) => {
        await page.goto('/');
        const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
        expect(accessibilityScanResults.violations).toEqual([]);
    });

    test('focus trap works correctly', async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
        await page.goto('/');
        await page.click('.menu-toggle');
        await page.waitForTimeout(400);

        // Tab through all elements
        for (let i = 0; i < 10; i++) {
            await page.keyboard.press('Tab');
        }

        // Focus should still be within nav
        const focusedElement = await page.evaluate(() => document.activeElement.closest('.nav'));
        expect(focusedElement).not.toBeNull();
    });

    test('escape key closes menu', async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
        await page.goto('/');
        await page.click('.menu-toggle');
        await page.waitForTimeout(400);
        await page.keyboard.press('Escape');

        const navActive = await page.locator('.nav.active').count();
        expect(navActive).toBe(0);
    });
});
```

### Manual Testing Checklist

#### PR 3.1: Navigation

- [ ] Close button appears when menu opens
- [ ] Close button closes menu on click
- [ ] Close button has visible focus indicator
- [ ] Escape key closes menu
- [ ] Focus moves to close button when menu opens
- [ ] Focus returns to menu toggle when menu closes
- [ ] Tab key cycles through nav links
- [ ] Shift+Tab cycles backwards
- [ ] Header gets blur effect on scroll
- [ ] Active page shows indicator
- [ ] Works on iOS Safari
- [ ] Works on Android Chrome
- [ ] Screen reader announces menu state

#### PR 3.2: Cards & Buttons

- [ ] Cards have glass effect
- [ ] Cards elevate on hover
- [ ] Gradient borders animate on hover
- [ ] Buttons have hover, focus, active states
- [ ] Loading spinner displays correctly
- [ ] Loading state is announced to screen readers
- [ ] Icon buttons are properly sized (44x44 minimum)
- [ ] Focus indicators visible on all buttons

#### PR 3.3: Gallery & Media

- [ ] Video poster frames display before play
- [ ] Images lazy load on scroll
- [ ] Grain texture is subtle but visible
- [ ] Gallery overlays slide up on hover
- [ ] Overlay animations are smooth
- [ ] Reduced motion preference respected

---

## Implementation Checklist

### PR 3.1: Navigation Enhancements

#### Files to Modify

- [ ] `/Users/damilola/Documents/Projects/sabor-con-flow-dance/views/layout.ejs`
- [ ] `/Users/damilola/Documents/Projects/sabor-con-flow-dance/public/css/styles.css`
- [ ] `/Users/damilola/Documents/Projects/sabor-con-flow-dance/public/js/main.js`
- [ ] `/Users/damilola/Documents/Projects/sabor-con-flow-dance/routes/*.js` (add currentPage)

#### Tasks

1. [ ] Add close button HTML to nav
2. [ ] Add close button CSS styles
3. [ ] Add header scroll blur CSS
4. [ ] Implement scroll detection JavaScript
5. [ ] Add active page indicator CSS
6. [ ] Update routes to pass currentPage
7. [ ] Implement keyboard navigation JavaScript
8. [ ] Add focus trap implementation
9. [ ] Add screen reader announcements
10. [ ] Add ARIA attributes
11. [ ] Test on mobile devices
12. [ ] Run accessibility audit

### PR 3.2: Card and Button System

#### Files to Modify

- [ ] `/Users/damilola/Documents/Projects/sabor-con-flow-dance/public/css/styles.css`
- [ ] `/Users/damilola/Documents/Projects/sabor-con-flow-dance/public/js/main.js`

#### Tasks

1. [ ] Add CSS custom properties (design tokens)
2. [ ] Implement glassmorphism base class
3. [ ] Add elevation utility classes
4. [ ] Implement gradient border cards
5. [ ] Update event card styles
6. [ ] Update mission item styles
7. [ ] Update class preview styles
8. [ ] Enhance button hover/focus/active states
9. [ ] Add button loading spinner CSS
10. [ ] Add ButtonLoader JavaScript utility
11. [ ] Add icon button variants
12. [ ] Test backdrop-filter fallbacks
13. [ ] Test on Safari (webkit prefix)

### PR 3.3: Gallery and Media Enhancements

#### Files to Modify

- [ ] `/Users/damilola/Documents/Projects/sabor-con-flow-dance/views/home.ejs`
- [ ] `/Users/damilola/Documents/Projects/sabor-con-flow-dance/public/css/styles.css`
- [ ] `/Users/damilola/Documents/Projects/sabor-con-flow-dance/public/js/main.js`

#### Assets to Create

- [ ] Video poster frame 1 (extract from video)
- [ ] Video poster frame 2 (extract from video)

#### Tasks

1. [ ] Add poster attribute to videos
2. [ ] Create/extract poster images
3. [ ] Add loading="lazy" to gallery images
4. [ ] Add width/height attributes to images
5. [ ] Implement lazy loading fallback JS
6. [ ] Add grain texture CSS
7. [ ] Apply grain to video section
8. [ ] Enhance gallery overlay CSS
9. [ ] Enhance video overlay CSS
10. [ ] Add reduced motion media query
11. [ ] Test lazy loading in Safari
12. [ ] Test grain texture performance

---

## File Summary

### Modified Files

| File | PR | Changes |
|------|-----|---------|
| `views/layout.ejs` | 3.1 | Nav close button, ARIA, currentPage |
| `public/css/styles.css` | 3.1, 3.2, 3.3 | All CSS enhancements |
| `public/js/main.js` | 3.1, 3.2, 3.3 | Navigation, scroll, lazy loading |
| `views/home.ejs` | 3.3 | Video poster, lazy loading, grain |
| `routes/*.js` | 3.1 | currentPage variable |

### New Files

| File | PR | Purpose |
|------|-----|---------|
| `public/images/video-poster-1.jpg` | 3.3 | Video poster frame |
| `public/images/video-poster-2.jpg` | 3.3 | Video poster frame |

---

## Appendix A: Complete CSS Module (Post-Phase 3)

After Phase 3 completion, the styles.css should be organized as:

```css
/* ==========================================================================
   SABOR CON FLOW - STYLES
   Phase 3: UI Uplift Components
   ========================================================================== */

/* --------------------------------------------------------------------------
   1. Design Tokens / Custom Properties
   -------------------------------------------------------------------------- */

/* --------------------------------------------------------------------------
   2. Base / Reset Styles
   -------------------------------------------------------------------------- */

/* --------------------------------------------------------------------------
   3. Navigation Component
   - Menu toggle
   - Mobile nav
   - Close button
   - Active indicators
   - Header scroll effects
   -------------------------------------------------------------------------- */

/* --------------------------------------------------------------------------
   4. Card System
   - Glass cards
   - Elevation utilities
   - Gradient borders
   - Event cards
   - Mission items
   - Class previews
   -------------------------------------------------------------------------- */

/* --------------------------------------------------------------------------
   5. Button System
   - Primary buttons
   - Secondary buttons
   - Icon buttons
   - Loading states
   - Focus states
   -------------------------------------------------------------------------- */

/* --------------------------------------------------------------------------
   6. Gallery / Media
   - Video containers
   - Gallery grid
   - Overlays
   - Grain textures
   - Lazy loading
   -------------------------------------------------------------------------- */

/* --------------------------------------------------------------------------
   7. Utilities
   - Screen reader only
   - Visibility
   - Spacing
   -------------------------------------------------------------------------- */

/* --------------------------------------------------------------------------
   8. Responsive Overrides
   -------------------------------------------------------------------------- */

/* --------------------------------------------------------------------------
   9. Accessibility / Reduced Motion
   -------------------------------------------------------------------------- */
```

---

## Appendix B: JavaScript Module Structure

```javascript
/* ==========================================================================
   SABOR CON FLOW - MAIN.JS
   Phase 3: UI Uplift Components
   ========================================================================== */

/**
 * Mobile Navigation Module
 */
const MobileNav = (function() { /* ... */ })();

/**
 * Header Scroll Effects
 */
(function initHeaderScroll() { /* ... */ })();

/**
 * Button Loading State Manager
 */
const ButtonLoader = { /* ... */ };

/**
 * Lazy Loading Fallback
 */
(function initLazyLoading() { /* ... */ })();

/**
 * Initialize all modules on DOM ready
 */
document.addEventListener('DOMContentLoaded', function() {
    MobileNav.init();
});
```

---

**Document Version**: 1.0
**Last Updated**: 2024-12-10
**Next Review**: After Phase 2 completion
