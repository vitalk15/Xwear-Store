import { useSuspenseQuery, skipToken } from '@tanstack/react-query'
import { fetchCategoryProducts } from '../api/productApi'

export const useCategoryProducts = (categoryId, params = {}) => {
	return useSuspenseQuery({
		queryKey: ['categoryProducts', categoryId, params],
		// Если categoryId есть — делаем запрос. Если нет — передаем skipToken,
		// чтобы хук "подождал" и не делал ошибочный запрос к бэкенду.
		queryFn: categoryId ? () => fetchCategoryProducts(categoryId, params) : skipToken,
		// Кэшируем на 5 минут
		staleTime: 5 * 60 * 1000,
	})
}
