# Phase 2: CSS Architecture and Modularization Specification

## Executive Summary

This document provides the complete technical specification for Phase 2 of the Sabor Con Flow
dance website modernization. Phase 2 focuses on decomposing the monolithic 974-line
`public/css/styles.css` into a modular, maintainable CSS architecture following modern best
practices.

**Timeline:** 2 PRs (estimated 2-3 days total)
**Dependencies:** Phase 1 completion (CSS custom properties in `base/variables.css`)
**Risk Level:** Medium - requires careful specificity management during migration

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Target Architecture](#target-architecture)
3. [PR 2.1: CSS Module Structure](#pr-21-css-module-structure)
4. [PR 2.2: Responsive Design Refinements](#pr-22-responsive-design-refinements)
5. [Migration Strategy](#migration-strategy)
6. [Risk Assessment](#risk-assessment)
7. [Verification Checklist](#verification-checklist)

---

## Current State Analysis

### File Statistics

| Metric | Value |
|--------|-------|
| Total lines | 974 |
| CSS rules | ~180 rule sets |
| Media queries | 6 breakpoints |
| Color declarations | 47 (rgb(191, 170, 101)) |
| Font-family declarations | 14 (Playfair Display) |

### Current Breakpoints Identified

| Breakpoint | Lines | Usage |
|------------|-------|-------|
| `max-width: 1000px` | 565-569 | Event grid 3 to 2 columns |
| `max-width: 768px` | 277-286, 571-578, 711-716, 951-974 | Mobile layouts |
| `max-width: 600px` | 580-587 | Small mobile event grid |

### CSS Sections Analysis

The monolithic file contains the following logical sections:

| Section | Lines | Category | Target Module |
|---------|-------|----------|---------------|
| Hamburger Menu | 1-35 | Component | `components/navigation.css` |
| Navigation Sidebar | 36-95 | Component | `components/navigation.css` |
| Dark Theme Base | 97-116 | Base | `base/reset.css` |
| Header | 117-149 | Layout | `layouts/sections.css` |
| Footer | 151-193 | Layout | `layouts/sections.css` |
| Tagline | 195-208 | Component | `components/typography.css` |
| Dual Video Container | 210-286 | Component | `components/gallery.css` |
| Dance Gallery | 288-354 | Component | `components/gallery.css` |
| Pasos Animation | 356-397 | Component | `components/gallery.css` |
| CTA Section | 399-463 | Component | `components/cards.css` |
| Events Page | 465-587 | Component | `components/cards.css` |
| Pricing Table | 589-637 | Component | `components/cards.css` |
| Contact Section | 639-700 | Component | `components/cards.css` |
| Pricing Layout | 702-716 | Layout | `layouts/sections.css` |
| Private Lessons | 718-747 | Component | `components/cards.css` |
| About Page | 749-948 | Component/Layout | Multiple |
| About Responsive | 950-974 | Component | Multiple |

### CSS Specificity Map

Current maximum specificity scores (class-based):

- `.nav.active a` - Specificity: 0-3-0
- `.gallery-item:hover .gallery-overlay` - Specificity: 0-3-0
- `.event-description p a` - Specificity: 0-2-2
- `.contact-item .contact-link` - Specificity: 0-2-0
- `.benefits-list li:before` - Specificity: 0-2-1

**Risk:** Split files must maintain import order to preserve cascade behavior.

---

## Target Architecture

### Directory Structure

```text
public/css/
├── base/
│   ├── variables.css      # (from Phase 1 - CSS custom properties)
│   ├── reset.css          # Box model, body defaults, accessibility
│   └── typography.css     # Font declarations, text utilities
├── components/
│   ├── buttons.css        # .btn, .btn-primary, .btn-secondary
│   ├── cards.css          # Event cards, CTA, pricing, contact, mission
│   ├── navigation.css     # .menu-toggle, .nav, header, footer
│   └── gallery.css        # .gallery-*, .video-*, .pasos-*
├── layouts/
│   ├── grid.css           # Grid systems, .event-container, .mission-grid
│   └── sections.css       # Page sections, .main-content, about-page
└── main.css               # @import orchestrator (replaces styles.css)
```

### Import Dependency Order

```css
/* main.css - Load order is critical */
@import 'base/variables.css';    /* 1. CSS Custom Properties */
@import 'base/reset.css';        /* 2. Reset and base styles */
@import 'base/typography.css';   /* 3. Typography foundation */
@import 'layouts/grid.css';      /* 4. Grid systems */
@import 'layouts/sections.css';  /* 5. Section layouts */
@import 'components/buttons.css';     /* 6. Buttons */
@import 'components/navigation.css';  /* 7. Navigation */
@import 'components/cards.css';       /* 8. Card components */
@import 'components/gallery.css';     /* 9. Gallery components */
```

---

## PR 2.1: CSS Module Structure

### Overview

**Branch:** `feature/css-modularization`
**Files Changed:** 1 deleted, 10 created
**Risk:** Medium - visual regression possible if import order incorrect

### File Contents

#### 1. `public/css/base/reset.css`

```css
/**
 * Reset and Base Styles
 * Sabor Con Flow Dance Studio
 *
 * Provides consistent cross-browser defaults and accessibility foundations.
 * Dependencies: variables.css must be loaded first.
 */

/* ============================================
   Box Model Reset
   ============================================ */

*,
*::before,
*::after {
  box-sizing: border-box;
}

/* ============================================
   Document Defaults
   ============================================ */

html {
  height: 100%;
  scroll-behavior: smooth;
  -webkit-text-size-adjust: 100%;
}

body {
  background-color: var(--color-background);
  color: var(--color-text-primary);
  min-height: 100%;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
  font-family: var(--font-family-body);
  line-height: var(--line-height-base);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ============================================
   Element Resets
   ============================================ */

h1, h2, h3, h4, h5, h6 {
  margin: 0;
  font-weight: var(--font-weight-bold);
}

p {
  margin: 0 0 1rem 0;
}

ul, ol {
  margin: 0;
  padding: 0;
}

a {
  color: inherit;
  text-decoration: none;
}

img {
  max-width: 100%;
  height: auto;
  display: block;
}

button {
  font: inherit;
  cursor: pointer;
  border: none;
  background: none;
}

/* ============================================
   Accessibility
   ============================================ */

:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

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

/* Reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

**Line mapping from original:**
- Lines 98-100 (html height) -> Document Defaults
- Lines 102-110 (body) -> Document Defaults

---

#### 2. `public/css/base/typography.css`

```css
/**
 * Typography Styles
 * Sabor Con Flow Dance Studio
 *
 * Establishes typographic scale and text styling utilities.
 * Dependencies: variables.css, reset.css
 */

/* ============================================
   Heading Styles
   ============================================ */

.page-title {
  font-size: clamp(2rem, 5vw, 3rem);
  margin-bottom: 2rem;
  text-align: center;
  color: var(--color-accent);
  font-family: var(--font-family-heading);
}

.page-subtitle {
  font-size: 1.3rem;
  color: var(--color-accent-muted);
  font-style: italic;
  margin: 0;
}

.section-title {
  color: var(--color-accent);
  font-family: var(--font-family-heading);
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  text-align: center;
  margin-bottom: 2rem;
}

/* ============================================
   Tagline Styles
   ============================================ */

.tagline-container {
  margin-top: 1rem;
  text-align: center;
  margin-bottom: 2rem;
}

.tagline {
  color: var(--color-accent);
  font-family: var(--font-family-heading);
  font-size: 1.5rem;
  margin-top: 1rem;
  margin-bottom: 1.5rem;
  font-style: italic;
}

/* ============================================
   Animation Section Typography
   ============================================ */

.animation-title {
  color: var(--color-accent);
  font-family: var(--font-family-heading);
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  margin-bottom: 1rem;
}

.animation-subtitle {
  color: var(--color-text-primary);
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
  font-style: italic;
}

/* ============================================
   Instructor Typography
   ============================================ */

.instructor-title {
  color: var(--color-accent);
  font-family: var(--font-family-heading);
  font-size: 2.2rem;
  margin-bottom: 1.5rem;
}

.instructor-bio p {
  color: var(--color-text-primary);
  font-size: 1.1rem;
  line-height: 1.7;
  margin-bottom: 1.5rem;
}

/* ============================================
   Pricing Typography
   ============================================ */

.pricing-heading {
  color: var(--color-accent);
  font-family: var(--font-family-heading);
  margin: 1.25rem 0 0.5rem;
  font-size: 1.5rem;
  text-align: center;
}

.pricing-description {
  margin-bottom: 0.5rem;
  color: var(--color-text-primary);
  font-size: 0.95rem;
  text-align: center;
}

.pricing-note {
  margin-top: 0.75rem;
  font-size: 0.9rem;
  color: var(--color-text-primary);
  opacity: 0.9;
  text-align: center;
}

/* ============================================
   Contact Typography
   ============================================ */

.contact-title {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--color-accent);
}

/* ============================================
   Link Styles
   ============================================ */

.instagram-link {
  color: var(--color-accent);
  text-decoration: none;
  font-style: italic;
  transition: color var(--transition-duration) ease;
}

.instagram-link:hover {
  color: var(--color-accent-muted);
  text-decoration: underline;
}

.contact-link {
  color: var(--color-accent);
  text-decoration: none;
}

.contact-link:hover {
  text-decoration: underline;
}
```

**Line mapping from original:**
- Lines 195-208 (tagline) -> Tagline Styles
- Lines 364-377 (animation titles) -> Animation Section Typography
- Lines 473-479, 761-772 (page-title, page-subtitle) -> Heading Styles
- Lines 616-637 (pricing typography) -> Pricing Typography
- Lines 648-652, 679-686 (contact typography) -> Contact Typography
- Lines 806-818, 841-851 (instructor, instagram) -> Instructor/Link Styles
- Lines 853-858 (section-title) -> Heading Styles

---

#### 3. `public/css/components/buttons.css`

```css
/**
 * Button Styles
 * Sabor Con Flow Dance Studio
 *
 * Provides consistent button styling throughout the application.
 * Dependencies: variables.css
 */

/* ============================================
   Base Button
   ============================================ */

.btn {
  display: inline-block;
  padding: 1rem 2rem;
  text-decoration: none;
  border-radius: var(--radius-md);
  font-weight: var(--font-weight-semibold);
  font-size: 1rem;
  transition: all var(--transition-duration) ease;
  border: 2px solid transparent;
  cursor: pointer;
  text-align: center;
  min-height: 44px; /* Touch target minimum */
  min-width: 44px;
}

.btn:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* ============================================
   Primary Button
   ============================================ */

.btn-primary {
  background-color: var(--color-accent);
  color: var(--color-background);
  border-color: var(--color-accent);
}

.btn-primary:hover {
  background-color: transparent;
  color: var(--color-accent);
  border-color: var(--color-accent);
}

/* ============================================
   Secondary Button
   ============================================ */

.btn-secondary {
  background-color: transparent;
  color: var(--color-accent);
  border-color: var(--color-accent);
}

.btn-secondary:hover {
  background-color: var(--color-accent);
  color: var(--color-background);
}

/* ============================================
   Button Containers
   ============================================ */

.cta-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* ============================================
   Special Buttons
   ============================================ */

.whatsapp-button {
  display: inline-block;
  background-color: var(--color-accent);
  color: var(--color-background);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  text-decoration: none;
  margin-top: 1rem;
  min-height: 44px;
  line-height: calc(44px - 1rem);
}

.whatsapp-button:hover {
  background-color: var(--color-accent-muted);
}
```

**Line mapping from original:**
- Lines 424-463 (btn, btn-primary, btn-secondary) -> Button styles
- Lines 688-700 (whatsapp-button) -> Special Buttons

---

#### 4. `public/css/components/cards.css`

```css
/**
 * Card Components
 * Sabor Con Flow Dance Studio
 *
 * Provides card-based UI components for events, pricing, and content sections.
 * Dependencies: variables.css, grid.css
 */

/* ============================================
   CTA Section
   ============================================ */

.cta-section {
  text-align: center;
  margin: 4rem auto;
  max-width: 600px;
  padding: 3rem 2rem;
  background: var(--gradient-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-accent-transparent);
}

.cta-section h2 {
  color: var(--color-accent);
  font-family: var(--font-family-heading);
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  margin-bottom: 1rem;
}

.cta-section p {
  color: var(--color-text-primary);
  font-size: 1.1rem;
  margin-bottom: 2rem;
  line-height: 1.6;
}

/* ============================================
   Event Cards
   ============================================ */

.event-card {
  background-color: var(--color-background);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  border-top: 4px solid var(--color-accent);
  display: flex;
  flex-direction: column;
  color: var(--color-accent);
}

.event-title {
  font-size: 1.5rem;
  font-weight: var(--font-weight-bold);
  margin-bottom: 0.5rem;
  color: var(--color-accent);
  font-family: var(--font-family-heading);
}

.event-date,
.event-time,
.event-location {
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  color: var(--color-accent);
}

.event-location a {
  color: var(--color-accent);
  text-decoration: none;
}

.event-location a:hover {
  text-decoration: underline;
}

.event-icon {
  width: 18px;
  height: 18px;
  margin-right: 0.5rem;
  display: inline-block;
}

.event-description {
  margin: 1rem 0;
  flex-grow: 1;
  color: var(--color-text-primary);
}

.event-description p a {
  color: var(--color-accent);
  text-decoration: none;
}

.event-description p a:hover {
  text-decoration: underline;
}

/* ============================================
   Event Pricing
   ============================================ */

.event-pricing {
  background-color: var(--color-accent-bg);
  padding: 1rem;
  border-radius: var(--radius-sm);
  margin-top: 1rem;
}

.event-pricing h3 {
  color: var(--color-accent);
  margin-top: 0;
  font-size: 1.1rem;
  font-family: var(--font-family-heading);
}

.event-pricing ul {
  margin: 0.5rem 0 0;
  padding-left: 1.5rem;
  color: var(--color-accent);
}

/* ============================================
   Pricing Tables
   ============================================ */

.pricing-table {
  width: 100%;
  max-width: 600px;
  margin: 2rem auto;
  border-collapse: collapse;
  background-color: var(--color-background);
}

.pricing-table th {
  background-color: var(--color-accent-bg);
  font-weight: bold;
  color: var(--color-accent);
  border: 1px solid var(--color-accent);
  padding: 1rem;
}

.pricing-table td {
  padding: 1rem;
  text-align: left;
  border: 1px solid var(--color-accent);
  color: var(--color-text-primary);
}

.pricing-table tr:hover {
  background-color: var(--color-accent-hover);
}

/* ============================================
   Contact Components
   ============================================ */

.contact-section {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  background-color: var(--color-background);
  text-align: center;
}

.contact-item {
  margin-bottom: 1.5rem;
  color: var(--color-text-primary);
  text-align: center;
}

.contact-item p {
  margin: 0;
  line-height: 1.5;
}

.contact-item .contact-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  justify-content: center;
}

.contact-icon {
  color: var(--color-accent);
  display: inline-flex;
  align-items: center;
}

/* ============================================
   Mission Cards
   ============================================ */

.mission-item {
  background: var(--color-accent-bg);
  padding: 2rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-accent-transparent);
  text-align: center;
}

.mission-item h3 {
  color: var(--color-accent);
  font-family: var(--font-family-heading);
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.mission-item p {
  color: var(--color-text-primary);
  line-height: 1.6;
  margin: 0;
}

/* ============================================
   Class Preview Cards
   ============================================ */

.class-preview {
  background: var(--color-surface);
  padding: 2rem;
  border-radius: var(--radius-md);
  border-left: 4px solid var(--color-accent);
  transition: transform var(--transition-duration) ease;
}

.class-preview:hover {
  transform: translateY(-3px);
}

.class-preview h3 {
  color: var(--color-accent);
  font-family: var(--font-family-heading);
  font-size: 1.4rem;
  margin-bottom: 1rem;
}

.class-preview p {
  color: var(--color-text-primary);
  line-height: 1.6;
  margin: 0;
}

/* ============================================
   About CTA
   ============================================ */

.about-cta {
  text-align: center;
  background: var(--gradient-card);
  padding: 3rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-accent-transparent);
}

.about-cta h2 {
  color: var(--color-accent);
  font-family: var(--font-family-heading);
  font-size: 2.2rem;
  margin-bottom: 1rem;
}

.about-cta p {
  color: var(--color-text-primary);
  font-size: 1.2rem;
  margin-bottom: 2rem;
}

/* ============================================
   Private Lessons Info
   ============================================ */

.private-lessons-info {
  margin: 2rem 0;
  text-align: left;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.benefits-list {
  list-style: none;
  padding: 0;
  margin: 1rem 0;
}

.benefits-list li {
  padding: 0.5rem 0;
  position: relative;
  padding-left: 2rem;
  color: var(--color-text-primary);
}

.benefits-list li::before {
  content: "\2713"; /* Checkmark */
  position: absolute;
  left: 0;
  color: var(--color-accent);
  font-weight: bold;
  font-size: 1.2rem;
}

/* ============================================
   Influences List
   ============================================ */

.influences-list {
  list-style: none;
  padding: 0;
  margin: 1.5rem 0;
}

.influences-list li {
  color: var(--color-text-primary);
  font-size: 1.1rem;
  margin-bottom: 1rem;
  padding-left: 2rem;
  position: relative;
}

.influences-list li::before {
  content: "\1F3B5"; /* Music note emoji */
  position: absolute;
  left: 0;
  font-size: 1.2rem;
}

/* ============================================
   Card Responsive Adjustments
   ============================================ */

@media (max-width: 768px) {
  .pricing-table {
    width: 100%;
    font-size: 0.9rem;
  }

  .pricing-table th,
  .pricing-table td {
    padding: 0.75rem;
  }
}
```

**Line mapping from original:**
- Lines 399-422 (cta-section) -> CTA Section
- Lines 488-563 (event cards, pricing) -> Event Cards, Event Pricing
- Lines 589-614 (pricing-table) -> Pricing Tables
- Lines 639-686 (contact) -> Contact Components
- Lines 718-747 (private-lessons, benefits-list) -> Private Lessons Info
- Lines 820-839 (influences-list) -> Influences List
- Lines 861-891 (mission-item) -> Mission Cards
- Lines 893-927 (class-preview) -> Class Preview Cards
- Lines 929-948 (about-cta) -> About CTA

---

#### 5. `public/css/components/navigation.css`

```css
/**
 * Navigation Styles
 * Sabor Con Flow Dance Studio
 *
 * Provides hamburger menu, sidebar navigation, header, and footer styling.
 * Dependencies: variables.css
 */

/* ============================================
   Hamburger Menu Toggle
   ============================================ */

.menu-toggle {
  display: block;
  background: none;
  border: none;
  cursor: pointer;
  padding: 10px;
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: var(--z-modal);
  transition: transform var(--transition-duration) ease;
  min-height: 44px; /* Touch target */
  min-width: 44px;
}

.menu-toggle span {
  display: block;
  width: 25px;
  height: 3px;
  background-color: var(--color-accent);
  margin: 5px 0;
  transition: 0.4s;
}

/* Hamburger Animation - Active State */
.menu-toggle.active span:nth-child(1) {
  transform: rotate(-45deg) translate(-5px, 6px);
}

.menu-toggle.active span:nth-child(2) {
  opacity: 0;
}

.menu-toggle.active span:nth-child(3) {
  transform: rotate(45deg) translate(-5px, -6px);
}

/* ============================================
   Sidebar Navigation
   ============================================ */

.nav {
  display: block;
  position: fixed;
  top: 0;
  left: -250px;
  width: 250px;
  height: 100vh;
  background-color: var(--color-nav-bg);
  padding: 80px 20px 20px;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.2);
  transition: left var(--transition-duration) ease;
  z-index: var(--z-dropdown);
}

.nav.active {
  left: 0;
}

/* ============================================
   Navigation Links
   ============================================ */

.nav a {
  display: block;
  margin: 15px 0;
  color: var(--color-accent);
  text-decoration: none;
  font-size: 1.2rem;
  opacity: 0;
  transform: translateX(-20px);
  transition: all var(--transition-duration) ease;
  min-height: 44px; /* Touch target */
  line-height: 44px;
}

.nav.active a {
  opacity: 1;
  transform: translateX(0);
}

/* Staggered animation delays */
.nav a:nth-child(1) { transition-delay: 0.1s; }
.nav a:nth-child(2) { transition-delay: 0.2s; }
.nav a:nth-child(3) { transition-delay: 0.3s; }
.nav a:nth-child(4) { transition-delay: 0.4s; }
.nav a:nth-child(5) { transition-delay: 0.5s; }

/* ============================================
   Navigation Link Underline Effect
   ============================================ */

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
  background-color: var(--color-accent);
  transition: width var(--transition-duration) ease;
}

.nav a:hover span::after {
  width: 100%;
}

/* ============================================
   Header
   ============================================ */

.header {
  background-color: var(--color-background);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: var(--z-sticky);
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

/* ============================================
   Header Logo
   ============================================ */

.header-logo-link {
  position: fixed;
  top: 10px;
  right: 20px;
  z-index: var(--z-modal);
  text-decoration: none;
  transition: transform var(--transition-duration) ease;
}

.header-logo-link:hover {
  transform: scale(1.05);
}

.header-logo {
  height: 40px;
  width: auto;
  object-fit: contain;
}

/* ============================================
   Footer
   ============================================ */

.footer {
  background-color: var(--color-background);
  border-top: 1px solid var(--color-accent);
  padding: 20px 0;
  margin-top: auto;
}

.footer h3,
.footer p,
.footer a {
  color: var(--color-accent);
}

/* ============================================
   Social Links
   ============================================ */

.social-links {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 3rem;
}

.social-link {
  color: var(--color-accent);
  transition: all var(--transition-duration) ease;
  display: inline-block;
  text-decoration: none !important;
  border: none !important;
  outline: none !important;
  min-height: 44px; /* Touch target */
  min-width: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.social-link:hover {
  text-decoration: none !important;
  border: none !important;
  outline: none !important;
}

.social-link svg {
  width: 36px;
  height: 36px;
  transition: transform var(--transition-duration) ease;
}

.social-link:hover svg {
  transform: scale(1.2);
}
```

**Line mapping from original:**
- Lines 1-35 (menu-toggle) -> Hamburger Menu Toggle
- Lines 36-95 (nav, nav links) -> Sidebar Navigation, Navigation Links
- Lines 117-149 (header, header-logo) -> Header
- Lines 151-193 (footer, social-links) -> Footer, Social Links

---

#### 6. `public/css/components/gallery.css`

```css
/**
 * Gallery Styles
 * Sabor Con Flow Dance Studio
 *
 * Provides video galleries, image galleries, and animation sections.
 * Dependencies: variables.css
 */

/* ============================================
   Dual Video Container
   ============================================ */

.dual-video-container {
  display: flex;
  gap: 2rem;
  max-width: 1000px;
  margin: 3rem auto;
  padding: 0 2rem;
  align-items: flex-start;
}

.video-item {
  position: relative;
  flex: 1;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  transition: transform var(--transition-duration) ease,
              box-shadow var(--transition-duration) ease;
}

.video-item:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-glow);
}

.side-video {
  width: 100%;
  height: auto;
  display: block;
  object-fit: cover;
}

.gif-video {
  height: auto;
  object-fit: cover;
}

/* ============================================
   Video Overlay
   ============================================ */

.video-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--gradient-overlay);
  color: var(--color-text-primary);
  padding: 1.5rem;
  text-align: center;
  opacity: 0;
  transition: opacity var(--transition-duration) ease;
}

