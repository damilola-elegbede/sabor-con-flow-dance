# Phase 1: Foundation and Cleanup - Technical Specification

## Executive Summary

This document provides the complete technical specification for Phase 1 of the Sabor Con Flow
website modernization. Phase 1 consolidates the architecture by removing the unused Express.js
server, establishes CSS design tokens, and removes Bootstrap while adding critical accessibility
improvements.

**Timeline**: 3 PRs over approximately 1-2 weeks

**Risk Level**: Low to Medium (Express removal is low-risk since it is unused; Bootstrap removal
requires careful CSS replacement)

---

## Current State Analysis

### Architecture Overview

The Sabor Con Flow dance website currently has a dual-architecture problem:

| Component | Status | Technology | Deployment |
|-----------|--------|------------|------------|
| Django Backend | **ACTIVE** | Python 3.12, WSGI | Vercel via `/api/index.py` |
| Express.js Server | **UNUSED** | Node.js, EJS | Not deployed |
| Static Assets | Active | CSS, Images | Vercel static |

**Key Finding**: The Express.js server (`server.js`) and all its supporting files are completely
unused in production. The Django application serves all traffic via Vercel's serverless functions.

### Package.json Analysis

The current `package.json` contains **957 dependencies** in a flat structure (no separation between
`dependencies` and `devDependencies`). This represents severe dependency bloat.

**Express-Related Dependencies Identified** (to be removed in PR 1.1):

| Package | Version | Purpose |
|---------|---------|---------|
| `express` | ^4.21.2 | Web framework |
| `express-ejs-layouts` | ^2.5.1 | EJS layout support |
| `ejs` | ^3.1.10 | Template engine |
| `compression` | ^1.8.1 | HTTP compression |
| `helmet` | ^8.1.0 | Security headers |
| `morgan` | ^1.10.1 | HTTP request logger |
| `cors` | ^2.8.5 | CORS middleware |
| `body-parser` | ^1.20.3 | Request body parsing (Express dep) |
| `cookie` | ^0.4.2 | Cookie parsing |
| `cookie-signature` | ^1.0.6 | Cookie signing |

**Test Dependencies** (affected by Express removal):

| Package | Version | Purpose |
|---------|---------|---------|
| `jest` | ^30.0.5 | Test framework (devDependency) |
| `supertest` | ^7.1.4 | HTTP assertions (devDependency) |
| `nodemon` | ^3.1.10 | Dev server auto-reload (devDependency) |

### CSS Analysis

**File**: `/public/css/styles.css` (974 lines)

**Color Values Identified** (hardcoded throughout):

| Color | Hex/RGB Value | Usage Count | Purpose |
|-------|---------------|-------------|---------|
| Gold/Accent | `rgb(191, 170, 101)` | 45+ | Primary brand color |
| Gold Hex | `#BFAA65` | 1 | Calendly widget |
| Gold Variant | `#C7B375` | 5 | Inline styles in EJS |
| Black | `#000` / `#000000` | 15+ | Background color |
| White | `white` / `#ffffff` | 20+ | Text color |
| White RGB | `rgba(191, 170, 101, X)` | 10+ | Transparency variants |
| Green (WhatsApp) | `#25D366` | 2 | Social icon |
| Blue (Facebook) | `#1877F2` | 2 | Social icon |

**Typography Values Identified**:

| Property | Values Used |
|----------|-------------|
| Font Family | `'Playfair Display', serif` (headings) |
| Font Sizes | 0.9rem, 0.95rem, 1rem, 1.1rem, 1.2rem, 1.3rem, 1.4rem, 1.5rem, 2rem, 2.2rem, 2.5rem, 3rem |
| Font Weights | 400, 600, 700, bold |
| Line Heights | 1.5, 1.6, 1.7 |

**Spacing Values Identified**:

| Size | Values |
|------|--------|
| XS | 0.5rem |
| SM | 0.75rem, 1rem |
| MD | 1.5rem, 2rem |
| LG | 3rem, 4rem |
| XL | 5rem |

**Shadow Values Identified**:

| Type | Value |
|------|-------|
| Card Shadow | `0 8px 25px rgba(0, 0, 0, 0.3)` |
| Card Hover | `0 12px 35px rgba(191, 170, 101, 0.2)` |
| Video Shadow | `0 15px 30px rgba(0, 0, 0, 0.3)` |
| Video Hover | `0 20px 40px rgba(191, 170, 101, 0.2)` |
| Image Shadow | `0 15px 35px rgba(0, 0, 0, 0.3)` |
| Nav Shadow | `2px 0 5px rgba(0, 0, 0, 0.2)` |

**Transition Values Identified**:

| Duration | Value |
|----------|-------|
| Fast | 0.3s |
| Medium | 0.4s |
| Easing | `ease`, `ease-in-out` |

### Bootstrap Usage Analysis

**File**: `/views/layout.ejs`

**CDN Resources Currently Loaded**:

```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
```

**Bootstrap CSS Classes Used Across All EJS Templates**:

