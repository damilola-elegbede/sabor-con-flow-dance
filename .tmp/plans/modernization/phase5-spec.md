# Phase 5: Performance and Optimization - Technical Specification

## Executive Summary

This specification details the implementation plan for Phase 5 of the Sabor Con Flow dance website
modernization. The phase focuses on three critical performance optimization areas: image
optimization, font and asset optimization, and build pipeline setup using Vite.

**Target Outcomes:**

- Reduce image payload by 60-70% (target: 100KB max per image)
- Eliminate render-blocking font resources
- Enable CSS/JS minification and cache-busting
- Achieve Lighthouse performance score of 90+

## Current State Analysis

### Codebase Architecture

The project has a **hybrid architecture**:

- **Node.js/Express** server (`server.js`) with EJS templates in `/views/`
- **Django** backend (`api/index.py`) with templates in `/templates/`
- **Vercel deployment** using Django for production (`vercel.json`)
- **WhiteNoise** for static file serving in production

### Image Inventory

| File | Location | Purpose | Estimated Size |
|------|----------|---------|----------------|
| `dance-1.jpeg` | `/static/images/` | Gallery - Technical Precision | ~460KB |
| `dance-3.jpeg` | `/static/images/` | Gallery - Music Integration | ~506KB |
| `dance-4.jpeg` | `/static/images/` | Gallery - Cuban Training | ~300KB |
| `sabor-con-flow-logo.png` | `/static/images/` | Header logo, About page | ~50KB |
| `sabor-con-flow-logo-2.png` | `/static/images/` | Favicon, logo variations | ~45KB |
| `pasos-basicos-animated.gif` | `/static/images/` | Hero animation (non-home) | ~800KB+ |
| `instructor-profile.jpg` | `/public/images/` | About page (if used) | ~389KB |

**Total estimated image payload: ~2.5MB+**

### Current Font Loading

From `/templates/base.html` (Django) and `/views/layout.ejs` (Express):

```html
<!-- Google Fonts CDN -->
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap"
      rel="stylesheet">

<!-- Font Awesome CDN -->
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
      rel="stylesheet">
```

**Issues Identified:**

1. Google Fonts loads entire character sets (Latin, Latin Extended, Vietnamese)
2. Font Awesome loads entire icon library (~1.5MB) for ~0 icons actually used
3. No `font-display: swap` explicit declaration
4. Render-blocking CSS resources

### Font Awesome Usage Audit

After comprehensive search of all templates:

| Template | Icons Used |
|----------|-----------|
| `base.html` | **None** - All social icons are inline SVGs |
| `home.html` | **None** |
| `contact.html` | **None** - Uses inline SVGs for email, WhatsApp, Instagram, Facebook |
| `events.html` | **None** - Uses emoji (calendar, clock, pin) |
| `pricing.html` | **None** |
| `private-lessons.html` | **None** |
| `layout.ejs` | **None** - All social icons are inline SVGs |

**Finding: Font Awesome CDN can be completely removed - zero icons are used from the library.**

### Current Build Pipeline

**No build pipeline exists.** Static files are served directly:

- CSS: `/static/css/styles.css` (unminified, ~657 lines)
- JS: Inline scripts in templates + Bootstrap CDN
- Images: Served as-is without optimization

**Current `package.json` scripts:**

```json
{
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "test": "jest",
    "test:watch": "jest --watch"
  }
}
```

### Vercel Build Process

From `/vercel.json`:

```json
{
  "version": 2,
  "buildCommand": "./vercel-build",
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb",
        "runtime": "python3.12"
      }
    }
  ]
}
```

From `/vercel-build`:

```bash
#!/bin/bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
```

**Django Static Configuration** (`sabor_con_flow/settings.py`):

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## PR 5.1: Image Optimization

### Objective

Convert all JPEG images to WebP format with JPEG fallbacks, implement responsive `srcset`, and add
lazy loading for below-fold images.

### Implementation Details

#### Step 1: Install Sharp for Image Processing

Sharp is already in `package.json`. Add optimization script:

```bash
# Verify sharp installation
npm ls sharp
```

#### Step 2: Image Conversion Script

Create `/scripts/optimize-images.js`:

