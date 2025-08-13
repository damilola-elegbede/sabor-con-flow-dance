import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Build cleanup utilities
 * Safely removes dist/ directory and other build artifacts
 */

const distDir = path.join(__dirname, '..', 'dist');
const buildArtifacts = [
    'dist',
    '.tmp',
    'build',
    'coverage'
];

/**
 * Remove directory recursively
 */
function removeDirectory(dirPath) {
    if (!fs.existsSync(dirPath)) {
        return false;
    }

    try {
        fs.rmSync(dirPath, { recursive: true, force: true });
        console.log(`🗑️  Removed: ${path.relative(process.cwd(), dirPath)}`);
        return true;
    } catch (error) {
        console.error(`❌ Failed to remove ${dirPath}: ${error.message}`);
        return false;
    }
}

/**
 * Remove file safely
 */
function removeFile(filePath) {
    if (!fs.existsSync(filePath)) {
        return false;
    }

    try {
        fs.unlinkSync(filePath);
        console.log(`🗑️  Removed file: ${path.relative(process.cwd(), filePath)}`);
        return true;
    } catch (error) {
        console.error(`❌ Failed to remove file ${filePath}: ${error.message}`);
        return false;
    }
}

/**
 * Clean specific directory
 */
function cleanDirectory(dirPath) {
    const absolutePath = path.resolve(dirPath);
    
    if (!fs.existsSync(absolutePath)) {
        console.log(`⚠️  Directory does not exist: ${path.relative(process.cwd(), absolutePath)}`);
        return false;
    }

    return removeDirectory(absolutePath);
}

/**
 * Clean all build artifacts
 */
function cleanAll() {
    console.log('🧹 Starting cleanup process...');
    
    let cleanedCount = 0;
    const projectRoot = path.join(__dirname, '..');
    
    for (const artifact of buildArtifacts) {
        const artifactPath = path.join(projectRoot, artifact);
        
        if (removeDirectory(artifactPath)) {
            cleanedCount++;
        }
    }
    
    // Clean common temporary files
    const tempFiles = [
        path.join(projectRoot, '*.log'),
        path.join(projectRoot, '.DS_Store'),
        path.join(projectRoot, 'npm-debug.log*'),
        path.join(projectRoot, 'yarn-debug.log*'),
        path.join(projectRoot, 'yarn-error.log*')
    ];
    
    // Note: In a real implementation, you'd use glob patterns
    // For now, we'll check specific common files
    const commonTempFiles = [
        'build.log',
        'error.log',
        'debug.log',
        '.DS_Store',
        'npm-debug.log',
        'yarn-debug.log',
        'yarn-error.log'
    ];
    
    for (const tempFile of commonTempFiles) {
        const tempFilePath = path.join(projectRoot, tempFile);
        if (removeFile(tempFilePath)) {
            cleanedCount++;
        }
    }
    
    if (cleanedCount > 0) {
        console.log(`✅ Cleanup completed! Removed ${cleanedCount} items.`);
    } else {
        console.log('✨ No cleanup needed - workspace is already clean!');
    }
    
    return true;
}

/**
 * Clean only dist directory
 */
function cleanDist() {
    console.log('🧹 Cleaning dist directory...');
    
    if (cleanDirectory(distDir)) {
        console.log('✅ Dist directory cleaned successfully!');
    } else {
        console.log('✨ Dist directory is already clean!');
    }
    
    return true;
}

/**
 * Clean node_modules (nuclear option)
 */
function cleanNodeModules() {
    console.log('💣 Nuclear cleanup: removing node_modules...');
    console.log('⚠️  You will need to run npm install after this!');
    
    const nodeModulesPath = path.join(__dirname, '..', 'node_modules');
    
    if (cleanDirectory(nodeModulesPath)) {
        console.log('✅ node_modules removed! Run npm install to restore dependencies.');
    } else {
        console.log('✨ node_modules directory not found or already clean!');
    }
    
    return true;
}

// Safe error handling
process.on('uncaughtException', (error) => {
    if (error.code === 'ENOENT') {
        console.log(`ℹ️  File or directory already removed: ${error.path}`);
    } else if (error.code === 'EACCES') {
        console.error(`❌ Permission denied: ${error.path}`);
        console.log('💡 Try running with elevated permissions or check file permissions.');
    } else {
        console.error(`❌ Unexpected error during cleanup: ${error.message}`);
    }
});

// Handle command line arguments
function handleCommandLine() {
    const args = process.argv.slice(2);
    
    if (args.includes('--help') || args.includes('-h')) {
        console.log(`
🧹 Clean Build Script

Usage:
  node clean.js [options]

Options:
  --all           Clean all build artifacts (default)
  --dist          Clean only dist directory
  --nuclear       Clean node_modules (requires npm install after)
  --help, -h      Show this help message

Examples:
  node clean.js            # Clean all build artifacts
  node clean.js --dist     # Clean only dist directory
  node clean.js --nuclear  # Remove node_modules
        `);
        return;
    }
    
    if (args.includes('--nuclear')) {
        cleanNodeModules();
    } else if (args.includes('--dist')) {
        cleanDist();
    } else {
        cleanAll();
    }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
    handleCommandLine();
}

export { 
    cleanAll, 
    cleanDist, 
    cleanDirectory, 
    cleanNodeModules,
    removeDirectory, 
    removeFile 
};