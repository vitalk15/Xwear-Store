import {
	useQuery,
	useSuspenseQuery,
	useMutation,
	useQueryClient,
} from '@tanstack/react-query'
// import useAuthStore from '@/features/auth/store/useAuthStore'
import { profileApi } from '../api/profileApi'

// !!! Добавить с поддержкой Suspense

export const profileKeys = {
	profile: ['user-profile'],
	cities: ['delivery-cities'],
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
	// const setUser = useAuthStore((state) => state.setUser)

	return useMutation({
		mutationFn: profileApi.updateProfile,
		onSuccess: (updatedUserData) => {
			// Обновляем кэш React Query
			queryClient.setQueryData(profileKeys.profile, updatedUserData)
			// Обновляем данные пользователя в Zustand store
			// setUser(updatedUserData)
		},
	})
}

/**
 * Хук для получения доступных городов доставки.
 */
export const useCitiesQuery = () => {
	return useQuery({
		queryKey: profileKeys.cities,
		queryFn: profileApi.getCities,
		staleTime: 60 * 60 * 1000, // Города меняются редко, кэшируем на 1 час
	})
}

/**
 * Хук для добавления нового адреса доставки.
 */
export const useCreateAddressMutation = () => {
	const queryClient = useQueryClient()

	return useMutation({
		mutationFn: profileApi.createAddress,
		onSuccess: () => {
			// Обновляем данные профиля, чтобы сразу подтянулся новый список адресов
			queryClient.invalidateQueries({ queryKey: profileKeys.profile })
		},
	})
}

/**
 * Хук для частичного обновления адреса доставки.
 */
export const useUpdateAddressMutation = () => {
	const queryClient = useQueryClient()
	return useMutation({
		mutationFn: profileApi.updateAddress,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: profileKeys.profile })
		},
	})
}

/**
 * Хук для удаления адреса доставки.
 */
export const useDeleteAddressMutation = () => {
	const queryClient = useQueryClient()
	return useMutation({
		mutationFn: profileApi.deleteAddress,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: profileKeys.profile })
		},
	})
}
