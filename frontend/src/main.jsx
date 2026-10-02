import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from './shared/api/queryClient'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import App from './App.jsx'
import '@/assets/styles/global.scss'

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
