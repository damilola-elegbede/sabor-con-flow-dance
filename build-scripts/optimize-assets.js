#!/usr/bin/env node

/**
 * Asset Optimization Script
 * 
 * Comprehensive asset optimization pipeline:
 * - Image compression and format conversion
 * - Font subsetting and optimization
 * - SVG optimization
 * - Asset fingerprinting and cache busting
 * 
 * Usage:
 *   node build-scripts/optimize-assets.js [--type=images|fonts|svg|all]
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import sharp from 'sharp';
import { globby } from 'globby';
import { createHash } from 'crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

// Configuration
const config = {
  input: {
    images: path.join(projectRoot, 'static/images'),
    fonts: path.join(projectRoot, 'static/fonts'),
    svg: path.join(projectRoot, 'static/images/svg')
  },
  output: {
    images: path.join(projectRoot, 'staticfiles/images/optimized'),
    fonts: path.join(projectRoot, 'staticfiles/fonts'),
    svg: path.join(projectRoot, 'staticfiles/images/svg')
  },
  imageOptimization: {
    jpeg: {
      quality: 85,
      progressive: true,
      mozjpeg: true
    },
    png: {
      quality: 90,
      compressionLevel: 8,
      adaptiveFiltering: true
    },
    webp: {
      quality: 85,
      effort: 6
    },
    avif: {
      quality: 80,
      effort: 4
    }
  },
  responsive: {
    breakpoints: [320, 480, 768, 1024, 1280, 1920],
    formats: ['webp', 'avif', 'jpeg']
  },
  performance: {
    concurrency: 4, // Parallel processing limit
    maxImageSize: 2 * 1024 * 1024, // 2MB max input size
    targetCompressionRatio: 0.7 // Target 70% size reduction
  }
};

// Logger utilities
const logger = {
  info: (msg) => console.log(`\x1b[36m[Asset Optimizer]\x1b[0m ${msg}`),
  success: (msg) => console.log(`\x1b[32m[Asset Optimizer]\x1b[0m ${msg}`),
  error: (msg) => console.error(`\x1b[31m[Asset Optimizer]\x1b[0m ${msg}`),
  warn: (msg) => console.warn(`\x1b[33m[Asset Optimizer]\x1b[0m ${msg}`)
};

/**
 * Generate file hash for cache busting
 */
function generateFileHash(content) {
  return createHash('md5').update(content).digest('hex').substring(0, 8);
}

/**
 * Ensure output directories exist
 */
async function ensureOutputDirs() {
  for (const dir of Object.values(config.output)) {
    await fs.mkdir(dir, { recursive: true });
  }
}

/**
 * Optimize single image with multiple formats and sizes
 */
