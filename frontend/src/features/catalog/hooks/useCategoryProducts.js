import { useSuspenseQuery } from '@tanstack/react-query'
import { fetchCategoryProducts } from '../api/productApi'

export const useCategoryProducts = (categoryId, params = {}) => {
	return useSuspenseQuery({
		queryKey: ['categoryProducts', categoryId, params],

		// Если categoryId === null, API-функция сама сделает запрос на глобальный эндпоинт /shop/products/
		queryFn: () => fetchCategoryProducts(categoryId, params),
		// Кэшируем на 5 минут
		staleTime: 5 * 60 * 1000,
	})
}
