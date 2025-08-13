#!/usr/bin/env node

/**
 * Comprehensive Build Script
 * 
 * Orchestrates all build processes with performance monitoring:
 * 1. Clean previous builds
 * 2. Optimize assets (images, fonts, SVG)
 * 3. Build CSS with PostCSS
 * 4. Build JavaScript with webpack
 * 5. Extract critical CSS
 * 6. Generate HTML templates
 * 7. Monitor performance metrics
 * 
 * Usage:
 *   node build-scripts/build-all.js [--dev|--prod] [--analyze] [--skip-assets]
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync, spawn } from 'child_process';
import { buildConfig } from '../build.config.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

// Build configuration
const config = {
  mode: process.argv.includes('--prod') ? 'production' : 
        process.argv.includes('--dev') ? 'development' : 'production',
  analyze: process.argv.includes('--analyze'),
  skipAssets: process.argv.includes('--skip-assets'),
  parallel: !process.argv.includes('--serial'),
  verbose: process.argv.includes('--verbose')
};

// Logger utilities
const logger = {
  info: (msg) => console.log(`\x1b[36m[Build]\x1b[0m ${msg}`),
  success: (msg) => console.log(`\x1b[32m[Build]\x1b[0m ${msg}`),
  error: (msg) => console.error(`\x1b[31m[Build]\x1b[0m ${msg}`),
  warn: (msg) => console.warn(`\x1b[33m[Build]\x1b[0m ${msg}`),
  step: (step, total, msg) => console.log(`\x1b[35m[Build ${step}/${total}]\x1b[0m ${msg}`)
};

/**
 * Execute command with performance monitoring
 */
async function executeCommand(command, name, options = {}) {
  const startTime = Date.now();
  
  try {
    logger.info(`Starting: ${name}`);
    
    const result = execSync(command, {
      cwd: projectRoot,
      stdio: config.verbose ? 'inherit' : 'pipe',
      encoding: 'utf8',
      ...options
    });
    
    const duration = Date.now() - startTime;
    logger.success(`✅ ${name} completed in ${(duration / 1000).toFixed(2)}s`);
    
    return {
      success: true,
      duration,
      output: result
    };
    
  } catch (error) {
    const duration = Date.now() - startTime;
    logger.error(`❌ ${name} failed after ${(duration / 1000).toFixed(2)}s`);
    
    if (config.verbose) {
      logger.error(error.message);
    }
    
    return {
      success: false,
      duration,
      error: error.message
    };
  }
}

/**
 * Execute commands in parallel
 */
async function executeParallel(commands) {
  const promises = commands.map(({ command, name, options }) => 
    executeCommand(command, name, options)
  );
  
  return Promise.all(promises);
}

/**
 * Clean previous builds
 */
async function cleanBuild() {
  logger.step(1, 7, 'Cleaning previous builds...');
  
  return executeCommand(
    'npm run clean:dist',
    'Clean Build Directories'
  );
}

/**
 * Optimize assets
 */
async function optimizeAssets() {
  if (config.skipAssets) {
    logger.step(2, 7, 'Skipping asset optimization...');
    return { success: true, duration: 0 };
  }
  
  logger.step(2, 7, 'Optimizing assets...');
  
  if (config.parallel) {
    // Run asset optimization tasks in parallel
    const assetCommands = [
      {
        command: 'node build-scripts/optimize-assets.js --type=images',
        name: 'Image Optimization'
      },
      {
        command: 'node build-scripts/optimize-assets.js --type=fonts',
        name: 'Font Processing'
      },
      {
        command: 'node build-scripts/optimize-assets.js --type=svg',
        name: 'SVG Optimization'
      }
    ];
    
    const results = await executeParallel(assetCommands);
    const allSuccessful = results.every(result => result.success);
    const totalDuration = Math.max(...results.map(result => result.duration));
    
    return {
      success: allSuccessful,
      duration: totalDuration,
      details: results
    };
  } else {
    return executeCommand(
      'node build-scripts/optimize-assets.js',
      'Asset Optimization'
    );
  }
}

/**
 * Build CSS
 */
async function buildCSS() {
  logger.step(3, 7, 'Building CSS...');
  
  const cssCommand = config.mode === 'production' ? 
    'npm run build:css:prod' : 
    'npm run build:css';
    
  return executeCommand(cssCommand, 'CSS Build');
}

/**
 * Build JavaScript
 */
async function buildJavaScript() {
  logger.step(4, 7, 'Building JavaScript...');
  
  let jsCommand = config.mode === 'production' ? 
    'npm run build:js' : 
    'npm run build:js:dev';
    
  if (config.analyze) {
    jsCommand = 'npm run build:js:analyze';
  }
  
  return executeCommand(jsCommand, 'JavaScript Build');
}

/**
 * Extract critical CSS
 */
async function extractCriticalCSS() {
  logger.step(5, 7, 'Extracting critical CSS...');
  
  // Only extract critical CSS in production mode
  if (config.mode !== 'production') {
    logger.info('Skipping critical CSS extraction in development mode');
    return { success: true, duration: 0 };
  }
  
  return executeCommand(
    'node build-scripts/critical-css.js',
    'Critical CSS Extraction'
  );
}

/**
 * Generate HTML templates
 */
