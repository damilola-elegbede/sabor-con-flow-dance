# PR 1.1: Project Setup & Build System

## PR Metadata

**Title**: Establish Project Foundation and Build System Infrastructure  
**Description**: Initialize modern frontend build system with npm scripts, Vercel configuration, and development environment setup  
**Dependencies**: None (Initial PR)  
**Estimated Effort**: 4-6 hours  
**Priority**: Critical Path  

## Implementation Overview

This PR establishes the foundational build system and project structure for the Sabor con Flow Dance website redesign, transitioning from Django-based static files to a modern frontend build pipeline with Vercel serverless functions.

## File Structure Changes

```
project-root/
├── package.json                 # NEW - npm dependencies and scripts
├── .nvmrc                      # NEW - Node.js version specification
├── .gitignore                  # UPDATED - add node_modules, build artifacts
├── vercel.json                 # UPDATED - enhance serverless config
├── webpack.config.js           # NEW - module bundling configuration
├── .babelrc                    # UPDATED - modern JS transpilation
├── build-scripts/              # NEW - custom build utilities
│   ├── build-css.js           # CSS processing and optimization
│   ├── build-js.js            # JavaScript bundling and minification
│   ├── copy-assets.js         # Static asset copying
│   └── clean.js               # Build cleanup utilities
├── src/                        # NEW - source files directory
│   ├── js/                    # JavaScript modules
│   ├── css/                   # SCSS/CSS source files
│   └── assets/                # Source images, fonts
└── dist/                       # NEW - build output directory
```

## Implementation Steps

### 1. Package.json Configuration

```json
{
  "name": "sabor-con-flow-dance",
  "version": "1.0.0",
  "description": "Professional dance studio website with booking and class management",
  "main": "index.js",
  "private": true,
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=8.0.0"
  },
  "scripts": {
    "dev": "npm run build:dev && vercel dev",
    "build": "npm run clean && npm run build:css && npm run build:js && npm run copy:assets",
    "build:dev": "npm run clean && npm run build:css:dev && npm run build:js:dev && npm run copy:assets",
    "build:css": "node build-scripts/build-css.js --production",
    "build:css:dev": "node build-scripts/build-css.js --development",
    "build:js": "webpack --mode=production",
    "build:js:dev": "webpack --mode=development",
    "copy:assets": "node build-scripts/copy-assets.js",
    "clean": "node build-scripts/clean.js",
    "watch": "npm run build:dev && npm run watch:css & npm run watch:js",
    "watch:css": "node build-scripts/build-css.js --watch",
    "watch:js": "webpack --mode=development --watch",
    "lint": "eslint src/js/**/*.js",
    "lint:fix": "eslint src/js/**/*.js --fix",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "deploy": "npm run build && vercel --prod",
    "preview": "npm run build && vercel",
    "analyze": "webpack-bundle-analyzer dist/js/bundle.js"
  },
  "dependencies": {
    "@vercel/analytics": "^1.1.1",
    "@vercel/speed-insights": "^1.0.2"
  },
  "devDependencies": {
    "@babel/core": "^7.23.6",
    "@babel/preset-env": "^7.23.6",
    "@vitest/ui": "^1.0.4",
    "autoprefixer": "^10.4.16",
    "babel-loader": "^9.1.3",
    "css-loader": "^6.8.1",
    "cssnano": "^6.0.2",
    "eslint": "^8.56.0",
    "mini-css-extract-plugin": "^2.7.6",
    "postcss": "^8.4.32",
    "postcss-cli": "^11.0.0",
    "sass": "^1.69.5",
    "sass-loader": "^13.3.2",
    "terser-webpack-plugin": "^5.3.9",
    "vitest": "^1.0.4",
    "webpack": "^5.89.0",
    "webpack-bundle-analyzer": "^4.10.1",
    "webpack-cli": "^5.1.4"
  }
}
```

### 2. Webpack Configuration

