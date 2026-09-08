import { useState } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { registerSchema } from '@/features/auth/schemas/auth.schema'
import { registerUser } from '@/features/auth/api/auth.api'
import Button from '@/components/ui/Button'
import PasswordHints from '@/features/auth/components/PasswordHints'
import ShowIcon from '@/shared/icons/show.svg'
import HideIcon from '@/shared/icons/hide.svg'
import styles from './RegisterForm.module.scss'

const RegisterForm = ({ onClose, onSwitchToLogin }) => {
	// Состояния для показа/скрытия паролей
	const [showPassword, setShowPassword] = useState(false)
	const [showConfirm, setShowConfirm] = useState(false)
	// Состояние фокуса на поле пароля
	const [isPasswordFocused, setIsPasswordFocused] = useState(false)
	// Состояние успеха регистрации
	const [isSuccess, setIsSuccess] = useState(false)
	// состояние зарегистрированной эл.почты
	const [registeredEmail, setRegisteredEmail] = useState('')

	// Инициализация формы регистрации и подключение схемы
	const {
		register,
		handleSubmit,
		formState: { errors, isSubmitting }, // isSubmitting - принимает значение true когда пользователь нажимает на кнопку отправки (и срабатывает функция handleSubmit(onSubmit)) и остаётся true пока выполняется запрос к серверу
		control, // <-- для хука слежения useWatch
		setError,
	} = useForm({
		resolver: zodResolver(registerSchema),
		defaultValues: { email: '', password: '', confirmPassword: '' },
		// mode: 'onSubmit', // Режим по-умолчанию. Проверка при отправке формы
		// mode: 'onTouched', // Проверка при потере фокуса полем
		// mode: 'onChange', // Режим реального времени
	})

	// Следим за полями паролей в реальном времени
	const passwordValue = useWatch({ control, name: 'password', defaultValue: '' })
	const confirmValue = useWatch({ control, name: 'confirmPassword', defaultValue: '' })

	// Извлекаем пропсы регистрации паролей
	const passwordProps = register('password')
	const confirmProps = register('confirmPassword')

	// Обработчик отправки данных
	const onSubmit = async (data) => {
		try {
			// Отправляем (маппим) данные, которые ожидает бэкенд
			await registerUser({
				email: data.email,
				password: data.password,
				password_confirm: data.confirmPassword,
			})

			setRegisteredEmail(data.email)
			setIsSuccess(true)
		} catch (error) {
			// Перехватываем ошибки валидации от Django (400 Bad Request)
			if (error.response && error.response.status === 400) {
				const backendErrors = error.response.data

				// DRF возвращает ошибки в виде объекта с массивами строк: { email: ["Такой email уже существует."] }
				// Обработка ошибки Email
				if (backendErrors.email) {
					const customEmailMessage = backendErrors.email[0].includes('уже существует')
						? 'Пользователь с таким email уже зарегистрирован'
						: backendErrors.email[0]

					setError('email', {
						type: 'server',
						message: customEmailMessage,
					})
				}

				// Обработка ошибок пароля (если Django решит, что он слишком простой)
				if (backendErrors.password) {
					setError('password', {
						type: 'server',
						message: backendErrors.password[0],
					})
				}

				// Обработка ошибок подтверждения пароля
				if (backendErrors.password_confirm) {
					setError('confirmPassword', {
						type: 'server',
						message: backendErrors.password_confirm[0],
					})
				}
			} else {
				alert('Произошла ошибка при соединении с сервером. Попробуйте позже.')
			}
		}
	}

	// Если регистрация прошла успешно — показываем сообщение
	if (isSuccess) {
		return (
			<div className={styles.successWrapper}>
				<button
					className={`${styles.closeBtn} ${styles.successBtn}`}
					onClick={onClose}
					aria-label="Закрыть"
				>
					&times;
				</button>
				<h2 className={styles.successTitle}>Регистрация прошла успешно!</h2>
				<p className={styles.successMessage}>
					Мы отправили письмо для активации аккаунта на адрес{' '}
					<strong>{registeredEmail}</strong>.
				</p>
				<p className={styles.subText}>
					Перейдите по ссылке в письме, чтобы завершить регистрацию и войти в систему.
				</p>
				<div className="submitBtnWrapper">
					<Button onClick={onClose} className={`submitBtn ${styles.Btn}`}>
						ПОНЯТНО
					</Button>
				</div>
			</div>
		)
	}

	return (
		<>
			{/* Крестик закрытия */}
			<button className={styles.closeBtn} onClick={onClose} aria-label="Закрыть">
				&times;
			</button>
			<h2 className={styles.title}>Регистрация</h2>

			<form className="form" onSubmit={handleSubmit(onSubmit)} noValidate>
				{/* Email */}
				<div className={`inputGroup ${errors.email ? 'inputError' : ''}`.trim()}>
					<label>Email адрес:</label>
					<input
						type="email"
						placeholder="yavasyaivanov@gmail.com"
						{...register('email')}
					/>
					{errors.email && <span className="errorText">{errors.email.message}</span>}
				</div>

				{/* Password с подсказками */}
				<div className={`inputGroup ${errors.password ? 'inputError' : ''}`.trim()}>
					<label>Пароль:</label>
					<div className="passwordInputWrapper">
						<input
							type={showPassword ? 'text' : 'password'}
							placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱"
							autoComplete="new-password" // Защита от автозаполнения браузером
							{...passwordProps} // Передаем все базовые пропсы RHF
							onChange={(e) => {
								passwordProps.onChange(e)
								if (e.target.value.length === 0) setShowPassword(false)
							}}
							onFocus={() => setIsPasswordFocused(true)} // Показываем подсказку
							onBlur={(e) => {
								passwordProps.onBlur(e) // Вызываем родной onBlur от RHF
								setIsPasswordFocused(false) // Скрываем подсказку
							}}
						/>
						{/* Показываем кнопку только если в поле есть хотя бы 1 символ */}
						{passwordValue.length > 0 && (
							<button
								type="button"
								className="eyeBtn"
								onClick={() => setShowPassword(!showPassword)}
								tabIndex="-1" // Чтобы кнопка не мешала навигации клавишей Tab
							>
								{showPassword ? <ShowIcon /> : <HideIcon />}
							</button>
						)}

						{/* Компонент подсказок */}
						<PasswordHints password={passwordValue} isVisible={isPasswordFocused} />
					</div>
					{errors.password && (
						<span className="errorText">{errors.password.message}</span>
					)}
				</div>

				{/* Confirm Password */}
				<div
					className={`inputGroup ${errors.confirmPassword ? 'inputError' : ''}`.trim()}
				>
					<label>Повторите пароль:</label>
					<div className="passwordInputWrapper">
						<input
							type={showConfirm ? 'text' : 'password'}
							placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱"
							autoComplete="new-password" // Защита от автозаполнения браузером
							{...confirmProps}
							onChange={(e) => {
								confirmProps.onChange(e)
								if (e.target.value.length === 0) setShowConfirm(false)
							}}
						/>
						{/* Показываем кнопку только если в поле есть хотя бы 1 символ */}
						{confirmValue.length > 0 && (
							<button
								type="button"
								className="eyeBtn"
								onClick={() => setShowConfirm(!showConfirm)}
								tabIndex="-1" // Чтобы кнопка не мешала навигации клавишей Tab
							>
								{showConfirm ? <ShowIcon /> : <HideIcon />}
							</button>
						)}
					</div>
					{errors.confirmPassword && (
						<span className="errorText">{errors.confirmPassword.message}</span>
					)}
				</div>

				<div className="submitBtnWrapper">
					{/* Отключаем кнопку во время отправки запроса (isSubmitting) */}
					<Button
						type="submit"
						className={`submitBtn ${styles.Btn}`}
						disabled={isSubmitting}
					>
						{isSubmitting ? 'РЕГИСТРАЦИЯ...' : 'ЗАРЕГИСТРИРОВАТЬСЯ'}
					</Button>
				</div>
			</form>

			<div className={styles.toggleText}>
				Уже есть аккаунт?{' '}
				<button type="button" onClick={onSwitchToLogin} disabled={isSubmitting}>
					Вход
				</button>
			</div>
		</>
	)
}

export default RegisterForm
