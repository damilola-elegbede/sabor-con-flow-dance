# PR 2.1: Homepage & Navigation Implementation

## PR Metadata

**Title:** feat: Implement responsive homepage and navigation system  
**Branch:** `feature/homepage-navigation`  
**Base:** `feature/phase-1-complete`  
**Dependencies:** 
- PR 1.1 (Project Setup)
- PR 1.2 (Static Assets)
- PR 1.3 (CSS Architecture)

## Overview

This PR implements the homepage with hero section, navigation system, and core layout components using semantic HTML5, custom CSS3, and vanilla JavaScript with progressive enhancement.

## File Structure

```
/
├── index.html
├── api/
│   └── navigation.js
├── static/
│   ├── css/
│   │   ├── homepage.css
│   │   ├── navigation.css
│   │   └── hero.css
│   ├── js/
│   │   ├── navigation.js
│   │   ├── hero.js
│   │   └── scroll-effects.js
│   └── images/
│       └── hero/
└── tests/
    ├── homepage.test.js
    └── navigation.test.js
```

## Implementation Details

### 1. Homepage HTML Structure (`index.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Sabor con Flow Dance - Learn Salsa, Bachata, and Latin dance in San Francisco">
    <title>Sabor con Flow Dance - Latin Dance Studio San Francisco</title>
    
    <!-- Critical CSS inline -->
    <style>
        /* Critical above-the-fold CSS */
        :root {
            --primary-color: #E63946;
            --secondary-color: #F1FAEE;
            --accent-color: #A8DADC;
            --dark-color: #1D3557;
            --text-color: #333;
            --white: #FFFFFF;
            --max-width: 1200px;
            --nav-height: 70px;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
        }
        
        /* Prevent layout shift */
        .hero {
            min-height: 100vh;
            position: relative;
        }
    </style>
    
    <!-- Async load non-critical CSS -->
    <link rel="preload" href="/static/css/homepage.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <link rel="preload" href="/static/css/navigation.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <noscript>
        <link rel="stylesheet" href="/static/css/homepage.css">
        <link rel="stylesheet" href="/static/css/navigation.css">
    </noscript>
    
    <!-- Preconnect to external resources -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="dns-prefetch" href="https://www.googletagmanager.com">