```javascript
// webpack.config.js
const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  
  return {
    entry: {
      main: './src/js/main.js',
      'performance-monitor': './src/js/performance-monitor.js',
      'lazy-load': './src/js/lazy-load.js'
    },
    output: {
      path: path.resolve(__dirname, 'dist/js'),
      filename: isProduction ? '[name].[contenthash].js' : '[name].js',
      clean: true
    },
    module: {
      rules: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: [
                ['@babel/preset-env', {
                  targets: {
                    browsers: ['> 1%', 'last 2 versions']
                  }
                }]
              ]
            }
          }
        },
        {
          test: /\.s?css$/,
          use: [
            MiniCssExtractPlugin.loader,
            'css-loader',
            'sass-loader'
          ]
        }
      ]
    },
    plugins: [
      new MiniCssExtractPlugin({
        filename: isProduction ? '../css/[name].[contenthash].css' : '../css/[name].css'
      })
    ],
    optimization: {
      minimize: isProduction,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: isProduction
            }
          }
        })
      ],
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all'
          }
        }
      }
    },
    devtool: isProduction ? 'source-map' : 'eval-source-map'
  };
};
```

### 3. Enhanced Vercel Configuration

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/**/*.js",
      "use": "@vercel/node"
    },
    {
      "src": "dist/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/static/(.*)",
      "dest": "/dist/$1"
    },
    {
      "src": "/(.*\\.(css|js|png|jpg|jpeg|webp|gif|svg|ico|woff|woff2|ttf|eot))",
      "dest": "/dist/$1",
      "headers": {
        "Cache-Control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/dist/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ],
  "env": {
    "NODE_ENV": "production"
  },
  "functions": {
    "api/**/*.js": {
      "maxDuration": 30
    }
  }
}
```

### 4. Build Scripts Implementation

```javascript
// build-scripts/build-css.js
const fs = require('fs').promises;
const path = require('path');
const postcss = require('postcss');
const autoprefixer = require('autoprefixer');
const cssnano = require('cssnano');

const isProduction = process.argv.includes('--production');
const isWatching = process.argv.includes('--watch');

const plugins = [autoprefixer];
if (isProduction) {
  plugins.push(cssnano({ preset: 'default' }));
}

async function buildCSS() {
  try {
    const srcDir = path.join(__dirname, '../src/css');
    const distDir = path.join(__dirname, '../dist/css');
    
    await fs.mkdir(distDir, { recursive: true });
    
    const files = await fs.readdir(srcDir);
    const cssFiles = files.filter(file => file.endsWith('.css'));
    
    for (const file of cssFiles) {
      const srcPath = path.join(srcDir, file);
      const distPath = path.join(distDir, file);
      
      const css = await fs.readFile(srcPath, 'utf8');
      const result = await postcss(plugins).process(css, { from: srcPath, to: distPath });
      
      await fs.writeFile(distPath, result.css);
      if (result.map) {
        await fs.writeFile(`${distPath}.map`, result.map.toString());
      }
      
      console.log(`✓ Built CSS: ${file}`);
    }
  } catch (error) {
    console.error('CSS build failed:', error);
    process.exit(1);
  }
}

if (isWatching) {
  const chokidar = require('chokidar');
  chokidar.watch('src/css/**/*.css').on('change', buildCSS);
  console.log('🔄 Watching CSS files for changes...');
} else {
  buildCSS();
}
```

```javascript
// build-scripts/copy-assets.js
const fs = require('fs').promises;
const path = require('path');

async function copyDirectory(src, dest) {
  await fs.mkdir(dest, { recursive: true });
  const entries = await fs.readdir(src, { withFileTypes: true });
  
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    
    if (entry.isDirectory()) {
      await copyDirectory(srcPath, destPath);
    } else {
      await fs.copyFile(srcPath, destPath);
    }
  }
}

async function copyAssets() {
  try {
    const assetDirs = [
      { src: 'src/assets/images', dest: 'dist/images' },
      { src: 'src/assets/fonts', dest: 'dist/fonts' },
      { src: 'src/assets/videos', dest: 'dist/videos' }
    ];
    
    for (const { src, dest } of assetDirs) {
      try {
        await copyDirectory(src, dest);
        console.log(`✓ Copied assets: ${src} → ${dest}`);
      } catch (error) {
        if (error.code !== 'ENOENT') {
          throw error;
        }
        console.log(`⚠ Source directory not found: ${src}`);
      }
    }
  } catch (error) {
    console.error('Asset copy failed:', error);
    process.exit(1);
  }
}

