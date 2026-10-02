import { QueryClient } from '@tanstack/react-query'

// Глобальный экземпляр клиента
export const queryClient = new QueryClient({
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