</head>
<body>
    <!-- Skip to content link for accessibility -->
    <a href="#main-content" class="skip-link">Skip to main content</a>
    
    <!-- Navigation -->
    <nav class="main-nav" role="navigation" aria-label="Main navigation">
        <div class="nav-container">
            <a href="/" class="nav-logo" aria-label="Sabor con Flow Dance Home">
                <img src="/static/images/logo.svg" alt="Sabor con Flow Dance" width="180" height="60" loading="eager">
            </a>
            
            <!-- Mobile menu button -->
            <button class="nav-toggle" 
                    aria-expanded="false" 
                    aria-controls="nav-menu"
                    aria-label="Toggle navigation menu">
                <span class="hamburger"></span>
                <span class="hamburger"></span>
                <span class="hamburger"></span>
            </button>
            
            <!-- Navigation menu -->
            <ul id="nav-menu" class="nav-menu">
                <li><a href="/" class="nav-link active" aria-current="page">Home</a></li>
                <li><a href="/schedule" class="nav-link">Schedule</a></li>
                <li class="nav-dropdown">
                    <button class="nav-link dropdown-toggle" 
                            aria-expanded="false"
                            aria-haspopup="true">
                        Classes <span class="arrow" aria-hidden="true">▼</span>
                    </button>
                    <ul class="dropdown-menu" role="menu">
                        <li><a href="/classes/salsa" role="menuitem">Salsa</a></li>
                        <li><a href="/classes/bachata" role="menuitem">Bachata</a></li>
                        <li><a href="/classes/private" role="menuitem">Private Lessons</a></li>
                    </ul>
                </li>
                <li><a href="/instructors" class="nav-link">Instructors</a></li>
                <li><a href="/events" class="nav-link">Events</a></li>
                <li><a href="/contact" class="nav-link">Contact</a></li>
                <li><a href="/book" class="nav-link nav-cta">Book Now</a></li>
            </ul>
        </div>
    </nav>
    
    <!-- Main content -->
    <main id="main-content">
        <!-- Hero Section -->
        <section class="hero" aria-labelledby="hero-heading">
            <div class="hero-background">
                <picture>
                    <source media="(max-width: 768px)" 
                            srcset="/static/images/hero/hero-mobile.webp" 
                            type="image/webp">
                    <source media="(max-width: 768px)" 
                            srcset="/static/images/hero/hero-mobile.jpg" 
                            type="image/jpeg">
                    <source srcset="/static/images/hero/hero-desktop.webp" 
                            type="image/webp">
                    <img src="/static/images/hero/hero-desktop.jpg" 
                         alt="Dance studio with students practicing salsa"
                         loading="eager"
                         width="1920"
                         height="1080"
                         class="hero-image">
                </picture>
                <div class="hero-overlay"></div>
            </div>
            
            <div class="hero-content">
                <h1 id="hero-heading" class="hero-title">
                    <span class="hero-title-line">Feel the Rhythm,</span>
                    <span class="hero-title-line">Live the Dance</span>
                </h1>
                <p class="hero-subtitle">
                    San Francisco's premier Latin dance studio offering Salsa, Bachata, and more
                </p>
                <div class="hero-actions">
                    <a href="/book" class="btn btn-primary btn-large">Start Dancing Today</a>
                    <a href="/schedule" class="btn btn-secondary btn-large">View Schedule</a>
                </div>
                
                <!-- Social proof -->
                <div class="hero-social-proof">
                    <div class="rating">
                        <span class="stars" aria-label="5 star rating">★★★★★</span>
                        <span>4.9/5 from 200+ students</span>
                    </div>
                </div>
            </div>
            
            <!-- Scroll indicator -->
            <button class="scroll-indicator" 
                    aria-label="Scroll to next section"
                    onclick="document.getElementById('intro').scrollIntoView({behavior: 'smooth'})">
                <svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6z"/>
                </svg>
            </button>
        </section>
        
        <!-- Introduction Section -->
        <section id="intro" class="section intro-section">
            <div class="container">
                <h2 class="section-title">Welcome to Sabor con Flow</h2>
                <p class="section-subtitle">Where passion meets rhythm in the heart of San Francisco</p>
                
                <div class="intro-grid">
                    <article class="intro-card">
                        <div class="intro-icon">
                            <svg aria-hidden="true"><!-- Icon SVG --></svg>
                        </div>
                        <h3>Expert Instructors</h3>
                        <p>Learn from internationally trained dance professionals with years of teaching experience.</p>
                    </article>
                    
                    <article class="intro-card">
                        <div class="intro-icon">
                            <svg aria-hidden="true"><!-- Icon SVG --></svg>
                        </div>
                        <h3>All Levels Welcome</h3>
                        <p>From absolute beginners to advanced dancers, we have the perfect class for you.</p>
                    </article>
                    
                    <article class="intro-card">
                        <div class="intro-icon">
                            <svg aria-hidden="true"><!-- Icon SVG --></svg>
                        </div>
                        <h3>Vibrant Community</h3>
                        <p>Join a supportive community of dance enthusiasts who share your passion.</p>
                    </article>
                </div>
            </div>
        </section>
    </main>
    
    <!-- Footer -->
    <footer class="site-footer">
        <div class="container">
            <p>&copy; 2024 Sabor con Flow Dance. All rights reserved.</p>
        </div>
    </footer>
    
    <!-- JavaScript modules -->
    <script type="module" src="/static/js/navigation.js"></script>
    <script type="module" src="/static/js/hero.js"></script>
    <script type="module" src="/static/js/scroll-effects.js"></script>
