#!/usr/bin/env node

/**
 * Build Performance Monitor
 *
 * Comprehensive build performance tracking and reporting:
 * - Build time monitoring with targets
 * - Bundle size analysis and alerts
 * - Asset optimization metrics
 * - Performance regression detection
 * - CI/CD integration ready
 *
 * Usage:
 *   node build-scripts/build-performance-monitor.js [--baseline] [--report]
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';
import { globby } from 'globby';
import { gzipSync } from 'zlib';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

// Performance targets from PRD
const performanceTargets = {
  buildTime: 30000, // 30 seconds max
  devServerStart: 5000, // 5 seconds max
  hotReload: 1000, // 1 second max
  bundleSize: {
    css: 50 * 1024, // 50KB gzipped
    js: 150 * 1024, // 150KB gzipped
    total: 200 * 1024, // 200KB gzipped total
  },
  assetOptimization: {
    compressionRatio: 0.3, // 30% minimum compression
    maxImageSize: 500 * 1024, // 500KB max per image
  },
};

// Configuration
const config = {
  metricsFile: path.join(projectRoot, 'build-metrics.json'),
  reportDir: path.join(projectRoot, 'reports'),
  staticDir: path.join(projectRoot, 'staticfiles'),
  distDir: path.join(projectRoot, 'static'),
};

// Logger utilities
const logger = {
  info: msg => console.log(`\x1b[36m[Performance Monitor]\x1b[0m ${msg}`),
  success: msg => console.log(`\x1b[32m[Performance Monitor]\x1b[0m ${msg}`),
  error: msg => console.error(`\x1b[31m[Performance Monitor]\x1b[0m ${msg}`),
  warn: msg => console.warn(`\x1b[33m[Performance Monitor]\x1b[0m ${msg}`),
};

/**
 * Measure execution time of a function
 */
async function measureTime(name, fn) {
  const startTime = process.hrtime.bigint();
  try {
    const result = await fn();
    const endTime = process.hrtime.bigint();
    const duration = Number(endTime - startTime) / 1000000; // Convert to milliseconds

    return {
      name,
      duration,
      success: true,
      result,
    };
  } catch (error) {
    const endTime = process.hrtime.bigint();
    const duration = Number(endTime - startTime) / 1000000;

    return {
      name,
      duration,
      success: false,
      error: error.message,
    };
  }
}

/**
 * Get file size with gzip compression
 */
async function getGzippedSize(filePath) {
  try {
    const content = await fs.readFile(filePath);
    const gzipped = gzipSync(content);
    return {
      original: content.length,
      gzipped: gzipped.length,
      compression: 1 - gzipped.length / content.length,
    };
  } catch (error) {
    return { original: 0, gzipped: 0, compression: 0 };
  }
}

/**
 * Analyze bundle sizes
 */
async function analyzeBundleSizes() {
  const bundleAnalysis = {
    js: { files: [], totalOriginal: 0, totalGzipped: 0 },
    css: { files: [], totalOriginal: 0, totalGzipped: 0 },
    assets: { files: [], totalOriginal: 0, totalGzipped: 0 },
  };

  // Analyze JavaScript bundles
  const jsFiles = await globby(['**/*.js'], { cwd: path.join(config.staticDir, 'js') });
  for (const jsFile of jsFiles) {
    const filePath = path.join(config.staticDir, 'js', jsFile);
    const sizeInfo = await getGzippedSize(filePath);

    bundleAnalysis.js.files.push({
      name: jsFile,
      ...sizeInfo,
    });

    bundleAnalysis.js.totalOriginal += sizeInfo.original;
    bundleAnalysis.js.totalGzipped += sizeInfo.gzipped;
  }

  // Analyze CSS bundles
  const cssFiles = await globby(['**/*.css'], { cwd: path.join(config.staticDir, 'css') });
  for (const cssFile of cssFiles) {
    const filePath = path.join(config.staticDir, 'css', cssFile);
    const sizeInfo = await getGzippedSize(filePath);

    bundleAnalysis.css.files.push({
      name: cssFile,
      ...sizeInfo,
    });

    bundleAnalysis.css.totalOriginal += sizeInfo.original;
    bundleAnalysis.css.totalGzipped += sizeInfo.gzipped;
  }

  // Analyze static assets
  const assetFiles = await globby(['**/*.{png,jpg,jpeg,webp,avif,svg,woff,woff2}'], {
    cwd: config.staticDir,
  });

  for (const assetFile of assetFiles.slice(0, 20)) {
    // Limit to first 20 for performance
    const filePath = path.join(config.staticDir, assetFile);
    const sizeInfo = await getGzippedSize(filePath);

    bundleAnalysis.assets.files.push({
      name: assetFile,
      ...sizeInfo,
    });

    bundleAnalysis.assets.totalOriginal += sizeInfo.original;
    bundleAnalysis.assets.totalGzipped += sizeInfo.gzipped;
  }

  return bundleAnalysis;
}

