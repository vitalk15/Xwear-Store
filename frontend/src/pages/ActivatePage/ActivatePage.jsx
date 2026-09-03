import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { activateUser } from '@/features/auth/api/auth.api'
import useAuthStore from '@/features/auth/store/useAuthStore'
import PageTitle from '@/components/common/PageTitle'
import styles from './ActivatePage.module.scss'

// Компонент забирает uid и token из параметров URL (используя useParams из react-router-dom), отправляет запрос на сервер, сохраняет авторизацию и перенаправляет пользователя
const ActivatePage = () => {
	const { uid, token } = useParams()
	const navigate = useNavigate()
	const setAuth = useAuthStore((state) => state.setAuth)

	const [status, setStatus] = useState('pending') // 'pending' | 'success' | 'error'
	const [errorMessage, setErrorMessage] = useState('')

	useEffect(() => {
		const handleActivation = async () => {
			try {
				// Отправляем uid и token на бэкенд
				const data = await activateUser({ uid, token })

				// Если активация прошла успешно, сохраняем данные в Zustand
				setAuth({
					user: data.user,
					access: data.access,
				})

				setStatus('success')

				// Через 3 секунды перенаправляем пользователя на главную
				setTimeout(() => {
					navigate('/')
				}, 3000)
			} catch (error) {
				setStatus('error')
				if (error.response && error.response.data.error) {
					setErrorMessage(error.response.data.error)
				} else {
					setErrorMessage('Произошла ошибка при активации аккаунта.')
				}
			}
		}

		if (uid && token) {
			handleActivation()
		}
	}, [uid, token, setAuth, navigate])

	return (
		<>
			<PageTitle title="Активация аккаунта" />

			<div className="container">
				<div className={styles.cardMessages}>
					{status === 'pending' && (
						<>
							<h2>Активация аккаунта...</h2>
							<p>Пожалуйста, подождите, мы проверяем вашу ссылку.</p>
						</>
					)}

					{status === 'success' && (
						<>
							<h2 className={styles.successTitle}>Аккаунт успешно активирован!</h2>
							<p>Вы успешно вошли в систему. Перенаправление на главную страницу...</p>
						</>
					)}

					{status === 'error' && (
						<>
							<h2 className={styles.errorTitle}>Ошибка активации</h2>
							<p>{errorMessage}</p>
						</>
					)}
				</div>
			</div>
		</>
	)
}

export default ActivatePage