async function optimizeImage(inputPath, outputDir) {
  try {
    const inputBuffer = await fs.readFile(inputPath);
    const inputSize = inputBuffer.length;
    
    if (inputSize > config.performance.maxImageSize) {
      logger.warn(`Skipping large image: ${path.basename(inputPath)} (${(inputSize / 1024 / 1024).toFixed(2)}MB)`);
      return { skipped: true, reason: 'too_large', inputSize };
    }
    
    const baseName = path.basename(inputPath, path.extname(inputPath));
    const image = sharp(inputBuffer);
    const metadata = await image.metadata();
    
    const results = [];
    
    // Generate responsive images
    for (const width of config.responsive.breakpoints) {
      if (width >= metadata.width) continue; // Skip larger breakpoints
      
      for (const format of config.responsive.formats) {
        const outputName = `${baseName}_${width}w.${format}`;
        const outputPath = path.join(outputDir, outputName);
        
        let processor = image.clone().resize(width, null, {
          withoutEnlargement: true,
          fastShrinkOnLoad: true
        });
        
        // Apply format-specific optimizations
        switch (format) {
          case 'webp':
            processor = processor.webp(config.imageOptimization.webp);
            break;
          case 'avif':
            processor = processor.avif(config.imageOptimization.avif);
            break;
          case 'jpeg':
            processor = processor.jpeg(config.imageOptimization.jpeg);
            break;
          case 'png':
            processor = processor.png(config.imageOptimization.png);
            break;
        }
        
        const outputBuffer = await processor.toBuffer();
        const hash = generateFileHash(outputBuffer);
        const hashedName = `${baseName}_${width}w.${hash}.${format}`;
        const hashedPath = path.join(outputDir, hashedName);
        
        await fs.writeFile(hashedPath, outputBuffer);
        
        results.push({
          width,
          format,
          originalSize: inputSize,
          optimizedSize: outputBuffer.length,
          compressionRatio: (1 - outputBuffer.length / inputSize),
          filename: hashedName,
          path: hashedPath
        });
      }
    }
    
    // Generate original size optimized versions
    for (const format of config.responsive.formats) {
      const outputName = `${baseName}.${format}`;
      const outputPath = path.join(outputDir, outputName);
      
      let processor = image.clone();
      
      switch (format) {
        case 'webp':
          processor = processor.webp(config.imageOptimization.webp);
          break;
        case 'avif':
          processor = processor.avif(config.imageOptimization.avif);
          break;
        case 'jpeg':
          processor = processor.jpeg(config.imageOptimization.jpeg);
          break;
        case 'png':
          processor = processor.png(config.imageOptimization.png);
          break;
      }
      
      const outputBuffer = await processor.toBuffer();
      const hash = generateFileHash(outputBuffer);
      const hashedName = `${baseName}.${hash}.${format}`;
      const hashedPath = path.join(outputDir, hashedName);
      
      await fs.writeFile(hashedPath, outputBuffer);
      
      results.push({
        width: metadata.width,
        format,
        originalSize: inputSize,
        optimizedSize: outputBuffer.length,
        compressionRatio: (1 - outputBuffer.length / inputSize),
        filename: hashedName,
        path: hashedPath
      });
    }
    
    return {
      inputPath,
      inputSize,
      results,
      totalOptimizedSize: results.reduce((sum, r) => sum + r.optimizedSize, 0)
    };
    
  } catch (error) {
    logger.error(`Failed to optimize ${inputPath}: ${error.message}`);
    return { error: error.message, inputPath };
  }
}

/**
 * Optimize all images
 */
async function optimizeImages() {
  logger.info('Optimizing images...');
  
  const imageExtensions = ['jpg', 'jpeg', 'png', 'webp', 'avif'];
  const imagePatterns = imageExtensions.map(ext => 
    path.join(config.input.images, '**', `*.${ext}`)
  );
  
  const imagePaths = await globby(imagePatterns);
  
  if (imagePaths.length === 0) {
    logger.warn('No images found to optimize');
    return { processed: 0, totalSaved: 0 };
  }
  
  logger.info(`Found ${imagePaths.length} images to optimize`);
  
  // Process images in batches to control memory usage
  const batches = [];
  for (let i = 0; i < imagePaths.length; i += config.performance.concurrency) {
    batches.push(imagePaths.slice(i, i + config.performance.concurrency));
  }
  
  let totalOriginalSize = 0;
  let totalOptimizedSize = 0;
  let processedCount = 0;
  let skippedCount = 0;
  let errorCount = 0;
  
  for (const batch of batches) {
    const batchPromises = batch.map(imagePath => 
      optimizeImage(imagePath, config.output.images)
    );
    
    const batchResults = await Promise.all(batchPromises);
    
    for (const result of batchResults) {
      if (result.error) {
        errorCount++;
        continue;
      }
      
      if (result.skipped) {
        skippedCount++;
        continue;
      }
      
      processedCount++;
      totalOriginalSize += result.inputSize;
      totalOptimizedSize += result.totalOptimizedSize;
      
      const compressionRatio = (1 - result.totalOptimizedSize / result.inputSize);
      logger.info(`Optimized: ${path.basename(result.inputPath)} -> ${result.results.length} variants (${(compressionRatio * 100).toFixed(1)}% reduction)`);
    }
  }
  
  const totalSaved = totalOriginalSize - totalOptimizedSize;
  const overallCompressionRatio = totalOriginalSize > 0 ? (totalSaved / totalOriginalSize) : 0;
  
  logger.success(`Image optimization complete:`);
  logger.info(`  Processed: ${processedCount} images`);
  logger.info(`  Skipped: ${skippedCount} images`);
  logger.info(`  Errors: ${errorCount} images`);
  logger.info(`  Original size: ${(totalOriginalSize / 1024 / 1024).toFixed(2)}MB`);
  logger.info(`  Optimized size: ${(totalOptimizedSize / 1024 / 1024).toFixed(2)}MB`);
  logger.info(`  Space saved: ${(totalSaved / 1024 / 1024).toFixed(2)}MB (${(overallCompressionRatio * 100).toFixed(1)}%)`);
  
  return {
    processed: processedCount,
    skipped: skippedCount,
    errors: errorCount,
    totalSaved,
    compressionRatio: overallCompressionRatio
  };
}