```javascript
#!/usr/bin/env node
/**
 * Image Optimization Script for Sabor Con Flow
 * Converts JPEG/PNG to WebP with multiple responsive sizes
 */

const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const INPUT_DIR = path.join(__dirname, '../static/images');
const OUTPUT_DIR = path.join(__dirname, '../static/images/optimized');

// Responsive breakpoints for srcset
const SIZES = [
  { width: 320, suffix: '-320w' },
  { width: 640, suffix: '-640w' },
  { width: 960, suffix: '-960w' },
  { width: 1280, suffix: '-1280w' },
];

// Images to process with their configurations
const IMAGES = [
  {
    input: 'dance-1.jpeg',
    output: 'dance-1',
    maxWidth: 1280,
    quality: 80,
  },
  {
    input: 'dance-3.jpeg',
    output: 'dance-3',
    maxWidth: 1280,
    quality: 80,
  },
  {
    input: 'dance-4.jpeg',
    output: 'dance-4',
    maxWidth: 1280,
    quality: 80,
  },
  {
    input: 'sabor-con-flow-logo.png',
    output: 'logo',
    maxWidth: 500,
    quality: 90,
    preserveAlpha: true,
  },
  {
    input: 'sabor-con-flow-logo-2.png',
    output: 'logo-2',
    maxWidth: 500,
    quality: 90,
    preserveAlpha: true,
  },
];

async function ensureOutputDir() {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }
}

async function processImage(config) {
  const inputPath = path.join(INPUT_DIR, config.input);

  if (!fs.existsSync(inputPath)) {
    console.warn(`Warning: ${config.input} not found, skipping...`);
    return;
  }

  const image = sharp(inputPath);
  const metadata = await image.metadata();

  console.log(`Processing ${config.input} (${metadata.width}x${metadata.height})`);

  for (const size of SIZES) {
    if (size.width > metadata.width) continue;

    const webpOutput = path.join(OUTPUT_DIR, `${config.output}${size.suffix}.webp`);
    const jpegOutput = path.join(OUTPUT_DIR, `${config.output}${size.suffix}.jpg`);

    // WebP version
    await sharp(inputPath)
      .resize(size.width, null, { withoutEnlargement: true })
      .webp({ quality: config.quality })
      .toFile(webpOutput);

    // JPEG fallback
    await sharp(inputPath)
      .resize(size.width, null, { withoutEnlargement: true })
      .jpeg({ quality: config.quality, mozjpeg: true })
      .toFile(jpegOutput);

    const webpStats = fs.statSync(webpOutput);
    const jpegStats = fs.statSync(jpegOutput);

    console.log(`  ${size.width}w: WebP ${(webpStats.size / 1024).toFixed(1)}KB, ` +
                `JPEG ${(jpegStats.size / 1024).toFixed(1)}KB`);
  }

  // Create full-size optimized versions
  const webpFull = path.join(OUTPUT_DIR, `${config.output}.webp`);
  const jpegFull = path.join(OUTPUT_DIR, `${config.output}.jpg`);

  await sharp(inputPath)
    .resize(config.maxWidth, null, { withoutEnlargement: true })
    .webp({ quality: config.quality })
    .toFile(webpFull);

  await sharp(inputPath)
    .resize(config.maxWidth, null, { withoutEnlargement: true })
    .jpeg({ quality: config.quality, mozjpeg: true })
    .toFile(jpegFull);

  console.log(`  Full: Created optimized versions`);
}

async function main() {
  console.log('Starting image optimization...\n');

  await ensureOutputDir();

  for (const config of IMAGES) {
    await processImage(config);
    console.log('');
  }

  console.log('Image optimization complete!');
}

main().catch(console.error);
```

#### Step 3: Package.json Script Addition

```json
{
  "scripts": {
    "optimize:images": "node scripts/optimize-images.js",
    "prebuild": "npm run optimize:images"
  }
}
```

#### Step 4: Picture Element Implementation

Update `/templates/home.html`:

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}Home - Sabor Con Flow{% endblock %}

{% block content %}
<div class="video-showcase">
    <div class="video-container">
        <video class="showcase-video" autoplay muted loop playsinline preload="metadata"
               poster="{% static 'images/optimized/dance-1-640w.webp' %}">
            {% if hero_video_path %}
                {% if 'http' in hero_video_path %}
                    <source src="{{ hero_video_path }}" type="video/mp4">
                {% else %}
                    <source src="{% static hero_video_path %}" type="video/mp4">
                {% endif %}
            {% endif %}
            Your browser does not support the video tag.
        </video>
    </div>
    <div class="video-container">
        <video class="showcase-video" autoplay muted loop playsinline preload="metadata"
               poster="{% static 'images/optimized/dance-3-640w.webp' %}">
            {% if second_video_path %}
                {% if 'http' in second_video_path %}
                    <source src="{{ second_video_path }}" type="video/mp4">
                {% else %}
                    <source src="{% static second_video_path %}" type="video/mp4">
                {% endif %}
            {% endif %}
            Your browser does not support the video tag.
        </video>
    </div>
</div>

