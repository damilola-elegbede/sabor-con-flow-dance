#!/usr/bin/env node

/**
 * CSS Build Script - Sabor con Flow Dance Studio
 *
 * PostCSS-based build system with:
 * - Autoprefixer for cross-browser compatibility
 * - cssnano for production minification
 * - File watching for development
 * - Source maps for debugging
 * - Environment-specific optimizations
 *
 * Usage:
 *   node build-scripts/build-css.js [--watch] [--env=production]
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import chokidar from 'chokidar';
import postcss from 'postcss';
import autoprefixer from 'autoprefixer';
import cssnano from 'cssnano';
import postcssImport from 'postcss-import';
import postcssPresetEnv from 'postcss-preset-env';

// ES module compatibility
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

// Configuration
const config = {
  input: {
    main: path.join(projectRoot, 'src/css/styles.css'),
    fallback: path.join(projectRoot, 'static/css/styles.css'),
  },
  output: {
    dev: path.join(projectRoot, 'staticfiles/css/styles.css'),
    prod: path.join(projectRoot, 'staticfiles/css/styles.min.css'),
  },
  watchPaths: [
    path.join(projectRoot, 'src/css/**/*.css'),
    path.join(projectRoot, 'static/css/**/*.css'),
  ],
};

// Environment detection
const isProduction =
  process.argv.includes('--env=production') || process.env.NODE_ENV === 'production';
const isWatching = process.argv.includes('--watch');

// Console logging utilities
const logger = {
  info: msg => console.log(`\x1b[36m[CSS]\x1b[0m ${msg}`),
  success: msg => console.log(`\x1b[32m[CSS]\x1b[0m ${msg}`),
  error: msg => console.error(`\x1b[31m[CSS]\x1b[0m ${msg}`),
  warn: msg => console.warn(`\x1b[33m[CSS]\x1b[0m ${msg}`),
};

/**
 * PostCSS plugin configuration
 */
function getPostCSSPlugins(isProd = false) {
  const plugins = [
    postcssImport({
      path: [path.join(projectRoot, 'src/css'), path.join(projectRoot, 'static/css')],
    }),
    postcssPresetEnv({
      stage: 1,
      features: {
        'custom-properties': false, // Preserve CSS custom properties
        'nesting-rules': true,
      },
    }),
    autoprefixer({
      overrideBrowserslist: ['> 1%', 'last 2 versions', 'not dead', 'not ie 11'],
    }),
  ];

  if (isProd) {
    plugins.push(
      cssnano({
        preset: [
          'default',
          {
            discardComments: { removeAll: true },
            reduceIdents: false,
            zindex: false,
            autoprefixer: false, // Already applied above
            minifyFontValues: true,
            minifyParams: true,
            minifySelectors: true,
            normalizeCharset: true,
            normalizeDisplayValues: true,
            normalizePositions: true,
            normalizeRepeatStyle: true,
            normalizeString: true,
            normalizeTimingFunctions: true,
            normalizeUnicode: true,
            normalizeUrl: true,
            normalizeWhitespace: true,
            orderedValues: true,
            reduceInitial: true,
            reduceTransforms: true,
            svgo: true,
            uniqueSelectors: true,
          },
        ],
      })
    );
  }

  return plugins;
}

/**
 * Ensure output directory exists
 */
async function ensureOutputDir() {
  try {
    const outputDir = path.dirname(config.output.dev);
    await fs.mkdir(outputDir, { recursive: true });
    return true;
  } catch (error) {
    logger.error(`Failed to create output directory: ${error.message}`);
    return false;
  }
}

/**
 * Read CSS input file with fallback
 */
async function readCSSInput() {
  try {
    // Try main input first
    try {
      const css = await fs.readFile(config.input.main, 'utf8');
      logger.info(`Reading CSS from: ${path.relative(projectRoot, config.input.main)}`);
      return css;
    } catch (mainError) {
      // Fallback to static CSS
      logger.warn(
        `Main CSS not found, using fallback: ${path.relative(projectRoot, config.input.fallback)}`
      );
      const css = await fs.readFile(config.input.fallback, 'utf8');
      return css;
    }
  } catch (error) {
    throw new Error(`Could not read CSS input: ${error.message}`);
  }
}

