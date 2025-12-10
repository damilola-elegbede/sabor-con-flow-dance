# Sabor Con Flow Dance - Modernization Plan

## Executive Summary

A comprehensive modernization plan for the Sabor Con Flow dance website, addressing architectural consolidation, UI uplift, and technical debt reduction **in parallel**.

### Key Decisions
- **Framework**: Consolidate to Django only (remove Express.js)
- **CSS Strategy**: Remove Bootstrap entirely, use vanilla CSS with custom properties
- **UI Approach**: Comprehensive uplift (animations, components, mobile experience)
- **Execution**: Phased approach with multiple PRs per phase

### PR Summary at a Glance
| Phase | PR | Description |
|-------|-----|-------------|
| **1** | 1.1 | Remove Express.js (architecture consolidation) |
| **1** | 1.2 | CSS design tokens (custom properties) |
| **1** | 1.3 | Remove Bootstrap & critical A11y fixes |
| **2** | 2.1 | CSS module structure (split 974 lines) |
| **2** | 2.2 | Responsive design refinements |
| **3** | 3.1 | Navigation enhancements (menu UX, blur header) |
| **3** | 3.2 | Card & button system (glassmorphism, depth) |
| **3** | 3.3 | Gallery & media enhancements |
| **4** | 4.1 | Micro-interactions (ripples, hover lifts) |
| **4** | 4.2 | Scroll animations (fade-in, parallax) |
| **5** | 5.1 | Image optimization (WebP, srcset, lazy) |
| **5** | 5.2 | Font & asset optimization |
| **5** | 5.3 | Build pipeline (Vite) |
| **6** | 6.1 | Contact form implementation |
| **6** | 6.2 | Dependency audit & cleanup |
| **6** | 6.3 | Final A11y & polish |

---

## Current State Analysis

### Architecture Overview
| Layer | Current State | Issues |
|-------|---------------|--------|
| **Backend** | Dual Django + Express.js | Only Django deployed; Express unused |
| **Frontend** | EJS templates + vanilla CSS/JS | Monolithic, no build pipeline |
| **Data** | Hardcoded in both frameworks | Duplicated, no single source of truth |
| **Deployment** | Vercel (Django WSGI) | Express ignored in production |

### Key Metrics
- **CSS**: 974 lines in single file (no modules)
- **npm dependencies**: 957 packages (severe bloat)
- **Python dependencies**: 4 packages (appropriate)
- **Pages**: 6 public pages + 2 error pages
- **Video assets**: 84MB + 9MB (migrated to external hosting)

### What's Working Well
- Strong brand identity (gold `#BFAA65` on black)
- Playfair Display typography (sophisticated feel)
- Clear information architecture
- Mobile-responsive hamburger navigation
- Helmet security headers configured
- Clean EJS templating patterns

---

## Modernization Plan

### Phase 1: Architecture Consolidation (Foundation)

#### 1.1 Remove Express.js / Consolidate to Django
**Rationale**: Django is deployed to production; Express adds confusion without value.

**Actions**:
- Remove `server.js`, `routes/`, `data/events.js`
- Remove Express-related npm dependencies
- Keep only essential Node.js tooling (build tools, linting)
- Move all routing to Django `core/urls.py`

**Files to remove**:
```
server.js
routes/index.js
data/events.js
tests/routes.test.js
tests/data.test.js
```

#### 1.2 Dependency Cleanup
**npm packages to audit and remove**:
- Build tools: Choose ONE (recommend Vite over Webpack)
- Testing: Consolidate (Jest OR Vitest, not both)
- Unused: PostCSS ecosystem, Puppeteer, Playwright, Lighthouse (unless actively used)

**Target**: Reduce from 957 to ~50-100 dependencies

#### 1.3 Centralize Data
**Current**: Events duplicated in `data/events.js` + `core/views.py`

**Solution**: Single JSON file consumed by Django
```
data/
  events.json    # Single source of truth
  pricing.json   # Extract from templates
```

---

### Phase 2: CSS Architecture Modernization

#### 2.1 Implement CSS Custom Properties
**Replace hardcoded colors with design tokens**:

