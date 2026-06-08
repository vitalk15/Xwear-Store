import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
	plugins: [react()], // подключает официальный плагин @vitejs/plugin-react (отвечает за JSX Transformation и Fast Refresh (HMR))
	css: {
		preprocessorOptions: {
			scss: {
				additionalData: (content, resolvePath) => {
					// Если Vite обрабатывает базовые файлы утилит, отдаем их как есть, без инъекций
					if (
						resolvePath.includes('_variables.scss') ||
						resolvePath.includes('_functions.scss') ||
						resolvePath.includes('_mixins.scss')
					) {
						return content
					}

					// Во все остальные файлы (например, *.module.scss) автоматически внедряем утилиты
					return `
            @use "@/assets/styles/_variables.scss" as *;
            @use "@/assets/styles/_functions.scss" as *;
            @use "@/assets/styles/_mixins.scss" as *;
            ${content}
          `
				},
			},
		},
		devSourcemap: true, // Включает карты кода для стилей в режиме разработки
	},
	resolve: {
		alias: {
			// Настройка удобного алиаса '@', чтобы не писать выходы из папок '../../../../'
			// fileURLToPath превращает URL в абсолютный путь файловой системы
			// '@': '/src',
			'@': fileURLToPath(new URL('./src', import.meta.url)),
		},
	},
})
