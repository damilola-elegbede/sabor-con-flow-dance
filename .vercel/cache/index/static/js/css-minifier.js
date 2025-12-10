/**
 * Runtime CSS Minification and Optimization
 * SPEC_04 Group D Implementation
 */

class CSSOptimizer {
    constructor() {
        this.criticalCSS = new Set();
        this.nonCriticalCSS = new Set();
        this.loadedStylesheets = new Map();
        this.performanceMetrics = {
            originalSize: 0,
            optimizedSize: 0,
            loadTime: 0,
            criticalCSSSize: 0
        };

        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.optimizeCSS());
        } else {
            this.optimizeCSS();
        }
    }

    async optimizeCSS() {
        console.log('🎨 CSS Optimizer starting...');
        const startTime = performance.now();

        try {
            // Inline critical CSS for immediate rendering
            await this.inlineCriticalCSS();
            
            // Defer non-critical CSS
            await this.deferNonCriticalCSS();
            
            // Remove unused CSS (experimental)
            if (this.shouldPurgeCSS()) {
                await this.purgeUnusedCSS();
            }
            
            // Optimize font loading
            this.optimizeFontLoading();
            
            // Track performance
            const loadTime = performance.now() - startTime;
            this.performanceMetrics.loadTime = loadTime;
            
            this.reportMetrics();
            
        } catch (error) {
            console.error('❌ CSS optimization failed:', error);
        }
    }

    async inlineCriticalCSS() {
        const criticalSelectors = [
            // Above-the-fold content
            'body', 'html', '.container',
            '.navbar', '.navbar-container', '.navbar-brand', '.navbar-menu',
            '.hero', '.hero-content', '.hero-title', '.hero-subtitle',
            '.btn', '.btn-primary', '.btn-outline',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            // Loading states
            '.loading', '.placeholder', '.shimmer',
            // Critical utilities
            '.text-center', '.text-left', '.text-right',
            '.sr-only', '.skip-link'
        ];

        const stylesheets = Array.from(document.styleSheets);
        let criticalCSS = '';

        for (const stylesheet of stylesheets) {
            try {
                const rules = this.getStyleSheetRules(stylesheet);
                if (!rules) continue;

                for (const rule of rules) {
                    if (rule.type === CSSRule.STYLE_RULE) {
                        if (this.isCriticalSelector(rule.selectorText, criticalSelectors)) {
                            criticalCSS += this.minifyCSS(rule.cssText) + '\n';
                        }
                    }
                }
            } catch (error) {
                // Cross-origin stylesheets might not be accessible
                console.warn('Cannot access stylesheet:', stylesheet.href);
            }
        }

        if (criticalCSS) {
            this.injectCriticalCSS(criticalCSS);
            this.performanceMetrics.criticalCSSSize = criticalCSS.length;
        }
    }

    getStyleSheetRules(stylesheet) {
        try {
            return stylesheet.cssRules || stylesheet.rules;
        } catch (error) {
            return null;
        }
    }

    isCriticalSelector(selectorText, criticalSelectors) {
        if (!selectorText) return false;
        
        return criticalSelectors.some(selector => {
            // Check for exact match or contains
            return selectorText.includes(selector) || 
                   selectorText.startsWith(selector) ||
                   // Check for media queries with critical selectors
                   (selectorText.includes('@media') && selectorText.includes(selector));
        });
    }

    minifyCSS(cssText) {
        return cssText
            // Remove comments
            .replace(/\/\*[\s\S]*?\*\//g, '')
            // Remove extra whitespace
            .replace(/\s+/g, ' ')
            // Remove whitespace around certain characters
            .replace(/\s*([{}:;,>+~])\s*/g, '$1')
            // Remove trailing semicolons
            .replace(/;}/g, '}')
            // Remove leading/trailing whitespace
            .trim();
    }

    injectCriticalCSS(cssText) {
        const style = document.createElement('style');
        style.id = 'critical-css-runtime';
        style.textContent = cssText;
        
        // Insert after existing critical CSS or at head start
        const existingCritical = document.getElementById('critical-css');
        if (existingCritical) {
            existingCritical.parentNode.insertBefore(style, existingCritical.nextSibling);
        } else {
            document.head.insertBefore(style, document.head.firstChild);
        }
    }

    async deferNonCriticalCSS() {
        const stylesheets = Array.from(document.querySelectorAll('link[rel="stylesheet"]'));
        
        for (const link of stylesheets) {
            // Skip critical stylesheets
            if (link.hasAttribute('data-critical')) continue;
            
            // Defer loading by changing rel attribute
            if (link.media !== 'print') {
                this.deferStylesheet(link);
            }
        }
    }

    deferStylesheet(link) {
        // Store original values
        const originalRel = link.rel;
        const originalMedia = link.media;
        
        // Set to preload to download but not apply
        link.rel = 'preload';
        link.as = 'style';
        
        // Apply stylesheet once loaded
        link.onload = () => {
            link.rel = originalRel;
            link.media = originalMedia;
            link.onload = null;
        };
        
        // Fallback for browsers that don't support preload
        if (!link.onload) {
            setTimeout(() => {
                link.rel = originalRel;
                link.media = originalMedia;
            }, 3000);
        }
    }

    shouldPurgeCSS() {
        // Only purge CSS in production or when explicitly enabled
        return !window.location.hostname.includes('localhost') && 
               !window.location.hostname.includes('127.0.0.1') &&
               localStorage.getItem('css-purge-enabled') === 'true';
    }

    async purgeUnusedCSS() {
        console.log('🧹 Purging unused CSS...');
        
        // Get all used selectors in the DOM
        const usedSelectors = new Set();
        const allElements = document.querySelectorAll('*');
        
        allElements.forEach(element => {
            // Add tag name
            usedSelectors.add(element.tagName.toLowerCase());
            
            // Add classes
            if (element.className) {
                const classes = element.className.split(/\s+/);
                classes.forEach(cls => {
                    if (cls.trim()) {
                        usedSelectors.add(`.${cls.trim()}`);
                    }
                });
            }
            
            // Add ID
            if (element.id) {
                usedSelectors.add(`#${element.id}`);
            }
        });

        // Also include pseudo-classes and states that might be used
        const pseudoSelectors = [':hover', ':focus', ':active', ':visited', '::before', '::after'];
        const additionalSelectors = new Set();
        
        usedSelectors.forEach(selector => {
            pseudoSelectors.forEach(pseudo => {
                additionalSelectors.add(selector + pseudo);
            });
        });
        
        // Merge sets
        pseudoSelectors.forEach(pseudo => additionalSelectors.add(pseudo));
        usedSelectors.forEach(selector => additionalSelectors.add(selector));

        // Purge unused styles (simplified implementation)
        this.removeUnusedStyles(additionalSelectors);
    }

    removeUnusedStyles(usedSelectors) {
        const stylesheets = Array.from(document.styleSheets);
        
        stylesheets.forEach(stylesheet => {
            try {
                const rules = this.getStyleSheetRules(stylesheet);
                if (!rules) return;

                const rulesToRemove = [];
                
                for (let i = rules.length - 1; i >= 0; i--) {
                    const rule = rules[i];
                    
                    if (rule.type === CSSRule.STYLE_RULE) {
                        const selector = rule.selectorText;
                        if (!this.isSelectorUsed(selector, usedSelectors)) {
                            rulesToRemove.push(i);
                        }
                    }
                }
                
                // Remove unused rules
                rulesToRemove.forEach(index => {
                    try {
                        stylesheet.deleteRule(index);
                    } catch (error) {
                        // Rule might already be deleted or protected
                    }
                });
                
            } catch (error) {
                // Cannot modify cross-origin stylesheets
                console.warn('Cannot purge stylesheet:', stylesheet.href);
            }
        });
    }

    isSelectorUsed(selector, usedSelectors) {
        if (!selector) return true; // Keep if we can't determine
        
        // Simple heuristic: check if any part of the selector is used
        const selectorParts = selector.split(/[,\s>+~]/);
        
        return selectorParts.some(part => {
            const cleanPart = part.trim().replace(/[:\[\]()]/g, '');
            return usedSelectors.has(cleanPart) || 
                   usedSelectors.has(cleanPart.toLowerCase()) ||
                   cleanPart === '' || // Empty parts are often combinators
                   cleanPart.startsWith('@'); // Keep media queries and other at-rules
        });
    }

    optimizeFontLoading() {
        // Add font-display: swap to existing font faces
        const fontFaces = Array.from(document.styleSheets).flatMap(sheet => {
            try {
                const rules = this.getStyleSheetRules(sheet);
                return rules ? Array.from(rules).filter(rule => rule.type === CSSRule.FONT_FACE_RULE) : [];
            } catch {
                return [];
            }
        });

        fontFaces.forEach(fontFace => {
            try {
                if (!fontFace.style.fontDisplay) {
                    fontFace.style.fontDisplay = 'swap';
                }
            } catch (error) {
                // Font face might be read-only
            }
        });

        // Preload critical fonts
        this.preloadCriticalFonts();
    }

    preloadCriticalFonts() {
        const criticalFonts = [
            'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&display=swap',
            'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap'
        ];

        criticalFonts.forEach(fontUrl => {
            const existingLink = document.querySelector(`link[href="${fontUrl}"]`);
            if (!existingLink) {
                const link = document.createElement('link');
                link.rel = 'preload';
                link.as = 'style';
                link.href = fontUrl;
                link.crossOrigin = 'anonymous';
                document.head.appendChild(link);
            }
        });
    }

    reportMetrics() {
        console.log('📊 CSS Optimization Metrics:', this.performanceMetrics);
        
        // Calculate potential savings
        const savings = this.performanceMetrics.originalSize - this.performanceMetrics.optimizedSize;
        const savingsPercent = this.performanceMetrics.originalSize > 0 ? 
            (savings / this.performanceMetrics.originalSize * 100).toFixed(2) : 0;

        console.log(`💾 Potential CSS savings: ${savings} bytes (${savingsPercent}%)`);
        
        // Send to analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', 'css_optimization', {
                optimization_time: this.performanceMetrics.loadTime,
                critical_css_size: this.performanceMetrics.criticalCSSSize,
                potential_savings: savings
            });
        }
    }

    // Public API
    reoptimize() {
        this.optimizeCSS();
    }

    getCriticalCSS() {
        const criticalStyle = document.getElementById('critical-css-runtime');
        return criticalStyle ? criticalStyle.textContent : '';
    }

    getMetrics() {
        return { ...this.performanceMetrics };
    }
}

// Initialize CSS optimizer
window.cssOptimizer = new CSSOptimizer();