/**
 * Check bundle size performance against targets
 */
function checkBundlePerformance(bundleAnalysis) {
  const issues = [];
  const warnings = [];

  // Check JavaScript bundle size
  if (bundleAnalysis.js.totalGzipped > performanceTargets.bundleSize.js) {
    issues.push({
      type: 'bundle_size',
      severity: 'error',
      message: `JavaScript bundle size (${(bundleAnalysis.js.totalGzipped / 1024).toFixed(2)}KB) exceeds target (${(performanceTargets.bundleSize.js / 1024).toFixed(2)}KB)`,
      actual: bundleAnalysis.js.totalGzipped,
      target: performanceTargets.bundleSize.js,
    });
  }

  // Check CSS bundle size
  if (bundleAnalysis.css.totalGzipped > performanceTargets.bundleSize.css) {
    issues.push({
      type: 'bundle_size',
      severity: 'error',
      message: `CSS bundle size (${(bundleAnalysis.css.totalGzipped / 1024).toFixed(2)}KB) exceeds target (${(performanceTargets.bundleSize.css / 1024).toFixed(2)}KB)`,
      actual: bundleAnalysis.css.totalGzipped,
      target: performanceTargets.bundleSize.css,
    });
  }

  // Check total bundle size
  const totalBundleSize = bundleAnalysis.js.totalGzipped + bundleAnalysis.css.totalGzipped;
  if (totalBundleSize > performanceTargets.bundleSize.total) {
    issues.push({
      type: 'bundle_size',
      severity: 'error',
      message: `Total bundle size (${(totalBundleSize / 1024).toFixed(2)}KB) exceeds target (${(performanceTargets.bundleSize.total / 1024).toFixed(2)}KB)`,
      actual: totalBundleSize,
      target: performanceTargets.bundleSize.total,
    });
  }

  // Check individual large assets
  bundleAnalysis.assets.files.forEach(asset => {
    if (asset.original > performanceTargets.assetOptimization.maxImageSize) {
      warnings.push({
        type: 'asset_size',
        severity: 'warning',
        message: `Large asset: ${asset.name} (${(asset.original / 1024).toFixed(2)}KB)`,
        actual: asset.original,
        target: performanceTargets.assetOptimization.maxImageSize,
      });
    }
  });

  // Check compression ratios
  const jsCompression = 1 - bundleAnalysis.js.totalGzipped / bundleAnalysis.js.totalOriginal;
  const cssCompression = 1 - bundleAnalysis.css.totalGzipped / bundleAnalysis.css.totalOriginal;

  if (jsCompression < performanceTargets.assetOptimization.compressionRatio) {
    warnings.push({
      type: 'compression',
      severity: 'warning',
      message: `JavaScript compression ratio (${(jsCompression * 100).toFixed(1)}%) below target (${(performanceTargets.assetOptimization.compressionRatio * 100).toFixed(1)}%)`,
      actual: jsCompression,
      target: performanceTargets.assetOptimization.compressionRatio,
    });
  }

  if (cssCompression < performanceTargets.assetOptimization.compressionRatio) {
    warnings.push({
      type: 'compression',
      severity: 'warning',
      message: `CSS compression ratio (${(cssCompression * 100).toFixed(1)}%) below target (${(performanceTargets.assetOptimization.compressionRatio * 100).toFixed(1)}%)`,
      actual: cssCompression,
      target: performanceTargets.assetOptimization.compressionRatio,
    });
  }

  return { issues, warnings };
}