```css
:root {
  /* Colors */
  --color-primary: rgb(191, 170, 101);
  --color-background: #000000;
  --color-text: #ffffff;
  --color-text-muted: rgba(255, 255, 255, 0.7);

  /* Typography */
  --font-display: 'Playfair Display', serif;
  --font-body: system-ui, sans-serif;

  /* Spacing */
  --space-xs: 0.5rem;
  --space-sm: 1rem;
  --space-md: 2rem;
  --space-lg: 4rem;

  /* Transitions */
  --transition-fast: 0.2s ease;
  --transition-normal: 0.3s ease;

  /* Shadows */
  --shadow-sm: 0 2px 4px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 8px rgba(0,0,0,0.4);
  --shadow-lg: 0 8px 16px rgba(0,0,0,0.5);
}
```

#### 2.2 Modularize CSS Structure
**Split `styles.css` (974 lines) into**:
```
public/css/
  base/
    reset.css        # Normalize/reset styles
    typography.css   # Font definitions, text styles
    variables.css    # CSS custom properties
  components/
    buttons.css      # .btn, .btn-primary, .btn-secondary
    cards.css        # .event-card, .class-preview
    navigation.css   # Header, hamburger, footer
    forms.css        # Future form styles
    gallery.css      # Video/image gallery
    pricing.css      # Pricing tables
  layouts/
    grid.css         # Grid utilities
    sections.css     # Page section layouts
  pages/
    home.css         # Homepage-specific
    about.css        # About page-specific
  main.css           # Import orchestrator
```

#### 2.3 Remove Bootstrap Entirely
**Current**: Bootstrap 5.1.3 CDN with heavy overrides

**Action**: Remove Bootstrap completely and replace with custom CSS.

**Rationale**:
- Site doesn't use complex Bootstrap components (no modals, carousels, accordions)
- Heavy custom overrides negate Bootstrap's benefits
- Reduces external dependencies and page load
- Cleaner CSS without framework conflicts

**Files to Update**:
- `views/layout.ejs` - Remove Bootstrap CDN links
- `public/css/styles.css` - Replace Bootstrap utilities with custom equivalents

**Bootstrap Features to Replace with Custom CSS**:
- Grid system → CSS Grid / Flexbox (already partially used)
- Buttons → Custom `.btn` classes (already exist)
- Forms → Custom form styles
- Utilities → Custom utility classes or inline CSS variables

---

### Phase 3: UI Uplift - Modern Visual Enhancements

#### 3.1 Typography Improvements
**Current issues**: No explicit body font, inconsistent sizing

**Enhancements**:
- Add Inter or DM Sans as body font (modern sans-serif)
- Implement typographic scale (1.25 ratio):
  ```
  --text-xs: 0.75rem
  --text-sm: 0.875rem
  --text-base: 1rem
  --text-lg: 1.125rem
  --text-xl: 1.25rem
  --text-2xl: 1.5rem
  --text-3xl: 2rem
  --text-4xl: 2.5rem
  --text-5xl: 3rem
  ```

#### 3.2 Modern UI Component Patterns

**Navigation Enhancement**:
- Add visible close button (X) to mobile menu
- Implement backdrop blur on header scroll
- Add active page indicator in nav
- Smooth scroll-to-section for anchor links

**Card Components**:
- Add glassmorphism effect to cards (subtle backdrop-filter)
- Implement skeleton loading states
- Add subtle gradient borders
- Enhance hover states with depth transitions

**Button System**:
- Add focus-visible states (accessibility)
- Implement ripple/click feedback
- Add loading spinner states
- Create icon button variants

**Hero Section**:
- Add parallax scroll effect to video
- Implement text reveal animation on load
- Add subtle grain texture overlay (premium feel)

#### 3.3 Micro-Interactions & Animations
**Implement using CSS/minimal JS**:
- Scroll-triggered fade-in for sections
- Staggered card entrance animations
- Smooth number counting for pricing
- Hover lift with shadow progression
- Menu item slide-in refinements

#### 3.4 Modern Layout Patterns
**Implement CSS Grid and modern techniques**:
- Use `clamp()` for fluid typography
- Implement container queries where beneficial
- Add `aspect-ratio` for media elements
- Use `gap` instead of margin hacks

---

### Phase 4: Accessibility Remediation (A11y)

