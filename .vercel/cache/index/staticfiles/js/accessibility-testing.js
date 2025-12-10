/**
 * Accessibility Testing and Validation Suite
 * WCAG 2.1 AA Compliance Testing
 * SPEC_06 Group C Task 8 - Sabor Con Flow Dance
 */

class AccessibilityTester {
    constructor() {
        this.testResults = {
            passed: 0,
            failed: 0,
            warnings: 0,
            violations: []
        };
        this.isAxeCoreLoaded = false;
        this.init();
    }

    async init() {
        // Load axe-core if available
        await this.loadAxeCore();
        
        // Run comprehensive accessibility tests
        this.runAccessibilityTests();
        
        // Setup continuous monitoring
        this.setupContinuousMonitoring();
        
        // Generate report
        this.generateAccessibilityReport();
    }

    /**
     * Load axe-core library for automated testing
     */
    async loadAxeCore() {
        try {
            if (typeof axe !== 'undefined') {
                this.isAxeCoreLoaded = true;
                console.log('✅ axe-core loaded successfully');
                return;
            }

            // Try to load axe-core from CDN
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/axe-core@4.8.3/axe.min.js';
            script.onload = () => {
                this.isAxeCoreLoaded = true;
                console.log('✅ axe-core loaded from CDN');
                this.runAxeTests();
            };
            script.onerror = () => {
                console.warn('⚠️ Could not load axe-core from CDN, running manual tests only');
            };
            document.head.appendChild(script);
        } catch (error) {
            console.warn('⚠️ axe-core not available, running manual tests only');
        }
    }

    /**
     * Run comprehensive accessibility tests
     */
    runAccessibilityTests() {
        console.log('🔍 Starting accessibility tests...');
        
        // Manual WCAG tests
        this.testColorContrast();
        this.testKeyboardNavigation();
        this.testFormAccessibility();
        this.testHeadingStructure();
        this.testSkipLinks();
        this.testAriaLabels();
        this.testFocusManagement();
        this.testImageAltText();
        this.testLandmarks();
        this.testTextContent();
        
        // Browser-specific tests
        this.testScreenReaderSupport();
        this.testReducedMotion();
        this.testHighContrast();
        
        console.log(`📊 Manual tests completed: ${this.testResults.passed} passed, ${this.testResults.failed} failed, ${this.testResults.warnings} warnings`);
    }

    /**
     * Run axe-core automated tests
     */
    async runAxeTests() {
        if (!this.isAxeCoreLoaded) return;

        try {
            const results = await axe.run();
            
            console.log('🔍 axe-core automated scan completed');
            console.log(`✅ ${results.passes.length} rules passed`);
            console.log(`❌ ${results.violations.length} violations found`);
            console.log(`⚠️ ${results.incomplete.length} incomplete tests`);
            
            // Process violations
            results.violations.forEach(violation => {
                this.addViolation({
                    type: 'axe-violation',
                    rule: violation.id,
                    impact: violation.impact,
                    description: violation.description,
                    help: violation.help,
                    helpUrl: violation.helpUrl,
                    elements: violation.nodes.map(node => ({
                        target: node.target,
                        html: node.html,
                        failureSummary: node.failureSummary
                    }))
                });
                this.testResults.failed++;
            });

            // Process incomplete tests
            results.incomplete.forEach(incomplete => {
                this.addViolation({
                    type: 'axe-incomplete',
                    rule: incomplete.id,
                    description: incomplete.description,
                    help: incomplete.help,
                    elements: incomplete.nodes.map(node => ({
                        target: node.target,
                        html: node.html
                    }))
                });
                this.testResults.warnings++;
            });

            this.testResults.passed += results.passes.length;
            
        } catch (error) {
            console.error('❌ axe-core test failed:', error);
        }
    }

