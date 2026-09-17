import apiClient from '@/shared/api/apiClient'

export const profileApi = {
	getProfile: async () => {
		const response = await apiClient.get('/auth/profile/')
		return response.data
	},

	updateProfile: async (data) => {
		const profilePayload = {}

		if ('first_name' in data) profilePayload.first_name = data.first_name
		if ('last_name' in data) profilePayload.last_name = data.last_name
		if ('phone' in data) {
			profilePayload.phone = data.phone ? data.phone.replace(/[\s()-]/g, '') : ''
		}

		const response = await apiClient.patch('/auth/profile/', {
			profile: profilePayload,
		})
		return response.data
	},

	// Получение списка городов, доступных для доставки
	getCities: async () => {
		const response = await apiClient.get('/core/cities/')
		return response.data
	},

	// Добавление нового адреса пользователя
	createAddress: async (addressData) => {
		const response = await apiClient.post('/auth/addresses/', {
			city_id: addressData.city_id,
			street: addressData.street,
			house: addressData.house,
			apartment: addressData.apartment || null,
		})
		return response.data
	},
}