#### 4.1 Critical Fixes (WCAG AA)
| Issue | Fix |
|-------|-----|
| Missing skip link | Add "Skip to main content" link at top |
| Social icon labels | Add `aria-label` or `<title>` to SVGs |
| Video accessibility | Add captions/transcripts |
| Focus states | Add `:focus-visible` styles matching hover |
| Color contrast | Audit text on gradients/overlays |
| Emoji indicators | Add `aria-hidden` or replace with semantic markup |

#### 4.2 Navigation A11y
- Add `aria-expanded` to hamburger button
- Implement focus trap within open menu
- Add keyboard navigation (Escape to close)
- Ensure proper heading hierarchy (h1 → h2 → h3)

#### 4.3 Form Accessibility (Future Contact Form)
- Proper label associations
- Error message announcements
- Required field indicators
- Input validation feedback

---

### Phase 5: Performance Optimization

#### 5.1 Asset Optimization
**Images**:
- Convert JPEG to WebP with fallbacks
- Implement responsive images (`srcset`)
- Add lazy loading (`loading="lazy"`)
- Compress: `dance-1.jpeg` (460KB → ~100KB), etc.

**Videos**:
- Already externally hosted (good)
- Add poster frames for immediate visual
- Implement intersection observer for playback

**Fonts**:
- Self-host fonts (reduce external requests)
- Use `font-display: swap`
- Subset fonts (Latin only)

#### 5.2 Build Pipeline
**Implement Vite build process**:
```javascript
// vite.config.js
export default {
  build: {
    cssMinify: true,
    rollupOptions: {
      output: {
        assetFileNames: 'assets/[name]-[hash][extname]'
      }
    }
  },
  css: {
    preprocessorOptions: {
      // If using SCSS
    }
  }
}
```

**Benefits**:
- CSS/JS minification
- Cache busting via hashing
- Tree shaking
- Source maps for debugging

#### 5.3 Critical CSS
- Extract above-fold CSS inline
- Defer non-critical CSS loading
- Use `@import` or build tool for splitting

---

### Phase 6: Feature Enhancements

#### 6.1 Contact Form Implementation
**Replace external links with actual form**:
- Name, email, message fields
- Form validation (client + server)
- CSRF protection (Django)
- Email notification integration
- Success/error states

#### 6.2 Class Schedule Enhancements
- Add filter by class level
- Implement "Add to Calendar" buttons
- Show instructor for each class
- Add class capacity/availability indicator

#### 6.3 PWA Capabilities (Optional)
- Service worker for offline support
- Push notifications for class reminders
- Install prompt for mobile
- Manifest already exists (`site.webmanifest`)

---

## Implementation Roadmap (Phased with PRs)

---

### PHASE 1: Foundation & Cleanup
**Goal**: Clean architecture, remove technical debt, establish CSS foundation

#### PR 1.1: Remove Express.js (Architecture Consolidation)
**Scope**: Remove all Express-related code, consolidate to Django only
**Files to Delete**:
- `server.js`
- `routes/index.js`
- `data/events.js`
- `tests/routes.test.js`
- `tests/data.test.js`

**Files to Update**:
- `package.json` - Remove Express dependencies (express, helmet, morgan, cors, compression, ejs, express-ejs-layouts)
- Keep: Node.js dev tooling (eslint, prettier, jest for future frontend tests)

**Verification**: Site continues to work via Django on Vercel

---

#### PR 1.2: CSS Design Tokens
**Scope**: Implement CSS custom properties system
**Files to Create**:
- `public/css/base/variables.css` - Design tokens

**Files to Update**:
- `public/css/styles.css` - Replace hardcoded values with `var(--token-name)`
- `views/layout.ejs` - Add import for variables.css

**Tokens to Define**:
```css
:root {
  /* Colors */
  --color-primary: rgb(191, 170, 101);
  --color-background: #000000;
  --color-text: #ffffff;
  --color-text-muted: rgba(255, 255, 255, 0.7);

  /* Typography */
  --font-display: 'Playfair Display', serif;
  --font-body: 'Inter', system-ui, sans-serif;

  /* Spacing scale */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 1rem;
  --space-4: 1.5rem;
  --space-5: 2rem;
  --space-6: 3rem;
  --space-7: 4rem;

  /* Typography scale */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 2rem;
  --text-4xl: 2.5rem;

  /* Effects */
  --transition-fast: 150ms ease;
  --transition-normal: 300ms ease;
  --shadow-sm: 0 2px 4px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 8px rgba(0,0,0,0.4);
  --shadow-lg: 0 8px 16px rgba(0,0,0,0.5);
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
}
```

