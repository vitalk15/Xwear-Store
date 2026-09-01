import { useState } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { registerSchema } from '@/features/auth/schemas/auth.schema'
import Button from '@/components/ui/Button'
import PasswordHints from '../PasswordHints'
import ShowIcon from '@/shared/icons/show.svg'
import HideIcon from '@/shared/icons/hide.svg'
import styles from './RegisterForm.module.scss'

const RegisterForm = ({ onClose, onSwitchToLogin }) => {
	// Состояния для показа/скрытия паролей
	const [showPassword, setShowPassword] = useState(false)
	const [showConfirm, setShowConfirm] = useState(false)

	// Состояние фокуса на поле пароля
	const [isPasswordFocused, setIsPasswordFocused] = useState(false)

	// Инициализация формы регистрации и подключение схемы
	const {
		register,
		handleSubmit,
		formState: { errors },
		control, // <-- для хука слежения useWatch
	} = useForm({
		resolver: zodResolver(registerSchema),
		defaultValues: { email: '', password: '', confirmPassword: '' },
		// mode: 'onTouched', // Проверка при потере фокуса полем
	})

	// Следим за полями паролей в реальном времени
	const passwordValue = useWatch({ control, name: 'password', defaultValue: '' })
	const confirmValue = useWatch({ control, name: 'confirmPassword', defaultValue: '' })

	// Извлекаем пропсы регистрации паролей
	const passwordProps = register('password')
	const confirmProps = register('confirmPassword')

	// Обработчик отправки данных
	const onSubmit = (data) => {
		console.log('Отправка регистрации:', data)
		// TODO: Здесь будет вызов API DRF для получения JWT
		// TODO: Вызов экшена Zustand
	}

	return (
		<>
			{/* Крестик закрытия */}
			<button className={styles.closeBtn} onClick={onClose} aria-label="Закрыть">
				&times;
			</button>
			<h2 className={styles.title}>Регистрация</h2>

			<form className={styles.form} onSubmit={handleSubmit(onSubmit)} noValidate>
				{/* Email */}
				<div className={styles.inputGroup}>
					<label>Email адрес:</label>
					<input
						type="email"
						placeholder="yavasyaivanov@gmail.com"
						{...register('email')}
					/>
					{errors.email && (
						<span className={styles.errorText}>{errors.email.message}</span>
					)}
				</div>

				{/* Password с подсказками */}
				<div className={styles.inputGroup}>
					<label>Пароль:</label>
					<div className={styles.passwordInputWrapper}>
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
								className={styles.eyeBtn}
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
						<span className={styles.errorText}>{errors.password.message}</span>
					)}
				</div>

				{/* Confirm Password */}
				<div className={styles.inputGroup}>
					<label>Повторите пароль:</label>
					<div className={styles.passwordInputWrapper}>
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
								className={styles.eyeBtn}
								onClick={() => setShowConfirm(!showConfirm)}
								tabIndex="-1" // Чтобы кнопка не мешала навигации клавишей Tab
							>
								{showConfirm ? <ShowIcon /> : <HideIcon />}
							</button>
						)}
					</div>
					{errors.confirmPassword && (
						<span className={styles.errorText}>{errors.confirmPassword.message}</span>
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
				<button type="button" onClick={onSwitchToLogin}>
					Вход
				</button>
			</div>
		</>
	)
}

export default RegisterForm
