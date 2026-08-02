import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import svgr from 'vite-plugin-svgr'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
	plugins: [
		react(),
		svgr({
			svgrOptions: {
				exportType: 'default', // позволяет писать import CrossIcon ... вместо import { ReactComponent as CrossIcon } ...
				ref: true, // если нужно будет анимировать иконку через сложные библиотеки (например, Framer Motion или GSAP) - даёт доступ к DOM-элементу <svg>
				svgo: false, // SVGO — это встроенный минификатор (оптимизатор) SVG-кода. Он удаляет из SVG лишние пробелы, комментарии и неиспользуемые теги. Часто бывает слишком агрессивным и может удалить или изменить то, что не следовало бы.
				titleProp: true, // Добавляет иконке поддержку пропса title (если нужно для SEO и скринридеров)
			},
			include: '**/*.svg', // избавляет от необходимости писать суфикс ?react в импортах: import Icon from './icon.svg?react'
		}),
	], // подключает плагины: официальный плагин @vitejs/plugin-react (отвечает за JSX Transformation и Fast Refresh (HMR)), плагин для использования svg-иконок как компоненты
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
