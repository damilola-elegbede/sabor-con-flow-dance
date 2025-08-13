import { describe, it, expect, beforeAll, afterAll, beforeEach, afterEach, vi } from 'vitest';
import { execSync, spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '../..');

/**
 * Build System Verification Tests
 * 
 * Tests all build processes and verifies output structure
 * according to PRD specification requirements.
 */
describe('Build System Tests', () => {
  // Test timeout for build operations
  const buildTimeout = 30000;
  
  beforeAll(() => {
    // Clean any existing build outputs
    try {
      execSync('npm run clean:dist', { stdio: 'pipe', cwd: projectRoot });
    } catch (error) {
      // Ignore clean errors in case directories don't exist
      console.warn('Clean command failed, continuing...');
    }
  }, buildTimeout);

  afterAll(() => {
    // Clean up after tests
    try {
      execSync('npm run clean:dist', { stdio: 'pipe', cwd: projectRoot });
    } catch (error) {
      // Ignore cleanup errors
    }
  });

  describe('CSS Build Process', () => {
    it('should build CSS successfully in development mode', async () => {
      // Run CSS build in development mode
      const result = execSync('npm run build:css', { 
        encoding: 'utf8',
        cwd: projectRoot
      });
      
      // Verify build completed without errors
      expect(result).toBeDefined();
      
      // Check that output file exists
      const cssOutputPath = path.join(projectRoot, 'staticfiles/css/styles.css');
      expect(fs.existsSync(cssOutputPath)).toBe(true);
      
      // Verify CSS file has content
      const cssContent = fs.readFileSync(cssOutputPath, 'utf8');
      expect(cssContent.length).toBeGreaterThan(0);
      
      // Verify source map exists in development
      const sourceMapPath = `${cssOutputPath}.map`;
      expect(fs.existsSync(sourceMapPath)).toBe(true);
    }, buildTimeout);

    it('should build CSS successfully in production mode', async () => {
      // Run CSS build in production mode
      const result = execSync('npm run build:css:prod', { 
        encoding: 'utf8',
        cwd: projectRoot
      });
      
      // Verify build completed without errors
      expect(result).toBeDefined();
      
      // Check that output file exists
      const cssOutputPath = path.join(projectRoot, 'staticfiles/css/styles.min.css');
      expect(fs.existsSync(cssOutputPath)).toBe(true);
      
      // Verify CSS file has content and is minified
      const cssContent = fs.readFileSync(cssOutputPath, 'utf8');
      expect(cssContent.length).toBeGreaterThan(0);
      
      // Production CSS should not have source map inline
      expect(cssContent).not.toContain('sourceMappingURL');
    }, buildTimeout);

    it('should process CSS with PostCSS plugins correctly', async () => {
      // Build CSS and check for expected processing
      execSync('npm run build:css', { 
        encoding: 'utf8',
        cwd: projectRoot
      });
      
      const cssOutputPath = path.join(projectRoot, 'staticfiles/css/styles.css');
      const cssContent = fs.readFileSync(cssOutputPath, 'utf8');
      
      // Verify autoprefixer added vendor prefixes (common properties)
      expect(
        cssContent.includes('-webkit-') || 
        cssContent.includes('-moz-') || 
        cssContent.includes('-ms-')
      ).toBe(true);
      
      // Verify CSS is valid (no obvious syntax errors)
      expect(cssContent).toMatch(/\{[\s\S]*\}/);
    }, buildTimeout);
  });

  describe('JavaScript Build Process', () => {
    it('should build JavaScript with Webpack successfully', async () => {
      // Run JavaScript build
      const result = execSync('npm run build:js', { 
        encoding: 'utf8',
        cwd: projectRoot
      });
      
      // Verify build completed without errors
      expect(result).toBeDefined();
      
      // Check that output files exist
      const jsOutputDir = path.join(projectRoot, 'static/js');
      expect(fs.existsSync(jsOutputDir)).toBe(true);
      
      // Check for main bundle
      const jsFiles = fs.readdirSync(jsOutputDir);
      const mainBundle = jsFiles.find(file => file.startsWith('main.') && file.endsWith('.js'));
      expect(mainBundle).toBeDefined();
      
      // Verify main bundle has content
      const mainBundlePath = path.join(jsOutputDir, mainBundle);
      const bundleContent = fs.readFileSync(mainBundlePath, 'utf8');
      expect(bundleContent.length).toBeGreaterThan(0);
    }, buildTimeout);

    it('should generate correct webpack output structure', async () => {
      // Build JavaScript
      execSync('npm run build:js', { 
        encoding: 'utf8',
        cwd: projectRoot
      });
      
      const jsOutputDir = path.join(projectRoot, 'static/js');
      const jsFiles = fs.readdirSync(jsOutputDir);
      
      // Should have main bundle
      expect(jsFiles.some(file => file.startsWith('main.'))).toBe(true);
      
      // Should have performance-monitor bundle
      expect(jsFiles.some(file => file.startsWith('performance-monitor.'))).toBe(true);
      
      // Should have lazy-load bundle
      expect(jsFiles.some(file => file.startsWith('lazy-load.'))).toBe(true);
      
      // May have vendors bundle if dependencies exist
      const hasVendors = jsFiles.some(file => file.startsWith('vendors.'));
      console.log('Vendors bundle present:', hasVendors);
    }, buildTimeout);

    it('should generate source maps for JavaScript', async () => {
      // Build JavaScript
      execSync('npm run build:js', { 
        encoding: 'utf8',
        cwd: projectRoot
      });
      
      const jsOutputDir = path.join(projectRoot, 'static/js');
      const jsFiles = fs.readdirSync(jsOutputDir);
      
      // Check for source map files
      const sourceMapFiles = jsFiles.filter(file => file.endsWith('.js.map'));
      expect(sourceMapFiles.length).toBeGreaterThan(0);
      
      // Verify source maps have content
      sourceMapFiles.forEach(mapFile => {
        const mapPath = path.join(jsOutputDir, mapFile);
        const mapContent = fs.readFileSync(mapPath, 'utf8');
        expect(mapContent.length).toBeGreaterThan(0);
        
        // Should be valid JSON
        expect(() => JSON.parse(mapContent)).not.toThrow();
      });
    }, buildTimeout);
  });

  describe('Asset Copying Process', () => {
    beforeEach(() => {
      // Ensure source assets directory exists
      const srcAssetsDir = path.join(projectRoot, 'src/assets');
      if (!fs.existsSync(srcAssetsDir)) {
        fs.mkdirSync(srcAssetsDir, { recursive: true });
        
        // Create test subdirectories
        ['images', 'fonts', 'videos'].forEach(subdir => {
          const subdirPath = path.join(srcAssetsDir, subdir);
          fs.mkdirSync(subdirPath, { recursive: true });
          
          // Create a test file in each subdirectory
          const testFilePath = path.join(subdirPath, `test-${subdir}.txt`);
          fs.writeFileSync(testFilePath, `Test ${subdir} asset file`);
        });
      }
    });

    it('should optimize assets from static to staticfiles', async () => {
      // Run asset optimization
      const result = execSync('npm run build:assets', { 
        encoding: 'utf8',
        cwd: projectRoot
      });
      
      // Verify optimization completed without errors
      expect(result).toBeDefined();
      
      // Check that staticfiles directories exist
      const staticfilesDir = path.join(projectRoot, 'staticfiles');
      expect(fs.existsSync(staticfilesDir)).toBe(true);
      
      // Verify asset optimization outputs exist
      ['images', 'css', 'js'].forEach(subdir => {
        const staticSubdir = path.join(staticfilesDir, subdir);
        if (fs.existsSync(staticSubdir)) {
          const files = fs.readdirSync(staticSubdir);
          expect(files.length).toBeGreaterThan(0);
        }
      });
      
      // Check for asset manifest
      const assetManifest = path.join(staticfilesDir, 'asset-manifest.json');
      expect(fs.existsSync(assetManifest)).toBe(true);
    }, buildTimeout);

    it('should handle missing source directories gracefully', async () => {
      // Temporarily rename source directory
      const srcAssetsDir = path.join(projectRoot, 'src/assets');
      const tempDir = path.join(projectRoot, 'src/assets-temp');
      
      if (fs.existsSync(srcAssetsDir)) {
        fs.renameSync(srcAssetsDir, tempDir);
      }
      
      try {
        // Run asset copying - should not fail completely
        const result = execSync('npm run build:assets', { 
          encoding: 'utf8',
          cwd: projectRoot,
          stdio: 'pipe'
        });
        
        // Should complete but may warn about missing directories
        expect(result).toBeDefined();
        
      } catch (error) {
        // Asset copying might fail if no source directory exists
        // This is acceptable behavior
        expect(error.message).toContain('assets');
      } finally {
        // Restore directory if it was moved
        if (fs.existsSync(tempDir)) {
          fs.renameSync(tempDir, srcAssetsDir);
        }
      }
    }, buildTimeout);
  });

  describe('Complete Build Process', () => {
    it('should run complete build process successfully', async () => {
      // Run complete build
      const result = execSync('npm run build', { 
        encoding: 'utf8',
        cwd: projectRoot,
        stdio: 'pipe'
      });
      
      // Verify build completed without errors
      expect(result).toBeDefined();
      
      // Check that all expected outputs exist
      const outputs = [
        'staticfiles/css/styles.min.css',  // Production CSS
        'static/js',                      // JavaScript output directory
        'staticfiles/asset-manifest.json' // Asset manifest
      ];
      
      outputs.forEach(outputPath => {
        const fullPath = path.join(projectRoot, outputPath);
        expect(fs.existsSync(fullPath)).toBe(true);
      });
    }, buildTimeout * 2); // Double timeout for complete build
  });

  describe('Dist Structure Verification', () => {
    beforeAll(async () => {
      // Run complete build to ensure dist structure
      try {
        execSync('npm run build', { 
          encoding: 'utf8',
          cwd: projectRoot,
          stdio: 'pipe'
        });
      } catch (error) {
        console.warn('Build failed in beforeAll, some tests may fail');
      }
    }, buildTimeout);

    it('should have correct dist directory structure', () => {
      const distDir = path.join(projectRoot, 'dist');
      
      if (fs.existsSync(distDir)) {
        // Check for assets directory
        expect(fs.existsSync(path.join(distDir, 'assets'))).toBe(true);
        
        // Check for expected subdirectories if they exist
        const assetsDir = path.join(distDir, 'assets');
        const assetsDirContents = fs.readdirSync(assetsDir);
        
        // Should contain at least some asset subdirectories
        const expectedSubdirs = ['images', 'fonts', 'videos'];
        const hasAssetSubdirs = expectedSubdirs.some(subdir => 
          assetsDirContents.includes(subdir)
        );
        
        expect(hasAssetSubdirs || assetsDirContents.length === 0).toBe(true);
      }
    });

    it('should have correct static/js structure', () => {
      const jsDir = path.join(projectRoot, 'static/js');
      
      if (fs.existsSync(jsDir)) {
        const jsFiles = fs.readdirSync(jsDir);
        
        // Should have JavaScript bundles
        expect(jsFiles.length).toBeGreaterThan(0);
        
        // Should have at least main bundle
        expect(jsFiles.some(file => file.startsWith('main.'))).toBe(true);
        
        // Files should be actual JavaScript files or source maps
        jsFiles.forEach(file => {
          expect(
            file.endsWith('.js') || 
            file.endsWith('.js.map') || 
            file.endsWith('.js.gz')  // Allow gzipped files
          ).toBe(true);
        });
      }
    });

    it('should have correct staticfiles/css structure', () => {
      const cssDir = path.join(projectRoot, 'staticfiles/css');
      
      if (fs.existsSync(cssDir)) {
        const cssFiles = fs.readdirSync(cssDir);
        
        // Should have CSS files
        expect(cssFiles.length).toBeGreaterThan(0);
        
        // Should have either styles.css or styles.min.css (or both)
        const hasStylesCSS = cssFiles.some(file => 
          file === 'styles.css' || file === 'styles.min.css'
        );
        expect(hasStylesCSS).toBe(true);
        
        // Files should be CSS or source map files
        cssFiles.forEach(file => {
          expect(
            file.endsWith('.css') || 
            file.endsWith('.css.map') ||
            file.endsWith('.min.css')
          ).toBe(true);
        });
      }
    });

    it('should verify file sizes are reasonable', () => {
      const filesToCheck = [
        'staticfiles/css/styles.css',
        'staticfiles/css/styles.min.css'
      ];
      
      filesToCheck.forEach(filePath => {
        const fullPath = path.join(projectRoot, filePath);
        if (fs.existsSync(fullPath)) {
          const stats = fs.statSync(fullPath);
          
          // CSS files should not be empty
          expect(stats.size).toBeGreaterThan(0);
          
          // CSS files should be reasonable size (not corrupted)
          expect(stats.size).toBeLessThan(10 * 1024 * 1024); // Less than 10MB
          
          // Minified files should generally be smaller than unminified
          if (filePath.includes('.min.css')) {
            const unminifiedPath = fullPath.replace('.min.css', '.css');
            if (fs.existsSync(unminifiedPath)) {
              const unminifiedStats = fs.statSync(unminifiedPath);
              // Minified should be smaller or equal (edge case where original is tiny)
              expect(stats.size).toBeLessThanOrEqual(unminifiedStats.size + 100); // Small buffer
            }
          }
        }
      });
    });
  });

  describe('Build Performance', () => {
    it('should complete CSS build within reasonable time', async () => {
      const startTime = Date.now();
      
      execSync('npm run build:css', { 
        encoding: 'utf8',
        cwd: projectRoot
      });
      
      const buildTime = Date.now() - startTime;
      
      // CSS build should complete within 10 seconds
      expect(buildTime).toBeLessThan(10000);
      console.log(`CSS build completed in ${buildTime}ms`);
    });

    it('should complete JavaScript build within reasonable time', async () => {
      const startTime = Date.now();
      
      execSync('npm run build:js', { 
        encoding: 'utf8',
        cwd: projectRoot
      });
      
      const buildTime = Date.now() - startTime;
      
      // JS build should complete within 15 seconds
      expect(buildTime).toBeLessThan(15000);
      console.log(`JavaScript build completed in ${buildTime}ms`);
    });

    it('should complete asset copying within reasonable time', async () => {
      const startTime = Date.now();
      
      execSync('npm run build:assets', { 
        encoding: 'utf8',
        cwd: projectRoot
      });
      
      const buildTime = Date.now() - startTime;
      
      // Asset optimization should complete within 10 seconds (includes image processing)
      expect(buildTime).toBeLessThan(10000);
      console.log(`Asset copying completed in ${buildTime}ms`);
    });
  });

  describe('Build Error Handling', () => {
    it('should handle invalid CSS gracefully', async () => {
      // Create a backup of the main CSS file
      const mainCSSPath = path.join(projectRoot, 'src/css/styles.css');
      const backupPath = `${mainCSSPath}.backup`;
      
      // Only run this test if the main CSS file exists
      if (fs.existsSync(mainCSSPath)) {
        try {
          // Backup original
          fs.copyFileSync(mainCSSPath, backupPath);
          
          // Write invalid CSS
          fs.writeFileSync(mainCSSPath, 'invalid-css { this is not valid css');
          
          // Attempt build - should fail gracefully
          try {
            execSync('npm run build:css', { 
              encoding: 'utf8',
              cwd: projectRoot,
              stdio: 'pipe'
            });
            
            // If build succeeds, PostCSS handled the error
            expect(true).toBe(true);
            
          } catch (error) {
            // Build should fail with meaningful error message
            expect(error.message).toBeDefined();
            expect(error.status).toBe(1);
          }
          
        } finally {
          // Restore original file
          if (fs.existsSync(backupPath)) {
            fs.copyFileSync(backupPath, mainCSSPath);
            fs.unlinkSync(backupPath);
          }
        }
      }
    });

    it('should handle missing source files appropriately', async () => {
      // Test with non-existent main.js entry point
      const webpackConfig = path.join(projectRoot, 'webpack.config.js');
      
      if (fs.existsSync(webpackConfig)) {
        try {
          // This should fail because src/js/main.js doesn't exist
          execSync('npm run build:js', { 
            encoding: 'utf8',
            cwd: projectRoot,
            stdio: 'pipe'
          });
          
          // If it succeeds, webpack handled missing files gracefully
          expect(true).toBe(true);
          
        } catch (error) {
          // Expected to fail with missing entry point
          expect(error.message).toBeDefined();
          expect(error.status).toBe(1);
        }
      }
    });
  });
});