</body>
</html>
```

### 2. Navigation CSS (`static/css/navigation.css`)

```css
/* Navigation Styles */
.main-nav {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: var(--nav-height);
    background: var(--white);
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    z-index: 1000;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.main-nav.scrolled {
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.main-nav.hidden {
    transform: translateY(-100%);
}

.nav-container {
    max-width: var(--max-width);
    margin: 0 auto;
    padding: 0 20px;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.nav-logo {
    display: flex;
    align-items: center;
    text-decoration: none;
    font-weight: bold;
    font-size: 1.5rem;
    color: var(--primary-color);
}

.nav-logo img {
    height: 40px;
    width: auto;
}

/* Navigation Menu */
.nav-menu {
    display: flex;
    list-style: none;
    gap: 2rem;
    align-items: center;
}

.nav-link {
    color: var(--text-color);
    text-decoration: none;
    font-weight: 500;
    padding: 0.5rem 0;
    position: relative;
    transition: color 0.3s ease;
    background: none;
    border: none;
    font-size: 1rem;
    cursor: pointer;
}

.nav-link:hover,
.nav-link:focus {
    color: var(--primary-color);
}

.nav-link.active {
    color: var(--primary-color);
}

.nav-link.active::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--primary-color);
}

/* CTA Button */
.nav-cta {
    background: var(--primary-color);
    color: var(--white);
    padding: 0.5rem 1.5rem;
    border-radius: 25px;
    transition: background 0.3s ease, transform 0.2s ease;
}

.nav-cta:hover,
.nav-cta:focus {
    background: var(--dark-color);
    color: var(--white);
    transform: translateY(-2px);
}

/* Dropdown Menu */
.nav-dropdown {
    position: relative;
}

.dropdown-toggle {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.dropdown-toggle .arrow {
    font-size: 0.75rem;
    transition: transform 0.3s ease;
}

.dropdown-toggle[aria-expanded="true"] .arrow {
    transform: rotate(180deg);
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    background: var(--white);
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    border-radius: 8px;
    padding: 0.5rem 0;
    min-width: 200px;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all 0.3s ease;
    list-style: none;
}

.nav-dropdown:hover .dropdown-menu,
.nav-dropdown:focus-within .dropdown-menu,
.dropdown-toggle[aria-expanded="true"] + .dropdown-menu {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.dropdown-menu a {
    display: block;
    padding: 0.75rem 1.5rem;
    color: var(--text-color);
    text-decoration: none;
    transition: background 0.2s ease, color 0.2s ease;
}

.dropdown-menu a:hover,
.dropdown-menu a:focus {
    background: var(--secondary-color);
    color: var(--primary-color);
}

/* Mobile Navigation */
.nav-toggle {
    display: none;
    flex-direction: column;
    gap: 4px;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.5rem;
}

.hamburger {
    width: 25px;
    height: 3px;
    background: var(--text-color);
    transition: all 0.3s ease;
    transform-origin: center;
}

.nav-toggle[aria-expanded="true"] .hamburger:nth-child(1) {
    transform: rotate(45deg) translate(6px, 6px);
}

.nav-toggle[aria-expanded="true"] .hamburger:nth-child(2) {
    opacity: 0;
}

.nav-toggle[aria-expanded="true"] .hamburger:nth-child(3) {
    transform: rotate(-45deg) translate(6px, -6px);
}

/* Mobile Styles */
@media (max-width: 768px) {
    .nav-toggle {
        display: flex;
    }
    
    .nav-menu {
        position: fixed;
        top: var(--nav-height);
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--white);
        flex-direction: column;
        justify-content: flex-start;
        padding: 2rem;
        gap: 1rem;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    }
    
    .nav-toggle[aria-expanded="true"] ~ .nav-menu {
        transform: translateX(0);
    }
    
    .nav-link {
        width: 100%;
        padding: 1rem;
        text-align: left;
        border-bottom: 1px solid var(--secondary-color);
    }
    
    .dropdown-menu {
        position: static;
        opacity: 1;
        visibility: visible;
        transform: none;
        box-shadow: none;
        padding-left: 1rem;
        display: none;
    }
    
    .dropdown-toggle[aria-expanded="true"] + .dropdown-menu {
        display: block;
    }
    
    .nav-cta {
        width: 100%;
        text-align: center;
        margin-top: 1rem;
    }
}

/* Accessibility */
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: var(--primary-color);
    color: var(--white);
    padding: 0.5rem 1rem;
    text-decoration: none;
    z-index: 100;
}

.skip-link:focus {
    top: 0;
}

/* Print styles */
@media print {
    .main-nav {
        position: static;
        box-shadow: none;
    }
    
    .nav-toggle,
    .nav-cta {
        display: none;
    }
}
```

### 3. Navigation JavaScript (`static/js/navigation.js`)

```javascript
/**
 * Navigation Module
 * Handles responsive navigation, scroll effects, and dropdown menus
 */

class Navigation {
    constructor() {
        this.nav = document.querySelector('.main-nav');
        this.navToggle = document.querySelector('.nav-toggle');
        this.navMenu = document.querySelector('.nav-menu');
        this.dropdownToggles = document.querySelectorAll('.dropdown-toggle');
        this.navLinks = document.querySelectorAll('.nav-link');
        
        this.lastScrollY = 0;
        this.ticking = false;
        
        this.init();
    }
    
    init() {
        if (!this.nav) return;
        
        // Mobile menu toggle
        if (this.navToggle) {
            this.navToggle.addEventListener('click', () => this.toggleMobileMenu());
        }
        
        // Dropdown menus
        this.initDropdowns();
        
        // Scroll effects
        this.initScrollEffects();
        
        // Active link highlighting
        this.highlightActiveLink();
        
        // Close mobile menu on link click
        this.navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    this.closeMobileMenu();
                }
            });
        });
        
        // Handle escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeMobileMenu();
                this.closeAllDropdowns();
            }
        });
        
        // Handle click outside
        document.addEventListener('click', (e) => {
            if (!this.nav.contains(e.target)) {
                this.closeMobileMenu();
                this.closeAllDropdowns();
            }
        });
    }
    
    toggleMobileMenu() {
        const isExpanded = this.navToggle.getAttribute('aria-expanded') === 'true';
        this.navToggle.setAttribute('aria-expanded', !isExpanded);
        
        // Trap focus when menu is open
        if (!isExpanded) {
            this.trapFocus();
        } else {
            this.releaseFocus();
        }
        
        // Prevent body scroll when menu is open
        document.body.style.overflow = !isExpanded ? 'hidden' : '';
    }
    
    closeMobileMenu() {
        if (this.navToggle) {
            this.navToggle.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
            this.releaseFocus();
        }
    }
    
    initDropdowns() {
        this.dropdownToggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleDropdown(toggle);
            });
            
            // Keyboard navigation
            toggle.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.toggleDropdown(toggle);
                }
            });
            
            // Close on focus out
            const dropdown = toggle.parentElement;
            dropdown.addEventListener('focusout', (e) => {
                setTimeout(() => {
                    if (!dropdown.contains(document.activeElement)) {
                        toggle.setAttribute('aria-expanded', 'false');
                    }
                }, 0);
            });
        });
    }
    
    toggleDropdown(toggle) {
        const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
        
        // Close all other dropdowns
        this.closeAllDropdowns();
        
        // Toggle current dropdown
        toggle.setAttribute('aria-expanded', !isExpanded);
    }
    
    closeAllDropdowns() {
        this.dropdownToggles.forEach(toggle => {
            toggle.setAttribute('aria-expanded', 'false');
        });
    }
    
    initScrollEffects() {
        let lastScrollY = window.scrollY;
        let ticking = false;
        
        const updateNav = () => {
            const currentScrollY = window.scrollY;
            
            // Add scrolled class
            if (currentScrollY > 50) {
                this.nav.classList.add('scrolled');
            } else {
                this.nav.classList.remove('scrolled');
            }
            
            // Hide/show on scroll
            if (currentScrollY > lastScrollY && currentScrollY > 100) {
                // Scrolling down
                this.nav.classList.add('hidden');
            } else {
                // Scrolling up
                this.nav.classList.remove('hidden');
            }
            
            lastScrollY = currentScrollY;
            ticking = false;
        };
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(updateNav);
                ticking = true;
            }
        });
    }
    
    highlightActiveLink() {
        const currentPath = window.location.pathname;
        
        this.navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
                link.setAttribute('aria-current', 'page');
            }
        });
    }
    
    trapFocus() {
        const focusableElements = this.navMenu.querySelectorAll(
            'a, button, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        this.handleTabKey = (e) => {
            if (e.key !== 'Tab') return;
            
            if (e.shiftKey) {
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        };
        
        document.addEventListener('keydown', this.handleTabKey);
        firstElement.focus();
    }
    
    releaseFocus() {
        if (this.handleTabKey) {
            document.removeEventListener('keydown', this.handleTabKey);
            this.handleTabKey = null;
        }
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new Navigation());
} else {
    new Navigation();
}

