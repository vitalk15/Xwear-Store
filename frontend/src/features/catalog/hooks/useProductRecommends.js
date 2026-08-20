import { useSuspenseQuery, skipToken } from '@tanstack/react-query'
import { getProductRecommends } from '../api/productApi'

/**
 * Хук для получения списка рекомендованных товаров
 * @param {string|number} productId - ID текущего товара
 */
export const useProductRecommends = (productId) => {
	return useSuspenseQuery({
		queryKey: ['recommends', productId],
		// Если productId есть — делаем запрос. Если нет — передаем skipToken
		queryFn: productId ? () => getProductRecommends(productId) : skipToken,
		staleTime: 5 * 60 * 1000, // Кэшируем на 5 минут
	})
}