<div class="dance-photos">
    <div class="photo-container" style="aspect-ratio: 0.61;">
        <picture>
            <source type="image/webp"
                    srcset="{% static 'images/optimized/dance-1-320w.webp' %} 320w,
                            {% static 'images/optimized/dance-1-640w.webp' %} 640w,
                            {% static 'images/optimized/dance-1-960w.webp' %} 960w,
                            {% static 'images/optimized/dance-1-1280w.webp' %} 1280w"
                    sizes="(max-width: 600px) 90vw, (max-width: 768px) 45vw, 440px">
            <source type="image/jpeg"
                    srcset="{% static 'images/optimized/dance-1-320w.jpg' %} 320w,
                            {% static 'images/optimized/dance-1-640w.jpg' %} 640w,
                            {% static 'images/optimized/dance-1-960w.jpg' %} 960w,
                            {% static 'images/optimized/dance-1-1280w.jpg' %} 1280w"
                    sizes="(max-width: 600px) 90vw, (max-width: 768px) 45vw, 440px">
            <img src="{% static 'images/optimized/dance-1-640w.jpg' %}"
                 alt="Technical Precision Cuban Dance"
                 class="dance-photo"
                 width="440"
                 height="722"
                 loading="lazy"
                 decoding="async">
        </picture>
    </div>
    <div class="photo-container" style="aspect-ratio: 0.61;">
        <picture>
            <source type="image/webp"
                    srcset="{% static 'images/optimized/dance-3-320w.webp' %} 320w,
                            {% static 'images/optimized/dance-3-640w.webp' %} 640w,
                            {% static 'images/optimized/dance-3-960w.webp' %} 960w,
                            {% static 'images/optimized/dance-3-1280w.webp' %} 1280w"
                    sizes="(max-width: 600px) 90vw, (max-width: 768px) 45vw, 440px">
            <source type="image/jpeg"
                    srcset="{% static 'images/optimized/dance-3-320w.jpg' %} 320w,
                            {% static 'images/optimized/dance-3-640w.jpg' %} 640w,
                            {% static 'images/optimized/dance-3-960w.jpg' %} 960w,
                            {% static 'images/optimized/dance-3-1280w.jpg' %} 1280w"
                    sizes="(max-width: 600px) 90vw, (max-width: 768px) 45vw, 440px">
            <img src="{% static 'images/optimized/dance-3-640w.jpg' %}"
                 alt="Music Integration Cuban Dance"
                 class="dance-photo"
                 width="440"
                 height="722"
                 loading="lazy"
                 decoding="async">
        </picture>
    </div>
    <div class="photo-container" style="aspect-ratio: 0.61;">
        <picture>
            <source type="image/webp"
                    srcset="{% static 'images/optimized/dance-4-320w.webp' %} 320w,
                            {% static 'images/optimized/dance-4-640w.webp' %} 640w,
                            {% static 'images/optimized/dance-4-960w.webp' %} 960w,
                            {% static 'images/optimized/dance-4-1280w.webp' %} 1280w"
                    sizes="(max-width: 600px) 90vw, (max-width: 768px) 45vw, 440px">
            <source type="image/jpeg"
                    srcset="{% static 'images/optimized/dance-4-320w.jpg' %} 320w,
                            {% static 'images/optimized/dance-4-640w.jpg' %} 640w,
                            {% static 'images/optimized/dance-4-960w.jpg' %} 960w,
                            {% static 'images/optimized/dance-4-1280w.jpg' %} 1280w"
                    sizes="(max-width: 600px) 90vw, (max-width: 768px) 45vw, 440px">
            <img src="{% static 'images/optimized/dance-4-640w.jpg' %}"
                 alt="Cuban Dance Training Boulder"
                 class="dance-photo"
                 width="440"
                 height="722"
                 loading="lazy"
                 decoding="async">
        </picture>
    </div>
</div>
{% endblock %}
```

#### Step 5: Hero GIF Optimization

The `pasos-basicos-animated.gif` needs special handling due to its large size:

**Option A: Convert to Video (Recommended)**

```javascript
// Add to optimize-images.js
const { exec } = require('child_process');

async function convertGifToVideo() {
  const gifPath = path.join(INPUT_DIR, 'pasos-basicos-animated.gif');
  const mp4Output = path.join(OUTPUT_DIR, 'pasos-basicos.mp4');
  const webmOutput = path.join(OUTPUT_DIR, 'pasos-basicos.webm');

  // Using ffmpeg for conversion
  const mp4Cmd = `ffmpeg -i "${gifPath}" -movflags faststart -pix_fmt yuv420p ` +
                 `-vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" "${mp4Output}"`;
  const webmCmd = `ffmpeg -i "${gifPath}" -c:v libvpx-vp9 -crf 30 -b:v 0 "${webmOutput}"`;

  console.log('Converting GIF to video formats...');
  // Execute commands...
}
```

**Option B: Create Optimized Static Frame**

```javascript
// Extract first frame and optimize
async function optimizeGifFallback() {
  const gifPath = path.join(INPUT_DIR, 'pasos-basicos-animated.gif');

  await sharp(gifPath, { pages: 1 })
    .resize(1200, null, { withoutEnlargement: true })
    .webp({ quality: 85 })
    .toFile(path.join(OUTPUT_DIR, 'pasos-basicos-poster.webp'));
}
```

#### Step 6: Logo Optimization for Header

Update `/templates/base.html` header:

```html
<a href="{% url 'core:home' %}" class="header-logo">
    <picture>
        <source type="image/webp"
                srcset="{% static 'images/optimized/logo-2.webp' %}">
        <img src="{% static 'images/optimized/logo-2.png' %}"
             alt="Sabor Con Flow"
             width="35"
             height="35"
             loading="eager">
    </picture>