    /**
     * Test color contrast ratios
     */
    testColorContrast() {
        console.log('🎨 Testing color contrast...');
        
        const elements = document.querySelectorAll('*');
        let contrastIssues = 0;
        
        elements.forEach(element => {
            const computedStyle = window.getComputedStyle(element);
            const color = computedStyle.color;
            const backgroundColor = computedStyle.backgroundColor;
            const fontSize = parseFloat(computedStyle.fontSize);
            const fontWeight = computedStyle.fontWeight;
            
            // Skip elements with no text content
            if (!element.textContent?.trim()) return;
            
            // Check contrast ratio (simplified check)
            const contrastRatio = this.calculateContrastRatio(color, backgroundColor);
            const isLargeText = fontSize >= 18 || (fontSize >= 14 && (fontWeight === 'bold' || parseInt(fontWeight) >= 700));
            const requiredRatio = isLargeText ? 3 : 4.5;
            
            if (contrastRatio > 0 && contrastRatio < requiredRatio) {
                this.addViolation({
                    type: 'color-contrast',
                    element: element.tagName.toLowerCase(),
                    selector: this.getElementSelector(element),
                    contrastRatio: contrastRatio.toFixed(2),
                    requiredRatio: requiredRatio,
                    color: color,
                    backgroundColor: backgroundColor,
                    message: `Insufficient color contrast: ${contrastRatio.toFixed(2)}:1 (required: ${requiredRatio}:1)`
                });
                contrastIssues++;
            }
        });
        
        if (contrastIssues === 0) {
            this.testResults.passed++;
            console.log('✅ Color contrast test passed');
        } else {
            this.testResults.failed++;
            console.log(`❌ Color contrast test failed: ${contrastIssues} issues found`);
        }
    }

    /**
     * Test keyboard navigation
     */
    testKeyboardNavigation() {
        console.log('⌨️ Testing keyboard navigation...');
        
        const focusableElements = document.querySelectorAll([
            'a[href]',
            'button:not([disabled])',
            'input:not([disabled])',
            'textarea:not([disabled])',
            'select:not([disabled])',
            '[tabindex]:not([tabindex="-1"])',
            'details',
            'summary'
        ].join(', '));
        
        let keyboardIssues = 0;
        
        focusableElements.forEach(element => {
            // Check if element is focusable
            const tabIndex = element.getAttribute('tabindex');
            const isHidden = element.hidden || element.style.display === 'none' || 
                            element.style.visibility === 'hidden';
            
            if (isHidden) return;
            
            // Check for missing focus indicators
            const computedStyle = window.getComputedStyle(element, ':focus');
            const outline = computedStyle.outline;
            const boxShadow = computedStyle.boxShadow;
            
            if (outline === 'none' && boxShadow === 'none') {
                this.addViolation({
                    type: 'keyboard-navigation',
                    element: element.tagName.toLowerCase(),
                    selector: this.getElementSelector(element),
                    message: 'Element is focusable but has no visible focus indicator'
                });
                keyboardIssues++;
            }
            
            // Check for keyboard event handlers
            if (element.onclick && !element.onkeydown && !element.onkeypress) {
                this.addViolation({
                    type: 'keyboard-navigation',
                    element: element.tagName.toLowerCase(),
                    selector: this.getElementSelector(element),
                    message: 'Element has click handler but no keyboard handler'
                });
                keyboardIssues++;
            }
        });
        
        if (keyboardIssues === 0) {
            this.testResults.passed++;
            console.log('✅ Keyboard navigation test passed');
        } else {
            this.testResults.failed++;
            console.log(`❌ Keyboard navigation test failed: ${keyboardIssues} issues found`);
        }
    }