| Class | File(s) | Replacement Strategy |
|-------|---------|---------------------|
| `container` | All templates | Already custom-styled in styles.css |
| `text-center` | pricing.ejs, private-lessons.ejs, 404.ejs, 500.ejs | Add custom `.text-center` |
| `py-4` | layout.ejs (footer) | Replace with custom padding |
| `mt-3` | layout.ejs (footer) | Replace with custom margin |

**Critical Finding**: Bootstrap usage is minimal. Only 4 utility classes are used, all easily
replaceable with custom CSS.

---

## PR 1.1: Remove Express.js (Architecture Consolidation)

### Objective

Remove all unused Express.js server code and dependencies to eliminate architectural confusion and
reduce package bloat.

### Files to Delete

| File Path | Purpose | Lines | Safe to Delete |
|-----------|---------|-------|----------------|
| `/server.js` | Express server entry point | 61 | YES - Not deployed |
| `/routes/index.js` | Express route definitions | 54 | YES - Not deployed |
| `/data/events.js` | Event data for Express | 31 | YES - Not deployed |
| `/tests/routes.test.js` | Express route tests | 105 | YES - Tests unused code |
| `/tests/data.test.js` | Event data tests | 41 | YES - Tests unused code |

**Total Lines Removed**: 292 lines

### Directories to Consolidate

The project currently has duplicate static asset directories:
- `/public/` - Used by Express
- `/static/` - Used by Django

**Action**: After Express removal, consolidate to Django's `/static/` directory:
1. Compare `/public/css/styles.css` with `/static/css/styles.css` - keep the newer/more complete version
2. Copy any unique assets from `/public/` to `/static/`
3. Delete `/public/` directory (or leave for reference until Phase 2 completes)

**After Phase 1, all CSS/JS/image paths should reference `/static/`**

Similarly, templates:
- `/views/*.ejs` - Express EJS templates (can be deleted or kept for reference)
- `/templates/*.html` - Django templates (actively used)

**After Phase 1, all template references should use `/templates/*.html`**

### package.json Modifications

**Scripts Section - Before**:

```json
"scripts": {
  "start": "node server.js",
  "dev": "nodemon server.js",
  "test": "jest",
  "test:watch": "jest --watch"
}
```

**Scripts Section - After**:

```json
"scripts": {
  "lint:css": "stylelint 'public/css/**/*.css'",
  "lint:css:fix": "stylelint 'public/css/**/*.css' --fix"
}
```

**Dependencies to Remove**:

Remove these packages from the `dependencies` section:

```text
express
express-ejs-layouts
ejs
compression
helmet
morgan
cors
body-parser
cookie
cookie-signature
accepts
array-flatten
content-disposition
content-type
depd
destroy
encodeurl
escape-html
etag
finalhandler
forwarded
fresh
http-errors
merge-descriptors
methods
mime
ms
on-finished
parseurl
path-to-regexp
proxy-addr
qs
range-parser
raw-body
safe-buffer
safer-buffer
send
serve-static
setprototypeof
statuses
toidentifier
type-is
unpipe
utils-merge
vary
```

**Note**: Many of these are transitive dependencies of Express that will be removed automatically
when `express` is removed. However, some may be used by other packages. The safest approach is to:

1. Delete `node_modules/` and `package-lock.json`
2. Remove `express`, `express-ejs-layouts`, `ejs`, `compression`, `helmet`, `morgan`, `cors` from
   package.json
3. Run `npm install` to regenerate dependencies
4. Verify no build errors

**DevDependencies to Remove**:

```text
supertest
nodemon
```

**DevDependency to Keep**:

```text
jest (may be useful for future frontend tests)
```

### Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Django breaks | High | None | Express is not connected to Django |
| Vercel deployment fails | High | Low | Test deployment in preview |
| Other npm scripts break | Medium | Low | Verify all scripts before merge |

### Verification Steps

1. **Pre-removal verification**:

   ```bash
   # Confirm Express server is not used in production
   curl https://saborconflow.com/
   # Response should come from Django (check headers)
   ```

2. **Post-removal verification**:

   ```bash
   # Verify no broken imports
   grep -r "require.*express" . --include="*.js" --exclude-dir=node_modules
   grep -r "require.*server" . --include="*.js" --exclude-dir=node_modules

   # Verify Django still works locally
   python manage.py runserver

   # Verify Vercel preview deployment works
   vercel --prod
   ```

3. **Package verification**:

   ```bash
   # Check for orphaned dependencies
   npm ls --all 2>&1 | grep -i "UNMET PEER DEPENDENCY"

   # Verify package count reduction
   npm ls --all | wc -l
   ```

### Implementation Checklist

- [ ] Delete `/server.js`
- [ ] Delete `/routes/index.js`
- [ ] Delete `/data/events.js`
- [ ] Delete `/tests/routes.test.js`
- [ ] Delete `/tests/data.test.js`
- [ ] Remove `/routes/` directory if empty
- [ ] Remove `/data/` directory if empty
- [ ] Update `package.json` scripts
- [ ] Remove Express-related dependencies from `package.json`
- [ ] Delete `node_modules/` and `package-lock.json`
- [ ] Run `npm install`
- [ ] Verify no errors
- [ ] Test Vercel preview deployment
- [ ] Merge PR