</a>
```

### Expected Outcomes

| Image | Original Size | Optimized Size | Reduction |
|-------|--------------|----------------|-----------|
| dance-1.jpeg | ~460KB | ~65KB (WebP 640w) | 86% |
| dance-3.jpeg | ~506KB | ~70KB (WebP 640w) | 86% |
| dance-4.jpeg | ~300KB | ~45KB (WebP 640w) | 85% |
| Logo PNG | ~50KB | ~8KB (WebP) | 84% |
| Hero GIF | ~800KB | ~150KB (video) | 81% |

**Total estimated savings: ~2MB per page load**

### Files Changed

```text
new file:   scripts/optimize-images.js
modified:   package.json
modified:   templates/base.html
modified:   templates/home.html
new dir:    static/images/optimized/
```

---

## PR 5.2: Font and Asset Optimization

### Objective

Self-host Playfair Display and Inter fonts, implement `font-display: swap`, subset fonts to
Latin only, and remove Font Awesome CDN by using inline SVGs (already done).

### Implementation Details

#### Step 1: Download and Subset Fonts

**Required Font Files:**

| Font | Weights | Format Priority |
|------|---------|-----------------|
| Playfair Display | 400, 700 | woff2, woff |

**Character Subset (Latin):**

```text
U+0000-00FF  # Basic Latin
U+0100-017F  # Latin Extended-A
U+0180-024F  # Latin Extended-B (partial)
U+2000-206F  # General Punctuation
U+20AC       # Euro Sign
U+2122       # Trademark
```

**Subsetting Commands (using `glyphhanger` or `fonttools`):**

```bash
# Install pyftsubset (part of fonttools)
pip install fonttools brotli

# Download Playfair Display from Google Fonts
# https://fonts.google.com/specimen/Playfair+Display

# Subset to Latin characters only
pyftsubset PlayfairDisplay-Regular.ttf \
  --unicodes="U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD" \
  --flavor=woff2 \
  --output-file=PlayfairDisplay-Regular.woff2

pyftsubset PlayfairDisplay-Regular.ttf \
  --unicodes="U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD" \
  --flavor=woff \
  --output-file=PlayfairDisplay-Regular.woff

pyftsubset PlayfairDisplay-Bold.ttf \
  --unicodes="U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD" \
  --flavor=woff2 \
  --output-file=PlayfairDisplay-Bold.woff2

pyftsubset PlayfairDisplay-Bold.ttf \
  --unicodes="U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD" \
  --flavor=woff \
  --output-file=PlayfairDisplay-Bold.woff
```

#### Step 2: Font File Directory Structure

```text
static/
  fonts/
    playfair-display/
      PlayfairDisplay-Regular.woff2
      PlayfairDisplay-Regular.woff
      PlayfairDisplay-Bold.woff2
      PlayfairDisplay-Bold.woff
```

#### Step 3: CSS Font Face Declarations

Create `/static/css/fonts.css`:

```css
/**
 * Sabor Con Flow - Self-Hosted Fonts
 * Playfair Display - Latin subset only
 */

/* Playfair Display Regular */
@font-face {
  font-family: 'Playfair Display';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('../fonts/playfair-display/PlayfairDisplay-Regular.woff2') format('woff2'),
       url('../fonts/playfair-display/PlayfairDisplay-Regular.woff') format('woff');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA,
                 U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193,
                 U+2212, U+2215, U+FEFF, U+FFFD;
}

/* Playfair Display Bold */
@font-face {
  font-family: 'Playfair Display';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('../fonts/playfair-display/PlayfairDisplay-Bold.woff2') format('woff2'),
       url('../fonts/playfair-display/PlayfairDisplay-Bold.woff') format('woff');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA,
                 U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193,
                 U+2212, U+2215, U+FEFF, U+FFFD;
}
```

#### Step 4: Update Base Template

Update `/templates/base.html`:

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Sabor Con Flow{% endblock %}</title>

    <!-- Favicon configuration -->
    <link rel="icon" type="image/png" href="{% static 'images/optimized/logo-2.webp' %}">
    <link rel="icon" type="image/png" sizes="32x32"
          href="{% static 'images/optimized/logo-2.webp' %}">
    <link rel="icon" type="image/png" sizes="16x16"
          href="{% static 'images/optimized/logo-2.webp' %}">
    <link rel="apple-touch-icon" sizes="180x180"
          href="{% static 'images/optimized/logo-2.webp' %}">
    <link rel="manifest" href="{% static 'images/site.webmanifest' %}">
    <meta name="theme-color" content="#000000">

    <!-- Preload critical fonts -->
    <link rel="preload"
          href="{% static 'fonts/playfair-display/PlayfairDisplay-Regular.woff2' %}"
          as="font"
          type="font/woff2"
          crossorigin>
    <link rel="preload"
          href="{% static 'fonts/playfair-display/PlayfairDisplay-Bold.woff2' %}"
          as="font"
          type="font/woff2"
          crossorigin>

    <!-- Bootstrap removed in Phase 1.3 - using custom CSS -->

    <!-- REMOVED: Font Awesome CDN - not used -->
    <!-- <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
          rel="stylesheet"> -->

    <!-- REMOVED: Google Fonts CDN - now self-hosted -->
    <!-- <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap"
          rel="stylesheet"> -->

    <!-- Self-hosted fonts -->
    <link href="{% static 'css/fonts.css' %}" rel="stylesheet" type="text/css">

    <!-- Main styles -->
    <link href="{% static 'css/styles.css' %}" rel="stylesheet" type="text/css">

    <!-- Calendly badge widget begin -->
    <link href="https://assets.calendly.com/assets/external/widget.css" rel="stylesheet">

    {% block extra_css %}{% endblock %}
</head>
```

#### Step 5: Update CSP in Django Settings

Update `/sabor_con_flow/settings.py` (if CSP is enforced):

```python
# Remove font CDN sources from CSP
# Old:
# fontSrc: ["'self'", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com"]
# New:
# fontSrc: ["'self'"]
```

