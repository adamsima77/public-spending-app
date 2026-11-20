export default {
  extends: ['stylelint-config-standard-scss', 'stylelint-config-prettier-scss'],
  plugins: ['stylelint-order'],
  ignoreFiles: [
    'dist/**',
    '.angular/**',
    'node_modules/**',
    'src/app/generated/**',
    'src/styles/_theme-colors.scss',
  ],
  rules: {
    'no-empty-source': null,
    'selector-pseudo-element-no-unknown': [true, { ignorePseudoElements: ['ng-deep'] }],
    'selector-pseudo-class-no-unknown': [true, { ignorePseudoClasses: ['host', 'host-context'] }],
    'declaration-no-important': true,
    'selector-class-pattern': null,
    'selector-max-id': 0,
    'max-nesting-depth': [3, { ignoreAtRules: ['include', 'media'] }],
    'order/properties-alphabetical-order': true,
  },
};
