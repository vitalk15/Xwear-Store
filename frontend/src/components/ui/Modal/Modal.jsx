import { useEffect } from 'react'
import { createPortal } from 'react-dom'
import styles from './Modal.module.scss'

/**
 * Универсальный компонент модального окна на основе React Portals.
 * ( Это позволит рендерить окно прямо в document.body, независимо от того,
 * насколько глубоко в дереве компонентов оно будет вызвано.
 * Это защищает нас от конфликтов с z-index и overflow родительских блоков.)
 *
 * Отображается по центру экрана поверх полупрозрачного оверлея,
 * блокирует скролл страницы при открытии и поддерживает закрытие
 * по нажатию клавиши Escape или клику на тёмный фон.
 *
 * @param {Object} props - Пропсы компонента.
 * @param {boolean} props.isOpen - Состояние отображения модального окна (true — открыто, false — закрыто).
 * @param {() => void} props.onClose - Функция обратного вызова для обработки закрытия модального окна.
 * @param {React.ReactNode} [props.title] - Необязательный заголовок в шапке модального окна.
 * @param {React.ReactNode} props.children - Содержимое, рендерящееся внутри тела модального окна.
 * @param {string} [props.className=''] - Дополнительные CSS-классы для переопределения или добавления стилей контейнеру окна.
 * @param {boolean} [props.showCloseButton=true] - Флаг, определяющий отображение стандартной кнопки закрытия (крестика) в базовом компоненте.
 *
 * @returns {React.ReactPortal | null} Возвращает React Portal в body или null, если isOpen === false.
 */
const Modal = ({
	isOpen,
	onClose,
	title,
	children,
	className = '',
	showCloseButton = true,
}) => {
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
			<div className={`${styles.modal} ${className}`.trim()}>
				{/* Кнопка закрытия (крестик) */}
				{showCloseButton && (
					<button className={styles.closeBtn} onClick={onClose} aria-label="Закрыть">
						&times;
					</button>
				)}

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
