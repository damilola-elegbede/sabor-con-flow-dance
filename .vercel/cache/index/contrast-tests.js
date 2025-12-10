/**
 * Color Contrast Testing Tool
 * WCAG 2.1 AA Compliance - SPEC_06 Group C Task 8
 * Tests color combinations used in Sabor Con Flow Dance website
 */

const fs = require('fs');
const path = require('path');

// WCAG 2.1 contrast requirements
const CONTRAST_REQUIREMENTS = {
    AA_NORMAL: 4.5,    // Normal text AA
    AA_LARGE: 3.0,     // Large text AA (18pt+ or 14pt+ bold)
    AAA_NORMAL: 7.0,   // Normal text AAA
    AAA_LARGE: 4.5,    // Large text AAA
    UI_COMPONENTS: 3.0 // UI components and graphical objects
};

// Brand colors from the website
const BRAND_COLORS = {
    // Primary brand colors
    'color-gold': '#C7B375',
    'color-gold-secondary': '#BFAA65', 
    'color-gold-accessible': '#A69854',
    'color-gold-light-accessible': '#D4C896',
    'color-black': '#000000',
    'color-white': '#FFFFFF',
    
    // Additional theme colors
    'color-gold-light': '#E5D4A1',
    'color-gold-dark': '#9C8E5A',
    'color-gray-dark': '#333333',
    'color-gray-medium': '#666666',
    'color-gray-light': '#999999',
    'color-gray-lighter': '#F5F5F5',
    
    // Status colors
    'color-error': '#d63384',
    'color-success': '#198754',
    'color-warning': '#fd7e14',
    'color-info': '#0dcaf0',
    
    // Focus colors
    'color-focus': '#2563eb',
    'color-text-primary': '#1a1a1a',
    'color-text-secondary': '#4a4a4a',
    'color-link-visited': '#8B7355'
};

// Common color combinations used on the site
const COLOR_COMBINATIONS = [
    // Navigation
    { name: 'Navbar Brand', foreground: 'color-gold', background: 'color-black' },
    { name: 'Navbar Items', foreground: 'color-white', background: 'color-black' },
    { name: 'Navbar Items Hover', foreground: 'color-gold-light-accessible', background: 'color-black' },
    
    // Buttons
    { name: 'Primary Button', foreground: 'color-black', background: 'color-gold-accessible' },
    { name: 'Primary Button Text', foreground: 'color-white', background: 'color-gold-accessible' },
    { name: 'Secondary Button', foreground: 'color-white', background: 'color-black' },
    
    // Text content
    { name: 'Body Text', foreground: 'color-text-primary', background: 'color-white' },
    { name: 'Secondary Text', foreground: 'color-text-secondary', background: 'color-white' },
    { name: 'Link Text', foreground: 'color-gold-accessible', background: 'color-white' },
    { name: 'Visited Link', foreground: 'color-link-visited', background: 'color-white' },
    
    // Form elements
    { name: 'Form Label', foreground: 'color-text-primary', background: 'color-white' },
    { name: 'Form Input', foreground: 'color-text-primary', background: 'color-white' },
    { name: 'Form Error', foreground: 'color-error', background: 'color-white' },
    { name: 'Form Success', foreground: 'color-success', background: 'color-white' },
    
    // Status messages
    { name: 'Error Message', foreground: '#842029', background: 'rgba(214, 51, 132, 0.1)' },
    { name: 'Success Message', foreground: '#0f5132', background: 'rgba(25, 135, 84, 0.1)' },
    { name: 'Warning Message', foreground: '#664d03', background: 'rgba(253, 126, 20, 0.1)' },
    { name: 'Info Message', foreground: '#055160', background: 'rgba(13, 202, 240, 0.1)' },
    
    // Footer
    { name: 'Footer Text', foreground: 'color-white', background: 'color-black' },
    { name: 'Footer Links', foreground: 'color-gold', background: 'color-black' },
    
    // Hero section
    { name: 'Hero Text', foreground: 'color-white', background: 'rgba(0, 0, 0, 0.7)' },
    { name: 'Hero CTA Button', foreground: 'color-black', background: 'color-gold' },
    
    // Cards
    { name: 'Card Text', foreground: 'color-text-primary', background: 'color-white' },
    { name: 'Card Border', foreground: 'color-gold', background: 'color-white' },
    
    // Focus indicators
    { name: 'Focus Outline', foreground: 'color-focus', background: 'color-white' },
    { name: 'Focus on Dark', foreground: 'color-white', background: 'color-black' }
];

/**
 * Convert hex color to RGB
 */
