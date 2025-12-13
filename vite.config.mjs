import { defineConfig } from 'vite';
import { resolve } from 'path';
import compression from 'vite-plugin-compression';

export default defineConfig({
  // Base public path for assets
  base: '/static/',

  // Build configuration
  build: {
    // Output directory (Django's staticfiles will collect from here)
    outDir: 'static/dist',

    // Empty outDir before build
    emptyOutDir: true,

    // Generate manifest for Django integration
    manifest: true,

    // Generate source maps for production debugging
    sourcemap: true,

    // Minification settings
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },

    // CSS code splitting - keep CSS in single bundle for simplicity
    cssCodeSplit: false,

    // Asset handling
    assetsDir: 'assets',

    // Rollup options
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'static/js/app.js'),
      },
      output: {
        // Asset file names with content hash for cache busting
        entryFileNames: 'js/[name]-[hash].js',
        chunkFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const extType = assetInfo.name.split('.').pop();
          if (/css/i.test(extType)) {
            return 'css/[name]-[hash][extname]';
          }
          if (/woff2?|ttf|eot/i.test(extType)) {
            return 'fonts/[name][extname]';
          }
          if (/png|jpe?g|svg|gif|webp|ico/i.test(extType)) {
            return 'images/[name]-[hash][extname]';
          }
          return 'assets/[name]-[hash][extname]';
        },
      },
    },

    // Chunk size warning limit (in kB)
    chunkSizeWarningLimit: 500,
  },

  // Plugins
  plugins: [
    // Gzip compression
    compression({
      algorithm: 'gzip',
      ext: '.gz',
    }),
    // Brotli compression
    compression({
      algorithm: 'brotliCompress',
      ext: '.br',
    }),
  ],

  // CSS configuration
  css: {
    devSourcemap: true,
  },

  // Resolve configuration
  resolve: {
    alias: {
      '@': resolve(__dirname, 'static'),
    },
  },
});
