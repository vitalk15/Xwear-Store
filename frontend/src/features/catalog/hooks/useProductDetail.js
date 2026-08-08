import { useSuspenseQuery, skipToken } from '@tanstack/react-query'
import { fetchProductDetail } from '../api/productApi'

export const useProductDetail = (productId) => {
	return useSuspenseQuery({
		// Уникальный ключ кэша для конкретного товара
		queryKey: ['productDetail', productId],

		// Если productId передан — делаем запрос. Если нет — ждем (skipToken).
		// Это защищает бэкенд от ошибочных запросов вида /shop/products/undefined/
		queryFn: productId ? () => fetchProductDetail(productId) : skipToken,

		// Детальная информация о товаре меняется не часто,
		// поэтому кэшируем на 5 минут
		staleTime: 5 * 60 * 1000,
	})
}
