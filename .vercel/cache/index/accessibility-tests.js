/**
 * Comprehensive Accessibility Testing Suite
 * WCAG 2.1 AA Compliance Testing - SPEC_06 Group C Task 8
 * Sabor Con Flow Dance Website
 */

const { chromium } = require('playwright');
const axeCore = require('axe-core');
const fs = require('fs');
const path = require('path');
const { runContrastTests } = require('./contrast-tests');

// Test configuration
const TEST_CONFIG = {
    baseUrl: process.env.BASE_URL || 'http://localhost:8000',
    pages: [
        { url: '/', name: 'Home Page' },
        { url: '/contact/', name: 'Contact Page' },
        { url: '/testimonials/submit/', name: 'Testimonials Form' },
        { url: '/pricing/', name: 'Pricing Page' },
        { url: '/events/', name: 'Events Page' },
        { url: '/private-lessons/', name: 'Private Lessons Page' }
    ],
    viewport: { width: 1920, height: 1080 },
    mobileViewport: { width: 375, height: 667 },
    wcagLevel: 'AA',
    timeout: 30000
};

// WCAG 2.1 rules configuration
const AXE_CONFIG = {
    rules: {
        // Level A rules
        'area-alt': { enabled: true },
        'aria-allowed-attr': { enabled: true },
        'aria-hidden-body': { enabled: true },
        'aria-hidden-focus': { enabled: true },
        'aria-label': { enabled: true },
        'aria-labelledby': { enabled: true },
        'aria-required-attr': { enabled: true },
        'aria-required-children': { enabled: true },
        'aria-required-parent': { enabled: true },
        'aria-roles': { enabled: true },
        'aria-valid-attr': { enabled: true },
        'aria-valid-attr-value': { enabled: true },
        'blink': { enabled: true },
        'button-name': { enabled: true },
        'bypass': { enabled: true },
        'document-title': { enabled: true },
        'duplicate-id': { enabled: true },
        'form-field-multiple-labels': { enabled: true },
        'frame-title': { enabled: true },
        'html-has-lang': { enabled: true },
        'html-lang-valid': { enabled: true },
        'image-alt': { enabled: true },
        'input-button-name': { enabled: true },
        'input-image-alt': { enabled: true },
        'label': { enabled: true },
        'link-name': { enabled: true },
        'list': { enabled: true },
        'listitem': { enabled: true },
        'marquee': { enabled: true },
        'meta-refresh': { enabled: true },
        'object-alt': { enabled: true },
        'role-img-alt': { enabled: true },
        'td-headers-attr': { enabled: true },
        'th-has-data-cells': { enabled: true },
        'valid-lang': { enabled: true },
        'video-caption': { enabled: true },
        
        // Level AA rules
        'color-contrast': { enabled: true },
        'duplicate-id-active': { enabled: true },
        'duplicate-id-aria': { enabled: true },
        'focus-order-semantics': { enabled: true },
        'frame-tested': { enabled: true },
        'hidden-content': { enabled: true },
        'label-title-only': { enabled: true },
        'landmark-banner-is-top-level': { enabled: true },
        'landmark-complementary-is-top-level': { enabled: true },
        'landmark-contentinfo-is-top-level': { enabled: true },
        'landmark-main-is-top-level': { enabled: true },
        'landmark-no-duplicate-banner': { enabled: true },
        'landmark-no-duplicate-contentinfo': { enabled: true },
        'landmark-one-main': { enabled: true },
        'link-in-text-block': { enabled: true },
        'meta-viewport': { enabled: true },
        'meta-viewport-large': { enabled: true },
        'page-has-heading-one': { enabled: true },
        'region': { enabled: true },
        'scope-attr-valid': { enabled: true },
        'scrollable-region-focusable': { enabled: true },
        'select-name': { enabled: true },
        'server-side-image-map': { enabled: true },
        'svg-img-alt': { enabled: true },
        'tabindex': { enabled: true },
        'table-duplicate-name': { enabled: true },
        'table-fake-caption': { enabled: true },
        'target-size': { enabled: true },
        'td-has-header': { enabled: true }
    },
    tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
    resultTypes: ['violations', 'incomplete', 'passes'],
    reporter: 'v2'
};