.video-item:hover .video-overlay {
  opacity: 1;
}

.video-overlay h3 {
  color: var(--color-accent);
  font-family: var(--font-family-heading);
  font-size: 1.4rem;
  margin: 0 0 0.5rem 0;
}

.video-overlay p {
  margin: 0;
  font-size: 1rem;
  opacity: 0.9;
}

/* ============================================
   Dance Gallery
   ============================================ */

.dance-gallery {
  margin: 4rem auto;
  max-width: 1200px;
  padding: 0 2rem;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.gallery-item {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  transition: transform var(--transition-duration) ease,
              box-shadow var(--transition-duration) ease;
  height: auto;
}

.gallery-item:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-glow);
}

.gallery-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-duration) ease;
}

.gallery-item:hover .gallery-image {
  transform: scale(1.05);
}

/* ============================================
   Gallery Overlay
   ============================================ */

.gallery-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--gradient-overlay);
  color: var(--color-text-primary);
  padding: 2rem 1.5rem 1.5rem;
  transform: translateY(100%);
  transition: transform var(--transition-duration) ease;
}

.gallery-item:hover .gallery-overlay {
  transform: translateY(0);
}

.gallery-overlay h3 {
  color: var(--color-accent);
  font-family: var(--font-family-heading);
  font-size: 1.3rem;
  margin: 0 0 0.5rem 0;
}

