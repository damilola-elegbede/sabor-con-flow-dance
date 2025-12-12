#!/usr/bin/env node
/**
 * Image Optimization Script for Sabor Con Flow
 * Converts JPEG/PNG to WebP with multiple responsive sizes
 *
 * Usage: npm run optimize:images
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
    description: 'Gallery - Technical Precision',
  },
  {
    input: 'dance-3.jpeg',
    output: 'dance-3',
    maxWidth: 1280,
    quality: 80,
    description: 'Gallery - Music Integration',
  },
  {
    input: 'dance-4.jpeg',
    output: 'dance-4',
    maxWidth: 1280,
    quality: 80,
    description: 'Gallery - Cuban Training',
  },
  {
    input: 'sabor-con-flow-logo.png',
    output: 'logo',
    maxWidth: 500,
    quality: 90,
    preserveAlpha: true,
    description: 'Header logo',
  },
  {
    input: 'sabor-con-flow-logo-2.png',
    output: 'logo-2',
    maxWidth: 500,
    quality: 90,
    preserveAlpha: true,
    description: 'Favicon/logo variations',
  },
];

// Track statistics
const stats = {
  originalTotal: 0,
  optimizedTotal: 0,
  filesProcessed: 0,
};

async function ensureOutputDir() {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    console.log(`Created output directory: ${OUTPUT_DIR}\n`);
  }
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

async function processImage(config) {
  const inputPath = path.join(INPUT_DIR, config.input);

  if (!fs.existsSync(inputPath)) {
    console.warn(`  Warning: ${config.input} not found, skipping...`);
    return;
  }

  const originalStats = fs.statSync(inputPath);
  stats.originalTotal += originalStats.size;

  const image = sharp(inputPath);
  const metadata = await image.metadata();

  console.log(`Processing: ${config.input}`);
  console.log(`  Original: ${metadata.width}x${metadata.height} (${formatBytes(originalStats.size)})`);
  console.log(`  Purpose: ${config.description}`);

  // Process each responsive size
  for (const size of SIZES) {
    // Skip sizes larger than original
    if (size.width > metadata.width) continue;

    const webpOutput = path.join(OUTPUT_DIR, `${config.output}${size.suffix}.webp`);
    const jpegOutput = path.join(OUTPUT_DIR, `${config.output}${size.suffix}.jpg`);

    // WebP version
    await sharp(inputPath)
      .resize(size.width, null, { withoutEnlargement: true })
      .webp({ quality: config.quality })
      .toFile(webpOutput);

    // JPEG fallback (skip for PNG with alpha)
    if (!config.preserveAlpha) {
      await sharp(inputPath)
        .resize(size.width, null, { withoutEnlargement: true })
        .jpeg({ quality: config.quality, mozjpeg: true })
        .toFile(jpegOutput);
    } else {
      // For PNGs, create PNG fallback instead
      const pngOutput = path.join(OUTPUT_DIR, `${config.output}${size.suffix}.png`);
      await sharp(inputPath)
        .resize(size.width, null, { withoutEnlargement: true })
        .png({ quality: config.quality, compressionLevel: 9 })
        .toFile(pngOutput);
    }

    const webpStats = fs.statSync(webpOutput);
    stats.optimizedTotal += webpStats.size;

    console.log(`    ${size.width}w: WebP ${formatBytes(webpStats.size)}`);
  }

  // Create full-size optimized versions
  const webpFull = path.join(OUTPUT_DIR, `${config.output}.webp`);

  await sharp(inputPath)
    .resize(config.maxWidth, null, { withoutEnlargement: true })
    .webp({ quality: config.quality })
    .toFile(webpFull);

  if (!config.preserveAlpha) {
    const jpegFull = path.join(OUTPUT_DIR, `${config.output}.jpg`);
    await sharp(inputPath)
      .resize(config.maxWidth, null, { withoutEnlargement: true })
      .jpeg({ quality: config.quality, mozjpeg: true })
      .toFile(jpegFull);
  } else {
    const pngFull = path.join(OUTPUT_DIR, `${config.output}.png`);
    await sharp(inputPath)
      .resize(config.maxWidth, null, { withoutEnlargement: true })
      .png({ quality: config.quality, compressionLevel: 9 })
      .toFile(pngFull);
  }

  const webpFullStats = fs.statSync(webpFull);
  console.log(`    Full: WebP ${formatBytes(webpFullStats.size)}`);

  stats.filesProcessed++;
  console.log('');
}

async function createGifPoster() {
  const gifPath = path.join(INPUT_DIR, 'pasos-basicos-animated.gif');

  if (!fs.existsSync(gifPath)) {
    console.log('No GIF found for poster extraction, skipping...\n');
    return;
  }

  const originalStats = fs.statSync(gifPath);
  stats.originalTotal += originalStats.size;

  console.log(`Processing: pasos-basicos-animated.gif`);
  console.log(`  Original: ${formatBytes(originalStats.size)} (animated GIF)`);
  console.log(`  Purpose: Hero animation poster frame`);

  try {
    // Extract first frame and create poster
    const posterWebp = path.join(OUTPUT_DIR, 'pasos-basicos-poster.webp');
    const posterJpg = path.join(OUTPUT_DIR, 'pasos-basicos-poster.jpg');

    await sharp(gifPath, { pages: 1 })
      .resize(1200, null, { withoutEnlargement: true })
      .webp({ quality: 85 })
      .toFile(posterWebp);

    await sharp(gifPath, { pages: 1 })
      .resize(1200, null, { withoutEnlargement: true })
      .jpeg({ quality: 85, mozjpeg: true })
      .toFile(posterJpg);

    const posterStats = fs.statSync(posterWebp);
    stats.optimizedTotal += posterStats.size;

    console.log(`    Poster: WebP ${formatBytes(posterStats.size)}`);
    console.log('');

    stats.filesProcessed++;
  } catch (error) {
    console.log(`  Warning: Could not process GIF - ${error.message}\n`);
  }
}

async function main() {
  console.log('='.repeat(60));
  console.log('  Sabor Con Flow - Image Optimization');
  console.log('='.repeat(60));
  console.log('');

  await ensureOutputDir();

  // Process all configured images
  for (const config of IMAGES) {
    await processImage(config);
  }

  // Create poster from animated GIF
  await createGifPoster();

  // Print summary
  console.log('='.repeat(60));
  console.log('  Summary');
  console.log('='.repeat(60));
  console.log(`  Files processed: ${stats.filesProcessed}`);
  console.log(`  Original total:  ${formatBytes(stats.originalTotal)}`);
  console.log(`  Optimized total: ${formatBytes(stats.optimizedTotal)}`);

  const savings = stats.originalTotal - stats.optimizedTotal;
  const savingsPercent = ((savings / stats.originalTotal) * 100).toFixed(1);

  console.log(`  Savings:         ${formatBytes(savings)} (${savingsPercent}%)`);
  console.log('');
  console.log(`  Output directory: ${OUTPUT_DIR}`);
  console.log('');
  console.log('Image optimization complete!');
}

main().catch((error) => {
  console.error('Error during image optimization:', error);
  process.exit(1);
});
