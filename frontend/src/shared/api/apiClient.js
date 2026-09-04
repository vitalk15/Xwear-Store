import axios from 'axios'
import useErrorStore from '@/shared/store/useErrorStore'
import useAuthStore from '@/features/auth/store/useAuthStore'

const apiClient = axios.create({
	// Vite автоматически подхватит VITE_API_URL из .env файла
	baseURL: import.meta.env.VITE_API_URL,
	timeout: 10000, // 10 секунд
})

// --- Interceptors ---

// 1. Перехватчик ЗАПРОСОВ: Автоматически добавляем Bearer access-токен из Zustand
apiClient.interceptors.request.use(
	(config) => {
		// В Zustand можно обращаться к состоянию вне React-компонентов через getState()
		const token = useAuthStore.getState().access

		if (token) {
			config.headers.Authorization = `Bearer ${token}`
		}

		return config
	},
	(error) => Promise.reject(error),
)

// 2. Перехватчик ОТВЕТОВ: Обработка 401 (Refresh token) + глобальные ошибки (500, 429, Network)
apiClient.interceptors.response.use(
	(response) => response, // Если запрос успешен — просто возвращаем ответ
	async (error) => {
		const originalRequest = error.config
		const setError = useErrorStore.getState().setError

		// А) Логика обновления access-токена при 401 Unauthorized
		// Если сервер вернул 401 и мы еще не пробовали повторить запрос (_isRetry)
		if (error.response?.status === 401 && !originalRequest._isRetry) {
			// Исключаем роуты логина и самого рефреша, чтобы не уйти в бесконечный цикл
			const isAuthRoute =
				originalRequest.url?.includes('/auth/token/') ||
				originalRequest.url?.includes('/auth/token/refresh/')

			if (!isAuthRoute) {
				originalRequest._isRetry = true // Ставим флаг, что это повторная попытка. Без него, если эндпоинт рефреша сломается и тоже вернет 401, приложение уйдёт в бесконечный цикл запросов.

				try {
					// Запрашиваем новый access-токен. Обязательно с withCredentials для отправки HttpOnly куки!
					// Браузер сам прикрепит HttpOnly куку
					const response = await apiClient.post('/auth/token/refresh/', null, {
						withCredentials: true,
					})
					const newAccess = response.data.access

					// Сохраняем новый токен в Zustand (без потери данных о пользователе)
					const currentUser = useAuthStore.getState().user
					useAuthStore.getState().setAuth({
						user: currentUser,
						access: newAccess,
					})

					// Обновляем заголовок авторизации и повторяем исходный запрос
					originalRequest.headers.Authorization = `Bearer ${newAccess}`
					return apiClient(originalRequest)
				} catch (refreshError) {
					// Если refresh-токен невалиден или истёк — сбрасываем состояние авторизации
					useAuthStore.getState().logout()
					return Promise.reject(refreshError)
				}
			}
		}

		// Б) Логика обработки критических ошибок сервера и сети
		if (!error.response) {
			// Если сервер недоступен вообще (Network Error)
			setError({ statusCode: 'NETWORK_ERROR' })
		} else {
			const status = error.response.status
			if ([429, 500, 502, 503, 504].includes(status)) {
				setError({ statusCode: status })
			}
		}

		return Promise.reject(error)
	},
)

export default apiClient
