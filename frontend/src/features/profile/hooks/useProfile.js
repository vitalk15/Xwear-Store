import {
	useQuery,
	useSuspenseQuery,
	useMutation,
	useQueryClient,
} from '@tanstack/react-query'
import useAuthStore from '@/features/auth/store/useAuthStore'
import { profileApi } from '../api/profileApi'

// !!! Добавить с поддержкой Suspense

export const profileKeys = {
	profile: ['user-profile'],
}

/**
 * Хук для получения данных профиля текущего авторизованного пользователя. Возвращает isLoading, isError и т.д.
 *
 * @returns {import('@tanstack/react-query').UseQueryResult} Объект состояния запроса TanStack Query с данными пользователя и его профиля.
 */
export const useProfileQuery = () => {
	return useQuery({
		queryKey: profileKeys.profile,
		queryFn: profileApi.getProfile,
		staleTime: 5 * 60 * 1000,
	})
}

/**
 * Suspense-хук для получения данных профиля.
 * Приостанавливает рендер компонента до получения данных.
 * Гарантирует, что если компонент отрендерился, то data (данные) точно существуют.
 */
export const useSuspenseProfileQuery = () => {
	return useSuspenseQuery({
		queryKey: profileKeys.profile,
		queryFn: profileApi.getProfile,
		staleTime: 5 * 60 * 1000,
	})
}

/**
 * Хук для частичного обновления данных профиля (имя, фамилия, телефон).
 * Автоматически актуализирует данные в кэше React Query и в Zustand store при успехе.
 *
 * @returns {import('@tanstack/react-query').UseMutationResult} Объект мутации для запуска PATCH-запроса на бэкенд.
 */
export const useUpdateProfileMutation = () => {
	const queryClient = useQueryClient()
	const setUser = useAuthStore((state) => state.setUser)

	return useMutation({
		mutationFn: profileApi.updateProfile,
		onSuccess: (updatedUserData) => {
			// Обновляем кэш React Query
			queryClient.setQueryData(profileKeys.profile, updatedUserData)
			// Обновляем данные пользователя в Zustand store
			setUser(updatedUserData)
		},
	})
}
