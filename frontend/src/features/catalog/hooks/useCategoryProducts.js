import { useSuspenseQuery, skipToken } from '@tanstack/react-query'
import { fetchCategoryProducts } from '../api/productApi'

export const useCategoryProducts = (categoryId, params = {}) => {
	// Разрешаем запрос, если передана категория или если идет текстовый поиск
	const shouldFetch = categoryId || params.search

	return useSuspenseQuery({
		queryKey: ['categoryProducts', categoryId, params],
		// Если ничего нет, передаем skipToken,
		// чтобы хук "подождал" и не делал ошибочный запрос к бэкенду.
		queryFn: shouldFetch ? () => fetchCategoryProducts(categoryId, params) : skipToken,
		// Кэшируем на 5 минут
		staleTime: 5 * 60 * 1000,
	})
}