.gallery-overlay p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.9;
}

/* ============================================
   Pasos Basicos Animation Section
   ============================================ */

.pasos-animation-section {
  text-align: center;
  margin: 4rem auto;
  max-width: 800px;
  padding: 2rem;
}

.animation-container {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}

.pasos-animation {
  max-width: 100%;
  width: auto;
  height: auto;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  transition: transform var(--transition-duration) ease,
              box-shadow var(--transition-duration) ease;
}

.pasos-animation:hover {
  transform: scale(1.02);
  box-shadow: var(--shadow-glow);
}

/* ============================================
   Instructor Photo
   ============================================ */

.instructor-photo {
  flex: 0 0 300px;
}

.profile-image {
  width: 100%;
  height: auto;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  transition: transform var(--transition-duration) ease;
}

.profile-image:hover {
  transform: scale(1.02);
}

/* ============================================
   Gallery Responsive
   ============================================ */

@media (max-width: 768px) {
  .dual-video-container {
    flex-direction: column;
    gap: 1.5rem;
  }

  .side-video,
  .gif-video {
    height: 250px;
  }

  .gallery-grid {
    grid-template-columns: 1fr;
  }

  .instructor-photo {
    flex: none;
    max-width: 300px;
    margin: 0 auto;
  }
}
```

**Line mapping from original:**
- Lines 210-286 (dual-video-container, video-item, video-overlay) -> Dual Video, Video Overlay
- Lines 288-354 (dance-gallery, gallery-grid, gallery-item, gallery-overlay) -> Dance Gallery
- Lines 356-397 (pasos-animation-section) -> Pasos Animation Section
- Lines 786-800 (instructor-photo, profile-image) -> Instructor Photo
- Lines 277-286 (video responsive) -> Gallery Responsive

---

#### 7. `public/css/layouts/grid.css`

```css
/**
 * Grid Systems
 * Sabor Con Flow Dance Studio
 *
 * Provides grid layouts for content organization.
 * Dependencies: variables.css
 */

