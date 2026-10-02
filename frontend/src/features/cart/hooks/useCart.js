import {
	useQuery,
	useSuspenseQuery,
	useMutation,
	useQueryClient,
} from '@tanstack/react-query'
import { cartApi } from '../api/cartApi'

export const cartKeys = {
	cart: ['cart'],
}

/**
 * Хук для получения данных корзины (стандартный).
 * Подходит для фонового запроса данных (например, для счетчика в шапке),
 * где мы можем управлять флагом enabled в зависимости от авторизации.
 *
 * @param {boolean} isAuthenticated - Флаг авторизации пользователя
 * @returns {import('@tanstack/react-query').UseQueryResult} Результат запроса (данные корзины, статус загрузки и ошибки)
 */
export const useCartQuery = (isAuthenticated) => {
	return useQuery({
		queryKey: cartKeys.cart,
		queryFn: cartApi.getCart,
		enabled: isAuthenticated, // Запрашиваем только если юзер залогинен
		staleTime: 5 * 60 * 1000, // Кэшируем на 5 минут
	})
}

/**
 * Хук для получения данных корзины с поддержкой React Suspense.
 * Подходит для страницы корзины (CartPage), где корзина — основной контент.
 * Внимание: Не имеет опции `enabled`. Компонент должен рендериться только для авторизованных.
 *
 * @returns {import('@tanstack/react-query').UseSuspenseQueryResult} Гарантированный результат запроса корзины
 */
export const useSuspenseCartQuery = () => {
	return useSuspenseQuery({
		queryKey: cartKeys.cart,
		queryFn: cartApi.getCart,
		staleTime: 5 * 60 * 1000,
	})
}

/**
 * Хук для добавления товара (конкретного размера/варианта) в корзину.
 * При успехе инвалидирует кэш корзины, заставляя React Query перезапросить актуальные данные.
 *
 * @returns {import('@tanstack/react-query').UseMutationResult} Мутация для добавления товара
 */
export const useAddToCartMutation = () => {
	const queryClient = useQueryClient()

	return useMutation({
		mutationFn: cartApi.addToCart,
		onSuccess: (updatedCart) => {
			// Бэкенд вернул свежую корзину - сразу обновляем кэш!
			queryClient.setQueryData(cartKeys.cart, updatedCart)
		},
	})
}

/**
 * Хук для изменения количества товара в корзине.
 * Ожидает, что бэкенд возвращает обновленный объект корзины при PATCH-запросе,
 * и сразу обновляет кэш (setQueryData) без лишних сетевых запросов.
 *
 * @returns {import('@tanstack/react-query').UseMutationResult} Мутация для обновления количества
 */
export const useUpdateCartItemMutation = () => {
	const queryClient = useQueryClient()

	return useMutation({
		mutationFn: cartApi.updateCartItem,
		onSuccess: (updatedCart) => {
			// Бэкенд при PATCH возвращает обновленную корзину — сразу кладем в кэш!
			queryClient.setQueryData(cartKeys.cart, updatedCart)
		},
	})
}

/**
 * Хук для удаления товара из корзины.
 * При успехе инвалидирует кэш корзины для её полного обновления.
 *
 * @returns {import('@tanstack/react-query').UseMutationResult} Мутация для удаления позиции
 */
export const useRemoveCartItemMutation = () => {
	const queryClient = useQueryClient()

	return useMutation({
		mutationFn: cartApi.removeCartItem,
		onSuccess: () => {
			// При удалении бэкенд не возвращает корзину (204),
			// поэтому мы просто просим React Query перезапросить её заново
			queryClient.invalidateQueries({ queryKey: cartKeys.cart })
		},
	})
}