/**
 * Measure build times
 */
async function measureBuildTimes() {
  const buildTimes = {};

  // Measure CSS build time
  buildTimes.css = await measureTime('CSS Build', async () => {
    execSync('npm run build:css:prod', {
      cwd: projectRoot,
      stdio: 'pipe',
    });
  });

  // Measure JavaScript build time
  buildTimes.js = await measureTime('JavaScript Build', async () => {
    execSync('npm run build:js', {
      cwd: projectRoot,
      stdio: 'pipe',
    });
  });

  // Measure asset optimization time
  buildTimes.assets = await measureTime('Asset Optimization', async () => {
    execSync('node build-scripts/optimize-assets.js', {
      cwd: projectRoot,
      stdio: 'pipe',
    });
  });

  // Calculate total build time
  const totalBuildTime = Object.values(buildTimes)
    .filter(time => time.success)
    .reduce((sum, time) => sum + time.duration, 0);

  buildTimes.total = {
    name: 'Total Build',
    duration: totalBuildTime,
    success: true,
  };

  return buildTimes;
}

/**
 * Check build time performance
 */
function checkBuildTimePerformance(buildTimes) {
  const issues = [];

  if (buildTimes.total.duration > performanceTargets.buildTime) {
    issues.push({
      type: 'build_time',
      severity: 'error',
      message: `Total build time (${(buildTimes.total.duration / 1000).toFixed(2)}s) exceeds target (${(performanceTargets.buildTime / 1000).toFixed(2)}s)`,
      actual: buildTimes.total.duration,
      target: performanceTargets.buildTime,
    });
  }

  // Check individual build steps
  Object.entries(buildTimes).forEach(([step, timing]) => {
    if (step !== 'total' && timing.duration > 10000) {
      // 10 second threshold for individual steps
      issues.push({
        type: 'build_time',
        severity: 'warning',
        message: `${timing.name} is slow (${(timing.duration / 1000).toFixed(2)}s)`,
        actual: timing.duration,
        target: 10000,
      });
    }
  });

  return { issues };
}

/**
 * Load previous metrics for comparison
 */
async function loadPreviousMetrics() {
  try {
    const metricsContent = await fs.readFile(config.metricsFile, 'utf8');
    return JSON.parse(metricsContent);
  } catch (error) {
    return null;
  }
}

/**
 * Save current metrics
 */
async function saveCurrentMetrics(metrics) {
  await fs.writeFile(config.metricsFile, JSON.stringify(metrics, null, 2));
}

/**
 * Compare metrics with previous build
 */
function compareMetrics(current, previous) {
  if (!previous) {
    return { regressions: [], improvements: [] };
  }

  const regressions = [];
  const improvements = [];

  // Compare build times
  if (current.buildTimes.total.duration > previous.buildTimes.total.duration * 1.1) {
    regressions.push({
      type: 'build_time_regression',
      message: `Build time increased from ${(previous.buildTimes.total.duration / 1000).toFixed(2)}s to ${(current.buildTimes.total.duration / 1000).toFixed(2)}s`,
      previousValue: previous.buildTimes.total.duration,
      currentValue: current.buildTimes.total.duration,
    });
  } else if (current.buildTimes.total.duration < previous.buildTimes.total.duration * 0.9) {
    improvements.push({
      type: 'build_time_improvement',
      message: `Build time improved from ${(previous.buildTimes.total.duration / 1000).toFixed(2)}s to ${(current.buildTimes.total.duration / 1000).toFixed(2)}s`,
      previousValue: previous.buildTimes.total.duration,
      currentValue: current.buildTimes.total.duration,
    });
  }

  // Compare bundle sizes
  const currentTotalSize =
    current.bundleAnalysis.js.totalGzipped + current.bundleAnalysis.css.totalGzipped;
  const previousTotalSize =
    previous.bundleAnalysis.js.totalGzipped + previous.bundleAnalysis.css.totalGzipped;

  if (currentTotalSize > previousTotalSize * 1.05) {
    regressions.push({
      type: 'bundle_size_regression',
      message: `Bundle size increased from ${(previousTotalSize / 1024).toFixed(2)}KB to ${(currentTotalSize / 1024).toFixed(2)}KB`,
      previousValue: previousTotalSize,
      currentValue: currentTotalSize,
    });
  } else if (currentTotalSize < previousTotalSize * 0.95) {
    improvements.push({
      type: 'bundle_size_improvement',
      message: `Bundle size improved from ${(previousTotalSize / 1024).toFixed(2)}KB to ${(currentTotalSize / 1024).toFixed(2)}KB`,
      previousValue: previousTotalSize,
      currentValue: currentTotalSize,
    });
  }

  return { regressions, improvements };
}