/* ============================================
   Event Container Grid
   ============================================ */

.event-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* ============================================
   Mission Grid
   ============================================ */

.mission-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

/* ============================================
   Classes Grid
   ============================================ */

.classes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

/* ============================================
   Instructor Content Grid
   ============================================ */

.instructor-content {
  display: flex;
  gap: 3rem;
  align-items: flex-start;
  margin-bottom: 3rem;
}

.instructor-info {
  flex: 1;
}

/* ============================================
   Grid Responsive Adjustments
   ============================================ */

@media (max-width: 1000px) {
  .event-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .event-container {
    grid-template-columns: repeat(2, 1fr);
  }

  .mission-grid,
  .classes-grid {
    grid-template-columns: 1fr;
  }

  .instructor-content {
    flex-direction: column;
    gap: 2rem;
  }
}

@media (max-width: 600px) {
  .event-container {
    grid-template-columns: 1fr;
  }
}
```

**Line mapping from original:**
- Lines 481-486 (event-container) -> Event Container Grid
- Lines 565-569, 571-578, 580-587 (event responsive) -> Grid Responsive
- Lines 865-870 (mission-grid) -> Mission Grid
- Lines 897-902 (classes-grid) -> Classes Grid
- Lines 779-804 (instructor-content, instructor-info) -> Instructor Content Grid
- Lines 960-963, 971-972 (responsive grids) -> Grid Responsive

---

#### 8. `public/css/layouts/sections.css`

```css
/**
 * Section Layouts
 * Sabor Con Flow Dance Studio
 *
 * Provides page sections and content containers.
 * Dependencies: variables.css, grid.css
 */