---

#### PR 1.3: Remove Bootstrap & Critical A11y
**Scope**: Remove Bootstrap CDN, add accessibility foundations
**Files to Update**:
- `views/layout.ejs`:
  - Remove Bootstrap CSS/JS CDN links
  - Add skip-to-content link
  - Add Inter font from Google Fonts
  - Fix nav `aria-expanded` attribute
- `public/css/styles.css`:
  - Add `.sr-only` utility class
  - Add `:focus-visible` states for all interactive elements
  - Replace any Bootstrap utility classes with custom equivalents

---

### PHASE 2: CSS Architecture & Modularization
**Goal**: Split monolithic CSS, improve maintainability

#### PR 2.1: CSS Module Structure
**Scope**: Split 974-line CSS into logical modules
**New File Structure**:
```
public/css/
├── base/
│   ├── variables.css    (from PR 1.2)
│   ├── reset.css        # Modern CSS reset
│   └── typography.css   # Font definitions, text utilities
├── components/
│   ├── buttons.css      # .btn variants
│   ├── cards.css        # .event-card, .class-preview, etc.
│   ├── navigation.css   # Header, hamburger, footer
│   └── gallery.css      # Video/image gallery styles
├── layouts/
│   ├── grid.css         # Grid utilities, containers
│   └── sections.css     # Page section patterns
└── main.css             # @import orchestrator
```

**Files to Update**:
- `views/layout.ejs` - Link to `main.css` instead of `styles.css`

---

#### PR 2.2: Responsive Design Refinements
**Scope**: Improve breakpoint system and mobile styles
**Changes**:
- Add consistent breakpoint variables (CSS custom media queries or documented values)
- Ensure mobile-first approach throughout
- Add proper touch targets (44px minimum)
- Fix any mobile layout issues identified in analysis

---

### PHASE 3: UI Uplift - Components
**Goal**: Modern component patterns with enhanced interactions

#### PR 3.1: Navigation Enhancements
**Scope**: Improve mobile menu UX and header behavior
**Changes**:
- Add visible close button (X) to mobile menu
- Implement backdrop blur on header when scrolling
- Add active page indicator in navigation
- Add keyboard navigation support (Escape to close menu)
- Implement focus trap within open mobile menu

**Files to Update**:
- `public/css/components/navigation.css`
- `views/layout.ejs` - Add close button markup
- `public/js/main.js` - Add scroll detection, focus trap

---

#### PR 3.2: Card & Button System
**Scope**: Modern card patterns with depth and refined buttons
**Changes**:
- Add glassmorphism effect to cards (subtle `backdrop-filter: blur()`)
- Implement layered shadow system (elevation on hover)
- Add gradient border accents
- Enhance button hover/focus/active states
- Add button loading spinner variant
- Add icon button variants

**Files to Update**:
- `public/css/components/cards.css`
- `public/css/components/buttons.css`

---

#### PR 3.3: Gallery & Media Enhancements
**Scope**: Improved video/image presentation
**Changes**:
- Add video poster frames for immediate visual
- Implement lazy loading for below-fold media
- Add subtle grain texture overlay to hero (premium feel)
- Enhance gallery hover overlays with smoother transitions

**Files to Update**:
- `views/home.ejs` - Add poster attributes, loading="lazy"
- `public/css/components/gallery.css`

---

### PHASE 4: UI Uplift - Animations & Polish
**Goal**: Micro-interactions and scroll-based animations

#### PR 4.1: Micro-Interactions
**Scope**: Subtle animations that enhance UX
**Changes**:
- Button ripple/click feedback effect
- Card hover lift with progressive shadow
- Menu item slide-in animation refinements
- Link underline reveal animations
- Input field focus animations (future forms)

**Implementation**: CSS animations + minimal JS
**Files to Update**:
- `public/css/components/buttons.css`
- `public/css/components/cards.css`
- `public/css/components/navigation.css`

---

#### PR 4.2: Scroll Animations
**Scope**: Intersection Observer-based reveal animations
**Changes**:
- Fade-in-up animation for sections on scroll
- Staggered entrance for card grids
- Parallax effect on hero video (subtle)
- Text reveal animation on page load