/**
 * Generate performance report
 */
async function generatePerformanceReport(metrics, comparison) {
  const reportPath = path.join(config.reportDir, `performance-report-${Date.now()}.json`);

  const report = {
    timestamp: new Date().toISOString(),
    buildTimes: metrics.buildTimes,
    bundleAnalysis: metrics.bundleAnalysis,
    performanceChecks: metrics.performanceChecks,
    comparison,
    summary: {
      buildTimeWithinTarget: metrics.buildTimes.total.duration <= performanceTargets.buildTime,
      bundleSizeWithinTarget:
        metrics.bundleAnalysis.js.totalGzipped + metrics.bundleAnalysis.css.totalGzipped <=
        performanceTargets.bundleSize.total,
      totalIssues:
        metrics.performanceChecks.bundleSize.issues.length +
        metrics.performanceChecks.buildTime.issues.length,
      totalWarnings: metrics.performanceChecks.bundleSize.warnings.length,
      regressions: comparison.regressions.length,
      improvements: comparison.improvements.length,
    },
  };

  // Ensure report directory exists
  await fs.mkdir(config.reportDir, { recursive: true });
  await fs.writeFile(reportPath, JSON.stringify(report, null, 2));

  return { report, reportPath };
}

/**
 * Generate HTML report
 */
