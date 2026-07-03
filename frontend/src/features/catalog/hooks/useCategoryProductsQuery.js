import { useSuspenseQuery } from '@tanstack/react-query'
import { getProductsByCategory } from '../api/catalogApi'

export const useCategoryProductsQuery = (categoryId, limit = 4) => {
	return useSuspenseQuery({
		// Ключ кэша уникален для каждой категории и лимита
		queryKey: ['products', 'category', categoryId, limit],
		queryFn: () => getProductsByCategory(categoryId, limit),
		// Товары на главной не нужно переспрашивать слишком часто,
		// данные могут спокойно жить в кэше пару минут
		staleTime: 1000 * 60 * 2,
	})
}
