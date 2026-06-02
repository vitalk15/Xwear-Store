import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
	plugins: [react()], // подключает официальный плагин @vitejs/plugin-react (отвечает за JSX Transformation и Fast Refresh (HMR))
	css: {
		preprocessorOptions: {
			scss: {
				// Автоматически внедряет указанные файлы во все ваши .scss и .module.scss файлы.
				// Больше не нужно вручную писать @use во всех компонентах!
				additionalData: `
          @use "@/assets/styles/_constants.scss" as *;
          @use "@/assets/styles/_functions.scss" as *;
        `,
			},
		},
	},
	resolve: {
		alias: {
			// Настройка удобного алиаса '@', чтобы не писать выходы из папок '../../../../'
			'@': '/src',
		},
	},
})
