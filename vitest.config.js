import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    // Environment configuration for build system tests
    environment: 'node',
    
    // Test file locations for build system tests
    include: [
      'tests/build/**/*.test.js',
      'tests/unit/**/*.test.js',
      'tests/integration/**/*.test.js'
    ],
    
    // Exclude patterns
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/cypress/**',
      '**/.{idea,git,cache,output,temp}/**'
    ],
    
    // Global test configuration
    globals: true,
    
    // Coverage configuration
    coverage: {
      // Coverage reporters
      reporter: ['text', 'json', 'html'],
      
      // Include coverage for build scripts
      include: [
        'build-scripts/**/*.js',
        'src/**/*.js'
      ],
      
      // Exclude patterns from coverage
      exclude: [
        'node_modules/**',
        'dist/**',
        'staticfiles/**',
        'static/**',
        'tests/**',
        'coverage/**',
        '**/*.config.js',
        '**/*.test.js'
      ],
      
      // Coverage thresholds
      thresholds: {
        global: {
          branches: 75,
          functions: 75,
          lines: 80,
          statements: 80
        }
      },
      
      // Output directory for coverage reports
      reportsDirectory: './coverage',
      
      // Clean coverage directory before running tests
      clean: true
    },
    
    // Test timeout configuration
    testTimeout: 10000,
    
    // Setup files (exclude for build system tests to avoid DOM dependencies)
    setupFiles: [],
    
    // Test environment options
    environmentOptions: {
      // Node-specific options for build system tests
      node: {
        // Enable experimental modules
        experimentalModules: true
      }
    },
    
    // Reporters configuration
    reporters: ['verbose'],
    
    // Use single-threaded execution for build tests (avoid process.chdir issues)
    pool: 'forks',
    poolOptions: {
      forks: {
        singleFork: true
      }
    }
  },
  
  // Resolve configuration for ES modules
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@build': path.resolve(__dirname, './build-scripts'),
      '@static': path.resolve(__dirname, './static'),
      '@dist': path.resolve(__dirname, './dist')
    }
  },
  
  // Define configuration for better compatibility
  define: {
    __TEST__: true
  }
});