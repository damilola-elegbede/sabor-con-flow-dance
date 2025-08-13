module.exports = {
  extends: [
    'stylelint-config-standard'
  ],
  plugins: [],
  rules: {
    // Disable problematic rules for existing CSS
    'unit-disallowed-list': null,
    'unit-allowed-list': null,
    'property-no-vendor-prefix': null,
    'value-no-vendor-prefix': null,
    'color-function-notation': null,
    'alpha-value-notation': null,
    'media-feature-range-notation': null,
    'selector-pseudo-element-colon-notation': null,
    'font-weight-notation': null,
    'no-duplicate-selectors': null, // Allow duplicates for now
    
    // Keep essential rules
    'color-no-invalid-hex': true,
    'unit-no-unknown': true,
    'property-no-unknown': true,
    'selector-pseudo-class-no-unknown': true,
    'selector-pseudo-element-no-unknown': true,
    'at-rule-no-unknown': [true, {
      ignoreAtRules: [
        'tailwind',
        'apply',
        'variants',
        'responsive',
        'screen',
        'layer',
        'define-mixin',
        'mixin'
      ]
    }],
    
    // Accessibility
    'no-descending-specificity': null // Allow for now
  },
  overrides: [
    {
      // Allow all units in vendor CSS and existing files
      files: [
        '**/vendor/**/*.css',
        '**/node_modules/**/*.css',
        'static/css/styles.css'
      ],
      rules: {
        'unit-disallowed-list': null,
        'property-no-vendor-prefix': null,
        'value-no-vendor-prefix': null,
        'at-rule-no-unknown': null,
        'selector-class-pattern': null,
        'selector-id-pattern': null
      }
    }
  ]
};