import axios from 'axios'
import useErrorStore from '@/shared/store/useErrorStore'

const apiClient = axios.create({
	// Vite автоматически подхватит VITE_API_URL из .env файла
	baseURL: import.meta.env.VITE_API_URL,
	timeout: 10000, // 10 секунд
})

// Перехватчик (interceptor), который при критических ошибках заполняет Zustand-стор
apiClient.interceptors.response.use(
	(response) => response,
	(error) => {
		const setError = useErrorStore.getState().setError

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
