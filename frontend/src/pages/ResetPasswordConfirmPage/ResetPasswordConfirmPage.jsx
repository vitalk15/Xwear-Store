import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useForm, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { confirmResetSchema } from '@/features/auth/schemas/auth.schema'
import { confirmPasswordReset } from '@/features/auth/api/auth.api'
import { paths } from '@/routes/paths'
import PageTitle from '@/components/common/PageTitle'
import Button from '@/components/ui/Button'
import PasswordHints from '@/features/auth/components/PasswordHints'
import ShowIcon from '@/shared/icons/show.svg'
import HideIcon from '@/shared/icons/hide.svg'
import styles from './ResetPasswordConfirmPage.module.scss'

const ResetPasswordConfirmPage = () => {
	const { uid, token } = useParams()
	const [isSuccess, setIsSuccess] = useState(false)
	const [serverError, setServerError] = useState('')
	const navigate = useNavigate()
	// Состояния для показа/скрытия паролей
	const [showPassword, setShowPassword] = useState(false)
	const [showConfirm, setShowConfirm] = useState(false)
	// Состояние фокуса на поле пароля
	const [isPasswordFocused, setIsPasswordFocused] = useState(false)

	const {
		register,
		handleSubmit,
		formState: { errors, isSubmitting },
		control,
	} = useForm({
		resolver: zodResolver(confirmResetSchema),
		defaultValues: { password: '', confirmPassword: '' },
	})

	// Следим за полями паролей в реальном времени
	const passwordValue = useWatch({ control, name: 'password', defaultValue: '' })
	const confirmValue = useWatch({ control, name: 'confirmPassword', defaultValue: '' })

	// Извлекаем пропсы регистрации паролей
	const passwordProps = register('password')
	const confirmProps = register('confirmPassword')

	// Обработчик отправки данных
	const onSubmit = async (data) => {
		setServerError('')
		try {
			// Маппинг: передаем данные из формы (data.password) в ключи, которые ждет API (new_password)
			await confirmPasswordReset({
				uid,
				token,
				new_password: data.password,
				new_password_confirm: data.confirmPassword,
			})
			setIsSuccess(true)
		} catch (err) {
			const errorMsg =
				err.response?.data?.non_field_errors?.[0] ||
				err.response?.data?.detail ||
				'Ссылка недействительна или её срок действия истёк.'
			setServerError(errorMsg)
		}
	}

	if (isSuccess) {
		return (
			<>
				<PageTitle title="Сброс пароля" />

				<div className={styles.wrapper}>
					<div className={styles.card}>
						<h1 className={styles.title}>ПАРОЛЬ УСПЕШНО ИЗМЕНЁН!</h1>
						<p className={styles.description}>
							Теперь вы можете войти в свой аккаунт, используя новый пароль.
						</p>
						<div className={styles.submitBtnWrapper}>
							<Button className="submitBtn" onClick={() => navigate(paths.home)}>
								НА ГЛАВНУЮ
							</Button>
						</div>
					</div>
				</div>
			</>
		)
	}

	return (
		<>
			<PageTitle title="Сброс пароля" />

			<div className="container">
				<div className={styles.wrapper}>
					<form className={styles.form} onSubmit={handleSubmit(onSubmit)} noValidate>
						<h1 className={styles.title}>УСТАНОВКА НОВОГО ПАРОЛЯ</h1>
						<div className={`inputGroup ${errors.password ? 'inputError' : ''}`.trim()}>
							<label>Новый пароль:</label>
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

						<div
							className={`inputGroup ${errors.confirmPassword ? 'inputError' : ''}`.trim()}
						>
							<label>Подтвердите новый пароль:</label>
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

						{/* Вывод ошибки сервера */}
						{serverError && <div className="serverErrorMessage">{serverError}</div>}

						<div className="submitBtnWrapper">
							<Button
								type="submit"
								className={`submitBtn ${styles.Btn}`}
								disabled={isSubmitting}
							>
								{isSubmitting ? 'СОХРАНЕНИЕ...' : 'СОХРАНИТЬ'}
							</Button>
						</div>
					</form>
				</div>
			</div>
		</>
	)
}

export default ResetPasswordConfirmPage
