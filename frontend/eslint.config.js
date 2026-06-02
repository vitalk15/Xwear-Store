import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
	globalIgnores(['dist']), // не проверять папку dist (куда собирается готовый сайт)
	{
		files: ['**/*.{js,jsx}'],
		extends: [
			js.configs.recommended, // базовый набор правил JavaScript
			reactHooks.configs.flat.recommended, // следит, чтобы правильно использовались хуки
			reactRefresh.configs.vite, // следит за тем, чтобы компоненты были написаны экспортируемыми функциями (чистыми компонентами)
		],
		languageOptions: {
			ecmaVersion: 2020,
			globals: globals.browser,
			parserOptions: {
				ecmaVersion: 'latest',
				ecmaFeatures: { jsx: true },
				sourceType: 'module',
			},
		},
		rules: {
			'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]' }], // не будет ругаться на неиспользованные переменные, если они начинаются с заглавной буквы или нижнего подчеркивания
		},
	},
])