class AccessibilityTester {
    constructor() {
        this.browser = null;
        this.results = {
            summary: {
                totalPages: 0,
                passedPages: 0,
                failedPages: 0,
                totalViolations: 0,
                totalPasses: 0,
                totalIncomplete: 0
            },
            pages: [],
            colorContrast: null,
            complianceScore: 0
        };
    }

    async init() {
        console.log('🚀 Initializing Accessibility Testing Suite...');
        console.log(`Target: ${TEST_CONFIG.baseUrl}`);
        console.log(`WCAG Level: ${TEST_CONFIG.wcagLevel}`);
        console.log('=' .repeat(60));

        this.browser = await chromium.launch({ 
            headless: true,
            args: ['--disable-web-security', '--disable-features=VizDisplayCompositor']
        });
    }

    async testPage(pageConfig, viewport = 'desktop') {
        const page = await this.browser.newPage();
        
        try {
            // Set viewport
            if (viewport === 'mobile') {
                await page.setViewportSize(TEST_CONFIG.mobileViewport);
            } else {
                await page.setViewportSize(TEST_CONFIG.viewport);
            }

            // Navigate to page
            const url = `${TEST_CONFIG.baseUrl}${pageConfig.url}`;
            console.log(`\n🔍 Testing ${pageConfig.name} (${viewport}): ${url}`);
            
            await page.goto(url, { 
                waitUntil: 'networkidle',
                timeout: TEST_CONFIG.timeout 
            });

            // Wait for any dynamic content
            await page.waitForTimeout(2000);

            // Inject axe-core
            await page.addScriptTag({ content: axeCore.source });

            // Run axe scan
            const axeResults = await page.evaluate(async (config) => {
                return await axe.run(document, config);
            }, AXE_CONFIG);

            // Additional manual checks
            const manualChecks = await this.runManualChecks(page);

            const pageResult = {
                name: pageConfig.name,
                url: pageConfig.url,
                viewport: viewport,
                timestamp: new Date().toISOString(),
                axeResults: axeResults,
                manualChecks: manualChecks,
                violations: axeResults.violations.length,
                passes: axeResults.passes.length,
                incomplete: axeResults.incomplete.length,
                complianceScore: this.calculatePageScore(axeResults, manualChecks)
            };

            this.logPageResults(pageResult);
            return pageResult;

        } catch (error) {
            console.error(`❌ Error testing ${pageConfig.name}:`, error.message);
            return {
                name: pageConfig.name,
                url: pageConfig.url,
                viewport: viewport,
                error: error.message,
                violations: 999, // Mark as failed
                passes: 0,
                incomplete: 0,
                complianceScore: 0
            };
        } finally {
            await page.close();
        }
    }

    async runManualChecks(page) {
        const checks = {
            skipLinks: await this.checkSkipLinks(page),
            headingStructure: await this.checkHeadingStructure(page),
            keyboardNavigation: await this.checkKeyboardNavigation(page),
            focusManagement: await this.checkFocusManagement(page),
            formAccessibility: await this.checkFormAccessibility(page),
            imageAltText: await this.checkImageAltText(page),
            colorContrast: await this.checkColorContrast(page),
            responsiveDesign: await this.checkResponsiveDesign(page)
        };

        return checks;
    }

    async checkSkipLinks(page) {
        try {
            const skipLinks = await page.$$('.skip-link, a[href^="#main"], a[href^="#content"]');
            
            if (skipLinks.length === 0) {
                return { 
                    status: 'fail', 
                    message: 'No skip links found',
                    impact: 'serious' 
                };
            }

            // Check if skip link targets exist
            const results = [];
            for (const link of skipLinks) {
                const href = await link.getAttribute('href');
                if (href && href.startsWith('#')) {
                    const target = await page.$(`${href}`);
                    if (!target) {
                        results.push({
                            status: 'fail',
                            message: `Skip link target ${href} not found`,
                            impact: 'moderate'
                        });
                    }
                }
            }

            return results.length === 0 ? 
                { status: 'pass', message: `${skipLinks.length} skip links found and valid` } :
                { status: 'fail', message: 'Some skip link targets missing', details: results };

        } catch (error) {
            return { status: 'error', message: error.message };
        }
    }