/* ============================================
   Main Content Areas
   ============================================ */

.main-content {
  flex-grow: 1;
  padding-top: 70px;
}

.main-content-events {
  width: 100%;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding-top: 4rem;
}

.main-content-pricing {
  width: 90%;
  max-width: 1000px;
  min-width: 300px;
  margin-left: auto;
  margin-right: auto;
  padding: 4rem 1rem;
}

/* ============================================
   About Page Layout
   ============================================ */

.about-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  text-align: center;
  margin-bottom: 4rem;
}

/* ============================================
   Content Sections
   ============================================ */

.instructor-section {
  margin-bottom: 5rem;
}

.mission-section {
  margin-bottom: 5rem;
}

.classes-overview {
  margin-bottom: 5rem;
}

/* ============================================
   Logo Container (Homepage)
   ============================================ */

.logo-container {
  margin-top: 15vh;
  text-align: center;
}

/* ============================================
   Section Responsive Adjustments
   ============================================ */

@media (max-width: 768px) {
  .main-content-pricing {
    width: 95%;
    padding: 3rem 0.5rem;
  }

  .about-page {
    padding: 1rem;
  }

  .logo-container {
    margin-top: 10vh;
  }
}

@media (max-width: 600px) {
  .logo-container {
    margin-top: 8vh;
  }
}
```

**Line mapping from original:**
- Lines 112-115 (main-content) -> Main Content Areas
- Lines 465-471 (main-content-events) -> Main Content Areas
- Lines 702-716 (main-content-pricing) -> Main Content Areas
- Lines 749-758 (about-page, page-header) -> About Page Layout
- Lines 775-777, 861-863, 893-895 (sections) -> Content Sections
- Lines 572-574, 580-583 (logo-container responsive) -> Responsive

---

#### 9. `public/css/main.css`

```css
/**
 * Main Stylesheet - Import Orchestrator
 * Sabor Con Flow Dance Studio
 *
 * This file imports all CSS modules in the correct dependency order.
 * IMPORTANT: Do not change the import order - it affects CSS cascade.
 *
 * Architecture:
 * 1. Base - Variables, reset, typography (lowest specificity)
 * 2. Layouts - Grid systems and section structures
 * 3. Components - UI components (highest specificity)
 */

