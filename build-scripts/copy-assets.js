import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Asset copying from src/assets to dist/
 * Supports images, fonts, videos subdirectories
 */

const srcAssetsDir = path.join(__dirname, '..', 'src', 'assets');
const distAssetsDir = path.join(__dirname, '..', 'dist', 'assets');

// Asset subdirectories to copy
const assetSubdirs = ['images', 'fonts', 'videos'];

/**
 * Create directory recursively if it doesn't exist
 */
function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    console.log(`📁 Created directory: ${dirPath}`);
  }
}

/**
 * Copy file from source to destination
 */
function copyFile(src, dest) {
  try {
    // Ensure destination directory exists
    ensureDir(path.dirname(dest));

    fs.copyFileSync(src, dest);
    console.log(
      `✅ Copied: ${path.relative(process.cwd(), src)} → ${path.relative(process.cwd(), dest)}`
    );
    return true;
  } catch (error) {
    console.error(`❌ Failed to copy ${src}: ${error.message}`);
    return false;
  }
}

/**
 * Copy directory recursively
 */
function copyDirectory(src, dest) {
  if (!fs.existsSync(src)) {
    console.warn(`⚠️  Source directory does not exist: ${src}`);
    return;
  }

  ensureDir(dest);

  const entries = fs.readdirSync(src, { withFileTypes: true });
  let copiedCount = 0;

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDirectory(srcPath, destPath);
    } else {
      if (copyFile(srcPath, destPath)) {
        copiedCount++;
      }
    }
  }

  if (copiedCount > 0) {
    console.log(`📦 Copied ${copiedCount} files from ${path.relative(process.cwd(), src)}`);
  }
}

/**
 * Main asset copying function
 */
function copyAssets() {
  console.log('🚀 Starting asset copy process...');

  // Check if source assets directory exists
  if (!fs.existsSync(srcAssetsDir)) {
    console.error(`❌ Source assets directory not found: ${srcAssetsDir}`);
    console.log('💡 Create src/assets directory with subdirectories: images, fonts, videos');
    return false;
  }

  // Ensure dist directory exists
  ensureDir(distAssetsDir);

  const _totalCopied = 0;

  // Copy each asset subdirectory
  for (const subdir of assetSubdirs) {
    const srcSubdir = path.join(srcAssetsDir, subdir);
    const destSubdir = path.join(distAssetsDir, subdir);

    if (fs.existsSync(srcSubdir)) {
      console.log(`\n📂 Processing ${subdir} assets...`);
      copyDirectory(srcSubdir, destSubdir);
    } else {
      console.log(`⚠️  ${subdir} directory not found, skipping...`);
    }
  }

  // Copy any root-level assets
  const rootAssets = fs
    .readdirSync(srcAssetsDir, { withFileTypes: true })
    .filter(entry => entry.isFile());

  if (rootAssets.length > 0) {
    console.log(`\n📄 Processing root-level assets...`);
    for (const asset of rootAssets) {
      const srcPath = path.join(srcAssetsDir, asset.name);
      const destPath = path.join(distAssetsDir, asset.name);
      copyFile(srcPath, destPath);
    }
  }

  console.log('\n✅ Asset copy process completed!');
  return true;
}

// Error handling for missing directories
process.on('uncaughtException', error => {
  if (error.code === 'ENOENT') {
    console.error(`❌ Directory or file not found: ${error.path}`);
    console.log('💡 Make sure all required directories exist before running the build.');
  } else {
    console.error(`❌ Unexpected error: ${error.message}`);
  }
  process.exit(1);
});

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  copyAssets();
}

export { copyAssets, copyDirectory, copyFile, ensureDir };