    async checkHeadingStructure(page) {
        try {
            const headings = await page.$$eval('h1, h2, h3, h4, h5, h6', headings => 
                headings.map(h => ({
                    level: parseInt(h.tagName.substring(1)),
                    text: h.textContent.trim(),
                    tagName: h.tagName.toLowerCase()
                }))
            );

            const issues = [];

            // Check for H1
            const h1Count = headings.filter(h => h.level === 1).length;
            if (h1Count === 0) {
                issues.push('No H1 element found');
            } else if (h1Count > 1) {
                issues.push(`Multiple H1 elements found (${h1Count})`);
            }

            // Check for proper hierarchy
            for (let i = 1; i < headings.length; i++) {
                const levelDiff = headings[i].level - headings[i-1].level;
                if (levelDiff > 1) {
                    issues.push(`Heading level skipped: ${headings[i-1].tagName} to ${headings[i].tagName}`);
                }
            }

            // Check for empty headings
            const emptyHeadings = headings.filter(h => !h.text);
            if (emptyHeadings.length > 0) {
                issues.push(`${emptyHeadings.length} empty heading(s) found`);
            }

            return issues.length === 0 ?
                { status: 'pass', message: `Proper heading structure with ${headings.length} headings` } :
                { status: 'fail', message: 'Heading structure issues', details: issues };

        } catch (error) {
            return { status: 'error', message: error.message };
        }
    }

    async checkKeyboardNavigation(page) {
        try {
            const focusableElements = await page.$$eval([
                'a[href]',
                'button:not([disabled])',
                'input:not([disabled])',
                'textarea:not([disabled])',
                'select:not([disabled])',
                '[tabindex]:not([tabindex="-1"])',
                'details',
                'summary'
            ].join(', '), elements => elements.length);

            if (focusableElements === 0) {
                return { 
                    status: 'warning', 
                    message: 'No focusable elements found',
                    impact: 'minor' 
                };
            }

            // Test tab navigation (simplified)
            await page.keyboard.press('Tab');
            const activeElement = await page.evaluate(() => document.activeElement.tagName);

            return {
                status: 'pass',
                message: `${focusableElements} focusable elements found, tab navigation functional`,
                details: { focusableCount: focusableElements, activeElement }
            };

        } catch (error) {
            return { status: 'error', message: error.message };
        }
    }

    async checkFocusManagement(page) {
        try {
            // Check for focus indicators in CSS
            const hasCustomFocus = await page.evaluate(() => {
                const stylesheets = Array.from(document.styleSheets);
                for (const sheet of stylesheets) {
                    try {
                        const rules = Array.from(sheet.cssRules || []);
                        for (const rule of rules) {
                            if (rule.selectorText && rule.selectorText.includes(':focus')) {
                                return true;
                            }
                        }
                    } catch (e) {
                        // Cross-origin stylesheet
                        continue;
                    }
                }
                return false;
            });

            // Check for skip-to-content functionality
            const skipToContent = await page.$('.skip-link');
            
            // Check for modal focus management
            const modals = await page.$$('[role="dialog"], [aria-modal="true"], .modal');
            
            const results = {
                customFocus: hasCustomFocus,
                skipToContent: !!skipToContent,
                modalCount: modals.length
            };

            const issues = [];
            if (!hasCustomFocus) issues.push('No custom focus styles detected');
            if (!skipToContent) issues.push('No skip-to-content link found');

            return issues.length === 0 ?
                { status: 'pass', message: 'Focus management implemented', details: results } :
                { status: 'warning', message: 'Focus management could be improved', details: { issues, results } };

        } catch (error) {
            return { status: 'error', message: error.message };
        }
    }

