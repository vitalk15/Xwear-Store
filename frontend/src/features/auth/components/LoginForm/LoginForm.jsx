import { useState } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { loginSchema } from '@/features/auth/schemas/auth.schema'
import Button from '@/components/ui/Button'
import CheckmarkIcon from '@/shared/icons/checkmark.svg'
import ShowIcon from '@/shared/icons/show.svg'
import HideIcon from '@/shared/icons/hide.svg'
import styles from './LoginForm.module.scss'

const LoginForm = ({ onClose, onSwitchToRegister }) => {
	// Состояния для показа/скрытия пароля
	const [showPassword, setShowPassword] = useState(false)

	// 1. Инициализация формы входа и подключение схемы
	const {
		register,
		handleSubmit,
		formState: { errors },
		control, // <-- для хука слежения useWatch
	} = useForm({
		resolver: zodResolver(loginSchema),
		defaultValues: { email: '', password: '', rememberMe: false },
		// mode: 'onTouched', // Проверка при потере фокуса полем
	})

	// Следим за полем пароля в реальном времени
	const passwordValue = useWatch({ control, name: 'password', defaultValue: '' })
	// Извлекаем пропсы регистрации пароля
	const passwordProps = register('password')

	// Обработчик отправки данных
	const onSubmit = (data) => {
		console.log('Отправка логина:', data)
		// TODO: Здесь будет вызов API DRF для получения JWT
		// TODO: Вызов экшена Zustand
	}

	return (
		<>
			{/* Крестик закрытия */}
			<button className={styles.closeBtn} onClick={onClose} aria-label="Закрыть">
				&times;
			</button>
			<h2 className={styles.title}>Войти</h2>

			<form className={styles.form} onSubmit={handleSubmit(onSubmit)} noValidate>
				{/* Email */}
				<div className={styles.inputGroup}>
					<label>Email адрес:</label>
					<input
						type="email"
						placeholder="yavasyaivanov@gmail.com"
						{...register('email')}
					/>
					{/* Вывод ошибки */}
					{errors.email && (
						<span className={styles.errorText}>{errors.email.message}</span>
					)}
				</div>

				{/* Password */}
				<div className={styles.inputGroup}>
					<label>Пароль:</label>
					<div className={styles.passwordInputWrapper}>
						<input
							type={showPassword ? 'text' : 'password'}
							placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱"
							autoComplete="new-password" // Защита от автозаполнения браузером
							{...passwordProps}
							onChange={(e) => {
								passwordProps.onChange(e) // Вызываем родной onChange от RHF
								if (e.target.value.length === 0) setShowPassword(false) // Логика сброса типа инпута
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
					</div>
					{/* Вывод ошибки */}
					{errors.password && (
						<span className={styles.errorText}>{errors.password.message}</span>
					)}
				</div>

				{/* Строка с чекбоксом и ссылкой восстановления */}
				<div className={styles.optionsRow}>
					<label className={styles.checkboxLabel}>
						{/* Нативный чекбокс скрыт, но сохраняет доступность для клавиатуры/скринридеров */}
						<input
							type="checkbox"
							className={styles.hiddenCheckbox}
							{...register('rememberMe')}
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
				<button type="button" onClick={onSwitchToRegister}>
					Регистрация
				</button>
			</div>
		</>
	)
}

export default LoginForm
