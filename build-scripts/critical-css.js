#!/usr/bin/env node

/**
 * Critical CSS Extraction Script
 * 
 * Extracts above-the-fold CSS for optimal performance.
 * Reduces First Contentful Paint (FCP) by inlining critical styles.
 * 
 * Usage:
 *   node build-scripts/critical-css.js [--url=http://localhost:8000]
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { launch } from 'puppeteer';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

// Configuration
const config = {
  url: process.env.CRITICAL_URL || 'http://localhost:8000',
  outputDir: path.join(projectRoot, 'static/css'),
  viewports: [
    { width: 320, height: 568, name: 'mobile' },    // iPhone SE
    { width: 768, height: 1024, name: 'tablet' },   // iPad
    { width: 1920, height: 1080, name: 'desktop' }  // Desktop
  ],
  timeout: 30000,
  maxCriticalSize: 14336 // 14KB target for critical CSS
};

// Logger utilities
const logger = {
  info: (msg) => console.log(`\x1b[36m[Critical CSS]\x1b[0m ${msg}`),
  success: (msg) => console.log(`\x1b[32m[Critical CSS]\x1b[0m ${msg}`),
  error: (msg) => console.error(`\x1b[31m[Critical CSS]\x1b[0m ${msg}`),
  warn: (msg) => console.warn(`\x1b[33m[Critical CSS]\x1b[0m ${msg}`)
};

/**
 * Extract critical CSS for a specific viewport
 */
async function extractCriticalCSS(browser, viewport) {
  const page = await browser.newPage();
  
  try {
    // Set viewport
    await page.setViewport(viewport);
    
    logger.info(`Extracting critical CSS for ${viewport.name} (${viewport.width}x${viewport.height})`);
    
    // Navigate to page
    await page.goto(config.url, {
      waitUntil: 'networkidle0',
      timeout: config.timeout
    });
    
    // Extract critical CSS using coverage API
    await page.coverage.startCSSCoverage();
    
    // Wait for page to be fully loaded and interactive
    await page.evaluate(() => {
      return new Promise((resolve) => {
        if (document.readyState === 'complete') {
          resolve();
        } else {
          window.addEventListener('load', resolve);
        }
      });
    });
    
    // Get CSS coverage
    const cssCoverage = await page.coverage.stopCSSCoverage();
    
    // Extract critical CSS from coverage data
    let criticalCSS = '';
    
    for (const entry of cssCoverage) {
      let css = entry.text;
      
      // Only process internal stylesheets (not external CDN resources)
      if (entry.url && (entry.url.includes('localhost') || entry.url.includes(config.url))) {
        // Extract used CSS ranges
        const usedCSS = [];
        
        for (const range of entry.ranges) {
          usedCSS.push(css.substring(range.start, range.end));
        }
        
        criticalCSS += usedCSS.join('\\n');
      }
    }
    
    // Additional critical styles extraction using DOM analysis
    const additionalCritical = await page.evaluate(() => {
      const criticalSelectors = [];
      
      // Get all elements in the viewport (above-the-fold)
      const viewportHeight = window.innerHeight;
      const elements = document.querySelectorAll('*');
      
      elements.forEach(element => {
        const rect = element.getBoundingClientRect();
        
        // Check if element is in the viewport
        if (rect.top < viewportHeight && rect.bottom > 0) {
          // Get computed styles for critical elements
          const styles = window.getComputedStyle(element);
          
          // Extract critical properties
          const criticalProps = [
            'display', 'position', 'top', 'left', 'right', 'bottom',
            'width', 'height', 'margin', 'padding', 'border',
            'background', 'background-color', 'background-image',
            'color', 'font-family', 'font-size', 'font-weight',
            'line-height', 'text-align', 'opacity', 'visibility',
            'z-index', 'transform', 'flex', 'grid'
          ];
          
          let elementCSS = '';
          const className = element.className;
          const tagName = element.tagName.toLowerCase();
          
          if (className && typeof className === 'string') {
            elementCSS += `.${className.split(' ').join('.')} {\\n`;
          } else {
            elementCSS += `${tagName} {\\n`;
          }
          
          criticalProps.forEach(prop => {
            const value = styles.getPropertyValue(prop);
            if (value && value !== 'initial' && value !== 'normal') {
              elementCSS += `  ${prop}: ${value};\\n`;
            }
          });
          
          elementCSS += '}\\n';
          criticalSelectors.push(elementCSS);
        }
      });
      
      return criticalSelectors.join('\\n');
    });
    
    // Combine coverage-based and DOM-based critical CSS
    criticalCSS = (criticalCSS + '\\n' + additionalCritical).trim();
    
    return {
      viewport: viewport.name,
      css: criticalCSS,
      size: Buffer.byteLength(criticalCSS, 'utf8')
    };
    
  } catch (error) {
    logger.error(`Failed to extract critical CSS for ${viewport.name}: ${error.message}`);
    return {
      viewport: viewport.name,
      css: '',
      size: 0,
      error: error.message
    };
  } finally {
    await page.close();
  }
}

