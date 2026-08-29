import { useState, useEffect } from 'react'
import Modal from '@/components/ui/Modal'
import Button from '@/components/ui/Button'
import styles from './AuthModal.module.scss'

const AuthModal = ({ isOpen, onClose }) => {
	// Состояние: true = показываем логин, false = показываем регистрацию
	const [isLoginView, setIsLoginView] = useState(true)

	// При закрытии модалки всегда возвращаем на форму входа
	useEffect(() => {
		if (!isOpen) {
			// Таймаут нужен, чтобы форма не перевернулась до окончания анимации закрытия модалки
			const timer = setTimeout(() => setIsLoginView(true), 300)
			return () => clearTimeout(timer)
		}
	}, [isOpen])

	// Заглушка отправки
	const handleSubmit = (e) => {
		e.preventDefault()
		console.log('Отправка формы...')
	}

	return (
		<Modal
			className={styles.transparentModalOverride}
			isOpen={isOpen}
			onClose={onClose}
			showCloseButton={false}
		>
			<div className={styles.flipContainer}>
				{/* Контейнер, который переворачивается */}
				<div className={`${styles.flipper} ${!isLoginView ? styles.isFlipped : ''}`}>
					{/* ================= ФОРМА ВХОДА ================= */}
					<div className={styles.front}>
						{/* Крестик закрытия */}
						<button className={styles.closeBtn} onClick={onClose} aria-label="Закрыть">
							&times;
						</button>

						<h2 className={styles.title}>Войти</h2>
						<form onSubmit={handleSubmit} className={styles.form}>
							<div className={styles.inputGroup}>
								<label>Email адрес:</label>
								<input type="email" placeholder="yavasyaivanov@gmail.com" />
							</div>
							<div className={styles.inputGroup}>
								<label>Пароль:</label>
								<input type="password" placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱" />
							</div>

							{/* Строка с чекбоксом и ссылкой восстановления */}
							<div className={styles.optionsRow}>
								<label className={styles.checkboxLabel}>
									{/* Нативный чекбокс скрыт, но сохраняет доступность для клавиатуры/скринридеров */}
									<input type="checkbox" className={styles.hiddenCheckbox} />
									<span className={styles.customCheckbox}>
										<svg
											className={styles.checkmark}
											viewBox="0 0 12 10"
											fill="none"
											xmlns="http://www.w3.org/2000/svg"
										>
											<path
												d="M1.5 5L4.5 8L10.5 1.5"
												stroke="currentColor"
												strokeWidth="2"
												strokeLinecap="round"
												strokeLinejoin="round"
											/>
										</svg>
									</span>
									<span>Запомнить меня</span>
								</label>
								<button type="button" className={styles.forgotLink}>
									Забыли пароль?
								</button>
							</div>

							<div className={styles.submitBtnWrapper}>
								<Button type="submit" className={styles.submitBtn}>
									ВОЙТИ
								</Button>
							</div>
						</form>

						<div className={styles.toggleText}>
							<span>Нет аккаунта? </span>
							<button type="button" onClick={() => setIsLoginView(false)}>
								Регистрация
							</button>
						</div>
					</div>

					{/* ================= ФОРМА РЕГИСТРАЦИИ ================= */}
					<div className={styles.back}>
						{/* Крестик закрытия */}
						<button className={styles.closeBtn} onClick={onClose} aria-label="Закрыть">
							&times;
						</button>

						<h2 className={styles.title}>Регистрация</h2>
						<form onSubmit={handleSubmit} className={styles.form}>
							<div className={styles.inputGroup}>
								<label>Email адрес:</label>
								<input type="email" placeholder="yavasyaivanov@gmail.com" />
							</div>
							<div className={styles.inputGroup}>
								<label>Пароль:</label>
								<input type="password" placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱" />
							</div>
							<div className={styles.inputGroup}>
								<label>Повторите пароль:</label>
								<input type="password" placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱" />
							</div>

							<div className={styles.submitBtnWrapper}>
								<Button type="submit" className={styles.submitBtn}>
									ЗАРЕГИСТРИРОВАТЬСЯ
								</Button>
							</div>
						</form>

						<div className={styles.toggleText}>
							Уже есть аккаунт?{' '}
							<button type="button" onClick={() => setIsLoginView(true)}>
								Вход
							</button>
						</div>
					</div>
				</div>
			</div>
		</Modal>
	)
}

export default AuthModal
