import { useState } from 'react'
import useAuthStore from '@/features/auth/store/useAuthStore'
import { useFavoritesCheck, useToggleFavoriteMutation } from './useFavorites'

/**
 * Универсальный хук для логики кнопки "В избранное"
 * @param {string|number} targetId - ID товара или варианта для добавления
 */
export const useFavoriteAction = (targetId) => {
	const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)
	const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

	// Подключаем функционал избранного
	const { isFavorite } = useFavoritesCheck()
	const { mutate: toggleFavorite } = useToggleFavoriteMutation()

	// Проверяем статус (находится ли в избранном) для конкретного ID
	const isFav = isFavorite(targetId)

	// Обработка клика на звёздочку
	const handleFavoriteClick = (e) => {
		e.preventDefault()
		e.stopPropagation() // Предотвращаем открытие модалки увеличения фото

		if (!isAuthenticated) {
			setIsAuthModalOpen(true)
			return
		}

		if (targetId) {
			toggleFavorite(targetId)
		}
	}

	return {
		isFav,
		isAuthModalOpen,
		setIsAuthModalOpen,
		handleFavoriteClick,
	}
}