    /**
     * Test form accessibility
     */
    testFormAccessibility() {
        console.log('📝 Testing form accessibility...');
        
        const forms = document.querySelectorAll('form');
        let formIssues = 0;
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                // Check for labels
                const id = input.getAttribute('id');
                const ariaLabel = input.getAttribute('aria-label');
                const ariaLabelledBy = input.getAttribute('aria-labelledby');
                const label = id ? form.querySelector(`label[for="${id}"]`) : null;
                
                if (!ariaLabel && !ariaLabelledBy && !label) {
                    this.addViolation({
                        type: 'form-accessibility',
                        element: input.tagName.toLowerCase(),
                        selector: this.getElementSelector(input),
                        message: 'Form input has no associated label'
                    });
                    formIssues++;
                }
                
                // Check required fields
                if (input.required && !input.getAttribute('aria-required')) {
                    this.addViolation({
                        type: 'form-accessibility',
                        element: input.tagName.toLowerCase(),
                        selector: this.getElementSelector(input),
                        message: 'Required field missing aria-required attribute'
                    });
                    formIssues++;
                }
                
                // Check for error associations
                const isInvalid = input.getAttribute('aria-invalid') === 'true';
                const describedBy = input.getAttribute('aria-describedby');
                
                if (isInvalid && !describedBy) {
                    this.addViolation({
                        type: 'form-accessibility',
                        element: input.tagName.toLowerCase(),
                        selector: this.getElementSelector(input),
                        message: 'Invalid field not associated with error message'
                    });
                    formIssues++;
                }
            });
        });
        
        if (formIssues === 0) {
            this.testResults.passed++;
            console.log('✅ Form accessibility test passed');
        } else {
            this.testResults.failed++;
            console.log(`❌ Form accessibility test failed: ${formIssues} issues found`);
        }
    }

    /**
     * Test heading structure
     */
    testHeadingStructure() {
        console.log('📑 Testing heading structure...');
        
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        let headingIssues = 0;
        let previousLevel = 0;
        let hasH1 = false;
        
        headings.forEach(heading => {
            const level = parseInt(heading.tagName.substring(1));
            
            // Check for H1
            if (level === 1) {
                if (hasH1) {
                    this.addViolation({
                        type: 'heading-structure',
                        element: heading.tagName.toLowerCase(),
                        selector: this.getElementSelector(heading),
                        message: 'Multiple H1 elements found on page'
                    });
                    headingIssues++;
                }
                hasH1 = true;
            }
            
            // Check for proper heading hierarchy
            if (previousLevel > 0 && level > previousLevel + 1) {
                this.addViolation({
                    type: 'heading-structure',
                    element: heading.tagName.toLowerCase(),
                    selector: this.getElementSelector(heading),
                    message: `Heading level skipped from H${previousLevel} to H${level}`
                });
                headingIssues++;
            }
            
            // Check for empty headings
            if (!heading.textContent.trim()) {
                this.addViolation({
                    type: 'heading-structure',
                    element: heading.tagName.toLowerCase(),
                    selector: this.getElementSelector(heading),
                    message: 'Empty heading element'
                });
                headingIssues++;
            }
            
            previousLevel = level;
        });
        
        // Check if page has H1
        if (!hasH1) {
            this.addViolation({
                type: 'heading-structure',
                message: 'Page is missing H1 element'
            });
            headingIssues++;
        }
        
        if (headingIssues === 0) {
            this.testResults.passed++;
            console.log('✅ Heading structure test passed');
        } else {
            this.testResults.failed++;
            console.log(`❌ Heading structure test failed: ${headingIssues} issues found`);
        }
    }

    /**
     * Test skip links
     */
    testSkipLinks() {
        console.log('🔗 Testing skip links...');
        
        const skipLinks = document.querySelectorAll('.skip-link, a[href^="#main"], a[href^="#content"]');
        let skipLinkIssues = 0;
        
        if (skipLinks.length === 0) {
            this.addViolation({
                type: 'skip-links',
                message: 'No skip links found on page'
            });
            skipLinkIssues++;
        } else {
            skipLinks.forEach(link => {
                const href = link.getAttribute('href');
                const target = document.querySelector(href);
                
                if (!target) {
                    this.addViolation({
                        type: 'skip-links',
                        element: 'a',
                        selector: this.getElementSelector(link),
                        message: `Skip link target "${href}" not found`
                    });
                    skipLinkIssues++;
                }
            });
        }
        
        if (skipLinkIssues === 0) {
            this.testResults.passed++;
            console.log('✅ Skip links test passed');
        } else {
            this.testResults.failed++;
            console.log(`❌ Skip links test failed: ${skipLinkIssues} issues found`);
        }
    }

    /**
     * Test ARIA labels and attributes
     */
    testAriaLabels() {
        console.log('🏷️ Testing ARIA labels...');
        
        const elementsWithAria = document.querySelectorAll('[aria-label], [aria-labelledby], [role]');
        let ariaIssues = 0;
        
        elementsWithAria.forEach(element => {
            const role = element.getAttribute('role');
            const ariaLabel = element.getAttribute('aria-label');
            const ariaLabelledBy = element.getAttribute('aria-labelledby');
            
            // Check for empty aria-label
            if (ariaLabel !== null && !ariaLabel.trim()) {
                this.addViolation({
                    type: 'aria-labels',
                    element: element.tagName.toLowerCase(),
                    selector: this.getElementSelector(element),
                    message: 'Empty aria-label attribute'
                });
                ariaIssues++;
            }
            
            // Check for invalid aria-labelledby references
            if (ariaLabelledBy) {
                const labelIds = ariaLabelledBy.split(/\s+/);
                labelIds.forEach(labelId => {
                    if (!document.getElementById(labelId)) {
                        this.addViolation({
                            type: 'aria-labels',
                            element: element.tagName.toLowerCase(),
                            selector: this.getElementSelector(element),
                            message: `aria-labelledby references non-existent ID "${labelId}"`
                        });
                        ariaIssues++;
                    }
                });
            }
            
            // Check for redundant role attributes
            const implicitRole = this.getImplicitRole(element);
            if (role && role === implicitRole) {
                this.addViolation({
                    type: 'aria-labels',
                    element: element.tagName.toLowerCase(),
                    selector: this.getElementSelector(element),
                    message: `Redundant role="${role}" attribute`
                });
                this.testResults.warnings++;
            }
        });
        
        if (ariaIssues === 0) {
            this.testResults.passed++;
            console.log('✅ ARIA labels test passed');
        } else {
            this.testResults.failed++;
            console.log(`❌ ARIA labels test failed: ${ariaIssues} issues found`);
        }
    }

    /**
     * Test focus management
     */
    testFocusManagement() {
        console.log('🎯 Testing focus management...');
        
        const modals = document.querySelectorAll('[role="dialog"], .modal');
        const dropdowns = document.querySelectorAll('[aria-expanded]');
        let focusIssues = 0;
        
        // Test modals
        modals.forEach(modal => {
            if (!modal.getAttribute('aria-modal')) {
                this.addViolation({
                    type: 'focus-management',
                    element: modal.tagName.toLowerCase(),
                    selector: this.getElementSelector(modal),
                    message: 'Modal missing aria-modal attribute'
                });
                focusIssues++;
            }
            
            // Check for focus trap elements
            const focusableElements = modal.querySelectorAll([
                'a[href]', 'button:not([disabled])', 'input:not([disabled])',
                'textarea:not([disabled])', 'select:not([disabled])', '[tabindex]:not([tabindex="-1"])'
            ].join(', '));
            
            if (focusableElements.length === 0) {
                this.addViolation({
                    type: 'focus-management',
                    element: modal.tagName.toLowerCase(),
                    selector: this.getElementSelector(modal),
                    message: 'Modal has no focusable elements'
                });
                focusIssues++;
            }
        });
        
        // Test dropdowns
        dropdowns.forEach(dropdown => {
            const expanded = dropdown.getAttribute('aria-expanded') === 'true';
            const controls = dropdown.getAttribute('aria-controls');
            
            if (expanded && controls) {
                const controlledElement = document.getElementById(controls);
                if (!controlledElement) {
                    this.addViolation({
                        type: 'focus-management',
                        element: dropdown.tagName.toLowerCase(),
                        selector: this.getElementSelector(dropdown),
                        message: `aria-controls references non-existent ID "${controls}"`
                    });
                    focusIssues++;
                }
            }
        });
        
        if (focusIssues === 0) {
            this.testResults.passed++;
            console.log('✅ Focus management test passed');
        } else {
            this.testResults.failed++;
            console.log(`❌ Focus management test failed: ${focusIssues} issues found`);
        }
    }

    /**
     * Test image alt text
     */
    testImageAltText() {
        console.log('🖼️ Testing image alt text...');
        
        const images = document.querySelectorAll('img');
        let imageIssues = 0;
        
        images.forEach(img => {
            const alt = img.getAttribute('alt');
            const role = img.getAttribute('role');
            const ariaLabel = img.getAttribute('aria-label');
            
            // Skip decorative images
            if (role === 'presentation' || alt === '') return;
            
            if (alt === null && !ariaLabel) {
                this.addViolation({
                    type: 'image-alt-text',
                    element: 'img',
                    selector: this.getElementSelector(img),
                    src: img.src,
                    message: 'Image missing alt attribute'
                });
                imageIssues++;
            }
            
            // Check for placeholder alt text
            if (alt && (alt.includes('image') || alt.includes('photo') || alt.includes('picture'))) {
                this.addViolation({
                    type: 'image-alt-text',
                    element: 'img',
                    selector: this.getElementSelector(img),
                    alt: alt,
                    message: 'Alt text appears to be placeholder text'
                });
                this.testResults.warnings++;
            }
        });
        
        if (imageIssues === 0) {
            this.testResults.passed++;
            console.log('✅ Image alt text test passed');
        } else {
            this.testResults.failed++;
            console.log(`❌ Image alt text test failed: ${imageIssues} issues found`);
        }
    }

    /**
     * Test landmarks and page structure
     */
    testLandmarks() {
        console.log('🗺️ Testing landmarks...');
        
        const main = document.querySelector('main, [role="main"]');
        const nav = document.querySelector('nav, [role="navigation"]');
        const header = document.querySelector('header, [role="banner"]');
        const footer = document.querySelector('footer, [role="contentinfo"]');
        
        let landmarkIssues = 0;
        
        if (!main) {
            this.addViolation({
                type: 'landmarks',
                message: 'Page missing main landmark'
            });
            landmarkIssues++;
        }
        
        if (!nav) {
            this.addViolation({
                type: 'landmarks',
                message: 'Page missing navigation landmark'
            });
            landmarkIssues++;
        }
        
        // Check for multiple landmarks without labels
        const navElements = document.querySelectorAll('nav, [role="navigation"]');
        if (navElements.length > 1) {
            navElements.forEach(navElement => {
                const ariaLabel = navElement.getAttribute('aria-label');
                const ariaLabelledBy = navElement.getAttribute('aria-labelledby');
                
                if (!ariaLabel && !ariaLabelledBy) {
                    this.addViolation({
                        type: 'landmarks',
                        element: navElement.tagName.toLowerCase(),
                        selector: this.getElementSelector(navElement),
                        message: 'Navigation landmark missing accessible name'
                    });
                    landmarkIssues++;
                }
            });
        }
        
        if (landmarkIssues === 0) {
            this.testResults.passed++;
            console.log('✅ Landmarks test passed');
        } else {
            this.testResults.failed++;
            console.log(`❌ Landmarks test failed: ${landmarkIssues} issues found`);
        }
    }

    /**
     * Test text content accessibility
     */
    testTextContent() {
        console.log('📝 Testing text content...');
        
        const textElements = document.querySelectorAll('p, li, td, th, span, div');
        let textIssues = 0;
        
        textElements.forEach(element => {
            const text = element.textContent.trim();
            if (!text) return;
            
            // Check for very small text
            const fontSize = parseFloat(window.getComputedStyle(element).fontSize);
            if (fontSize < 12) {
                this.addViolation({
                    type: 'text-content',
                    element: element.tagName.toLowerCase(),
                    selector: this.getElementSelector(element),
                    fontSize: fontSize,
                    message: `Text size too small: ${fontSize}px (minimum recommended: 12px)`
                });
                textIssues++;
            }
            
            // Check for very long lines
            const width = element.offsetWidth;
            const approxCharsPerLine = width / (fontSize * 0.5);
            if (approxCharsPerLine > 80) {
                this.addViolation({
                    type: 'text-content',
                    element: element.tagName.toLowerCase(),
                    selector: this.getElementSelector(element),
                    message: 'Text line length may be too long for comfortable reading'
                });
                this.testResults.warnings++;
            }
        });
        
        if (textIssues === 0) {
            this.testResults.passed++;
            console.log('✅ Text content test passed');
        } else {
            this.testResults.failed++;
            console.log(`❌ Text content test failed: ${textIssues} issues found`);
        }
    }

    /**
     * Test screen reader support
     */
    testScreenReaderSupport() {
        console.log('🔊 Testing screen reader support...');
        
        // Check for live regions
        const liveRegions = document.querySelectorAll('[aria-live]');
        if (liveRegions.length === 0) {
            this.addViolation({
                type: 'screen-reader',
                message: 'No ARIA live regions found for dynamic content announcements'
            });
            this.testResults.warnings++;
        }
        
        // Check for screen reader only content
        const srOnly = document.querySelectorAll('.sr-only, .visually-hidden');
        if (srOnly.length > 0) {
            this.testResults.passed++;
            console.log('✅ Screen reader only content found');
        }
        
        console.log('✅ Screen reader support test completed');
    }

    /**
     * Test reduced motion support
     */
    testReducedMotion() {
        console.log('🎬 Testing reduced motion support...');
        
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const hasReducedMotionCSS = this.checkForReducedMotionCSS();
        
        if (!hasReducedMotionCSS) {
            this.addViolation({
                type: 'reduced-motion',
                message: 'No @media (prefers-reduced-motion: reduce) CSS rules found'
            });
            this.testResults.warnings++;
        } else {
            this.testResults.passed++;
            console.log('✅ Reduced motion support found');
        }
    }

    /**
     * Test high contrast support
     */
    testHighContrast() {
        console.log('🎨 Testing high contrast support...');
        
        const highContrastToggle = document.getElementById('high-contrast-toggle');
        if (highContrastToggle) {
            this.testResults.passed++;
            console.log('✅ High contrast toggle found');
        } else {
            this.addViolation({
                type: 'high-contrast',
                message: 'No high contrast mode toggle found'
            });
            this.testResults.warnings++;
        }
    }

    /**
     * Setup continuous monitoring
     */
    setupContinuousMonitoring() {
        // Monitor for dynamic content changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            this.testNewElement(node);
                        }
                    });
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    /**
     * Test newly added elements
     */
    testNewElement(element) {
        // Quick accessibility check for new elements
        if (element.matches('img') && !element.hasAttribute('alt')) {
            console.warn('⚠️ New image added without alt text:', element);
        }
        
        if (element.matches('button, a') && !element.textContent.trim() && 
            !element.hasAttribute('aria-label')) {
            console.warn('⚠️ New interactive element added without accessible name:', element);
        }
    }

    /**
     * Generate accessibility report
     */
    generateAccessibilityReport() {
        const report = {
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent,
            summary: {
                passed: this.testResults.passed,
                failed: this.testResults.failed,
                warnings: this.testResults.warnings,
                total: this.testResults.passed + this.testResults.failed + this.testResults.warnings
            },
            violations: this.testResults.violations,
            wcagLevel: 'AA',
            complianceScore: this.calculateComplianceScore()
        };
        
        console.log('📊 Accessibility Report:', report);
        
        // Store report for debugging
        window.accessibilityReport = report;
        
        // Display summary
        this.displayReportSummary(report);
        
        return report;
    }

    /**
     * Display report summary
     */
    displayReportSummary(report) {
        const summary = `
🔍 Accessibility Test Results:
✅ Passed: ${report.summary.passed}
❌ Failed: ${report.summary.failed}
⚠️ Warnings: ${report.summary.warnings}
📊 Compliance Score: ${report.complianceScore}%

${report.summary.failed > 0 ? '❌ Critical issues found - review console for details' : '✅ No critical accessibility issues found'}
        `;
        
        console.log(summary);
        
        // Show on-screen notification if enabled
        if (window.location.search.includes('debug') || window.location.search.includes('accessibility')) {
            this.showAccessibilityNotification(report);
        }
    }

    /**
     * Show accessibility notification
     */
    showAccessibilityNotification(report) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: ${report.summary.failed > 0 ? '#d63384' : '#198754'};
            color: white;
            padding: 16px;
            border-radius: 8px;
            z-index: 10000;
            max-width: 300px;
            font-family: monospace;
            font-size: 12px;
            line-height: 1.4;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        `;
        
        notification.innerHTML = `
            <strong>Accessibility Report</strong><br>
            ✅ ${report.summary.passed} passed<br>
            ❌ ${report.summary.failed} failed<br>
            ⚠️ ${report.summary.warnings} warnings<br>
            Score: ${report.complianceScore}%
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 10000);
    }

    /**
     * Utility methods
     */
    addViolation(violation) {
        this.testResults.violations.push(violation);
        console.warn('⚠️ Accessibility issue:', violation);
    }

    getElementSelector(element) {
        if (element.id) return `#${element.id}`;
        if (element.className) return `.${element.className.split(' ')[0]}`;
        return element.tagName.toLowerCase();
    }

    getImplicitRole(element) {
        const tagName = element.tagName.toLowerCase();
        const roleMap = {
            'a': 'link',
            'button': 'button',
            'input': 'textbox',
            'textarea': 'textbox',
            'select': 'combobox',
            'nav': 'navigation',
            'main': 'main',
            'header': 'banner',
            'footer': 'contentinfo'
        };
        return roleMap[tagName] || null;
    }

    calculateContrastRatio(foreground, background) {
        // Simplified contrast calculation
        // In production, use a proper color contrast library
        try {
            const fg = this.parseColor(foreground);
            const bg = this.parseColor(background);
            
            if (!fg || !bg) return 0;
            
            const l1 = this.getLuminance(fg);
            const l2 = this.getLuminance(bg);
            
            return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
        } catch (error) {
            return 0;
        }
    }

    parseColor(color) {
        // Very basic color parsing - use proper color library in production
        if (color === 'transparent') return null;
        if (color.startsWith('rgb')) {
            const matches = color.match(/\d+/g);
            if (matches && matches.length >= 3) {
                return {
                    r: parseInt(matches[0]) / 255,
                    g: parseInt(matches[1]) / 255,
                    b: parseInt(matches[2]) / 255
                };
            }
        }
        return null;
    }

    getLuminance(color) {
        const { r, g, b } = color;
        const [rs, gs, bs] = [r, g, b].map(c => {
            return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
    }

    checkForReducedMotionCSS() {
        // Check if any stylesheets contain reduced motion media queries
        for (let stylesheet of document.styleSheets) {
            try {
                for (let rule of stylesheet.cssRules || []) {
                    if (rule.media && rule.media.mediaText.includes('prefers-reduced-motion')) {
                        return true;
                    }
                }
            } catch (e) {
                // Cross-origin stylesheet
                continue;
            }
        }
        return false;
    }

    calculateComplianceScore() {
        const total = this.testResults.passed + this.testResults.failed;
        if (total === 0) return 0;
        return Math.round((this.testResults.passed / total) * 100);
    }
}

// Initialize accessibility tester
const accessibilityTester = new AccessibilityTester();

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AccessibilityTester;
}

// Make available globally for debugging
window.AccessibilityTester = AccessibilityTester;
window.accessibilityTester = accessibilityTester;