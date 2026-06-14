// import { useQuery } from '@tanstack/react-query'
import { useSuspenseQuery } from '@tanstack/react-query'
import { apiClient } from '@/api/client'

// Получение категорий
// export const useCategories = () => {
// 	// возвращает объект с данными и кучей полезных состояний (isLoading, isError и др.)
// 	return useQuery({
// 		queryKey: ['categories'], // имя ячейки памяти (кэша)
// 		// функция, которая объясняет React Query, как именно нужно получить данные, если их нет в кэше.
// 		queryFn: async () => {
// 			const { data } = await apiClient.get('/shop/categories/')
// 			return data
// 		},
// 		// Кэшируем меню на 10 минут, так как категории меняются редко
// 		staleTime: 10 * 60 * 1000,
// 	})
// }

export const useCategories = () => {
	// делегируя обработку состояний компонентам Suspense (для загрузки)
	return useSuspenseQuery({
		queryKey: ['categories'], // имя ячейки памяти (кэша)
		// функция, которая объясняет React Query, как именно нужно получить данные, если их нет в кэше.
		queryFn: async () => {
			const { data } = await apiClient.get('/shop/categories/')
			return data
		},
		// Кэшируем меню на 10 минут, так как категории меняются редко
		staleTime: 10 * 60 * 1000,
	})
}