---

## PR 1.2: CSS Design Tokens

### Objective

Create a centralized CSS custom properties (variables) file to establish design tokens for colors,
typography, spacing, shadows, and transitions.

### File to Create

**Path**: `/public/css/base/variables.css`

### Complete File Content

```css
/**
 * Sabor Con Flow - CSS Design Tokens
 *
 * This file defines all design tokens as CSS custom properties.
 * Import this file before all other stylesheets.
 *
 * @version 1.0.0
 * @author Sabor Con Flow
 */

:root {
  /* ==========================================================================
     COLOR TOKENS
     ========================================================================== */

  /* Brand Colors - Primary Palette */
  --color-gold: rgb(191, 170, 101);
  --color-gold-hex: #bfaa65;
  --color-gold-light: #c7b375;
  --color-black: #000000;
  --color-white: #ffffff;

  /* Brand Colors - Opacity Variants */
  --color-gold-10: rgba(191, 170, 101, 0.1);
  --color-gold-20: rgba(191, 170, 101, 0.2);
  --color-gold-50: rgba(191, 170, 101, 0.5);
  --color-gold-80: rgba(191, 170, 101, 0.8);
  --color-black-80: rgba(0, 0, 0, 0.8);
  --color-black-95: rgba(0, 0, 0, 0.95);
  --color-white-90: rgba(255, 255, 255, 0.9);

  /* Semantic Colors */
  --color-background: var(--color-black);
  --color-surface: var(--color-black);
  --color-text-primary: var(--color-white);
  --color-text-secondary: var(--color-gold);
  --color-text-muted: var(--color-white-90);
  --color-accent: var(--color-gold);
  --color-accent-hover: var(--color-gold-80);
  --color-accent-muted: var(--color-gold-80);
  --color-accent-bg: var(--color-gold-10);
  --color-accent-transparent: var(--color-gold-20);
  --color-nav-bg: var(--color-black-95);
  --color-border: var(--color-gold);
  --color-border-subtle: var(--color-gold-20);

  /* Gradients (for Phase 2+ components) */
  --gradient-overlay: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  --gradient-card: linear-gradient(135deg, rgba(191, 170, 101, 0.1), rgba(191, 170, 101, 0.05));

  /* Social Media Colors (for reference/icons) */
  --color-whatsapp: #25d366;
  --color-facebook: #1877f2;
  --color-instagram-yellow: #feda75;
  --color-instagram-orange: #f58529;
  --color-instagram-pink: #dd2a7b;
  --color-instagram-purple: #833ab4;
  --color-instagram-blue: #405de6;

  /* ==========================================================================
     TYPOGRAPHY TOKENS
     ========================================================================== */

  /* Font Families */
  --font-family-heading: 'Playfair Display', serif;
  --font-family-body: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
  --font-family-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace;

  /* Font Sizes - Fluid Scale */
  --font-size-xs: 0.75rem;   /* 12px */
  --font-size-sm: 0.875rem;  /* 14px */
  --font-size-base: 1rem;    /* 16px */
  --font-size-md: 1.125rem;  /* 18px */
  --font-size-lg: 1.25rem;   /* 20px */
  --font-size-xl: 1.5rem;    /* 24px */
  --font-size-2xl: 2rem;     /* 32px */
  --font-size-3xl: 2.5rem;   /* 40px */
  --font-size-4xl: 3rem;     /* 48px */

  /* Font Weights */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* Line Heights */
  --line-height-tight: 1.25;
  --line-height-snug: 1.375;
  --line-height-normal: 1.5;
  --line-height-base: var(--line-height-normal);  /* Alias for Phase 2+ compatibility */
  --line-height-relaxed: 1.625;
  --line-height-loose: 1.75;

  /* Letter Spacing */
  --letter-spacing-tight: -0.025em;
  --letter-spacing-normal: 0;
  --letter-spacing-wide: 0.025em;
  --letter-spacing-wider: 0.05em;

  /* ==========================================================================
     SPACING TOKENS
     ========================================================================== */

  /* Base spacing unit: 4px */
  --space-0: 0;
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
  --space-24: 6rem;     /* 96px */

  /* Semantic Spacing */
  --space-section: var(--space-16);
  --space-component: var(--space-8);
  --space-element: var(--space-4);
  --space-inline: var(--space-2);

  /* ==========================================================================
     LAYOUT TOKENS
     ========================================================================== */

  /* Container Widths */
  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1200px;
  --container-2xl: 1400px;

  /* Content Widths */
  --content-narrow: 600px;
  --content-default: 800px;
  --content-wide: 1000px;

  /* Z-Index Scale */
  --z-base: 0;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-fixed: 300;
  --z-modal-backdrop: 400;
  --z-modal: 500;
  --z-popover: 600;
  --z-tooltip: 700;
  --z-nav: 998;
  --z-nav-toggle: 999;
  --z-header-logo: 1000;
  --z-menu-toggle: 1001;

  /* ==========================================================================
     BORDER TOKENS
     ========================================================================== */

  /* Border Widths */
  --border-width-thin: 1px;
  --border-width-default: 2px;
  --border-width-thick: 4px;

  /* Border Radii */
  --radius-none: 0;
  --radius-sm: 4px;
  --radius-default: 8px;
  --radius-md: 12px;
  --radius-lg: 15px;
  --radius-xl: 20px;
  --radius-full: 9999px;

  /* ==========================================================================
     SHADOW TOKENS
     ========================================================================== */

  /* Elevation Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.1);
  --shadow-default: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 8px 25px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 15px 30px rgba(0, 0, 0, 0.3);
  --shadow-xl: 0 15px 35px rgba(0, 0, 0, 0.3);

  /* Hover State Shadows */
  --shadow-hover-sm: 0 4px 12px rgba(191, 170, 101, 0.15);
  --shadow-hover-md: 0 12px 35px rgba(191, 170, 101, 0.2);
  --shadow-glow: 0 20px 40px rgba(191, 170, 101, 0.2);
  --shadow-hover-lg: 0 20px 40px rgba(191, 170, 101, 0.2);

  /* Component-Specific Shadows */
  --shadow-card: var(--shadow-md);
  --shadow-card-hover: var(--shadow-hover-md);
  --shadow-video: var(--shadow-lg);
  --shadow-video-hover: var(--shadow-hover-lg);
  --shadow-nav: 2px 0 5px rgba(0, 0, 0, 0.2);
  --shadow-image: var(--shadow-xl);

  /* ==========================================================================
     TRANSITION TOKENS
     ========================================================================== */

  /* Durations */
  --duration-instant: 0ms;
  --duration-fast: 150ms;
  --duration-default: 300ms;
  --duration-slow: 400ms;
  --duration-slower: 500ms;

  /* Easing Functions */
  --ease-linear: linear;
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);

  /* Common Transitions */
  --transition-fast: all var(--duration-fast) var(--ease-out);
  --transition-default: all var(--duration-default) ease;
  --transition-slow: all var(--duration-slow) ease;
  --transition-transform: transform var(--duration-default) ease;
  --transition-opacity: opacity var(--duration-default) ease;
  --transition-colors: background-color var(--duration-default) ease,
    color var(--duration-default) ease, border-color var(--duration-default) ease;

  /* ==========================================================================
     BREAKPOINT TOKENS (for reference in media queries)
     ========================================================================== */

  /* Note: CSS custom properties cannot be used in media queries directly.
     These values are documented here for reference.
     Use these values when writing @media queries:

     --breakpoint-sm: 640px;
     --breakpoint-md: 768px;
     --breakpoint-lg: 1024px;
     --breakpoint-xl: 1200px;
     --breakpoint-2xl: 1400px;
  */
}

/* ==========================================================================
   DARK MODE SUPPORT (Future Enhancement)
   ========================================================================== */

/*
@media (prefers-color-scheme: light) {
  :root {
    --color-background: var(--color-white);
    --color-surface: #f5f5f5;
    --color-text-primary: var(--color-black);
    --color-text-secondary: #333333;
  }
}
*/
```

