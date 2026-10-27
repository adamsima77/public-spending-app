export default {
  'frontend/**/*.{ts,html}': [
    'npx eslint --fix --config frontend/eslint.config.js',
    'npx prettier --write --config frontend/.prettierrc',
  ],

  'frontend/**/*.{css,json}': [
    'npx prettier --write --config frontend/.prettierrc',
  ],

  'backend/**/*.php': (files) =>
    `php backend/vendor/bin/pint ${files.map((file) => `"${file}"`).join(' ')}`,

  'etl/**/*.py': [
    'ruff check --fix',
    'ruff format',
  ],
};