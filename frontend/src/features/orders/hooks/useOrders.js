import {
	useQuery,
	useSuspenseQuery,
	useMutation,
	useQueryClient,
} from '@tanstack/react-query'
import { ordersApi } from '../api/ordersApi'

// Ключи кэша
export const ORDER_KEYS = {
	all: ['orders'],
	list: () => [...ORDER_KEYS.all, 'list'],
	cities: ['cities'],
	pickupPoints: ['pickup-points'],
	commercialConfig: ['commercial-config'],
}

// Загрузка списка городов
export const useCitiesQuery = () => {
	return useQuery({
		queryKey: ORDER_KEYS.cities,
		queryFn: ordersApi.getCities,
		staleTime: 1000 * 60 * 60, // Города меняются редко, кэшируем на час
	})
}

// Загрузка списка ПВЗ
export const usePickupPointsQuery = () => {
	return useQuery({
		queryKey: ORDER_KEYS.pickupPoints,
		queryFn: ordersApi.getPickupPoints,
		staleTime: 1000 * 60 * 30, // Данные актуальны 30 минут
	})
}

// Suspense-версия получения списка ПВЗ
export const useSuspensePickupPointsQuery = () => {
	return useSuspenseQuery({
		queryKey: ORDER_KEYS.pickupPoints,
		queryFn: ordersApi.getPickupPoints,
		staleTime: 1000 * 60 * 30, // 30 минут
	})
}

// Загрузка CommercialConfig (порог бесплатной доставки)
export const useCommercialConfigQuery = () => {
	return useQuery({
		queryKey: ORDER_KEYS.commercialConfig,
		queryFn: ordersApi.getCommercialConfig,
		staleTime: 1000 * 60 * 30,
	})
}

// Загрузка всех заказов пользователя (для вкладки account в профиле)
export const useOrdersQuery = () => {
	return useQuery({
		queryKey: ORDER_KEYS.list(),
		queryFn: ordersApi.getOrders,
	})
}

// Мутация создания заказа
export const useCreateOrderMutation = () => {
	const queryClient = useQueryClient()

	return useMutation({
		mutationFn: ordersApi.createOrder,
		onSuccess: () => {
			// Инвалидируем кэш корзины и заказов после успешного оформления
			queryClient.invalidateQueries({ queryKey: ['cart'] })
			queryClient.invalidateQueries({ queryKey: ORDER_KEYS.all })
		},
	})
}
