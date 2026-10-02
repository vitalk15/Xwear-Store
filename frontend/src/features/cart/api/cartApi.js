import apiClient from '@/shared/api/apiClient'

export const cartApi = {
	// Получить корзину
	getCart: async () => {
		const { data } = await apiClient.get('/orders/cart/')
		return data
	},

	// Добавить товар (payload: { product_size: number, quantity?: number })
	addToCart: async (payload) => {
		const { data } = await apiClient.post('/orders/cart/add/', payload)
		return data
	},

	// Запрос на изменение количества товара
	updateCartItem: async ({ id, quantity }) => {
		const { data } = await apiClient.patch(`/orders/cart/item/${id}/`, { quantity })
		return data
	},

	// Запрос на удаление позиции
	removeCartItem: async (id) => {
		await apiClient.delete(`/orders/cart/item/${id}/delete/`)
		// Бэкенд возвращает 204 No Content, поэтому data не ждем
	},
}
