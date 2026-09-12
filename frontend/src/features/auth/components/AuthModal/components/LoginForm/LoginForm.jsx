import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { loginSchema } from '@/features/auth/schemas/auth.schema'
import { loginUser } from '@/features/auth/api/auth.api'
import useAuthStore from '@/features/auth/store/useAuthStore'
import InputField from '@/components/ui/InputField'
import PasswordInput from '@/components/ui/PasswordInput'
import Button from '@/components/ui/Button'
import styles from './LoginForm.module.scss'

const LoginForm = ({ onClose, onSwitchToRegister, onForgotPassword }) => {
	// Достаем функцию сохранения данных из Zustand-стора
	const setAuth = useAuthStore((state) => state.setAuth)

	// Инициализация формы входа и подключение схемы
	const {
		register,
		handleSubmit,
		formState: { errors, isSubmitting }, // isSubmitting - принимает значение true когда пользователь нажимает на кнопку отправки (и срабатывает функция handleSubmit(onSubmit)) и остаётся true пока выполняется запрос к серверу
		setError,
	} = useForm({
		resolver: zodResolver(loginSchema),
		defaultValues: { email: '', password: '' },
		// defaultValues: { email: '', password: '', rememberMe: false },
		// mode: 'onSubmit', // Режим по-умолчанию. Проверка при отправке формы
		// mode: 'onTouched', // Проверка при потере фокуса полем
		// mode: 'onChange', // Режим реального времени
	})

	// Обработчик отправки данных
	const onSubmit = async (data) => {
		// Отправляем (маппим) данные, которые ожидает бэкенд
		try {
			const response = await loginUser({
				email: data.email,
				password: data.password,
			})

			// Если запрос успешен, сохраняем user и access-токен в Zustand
			setAuth({
				user: response.user,
				access: response.access,
			})

			// Закрываем модальное окно после успешного входа
			onClose()
		} catch (error) {
			if (
				error.response &&
				(error.response.status === 401 || error.response.status === 400)
			) {
				// Достаем ошибку от бэкенда (если она есть)
				const backendDetail =
					error.response.data.detail ||
					(error.response.data.non_field_errors &&
						error.response.data.non_field_errors[0])

				// Задаем базовое сообщение
				let errorMessage = 'Неверный email или пароль'

				// Если пришла стандартная английская ошибка SimpleJWT — подменяем её на нашу
				if (backendDetail === 'No active account found with the given credentials') {
					errorMessage
				} else if (backendDetail) {
					// Если пришла какая-то другая ошибка (например, кастомная с бэкенда), выводим её
					errorMessage = backendDetail
				}

				// Устанавливаем "корневую" ошибку формы, так как мы не знаем, где именно ошибся юзер (в email или пароле)
				setError('root.serverError', {
					type: 'server',
					message: errorMessage,
				})
			} else {
				setError('root.serverError', {
					type: 'server',
					message: 'Ошибка при подключении к серверу. Попробуйте позже.',
				})
			}
		}
	}

	return (
		<>
			{/* Крестик закрытия */}
			<button className={styles.closeBtn} onClick={onClose} aria-label="Закрыть">
				&times;
			</button>
			<h2 className={styles.title}>Войти</h2>

			<form className="form" onSubmit={handleSubmit(onSubmit)} noValidate>
				{/* Вывод общей ошибки сервера (например, "Неверный email или пароль") */}
				{errors.root?.serverError && (
					<div className="serverErrorMessage">{errors.root.serverError.message}</div>
				)}

				{/* Email */}
				<InputField
					label="Email адрес:"
					type="email"
					placeholder="yavasyaivanov@gmail.com"
					error={errors.email}
					{...register('email')}
				/>

				{/* Password */}
				<PasswordInput
					label="Пароль:"
					placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱"
					error={errors.password}
					{...register('password')}
				/>

				{/* Строка с чекбоксом и ссылкой восстановления */}
				<div className={styles.optionsRow}>
					{/* <label className={styles.checkboxLabel}> */}
					{/* Нативный чекбокс скрыт, но сохраняет доступность для клавиатуры/скринридеров */}
					{/* <input
							type="checkbox"
							className={styles.hiddenCheckbox}
							{...register('rememberMe')}
						/> */}
					{/* <span className={styles.customCheckbox}>
							<CheckmarkIcon className={styles.checkmark} />
						</span> */}
					{/* <span>Запомнить меня</span> */}
					{/* </label> */}
					<button type="button" onClick={onForgotPassword} className={styles.forgotLink}>
						Забыли пароль?
					</button>
				</div>
				<div className="submitBtnWrapper">
					{/* Блокируем кнопку на время отправки запроса (isSubmitting) */}
					<Button
						type="submit"
						className={`submitBtn ${styles.Btn}`}
						disabled={isSubmitting}
					>
						{isSubmitting ? 'ВХОД...' : 'ВОЙТИ'}
					</Button>
				</div>
			</form>

			<div className={styles.toggleText}>
				<span>Нет аккаунта? </span>
				<button type="button" onClick={onSwitchToRegister} disabled={isSubmitting}>
					Регистрация
				</button>
			</div>
		</>
	)
}

export default LoginForm
