import useErrorStore from '@/store/useErrorStore'

export const handleCriticalError = (error, info) => {
	// 1. Логируем ошибку в консоль
	// !!! Todo: позже будет отправка в Sentry или другой сервис
	console.error('Системная ошибка:', error)
	console.error('Компонент:', info)

	// 2. Записываем ошибку в Zustand.
	// Даже если этот метод вызовется 5 раз от разных ErrorBoundary,
	// стейт просто перезапишется тем же значением, и никакого дублирования окон не будет.
	useErrorStore.getState().setError('Данные не могут быть загружены. Зайдите позже.')
}

export const handleError = (error, info) => {
	// 1. Логируем ошибку в консоль
	// !!! Todo: позже будет отправка в Sentry или другой сервис
	console.error('Системная ошибка:', error)
	console.error('Компонент:', info)
}