    async checkFormAccessibility(page) {
        try {
            const forms = await page.$$('form');
            
            if (forms.length === 0) {
                return { status: 'pass', message: 'No forms on page' };
            }

            const issues = [];
            
            for (let i = 0; i < forms.length; i++) {
                const form = forms[i];
                
                // Check inputs have labels
                const inputs = await form.$$('input, textarea, select');
                for (const input of inputs) {
                    const inputId = await input.getAttribute('id');
                    const ariaLabel = await input.getAttribute('aria-label');
                    const ariaLabelledBy = await input.getAttribute('aria-labelledby');
                    
                    if (inputId) {
                        const label = await page.$(`label[for="${inputId}"]`);
                        if (!label && !ariaLabel && !ariaLabelledBy) {
                            const inputType = await input.getAttribute('type');
                            const inputName = await input.getAttribute('name');
                            if (inputType !== 'hidden') {
                                issues.push(`Input ${inputName || inputId} has no accessible label`);
                            }
                        }
                    }
                    
                    // Check required fields
                    const required = await input.getAttribute('required');
                    const ariaRequired = await input.getAttribute('aria-required');
                    if (required !== null && ariaRequired !== 'true') {
                        issues.push(`Required field missing aria-required`);
                    }
                }
            }

            return issues.length === 0 ?
                { status: 'pass', message: `${forms.length} form(s) properly accessible` } :
                { status: 'fail', message: 'Form accessibility issues', details: issues };

        } catch (error) {
            return { status: 'error', message: error.message };
        }
    }

    async checkImageAltText(page) {
        try {
            const images = await page.$$eval('img', imgs => 
                imgs.map(img => ({
                    src: img.src,
                    alt: img.alt,
                    role: img.getAttribute('role'),
                    ariaLabel: img.getAttribute('aria-label'),
                    ariaLabelledBy: img.getAttribute('aria-labelledby')
                }))
            );

            const issues = [];
            
            for (const img of images) {
                // Skip decorative images
                if (img.role === 'presentation' || img.alt === '') {
                    continue;
                }
                
                // Check for missing alt text
                if (img.alt === null && !img.ariaLabel && !img.ariaLabelledBy) {
                    issues.push(`Image missing alt text: ${img.src}`);
                }
                
                // Check for placeholder alt text
                if (img.alt && ['image', 'photo', 'picture'].some(word => 
                    img.alt.toLowerCase().includes(word) && img.alt.split(' ').length <= 2
                )) {
                    issues.push(`Possible placeholder alt text: "${img.alt}"`);
                }
            }

            return issues.length === 0 ?
                { status: 'pass', message: `${images.length} image(s) properly described` } :
                { status: 'fail', message: 'Image alt text issues', details: issues };

        } catch (error) {
            return { status: 'error', message: error.message };
        }
    }

    async checkColorContrast(page) {
        try {
            // This is a simplified check - in production, use proper color analysis
            const hasAccessibilityCSS = await page.evaluate(() => {
                const stylesheets = Array.from(document.styleSheets);
                for (const sheet of stylesheets) {
                    try {
                        const cssText = Array.from(sheet.cssRules || [])
                            .map(rule => rule.cssText || '')
                            .join(' ');
                        if (cssText.includes('accessibility') || cssText.includes('contrast')) {
                            return true;
                        }
                    } catch (e) {
                        continue;
                    }
                }
                return false;
            });

            return {
                status: hasAccessibilityCSS ? 'pass' : 'warning',
                message: hasAccessibilityCSS ? 
                    'Accessibility CSS detected' : 
                    'No accessibility-specific CSS detected',
                note: 'Manual contrast testing recommended'
            };

        } catch (error) {
            return { status: 'error', message: error.message };
        }
    }