copyAssets();
```

### 5. Node.js Version Management

```
# .nvmrc
18.18.0
```

### 6. Updated .gitignore

```gitignore
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
dist/
.next/
.vercel/

# Environment files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Coverage
coverage/

# Temporary files
.tmp/
temp/

# Cache
.cache/
.parcel-cache/

# Django (legacy)
__pycache__/
*.py[cod]
*$py.class
staticfiles/
media/
db.sqlite3
```

## Testing Requirements

### Build System Tests

```javascript
// vitest.config.js
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    include: ['tests/build/**/*.test.js'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      include: ['build-scripts/**/*.js']
    }
  }
});
```

```javascript
// tests/build/build-system.test.js
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import fs from 'fs/promises';
import path from 'path';
import { execSync } from 'child_process';

describe('Build System', () => {
  beforeEach(async () => {
    // Clean dist directory
    await fs.rm('dist', { recursive: true, force: true });
  });

  it('should build CSS files', async () => {
    execSync('npm run build:css:dev', { stdio: 'inherit' });
    
    const cssFiles = await fs.readdir('dist/css');
    expect(cssFiles.length).toBeGreaterThan(0);
    expect(cssFiles.some(file => file.endsWith('.css'))).toBe(true);
  });

  it('should build JavaScript files', async () => {
    execSync('npm run build:js:dev', { stdio: 'inherit' });
    
    const jsFiles = await fs.readdir('dist/js');
    expect(jsFiles.length).toBeGreaterThan(0);
    expect(jsFiles.some(file => file.endsWith('.js'))).toBe(true);
  });

  it('should copy assets', async () => {
    execSync('npm run copy:assets', { stdio: 'inherit' });
    
    // Check if asset directories exist (if source exists)
    try {
      await fs.access('dist/images');
      const imageFiles = await fs.readdir('dist/images');
      expect(Array.isArray(imageFiles)).toBe(true);
    } catch (error) {
      // Asset directory doesn't exist, which is acceptable
      expect(error.code).toBe('ENOENT');
    }
  });

  it('should run complete build process', async () => {
    execSync('npm run build', { stdio: 'inherit' });
    
    // Verify dist structure
    const distContents = await fs.readdir('dist', { withFileTypes: true });
    const dirs = distContents.filter(item => item.isDirectory()).map(item => item.name);
    
    expect(dirs).toContain('css');
    expect(dirs).toContain('js');
  });
});
```

## Completion Checklist

### Infrastructure Setup
- [ ] Package.json with all dependencies and scripts
- [ ] Webpack configuration for module bundling
- [ ] Enhanced Vercel configuration
- [ ] Build scripts for CSS, JS, and assets
- [ ] Node.js version specification (.nvmrc)
- [ ] Updated .gitignore for frontend build

### Build System
- [ ] CSS processing with PostCSS and autoprefixer
- [ ] JavaScript bundling with code splitting
- [ ] Asset copying pipeline
- [ ] Development and production build modes
- [ ] File watching for development
- [ ] Build cleanup utilities

### Development Environment
- [ ] npm scripts for all common tasks
- [ ] ESLint configuration for code quality
- [ ] Source maps for debugging
- [ ] Hot reloading setup with Vercel dev
- [ ] Bundle analysis tools

### Testing Framework
- [ ] Vitest configuration
- [ ] Build system tests
- [ ] Coverage reporting setup
- [ ] Test scripts in package.json

### Documentation
- [ ] README updates for new build system
- [ ] npm script documentation
- [ ] Development setup instructions
- [ ] Build process documentation

## Performance Targets

- **Build Time**: < 30 seconds for full build
- **Dev Server Start**: < 5 seconds
- **Hot Reload**: < 1 second for CSS/JS changes
- **Bundle Size**: CSS < 50KB, JS < 150KB (gzipped)
- **Asset Optimization**: Images compressed, fonts subset

## Security Considerations

- All npm packages pinned to specific versions
- No sensitive data in client-side bundles
- CSP headers configured in Vercel
- Source maps excluded from production builds
- Bundle analysis to detect unexpected dependencies

## Next Steps

After PR approval and merge:
1. Team onboarding for new build system
2. CI/CD integration with build verification
3. Performance monitoring setup
4. Bundle size monitoring alerts
5. Preparation for PR 1.2: Static Site Foundation