/* ============================================
   Base Layer
   ============================================ */
@import 'base/variables.css';
@import 'base/reset.css';
@import 'base/typography.css';

/* ============================================
   Layout Layer
   ============================================ */
@import 'layouts/grid.css';
@import 'layouts/sections.css';

/* ============================================
   Component Layer
   ============================================ */
@import 'components/buttons.css';
@import 'components/navigation.css';
@import 'components/cards.css';
@import 'components/gallery.css';
```

---

### HTML Link Tag Update

Replace in layout template:

```html
<!-- BEFORE -->
<link rel="stylesheet" href="/css/styles.css">

<!-- AFTER -->
<link rel="stylesheet" href="/css/main.css">
```

---

### CSS Custom Properties Required (from Phase 1)

The following variables must exist in `base/variables.css`:

```css
:root {
  /* Colors */
  --color-accent: rgb(191, 170, 101);
  --color-accent-muted: rgba(191, 170, 101, 0.8);
  --color-accent-bg: rgba(191, 170, 101, 0.1);
  --color-accent-hover: rgba(191, 170, 101, 0.05);
  --color-accent-transparent: rgba(191, 170, 101, 0.2);
  --color-background: #000;
  --color-surface: rgba(0, 0, 0, 0.5);
  --color-nav-bg: rgba(0, 0, 0, 0.95);
  --color-text-primary: #ffffff;

  /* Typography */
  --font-family-heading: 'Playfair Display', serif;
  --font-family-body: system-ui, -apple-system, sans-serif;
  --font-weight-bold: 700;
  --font-weight-semibold: 600;
  --line-height-base: 1.5;

  /* Spacing - defined in Phase 1 */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;
  --spacing-3xl: 4rem;

  /* Border Radius */
  --radius-sm: 5px;
  --radius-md: 8px;
  --radius-lg: 15px;

  /* Shadows */
  --shadow-md: 0 8px 25px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 15px 35px rgba(0, 0, 0, 0.3);
  --shadow-glow: 0 20px 40px rgba(191, 170, 101, 0.2);

  /* Gradients */
  --gradient-overlay: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  --gradient-card: linear-gradient(135deg, rgba(191, 170, 101, 0.1), rgba(191, 170, 101, 0.05));

  /* Z-Index Scale */
  --z-dropdown: 999;
  --z-sticky: 998;
  --z-modal: 1000;

  /* Transitions */
  --transition-duration: 0.3s;
}
```

---

## PR 2.2: Responsive Design Refinements

### Overview

**Branch:** `feature/responsive-refinements`
**Files Changed:** Multiple component files
**Depends On:** PR 2.1 merged

### Breakpoint System

Standardize breakpoints across all files:

```css
/* In base/variables.css - add these */
:root {
  /* Breakpoints (for documentation - CSS can't use custom props in media queries) */
  /* --breakpoint-sm: 480px;  Small mobile */
  /* --breakpoint-md: 768px;  Tablet */
  /* --breakpoint-lg: 1000px; Desktop */
  /* --breakpoint-xl: 1200px; Large desktop */
}