#### Step 6: Update CSP via Vercel Headers (server.js removed in Phase 1)

Since Express is removed in Phase 1, configure CSP via `vercel.json`:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; style-src 'self' 'unsafe-inline' https://assets.calendly.com; script-src 'self' 'unsafe-inline' https://assets.calendly.com; font-src 'self'; img-src 'self' data: https:; frame-src 'self' https://calendly.com"
        }
      ]
    }
  ]
}
```

Or configure via Django middleware if preferred.

### Expected Outcomes

| Resource | Before | After | Reduction |
|----------|--------|-------|-----------|
| Google Fonts CSS | ~2KB + fonts | 0 | 100% |
| Google Font files | ~80KB (all weights) | ~30KB (subsetted) | 62% |
| Font Awesome CSS | ~60KB | 0 | 100% |
| Font Awesome fonts | ~1.5MB | 0 | 100% |

**Total estimated savings: ~1.6MB**

### Files Changed

```text
new file:   static/css/fonts.css
new dir:    static/fonts/playfair-display/
modified:   templates/base.html
modified:   server.js (CSP update)
```

---

## PR 5.3: Build Pipeline Setup (Vite)

### Objective

Implement Vite as the build tool for CSS minification, JS bundling, cache-busting via content
hashing, and source map generation.

### Implementation Details

#### Step 1: Install Vite and Dependencies

```bash
npm install --save-dev vite vite-plugin-compression
```

Update `package.json` devDependencies:

```json
{
  "devDependencies": {
    "jest": "^30.0.5",
    "nodemon": "^3.1.10",
    "supertest": "^7.1.4",
    "vite": "^5.4.19",
    "vite-plugin-compression": "^0.5.1"
  }
}
```

#### Step 2: Create Vite Configuration

Create `/vite.config.js`:

```javascript
import { defineConfig } from 'vite';
import { resolve } from 'path';
import compression from 'vite-plugin-compression';

export default defineConfig({
  // Base public path for assets
  base: '/static/',

  // Build configuration
  build: {
    // Output directory (Django's staticfiles will collect from here)
    outDir: 'static/dist',

    // Empty outDir before build
    emptyOutDir: true,

    // Generate source maps for production
    sourcemap: true,

    // Minification settings
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },

    // CSS code splitting
    cssCodeSplit: false,

    // Asset handling
    assetsDir: 'assets',

    // Rollup options
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'static/css/styles.css'),
        fonts: resolve(__dirname, 'static/css/fonts.css'),
        app: resolve(__dirname, 'static/js/app.js'),
      },
      output: {
        // Asset file names with content hash for cache busting
        entryFileNames: 'js/[name]-[hash].js',
        chunkFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const extType = assetInfo.name.split('.').pop();
          if (/css/i.test(extType)) {
            return 'css/[name]-[hash][extname]';
          }
          if (/woff2?|ttf|eot/i.test(extType)) {
            return 'fonts/[name][extname]';
          }
          if (/png|jpe?g|svg|gif|webp|ico/i.test(extType)) {
            return 'images/[name]-[hash][extname]';
          }
          return 'assets/[name]-[hash][extname]';
        },
      },
    },

    // Chunk size warning limit (in kB)
    chunkSizeWarningLimit: 500,
  },

  // Plugins
  plugins: [
    // Gzip compression
    compression({
      algorithm: 'gzip',
      ext: '.gz',
    }),
    // Brotli compression
    compression({
      algorithm: 'brotliCompress',
      ext: '.br',
    }),
  ],

  // CSS configuration
  css: {
    devSourcemap: true,
    postcss: {
      plugins: [
        // Autoprefixer is already in dependencies
      ],
    },
  },

  // Resolve configuration
  resolve: {
    alias: {
      '@': resolve(__dirname, 'static'),
    },
  },
});
```

#### Step 3: Create JavaScript Entry Point

Create `/static/js/app.js`:

```javascript
/**
 * Sabor Con Flow - Main Application JavaScript
 * This file bundles all client-side functionality
 */

// Import styles (Vite will process these)
import '../css/fonts.css';
import '../css/styles.css';

// Menu toggle functionality
function initMenuToggle() {
  document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.getElementById('site-nav');

    if (!menuToggle || !nav) return;

    menuToggle.addEventListener('click', function() {
      const isOpen = nav.classList.toggle('active');
      menuToggle.classList.toggle('active', isOpen);
      menuToggle.setAttribute('aria-expanded', String(isOpen));
      nav.setAttribute('aria-hidden', String(!isOpen));
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
      if (!nav.contains(event.target) && !menuToggle.contains(event.target)) {
        nav.classList.remove('active');
        nav.setAttribute('aria-hidden', 'true');
        menuToggle.classList.remove('active');
        menuToggle.setAttribute('aria-expanded', 'false');
      }
    });

    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && nav.classList.contains('active')) {
        nav.classList.remove('active');
        nav.setAttribute('aria-hidden', 'true');
        menuToggle.classList.remove('active');
        menuToggle.setAttribute('aria-expanded', 'false');
        menuToggle.focus();
      }
    });
  });
}