### Directory Structure

Create the following directory structure:

```text
public/
  css/
    base/
      variables.css    <-- NEW FILE
    styles.css         <-- EXISTING (modify import later)
```

### Integration Steps

**Step 1**: Create the directory and file:

```bash
mkdir -p public/css/base
touch public/css/base/variables.css
```

**Step 2**: Add variables.css content (as shown above)

**Step 3**: (In future PR) Update `layout.ejs` to include variables.css before styles.css:

```html
<link href="/css/base/variables.css" rel="stylesheet" type="text/css">
<link href="/css/styles.css" rel="stylesheet" type="text/css">
```

**Note**: The actual integration into styles.css will happen in a future PR (Phase 2) to minimize
risk in this phase.

### Verification Steps

1. **Validate CSS syntax**:

   ```bash
   npx stylelint public/css/base/variables.css
   ```

2. **Test in browser**:

   - Open browser DevTools
   - Navigate to Elements > Computed
   - Verify CSS variables are present on `:root`

3. **Test variable usage**:

   ```css
   /* Test in browser console */
   getComputedStyle(document.documentElement).getPropertyValue('--color-gold')
   /* Should return: rgb(191, 170, 101) */
   ```

### Implementation Checklist

- [ ] Create `/public/css/base/` directory
- [ ] Create `/public/css/base/variables.css`
- [ ] Add all color tokens
- [ ] Add all typography tokens
- [ ] Add all spacing tokens
- [ ] Add all layout tokens
- [ ] Add all border tokens
- [ ] Add all shadow tokens
- [ ] Add all transition tokens
- [ ] Validate with stylelint
- [ ] Test in browser
- [ ] Merge PR

---

## PR 1.3: Remove Bootstrap and Critical Accessibility

### Objective

Remove Bootstrap CSS/JS dependencies and add essential accessibility features including skip-to-
content link, Inter font for body text, focus-visible states, and screen reader utilities.

### Part A: Remove Bootstrap CDN