export default Navigation;
```

### 4. Hero Section JavaScript (`static/js/hero.js`)

```javascript
/**
 * Hero Section Module
 * Handles hero animations, parallax effects, and interactions
 */

class HeroSection {
    constructor() {
        this.hero = document.querySelector('.hero');
        this.heroImage = document.querySelector('.hero-image');
        this.heroContent = document.querySelector('.hero-content');
        this.scrollIndicator = document.querySelector('.scroll-indicator');
        
        this.init();
    }
    
    init() {
        if (!this.hero) return;
        
        // Parallax effect
        this.initParallax();
        
        // Animate content on load
        this.animateContent();
        
        // Scroll indicator animation
        this.animateScrollIndicator();
        
        // Lazy load background image
        this.lazyLoadBackground();
    }
    
    initParallax() {
        if (!this.heroImage) return;
        
        let ticking = false;
        
        const updateParallax = () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            
            this.heroImage.style.transform = `translateY(${rate}px)`;
            ticking = false;
        };
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(updateParallax);
                ticking = true;
            }
        });
    }
    
    animateContent() {
        if (!this.heroContent) return;
        
        // Add animation classes
        this.heroContent.classList.add('animate');
        
        // Stagger animations for children
        const elements = this.heroContent.querySelectorAll('.hero-title-line, .hero-subtitle, .hero-actions, .hero-social-proof');
        
        elements.forEach((element, index) => {
            element.style.animationDelay = `${index * 0.1}s`;
            element.classList.add('fade-in-up');
        });
    }
    
    animateScrollIndicator() {
        if (!this.scrollIndicator) return;
        
        // Bounce animation
        this.scrollIndicator.classList.add('bounce');
        
        // Hide on scroll
        let hidden = false;
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 100 && !hidden) {
                this.scrollIndicator.style.opacity = '0';
                hidden = true;
            } else if (window.pageYOffset <= 100 && hidden) {
                this.scrollIndicator.style.opacity = '1';
                hidden = false;
            }
        });
    }
    
    lazyLoadBackground() {
        // Use Intersection Observer for background images
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                });
            });
            
            if (this.heroImage) {
                imageObserver.observe(this.heroImage);
            }
        }
    }
}

// Initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new HeroSection());
} else {
    new HeroSection();
}

export default HeroSection;
```

### 5. Vercel Serverless Function (`api/navigation.js`)

```javascript
/**
 * Navigation API Endpoint
 * Returns navigation menu data and configuration
 */

export default function handler(req, res) {
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    if (req.method !== 'GET') {
        res.status(405).json({ error: 'Method not allowed' });
        return;
    }
    
    // Navigation menu structure
    const navigation = {
        logo: {
            text: 'Sabor con Flow',
            href: '/',
            image: '/static/images/logo.svg'
        },
        items: [
            {
                label: 'Home',
                href: '/',
                active: req.url === '/'
            },
            {
                label: 'Schedule',
                href: '/schedule'
            },
            {
                label: 'Classes',
                href: '#',
                dropdown: true,
                items: [
                    { label: 'Salsa', href: '/classes/salsa' },
                    { label: 'Bachata', href: '/classes/bachata' },
                    { label: 'Private Lessons', href: '/classes/private' }
                ]
            },
            {
                label: 'Instructors',
                href: '/instructors'
            },
            {
                label: 'Events',
                href: '/events'
            },
            {
                label: 'Contact',
                href: '/contact'
            }
        ],
        cta: {
            label: 'Book Now',
            href: '/book',
            style: 'primary'
        },
        mobile: {
            breakpoint: 768,
            animation: 'slide'
        }
    };
    
    res.status(200).json(navigation);
}
```

### 6. Test Suite (`tests/homepage.test.js`)

```javascript
/**
 * Homepage Test Suite
 * Using Vitest for testing
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { JSDOM } from 'jsdom';
import Navigation from '../static/js/navigation.js';
import HeroSection from '../static/js/hero.js';

describe('Navigation Component', () => {
    let dom;
    let document;
    let window;
    let navigation;
    
    beforeEach(() => {
        dom = new JSDOM(`
            <!DOCTYPE html>
            <html>
                <body>
                    <nav class="main-nav">
                        <button class="nav-toggle" aria-expanded="false"></button>
                        <ul class="nav-menu">
                            <li><a href="/" class="nav-link">Home</a></li>
                            <li class="nav-dropdown">
                                <button class="nav-link dropdown-toggle" aria-expanded="false">
                                    Classes
                                </button>
                                <ul class="dropdown-menu">
                                    <li><a href="/classes/salsa">Salsa</a></li>
                                </ul>
                            </li>
                        </ul>
                    </nav>
                </body>
            </html>
        `, { url: 'http://localhost' });
        
        document = dom.window.document;
        window = dom.window;
        global.document = document;
        global.window = window;
        
        navigation = new Navigation();
    });
    
    afterEach(() => {
        vi.restoreAllMocks();
    });
    
    describe('Mobile Menu', () => {
        it('should toggle mobile menu on button click', () => {
            const toggle = document.querySelector('.nav-toggle');
            const initialState = toggle.getAttribute('aria-expanded');
            
            toggle.click();
            
            expect(toggle.getAttribute('aria-expanded')).toBe('true');
            expect(initialState).toBe('false');
        });
        
        it('should close mobile menu on escape key', () => {
            const toggle = document.querySelector('.nav-toggle');
            toggle.click();
            
            const escapeEvent = new window.KeyboardEvent('keydown', { key: 'Escape' });
            document.dispatchEvent(escapeEvent);
            
            expect(toggle.getAttribute('aria-expanded')).toBe('false');
        });
        
        it('should trap focus when mobile menu is open', () => {
            const toggle = document.querySelector('.nav-toggle');
            const spy = vi.spyOn(navigation, 'trapFocus');
            
            toggle.click();
            
            expect(spy).toHaveBeenCalled();
        });
    });
    
    describe('Dropdown Menus', () => {
        it('should toggle dropdown on click', () => {
            const dropdownToggle = document.querySelector('.dropdown-toggle');
            
            dropdownToggle.click();
            
            expect(dropdownToggle.getAttribute('aria-expanded')).toBe('true');
        });
        
        it('should close other dropdowns when opening one', () => {
            // Add second dropdown
            const navMenu = document.querySelector('.nav-menu');
            navMenu.innerHTML += `
                <li class="nav-dropdown">
                    <button class="nav-link dropdown-toggle" aria-expanded="false">
                        Events
                    </button>
                </li>
            `;
            
            navigation.initDropdowns();
            const dropdowns = document.querySelectorAll('.dropdown-toggle');
            
            dropdowns[0].click();
            dropdowns[1].click();
            
            expect(dropdowns[0].getAttribute('aria-expanded')).toBe('false');
            expect(dropdowns[1].getAttribute('aria-expanded')).toBe('true');
        });
    });
    
    describe('Scroll Effects', () => {
        it('should add scrolled class when scrolling down', () => {
            const nav = document.querySelector('.main-nav');
            
            window.scrollY = 100;
            window.dispatchEvent(new Event('scroll'));
            
            // Wait for requestAnimationFrame
            setTimeout(() => {
                expect(nav.classList.contains('scrolled')).toBe(true);
            }, 20);
        });
        
        it('should hide nav when scrolling down past threshold', () => {
            const nav = document.querySelector('.main-nav');
            
            window.scrollY = 200;
            window.dispatchEvent(new Event('scroll'));
            
            setTimeout(() => {
                expect(nav.classList.contains('hidden')).toBe(true);
            }, 20);
        });
    });
    
    describe('Accessibility', () => {
        it('should have proper ARIA attributes', () => {
            const toggle = document.querySelector('.nav-toggle');
            const dropdown = document.querySelector('.dropdown-toggle');
            
            expect(toggle.hasAttribute('aria-expanded')).toBe(true);
            expect(toggle.hasAttribute('aria-controls')).toBe(true);
            expect(dropdown.hasAttribute('aria-haspopup')).toBe(true);
        });
        
        it('should support keyboard navigation', () => {
            const dropdown = document.querySelector('.dropdown-toggle');
            const enterEvent = new window.KeyboardEvent('keydown', { key: 'Enter' });
            
            dropdown.dispatchEvent(enterEvent);
            
            expect(dropdown.getAttribute('aria-expanded')).toBe('true');
        });
    });
});

describe('Hero Section', () => {
    let dom;
    let document;
    let window;
    let hero;
    
    beforeEach(() => {
        dom = new JSDOM(`
            <!DOCTYPE html>
            <html>
                <body>
                    <section class="hero">
                        <img class="hero-image" src="test.jpg" alt="Test">
                        <div class="hero-content">
                            <h1 class="hero-title-line">Test Title</h1>
                            <p class="hero-subtitle">Test Subtitle</p>
                        </div>
                        <button class="scroll-indicator"></button>
                    </section>
                </body>
            </html>
        `);
        
        document = dom.window.document;
        window = dom.window;
        global.document = document;
        global.window = window;
        
        hero = new HeroSection();
    });
    
    it('should apply parallax effect on scroll', () => {
        const heroImage = document.querySelector('.hero-image');
        
        window.pageYOffset = 100;
        window.dispatchEvent(new Event('scroll'));
        
        setTimeout(() => {
            expect(heroImage.style.transform).toContain('translateY');
        }, 20);
    });
    
    it('should animate content on load', () => {
        const heroContent = document.querySelector('.hero-content');
        
        expect(heroContent.classList.contains('animate')).toBe(true);
    });
    
    it('should hide scroll indicator on scroll', () => {
        const scrollIndicator = document.querySelector('.scroll-indicator');
        
        window.pageYOffset = 150;
        window.dispatchEvent(new Event('scroll'));
        
        expect(scrollIndicator.style.opacity).toBe('0');
    });
});
```

### 7. Performance Optimizations

```javascript
// static/js/performance.js
/**
 * Performance monitoring and optimization
 */

