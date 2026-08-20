import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import App from './App.jsx'
import '@/assets/styles/global.scss'

// 1. Создаем глобальный экземпляр клиента
const queryClient = new QueryClient({
	defaultOptions: {
		queries: {
			// Отключаем автоматический повторный запрос при возвращении на вкладку браузера
			// (чтобы сервер не дергался каждый раз, когда вы переключаетесь между окнами)
			refetchOnWindowFocus: false,

			// Если сервер ответил ошибкой, делаем только 1 повторную попытку (по умолчанию их 3)
			retry: 1,
		},
	},
})

createRoot(document.getElementById('root')).render(
	<StrictMode>
		{/* 2. Оборачиваем App в провайдер и передаем ему клиента */}
		<QueryClientProvider client={queryClient}>
			<App />

			{/* 3. Добавляем панель разработчика (она сама скроется в production-сборке) */}
			<ReactQueryDevtools initialIsOpen={false} />
		</QueryClientProvider>
	</StrictMode>,
)