/*
  Breakpoint Usage Guide:
  - max-width: 480px  - Small mobile phones
  - max-width: 768px  - Tablets and large phones
  - max-width: 1000px - Small desktops
  - max-width: 1200px - Standard desktops
*/
```

### Mobile-First Refactoring

Current styles use desktop-first (`max-width`). For PR 2.2, consider gradual migration
to mobile-first (`min-width`) in future phases. For now, standardize existing patterns.

### Touch Target Compliance

All interactive elements must have minimum 44x44px touch targets:

| Element | Current Size | Target | Status |
|---------|--------------|--------|--------|
| `.menu-toggle` | ~45x45px | 44px min | Compliant |
| `.btn` | Variable | 44px min-height | Updated |
| `.nav a` | Variable | 44px line-height | Updated |
| `.social-link` | 36x36px | 44x44px | Updated |
| `.gallery-item` | Large | N/A | Compliant |

### Responsive Refinements by Component

#### Navigation Touch Targets

```css
/* In components/navigation.css - ensure these exist */
.menu-toggle {
  min-height: 44px;
  min-width: 44px;
}

.nav a {
  min-height: 44px;
  line-height: 44px;
}

.social-link {
  min-height: 44px;
  min-width: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

#### Grid Responsive Consistency

Ensure all grids follow the same breakpoint pattern:

```css
/* In layouts/grid.css */
@media (max-width: 1000px) {
  /* 3-column to 2-column */
}

@media (max-width: 768px) {
  /* 2-column to 1-column for some grids */
}

@media (max-width: 600px) {
  /* All grids to 1-column */
}
```

---

## Migration Strategy

### Step-by-Step Process

#### Step 1: Create Directory Structure

```bash
mkdir -p public/css/base
mkdir -p public/css/components
mkdir -p public/css/layouts
```

#### Step 2: Copy Existing File as Backup

```bash
cp public/css/styles.css public/css/styles.css.backup
```

#### Step 3: Create New Files (Empty)

```bash
touch public/css/base/reset.css
touch public/css/base/typography.css
touch public/css/components/buttons.css
touch public/css/components/cards.css
touch public/css/components/navigation.css
touch public/css/components/gallery.css
touch public/css/layouts/grid.css
touch public/css/layouts/sections.css
touch public/css/main.css
```

#### Step 4: Populate Files

Copy content from this specification into each file in this order:

1. `base/reset.css`
2. `base/typography.css`
3. `layouts/grid.css`
4. `layouts/sections.css`
5. `components/buttons.css`
6. `components/navigation.css`
7. `components/cards.css`
8. `components/gallery.css`
9. `main.css`

#### Step 5: Update HTML Reference

In `views/layout.ejs`, change:

```html
<link rel="stylesheet" href="/css/main.css">
```

#### Step 6: Visual Regression Testing

1. Start local server: `npm start`
2. Visit each page and compare against backup
3. Use browser DevTools to inspect computed styles
4. Check responsive breakpoints at 1000px, 768px, 600px

#### Step 7: Delete Backup After Verification

```bash
rm public/css/styles.css.backup
rm public/css/styles.css
```

---

## Risk Assessment

### High Priority Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Cascade order broken | High | Medium | Strict import order in main.css |
| Specificity conflicts | Medium | Medium | Test each component independently |
| Missing styles | High | Low | Line-by-line mapping verification |
| Browser @import perf | Low | Low | Consider build step in future |

### Specificity Analysis

Current highest specificity patterns that must be preserved:

```text
.nav.active a                    -> 0-3-0 (navigation.css)
.gallery-item:hover .gallery-overlay -> 0-3-0 (gallery.css)
.event-description p a           -> 0-2-2 (cards.css)
.menu-toggle.active span:nth-child(1) -> 0-3-1 (navigation.css)
```

**Mitigation:** Keep related selectors in the same file to maintain cascade relationships.

### Browser Support for @import

| Browser | Support |
|---------|---------|
| Chrome 1+ | Full |
| Firefox 1+ | Full |
| Safari 1+ | Full |
| Edge 12+ | Full |
| IE 5.5+ | Full |

**Note:** @import has minor performance implications (sequential loading). Consider PostCSS
or build tool concatenation for production optimization in future phases.

---

## Verification Checklist

### PR 2.1 Checklist

- [ ] All 9 CSS files created with correct content
- [ ] `main.css` imports in correct order
- [ ] HTML references updated to `main.css`
- [ ] No 404 errors for CSS files
- [ ] Homepage renders correctly
- [ ] Events page renders correctly
- [ ] Pricing page renders correctly
- [ ] Private Lessons page renders correctly
- [ ] About page renders correctly
- [ ] Contact page renders correctly
- [ ] Mobile navigation works
- [ ] Hamburger animation works
- [ ] Footer social links work
- [ ] All hover effects preserved
- [ ] All responsive breakpoints work

### PR 2.2 Checklist

- [ ] Touch targets 44px minimum verified
- [ ] Breakpoints consistent across files
- [ ] Mobile navigation comfortable to use
- [ ] Button tap areas adequate
- [ ] Social links tap areas adequate
- [ ] Forms accessible on mobile (if any)
- [ ] No horizontal scroll on mobile

### Visual Regression Pages

Test at these viewport widths: 320px, 480px, 768px, 1000px, 1200px, 1920px

| Page | Route | Key Elements |
|------|-------|--------------|
| Home | `/` | Logo, nav, videos, gallery, CTA |
| Events | `/events` | Event grid, cards |
| Pricing | `/pricing` | Pricing tables |
| Private Lessons | `/private-lessons` | Benefits list |
| About | `/about` | Instructor layout, mission grid |
| Contact | `/contact` | Contact items |

---

## Appendix: Line-by-Line Mapping Reference

### Complete Source to Target Mapping

| Original Lines | Content | Target File |
|----------------|---------|-------------|
| 1-35 | Hamburger menu | `components/navigation.css` |
| 36-95 | Nav sidebar | `components/navigation.css` |
| 97-116 | Body defaults | `base/reset.css` |
| 117-149 | Header | `components/navigation.css` |
| 151-193 | Footer, social | `components/navigation.css` |
| 195-208 | Tagline | `base/typography.css` |
| 210-286 | Dual video | `components/gallery.css` |
| 288-354 | Dance gallery | `components/gallery.css` |
| 356-397 | Pasos animation | `components/gallery.css` |
| 399-463 | CTA, buttons | `components/cards.css`, `components/buttons.css` |
| 465-587 | Events page | `layouts/sections.css`, `components/cards.css`, `layouts/grid.css` |
| 589-637 | Pricing tables | `components/cards.css`, `base/typography.css` |
| 639-700 | Contact | `components/cards.css`, `base/typography.css` |
| 702-716 | Pricing layout | `layouts/sections.css` |
| 718-747 | Private lessons | `components/cards.css` |
| 749-948 | About page | Multiple files |
| 950-974 | About responsive | Multiple files |

---

## Document Metadata

| Field | Value |
|-------|-------|
| Version | 1.0.0 |
| Created | 2025-12-10 |
| Author | Principal Architect Agent |
| Status | Ready for Implementation |
| Dependencies | Phase 1 (variables.css) |
