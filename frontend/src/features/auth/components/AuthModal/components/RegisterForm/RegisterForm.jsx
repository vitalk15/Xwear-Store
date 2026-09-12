import { useState } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { registerSchema } from '@/features/auth/schemas/auth.schema'
import { registerUser } from '@/features/auth/api/auth.api'
import Button from '@/components/ui/Button'
import InputField from '@/components/ui/InputField'
import PasswordInput from '@/components/ui/PasswordInput'
import PasswordHints from '@/features/auth/components/PasswordHints'
import styles from './RegisterForm.module.scss'

const RegisterForm = ({ onClose, onSwitchToLogin }) => {
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

	// Следим за полем пароля в реальном времени
	const passwordValue = useWatch({ control, name: 'password', defaultValue: '' })

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
				<InputField
					label="Email адрес:"
					type="email"
					placeholder="yavasyaivanov@gmail.com"
					error={errors.email}
					{...register('email')}
				/>

				{/* Password с подсказками */}
				<PasswordInput
					label="Пароль:"
					placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱"
					error={errors.password}
					onFocus={() => setIsPasswordFocused(true)} // Показываем подсказку
					{...register('password', {
						onBlur: () => setIsPasswordFocused(false), // Передаем onBlur в RHF и скрываем подсказку
					})}
				>
					{/* Компонент подсказок */}
					<PasswordHints password={passwordValue} isVisible={isPasswordFocused} />
				</PasswordInput>

				{/* Confirm Password */}
				<PasswordInput
					label="Повторите пароль:"
					placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱"
					error={errors.confirmPassword}
					{...register('confirmPassword')}
				/>

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
