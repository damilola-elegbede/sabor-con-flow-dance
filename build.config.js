/**
 * Build Configuration
 * 
 * Centralized configuration for all build tools and performance targets
 */

export const buildConfig = {
  // Performance targets from PRD
  performance: {
    buildTime: {
      max: 30000, // 30 seconds max full build
      dev: 5000,  // 5 seconds dev server start
      hotReload: 1000 // 1 second hot reload
    },
    bundleSize: {
      css: {
        max: 50 * 1024,      // 50KB gzipped
        critical: 14 * 1024   // 14KB critical CSS
      },
      js: {
        max: 150 * 1024,     // 150KB gzipped
        vendor: 100 * 1024   // 100KB vendor bundle
      },
      total: 200 * 1024      // 200KB total gzipped
    },
    assets: {
      maxImageSize: 500 * 1024,        // 500KB max per image
      compressionRatio: 0.3,           // 30% minimum compression
      webpSupport: true,               // Enable WebP format
      avifSupport: true,               // Enable AVIF format
      responsiveBreakpoints: [320, 480, 768, 1024, 1280, 1920]
    }
  },

  // Build paths
  paths: {
    src: {
      js: './src/js',
      css: './src/css',
      images: './static/images',
      fonts: './static/fonts',
      templates: './templates'
    },
    output: {
      js: './static/js',
      css: './staticfiles/css',
      images: './staticfiles/images/optimized',
      fonts: './staticfiles/fonts',
      reports: './reports'
    },
    temp: {
      cache: './node_modules/.cache',
      webpack: './.webpack-cache'
    }
  },

  // Webpack configuration
  webpack: {
    entry: {
      main: './src/js/main.js',
      'performance-monitor': './src/js/features/performance-monitor.js',
      'lazy-load': './src/js/features/lazy-load.js'
    },
    optimization: {
      splitChunks: {
        chunks: 'all',
        minSize: 20000,
        maxSize: 244000,
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: 10,
            chunks: 'all'
          },
          common: {
            name: 'common',
            minChunks: 2,
            priority: 5,
            reuseExistingChunk: true
          },
          critical: {
            name: 'critical',
            test: /critical|above-the-fold/,
            priority: 15,
            chunks: 'all'
          }
        }
      }
    },
    devServer: {
      port: 3000,
      hot: true,
      open: false,
      compress: true
    }
  },

  // CSS build configuration
  css: {
    autoprefixer: {
      overrideBrowserslist: [
        '> 1%',
        'last 2 versions',
        'not dead',
        'not ie 11'
      ]
    },
    cssnano: {
      preset: ['default', {
        discardComments: { removeAll: true },
        reduceIdents: false,
        zindex: false,
        autoprefixer: false,
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
        uniqueSelectors: true
      }]
    }
  },

  // Image optimization settings
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
    },
    svg: {
      removeComments: true,
      removeMetadata: true,
      removeXMLNS: false,
      inlineStyles: true
    }
  },

  // Critical CSS configuration
  critical: {
    url: process.env.CRITICAL_URL || 'http://localhost:8000',
    viewports: [
      { width: 320, height: 568, name: 'mobile' },
      { width: 768, height: 1024, name: 'tablet' },
      { width: 1920, height: 1080, name: 'desktop' }
    ],
    maxSize: 14 * 1024, // 14KB target
    timeout: 30000
  },

  // Development settings
  development: {
    sourceMap: true,
    watchOptions: {
      ignored: /node_modules/,
      aggregateTimeout: 300,
      poll: false
    },
    devMiddleware: {
      writeToDisk: false
    }
  },

  // Production settings
  production: {
    sourceMap: true,
    minify: true,
    compress: true,
    analyze: false,
    generateReport: true
  },

  // Performance monitoring
  monitoring: {
    enabled: true,
    thresholds: {
      buildTime: 30000,      // 30s max build time
      bundleSize: 200000,    // 200KB max bundle size
      regressionTolerance: 0.1 // 10% regression tolerance
    },
    reports: {
      json: true,
      html: true,
      console: true
    }
  },

  // Cache configuration
  cache: {
    type: 'filesystem',
    version: '1.0.0',
    buildDependencies: {
      config: [
        './webpack.config.js',
        './build.config.js',
        './package.json'
      ]
    }
  },

  // Environment variables
  env: {
    NODE_ENV: process.env.NODE_ENV || 'development',
    DEBUG: process.env.DEBUG === 'true',
    ANALYZE: process.env.ANALYZE === '1',
    CI: process.env.CI === 'true'
  }
};

export default buildConfig;