/**
 * Generate responsive image manifest
 */
async function generateImageManifest() {
  const manifestPath = path.join(config.output.images, 'manifest.json');
  const imagePatterns = ['**/*.webp', '**/*.avif', '**/*.jpg', '**/*.jpeg', '**/*.png'];
  
  const imagePaths = await globby(imagePatterns, {
    cwd: config.output.images
  });
  
  const manifest = {};
  
  for (const imagePath of imagePaths) {
    const filename = path.basename(imagePath);
    const match = filename.match(/^(.+?)(?:_(\\d+)w)?(?:\\.[a-f0-9]{8})?\\.(.+)$/);
    
    if (match) {
      const [, baseName, width, format] = match;
      const key = baseName;
      
      if (!manifest[key]) {
        manifest[key] = {
          formats: {},
          responsive: {}
        };
      }
      
      if (width) {
        if (!manifest[key].responsive[width]) {
          manifest[key].responsive[width] = {};
        }
        manifest[key].responsive[width][format] = imagePath;
      } else {
        manifest[key].formats[format] = imagePath;
      }
    }
  }
  
  await fs.writeFile(manifestPath, JSON.stringify(manifest, null, 2));
  logger.success(`Image manifest generated: ${manifestPath}`);
  
  return manifest;
}

/**
 * Optimize SVG files
 */
async function optimizeSVGs() {
  logger.info('Optimizing SVGs...');
  
  const svgPaths = await globby([
    path.join(config.input.svg, '**/*.svg')
  ]);
  
  if (svgPaths.length === 0) {
    logger.warn('No SVG files found to optimize');
    return { processed: 0 };
  }
  
  let processedCount = 0;
  let totalOriginalSize = 0;
  let totalOptimizedSize = 0;
  
  for (const svgPath of svgPaths) {
    try {
      const svgContent = await fs.readFile(svgPath, 'utf8');
      const originalSize = Buffer.byteLength(svgContent, 'utf8');
      
      // Basic SVG optimization (remove comments, unnecessary whitespace)
      let optimizedSVG = svgContent
        .replace(/<!--[\\s\\S]*?-->/g, '') // Remove comments
        .replace(/\\s+/g, ' ') // Normalize whitespace
        .replace(/> </g, '><') // Remove spaces between tags
        .trim();
      
      const optimizedSize = Buffer.byteLength(optimizedSVG, 'utf8');
      const hash = generateFileHash(Buffer.from(optimizedSVG, 'utf8'));
      
      const baseName = path.basename(svgPath, '.svg');
      const outputName = `${baseName}.${hash}.svg`;
      const outputPath = path.join(config.output.svg, outputName);
      
      await fs.writeFile(outputPath, optimizedSVG);
      
      processedCount++;
      totalOriginalSize += originalSize;
      totalOptimizedSize += optimizedSize;
      
      const compressionRatio = (1 - optimizedSize / originalSize);
      logger.info(`Optimized SVG: ${baseName}.svg (${(compressionRatio * 100).toFixed(1)}% reduction)`);
      
    } catch (error) {
      logger.error(`Failed to optimize SVG ${svgPath}: ${error.message}`);
    }
  }
  
  const totalSaved = totalOriginalSize - totalOptimizedSize;
  const overallCompressionRatio = totalOriginalSize > 0 ? (totalSaved / totalOriginalSize) : 0;
  
  logger.success(`SVG optimization complete:`);
  logger.info(`  Processed: ${processedCount} files`);
  logger.info(`  Space saved: ${(totalSaved / 1024).toFixed(2)}KB (${(overallCompressionRatio * 100).toFixed(1)}%)`);
  
  return {
    processed: processedCount,
    totalSaved,
    compressionRatio: overallCompressionRatio
  };
}

/**
 * Copy and optimize fonts
 */
