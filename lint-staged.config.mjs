import path from 'node:path';

const rel = (dir, files) =>
  files.map((f) => path.relative(path.resolve(dir), f)).join(' ');

export default {
  'frontend/**/*.{ts,html}': (files) => [
    `cd frontend && npx eslint --fix ${rel('frontend', files)}`,
    `cd frontend && npx prettier --write ${rel('frontend', files)}`,
  ],
  'frontend/**/*.{css,json}': (files) =>
    `cd frontend && npx prettier --write ${rel('frontend', files)}`,

  'backend/**/*.php': (files) =>
    `cd backend && vendor/bin/pint ${rel('backend', files)}`,

  'etl/**/*.py': ['ruff check --fix', 'ruff format'],
};