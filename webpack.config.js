import path from 'path';
import MiniCssExtractPlugin from 'mini-css-extract-plugin';
import TerserPlugin from 'terser-webpack-plugin';
import CssMinimizerPlugin from 'css-minimizer-webpack-plugin';
import CompressionPlugin from 'compression-webpack-plugin';
import { BundleAnalyzerPlugin } from 'webpack-bundle-analyzer';
import HtmlWebpackPlugin from 'html-webpack-plugin';
import { fileURLToPath } from 'url';

// Performance monitoring plugin
class BuildPerformancePlugin {
  constructor() {
    this.startTime = Date.now();
  }
  
  apply(compiler) {
    compiler.hooks.run.tap('BuildPerformancePlugin', () => {
      this.startTime = Date.now();
      console.log('🚀 Build started...');
    });
    
    compiler.hooks.done.tap('BuildPerformancePlugin', (stats) => {
      const duration = Date.now() - this.startTime;
      const seconds = (duration / 1000).toFixed(2);
      
      console.log(`✅ Build completed in ${seconds}s`);
      
      if (duration > 30000) {
        console.warn('⚠️  Build time exceeds 30s target');
      }
      
      // Log bundle sizes
      const assets = stats.compilation.assets;
      let totalSize = 0;
      let jsSize = 0;
      let cssSize = 0;
      
      Object.entries(assets).forEach(([name, asset]) => {
        const size = asset.size();
        totalSize += size;
        
        if (name.endsWith('.js')) {
          jsSize += size;
        } else if (name.endsWith('.css')) {
          cssSize += size;
        }
      });
      
      console.log(`📦 Bundle sizes:`);
      console.log(`   JS: ${(jsSize / 1024).toFixed(2)}KB`);
      console.log(`   CSS: ${(cssSize / 1024).toFixed(2)}KB`);
      console.log(`   Total: ${(totalSize / 1024).toFixed(2)}KB`);
      
      // Check size targets (assuming gzipped will be ~30% smaller)
      const estimatedJsGzip = jsSize * 0.3;
      const estimatedCssGzip = cssSize * 0.3;
      
      if (estimatedJsGzip > 150 * 1024) {
        console.warn(`⚠️  JS bundle may exceed 150KB gzipped target`);
      }
      
      if (estimatedCssGzip > 50 * 1024) {
        console.warn(`⚠️  CSS bundle may exceed 50KB gzipped target`);
      }
    });
  }
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default (env, argv) => {
  const isProduction = argv.mode === 'production';

  return {
    // Multiple entry points as specified in PRD
    entry: {
      main: './src/js/main.js',
      vendor: './src/js/vendor.js',
      'performance-monitor': './src/js/features/performance-monitor.js',
      'lazy-load': './src/js/features/lazy-load.js',
      'mobile-nav': './src/js/features/mobile-nav.js'
    },

    // Output configuration with content hashing for production
    output: {
      path: path.resolve(__dirname, 'static/js'),
      filename: isProduction ? '[name].[contenthash:8].js' : '[name].js',
      clean: true,
      // Enable asset modules for better handling
      assetModuleFilename: 'assets/[name][ext][query]'
    },

    // Production vs development mode handling
    mode: isProduction ? 'production' : 'development',

    // Source maps: source-map for prod, eval-source-map for dev
    devtool: isProduction ? 'source-map' : 'eval-source-map',

    optimization: {
      minimize: isProduction,
      minimizer: [
        // Enhanced TerserPlugin for JavaScript minification
        new TerserPlugin({
          parallel: true,
          terserOptions: {
            compress: {
              drop_console: isProduction,
              drop_debugger: isProduction,
              pure_funcs: isProduction ? ['console.log', 'console.info', 'console.debug'] : [],
              passes: 2 // Multiple passes for better optimization
            },
            mangle: {
              safari10: true // Fix Safari 10 issues
            },
            format: {
              comments: false
            }
          },
          extractComments: false
        }),
        
        // CSS minification
        new CssMinimizerPlugin({
          parallel: true,
          minimizerOptions: {
            preset: [
              'default',
              {
                discardComments: { removeAll: true },
                normalizeWhitespace: true,
                colormin: true,
                minifyFontValues: { removeQuotes: false },
                calc: true
              }
            ]
          }
        })
      ],
      
      // Advanced code splitting for optimal caching
      splitChunks: {
        chunks: 'all',
        minSize: 20000,
        maxSize: 244000, // Split large chunks
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
      },
      
      // Enable module concatenation (scope hoisting)
      concatenateModules: isProduction,
      
      // Enable tree shaking for side-effect-free modules
      usedExports: isProduction,
      sideEffects: false
    },

    module: {
      rules: [
        {
          // Basic JS processing for modern browsers (ES2020+)
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: [
                ['@babel/preset-env', {
                  targets: {
                    browsers: ['> 1%', 'last 2 versions', 'not dead']
                  },
                  modules: false
                }]
              ],
              cacheDirectory: true,
              compact: isProduction
            }
          }
        },
        {
          // CSS/SCSS processing with MiniCssExtractPlugin
          test: /\.s?css$/,
          use: [
            isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
            {
              loader: 'css-loader',
              options: {
                sourceMap: !isProduction
              }
            },
            {
              loader: 'postcss-loader',
              options: {
                sourceMap: !isProduction,
                postcssOptions: {
                  plugins: [
                    'autoprefixer',
                    ...(isProduction ? ['cssnano'] : [])
                  ]
                }
              }
            }
          ]
        },
        {
          // Asset handling for images, fonts, etc.
          test: /\.(png|jpe?g|gif|svg|woff2?|eot|ttf|otf)$/,
          type: 'asset/resource'
        }
      ]
    },

    plugins: [
      // Build performance monitoring
      new BuildPerformancePlugin(),
      
      // CSS extraction with optimized configuration
      ...(isProduction ? [
        new MiniCssExtractPlugin({
          filename: '[name].[contenthash:8].css',
          chunkFilename: '[id].[contenthash:8].css',
          ignoreOrder: false // Enable to remove warnings about conflicting order
        }),
        
        // Gzip compression for production
        new CompressionPlugin({
          algorithm: 'gzip',
          test: /\.(js|css|html|svg)$/,
          threshold: 8192, // Only compress files larger than 8KB
          minRatio: 0.8,
          compressionOptions: {
            level: 9 // Maximum compression
          }
        })
      ] : []),
      
      // Bundle analyzer (conditional)
      ...(process.env.ANALYZE ? [
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: false,
          reportFilename: 'bundle-report.html'
        })
      ] : []),
      
      // Note: HtmlWebpackPlugin disabled for Django integration
    ],
    
    // Performance configuration
    performance: {
      maxEntrypointSize: isProduction ? 150000 : 250000, // 150KB for production
      maxAssetSize: isProduction ? 100000 : 200000,
      hints: isProduction ? 'error' : 'warning'
    },
    
    // Cache configuration for faster rebuilds
    cache: {
      type: 'filesystem',
      buildDependencies: {
        config: [__filename]
      }
    },
    
    // Development server configuration
    devServer: {
      static: {
        directory: path.join(__dirname, 'static')
      },
      compress: true,
      port: 3000,
      hot: true,
      open: false
    },
    
    // Resolve configuration
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
        '@css': path.resolve(__dirname, 'src/css'),
        '@js': path.resolve(__dirname, 'src/js')
      },
      extensions: ['.js', '.jsx', '.ts', '.tsx', '.json']
    }
  };
};