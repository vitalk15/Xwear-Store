import { useFavoriteAction } from '@/features/favorites/hooks/useFavoriteAction'
import AuthModal from '@/features/auth/components/AuthModal'
import StarIcon from '@/shared/icons/star.svg'
import styles from './ButtonFavorite.module.scss'

/**
 * Умная кнопка "В избранное"
 * @param {string|number} targetId - ID товара или варианта
 * @param {string} className - Дополнительный класс для внешнего позиционирования
 */
const ButtonFavorite = ({ targetId, className = '' }) => {
	const { isFav, isAuthModalOpen, setIsAuthModalOpen, handleFavoriteClick } =
		useFavoriteAction(targetId)

	return (
		<>
			<button
				type="button"
				className={`${styles.button} ${isFav ? styles.favoriteActive : ''} ${className}`}
				onClick={handleFavoriteClick}
				aria-label={isFav ? 'Удалить из избранного' : 'Добавить в избранное'}
			>
				<StarIcon className={styles.starIcon} />
			</button>

			{/* Модальное окно авторизации для незарегистрированных пользователей */}
			<AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />
			{/* {isAuthModalOpen && <AuthModal onClose={() => setIsAuthModalOpen(false)} />} */}
		</>
	)
}

export default ButtonFavorite