// Lazy loading for images (progressive enhancement)
function initLazyLoading() {
  if ('loading' in HTMLImageElement.prototype) {
    // Native lazy loading supported
    return;
  }

  // Fallback for browsers without native lazy loading
  const lazyImages = document.querySelectorAll('img[loading="lazy"]');

  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src || img.src;
          imageObserver.unobserve(img);
        }
      });
    });

    lazyImages.forEach((img) => imageObserver.observe(img));
  }
}

// Initialize all modules
initMenuToggle();
initLazyLoading();

// Export for potential module usage
export { initMenuToggle, initLazyLoading };
```

#### Step 4: Create Manifest Template Tag (Django)

Create `/core/templatetags/vite.py`:

```python
"""
Vite integration template tags for Django
Reads the Vite manifest to get hashed asset URLs
"""

import json
from pathlib import Path
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

# Cache the manifest in memory
_manifest_cache = None


def get_manifest():
    """Load and cache the Vite manifest."""
    global _manifest_cache

    if _manifest_cache is not None and not settings.DEBUG:
        return _manifest_cache

    manifest_path = Path(settings.BASE_DIR) / 'static' / 'dist' / '.vite' / 'manifest.json'

    if not manifest_path.exists():
        if settings.DEBUG:
            return {}
        raise FileNotFoundError(f"Vite manifest not found at {manifest_path}")

    with open(manifest_path, 'r') as f:
        _manifest_cache = json.load(f)

    return _manifest_cache


@register.simple_tag
def vite_asset(entry_name):
    """
    Get the URL for a Vite-processed asset.

    Usage: {% vite_asset 'static/css/styles.css' %}
    Returns: /static/dist/css/styles-abc123.css
    """
    if settings.DEBUG:
        # In development, serve files directly (no Vite build)
        return f"/static/{entry_name.replace('static/', '')}"

    manifest = get_manifest()

    if entry_name not in manifest:
        raise KeyError(f"Asset '{entry_name}' not found in Vite manifest")

    asset_info = manifest[entry_name]
    return f"/static/dist/{asset_info['file']}"


@register.simple_tag
def vite_css(entry_name):
    """
    Get CSS link tags for a Vite entry point.

    Usage: {% vite_css 'static/js/app.js' %}
    Returns: <link rel="stylesheet" href="/static/dist/css/styles-abc123.css">
    """
    if settings.DEBUG:
        return mark_safe(
            f'<link rel="stylesheet" href="/static/css/fonts.css">\n'
            f'<link rel="stylesheet" href="/static/css/styles.css">'
        )

    manifest = get_manifest()

    if entry_name not in manifest:
        return ''

    asset_info = manifest[entry_name]
    css_files = asset_info.get('css', [])

    links = []
    for css_file in css_files:
        links.append(f'<link rel="stylesheet" href="/static/dist/{css_file}">')

    return mark_safe('\n'.join(links))


@register.simple_tag
def vite_js(entry_name):
    """
    Get JS script tag for a Vite entry point.

    Usage: {% vite_js 'static/js/app.js' %}
    Returns: <script type="module" src="/static/dist/js/app-abc123.js"></script>
    """
    if settings.DEBUG:
        return ''  # In dev, JS is inline in templates

    manifest = get_manifest()

    if entry_name not in manifest:
        raise KeyError(f"Entry '{entry_name}' not found in Vite manifest")

    asset_info = manifest[entry_name]
    return mark_safe(
        f'<script type="module" src="/static/dist/{asset_info["file"]}"></script>'
    )
```

Create `/core/templatetags/__init__.py`:

```python
# Template tags package
```

#### Step 5: Update Base Template for Vite

Update `/templates/base.html`:

```html
{% load static %}
{% load vite %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Sabor Con Flow{% endblock %}</title>

    <!-- Favicon configuration -->
    <link rel="icon" type="image/png" href="{% static 'images/optimized/logo-2.webp' %}">
    <link rel="icon" type="image/png" sizes="32x32"
          href="{% static 'images/optimized/logo-2.webp' %}">
    <link rel="apple-touch-icon" sizes="180x180"
          href="{% static 'images/optimized/logo-2.webp' %}">
    <link rel="manifest" href="{% static 'images/site.webmanifest' %}">
    <meta name="theme-color" content="#000000">

    <!-- Preload critical fonts -->
    <link rel="preload"
          href="{% static 'fonts/playfair-display/PlayfairDisplay-Regular.woff2' %}"
          as="font"
          type="font/woff2"
          crossorigin>
    <link rel="preload"
          href="{% static 'fonts/playfair-display/PlayfairDisplay-Bold.woff2' %}"
          as="font"
          type="font/woff2"
          crossorigin>

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
          rel="stylesheet">

    <!-- Vite-processed CSS (includes fonts.css and styles.css) -->
    {% vite_css 'static/js/app.js' %}

    <!-- Calendly badge widget -->
    <link href="https://assets.calendly.com/assets/external/widget.css" rel="stylesheet">

    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- ... body content ... -->

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js">
    </script>

    <!-- Vite-processed JavaScript -->
    {% vite_js 'static/js/app.js' %}

    {% block extra_js %}{% endblock %}
</body>
</html>
```

#### Step 6: Update Package.json Scripts

```json
{
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "dev:vite": "vite",
    "build": "npm run optimize:images && vite build",
    "build:vite": "vite build",
    "preview": "vite preview",
    "optimize:images": "node scripts/optimize-images.js",
    "test": "jest",
    "test:watch": "jest --watch"
  }
}
```

#### Step 7: Update Vercel Build Script

Update `/vercel-build`:

```bash
#!/bin/bash
set -e