/**
 * Merge critical CSS from multiple viewports
 */
function mergeCriticalCSS(criticalCSSResults) {
  const allCSS = criticalCSSResults
    .filter(result => result.css && !result.error)
    .map(result => result.css)
    .join('\\n');
  
  // Remove duplicates and optimize
  const cssRules = allCSS.split('}').filter(rule => rule.trim());
  const uniqueRules = [...new Set(cssRules)];
  
  return uniqueRules.join('}\\n') + (uniqueRules.length > 0 ? '}' : '');
}

/**
 * Optimize critical CSS
 */
function optimizeCriticalCSS(css) {
  return css
    // Remove comments
    .replace(/\\/\\*[\\s\\S]*?\\*\\//g, '')
    // Remove extra whitespace
    .replace(/\\s+/g, ' ')
    // Remove whitespace around brackets and semicolons
    .replace(/\\s*{\\s*/g, '{')
    .replace(/;\\s*/g, ';')
    .replace(/}\\s*/g, '}')
    // Remove trailing semicolons before closing braces
    .replace(/;}/g, '}')
    .trim();
}

/**
 * Save critical CSS files
 */
async function saveCriticalCSS(css, size) {
  try {
    // Ensure output directory exists
    await fs.mkdir(config.outputDir, { recursive: true });
    
    // Save critical CSS
    const criticalPath = path.join(config.outputDir, 'critical.css');
    await fs.writeFile(criticalPath, css, 'utf8');
    
    // Save minified version
    const minifiedCSS = optimizeCriticalCSS(css);
    const criticalMinPath = path.join(config.outputDir, 'critical.min.css');
    await fs.writeFile(criticalMinPath, minifiedCSS, 'utf8');
    
    const minifiedSize = Buffer.byteLength(minifiedCSS, 'utf8');
    
    logger.success(`Critical CSS saved:`);
    logger.info(`  Original: ${criticalPath} (${(size / 1024).toFixed(2)}KB)`);
    logger.info(`  Minified: ${criticalMinPath} (${(minifiedSize / 1024).toFixed(2)}KB)`);
    
    // Check size target
    if (minifiedSize > config.maxCriticalSize) {
      logger.warn(`⚠️  Critical CSS size (${(minifiedSize / 1024).toFixed(2)}KB) exceeds 14KB target`);
    } else {
      logger.success(`✅ Critical CSS size is within 14KB target`);
    }
    
    return {
      originalSize: size,
      minifiedSize: minifiedSize,
      originalPath: criticalPath,
      minifiedPath: criticalMinPath
    };
    
  } catch (error) {
    logger.error(`Failed to save critical CSS: ${error.message}`);
    throw error;
  }
}

/**
 * Generate critical CSS inline template
 */