**File to Modify**: `/views/layout.ejs`

**Lines to Remove**:

```html
<!-- Line 15: Remove this -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- Line 81: Remove this -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
```

### Part B: Add CSS Replacements for Bootstrap Classes

**File to Modify**: `/public/css/styles.css`

**Add at the beginning of the file** (after any existing comments):

```css
/* ==========================================================================
   UTILITY CLASSES (Bootstrap Replacements)
   ========================================================================== */

/**
 * Text alignment utilities
 * Replaces: Bootstrap text-center, text-left, text-right
 */
.text-center {
  text-align: center;
}

.text-left {
  text-align: left;
}

.text-right {
  text-align: right;
}

/**
 * Spacing utilities
 * Replaces: Bootstrap py-4, mt-3, etc.
 */
.py-4 {
  padding-top: 1.5rem;
  padding-bottom: 1.5rem;
}

.mt-3 {
  margin-top: 1rem;
}

.mb-3 {
  margin-bottom: 1rem;
}

/**
 * Container utility
 * Note: Already defined elsewhere in styles.css, but ensuring fallback
 */
```

### Part C: Add Skip-to-Content Link

**File to Modify**: `/views/layout.ejs`

**Add immediately after `<body>` tag** (before `<header>`):

```html
<body>
    <!-- Skip to main content link for keyboard/screen reader users -->
    <a href="#main-content" class="skip-link">Skip to main content</a>

    <header class="header">
```

**Also update the `<main>` tag**:

```html
<!-- Change from: -->
<main class="main-content">

<!-- Change to: -->
<main id="main-content" class="main-content">
```

**Add to `/public/css/styles.css`**:

```css
/* ==========================================================================
   ACCESSIBILITY UTILITIES
   ========================================================================== */

/**
 * Skip Link
 * Allows keyboard users to skip navigation and jump to main content.
 * Hidden by default, visible on focus.
 */
.skip-link {
  position: absolute;
  top: -100px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10000;
  padding: 1rem 2rem;
  background-color: rgb(191, 170, 101);
  color: #000;
  text-decoration: none;
  font-weight: 600;
  font-size: 1rem;
  border-radius: 0 0 8px 8px;
  transition: top 0.3s ease;
}

.skip-link:focus {
  top: 0;
  outline: 3px solid #fff;
  outline-offset: 2px;
}

/**
 * Screen Reader Only
 * Visually hidden but accessible to screen readers.
 * Use for content that provides context for assistive technology.
 */
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

/**
 * Screen Reader Only - Focusable variant
 * Becomes visible when focused (for skip links, etc.)
 */
.sr-only-focusable:focus,
.sr-only-focusable:active {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

### Part D: Add Focus-Visible States

**Add to `/public/css/styles.css`**:

```css
/* ==========================================================================
   FOCUS STATES
   ========================================================================== */

/**
 * Global focus-visible styles
 * Provides visible focus indicators for keyboard navigation
 * while avoiding visual clutter for mouse users.
 */

/* Remove default outline for mouse users */
:focus:not(:focus-visible) {
  outline: none;
}

/* Enhanced focus ring for keyboard users */
:focus-visible {
  outline: 3px solid rgb(191, 170, 101);
  outline-offset: 2px;
}

