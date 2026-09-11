import {
	useSuspenseQuery,
	useQuery,
	useMutation,
	useQueryClient,
} from '@tanstack/react-query'
import { fetchFavorites, toggleFavorite } from '../api/favoriteApi'
import useAuthStore from '@/features/auth/store/useAuthStore'

export const FAVORITES_QUERY_KEY = ['favorites']

/**
 * Хук для получения списка избранного (с поддержкой Suspense)
 */
export const useFavorites = () => {
	return useSuspenseQuery({
		queryKey: FAVORITES_QUERY_KEY,
		queryFn: fetchFavorites,
		staleTime: 5 * 60 * 1000,
	})
}

/**
 * Хук для безопасной проверки статуса избранного вне Suspense (например, в ProductCard)
 */
export const useFavoritesCheck = () => {
	const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

	const { data: rawData = [] } = useQuery({
		queryKey: FAVORITES_QUERY_KEY,
		queryFn: fetchFavorites,
		enabled: isAuthenticated, // Запрос идет только для авторизованных
		staleTime: 5 * 60 * 1000,
	})

	// Если юзер не авторизован, принудительно используем пустой массив,
	// даже если в кэше React Query что-то осталось от предыдущей сессии.
	const favorites = isAuthenticated ? rawData : []

	// Вспомогательная функция проверки: находится ли вариант товара в избранном
	const isFavorite = (variantId) => {
		return favorites.some((fav) => fav.variant === variantId)
	}

	return { favorites, isFavorite }
}

/**
 * Мутация переключения избранного с Optimistic UI
 */
export const useToggleFavoriteMutation = () => {
	const queryClient = useQueryClient()

	return useMutation({
		mutationFn: toggleFavorite,
		onMutate: async (variantId) => {
			// 1. Отменяем исходящие запросы, чтобы они не перезаписали оптимистичный ответ
			await queryClient.cancelQueries({ queryKey: FAVORITES_QUERY_KEY })

			// 2. Сохраняем предыдущее состояние из кэша для возможного отката
			const previousFavorites = queryClient.getQueryData(FAVORITES_QUERY_KEY) || []

			// 3. Оптимистично обновляем кэш
			queryClient.setQueryData(FAVORITES_QUERY_KEY, (old = []) => {
				const exists = old.some((fav) => fav.variant === variantId)
				if (exists) {
					return old.filter((fav) => fav.variant !== variantId)
				}
				// Если добавляем — формируем временный объект
				return [{ id: Date.now(), variant: variantId, isOptimistic: true }, ...old]
			})

			return { previousFavorites }
		},
		onError: (err, variantId, context) => {
			// При ошибке откатываем кэш к предыдущему состоянию
			if (context?.previousFavorites) {
				queryClient.setQueryData(FAVORITES_QUERY_KEY, context.previousFavorites)
			}
		},
		onSettled: () => {
			// Синхронизируем данные с сервером
			queryClient.invalidateQueries({ queryKey: FAVORITES_QUERY_KEY })
		},
	})
}
