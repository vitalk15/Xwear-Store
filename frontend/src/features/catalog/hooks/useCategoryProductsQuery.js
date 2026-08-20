import { useSuspenseQuery } from '@tanstack/react-query'
import { getProductsByCategory } from '../api/productApi'

// укороченный список товаров (используется для блоков на главной странице)
export const useCategoryProductsQuery = (categoryId, limit = 4) => {
	return useSuspenseQuery({
		// Ключ кэша уникален для каждой категории и лимита
		queryKey: ['products', 'category', categoryId, limit],
		queryFn: () => getProductsByCategory(categoryId, limit),
		// Товары на главной не нужно переспрашивать слишком часто,
		// данные могут спокойно жить в кэше пять минут
		staleTime: 5 * 60 * 1000,
	})
}