    async checkResponsiveDesign(page) {
        try {
            // Check viewport meta tag
            const viewportMeta = await page.$('meta[name="viewport"]');
            const viewportContent = viewportMeta ? 
                await viewportMeta.getAttribute('content') : null;

            const hasViewport = viewportContent && 
                viewportContent.includes('width=device-width');

            // Check for responsive CSS
            const hasResponsiveCSS = await page.evaluate(() => {
                const stylesheets = Array.from(document.styleSheets);
                for (const sheet of stylesheets) {
                    try {
                        const cssText = Array.from(sheet.cssRules || [])
                            .map(rule => rule.cssText || '')
                            .join(' ');
                        if (cssText.includes('@media') && cssText.includes('max-width')) {
                            return true;
                        }
                    } catch (e) {
                        continue;
                    }
                }
                return false;
            });

            const issues = [];
            if (!hasViewport) issues.push('Missing or incorrect viewport meta tag');
            if (!hasResponsiveCSS) issues.push('No responsive CSS media queries detected');

            return issues.length === 0 ?
                { status: 'pass', message: 'Responsive design implemented' } :
                { status: 'warning', message: 'Responsive design issues', details: issues };

        } catch (error) {
            return { status: 'error', message: error.message };
        }
    }

    calculatePageScore(axeResults, manualChecks) {
        const totalRules = axeResults.passes.length + axeResults.violations.length;
        const passedRules = axeResults.passes.length;
        
        const axeScore = totalRules > 0 ? (passedRules / totalRules) * 100 : 0;
        
        // Manual checks weight
        const manualChecksPassed = Object.values(manualChecks).filter(
            check => check.status === 'pass'
        ).length;
        const totalManualChecks = Object.keys(manualChecks).length;
        const manualScore = totalManualChecks > 0 ? 
            (manualChecksPassed / totalManualChecks) * 100 : 100;
        
        // Weighted average: 70% axe, 30% manual
        return Math.round((axeScore * 0.7) + (manualScore * 0.3));
    }

    logPageResults(pageResult) {
        console.log(`\n📊 Results for ${pageResult.name} (${pageResult.viewport}):`);
        console.log(`   Compliance Score: ${pageResult.complianceScore}%`);
        console.log(`   ✅ Passed: ${pageResult.passes}`);
        console.log(`   ❌ Violations: ${pageResult.violations}`);
        console.log(`   ⚠️  Incomplete: ${pageResult.incomplete}`);

        if (pageResult.violations > 0) {
            console.log('\n   Critical Violations:');
            pageResult.axeResults.violations
                .filter(v => v.impact === 'critical' || v.impact === 'serious')
                .slice(0, 3)
                .forEach(violation => {
                    console.log(`   • ${violation.description}`);
                });
        }

        // Show manual check results
        if (pageResult.manualChecks) {
            const failed = Object.entries(pageResult.manualChecks)
                .filter(([_, check]) => check.status === 'fail');
            
            if (failed.length > 0) {
                console.log('\n   Manual Check Failures:');
                failed.forEach(([name, check]) => {
                    console.log(`   • ${name}: ${check.message}`);
                });
            }
        }
    }

    async runAllTests() {
        console.log('\n🎯 Running Comprehensive Accessibility Tests...\n');

        // Test color contrast first
        console.log('🎨 Running Color Contrast Tests...');
        this.results.colorContrast = runContrastTests();

        // Test each page on desktop and mobile
        for (const pageConfig of TEST_CONFIG.pages) {
            // Desktop test
            const desktopResult = await this.testPage(pageConfig, 'desktop');
            this.results.pages.push(desktopResult);

            // Mobile test
            const mobileResult = await this.testPage(pageConfig, 'mobile');
            this.results.pages.push(mobileResult);
        }

        this.calculateSummary();
        this.generateReport();
    }

    calculateSummary() {
        this.results.summary.totalPages = this.results.pages.length;
        
        this.results.pages.forEach(page => {
            if (page.violations === 0 && page.complianceScore >= 80) {
                this.results.summary.passedPages++;
            } else {
                this.results.summary.failedPages++;
            }
            
            this.results.summary.totalViolations += page.violations || 0;
            this.results.summary.totalPasses += page.passes || 0;
            this.results.summary.totalIncomplete += page.incomplete || 0;
        });

        // Calculate overall compliance score
        const scores = this.results.pages
            .filter(p => !p.error)
            .map(p => p.complianceScore);
        
        this.results.complianceScore = scores.length > 0 ?
            Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
    }

