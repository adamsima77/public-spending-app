export default {
  'frontend/**/*.{ts,html}': [
    'frontend/node_modules/.bin/eslint --fix --no-warn-ignored --config frontend/eslint.config.js',
    'frontend/node_modules/.bin/prettier --write --config frontend/.prettierrc',
  ],
  'frontend/**/*.{css,json}': [
    'frontend/node_modules/.bin/prettier --write --config frontend/.prettierrc',
  ],

  'backend/**/*.php': ['backend/vendor/bin/pint --config backend/pint.json'],

  'etl/**/*.py': [
    'etl/.venv/bin/ruff check --fix --config etl/pyproject.toml',
    'etl/.venv/bin/ruff format --config etl/pyproject.toml',
  ],
};