echo "Installing Node.js dependencies..."
npm ci

echo "Building assets with Vite..."
npm run build

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"
```

#### Step 8: Update Django Settings for Vite

Update `/sabor_con_flow/settings.py`:

```python
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Include both source static files and Vite build output
STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "static" / "dist",  # Vite output
]

# Static file configuration for Vercel
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

#### Step 9: Update Vercel Configuration

Update `/vercel.json`:

```json
{
  "version": 2,
  "buildCommand": "./vercel-build",
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb",
        "runtime": "python3.12"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/dist/(.*)",
      "dest": "/staticfiles/dist/$1",
      "headers": {
        "Cache-Control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/static/(.*)",
      "dest": "/staticfiles/$1"
    },
    {
      "src": "/staticfiles/(.*)",
      "dest": "/staticfiles/$1"
    },
    {
      "handle": "filesystem"
    },
    {
      "src": "^/([^?]*)(\\?.*fbclid=.*)$",
      "status": 301,
      "headers": {
        "Location": "https://www.saborconflowdance.com/$1",
        "Cache-Control": "no-cache, no-store, must-revalidate"
      }
    },
    {
      "src": "/favicon\\.(ico|png|jpg|jpeg|gif|svg)$",
      "status": 301,
      "headers": {
        "Location": "/static/images/favicon/favicon.png"
      }
    },
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "PYTHONPATH": ".",
    "DJANGO_DEBUG": "False"
  }
}
```

### Expected Build Output

```text
static/dist/
  .vite/
    manifest.json
  css/
    main-abc123.css
    main-abc123.css.gz
    main-abc123.css.br
  js/
    app-def456.js
    app-def456.js.gz
    app-def456.js.br
    app-def456.js.map
  fonts/
    PlayfairDisplay-Regular.woff2
    PlayfairDisplay-Bold.woff2
```

### Expected Outcomes

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| CSS size | ~25KB | ~8KB (minified + gzipped) | 68% |
| JS size | ~3KB (inline) | ~2KB (bundled + gzipped) | 33% |
| Cache efficiency | None (query params) | Immutable (content hash) | 100% cache hit |
| Source maps | None | Full | Debug capability |

### Files Changed

```text
new file:   vite.config.js
new file:   static/js/app.js
new file:   core/templatetags/vite.py
new file:   core/templatetags/__init__.py
modified:   package.json
modified:   vercel-build
modified:   vercel.json
modified:   sabor_con_flow/settings.py
modified:   templates/base.html
new dir:    static/dist/ (build output)
```

---

## Implementation Roadmap

### Phase 5 Timeline

```yaml
roadmap:
  title: "Phase 5: Performance & Optimization"
  phases:
    - name: "PR 5.1: Image Optimization"
      duration: "3-4 days"
      objectives:
        - description: "Create image optimization script"
          owner: "Frontend Developer"
          dependencies: []
          deliverables:
            - scripts/optimize-images.js
            - npm script integration
        - description: "Generate optimized images"
          owner: "Frontend Developer"
          dependencies: ["Create image optimization script"]
          deliverables:
            - WebP versions of all images
            - Multiple responsive sizes
        - description: "Update templates with picture elements"
          owner: "Frontend Developer"
          dependencies: ["Generate optimized images"]
          deliverables:
            - Updated home.html
            - Updated base.html
            - Lazy loading implementation

    - name: "PR 5.2: Font & Asset Optimization"
      duration: "2-3 days"
      objectives:
        - description: "Download and subset fonts"
          owner: "Frontend Developer"
          dependencies: []
          deliverables:
            - Subsetted woff2/woff files
            - fonts.css file
        - description: "Remove CDN dependencies"
          owner: "Frontend Developer"
          dependencies: ["Download and subset fonts"]
          deliverables:
            - Updated base.html (no Google Fonts, no Font Awesome)
            - Updated CSP policies

    - name: "PR 5.3: Build Pipeline Setup"
      duration: "4-5 days"
      objectives:
        - description: "Configure Vite"
          owner: "Frontend Developer"
          dependencies: []
          deliverables:
            - vite.config.js
            - static/js/app.js entry point
        - description: "Create Django template tags"
          owner: "Backend Developer"
          dependencies: ["Configure Vite"]
          deliverables:
            - core/templatetags/vite.py
            - Manifest reading logic
        - description: "Update build process"
          owner: "DevOps"
          dependencies: ["Configure Vite", "Create Django template tags"]
          deliverables:
            - Updated vercel-build
            - Updated vercel.json
            - Cache-control headers

  milestones:
    - date: "End of Week 1"
      description: "Image optimization complete"
      success_criteria:
        - All images converted to WebP
        - Picture elements with srcset
        - Lazy loading implemented
    - date: "End of Week 2"
      description: "Font optimization complete"
      success_criteria:
        - Self-hosted fonts working
        - Font Awesome CDN removed
        - Google Fonts CDN removed
    - date: "End of Week 3"
      description: "Build pipeline operational"
      success_criteria:
        - Vite builds successfully
        - Cache-busting working
        - Source maps generated
        - Vercel deployment successful
```

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Browser WebP support | Low | Low | JPEG fallbacks in picture elements |
| Font rendering flash | Medium | Medium | font-display: swap + preload hints |
| Build failure on Vercel | High | Low | Local testing, verbose logging |
| Cache invalidation issues | Medium | Low | Content hashing ensures fresh assets |
| Image quality degradation | Medium | Medium | Quality parameter tuning, visual QA |

