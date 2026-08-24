import { useEffect } from 'react'
import { createPortal } from 'react-dom'
import styles from './Modal.module.scss'

const Modal = ({ isOpen, onClose, title, children }) => {
	// Обработка закрытия по клавише Escape и блокировка скролла
	useEffect(() => {
		const handleKeyDown = (e) => {
			if (e.key === 'Escape') onClose()
		}

		if (isOpen) {
			document.body.style.overflow = 'hidden' // Блокируем скролл сайта
			window.addEventListener('keydown', handleKeyDown)
		}

		return () => {
			document.body.style.overflow = '' // Возвращаем скролл
			window.removeEventListener('keydown', handleKeyDown)
		}
	}, [isOpen, onClose])

	if (!isOpen) return null

	// Закрытие при клике на темный фон (overlay)
	const handleOverlayClick = (e) => {
		// Если клик был именно по фону, а не по самому окну внутри
		if (e.target === e.currentTarget) {
			onClose()
		}
	}

	// Рендерим модалку прямо в <body> через Портал
	return createPortal(
		<div className={styles.overlay} onClick={handleOverlayClick}>
			<div className={styles.modal}>
				{/* Кнопка закрытия (крестик) */}
				<button className={styles.closeBtn} onClick={onClose} aria-label="Закрыть">
					&times;
				</button>

				{/* Опциональный заголовок */}
				{title && <h2 className={styles.title}>{title}</h2>}

				{/* Контент, который мы будем передавать внутрь */}
				<div className={styles.content}>{children}</div>
			</div>
		</div>,
		document.body,
	)
}

export default Modal
