import apiClient from '@/shared/api/apiClient'

export const profileApi = {
	getProfile: async () => {
		const response = await apiClient.get('/auth/profile/')
		return response.data
	},

	updateProfile: async (data) => {
		// ВАЖНО: бэкенд ждет вложенный объект profile внутри UserSerializer
		const response = await apiClient.patch('/auth/profile/', {
			profile: {
				first_name: data.first_name,
				last_name: data.last_name,
				phone: data.phone ? data.phone.replace(/[\s()-]/g, '') : '',
			},
		})
		return response.data
	},
}
