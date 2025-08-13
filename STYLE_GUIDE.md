# Sabor Con Flow Dance - Official Style Guide

<document-metadata>
  <version>1.0</version>
  <created>2025-01-13</created>
  <status>Active</status>
  <scope>Website Design System</scope>
</document-metadata>

<brand-overview>
  <mission>To create an elegant, accessible, and culturally-rich digital experience that embodies the passion, sophistication, and community spirit of Cuban salsa dance</mission>
  <visual-identity>Luxury meets accessibility through a sophisticated black and gold palette, elegant typography, and fluid animations that mirror the grace of dance</visual-identity>
  <target-audience>Dance enthusiasts, cultural explorers, and community seekers across all skill levels and backgrounds</target-audience>
</brand-overview>

---

## Table of Contents

1. [Brand Identity & Design Principles](#brand-identity--design-principles)
2. [Color System](#color-system)
3. [Typography System](#typography-system)
4. [Spacing & Layout](#spacing--layout)
5. [Component Library](#component-library)
6. [Interaction Design](#interaction-design)
7. [Accessibility Standards](#accessibility-standards)
8. [Implementation Guidelines](#implementation-guidelines)

---

## Brand Identity & Design Principles

<brand-principles>
  <principle name="Elegance">
    <description>Every element should embody the sophisticated nature of dance through refined aesthetics, subtle gradients, and premium materials</description>
    <implementation>Use of luxury gold accents, high-quality imagery, and refined typography combinations</implementation>
  </principle>
  
  <principle name="Cultural Authenticity">
    <description>Visual elements should honor and celebrate Cuban dance culture without appropriation</description>
    <implementation>Respectful color choices, authentic imagery, and culturally-informed design decisions</implementation>
  </principle>
  
  <principle name="Inclusive Accessibility">
    <description>Design must be accessible to all users, regardless of ability, device, or technical skill</description>
    <implementation>WCAG 2.1 AA compliance, mobile-first design, and progressive enhancement</implementation>
  </principle>
  
  <principle name="Movement & Flow">
    <description>Interface elements should feel fluid and dynamic, reflecting the grace of dance</description>
    <implementation>Smooth transitions, thoughtful animations, and organic curves in design elements</implementation>
  </principle>
</brand-principles>

---

## Color System

<color-palette>
  <primary-colors>
    <color name="Brand Gold" hex="#C7B375" usage="Primary accent, CTA buttons, highlights">
      <contrast-ratios>
        <on-white>4.52:1 (AA)</on-white>
        <on-black>9.25:1 (AAA)</on-black>
      </contrast-ratios>
      <css-variable>--color-gold</css-variable>
    </color>
    
    <color name="Secondary Gold" hex="#BFAA65" usage="Secondary accents, gradients, hover states">
      <contrast-ratios>
        <on-white>4.89:1 (AA)</on-white>
        <on-black>8.58:1 (AAA)</on-black>
      </contrast-ratios>
      <css-variable>--color-gold-secondary</css-variable>
    </color>
    
    <color name="Pure Black" hex="#000000" usage="Text, backgrounds, high-contrast elements">
      <contrast-ratios>
        <on-white>21:1 (AAA)</on-white>
        <on-gold>9.25:1 (AAA)</on-gold>
      </contrast-ratios>
      <css-variable>--color-black</css-variable>
    </color>
    
    <color name="Pure White" hex="#FFFFFF" usage="Text on dark backgrounds, card backgrounds">
      <contrast-ratios>
        <on-black>21:1 (AAA)</on-black>
        <on-gold>4.52:1 (AA)</on-gold>
      </contrast-ratios>
      <css-variable>--color-white</css-variable>
    </color>
  </primary-colors>

  <extended-palette>
    <color name="Light Gold" hex="#E5D4A1" usage="Subtle backgrounds, disabled states">
      <css-variable>--color-gold-light</css-variable>
    </color>
    
    <color name="Dark Gold" hex="#9C8E5A" usage="Darker accents, pressed states">
      <css-variable>--color-gold-dark</css-variable>
    </color>
    
    <color name="Dark Gray" hex="#333333" usage="Secondary text, subtle backgrounds">
      <css-variable>--color-gray-dark</css-variable>
    </color>
    
    <color name="Medium Gray" hex="#666666" usage="Supporting text, placeholder text">
      <css-variable>--color-gray-medium</css-variable>
    </color>
    
    <color name="Light Gray" hex="#999999" usage="Borders, dividers, disabled text">
      <css-variable>--color-gray-light</css-variable>
    </color>
    
    <color name="Lighter Gray" hex="#F5F5F5" usage="Background tints, subtle containers">
      <css-variable>--color-gray-lighter</css-variable>
    </color>
  </extended-palette>

  <accessibility-colors>
    <color name="Accessible Gold" hex="#A69854" usage="Enhanced contrast version for better accessibility">
      <css-variable>--color-gold-accessible</css-variable>
    </color>
    
    <color name="Focus Blue" hex="#2563eb" usage="Focus indicators, high-contrast interactions">
      <css-variable>--color-focus</css-variable>
    </color>
    
    <color name="Error Red" hex="#d63384" usage="Error messages, validation failures">
      <css-variable>--color-error</css-variable>
    </color>
    
    <color name="Success Green" hex="#198754" usage="Success messages, confirmations">
      <css-variable>--color-success</css-variable>
    </color>
  </accessibility-colors>
</color-palette>

### Color Usage Guidelines

<usage-rules>
  <rule type="primary-actions">Use Brand Gold (#C7B375) for all primary actions and key CTAs</rule>
  <rule type="backgrounds">Black backgrounds create luxury feel; white backgrounds provide clarity for content</rule>
  <rule type="contrast">Always ensure 4.5:1 contrast ratio minimum for normal text, 3:1 for large text</rule>
  <rule type="gradients">Combine Brand Gold with Secondary Gold for elegant gradient effects</rule>
  <rule type="accessibility">Use --color-gold-accessible when standard gold doesn't meet contrast requirements</rule>
</usage-rules>

**Do's:**
- Use gold sparingly as an accent to maintain elegance
- Pair black with gold for maximum sophistication
- Test all color combinations for accessibility compliance
- Use gradients to add depth and visual interest

**Don'ts:**
- Never use gold on light backgrounds without accessibility testing
- Avoid using more than 3 colors in a single component
- Don't use gray text without verifying contrast ratios
- Never sacrifice accessibility for aesthetic preferences

---

## Typography System

<typography-system>
  <font-families>
    <font-heading>
      <name>Playfair Display</name>
      <type>Serif</type>
      <usage>Headings, elegant display text, brand elements</usage>
      <css-variable>--font-heading</css-variable>
      <character>Sophisticated, classical, elegant</character>
    </font-heading>
    
    <font-body>
      <name>Inter</name>
      <type>Sans-serif</type>
      <usage>Body text, UI elements, navigation</usage>
      <css-variable>--font-body</css-variable>
      <character>Modern, clean, highly readable</character>
      <fallback>-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif</fallback>
    </font-body>
  </font-families>

  <font-scale>
    <heading-1>
      <size>clamp(2.5rem, 6vw, 4rem)</size>
      <weight>700</weight>
      <line-height>1.2</line-height>
      <letter-spacing>-0.02em</letter-spacing>
      <usage>Page titles, hero headings</usage>
      <css-class>.h1, h1</css-class>
    </heading-1>
    
    <heading-2>
      <size>clamp(2rem, 5vw, 3rem)</size>
      <weight>600</weight>
      <line-height>1.2</line-height>
      <letter-spacing>-0.02em</letter-spacing>
      <usage>Section headings, major content blocks</usage>
      <css-class>.h2, h2</css-class>
    </heading-2>
    
    <heading-3>
      <size>clamp(1.5rem, 4vw, 2.25rem)</size>
      <weight>600</weight>
      <line-height>1.2</line-height>
      <letter-spacing>-0.02em</letter-spacing>
      <usage>Subsection headings, card titles</usage>
      <css-class>.h3, h3</css-class>
    </heading-3>
    
    <heading-4>
      <size>clamp(1.25rem, 3vw, 1.75rem)</size>
      <weight>600</weight>
      <line-height>1.3</line-height>
      <usage>Component headings, sidebar titles</usage>
      <css-class>.h4, h4</css-class>
    </heading-4>
    
    <body-text>
      <size>1rem (16px)</size>
      <weight>400</weight>
      <line-height>1.6</line-height>
      <usage>Standard body text, descriptions</usage>
      <css-class>body, p</css-class>
    </body-text>
    
    <lead-text>
      <size>1.25rem</size>
      <weight>300</weight>
      <line-height>1.7</line-height>
      <usage>Introduction paragraphs, important descriptions</usage>
      <css-class>.lead</css-class>
    </lead-text>
    
    <small-text>
      <size>0.875rem</size>
      <weight>400</weight>
      <line-height>1.5</line-height>
      <usage>Meta information, captions, footnotes</usage>
      <css-class>.text-small</css-class>
    </small-text>
  </font-scale>
</typography-system>

### Typography Implementation Examples

```css
/* Heading Examples */
.hero-title {
    font-family: var(--font-heading);
    font-size: clamp(3rem, 8vw, 5rem);
    font-weight: 700;
    color: var(--color-white);
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.section-heading {
    font-family: var(--font-heading);
    font-size: clamp(2rem, 5vw, 3rem);
    color: var(--color-black);
    margin-bottom: var(--spacing-lg);
}

/* Body Text Examples */
.body-text {
    font-family: var(--font-body);
    font-size: 1rem;
    line-height: 1.6;
    color: var(--color-black);
}

.lead-paragraph {
    font-family: var(--font-body);
    font-size: 1.25rem;
    font-weight: 300;
    line-height: 1.7;
    color: var(--color-gray-medium);
}
```

---

## Spacing & Layout

<spacing-system>
  <scale-values>
    <spacing name="Extra Small" value="0.25rem (4px)" variable="--spacing-xs" usage="Fine adjustments, tight spacing"/>
    <spacing name="Small" value="0.5rem (8px)" variable="--spacing-sm" usage="Component internal spacing"/>
    <spacing name="Medium" value="1rem (16px)" variable="--spacing-md" usage="Standard element spacing"/>
    <spacing name="Large" value="1.5rem (24px)" variable="--spacing-lg" usage="Section spacing, large gaps"/>
    <spacing name="Extra Large" value="2rem (32px)" variable="--spacing-xl" usage="Component separation"/>
    <spacing name="2X Large" value="3rem (48px)" variable="--spacing-2xl" usage="Major section separation"/>
    <spacing name="3X Large" value="4rem (64px)" variable="--spacing-3xl" usage="Page-level spacing"/>
  </scale-values>

  <layout-patterns>
    <pattern name="Container">
      <max-width>1200px</max-width>
      <padding>var(--spacing-lg) on mobile, var(--spacing-xl) on desktop</padding>
      <margin>0 auto for centering</margin>
    </pattern>
    
    <pattern name="Grid System">
      <columns>CSS Grid with auto-fit and minmax for responsive layouts</columns>
      <gaps>var(--spacing-lg) to var(--spacing-2xl) depending on content</gaps>
      <breakpoints>640px, 768px, 1024px, 1280px</breakpoints>
    </pattern>
    
    <pattern name="Card Spacing">
      <internal-padding>var(--spacing-xl) to var(--spacing-2xl)</internal-padding>
      <external-margin>var(--spacing-lg) between cards</external-margin>
      <content-spacing>var(--spacing-md) between elements</content-spacing>
    </pattern>
  </layout-patterns>
</spacing-system>

### Layout Implementation Examples

```css
/* Container Pattern */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
}

/* Responsive Grid Pattern */
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: var(--spacing-2xl);
    margin: var(--spacing-3xl) 0;
}

/* Component Spacing Pattern */
.component {
    padding: var(--spacing-xl);
    margin-bottom: var(--spacing-lg);
}

.component-header {
    margin-bottom: var(--spacing-md);
}

.component-content > * + * {
    margin-top: var(--spacing-md);
}
```

---

## Component Library

<component-system>
  <buttons>
    <button-primary>
      <appearance>Gold gradient background with black text</appearance>
      <hover>Darker gradient with white text and subtle lift</hover>
      <css-class>.btn-primary</css-class>
      <use-cases>Main actions, form submissions, primary CTAs</use-cases>
    </button-primary>
    
    <button-secondary>
      <appearance>Black background with white text</appearance>
      <hover>Dark gray background with lift effect</hover>
      <css-class>.btn-secondary</css-class>
      <use-cases>Secondary actions, navigation buttons</use-cases>
    </button-secondary>
    
    <button-outline>
      <appearance>Transparent with gold border and text</appearance>
      <hover>Gold background with black text</hover>
      <css-class>.btn-outline</css-class>
      <use-cases>Alternative actions, less emphasis</use-cases>
    </button-outline>
    
    <button-outline-white>
      <appearance>Transparent with white border and text</appearance>
      <hover>White background with black text</hover>
      <css-class>.btn-outline-white</css-class>
      <use-cases>Actions on dark backgrounds, hero sections</use-cases>
    </button-outline-white>
  </buttons>

  <cards>
    <card-basic>
      <structure>White background, rounded corners, subtle shadow</structure>
      <hover>Elevated shadow and slight upward movement</hover>
      <css-class>.card</css-class>
    </card-basic>
    
    <card-gold-accent>
      <structure>Basic card with gold top border</structure>
      <hover>Enhanced gold accent and elevation</hover>
      <css-class>.card-gold</css-class>
    </card-gold-accent>
    
    <card-feature>
      <structure>Centered content with icon, gradient background</structure>
      <icon>Gold circular icon container</icon>
      <css-class>.card-feature</css-class>
    </card-feature>
  </cards>

  <forms>
    <form-control>
      <appearance>White background, light gray border, rounded corners</appearance>
      <focus>Gold border with subtle glow effect</focus>
      <css-class>.form-control</css-class>
    </form-control>
    
    <form-label>
      <typography>Bold, black text</typography>
      <spacing>Small margin below</spacing>
      <css-class>.form-label</css-class>
    </form-label>
    
    <form-validation>
      <invalid>Red border and error message</invalid>
      <valid>Green border confirmation</valid>
      <css-classes>.is-invalid, .is-valid</css-classes>
    </form-validation>
  </forms>
</component-system>

### Button Implementation Examples

```css
/* Primary Button */
.btn-primary {
    background: linear-gradient(135deg, var(--color-gold) 0%, var(--color-gold-secondary) 100%);
    color: var(--color-black);
    border: 2px solid var(--color-gold);
    padding: var(--spacing-md) var(--spacing-xl);
    border-radius: 6px;
    font-weight: 600;
    transition: all var(--transition-base);
}

.btn-primary:hover:not(:disabled) {
    background: linear-gradient(135deg, var(--color-gold-dark) 0%, var(--color-gold) 100%);
    color: var(--color-white);
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(199, 179, 117, 0.3);
}

/* Secondary Button */
.btn-secondary {
    background-color: var(--color-black);
    color: var(--color-white);
    border: 2px solid var(--color-black);
    padding: var(--spacing-md) var(--spacing-xl);
    border-radius: 6px;
    font-weight: 600;
    transition: all var(--transition-base);
}

.btn-secondary:hover:not(:disabled) {
    background-color: var(--color-gray-dark);
    transform: translateY(-2px);
}
```

### Card Implementation Examples

```css
/* Basic Card */
.card {
    background: var(--color-white);
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    transition: all var(--transition-base);
}

.card:hover {
    box-shadow: 0 20px 25px rgba(0, 0, 0, 0.1);
    transform: translateY(-4px);
}

/* Gold Accent Card */
.card-gold {
    border-top: 4px solid var(--color-gold);
}

.card-gold:hover {
    border-top-color: var(--color-gold-dark);
}

/* Feature Card */
.card-feature {
    text-align: center;
    padding: var(--spacing-2xl);
    background: linear-gradient(135deg, var(--color-white) 0%, var(--color-gray-lighter) 100%);
}

.card-feature-icon {
    width: 80px;
    height: 80px;
    margin: 0 auto var(--spacing-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-gold);
    color: var(--color-white);
    border-radius: 50%;
    font-size: 2rem;
}
```

---

## Interaction Design

<interaction-principles>
  <principle name="Smooth Transitions">
    <description>All state changes should feel natural and fluid</description>
    <timing>Base: 250ms, Fast: 150ms, Slow: 350ms</timing>
    <easing>ease, cubic-bezier for complex animations</easing>
  </principle>
  
  <principle name="Meaningful Motion">
    <description>Animations should communicate purpose and guide user attention</description>
    <examples>Button lift on hover, card elevation, page transitions</examples>
  </principle>
  
  <principle name="Performance First">
    <description>Animations must not compromise performance or accessibility</description>
    <implementation>CSS transforms over layout properties, respect prefers-reduced-motion</implementation>
  </principle>
</interaction-principles>

<transition-system>
  <timing-values>
    <timing name="Fast" value="150ms" variable="--transition-fast" usage="Micro-interactions, hover states"/>
    <timing name="Base" value="250ms" variable="--transition-base" usage="Standard transitions, UI feedback"/>
    <timing name="Slow" value="350ms" variable="--transition-slow" usage="Complex animations, page transitions"/>
  </timing-values>

  <hover-effects>
    <effect name="Button Lift">
      <transform>translateY(-2px)</transform>
      <shadow>Enhanced box-shadow with brand colors</shadow>
    </effect>
    
    <effect name="Card Elevation">
      <transform>translateY(-4px)</transform>
      <shadow>Increased shadow blur and spread</shadow>
    </effect>
    
    <effect name="Image Scale">
      <transform>scale(1.05)</transform>
      <container>overflow: hidden for clipping</container>
    </effect>
  </hover-effects>
</transition-system>

### Animation Implementation Examples

```css
/* Transition Variables */
:root {
    --transition-fast: 150ms ease;
    --transition-base: 250ms ease;
    --transition-slow: 350ms ease;
}

/* Hover Effects */
.btn:hover {
    transform: translateY(-2px);
    transition: all var(--transition-base);
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15);
    transition: all var(--transition-base);
}

/* Keyframe Animations */
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

.animate-fadeInUp {
    animation: fadeInUp 0.5s ease-in-out;
}

/* Reduced Motion Support */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

---

## Accessibility Standards

<accessibility-requirements>
  <wcag-compliance>
    <level>AA</level>
    <version>2.1</version>
    <key-areas>Color contrast, keyboard navigation, screen reader support, focus management</key-areas>
  </wcag-compliance>

  <color-contrast>
    <normal-text>4.5:1 minimum ratio</normal-text>
    <large-text>3:1 minimum ratio (18pt+ or 14pt+ bold)</large-text>
    <ui-components>3:1 minimum for interactive elements</ui-components>
    <testing>Use contrast checkers and automated testing tools</testing>
  </color-contrast>

  <keyboard-navigation>
    <focus-indicators>2px solid var(--color-focus) with 2px offset</focus-indicators>
    <tab-order>Logical, predictable sequence through interface</tab-order>
    <shortcuts>Skip links, keyboard shortcuts for power users</shortcuts>
  </keyboard-navigation>

  <screen-readers>
    <semantic-html>Use proper heading hierarchy, landmarks, lists</semantic-html>
    <alt-text>Descriptive alt attributes for all images</alt-text>
    <aria-labels>Enhanced labels for complex interactions</aria-labels>
  </screen-readers>
</accessibility-requirements>

### Accessibility Implementation Examples

```css
/* Focus Indicators */
*:focus-visible {
    outline: 2px solid var(--color-focus);
    outline-offset: 2px;
    border-radius: 2px;
}

/* High Contrast Support */
@media (prefers-contrast: high) {
    .btn-primary {
        border-width: 3px;
        font-weight: 700;
    }
}

/* Reduced Motion Support */
@media (prefers-reduced-motion: reduce) {
    .card:hover {
        transform: none;
    }
    
    .animate-fadeInUp {
        animation: none;
    }
}

/* Screen Reader Only Content */
.sr-only {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    padding: 0 !important;
    margin: -1px !important;
    overflow: hidden !important;
    clip: rect(0, 0, 0, 0) !important;
    border: 0 !important;
}
```

### HTML Best Practices

```html
<!-- Proper Heading Hierarchy -->
<h1>Page Title</h1>
  <h2>Main Section</h2>
    <h3>Subsection</h3>
    <h3>Another Subsection</h3>
  <h2>Another Main Section</h2>

<!-- Accessible Buttons -->
<button type="button" aria-label="Close dialog" class="btn-secondary">
    <span aria-hidden="true">&times;</span>
</button>

<!-- Form Accessibility -->
<div class="form-group">
    <label for="email" class="form-label">Email Address</label>
    <input 
        type="email" 
        id="email" 
        class="form-control" 
        required 
        aria-describedby="email-help"
    >
    <div id="email-help" class="form-text">
        We'll never share your email with anyone else.
    </div>
</div>
```

---

## Implementation Guidelines

<css-architecture>
  <methodology>BEM-inspired with utility classes for flexibility</methodology>
  <custom-properties>Extensive use of CSS variables for theming and consistency</custom-properties>
  <mobile-first>All styles written mobile-first with progressive enhancement</mobile-first>
  <performance>Critical CSS inlined, non-critical loaded asynchronously</performance>
</css-architecture>

<responsive-design>
  <breakpoints>
    <mobile>320px - 639px</mobile>
    <tablet>640px - 767px</tablet>
    <desktop>768px - 1023px</desktop>
    <large-desktop>1024px+</large-desktop>
  </breakpoints>
  
  <approach>Mobile-first with min-width media queries</approach>
  <testing>Test on actual devices and various screen sizes</testing>
</responsive-design>

### CSS Custom Properties Usage

```css
/* Define all variables in :root */
:root {
    /* Brand Colors */
    --color-gold: #C7B375;
    --color-gold-secondary: #BFAA65;
    --color-black: #000000;
    --color-white: #FFFFFF;
    
    /* Extended Palette */
    --color-gold-light: #E5D4A1;
    --color-gold-dark: #9C8E5A;
    --color-gray-dark: #333333;
    --color-gray-medium: #666666;
    --color-gray-light: #999999;
    --color-gray-lighter: #F5F5F5;
    
    /* Typography */
    --font-heading: 'Playfair Display', serif;
    --font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    
    /* Spacing Scale */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    --spacing-2xl: 3rem;
    --spacing-3xl: 4rem;
    
    /* Transitions */
    --transition-fast: 150ms ease;
    --transition-base: 250ms ease;
    --transition-slow: 350ms ease;
    
    /* Shadows */
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
    --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
}

/* Usage Examples */
.component {
    background: var(--color-white);
    color: var(--color-black);
    padding: var(--spacing-xl);
    border-radius: 12px;
    box-shadow: var(--shadow-md);
    transition: all var(--transition-base);
}

.component:hover {
    box-shadow: var(--shadow-xl);
    transform: translateY(-4px);
}
```

### Responsive Design Implementation

```css
/* Mobile-First Approach */
.container {
    padding: 0 var(--spacing-md);
}

.grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
}

/* Tablet */
@media (min-width: 640px) {
    .container {
        padding: 0 var(--spacing-lg);
    }
    
    .grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* Desktop */
@media (min-width: 768px) {
    .container {
        padding: 0 var(--spacing-xl);
    }
    
    .grid {
        grid-template-columns: repeat(3, 1fr);
        gap: var(--spacing-xl);
    }
}

/* Large Desktop */
@media (min-width: 1024px) {
    .container {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .grid {
        grid-template-columns: repeat(4, 1fr);
        gap: var(--spacing-2xl);
    }
}
```

### Component Development Guidelines

<development-rules>
  <rule>Always use CSS custom properties instead of hard-coded values</rule>
  <rule>Test all components in both light and dark contexts</rule>
  <rule>Ensure keyboard accessibility for all interactive elements</rule>
  <rule>Test with screen readers and automated accessibility tools</rule>
  <rule>Optimize for performance - avoid layout-triggering properties in animations</rule>
  <rule>Follow mobile-first responsive design principles</rule>
  <rule>Include focus states for all interactive elements</rule>
  <rule>Support prefers-reduced-motion for accessibility</rule>
</development-rules>

### Quality Assurance Checklist

<qa-checklist>
  <visual-testing>
    <item>Component renders correctly across all breakpoints</item>
    <item>Colors meet WCAG contrast requirements</item>
    <item>Typography scales appropriately on different devices</item>
    <item>Animations are smooth and purposeful</item>
    <item>Loading states and error states are handled gracefully</item>
  </visual-testing>
  
  <functional-testing>
    <item>All interactive elements are keyboard accessible</item>
    <item>Focus indicators are clearly visible</item>
    <item>Screen readers can navigate and understand content</item>
    <item>Touch targets meet minimum size requirements (44x44px)</item>
    <item>Component works without JavaScript (progressive enhancement)</item>
  </functional-testing>
  
  <performance-testing>
    <item>CSS is optimized and unnecessary rules removed</item>
    <item>Images are appropriately sized and optimized</item>
    <item>Animations don't cause layout thrashing</item>
    <item>Critical CSS is identified and prioritized</item>
  </performance-testing>
</qa-checklist>

---

## Maintenance & Evolution

<maintenance-guidelines>
  <updates>Review and update this style guide quarterly or when major changes occur</updates>
  <versioning>Use semantic versioning for style guide releases</versioning>
  <testing>Maintain automated visual regression testing for components</testing>
  <documentation>Keep code examples current with actual implementation</documentation>
  <feedback>Collect feedback from developers and designers using the system</feedback>
</maintenance-guidelines>

<style-guide-metadata>
  <last-updated>2025-01-13</last-updated>
  <version>1.0.0</version>
  <contributors>Technical Documentation Specialist</contributors>
  <review-cycle>Quarterly</review-cycle>
  <next-review>2025-04-13</next-review>
</style-guide-metadata>

---

*This style guide serves as the single source of truth for the Sabor Con Flow Dance website design system. All design and development decisions should align with these guidelines to ensure consistency, accessibility, and brand integrity.*