async function generateHTMLReport(report, reportPath) {
  const htmlReportPath = reportPath.replace('.json', '.html');

  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Build Performance Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px; }
        .header { border-bottom: 2px solid #e1e5e9; padding-bottom: 20px; margin-bottom: 30px; }
        .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { border: 1px solid #e1e5e9; border-radius: 8px; padding: 20px; }
        .metric-title { font-weight: 600; font-size: 18px; margin-bottom: 10px; }
        .metric-value { font-size: 24px; font-weight: 700; margin-bottom: 5px; }
        .metric-target { color: #666; font-size: 14px; }
        .status-pass { color: #28a745; }
        .status-fail { color: #dc3545; }
        .status-warn { color: #ffc107; }
        .issues { margin-top: 30px; }
        .issue { padding: 10px; margin-bottom: 10px; border-radius: 4px; }
        .issue-error { background-color: #f8d7da; border-left: 4px solid #dc3545; }
        .issue-warning { background-color: #fff3cd; border-left: 4px solid #ffc107; }
        .issue-improvement { background-color: #d4edda; border-left: 4px solid #28a745; }
        .timestamp { color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Build Performance Report</h1>
        <div class="timestamp">Generated: ${report.timestamp}</div>
    </div>
    
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-title">Total Build Time</div>
            <div class="metric-value ${report.summary.buildTimeWithinTarget ? 'status-pass' : 'status-fail'}">
                ${(report.buildTimes.total.duration / 1000).toFixed(2)}s
            </div>
            <div class="metric-target">Target: ${(performanceTargets.buildTime / 1000).toFixed(2)}s</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-title">Bundle Size (Gzipped)</div>
            <div class="metric-value ${report.summary.bundleSizeWithinTarget ? 'status-pass' : 'status-fail'}">
                ${((report.bundleAnalysis.js.totalGzipped + report.bundleAnalysis.css.totalGzipped) / 1024).toFixed(2)}KB
            </div>
            <div class="metric-target">Target: ${(performanceTargets.bundleSize.total / 1024).toFixed(2)}KB</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-title">JavaScript Bundle</div>
            <div class="metric-value ${report.bundleAnalysis.js.totalGzipped <= performanceTargets.bundleSize.js ? 'status-pass' : 'status-fail'}">
                ${(report.bundleAnalysis.js.totalGzipped / 1024).toFixed(2)}KB
            </div>
            <div class="metric-target">Target: ${(performanceTargets.bundleSize.js / 1024).toFixed(2)}KB</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-title">CSS Bundle</div>
            <div class="metric-value ${report.bundleAnalysis.css.totalGzipped <= performanceTargets.bundleSize.css ? 'status-pass' : 'status-fail'}">
                ${(report.bundleAnalysis.css.totalGzipped / 1024).toFixed(2)}KB
            </div>
            <div class="metric-target">Target: ${(performanceTargets.bundleSize.css / 1024).toFixed(2)}KB</div>
        </div>
    </div>
    
    ${
      report.summary.totalIssues > 0
        ? `
    <div class="issues">
        <h2>Performance Issues</h2>
        ${report.performanceChecks.bundleSize.issues
          .map(
            issue => `
            <div class="issue issue-error">
                <strong>${issue.type}:</strong> ${issue.message}
            </div>
        `
          )
          .join('')}
        ${report.performanceChecks.buildTime.issues
          .map(
            issue => `
            <div class="issue issue-error">
                <strong>${issue.type}:</strong> ${issue.message}
            </div>
        `
          )
          .join('')}
    </div>
    `
        : ''
    }
    
    ${
      report.summary.totalWarnings > 0
        ? `
    <div class="issues">
        <h2>Performance Warnings</h2>
        ${report.performanceChecks.bundleSize.warnings
          .map(
            warning => `
            <div class="issue issue-warning">
                <strong>${warning.type}:</strong> ${warning.message}
            </div>
        `
          )
          .join('')}
    </div>
    `
        : ''
    }
    
    ${
      report.comparison.regressions.length > 0
        ? `
    <div class="issues">
        <h2>Performance Regressions</h2>
        ${report.comparison.regressions
          .map(
            regression => `
            <div class="issue issue-error">
                <strong>${regression.type}:</strong> ${regression.message}
            </div>
        `
          )
          .join('')}
    </div>
    `
        : ''
    }
    
    ${
      report.comparison.improvements.length > 0
        ? `
    <div class="issues">
        <h2>Performance Improvements</h2>
        ${report.comparison.improvements
          .map(
            improvement => `
            <div class="issue issue-improvement">
                <strong>${improvement.type}:</strong> ${improvement.message}
            </div>
        `
          )
          .join('')}
    </div>
    `
        : ''
    }
</body>
</html>`;

  await fs.writeFile(htmlReportPath, html);
  return htmlReportPath;
}

/**
 * Main execution function
 */
async function main() {
  const startTime = Date.now();
  const _isBaseline = process.argv.includes('--baseline');
  const generateReport = process.argv.includes('--report');

  try {
    logger.info('Starting build performance monitoring...');

    // Load previous metrics for comparison
    const previousMetrics = await loadPreviousMetrics();

    // Measure build times
    logger.info('Measuring build times...');
    const buildTimes = await measureBuildTimes();

    // Analyze bundle sizes
    logger.info('Analyzing bundle sizes...');
    const bundleAnalysis = await analyzeBundleSizes();

    // Check performance against targets
    const bundleSizeChecks = checkBundlePerformance(bundleAnalysis);
    const buildTimeChecks = checkBuildTimePerformance(buildTimes);

    // Compile current metrics
    const currentMetrics = {
      timestamp: new Date().toISOString(),
      buildTimes,
      bundleAnalysis,
      performanceChecks: {
        bundleSize: bundleSizeChecks,
        buildTime: buildTimeChecks,
      },
    };

    // Compare with previous metrics
    const comparison = compareMetrics(currentMetrics, previousMetrics);

    // Save current metrics (unless this is just a report)
    if (!generateReport) {
      await saveCurrentMetrics(currentMetrics);
    }

    // Generate reports if requested or if there are issues
    const hasIssues =
      bundleSizeChecks.issues.length > 0 ||
      buildTimeChecks.issues.length > 0 ||
      comparison.regressions.length > 0;

    if (generateReport || hasIssues) {
      const { report, reportPath } = await generatePerformanceReport(currentMetrics, comparison);
      const htmlReportPath = await generateHTMLReport(report, reportPath);

      logger.success(`Performance report generated:`);
      logger.info(`  JSON: ${reportPath}`);
      logger.info(`  HTML: ${htmlReportPath}`);
    }

    // Log results
    const totalDuration = Date.now() - startTime;
    logger.success(`Performance monitoring completed in ${(totalDuration / 1000).toFixed(2)}s`);

    // Log build times
    logger.info('Build Times:');
    Object.entries(buildTimes).forEach(([_step, timing]) => {
      const status = timing.success ? '✅' : '❌';
      const duration = (timing.duration / 1000).toFixed(2);
      logger.info(`  ${status} ${timing.name}: ${duration}s`);
    });

    // Log bundle sizes
    logger.info('Bundle Sizes (Gzipped):');
    logger.info(`  JS: ${(bundleAnalysis.js.totalGzipped / 1024).toFixed(2)}KB`);
    logger.info(`  CSS: ${(bundleAnalysis.css.totalGzipped / 1024).toFixed(2)}KB`);
    logger.info(
      `  Total: ${((bundleAnalysis.js.totalGzipped + bundleAnalysis.css.totalGzipped) / 1024).toFixed(2)}KB`
    );

    // Log performance issues
    const totalIssues = bundleSizeChecks.issues.length + buildTimeChecks.issues.length;
    const totalWarnings = bundleSizeChecks.warnings.length;

    if (totalIssues > 0) {
      logger.error(`❌ ${totalIssues} performance issues found`);
      [...bundleSizeChecks.issues, ...buildTimeChecks.issues].forEach(issue => {
        logger.error(`  ${issue.message}`);
      });
    }

    if (totalWarnings > 0) {
      logger.warn(`⚠️  ${totalWarnings} performance warnings`);
      bundleSizeChecks.warnings.forEach(warning => {
        logger.warn(`  ${warning.message}`);
      });
    }

    if (comparison.regressions.length > 0) {
      logger.error(`📈 ${comparison.regressions.length} performance regressions detected`);
      comparison.regressions.forEach(regression => {
        logger.error(`  ${regression.message}`);
      });
    }

    if (comparison.improvements.length > 0) {
      logger.success(`📉 ${comparison.improvements.length} performance improvements`);
      comparison.improvements.forEach(improvement => {
        logger.success(`  ${improvement.message}`);
      });
    }

    if (totalIssues === 0 && totalWarnings === 0 && comparison.regressions.length === 0) {
      logger.success('✅ All performance targets met!');
    }

    // Exit with error code if there are critical issues
    if (totalIssues > 0 || comparison.regressions.length > 0) {
      process.exit(1);
    }
  } catch (error) {
    logger.error(`Performance monitoring failed: ${error.message}`);
    process.exit(1);
  }
}

// Handle command line arguments
if (process.argv.includes('--help')) {
  console.log(`
Build Performance Monitor

Usage:
  node build-scripts/build-performance-monitor.js [options]

Options:
  --baseline         Set current metrics as baseline (don't compare)
  --report           Generate report without running builds
  --help             Show this help message

Examples:
  node build-scripts/build-performance-monitor.js
  node build-scripts/build-performance-monitor.js --baseline
  node build-scripts/build-performance-monitor.js --report
  `);
  process.exit(0);
}

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error(`Unhandled rejection at: ${promise}, reason: ${reason}`);
  process.exit(1);
});

// Execute main function
main();