---

## Testing Strategy

### PR 5.1 Testing

```bash
# Verify image optimization
npm run optimize:images
ls -la static/images/optimized/

# Check file sizes
du -sh static/images/optimized/*.webp

# Visual comparison (manual QA)
open static/images/dance-1.jpeg
open static/images/optimized/dance-1-640w.webp
```

### PR 5.2 Testing

```bash
# Verify font files exist
ls -la static/fonts/playfair-display/

# Test font loading in browser DevTools
# Network tab: Filter by "font"
# Verify fonts load from /static/fonts/

# Test fallback (disable JavaScript)
# Fonts should still load via CSS
```

### PR 5.3 Testing

```bash
# Local Vite build
npm run build

# Verify manifest
cat static/dist/.vite/manifest.json | jq .

# Test Django collectstatic
python manage.py collectstatic --noinput

# Verify hashed filenames
ls -la staticfiles/dist/css/
ls -la staticfiles/dist/js/

# Full integration test
./vercel-build
```

### Lighthouse Performance Testing

```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run audit
lighthouse https://www.saborconflowdance.com --output=json --output-path=./lighthouse-report.json

# Key metrics to verify:
# - First Contentful Paint < 1.8s
# - Largest Contentful Paint < 2.5s
# - Total Blocking Time < 200ms
# - Cumulative Layout Shift < 0.1
# - Performance Score > 90
```

---

## Rollback Plan

### PR 5.1 Rollback

```bash
# Revert to original images
git revert <commit-hash>
# Original images remain in static/images/
# Templates fall back to direct image references
```

### PR 5.2 Rollback

```bash
# Restore CDN links
git revert <commit-hash>
# CDN fonts will load immediately
# No local dependencies
```

### PR 5.3 Rollback

```bash
# Disable Vite integration
git revert <commit-hash>
# Remove static/dist/ from STATICFILES_DIRS
# Templates use direct static references
# vercel-build skips npm build step
```

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Image payload | ~2.5MB | ~500KB | Network tab total |
| Font payload | ~1.6MB | ~50KB | Network tab fonts |
| CSS size | ~25KB | ~8KB | Bundle size |
| JS size | ~3KB | ~2KB | Bundle size |
| Lighthouse Performance | ~60 | 90+ | Lighthouse audit |
| First Contentful Paint | ~3s | <1.8s | Lighthouse |
| Largest Contentful Paint | ~5s | <2.5s | Lighthouse |

---

## Appendix A: Command Reference

### Image Optimization Commands

```bash
# Install Sharp (if needed)
npm install sharp

# Run optimization script
npm run optimize:images

# Manual Sharp conversion
npx sharp -i input.jpg -o output.webp --format webp --quality 80
```

### Font Subsetting Commands

```bash
# Install fonttools
pip install fonttools brotli

# Subset to Latin
pyftsubset input.ttf \
  --unicodes="U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD" \
  --flavor=woff2 \
  --output-file=output.woff2
```

### Vite Commands

```bash
# Development server
npm run dev:vite

# Production build
npm run build:vite

# Preview production build
npm run preview

# Analyze bundle
npx vite-bundle-visualizer
```

---

## Appendix B: File Structure After Phase 5

```text
sabor-con-flow-dance/
  core/
    templatetags/
      __init__.py
      vite.py
  scripts/
    optimize-images.js
  static/
    css/
      fonts.css
      styles.css
    dist/
      .vite/
        manifest.json
      css/
        main-[hash].css
        main-[hash].css.gz
        main-[hash].css.br
      js/
        app-[hash].js
        app-[hash].js.map
        app-[hash].js.gz
        app-[hash].js.br
    fonts/
      playfair-display/
        PlayfairDisplay-Regular.woff2
        PlayfairDisplay-Regular.woff
        PlayfairDisplay-Bold.woff2
        PlayfairDisplay-Bold.woff
    images/
      optimized/
        dance-1-320w.webp
        dance-1-320w.jpg
        dance-1-640w.webp
        dance-1-640w.jpg
        dance-1-960w.webp
        dance-1-960w.jpg
        dance-1-1280w.webp
        dance-1-1280w.jpg
        dance-1.webp
        dance-1.jpg
        dance-3-320w.webp
        ... (similar for other images)
        logo-2.webp
        pasos-basicos-poster.webp
      dance-1.jpeg (original)
      dance-3.jpeg (original)
      dance-4.jpeg (original)
      sabor-con-flow-logo.png (original)
      sabor-con-flow-logo-2.png (original)
      pasos-basicos-animated.gif (original)
    js/
      app.js
  templates/
    base.html
    home.html
  vite.config.js
  vercel-build
  vercel.json
  package.json
```