**Files to Create**:
- `public/js/animations.js` - Intersection Observer setup

**Files to Update**:
- `views/*.ejs` - Add `data-animate` attributes to animatable elements
- `public/css/base/animations.css` - Animation keyframes

---

### PHASE 5: Performance & Optimization
**Goal**: Fast loading, optimized assets

#### PR 5.1: Image Optimization
**Scope**: Modern image formats and responsive images
**Changes**:
- Convert JPEG images to WebP with fallbacks
- Implement `srcset` for responsive image sizes
- Add `loading="lazy"` to below-fold images
- Compress images (target: 100KB max per image)

**Files to Update**:
- All `views/*.ejs` files with images
- Image files in `public/images/`

---

#### PR 5.2: Font & Asset Optimization
**Scope**: Self-hosted fonts, reduced external requests
**Changes**:
- Self-host Playfair Display and Inter fonts
- Use `font-display: swap` for text visibility
- Subset fonts to Latin characters only
- Remove Font Awesome CDN (replace with inline SVGs or custom icons)

**Files to Update**:
- `views/layout.ejs` - Update font loading strategy
- `public/css/base/typography.css` - Add @font-face rules

---

#### PR 5.3: Build Pipeline Setup
**Scope**: Vite build process for CSS/JS optimization
**Files to Create**:
- `vite.config.js` - Build configuration
- Update `package.json` scripts

**Benefits**:
- CSS minification
- JS bundling and minification
- Cache-busting via content hashing
- Source maps for debugging

---

### PHASE 6: Features & Polish
**Goal**: New functionality and final refinements

#### PR 6.1: Contact Form Implementation
**Scope**: Replace external links with actual form
**Changes**:
- Add contact form to `views/contact.ejs`
- Create form handler in Django `core/views.py`
- Implement form validation (client + server)
- Add CSRF protection
- Success/error state feedback

**Files to Update**:
- `views/contact.ejs`
- `core/views.py`
- `core/urls.py`
- `public/css/components/forms.css`

---

#### PR 6.2: Dependency Audit & Cleanup
**Scope**: Reduce npm dependencies from 957 to ~50-100
**Changes**:
- Audit all npm packages
- Remove unused build tools (choose Vite, remove webpack/rollup)
- Remove unused test tools (keep Jest or Vitest, not both)
- Remove unused CSS tools (PostCSS ecosystem if not needed)
- Update remaining packages to latest versions

---

#### PR 6.3: Final A11y & Polish
**Scope**: Complete accessibility audit and final touches
**Changes**:
- Video captions/transcripts
- Full keyboard navigation audit
- Screen reader testing
- Color contrast verification (WCAG AA)
- SEO meta tags audit
- Open Graph tags for social sharing

---

## Critical Files Reference

### Files to Modify
- `public/css/styles.css` → Split into modules
- `views/layout.ejs` → Add skip link, fix nav A11y
- `views/home.ejs` → Video poster frames, lazy loading
- `views/contact.ejs` → Add contact form
- `core/views.py` → Centralize data, form handling

### Files to Remove
- `server.js` (Express server)
- `routes/index.js` (Express routes)
- `data/events.js` (duplicate data)
- `tests/routes.test.js` (Express tests)
- `tests/data.test.js` (Express tests)

### New Files to Create
- `public/css/base/variables.css`
- `public/css/components/*.css` (modular components)
- `data/events.json` (single source of truth)
- `vite.config.js` (build configuration)

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Lighthouse Performance | ~60 | 90+ |
| Lighthouse Accessibility | ~75 | 95+ |
| CSS file size | 974 lines/1 file | ~800 lines/10+ modules |
| npm dependencies | 957 | <100 |
| First Contentful Paint | ~2.5s | <1.5s |
| Time to Interactive | ~4s | <2.5s |

---

## Design Direction Summary

The modernization maintains the sophisticated **gold-on-black luxury aesthetic** while adding:

1. **Depth & Dimension** - Layered shadows, glassmorphism, parallax
2. **Motion & Life** - Smooth micro-interactions, scroll animations
3. **Clarity & Focus** - Cleaner typography, better spacing, modular components
4. **Accessibility** - Inclusive design for all users
5. **Performance** - Fast loading, optimized assets

The result: A modern, accessible, performant website that preserves the brand's premium positioning while providing an excellent user experience across all devices.
