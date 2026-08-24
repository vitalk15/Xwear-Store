import apiClient from '@/shared/api/apiClient'

/**
 * Получить список товаров для конкретной категории с учетом фильтрации и пагинации
 * @param {string|number} categoryId - ID категории (например, 1 - одежда, 2 - обувь)
 * @param {Object} [params={}] - GET-параметры запроса (Query parameters) для фильтрации
 * @param {number} [params.limit] - Количество товаров на страницу (LimitOffsetPagination)
 * @param {number} [params.offset] - Смещение для пагинации
 * @param {string} [params.brands] - Выбранные бренды через запятую (например, "nike,adidas")
 * @param {string} [params.sizes] - Выбранные размеры через запятую (например, "41,42")
 * @param {string} [params.colors] - Выбранные цвета через запятую (например, "red,black")
 * @param {string|number} [params.min_price] - Минимальная цена
 * @param {string|number} [params.max_price] - Максимальная цена
 * @param {string} [params.sort] - Параметр сортировки (например, "price" или "-price")
 * @param {string} [params.search] - Текстовый запрос для поиска (например, "nike")
 * @returns {Promise<Object>} Объект ответа DRF { count, next, previous, results: [], category: {}, filters: {} }
 */
export const fetchCategoryProducts = async (categoryId, params = {}) => {
	// Динамически определяем эндпоинт
	const endpoint = categoryId
		? `/shop/categories/${categoryId}/products/`
		: '/shop/products/'

	const { data } = await apiClient.get(endpoint, {
		params,
	})

	return data
}

/**
 * Получить укороченный список товаров по ID категории (используется для блоков на главной странице)
 * Бэкенд (DRF) автоматически применит пагинацию, но функция вернет только массив товаров (results).
 * @param {string|number} categoryId - ID категории (1 - Одежда, 2 - Обувь, 3 - Аксессуары)
 * @param {number} [limit=4] - Количество возвращаемых товаров (по умолчанию 4)
 * @returns {Promise<Array>} Массив объектов товаров (извлеченный из data.results)
 */
export const getProductsByCategory = async (categoryId, limit = 4) => {
	const response = await apiClient.get(`/shop/categories/${categoryId}/products/`, {
		params: {
			limit, // Бэкенд (DRF) автоматически применит пагинацию и вернет только 4 товара
		},
	})
	// Возвращаем только массив результатов, отбрасывая count, next и previous
	return response.data.results
}

/**
 * Получить детальную информацию о конкретном товаре по его ID
 * @param {string|number} productId - ID товара (например, "60")
 * @returns {Promise<Object>} Объект с полными данными товара (включая галерею, варианты, размеры)
 */
export const fetchProductDetail = async (productId) => {
	const { data } = await apiClient.get(`/shop/products/${productId}/`)
	return data
}

/**
 * Получить список рекомендованных товаров (похожих предложений) для конкретного варианта товара
 * @param {string|number} productId - ID текущего варианта товара
 * @returns {Promise<Array>} Массив объектов товаров для ленты рекомендаций
 */
export const getProductRecommends = async (productId) => {
	const response = await apiClient.get(`/shop/products/${productId}/recommends/`)
	return response.data
}
