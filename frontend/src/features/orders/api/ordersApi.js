import apiClient from '@/shared/api/apiClient'

export const ordersApi = {
	// Получение списка городов для доставки
	getCities: async () => {
		const response = await apiClient.get('core/cities/')
		return response.data
	},

	// Получение настроек доставки (порог бесплатной доставки и условия)
	getCommercialConfig: async () => {
		const response = await apiClient.get('core/commercial-info/')
		return response.data
	},

	// Получение списка пунктов выдачи (ПВЗ)
	getPickupPoints: async () => {
		const response = await apiClient.get('/orders/pickup-points/')
		return response.data
	},

	// Создание нового заказа
	createOrder: async (orderData) => {
		const response = await apiClient.post('/orders/checkout/', orderData)
		return response.data
	},

	// Получение всех заказов текущего пользователя
	getOrders: async () => {
		const response = await apiClient.get('/orders/list/')
		return response.data
	},
}
