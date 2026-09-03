import { useState, useEffect } from 'react'
import Modal from '@/components/ui/Modal'
import LoginForm from './components/LoginForm'
import RegisterForm from './components/RegisterForm'
import styles from './AuthModal.module.scss'

const AuthModal = ({ isOpen, onClose }) => {
	// Состояние: true = показываем логин, false = показываем регистрацию
	const [isLoginView, setIsLoginView] = useState(true)

	// Возвращаем форму входа на лицевую сторону при закрытии модалки (после завершения CSS-анимации скрытия)
	useEffect(() => {
		if (!isOpen) {
			const timer = setTimeout(() => setIsLoginView(true), 300)
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
					<div className={styles.front}>
						{/* Отрисовка компонента входа. Если окно закрыто, React Hook Form 
                внутри LoginForm автоматически размонтируется и очистит свои данные (не нужно вручную вызывать функцию reset())*/}
						{isOpen && (
							<LoginForm
								onClose={onClose}
								onSwitchToRegister={() => setIsLoginView(false)}
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