/* Specific focus styles for interactive elements */
a:focus-visible,
button:focus-visible,
[role="button"]:focus-visible {
  outline: 3px solid rgb(191, 170, 101);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Focus styles for form inputs (future use) */
input:focus-visible,
textarea:focus-visible,
select:focus-visible {
  outline: 3px solid rgb(191, 170, 101);
  outline-offset: 0;
  border-color: rgb(191, 170, 101);
}

/* Navigation link focus enhancement */
.nav a:focus-visible {
  outline: 3px solid rgb(191, 170, 101);
  outline-offset: 4px;
  border-radius: 4px;
}

/* Button focus enhancement */
.btn:focus-visible {
  outline: 3px solid rgb(191, 170, 101);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(191, 170, 101, 0.3);
}

/* Menu toggle focus */
.menu-toggle:focus-visible {
  outline: 3px solid rgb(191, 170, 101);
  outline-offset: 4px;
  border-radius: 4px;
}

/* Social link focus */
.social-link:focus-visible {
  outline: 3px solid rgb(191, 170, 101);
  outline-offset: 4px;
  border-radius: 8px;
}
```

### Part E: Add Inter Font for Body Text

**File to Modify**: `/views/layout.ejs`

**Add after Playfair Display font import** (line 17):

```html
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

**File to Modify**: `/public/css/styles.css`

**Update the body rule**:

```css
body {
  background-color: #000;
  color: white;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
  font-size: 1rem;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

### Complete layout.ejs After Modifications

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><%= typeof title !== 'undefined' ? title : 'Sabor Con Flow' %></title>
    <!-- Favicon configuration -->
    <link rel="icon" type="image/png" href="/images/favicon/favicon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/images/sabor-con-flow-logo.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/images/sabor-con-flow-logo.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/images/sabor-con-flow-logo.png">
    <link rel="manifest" href="/images/site.webmanifest">
    <meta name="theme-color" content="#000000">
    <!-- End favicon configuration -->
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <!-- Icons -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <!-- Styles -->
    <link href="/css/styles.css" rel="stylesheet" type="text/css">
    <!-- Calendly badge widget begin -->
    <link href="https://assets.calendly.com/assets/external/widget.css" rel="stylesheet">
    <!-- Calendly badge widget end -->
</head>
<body>
    <!-- Skip to main content link for keyboard/screen reader users -->
    <a href="#main-content" class="skip-link">Skip to main content</a>

    <header class="header">
        <button class="menu-toggle" aria-label="Toggle navigation" aria-expanded="false" aria-controls="main-nav">
            <span></span>
            <span></span>
            <span></span>
        </button>
        <a href="/" class="header-logo-link">
            <img src="/images/sabor-con-flow-logo.png" alt="Sabor Con Flow - Home" class="header-logo">
        </a>
        <nav id="main-nav" class="nav" aria-label="Main navigation">
            <a href="/"><span>Home</span></a>
            <a href="/about"><span>About</span></a>
            <a href="/events"><span>Events</span></a>
            <a href="/pricing"><span>Pricing</span></a>
            <a href="/private-lessons"><span>Private Lessons</span></a>
            <a href="/contact"><span>Contact</span></a>
        </nav>
    </header>

    <main id="main-content" class="main-content">
        <%- body %>
    </main>

    <footer class="footer text-center py-4">
        <div class="container">
            <div class="social-links">
                <a href="https://www.instagram.com/saborconflow.dance/" target="_blank" rel="noopener noreferrer" class="social-link" aria-label="Follow us on Instagram">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36" aria-hidden="true">
                        <defs>
                            <linearGradient id="instaFooterGradient" x1="0%" y1="100%" x2="100%" y2="0%">
                                <stop offset="0%" stop-color="#FEDA75"/><stop offset="25%" stop-color="#F58529"/><stop offset="50%" stop-color="#DD2A7B"/><stop offset="75%" stop-color="#833AB4"/><stop offset="100%" stop-color="#405DE6"/>
                            </linearGradient>
                        </defs>
                        <rect width="24" height="24" rx="6" ry="6" fill="url(#instaFooterGradient)"/>
                        <path fill="none" stroke="#ffffff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"
                              d="M12 16.14a4.14 4.14 0 100-8.28 4.14 4.14 0 000 8.28z"/>
                        <circle fill="#ffffff" cx="17.3" cy="6.7" r="1.1"/>
                        <rect x="3.5" y="3.5" width="17" height="17" rx="4" ry="4" fill="none" stroke="#ffffff" stroke-width="1.8"/>
                    </svg>
                </a>
                <a href="https://chat.whatsapp.com/GaZONDA1HgFG7C8djihJ1x" target="_blank" rel="noopener noreferrer" class="social-link" aria-label="Join our WhatsApp community">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36" aria-hidden="true">
                        <rect width="24" height="24" rx="6" ry="6" fill="#25D366"/>
                        <path fill="#ffffff" d="M17.6 6.2c-1.5-1.5-3.4-2.3-5.5-2.3-4.3 0-7.8 3.5-7.8 7.8 0 1.4.4 2.7 1 3.9l-1.1 4 4.1-1.1c1.1.6 2.4 1 3.7 1 4.3 0 7.8-3.5 7.8-7.8.1-2.1-.7-4-2.2-5.5zm-5.5 12c-1.2 0-2.3-.3-3.3-.9l-.2-.1-2.4.6.6-2.3-.2-.2c-.6-1-1-2.2-1-3.4 0-3.6 2.9-6.5 6.5-6.5 1.7 0 3.3.7 4.6 1.9 1.2 1.2 1.9 2.8 1.9 4.6-.1 3.5-3 6.3-6.5 6.3zm3.6-4.9c-.2-.1-1.1-.6-1.3-.6-.2-.1-.3-.1-.4.1-.1.2-.5.6-.6.8-.1.1-.2.1-.4 0-.6-.3-1.3-.7-1.9-1.3-.8-.7-1.2-1.5-1.3-1.7-.1-.2 0-.3.1-.4l.3-.3s.1-.2.2-.3c.1-.1.1-.2.1-.3 0-.1 0-.2-.1-.3l-.6-1.4c-.1-.3-.3-.3-.4-.3h-.4c-.1 0-.3.1-.5.2-.2.1-.6.6-.6 1.4s.6 1.6.7 1.7c.1.1 1.3 2 3.2 2.8.4.2.8.3 1 .3.2.1.5.1.7.1.2 0 .6-.3.7-.5.1-.3.1-.5.1-.6-.1-.1-.2-.1-.4-.2z"/>
                    </svg>
                </a>
                <a href="https://www.facebook.com/profile.php?id=61575502290591" target="_blank" rel="noopener noreferrer" class="social-link" aria-label="Follow us on Facebook">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36" aria-hidden="true">
                        <rect width="24" height="24" rx="6" ry="6" fill="#1877F2"/>
                        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" fill="#ffffff"/>
                    </svg>
                </a>
            </div>
            <p class="mt-3">&copy; <%= new Date().getFullYear() %> Sabor Con Flow. All rights reserved.</p>
        </div>
    </footer>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const menuToggle = document.querySelector('.menu-toggle');
            const nav = document.querySelector('.nav');

            menuToggle.addEventListener('click', function() {
                const isExpanded = nav.classList.toggle('active');
                menuToggle.classList.toggle('active');
                menuToggle.setAttribute('aria-expanded', isExpanded);
            });

            // Close menu when clicking outside
            document.addEventListener('click', function(event) {
                if (!nav.contains(event.target) && !menuToggle.contains(event.target)) {
                    nav.classList.remove('active');
                    menuToggle.classList.remove('active');
                    menuToggle.setAttribute('aria-expanded', 'false');
                }
            });

            // Close menu on Escape key
            document.addEventListener('keydown', function(event) {
                if (event.key === 'Escape' && nav.classList.contains('active')) {
                    nav.classList.remove('active');
                    menuToggle.classList.remove('active');
                    menuToggle.setAttribute('aria-expanded', 'false');
                    menuToggle.focus();
                }
            });
        });
    </script>
</body>
</html>
```

### Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Layout breaks without Bootstrap | High | Medium | Custom CSS replacements added |
| Container class conflicts | Medium | Low | Existing custom styles take precedence |
| Font loading performance | Low | Low | Preload critical fonts |
| Focus states too prominent | Low | Medium | Test with users, adjust if needed |

### Verification Steps

1. **Visual regression testing**:

   - Visit each page: `/`, `/about`, `/events`, `/pricing`, `/private-lessons`, `/contact`
   - Compare screenshots before/after Bootstrap removal
   - Verify no layout shifts or broken styles

2. **Accessibility testing**:

   ```bash
   # Using Lighthouse
   npx lighthouse https://localhost:3000 --only-categories=accessibility

   # Or use axe-core in browser DevTools
   ```

3. **Keyboard navigation testing**:

   - Tab through entire site
   - Verify skip link appears on first Tab press
   - Verify all interactive elements have visible focus
   - Verify Escape closes mobile menu

4. **Screen reader testing**:

   - Test with VoiceOver (macOS) or NVDA (Windows)
   - Verify skip link is announced
   - Verify navigation landmarks are announced
   - Verify social links have accessible names

5. **Font loading verification**:

   ```javascript
   // In browser console
   document.fonts.ready.then(() => {
     console.log('Fonts loaded:', document.fonts.check('1em Inter'));
   });
   ```

### Implementation Checklist

- [ ] Remove Bootstrap CSS CDN from layout.ejs
- [ ] Remove Bootstrap JS CDN from layout.ejs
- [ ] Add Inter font import to layout.ejs
- [ ] Add skip-link to layout.ejs
- [ ] Add id="main-content" to main element
- [ ] Add aria attributes to menu toggle
- [ ] Add aria-label to navigation
- [ ] Add aria-label to social links
- [ ] Add aria-hidden to decorative SVGs
- [ ] Add utility classes to styles.css (text-center, py-4, mt-3)
- [ ] Add skip-link styles to styles.css
- [ ] Add .sr-only class to styles.css
- [ ] Add focus-visible styles to styles.css
- [ ] Update body font-family to Inter
- [ ] Update JavaScript for aria-expanded
- [ ] Add Escape key handler for menu
- [ ] Test all pages visually
- [ ] Test keyboard navigation
- [ ] Test with screen reader
- [ ] Run Lighthouse accessibility audit
- [ ] Merge PR

---

## Appendix A: Complete CSS Additions for PR 1.3

This is the complete CSS to add to the beginning of `/public/css/styles.css`:

```css
/* ==========================================================================
   UTILITY CLASSES (Bootstrap Replacements)
   ========================================================================== */

/**
 * Text alignment utilities
 */
.text-center {
  text-align: center;
}

.text-left {
  text-align: left;
}

.text-right {
  text-align: right;
}

/**
 * Spacing utilities
 */
.py-4 {
  padding-top: 1.5rem;
  padding-bottom: 1.5rem;
}

.mt-3 {
  margin-top: 1rem;
}

.mb-3 {
  margin-bottom: 1rem;
}

/* ==========================================================================
   ACCESSIBILITY UTILITIES
   ========================================================================== */

/**
 * Skip Link
 */
.skip-link {
  position: absolute;
  top: -100px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10000;
  padding: 1rem 2rem;
  background-color: rgb(191, 170, 101);
  color: #000;
  text-decoration: none;
  font-weight: 600;
  font-size: 1rem;
  border-radius: 0 0 8px 8px;
  transition: top 0.3s ease;
}

.skip-link:focus {
  top: 0;
  outline: 3px solid #fff;
  outline-offset: 2px;
}

/**
 * Screen Reader Only
 */
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

.sr-only-focusable:focus,
.sr-only-focusable:active {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}

/* ==========================================================================
   FOCUS STATES
   ========================================================================== */

:focus:not(:focus-visible) {
  outline: none;
}

:focus-visible {
  outline: 3px solid rgb(191, 170, 101);
  outline-offset: 2px;
}

a:focus-visible,
button:focus-visible,
[role="button"]:focus-visible {
  outline: 3px solid rgb(191, 170, 101);
  outline-offset: 2px;
  border-radius: 4px;
}

input:focus-visible,
textarea:focus-visible,
select:focus-visible {
  outline: 3px solid rgb(191, 170, 101);
  outline-offset: 0;
  border-color: rgb(191, 170, 101);
}

.nav a:focus-visible {
  outline: 3px solid rgb(191, 170, 101);
  outline-offset: 4px;
  border-radius: 4px;
}

.btn:focus-visible {
  outline: 3px solid rgb(191, 170, 101);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(191, 170, 101, 0.3);
}

.menu-toggle:focus-visible {
  outline: 3px solid rgb(191, 170, 101);
  outline-offset: 4px;
  border-radius: 4px;
}

.social-link:focus-visible {
  outline: 3px solid rgb(191, 170, 101);
  outline-offset: 4px;
  border-radius: 8px;
}

/* ==========================================================================
   EXISTING STYLES BELOW
   ========================================================================== */
```

---

## Appendix B: Dependencies Analysis Summary

### Before Phase 1

| Metric | Value |
|--------|-------|
| Total npm packages | 957 |
| Express-related packages | ~15 |
| Test-related packages | 3 |
| External CSS CDNs | 2 (Bootstrap, Font Awesome) |
| External JS CDNs | 2 (Bootstrap, Calendly) |

### After Phase 1

| Metric | Value | Change |
|--------|-------|--------|
| Total npm packages | ~800 (estimated) | -157 |
| Express-related packages | 0 | -15 |
| Test-related packages | 1 (jest retained) | -2 |
| External CSS CDNs | 1 (Font Awesome only) | -1 |
| External JS CDNs | 1 (Calendly only) | -1 |

### Files Changed Summary

| PR | Files Deleted | Files Modified | Files Created |
|----|---------------|----------------|---------------|
| 1.1 | 5 | 1 | 0 |
| 1.2 | 0 | 0 | 1 |
| 1.3 | 0 | 2 | 0 |
| **Total** | **5** | **3** | **1** |

---

## Appendix C: Testing Matrix

### PR 1.1 Testing

| Test Case | Expected Result | Status |
|-----------|-----------------|--------|
| Django homepage loads | 200 OK | Pending |
| Django about page loads | 200 OK | Pending |
| Django events page loads | 200 OK | Pending |
| Vercel deployment succeeds | Build passes | Pending |
| No console errors | Clean console | Pending |

### PR 1.2 Testing

| Test Case | Expected Result | Status |
|-----------|-----------------|--------|
| variables.css loads | No 404 | Pending |
| CSS variables accessible | DevTools shows values | Pending |
| Stylelint passes | No errors | Pending |

### PR 1.3 Testing

| Test Case | Expected Result | Status |
|-----------|-----------------|--------|
| Homepage layout correct | No visual changes | Pending |
| About page layout correct | No visual changes | Pending |
| Events page layout correct | No visual changes | Pending |
| Pricing page layout correct | No visual changes | Pending |
| Private lessons layout correct | No visual changes | Pending |
| Contact page layout correct | No visual changes | Pending |
| Skip link appears on Tab | Link visible at top | Pending |
| Skip link jumps to content | Focus moves to main | Pending |
| Menu toggle focus visible | Gold outline shown | Pending |
| Nav links focus visible | Gold outline shown | Pending |
| Social links focus visible | Gold outline shown | Pending |
| Buttons focus visible | Gold outline + shadow | Pending |
| Inter font loads | Body text in Inter | Pending |
| Lighthouse accessibility | Score >= 90 | Pending |

---

## Appendix D: Rollback Procedures

### PR 1.1 Rollback

```bash
# If Express removal causes issues (unlikely since unused)
git revert <commit-hash>
npm install
```

### PR 1.2 Rollback

```bash
# If variables.css causes issues
git revert <commit-hash>
# Or simply delete the file if not yet integrated
rm public/css/base/variables.css
```

### PR 1.3 Rollback

```bash
# If Bootstrap removal breaks layout
git revert <commit-hash>
# Manually restore Bootstrap CDN links if needed
```

---

## Appendix E: Future Phase Preview

This specification covers Phase 1 only. Future phases will include:

**Phase 2: CSS Architecture**

- Integrate design tokens into styles.css
- Refactor monolithic CSS into modular components
- Add CSS linting and formatting

**Phase 3: Performance Optimization**

- Remove Font Awesome (replace with custom SVGs)
- Implement critical CSS extraction
- Add lazy loading for images

**Phase 4: Build Pipeline**

- Add PostCSS processing
- Implement CSS minification
- Add CSS purging for unused styles

---

## Document Metadata

| Property | Value |
|----------|-------|
| Version | 1.0.0 |
| Created | 2025-12-10 |
| Last Updated | 2025-12-10 |
| Author | Principal Architect Agent |
| Status | Ready for Implementation |
