import { useState, useEffect } from 'react'
import Modal from '@/components/ui/Modal'
import LoginForm from './components/LoginForm'
import RegisterForm from './components/RegisterForm'
import ResetPasswordForm from './components/ResetPasswordForm'
import styles from './AuthModal.module.scss'

const AuthModal = ({ isOpen, onClose }) => {
	// Состояние: true = показываем логин, false = показываем регистрацию
	const [isLoginView, setIsLoginView] = useState(true)
	// Состояние показа формы сброса пароля
	const [showResetPassword, setShowResetPassword] = useState(false)

	// Возвращаем форму входа на лицевую сторону при закрытии модалки (после завершения CSS-анимации скрытия)
	useEffect(() => {
		if (!isOpen) {
			const timer = setTimeout(() => {
				setIsLoginView(true)
				setShowResetPassword(false)
			}, 300)
			return () => clearTimeout(timer)
		}
	}, [isOpen])

	return (
		<Modal
			className={styles.transparentModalOverride}
			isOpen={isOpen}
			onClose={onClose}
			showCloseButton={false}
		>
			<div className={styles.flipContainer}>
				<div className={`${styles.flipper} ${!isLoginView ? styles.isFlipped : ''}`}>
					{/* ЛИЦЕВАЯ СТОРОНА: Логин ИЛИ Сброс пароля */}
					<div className={styles.front}>
						{/* Отрисовка компонента входа. Если окно закрыто, React Hook Form 
                внутри LoginForm автоматически размонтируется и очистит свои данные (не нужно вручную вызывать функцию reset())*/}
						{isOpen && !showResetPassword && (
							<LoginForm
								onClose={onClose}
								onSwitchToRegister={() => setIsLoginView(false)}
								onForgotPassword={() => setShowResetPassword(true)} // Переключаем на сброс пароля
							/>
						)}

						{isOpen && showResetPassword && (
							<ResetPasswordForm
								onBackToLogin={() => setShowResetPassword(false)} // Возвращаем логин
							/>
						)}
					</div>

					<div className={styles.back}>
						{/* Отрисовка компонента регистрации */}
						{isOpen && (
							<RegisterForm
								onClose={onClose}
								onSwitchToLogin={() => setIsLoginView(true)}
							/>
						)}
					</div>
				</div>
			</div>
		</Modal>
	)
}

export default AuthModal
