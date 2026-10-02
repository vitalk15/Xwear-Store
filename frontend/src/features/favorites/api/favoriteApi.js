import apiClient from '@/shared/api/apiClient'

/**
 * Получить список избранных товаров пользователя
 * @returns {Promise<Array>} Массив объектов [{ id, variant, variant_details, created_at }]
 */
export const fetchFavorites = async () => {
	const { data } = await apiClient.get('/shop/favorites/')
	return data
}

/**
 * Переключить состояние "в избранном" для варианта товара
 * @param {number|string} variantId - ID варианта товара (ProductVariant pk)
 * @returns {Promise<Object>}
 */
export const toggleFavorite = async (variantId) => {
	const { data } = await apiClient.post(`/shop/favorites/toggle/${variantId}/`)
	return data
}
