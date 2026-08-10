import { useEffect } from 'react'
import useErrorStore from '@/store/useErrorStore'
import styles from './GlobalErrorModal.module.scss'

const GlobalErrorModal = () => {
	const { hasError, errorMessage, clearError } = useErrorStore()

	// Блокировка прокрутки (гибридный подход с добавлением класса)
	useEffect(() => {
		if (hasError) {
			document.body.style.overflow = 'hidden'
		} else {
			document.body.style.overflow = ''
		}

		// Очистка при размонтировании (на всякий случай)
		return () => {
			document.body.style.overflow = ''
		}
	}, [hasError])

	// Если ошибки нет — ничего не рендерим
	if (!hasError) return null

	const handleRetry = () => {
		clearError() // Сбрасываем ошибку в Zustand
		window.location.reload() // Перезагружаем страницу, чтобы запросы ушли заново
	}

	return (
		<div className={styles.overlay}>
			<div className={styles.modal}>
				<div className={styles.icon}>⚠️</div>
				<h2 className={styles.title}>Проблема с загрузкой данных</h2>
				<p className={styles.text}>
					{errorMessage ||
						'На сервере ведутся технические работы. Пожалуйста, зайдите позже.'}
				</p>
				<button className={styles.retryBtn} onClick={handleRetry}>
					Обновить страницу
				</button>
			</div>
		</div>
	)
}

export default GlobalErrorModal