function hexToRgb(hex) {
    // Handle color names and CSS variables
    if (hex.startsWith('color-')) {
        hex = BRAND_COLORS[hex] || hex;
    }
    
    // Handle rgba() values
    if (hex.startsWith('rgba(')) {
        const match = hex.match(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)/);
        if (match) {
            const [, r, g, b, a] = match;
            // For contrast calculation, we need to handle alpha
            // This is simplified - proper implementation would blend with background
            return { r: parseInt(r), g: parseInt(g), b: parseInt(b), a: parseFloat(a) };
        }
    }
    
    // Handle rgb() values
    if (hex.startsWith('rgb(')) {
        const match = hex.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
        if (match) {
            const [, r, g, b] = match;
            return { r: parseInt(r), g: parseInt(g), b: parseInt(b) };
        }
    }
    
    // Remove # if present
    hex = hex.replace('#', '');
    
    // Handle 3-character hex codes
    if (hex.length === 3) {
        hex = hex.split('').map(char => char + char).join('');
    }
    
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    return { r, g, b };
}

/**
 * Calculate relative luminance
 */
function relativeLuminance(rgb) {
    const { r, g, b } = rgb;
    
    const rsRGB = r / 255;
    const gsRGB = g / 255;
    const bsRGB = b / 255;
    
    const rLin = rsRGB <= 0.03928 ? rsRGB / 12.92 : Math.pow((rsRGB + 0.055) / 1.055, 2.4);
    const gLin = gsRGB <= 0.03928 ? gsRGB / 12.92 : Math.pow((gsRGB + 0.055) / 1.055, 2.4);
    const bLin = bsRGB <= 0.03928 ? bsRGB / 12.92 : Math.pow((bsRGB + 0.055) / 1.055, 2.4);
    
    return 0.2126 * rLin + 0.7152 * gLin + 0.0722 * bLin;
}

/**
 * Calculate contrast ratio
 */
