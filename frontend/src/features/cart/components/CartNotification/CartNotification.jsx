import { useEffect } from 'react'
import { createPortal } from 'react-dom'
import { useCartNotificationStore } from '@/features/cart/store/useCartNotificationStore'
import CloseIcon from '@/shared/icons/cross.svg'
import styles from './CartNotification.module.scss'

const CartNotification = () => {
	const { isOpen, productInfo, closeNotification } = useCartNotificationStore()

	// Блокируем клики под плашкой, если нужно (обычно для toast-уведомлений это не делают,
	// но оставим возможность закрытия по нажатию клавиши Esc)
	useEffect(() => {
		const handleKeyDown = (e) => {
			if (e.key === 'Escape' && isOpen) {
				closeNotification()
			}
		}
		document.addEventListener('keydown', handleKeyDown)
		return () => document.removeEventListener('keydown', handleKeyDown)
	}, [isOpen, closeNotification])

	if (!isOpen || !productInfo) return null

	return createPortal(
		<div className={styles.overlay}>
			<div className={styles.notificationCard}>
				{/* Кнопка закрытия */}
				<button
					type="button"
					className={styles.closeBtn}
					onClick={closeNotification}
					aria-label="Закрыть уведомление"
				>
					<CloseIcon className={styles.closeIcon} />
				</button>

				{/* Контент плашки */}
				<div className={styles.content}>
					<div className={styles.imageWrapper}>
						<img
							src={productInfo.image}
							alt={productInfo.name}
							className={styles.image}
						/>
					</div>

					<div className={styles.textBlock}>
						<span className={styles.statusText}>ТОВАР ДОБАВЛЕН В КОРЗИНУ</span>
						<strong className={styles.productName}>{productInfo.name}</strong>
						<span className={styles.productSize}>Размер: {productInfo.size}</span>
					</div>
				</div>
			</div>
		</div>,
		document.body, // Рендерим портал прямо в body
	)
}

export default CartNotification
