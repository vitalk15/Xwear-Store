import useErrorStore from '@/shared/store/useErrorStore'
import styles from './ServerErrorPage.module.scss'

const ERROR_CONFIGS = {
	429: {
		icon: '⏳',
		title: 'Слишком много запросов',
		description:
			'Вы отправляете запросы слишком часто. Пожалуйста, подождите пару минут и попробуйте снова.',
	},
	NETWORK_ERROR: {
		icon: '🔌',
		title: 'Нет связи с сервером',
		description:
			'Не удалось соединиться с сервером.\nПроверьте интернет или загляните к нам чуть позже.',
	},
	403: {
		icon: '🚫',
		title: 'Доступ ограничен',
		description: 'Запрос отклонен защитной системой сервера.',
	},
	DEFAULT: {
		icon: '🛠️',
		title: 'Технические работы на сервере',
		description:
			'Мы уже знаем о проблеме и восстанавливаем работу. Загляните к нам чуть позже.',
	},
}

const ServerErrorPage = () => {
	const { statusCode, errorMessage, clearError } = useErrorStore()

	const config = ERROR_CONFIGS[statusCode] || ERROR_CONFIGS.DEFAULT

	const handleRetry = () => {
		clearError()
		window.location.reload()
	}

	return (
		<div className={styles.container}>
			<div className={styles.content}>
				<div className={styles.icon}>{config.icon}</div>
				<h1 className={styles.title}>{config.title}</h1>
				<p className={styles.description}>{errorMessage || config.description}</p>
				<button type="button" className={styles.retryBtn} onClick={handleRetry}>
					Обновить страницу
				</button>
			</div>
		</div>
	)
}

export default ServerErrorPage