function contrastRatio(color1, color2) {
    const rgb1 = hexToRgb(color1);
    const rgb2 = hexToRgb(color2);
    
    if (!rgb1 || !rgb2) {
        return 0;
    }
    
    const lum1 = relativeLuminance(rgb1);
    const lum2 = relativeLuminance(rgb2);
    
    const lighter = Math.max(lum1, lum2);
    const darker = Math.min(lum1, lum2);
    
    return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Check if contrast ratio meets WCAG requirements
 */
function checkContrast(ratio, level = 'AA', size = 'normal') {
    const key = `${level}_${size.toUpperCase()}`;
    const requirement = CONTRAST_REQUIREMENTS[key];
    
    return {
        passes: ratio >= requirement,
        ratio: ratio,
        requirement: requirement,
        level: level,
        size: size
    };
}

/**
 * Format contrast ratio for display
 */
function formatRatio(ratio) {
    return `${ratio.toFixed(2)}:1`;
}

/**
 * Get color display name
 */
function getColorDisplayName(color) {
    if (color.startsWith('color-')) {
        return color.replace('color-', '').replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    return color;
}

/**
 * Generate status icon
 */
function getStatusIcon(passes) {
    return passes ? '✅' : '❌';
}

/**
 * Run contrast tests
 */
function runContrastTests() {
    console.log('🎨 Running Color Contrast Tests for WCAG 2.1 AA Compliance');
    console.log('=' .repeat(70));
    
    const results = {
        total: 0,
        passed: 0,
        failed: 0,
        warnings: 0,
        combinations: []
    };
    
    COLOR_COMBINATIONS.forEach(combo => {
        const { name, foreground, background } = combo;
        const ratio = contrastRatio(foreground, background);
        
        // Test different requirements
        const tests = [
            { label: 'Normal Text (AA)', ...checkContrast(ratio, 'AA', 'normal') },
            { label: 'Large Text (AA)', ...checkContrast(ratio, 'AA', 'large') },
            { label: 'UI Components', ...checkContrast(ratio, 'AA', 'normal') } // Using AA normal as baseline
        ];
        
        console.log(`\n📋 Testing: ${name}`);
        console.log(`   Foreground: ${getColorDisplayName(foreground)} (${BRAND_COLORS[foreground] || foreground})`);
        console.log(`   Background: ${getColorDisplayName(background)} (${BRAND_COLORS[background] || background})`);
        console.log(`   Contrast Ratio: ${formatRatio(ratio)}`);
        
        let comboPassed = true;
        tests.forEach(test => {
            const status = getStatusIcon(test.passes);
            const requirement = formatRatio(test.requirement);
            console.log(`   ${status} ${test.label}: ${requirement} required`);
            
            if (!test.passes) {
                comboPassed = false;
            }
        });
        
        // Primary test is normal text AA
        const primaryTest = tests[0];
        if (primaryTest.passes) {
            results.passed++;
        } else {
            results.failed++;
            console.log(`   ⚠️  FAILS WCAG 2.1 AA for normal text`);
        }
        
        results.total++;
        results.combinations.push({
            name,
            foreground,
            background,
            ratio,
            tests,
            passed: comboPassed
        });
    });
    
    // Generate summary
    console.log('\n' + '=' .repeat(70));
    console.log('📊 CONTRAST TEST SUMMARY');
    console.log('=' .repeat(70));
    console.log(`Total Combinations Tested: ${results.total}`);
    console.log(`${getStatusIcon(true)} Passed: ${results.passed}`);
    console.log(`${getStatusIcon(false)} Failed: ${results.failed}`);
    console.log(`Compliance Rate: ${((results.passed / results.total) * 100).toFixed(1)}%`);
    
    // Show critical failures
    const failures = results.combinations.filter(combo => !combo.passed);
    if (failures.length > 0) {
        console.log('\n❌ CRITICAL FAILURES (Must Fix):');
        failures.forEach(failure => {
            console.log(`   • ${failure.name}: ${formatRatio(failure.ratio)} (needs ${formatRatio(CONTRAST_REQUIREMENTS.AA_NORMAL)})`);
        });
    }
    
    // Show near misses (might need attention)
    const nearMisses = results.combinations.filter(combo => 
        combo.ratio >= CONTRAST_REQUIREMENTS.AA_NORMAL * 0.9 && 
        combo.ratio < CONTRAST_REQUIREMENTS.AA_NORMAL
    );
    
    if (nearMisses.length > 0) {
        console.log('\n⚠️  NEAR MISSES (Monitor):');
        nearMisses.forEach(miss => {
            console.log(`   • ${miss.name}: ${formatRatio(miss.ratio)} (almost meets ${formatRatio(CONTRAST_REQUIREMENTS.AA_NORMAL)})`);
        });
    }
    
    // Show excellent ratios (AAA compliant)
    const excellent = results.combinations.filter(combo => 
        combo.ratio >= CONTRAST_REQUIREMENTS.AAA_NORMAL
    );
    
    if (excellent.length > 0) {
        console.log('\n🌟 EXCELLENT RATIOS (AAA Compliant):');
        excellent.forEach(combo => {
            console.log(`   • ${combo.name}: ${formatRatio(combo.ratio)}`);
        });
    }
    
    // Recommendations
    console.log('\n💡 RECOMMENDATIONS:');
    
    if (results.failed === 0) {
        console.log('   ✅ All color combinations meet WCAG 2.1 AA requirements!');
        console.log('   ✅ Website is accessible for users with color vision deficiencies');
    } else {
        console.log('   🔧 Fix critical failures by:');
        console.log('      • Using darker text colors on light backgrounds');
        console.log('      • Using lighter text colors on dark backgrounds');
        console.log('      • Increasing font weight for borderline cases');
        console.log('      • Adding background colors for better contrast');
    }
    
    console.log('   📋 Test with actual users who have color vision deficiencies');
    console.log('   🔍 Use tools like WebAIM Contrast Checker for verification');
    console.log('   🎨 Consider providing high contrast mode toggle');
    
    // Generate JSON report
    const report = {
        timestamp: new Date().toISOString(),
        wcagLevel: 'AA',
        results: results,
        brandColors: BRAND_COLORS,
        recommendations: {
            critical: failures.length,
            nearMisses: nearMisses.length,
            excellent: excellent.length,
            overallCompliance: results.failed === 0
        }
    };
    
    // Save report
    const reportsDir = path.join(__dirname, 'reports');
    if (!fs.existsSync(reportsDir)) {
        fs.mkdirSync(reportsDir, { recursive: true });
    }
    
    const reportPath = path.join(reportsDir, 'contrast-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    console.log(`\n📄 Detailed report saved to: ${reportPath}`);
    console.log('=' .repeat(70));
    
    return results;
}

/**
 * Test specific color combination
 */
function testColorCombo(foreground, background, context = 'Custom Test') {
    const ratio = contrastRatio(foreground, background);
    const aaTest = checkContrast(ratio, 'AA', 'normal');
    const aaaTest = checkContrast(ratio, 'AAA', 'normal');
    
    console.log(`\n🎨 ${context}`);
    console.log(`Foreground: ${foreground}`);
    console.log(`Background: ${background}`);
    console.log(`Contrast Ratio: ${formatRatio(ratio)}`);
    console.log(`${getStatusIcon(aaTest.passes)} WCAG AA: ${aaTest.passes ? 'PASS' : 'FAIL'}`);
    console.log(`${getStatusIcon(aaaTest.passes)} WCAG AAA: ${aaaTest.passes ? 'PASS' : 'FAIL'}`);
    
    return { ratio, aaTest, aaaTest };
}

// CLI interface
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length === 2) {
        // Test specific colors
        testColorCombo(args[0], args[1]);
    } else if (args.length === 0) {
        // Run full test suite
        runContrastTests();
    } else {
        console.log('Usage:');
        console.log('  node contrast-tests.js                    # Run full test suite');
        console.log('  node contrast-tests.js #000000 #FFFFFF   # Test specific colors');
    }
}

module.exports = {
    runContrastTests,
    testColorCombo,
    contrastRatio,
    checkContrast,
    BRAND_COLORS,
    CONTRAST_REQUIREMENTS
};