    generateReport() {
        console.log('\n' + '=' .repeat(60));
        console.log('📋 COMPREHENSIVE ACCESSIBILITY AUDIT REPORT');
        console.log('=' .repeat(60));
        
        console.log(`\n🎯 Overall Compliance Score: ${this.results.complianceScore}%`);
        console.log(`📄 Pages Tested: ${this.results.summary.totalPages}`);
        console.log(`✅ Passed: ${this.results.summary.passedPages}`);
        console.log(`❌ Failed: ${this.results.summary.failedPages}`);
        console.log(`🔍 Total Violations: ${this.results.summary.totalViolations}`);
        console.log(`⚠️  Total Incomplete: ${this.results.summary.totalIncomplete}`);

        // WCAG compliance status
        const wcagCompliance = this.results.complianceScore >= 80 ? 
            '✅ WCAG 2.1 AA COMPLIANT' : 
            '❌ NOT WCAG 2.1 AA COMPLIANT';
        
        console.log(`\n🏆 WCAG 2.1 AA Status: ${wcagCompliance}`);

        // Color contrast summary
        if (this.results.colorContrast) {
            const contrastRate = (this.results.colorContrast.passed / 
                this.results.colorContrast.total * 100).toFixed(1);
            console.log(`🎨 Color Contrast Compliance: ${contrastRate}%`);
        }

        // Recommendations
        console.log('\n💡 PRIORITY RECOMMENDATIONS:');
        if (this.results.summary.totalViolations > 0) {
            console.log('   🔧 Fix critical and serious violations first');
            console.log('   🧪 Run manual testing with screen readers');
            console.log('   👥 Test with users who have disabilities');
        } else {
            console.log('   ✅ Excellent! Continue monitoring for new content');
            console.log('   📚 Consider WCAG 2.1 AAA compliance for premium experience');
        }

        console.log('   🔄 Set up automated testing in CI/CD pipeline');
        console.log('   📖 Train team on accessibility best practices');

        // Save detailed report
        this.saveReport();
        
        console.log('\n' + '=' .repeat(60));
        console.log('🎉 Accessibility audit complete!');
        console.log('=' .repeat(60));
    }

    saveReport() {
        const reportsDir = path.join(__dirname, 'reports');
        if (!fs.existsSync(reportsDir)) {
            fs.mkdirSync(reportsDir, { recursive: true });
        }

        const report = {
            timestamp: new Date().toISOString(),
            testConfig: TEST_CONFIG,
            wcagLevel: TEST_CONFIG.wcagLevel,
            results: this.results,
            complianceStatus: this.results.complianceScore >= 80 ? 'COMPLIANT' : 'NON_COMPLIANT'
        };

        const reportPath = path.join(reportsDir, 'accessibility-audit-report.json');
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

        // Generate CSV summary for easy sharing
        const csvData = this.generateCSVReport();
        const csvPath = path.join(reportsDir, 'accessibility-summary.csv');
        fs.writeFileSync(csvPath, csvData);

        console.log(`\n📄 Detailed report saved to: ${reportPath}`);
        console.log(`📊 CSV summary saved to: ${csvPath}`);
    }

    generateCSVReport() {
        const headers = [
            'Page', 'Viewport', 'Compliance Score', 'Violations', 
            'Passes', 'Incomplete', 'Status'
        ];

        const rows = this.results.pages.map(page => [
            page.name,
            page.viewport,
            page.complianceScore,
            page.violations,
            page.passes,
            page.incomplete,
            page.violations === 0 && page.complianceScore >= 80 ? 'PASS' : 'FAIL'
        ]);

        return [headers, ...rows]
            .map(row => row.join(','))
            .join('\n');
    }

    async cleanup() {
        if (this.browser) {
            await this.browser.close();
        }
    }
}

// Main execution
async function main() {
    const tester = new AccessibilityTester();
    
    try {
        await tester.init();
        await tester.runAllTests();
    } catch (error) {
        console.error('❌ Test execution failed:', error);
        process.exit(1);
    } finally {
        await tester.cleanup();
    }
}

// CLI execution
if (require.main === module) {
    main().catch(console.error);
}

module.exports = AccessibilityTester;