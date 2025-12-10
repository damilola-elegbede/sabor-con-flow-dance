const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const { WorkboxPlugin } = require('workbox-webpack-plugin');
const WebpackManifestPlugin = require('./build-scripts/webpack-manifest');
const PerformanceBudgetPlugin = require('./build-scripts/performance-budget');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  const isDevelopment = !isProduction;

  return {
    entry: {
      // Core bundles with route-based code splitting
      main: './src/js/main.js',
      mobile: './src/js/mobile-nav.js',
      gallery: './src/js/gallery.js',
      analytics: './src/js/analytics.js',
      
      // Page-specific bundles
      home: './src/js/pages/home.js',
      contact: './src/js/pages/contact.js',
      pricing: './src/js/pages/pricing.js',
      
      // Feature bundles (lazy loaded)
      'lazy-load': './src/js/features/lazy-load.js',
      'performance-monitor': './src/js/features/performance-monitor.js',
      'social-features': './src/js/features/social-features.js',
      'whatsapp-chat': './src/js/features/whatsapp-chat.js',
      
      // Vendor bundles
      vendor: './src/js/vendor.js'
    },

    output: {
      path: path.resolve(__dirname, 'static/js/dist'),
      filename: isProduction 
        ? '[name].[contenthash:8].bundle.js' 
        : '[name].bundle.js',
      chunkFilename: isProduction 
        ? '[name].[contenthash:8].chunk.js' 
        : '[name].chunk.js',
      publicPath: '/static/js/dist/',
      clean: true,
      // Enable module federation for micro-frontend architecture
      library: {
        type: 'umd',
        name: 'SaborConFlowModules'
      },
      globalObject: 'this'
    },

    mode: isProduction ? 'production' : 'development',
    devtool: isProduction ? 'source-map' : 'eval-source-map',

    optimization: {
      minimize: isProduction,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: isProduction,
              drop_debugger: isProduction,
              pure_funcs: ['console.log', 'console.info'],
            },
            mangle: {
              safari10: true,
            },
            format: {
              comments: false,
            },
          },
          extractComments: false,
        }),
      ],
      
      // Advanced code splitting strategy
      splitChunks: {
        chunks: 'all',
        minSize: 20000,
        maxSize: 250000,
        cacheGroups: {
          // Vendor libraries
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 20,
          },
          
          // Common utilities used across multiple chunks
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            priority: 10,
            reuseExistingChunk: true,
          },
          
          // Critical path bundle
          critical: {
            test: /[\\/]src[\\/]js[\\/](main|mobile-nav|lazy-load)\.js$/,
            name: 'critical',
            chunks: 'all',
            priority: 30,
          },
          
          // Analytics and performance monitoring
          analytics: {
            test: /[\\/]src[\\/]js[\\/](analytics|performance)[\\/]/,
            name: 'analytics',
            chunks: 'all',
            priority: 15,
          },
          
          // Social features bundle
          social: {
            test: /[\\/]src[\\/]js[\\/]features[\\/](social|whatsapp)[\\/]/,
            name: 'social',
            chunks: 'all',
            priority: 15,
          }
        },
      },
      
      // Runtime chunk for better caching
      runtimeChunk: {
        name: 'runtime',
      },
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
                    browsers: ['> 1%', 'last 2 versions', 'not dead'],
                  },
                  modules: false,
                  useBuiltIns: 'usage',
                  corejs: 3,
                }],
              ],
              plugins: [
                // Dynamic import support for code splitting
                '@babel/plugin-syntax-dynamic-import',
              ],
            },
          },
        },
        
        {
          test: /\.css$/,
          use: [
            isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
            'css-loader',
          ],
        },
      ],
    },

    plugins: [
      // Extract CSS to separate files in production
      ...(isProduction ? [
        new MiniCssExtractPlugin({
          filename: '../css/[name].[contenthash:8].css',
          chunkFilename: '../css/[name].[contenthash:8].chunk.css',
        }),
      ] : []),

      // Bundle analyzer for optimization insights
      ...(process.env.ANALYZE ? [
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: false,
          reportFilename: path.resolve(__dirname, 'bundle-report.html'),
        }),
      ] : []),

      // Webpack manifest for Django integration
      new WebpackManifestPlugin({
        fileName: 'manifest.json',
        publicPath: '/static/js/dist/',
      }),

      // Performance budget enforcement
      new PerformanceBudgetPlugin({
        budgets: {
          main: 250000,      // 250KB for main bundle
          vendor: 300000,    // 300KB for vendor bundle
          critical: 150000,  // 150KB for critical path bundles
          page: 100000,      // 100KB for page-specific bundles
          feature: 75000     // 75KB for feature bundles
        }
      }),

      // Service Worker for Progressive Web App features
      ...(isProduction ? [
        new WorkboxPlugin.GenerateSW({
          clientsClaim: true,
          skipWaiting: true,
          runtimeCaching: [
            {
              urlPattern: /\.(?:png|jpg|jpeg|svg|webp)$/,
              handler: 'CacheFirst',
              options: {
                cacheName: 'images',
                expiration: {
                  maxEntries: 60,
                  maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
                },
              },
            },
            {
              urlPattern: /\.(?:js|css)$/,
              handler: 'StaleWhileRevalidate',
              options: {
                cacheName: 'static-resources',
              },
            },
          ],
        }),
      ] : []),
    ],

    // Development server configuration
    devServer: {
      static: {
        directory: path.join(__dirname, 'static'),
      },
      compress: true,
      port: 9000,
      hot: true,
      proxy: {
        '/': 'http://localhost:8000', // Proxy Django dev server
      },
    },

    // Performance budget enforcement
    performance: {
      hints: isProduction ? 'warning' : false,
      maxEntrypointSize: 300000, // 300KB
      maxAssetSize: 250000, // 250KB
      assetFilter: (assetFilename) => {
        return assetFilename.endsWith('.js') || assetFilename.endsWith('.css');
      },
    },

    // Resolve configuration
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src/js'),
        '@features': path.resolve(__dirname, 'src/js/features'),
        '@utils': path.resolve(__dirname, 'src/js/utils'),
        '@pages': path.resolve(__dirname, 'src/js/pages'),
      },
      extensions: ['.js', '.json'],
    },

    // External dependencies (CDN)
    externals: {
      // Load from CDN in production
      ...(isProduction ? {
        'font-awesome': 'FontAwesome',
      } : {}),
    },

    // Stats configuration for better output
    stats: {
      assets: true,
      chunks: false,
      modules: false,
      colors: true,
      errors: true,
      warnings: true,
      performance: true,
      timings: true,
    },
  };
};