/**
 * Process CSS with PostCSS
 */
async function processCSS(css, options = {}) {
  const { isProd = false, generateSourceMap = !isProd } = options;

  try {
    const plugins = getPostCSSPlugins(isProd);
    const processor = postcss(plugins);

    const result = await processor.process(css, {
      from: config.input.main,
      to: isProd ? config.output.prod : config.output.dev,
      map: generateSourceMap ? { inline: false } : false,
    });

    // Handle warnings
    result.warnings().forEach(warn => {
      logger.warn(warn.toString());
    });

    return result;
  } catch (error) {
    throw new Error(`PostCSS processing failed: ${error.message}`);
  }
}

/**
 * Write processed CSS to output
 */
async function writeCSSOutput(result, isProd = false) {
  try {
    const outputPath = isProd ? config.output.prod : config.output.dev;

    // Write CSS
    await fs.writeFile(outputPath, result.css);

    // Write source map if generated
    if (result.map) {
      const mapPath = `${outputPath}.map`;
      await fs.writeFile(mapPath, result.map.toString());
      logger.info(`Source map: ${path.relative(projectRoot, mapPath)}`);
    }

    // Log file size
    const stats = await fs.stat(outputPath);
    const sizeKB = (stats.size / 1024).toFixed(2);

    logger.success(`Built CSS: ${path.relative(projectRoot, outputPath)} (${sizeKB}KB)`);

    return true;
  } catch (error) {
    logger.error(`Failed to write CSS output: ${error.message}`);
    return false;
  }
}

/**
 * Main build function
 */
async function buildCSS() {
  const startTime = Date.now();

  try {
    logger.info(`Building CSS... (${isProduction ? 'production' : 'development'})`);

    // Ensure output directory exists
    if (!(await ensureOutputDir())) {
      process.exit(1);
    }

    // Read input CSS
    const css = await readCSSInput();

    // Process CSS
    const result = await processCSS(css, {
      isProd: isProduction,
      generateSourceMap: !isProduction,
    });

    // Write output
    if (!(await writeCSSOutput(result, isProduction))) {
      process.exit(1);
    }

    const duration = Date.now() - startTime;
    logger.success(`Build completed in ${duration}ms`);
  } catch (error) {
    logger.error(`Build failed: ${error.message}`);
    process.exit(1);
  }
}

/**
 * Watch for file changes
 */
function startWatching() {
  logger.info('Starting file watcher...');

  const watcher = chokidar.watch(config.watchPaths, {
    ignored: /node_modules/,
    persistent: true,
    ignoreInitial: true,
  });

  let debounceTimer;

  const rebuild = () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
      logger.info('File changed, rebuilding...');
      await buildCSS();
    }, 100);
  };

  watcher
    .on('change', filePath => {
      logger.info(`Changed: ${path.relative(projectRoot, filePath)}`);
      rebuild();
    })
    .on('add', filePath => {
      logger.info(`Added: ${path.relative(projectRoot, filePath)}`);
      rebuild();
    })
    .on('unlink', filePath => {
      logger.info(`Removed: ${path.relative(projectRoot, filePath)}`);
      rebuild();
    })
    .on('error', error => {
      logger.error(`Watcher error: ${error.message}`);
    });

  logger.info('Watching CSS files for changes...');
  logger.info('Press Ctrl+C to stop watching');

  // Handle graceful shutdown
  process.on('SIGINT', () => {
    logger.info('Stopping file watcher...');
    watcher.close();
    process.exit(0);
  });
}

/**
 * Main execution
 */
async function main() {
  try {
    // Initial build
    await buildCSS();

    // Start watching if requested
    if (isWatching) {
      startWatching();
    }
  } catch (error) {
    logger.error(`Fatal error: ${error.message}`);
    process.exit(1);
  }
}

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error(`Unhandled rejection at: ${promise}, reason: ${reason}`);
  process.exit(1);
});

// Execute main function
main();
