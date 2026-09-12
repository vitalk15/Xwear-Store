import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useForm, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { confirmResetSchema } from '@/features/auth/schemas/auth.schema'
import { confirmPasswordReset } from '@/features/auth/api/auth.api'
import { paths } from '@/routes/paths'
import PageTitle from '@/components/common/PageTitle'
import Button from '@/components/ui/Button'
import PasswordInput from '@/components/ui/PasswordInput'
import PasswordHints from '@/features/auth/components/PasswordHints'
import styles from './ResetPasswordConfirmPage.module.scss'

const ResetPasswordConfirmPage = () => {
	const { uid, token } = useParams()
	const navigate = useNavigate()

	const [isSuccess, setIsSuccess] = useState(false)
	const [serverError, setServerError] = useState('')

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

	// Следим за полем пароля в реальном времени
	const passwordValue = useWatch({ control, name: 'password', defaultValue: '' })

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

						<PasswordInput
							label="Новый пароль:"
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

						<PasswordInput
							label="Подтвердите новый пароль:"
							placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱"
							error={errors.confirmPassword}
							{...register('confirmPassword')}
						/>

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
