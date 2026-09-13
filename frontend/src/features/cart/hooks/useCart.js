import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { cartApi } from '../api/cartApi'

export const cartKeys = {
	cart: ['cart'],
}

// !!! Todo: добавить useSuspenseQuery?

// Хук для получения корзины
export const useCartQuery = (isAuthenticated) => {
	return useQuery({
		queryKey: cartKeys.cart,
		queryFn: cartApi.getCart,
		enabled: isAuthenticated, // Запрашиваем только если юзер залогинен
		staleTime: 5 * 60 * 1000,
	})
}

// Хук для добавления товара
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

// Хук для изменения количества товара
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

// Хук для удаления товара
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
