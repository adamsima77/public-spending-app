export default {
  'frontend/**/*.{ts,html}': [
    'frontend/node_modules/.bin/eslint --fix --config frontend/eslint.config.js',
    'frontend/node_modules/.bin/prettier --write --config frontend/.prettierrc',
  ],

  'frontend/**/*.{css,json}': [
    'frontend/node_modules/.bin/prettier --write --config frontend/.prettierrc',
  ],

  'backend/**/*.php': ['php backend/vendor/bin/pint'],
};
