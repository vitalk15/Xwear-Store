import axios from 'axios'

export const apiClient = axios.create({
	// Vite автоматически подхватит VITE_API_URL из .env файла
	baseURL: import.meta.env.VITE_API_URL,
})