async function generateHTML() {
  logger.step(6, 7, 'Generating HTML templates...');
  
  // Check if HTML optimization script exists
  const htmlScriptPath = path.join(projectRoot, 'scripts/optimize-html.js');
  
  try {
    await fs.access(htmlScriptPath);
    return executeCommand('npm run build:html', 'HTML Template Generation');
  } catch (error) {
    logger.warn('HTML optimization script not found, skipping...');
    return { success: true, duration: 0 };
  }
}

/**
 * Monitor performance
 */
async function monitorPerformance() {
  logger.step(7, 7, 'Monitoring build performance...');
  
  return executeCommand(
    'node build-scripts/build-performance-monitor.js',
    'Performance Monitoring'
  );
}

/**
 * Generate build summary
 */
function generateBuildSummary(results) {
  const totalDuration = results.reduce((sum, result) => sum + (result?.duration || 0), 0);
  const successCount = results.filter(result => result?.success).length;
  const failureCount = results.length - successCount;
  
  logger.info('\n📊 Build Summary:');
  logger.info(`   Total time: ${(totalDuration / 1000).toFixed(2)}s`);
  logger.info(`   Successful steps: ${successCount}/${results.length}`);
  
  if (failureCount > 0) {
    logger.error(`   Failed steps: ${failureCount}`);
  }
  
  // Check performance targets
  const buildTimeTarget = buildConfig.performance.buildTime.max;
  if (totalDuration > buildTimeTarget) {
    logger.warn(`   ⚠️  Build time (${(totalDuration / 1000).toFixed(2)}s) exceeds target (${(buildTimeTarget / 1000).toFixed(2)}s)`);
  } else {
    logger.success(`   ✅ Build time within target (${(buildTimeTarget / 1000).toFixed(2)}s)`);
  }
  
  // Log detailed results
  if (config.verbose) {
    logger.info('\n📋 Detailed Results:');
    results.forEach((result, index) => {
      const stepNames = [
        'Clean Build',
        'Asset Optimization', 
        'CSS Build',
        'JavaScript Build',
        'Critical CSS',
        'HTML Generation',
        'Performance Monitor'
      ];
      
      const stepName = stepNames[index] || `Step ${index + 1}`;
      const status = result?.success ? '✅' : '❌';
      const duration = result?.duration ? `${(result.duration / 1000).toFixed(2)}s` : '0s';
      
      logger.info(`   ${status} ${stepName}: ${duration}`);
    });
  }
}

/**
 * Main build execution
 */
async function main() {
  const overallStartTime = Date.now();
  
  try {
    logger.info(`🚀 Starting ${config.mode} build...`);
    logger.info(`   Mode: ${config.mode}`);
    logger.info(`   Analyze: ${config.analyze}`);
    logger.info(`   Skip assets: ${config.skipAssets}`);
    logger.info(`   Parallel: ${config.parallel}`);
    
    const results = [];
    
    // Execute build steps sequentially
    results.push(await cleanBuild());
    results.push(await optimizeAssets());
    results.push(await buildCSS());
    results.push(await buildJavaScript());
    results.push(await extractCriticalCSS());
    results.push(await generateHTML());
    results.push(await monitorPerformance());
    
    // Check if any critical steps failed
    const criticalSteps = [0, 2, 3]; // Clean, CSS, JS are critical
    const criticalFailures = criticalSteps.filter(stepIndex => 
      !results[stepIndex]?.success
    );
    
    if (criticalFailures.length > 0) {
      logger.error(`❌ Critical build steps failed: ${criticalFailures.length}`);
      generateBuildSummary(results);
      process.exit(1);
    }
    
    const overallDuration = Date.now() - overallStartTime;
    logger.success(`🎉 Build completed successfully in ${(overallDuration / 1000).toFixed(2)}s`);
    
    generateBuildSummary(results);
    
    // Generate bundle analysis if requested
    if (config.analyze) {
      logger.info('\n📈 Opening bundle analyzer...');
      try {
        spawn('npm', ['run', 'analyze:bundle'], {
          cwd: projectRoot,
          stdio: 'inherit',
          detached: true
        });
      } catch (error) {
        logger.warn('Could not open bundle analyzer automatically');
      }
    }
    
  } catch (error) {
    const overallDuration = Date.now() - overallStartTime;
    logger.error(`💥 Build failed after ${(overallDuration / 1000).toFixed(2)}s: ${error.message}`);
    process.exit(1);
  }
}

// Handle command line help
if (process.argv.includes('--help')) {
  console.log(`
Comprehensive Build Script

Usage:
  node build-scripts/build-all.js [options]

Options:
  --dev              Development build mode
  --prod             Production build mode (default)
  --analyze          Enable bundle analysis
  --skip-assets      Skip asset optimization
  --serial           Run tasks serially (not in parallel)
  --verbose          Verbose logging
  --help             Show this help message

Examples:
  node build-scripts/build-all.js
  node build-scripts/build-all.js --dev --verbose
  node build-scripts/build-all.js --prod --analyze
  node build-scripts/build-all.js --skip-assets --serial
  `);
  process.exit(0);
}

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error(`Unhandled rejection at: ${promise}, reason: ${reason}`);
  process.exit(1);
});

// Handle SIGINT gracefully
process.on('SIGINT', () => {
  logger.warn('\n⚠️  Build interrupted by user');
  process.exit(130);
});

// Execute main function
main();