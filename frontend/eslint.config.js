import { FlatCompat } from '@eslint/eslintrc';
import path from 'path';
import { fileURLToPath } from 'url';
import js from '@eslint/js';
import globals from 'globals';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended
});

export default [
  js.configs.recommended,
  ...compat.extends('plugin:react/recommended', 'plugin:react/jsx-runtime'),
  {
    files: ['src/**/*.{js,jsx}', '*.{js,jsx}'],
    ignores: ['dist/**'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.es2021,
        ...globals.node,
        document: 'readonly',
        window: 'readonly',
        console: 'readonly',
        localStorage: 'readonly',
        fetch: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        queueMicrotask: 'readonly',
        setImmediate: 'readonly',
        MessageChannel: 'readonly',
        navigator: 'readonly',
        performance: 'readonly',
        MSApp: 'readonly',
        reportError: 'readonly',
        __REACT_DEVTOOLS_GLOBAL_HOOK__: 'readonly'
      },
      parserOptions: {
        ecmaFeatures: {
          jsx: true
        }
      }
    },
    settings: {
      react: {
        version: 'detect'
      }
    },
    rules: {
      'semi': ['error', 'always'],
      'quotes': ['error', 'single'],
      'no-unused-vars': ['error', {
        'args': 'after-used',
        'ignoreRestSiblings': true,
        'varsIgnorePattern': '^(React|_)',
        'argsIgnorePattern': '^_'
      }],
      'no-empty': ['error', { 'allowEmptyCatch': true }],
      'no-constant-condition': ['error', { 'checkLoops': false }],
      'no-control-regex': 'off',
      'no-prototype-builtins': 'off',
      'no-misleading-character-class': 'off',
      'no-useless-escape': 'off',
      'no-cond-assign': ['error', 'except-parens'],
      'getter-return': 'off',
      'no-func-assign': 'off',
      'react/react-in-jsx-scope': 'off',
      'react/prop-types': 'off',
      'react/display-name': 'off'
    }
  }
];