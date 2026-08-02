import { useState } from 'react'
import ArrowIcon from '@/shared/icons/arrow.svg'
import { useDocuments } from '@/entities/documents/hooks/useDocuments'
import { apiClient } from '@/shared/api/apiClient'
import styles from '@/components/common/Footer/Footer.module.scss'

const API_URL = apiClient.defaults.baseURL || 'http://127.0.0.1:8000/api'
// Вытаскиваем "чистый" домен (origin) с помощью нативного класса URL
const DOMAIN_URL = new URL(API_URL).origin

const Subscribe = () => {
	const [email, setEmail] = useState('')

	// Получаем данные документов
	const { data: documents } = useDocuments()

	// Находим нужные файлы по ID
	const privacyPolicy = documents?.find(
		(doc) => doc.title === 'Политика конфиденциальности',
	)
	const userAgreement = documents?.find(
		(doc) => doc.title === 'Пользовательское соглашение',
	)

	const handleSubscribe = (e) => {
		e.preventDefault()
		if (!email) return

		// !!! Todo: Добавить функционал подписки
		// Временная заглушка для фронтенда
		alert(`Спасибо за подписку! Письма будут приходить на указанный email: ${email}`)
		setEmail('')
	}

	return (
		<div className={styles.subscribeCol}>
			<h4 className={styles.colTitle}>Подписка на новости</h4>
			<p className={styles.subscribeDesc}>Будьте в курсе скидок и новостей</p>
			<form onSubmit={handleSubscribe} className={styles.subscribeForm}>
				<input
					type="email"
					placeholder="Ваш email"
					value={email}
					onChange={(e) => setEmail(e.target.value)}
					required
					className={styles.input}
				/>
				<button
					type="submit"
					className={styles.submitBtn}
					aria-label="Подписаться на новости"
				>
					<ArrowIcon />
				</button>
			</form>
			{/* Дисклеймер и документы */}
			<div className={styles.disclaimerBlock}>
				<p className={styles.disclaimerText}>
					Подписываясь на рассылку вы соглашаетесь с обработкой персональных данных
				</p>
				<div className={styles.legalLinks}>
					<a
						href={privacyPolicy ? `${DOMAIN_URL}${privacyPolicy.file}` : '#'}
						target="_blank"
						rel="noopener noreferrer"
					>
						{privacyPolicy ? privacyPolicy.title : 'Политика конфиденциальности'}
					</a>

					<a
						href={userAgreement ? `${DOMAIN_URL}${userAgreement.file}` : '#'}
						target="_blank"
						rel="noopener noreferrer"
					>
						{userAgreement ? userAgreement.title : 'Пользовательское соглашение'}
					</a>
				</div>
			</div>
		</div>
	)
}

export default Subscribe
