import useErrorStore from '@/store/useErrorStore'
import styles from './GlobalErrorModal.module.scss'

const GlobalErrorModal = () => {
	const { hasError, errorMessage, clearError } = useErrorStore()

	// Если ошибки нет — ничего не рендерим
	if (!hasError) {
		document.body.classList.remove('modal-open')
		return null
	} else {
		document.body.classList.add('modal-open')
	}

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