async function generateInlineTemplate(criticalCSS) {
  const templatePath = path.join(projectRoot, 'templates/components/critical-css.html');
  
  const template = `{# Critical CSS - Auto-generated #}
{# Above-the-fold styles for optimal performance #}
<style id="critical-css">
${criticalCSS}
</style>

<script>
  // Load non-critical CSS asynchronously
  (function() {
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '{% load static %}{% static "css/styles.min.css" %}';
    link.media = 'print';
    link.onload = function() { this.media = 'all'; };
    document.head.appendChild(link);
    
    // Fallback for browsers that don't support onload
    setTimeout(function() {
      if (link.media === 'print') {
        link.media = 'all';
      }
    }, 3000);
  })();
</script>`;
  
  // Ensure template directory exists
  const templateDir = path.dirname(templatePath);
  await fs.mkdir(templateDir, { recursive: true });
  
  await fs.writeFile(templatePath, template, 'utf8');
  
  logger.success(`Inline template saved: ${templatePath}`);
  
  return templatePath;
}

/**
 * Main execution function
 */
async function main() {
  const startTime = Date.now();
  
  try {
    logger.info('Starting critical CSS extraction...');
    
    // Launch browser
    const browser = await launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    logger.info(`Extracting critical CSS from: ${config.url}`);
    
    // Extract critical CSS for each viewport
    const criticalCSSPromises = config.viewports.map(viewport => 
      extractCriticalCSS(browser, viewport)
    );
    
    const criticalCSSResults = await Promise.all(criticalCSSPromises);
    
    await browser.close();
    
    // Check for errors
    const errors = criticalCSSResults.filter(result => result.error);
    if (errors.length > 0) {
      logger.warn(`${errors.length} viewport(s) had extraction errors`);
    }
    
    // Merge and optimize critical CSS
    const mergedCSS = mergeCriticalCSS(criticalCSSResults);
    const totalSize = Buffer.byteLength(mergedCSS, 'utf8');
    
    if (totalSize === 0) {
      logger.error('No critical CSS extracted. Check if the URL is accessible.');
      process.exit(1);
    }
    
    // Save critical CSS files
    const saveResult = await saveCriticalCSS(mergedCSS, totalSize);
    
    // Generate inline template
    const minifiedCSS = optimizeCriticalCSS(mergedCSS);
    await generateInlineTemplate(minifiedCSS);
    
    // Performance summary
    const duration = Date.now() - startTime;
    logger.success(`Critical CSS extraction completed in ${(duration / 1000).toFixed(2)}s`);
    
    // Log viewport results
    criticalCSSResults.forEach(result => {
      if (result.error) {
        logger.error(`${result.viewport}: ${result.error}`);
      } else {
        logger.info(`${result.viewport}: ${(result.size / 1024).toFixed(2)}KB extracted`);
      }
    });
    
  } catch (error) {
    logger.error(`Critical CSS extraction failed: ${error.message}`);
    process.exit(1);
  }
}

// Handle command line arguments
if (process.argv.includes('--help')) {
  console.log(`
Critical CSS Extraction Tool

Usage:
  node build-scripts/critical-css.js [options]

Options:
  --url=URL          URL to extract critical CSS from (default: http://localhost:8000)
  --help             Show this help message

Environment Variables:
  CRITICAL_URL       URL to extract critical CSS from

Examples:
  node build-scripts/critical-css.js
  node build-scripts/critical-css.js --url=https://saborconflow.ca
  CRITICAL_URL=https://saborconflow.ca node build-scripts/critical-css.js
  `);
  process.exit(0);
}

// Parse URL argument
const urlArg = process.argv.find(arg => arg.startsWith('--url='));
if (urlArg) {
  config.url = urlArg.split('=')[1];
}

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error(`Unhandled rejection at: ${promise}, reason: ${reason}`);
  process.exit(1);
});

// Execute main function
main();