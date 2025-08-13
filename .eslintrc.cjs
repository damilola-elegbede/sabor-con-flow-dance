module.exports = {
  env: {
    browser: true,
    es2024: true,
    node: true,
    jest: true,
    serviceworker: true
  },
  extends: [
    'eslint:recommended',
    'prettier'
  ],
  plugins: [
    'prettier'
  ],
  parserOptions: {
    ecmaVersion: 2024,
    sourceType: 'module',
    ecmaFeatures: {
      impliedStrict: true
    }
  },
  globals: {
    // Build-time globals
    __DEV__: 'readonly',
    __PROD__: 'readonly',
    
    // Browser APIs that might not be detected
    IntersectionObserver: 'readonly',
    ResizeObserver: 'readonly',
    PerformanceObserver: 'readonly',
    
    // Service Worker globals
    self: 'readonly',
    clients: 'readonly',
    registration: 'readonly',
    skipWaiting: 'readonly',
    
    // Testing globals
    vitest: 'readonly',
    vi: 'readonly',
    describe: 'readonly',
    it: 'readonly',
    test: 'readonly',
    expect: 'readonly',
    beforeEach: 'readonly',
    afterEach: 'readonly',
    beforeAll: 'readonly',
    afterAll: 'readonly'
  },
  rules: {
    // Prettier integration
    'prettier/prettier': ['error', {
      singleQuote: true,
      semi: true,
      trailingComma: 'es5',
      tabWidth: 2,
      printWidth: 100
    }],
    
    // Error prevention
    'no-console': ['warn', { 
      allow: ['warn', 'error', 'info', 'group', 'groupEnd', 'time', 'timeEnd'] 
    }],
    'no-debugger': 'error',
    'no-alert': 'error',
    'no-eval': 'error',
    'no-implied-eval': 'error',
    'no-new-func': 'error',
    'no-script-url': 'error',
    'no-unused-vars': ['error', { 
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_',
      caughtErrorsIgnorePattern: '^_'
    }],
    'no-unreachable': 'error',
    'no-duplicate-imports': 'error',
    
    // Code quality
    'prefer-const': 'error',
    'no-var': 'error',
    'prefer-arrow-callback': 'error',
    'prefer-template': 'error',
    'template-curly-spacing': ['error', 'never'],
    'object-shorthand': 'error',
    'prefer-destructuring': ['error', {
      array: false,
      object: true
    }],
    
    // Performance
    'no-loop-func': 'error',
    'no-inner-declarations': 'error',
    
    // Modern JS
    'prefer-spread': 'error',
    'prefer-rest-params': 'error',
    'no-useless-concat': 'error',
    'no-useless-return': 'error',
    
    // Security
    'no-new-wrappers': 'error',
    'no-constructor-return': 'error',
    
    // Accessibility reminders
    'no-noninteractive-element-interactions': 'off', // Handled by JSX a11y in React projects
    
    // Build system specific
    'no-undef': 'error',
    'no-global-assign': 'error'
  },
  overrides: [
    {
      // Build scripts and Node.js files
      files: [
        'build-scripts/**/*.js',
        'scripts/**/*.js',
        '*.config.js',
        'vercel-build'
      ],
      env: {
        node: true,
        browser: false
      },
      rules: {
        'no-console': 'off' // Allow console in build scripts
      }
    },
    {
      // Test files
      files: [
        '**/*.test.js',
        '**/*.spec.js',
        '**/test-*.js',
        'accessibility-tests.js',
        'contrast-tests.js'
      ],
      env: {
        jest: true,
        node: true
      },
      rules: {
        'no-console': 'off' // Allow console in tests
      }
    },
    {
      // Service Worker files
      files: [
        '**/sw.js',
        '**/service-worker.js',
        '**/workbox-*.js'
      ],
      env: {
        serviceworker: true,
        browser: false,
        node: false
      },
      globals: {
        workbox: 'readonly',
        importScripts: 'readonly'
      }
    },
    {
      // Development and debugging files
      files: [
        '**/dev.js',
        '**/debug.js',
        '**/*-dev.js',
        '**/*-debug.js'
      ],
      rules: {
        'no-console': 'off',
        'no-debugger': 'warn'
      }
    }
  ]
};