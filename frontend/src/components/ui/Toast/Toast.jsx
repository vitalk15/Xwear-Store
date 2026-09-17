import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import styles from './Toast.module.scss'

const Toast = ({ message, type = 'success', onClose }) => {
	// Флаг для отслеживания этапа ухода плашки (false — появление, true — исчезновение)
	const [isLeaving, setIsLeaving] = useState(false)

	useEffect(() => {
		// 1. Таймер на запуск анимации скрытия (через 3 секунды)
		const timer = setTimeout(() => {
			setIsLeaving(true) // Включает CSS-класс с анимацией slideOut
		}, 3000)

		// 2. Таймер на полное размонтирование компонента из DOM.
		// 3300 мс = 3000 мс (показ) + 300 мс (длительность CSS-анимации slideOut)
		const removeTimer = setTimeout(() => {
			onClose() // Вызываем родительский колбэк для сброса состояния toast в null
		}, 3300)

		// Функция очистки: если пользователь быстро переключит вкладку или toast удалится раньше,
		// очищаем таймеры для предотвращения утечек памяти.
		return () => {
			clearTimeout(timer)
			clearTimeout(removeTimer)
		}
	}, [onClose])

	return createPortal(
		<div
			className={`${styles.toast} ${styles[type]} ${
				isLeaving ? styles.leave : styles.enter
			}`}
		>
			<span className={styles.icon}>{type === 'success' ? '✓' : '✕'}</span>
			<span className={styles.message}>{message}</span>
		</div>,
		document.body, // Рендерим прямо в body
	)
}

export default Toast
