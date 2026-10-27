import eslint from '@eslint/js';
import angular from 'angular-eslint';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  {
    ignores: ['src/app/generated/**', 'frontend/src/app/generated/**'],
  },
  {
    files: ['src/**/*.ts', 'frontend/src/**/*.ts'],
    extends: [
      eslint.configs.recommended,
      ...tseslint.configs.recommended,
      ...angular.configs.tsRecommended,
    ],
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    processor: angular.processInlineTemplates,
  },
  {
    files: ['src/**/*.html', 'frontend/src/**/*.html'],
    extends: [...angular.configs.templateRecommended, ...angular.configs.templateAccessibility],
  },
);
