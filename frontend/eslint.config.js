import js from '@eslint/js';
import globals from 'globals';

export default [
  {
    files: ['src/**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.es2021,
        ...globals.node
      },
      parserOptions: {
        ecmaFeatures: {
          jsx: true
        }
      }
    },
    plugins: [],
    rules: {
      ...js.configs.recommended.rules,
      // Add any custom rules here
      'semi': ['error', 'always'],
      'quotes': ['error', 'single']
    }
  }
];