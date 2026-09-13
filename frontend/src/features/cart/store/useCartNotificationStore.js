import { create } from 'zustand'

export const useCartNotificationStore = create((set, get) => ({
	isOpen: false,
	productInfo: null, // Здесь будем хранить { name, size, image } добавленного товара
	timerId: null, // Хранилище для ID таймера

	showNotification: (productInfo) => {
		// 1. Если уже есть запущенный таймер — удаляем его
		const currentTimer = get().timerId
		if (currentTimer) {
			clearTimeout(currentTimer)
		}

		// 2. Создаем новый таймер на полные 3 секунды
		const newTimerId = setTimeout(() => {
			set({ isOpen: false, productInfo: null, timerId: null })
		}, 3000)

		// 3. Показываем плашку с новыми данными и сохраняем новый таймер
		set({ isOpen: true, productInfo, timerId: newTimerId })
	},
	closeNotification: () => {
		// При ручном закрытии (на крестик) тоже удаляем таймер
		const currentTimer = get().timerId
		if (currentTimer) {
			clearTimeout(currentTimer)
		}
		set({ isOpen: false, productInfo: null, timerId: null })
	},
}))
