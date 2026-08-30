import { useState, useEffect } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Modal from '@/components/ui/Modal'
import Button from '@/components/ui/Button'
import CheckmarkIcon from '@/shared/icons/checkmark.svg'
import ShowIcon from '@/shared/icons/show.svg'
import HideIcon from '@/shared/icons/hide.svg'
import styles from './AuthModal.module.scss'

// --- Схемы валидации Zod ---

// Базовая схема для пароля
const passwordValidation = z
	.string()
	.min(8, { message: 'Пароль должен содержать минимум 8 символов' })
	.regex(/^[a-zA-Z0-9!?$@#_.]+$/, {
		message: 'Допускаются только латинские буквы, цифры и допустимые спецсимволы',
	})
	.regex(/[a-z]/, { message: 'Добавьте хотя бы одну строчную латинскую букву' })
	.regex(/[A-Z]/, { message: 'Добавьте хотя бы одну заглавную латинскую букву' })
	.regex(/\d/, { message: 'Добавьте хотя бы одну цифру' })
	.regex(/[!?$@#_.]/, { message: 'Добавьте хотя бы один спецсимвол (!?$@#_.)' })

// Схема логина
const loginSchema = z.object({
	email: z.string().email({ message: 'Введите корректный email адрес' }),
	password: z.string().min(1, { message: 'Введите пароль' }), // Для логина достаточно просто проверить, что поле не пустое
	rememberMe: z.boolean().optional(),
})

// Схема регистрации
const registerSchema = z
	.object({
		email: z.string().email({ message: 'Введите корректный email адрес' }),
		password: passwordValidation,
		confirmPassword: z.string(),
	})
	.refine((data) => data.password === data.confirmPassword, {
		message: 'Пароли не совпадают',
		path: ['confirmPassword'], // Ошибка будет привязана к этому полю
	})

const AuthModal = ({ isOpen, onClose }) => {
	// Состояние: true = показываем логин, false = показываем регистрацию
	const [isLoginView, setIsLoginView] = useState(true)

	// Состояния для показа/скрытия паролей
	const [showLoginPassword, setShowLoginPassword] = useState(false)
	const [showRegPassword, setShowRegPassword] = useState(false)
	const [showConfirmPassword, setShowConfirmPassword] = useState(false)

	const [isRegPasswordFocused, setIsRegPasswordFocused] = useState(false)

	// 1. Инициализация формы входа
	const {
		register: registerLogin,
		handleSubmit: handleLoginSubmit,
		formState: { errors: loginErrors },
		reset: resetLogin,
		control: controlLogin, // <-- для хука слежения useWatch
	} = useForm({
		resolver: zodResolver(loginSchema),
		defaultValues: { email: '', password: '', rememberMe: false },
		// mode: 'onTouched', // Проверка при потере фокуса полем
	})

	// 2. Инициализация формы регистрации
	const {
		register: registerReg,
		handleSubmit: handleRegSubmit,
		formState: { errors: regErrors },
		reset: resetReg,
		control: controlReg, // <-- для хука слежения useWatch
	} = useForm({
		resolver: zodResolver(registerSchema),
		defaultValues: { email: '', password: '', confirmPassword: '' },
		// mode: 'onTouched', // Проверка при потере фокуса полем
	})

	// Следим за полями пароля в реальном времени
	const loginPasswordValue = useWatch({
		control: controlLogin,
		name: 'password',
		defaultValue: '',
	})
	const regPasswordValue = useWatch({
		control: controlReg,
		name: 'password',
		defaultValue: '',
	})
	const regConfirmPasswordValue = useWatch({
		control: controlReg,
		name: 'confirmPassword',
		defaultValue: '',
	})

	// Извлекаем пропсы регистрации паролей
	const loginPasswordProps = registerLogin('password')
	const regPasswordProps = registerReg('password')
	const regConfirmPasswordProps = registerReg('confirmPassword')

	// Сброс форм при закрытии модального окна
	// При закрытии модалки всегда возвращаем форму входа
	// и инпуты пароля в состояние "скрыто"
	useEffect(() => {
		if (!isOpen) {
			// Таймаут нужен, чтобы форма не перевернулась до окончания анимации закрытия модалки
			const timer = setTimeout(() => {
				setIsLoginView(true)
				resetLogin()
				resetReg()
				setShowLoginPassword(false)
				setShowRegPassword(false)
				setShowConfirmPassword(false)
			}, 300)
			return () => clearTimeout(timer)
		}
	}, [isOpen, resetLogin, resetReg])

	// Обработчики отправки данных
	const onLogin = (data) => {
		console.log('Данные входа:', data)
		// TODO: Здесь будет вызов API DRF для получения JWT
	}

	const onRegister = (data) => {
		console.log('Данные регистрации:', data)
		// TODO: Здесь будет вызов API DRF для регистрации
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

						<form onSubmit={handleLoginSubmit(onLogin)} className={styles.form}>
							<div className={styles.inputGroup}>
								<label>Email адрес:</label>
								<input
									type="email"
									placeholder="yavasyaivanov@gmail.com"
									{...registerLogin('email')}
								/>

								{/* Вывод ошибки */}
								{loginErrors.email && (
									<span className={styles.errorText}>{loginErrors.email.message}</span>
								)}
							</div>

							<div className={styles.inputGroup}>
								<label>Пароль:</label>
								{/* Обертка для инпута с кнопкой глазика */}
								<div className={styles.passwordInputWrapper}>
									<input
										type={showLoginPassword ? 'text' : 'password'}
										placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱"
										autoComplete="new-password" // Защита от автозаполнения браузером
										{...loginPasswordProps}
										onChange={(e) => {
											loginPasswordProps.onChange(e) // Вызываем родной onChange от RHF
											if (e.target.value.length === 0) setShowLoginPassword(false) // Наша логика сброса
										}}
									/>

									{/* Показываем кнопку только если в поле есть хотя бы 1 символ */}
									{loginPasswordValue.length > 0 && (
										<button
											type="button"
											className={styles.eyeBtn}
											onClick={() => setShowLoginPassword(!showLoginPassword)}
											tabIndex="-1" // Чтобы кнопка не мешала навигации клавишей Tab
										>
											{showLoginPassword ? <ShowIcon /> : <HideIcon />}
										</button>
									)}
								</div>

								{loginErrors.password && (
									<span className={styles.errorText}>{loginErrors.password.message}</span>
								)}
							</div>

							{/* Строка с чекбоксом и ссылкой восстановления */}
							<div className={styles.optionsRow}>
								<label className={styles.checkboxLabel}>
									{/* Нативный чекбокс скрыт, но сохраняет доступность для клавиатуры/скринридеров */}
									<input
										type="checkbox"
										className={styles.hiddenCheckbox}
										{...registerLogin('rememberMe')}
									/>
									<span className={styles.customCheckbox}>
										<CheckmarkIcon className={styles.checkmark} />
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

						<form onSubmit={handleRegSubmit(onRegister)} className={styles.form}>
							<div className={styles.inputGroup}>
								<label>Email адрес:</label>
								<input
									type="email"
									placeholder="yavasyaivanov@gmail.com"
									{...registerReg('email')}
								/>
								{regErrors.email && (
									<span className={styles.errorText}>{regErrors.email.message}</span>
								)}
							</div>

							<div className={styles.inputGroup}>
								<label>Пароль:</label>
								<div className={styles.passwordInputWrapper}>
									<input
										type={showRegPassword ? 'text' : 'password'}
										placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱"
										autoComplete="new-password" // Защита от автозаполнения браузером
										{...regPasswordProps} // Передаем все базовые пропсы RHF
										onChange={(e) => {
											regPasswordProps.onChange(e)
											if (e.target.value.length === 0) setShowRegPassword(false)
										}}
										onFocus={() => setIsRegPasswordFocused(true)} // Показываем подсказку
										onBlur={(e) => {
											regPasswordProps.onBlur(e) // Вызываем родной onBlur от RHF
											setIsRegPasswordFocused(false) // Скрываем подсказку
										}}
									/>

									{/* Показываем кнопку только если в поле есть хотя бы 1 символ */}
									{regPasswordValue.length > 0 && (
										<button
											type="button"
											className={styles.eyeBtn}
											onClick={() => setShowRegPassword(!showRegPassword)}
											tabIndex="-1" // Чтобы кнопка не мешала навигации клавишей Tab
										>
											{showRegPassword ? <ShowIcon /> : <HideIcon />}
										</button>
									)}

									{/* --- ВСПЛЫВАЮЩИЕ ПОДСКАЗКИ --- */}
									<div
										className={`${styles.passwordHintsContainer} ${isRegPasswordFocused ? styles.passwordHintsContainerVisible : ''}`}
									>
										<p>Пароль должен содержать:</p>
										<ul>
											<li
												className={
													regPasswordValue.length > 0 &&
													/^[a-zA-Z0-9!?$@#_.]+$/.test(regPasswordValue)
														? styles.hintValid
														: ''
												}
											>
												Только латиницу, цифры и допустимые спецсимволы
											</li>
											<li
												className={regPasswordValue.length >= 8 ? styles.hintValid : ''}
											>
												Минимум 8 символов
											</li>
											<li
												className={/[a-z]/.test(regPasswordValue) ? styles.hintValid : ''}
											>
												Строчную букву (a-z)
											</li>
											<li
												className={/[A-Z]/.test(regPasswordValue) ? styles.hintValid : ''}
											>
												Заглавную букву (A-Z)
											</li>
											<li className={/\d/.test(regPasswordValue) ? styles.hintValid : ''}>
												Цифру (0-9)
											</li>
											<li
												className={
													/[!?$@#_.]/.test(regPasswordValue) ? styles.hintValid : ''
												}
											>
												Спецсимвол (!?$@#_.)
											</li>
										</ul>
									</div>
									{/* ----------------------------- */}
								</div>

								{regErrors.password && (
									<span className={styles.errorText}>{regErrors.password.message}</span>
								)}
							</div>

							<div className={styles.inputGroup}>
								<label>Повторите пароль:</label>
								<div className={styles.passwordInputWrapper}>
									<input
										type={showConfirmPassword ? 'text' : 'password'}
										placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱"
										autoComplete="new-password" // Защита от автозаполнения браузером
										{...regConfirmPasswordProps}
										onChange={(e) => {
											regConfirmPasswordProps.onChange(e)
											if (e.target.value.length === 0) setShowConfirmPassword(false)
										}}
									/>

									{/* Показываем кнопку только если в поле есть хотя бы 1 символ */}
									{regConfirmPasswordValue.length > 0 && (
										<button
											type="button"
											className={styles.eyeBtn}
											onClick={() => setShowConfirmPassword(!showConfirmPassword)}
											tabIndex="-1" // Чтобы кнопка не мешала навигации клавишей Tab
										>
											{showConfirmPassword ? <ShowIcon /> : <HideIcon />}
										</button>
									)}
								</div>

								{regErrors.confirmPassword && (
									<span className={styles.errorText}>
										{regErrors.confirmPassword.message}
									</span>
								)}
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