async function optimizeFonts() {
  logger.info('Processing fonts...');
  
  const fontPaths = await globby([
    path.join(config.input.fonts, '**/*.{woff,woff2,ttf,otf}')
  ]);
  
  if (fontPaths.length === 0) {
    logger.warn('No font files found to process');
    return { processed: 0 };
  }
  
  let processedCount = 0;
  
  for (const fontPath of fontPaths) {
    try {
      const fontBuffer = await fs.readFile(fontPath);
      const hash = generateFileHash(fontBuffer);
      
      const ext = path.extname(fontPath);
      const baseName = path.basename(fontPath, ext);
      const outputName = `${baseName}.${hash}${ext}`;
      const outputPath = path.join(config.output.fonts, outputName);
      
      await fs.writeFile(outputPath, fontBuffer);
      
      processedCount++;
      logger.info(`Processed font: ${baseName}${ext}`);
      
    } catch (error) {
      logger.error(`Failed to process font ${fontPath}: ${error.message}`);
    }
  }
  
  logger.success(`Font processing complete: ${processedCount} files processed`);
  
  return { processed: processedCount };
}

/**
 * Generate asset manifest for cache busting
 */
async function generateAssetManifest() {
  const manifestPath = path.join(projectRoot, 'staticfiles/asset-manifest.json');
  const manifest = {};
  
  // Collect all optimized assets
  const assetPatterns = [
    path.join(config.output.images, '**/*'),
    path.join(config.output.fonts, '**/*'),
    path.join(config.output.svg, '**/*')
  ];
  
  const assetPaths = await globby(assetPatterns);
  
  for (const assetPath of assetPaths) {
    const relativePath = path.relative(path.join(projectRoot, 'staticfiles'), assetPath);
    const filename = path.basename(assetPath);
    
    // Extract original name from hashed filename
    const match = filename.match(/^(.+?)(?:\\.[a-f0-9]{8})?(\\..+)$/);
    if (match) {
      const [, baseName, ext] = match;
      const originalName = baseName + ext;
      manifest[originalName] = relativePath;
    }
  }
  
  await fs.writeFile(manifestPath, JSON.stringify(manifest, null, 2));
  logger.success(`Asset manifest generated: ${manifestPath}`);
  
  return manifest;
}

/**
 * Main execution function
 */
async function main() {
  const startTime = Date.now();
  const optimizationType = process.argv.find(arg => arg.startsWith('--type='))?.split('=')[1] || 'all';
  
  try {
    logger.info(`Starting asset optimization (type: ${optimizationType})...`);
    
    // Ensure output directories exist
    await ensureOutputDirs();
    
    const results = {};
    
    // Run optimization based on type
    if (optimizationType === 'all' || optimizationType === 'images') {
      results.images = await optimizeImages();
      await generateImageManifest();
    }
    
    if (optimizationType === 'all' || optimizationType === 'svg') {
      results.svg = await optimizeSVGs();
    }
    
    if (optimizationType === 'all' || optimizationType === 'fonts') {
      results.fonts = await optimizeFonts();
    }
    
    // Generate overall asset manifest
    await generateAssetManifest();
    
    // Performance summary
    const duration = Date.now() - startTime;
    logger.success(`Asset optimization completed in ${(duration / 1000).toFixed(2)}s`);
    
    // Log optimization results
    let totalSaved = 0;
    Object.entries(results).forEach(([type, result]) => {
      if (result.totalSaved) {
        totalSaved += result.totalSaved;
        logger.info(`${type}: ${result.processed} files, ${(result.totalSaved / 1024 / 1024).toFixed(2)}MB saved`);
      } else {
        logger.info(`${type}: ${result.processed} files processed`);
      }
    });
    
    if (totalSaved > 0) {
      logger.success(`Total space saved: ${(totalSaved / 1024 / 1024).toFixed(2)}MB`);
    }
    
  } catch (error) {
    logger.error(`Asset optimization failed: ${error.message}`);
    process.exit(1);
  }
}

// Handle command line arguments
if (process.argv.includes('--help')) {
  console.log(`
Asset Optimization Tool

Usage:
  node build-scripts/optimize-assets.js [options]

Options:
  --type=TYPE        Optimization type: images, fonts, svg, or all (default: all)
  --help             Show this help message

Examples:
  node build-scripts/optimize-assets.js
  node build-scripts/optimize-assets.js --type=images
  node build-scripts/optimize-assets.js --type=fonts
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