class PerformanceMonitor {
    constructor() {
        this.metrics = {};
        this.init();
    }
    
    init() {
        // Web Vitals
        if ('PerformanceObserver' in window) {
            // Largest Contentful Paint
            new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                this.metrics.lcp = lastEntry.renderTime || lastEntry.loadTime;
            }).observe({ entryTypes: ['largest-contentful-paint'] });
            
            // First Input Delay
            new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    this.metrics.fid = entry.processingStart - entry.startTime;
                });
            }).observe({ entryTypes: ['first-input'] });
            
            // Cumulative Layout Shift
            let clsValue = 0;
            new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                        this.metrics.cls = clsValue;
                    }
                }
            }).observe({ entryTypes: ['layout-shift'] });
        }
        
        // Send metrics to analytics
        window.addEventListener('beforeunload', () => {
            this.sendMetrics();
        });
    }
    
    sendMetrics() {
        if (navigator.sendBeacon) {
            navigator.sendBeacon('/api/analytics/performance', JSON.stringify(this.metrics));
        }
    }
}

export default PerformanceMonitor;
```

## Testing Requirements

### Unit Tests
- Navigation component functionality
- Hero section animations
- Dropdown menu behavior
- Mobile menu interactions
- Accessibility features

### Integration Tests
- Navigation state management
- Scroll effects coordination
- Menu interactions with page content
- API endpoint responses

### E2E Tests
```javascript
// tests/e2e/homepage.spec.js
import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
    test('should load and display hero section', async ({ page }) => {
        await page.goto('/');
        await expect(page.locator('.hero')).toBeVisible();
        await expect(page.locator('.hero-title')).toContainText('Feel the Rhythm');
    });
    
    test('should navigate to schedule page', async ({ page }) => {
        await page.goto('/');
        await page.click('text=Schedule');
        await expect(page).toHaveURL('/schedule');
    });
    
    test('should open mobile menu on mobile', async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
        await page.goto('/');
        await page.click('.nav-toggle');
        await expect(page.locator('.nav-menu')).toBeVisible();
    });
    
    test('should be accessible', async ({ page }) => {
        await page.goto('/');
        const accessibilityScanResults = await page.accessibility.snapshot();
        expect(accessibilityScanResults).toBeDefined();
    });
});
```

## Deployment Checklist

- [ ] HTML validation passes
- [ ] CSS validation passes
- [ ] JavaScript linting passes
- [ ] All tests pass
- [ ] Lighthouse score > 90 for all metrics
- [ ] WCAG 2.1 AA compliance verified
- [ ] Cross-browser testing complete
- [ ] Mobile responsiveness verified
- [ ] Performance budget met
- [ ] SEO meta tags in place
- [ ] Open Graph tags configured
- [ ] Analytics tracking implemented
- [ ] Error tracking configured
- [ ] CDN configured for static assets
- [ ] SSL certificate verified

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile Safari iOS 14+
- Chrome Mobile Android 90+

## Performance Targets

- First Contentful Paint: < 1.5s
- Largest Contentful Paint: < 2.5s
- Time to Interactive: < 3.5s
- Cumulative Layout Shift: < 0.1
- First Input Delay: < 100ms
- Total JavaScript size: < 50KB gzipped
- Total CSS size: < 20KB gzipped