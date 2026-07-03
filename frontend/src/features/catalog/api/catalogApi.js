import { apiClient } from '@/shared/api/apiClient'

/**
 * Получить товары по ID категории
 * @param {number} categoryId - ID категории (1 - Одежда, 2 - Обувь, 3 - Аксессуары)
 * @param {number} limit - Количество возвращаемых товаров
 */
export const getProductsByCategory = async (categoryId, limit = 4) => {
	const response = await apiClient.get(`/shop/categories/${categoryId}/products/`, {
		params: {
			limit, // Бэкенд (DRF) автоматически применит пагинацию и вернет только 4 товара
		},
	})
	// Так как ответ пагинирован (есть count, next, results),
	// нам для карточек нужен только массив results
	return response.data.results
}
