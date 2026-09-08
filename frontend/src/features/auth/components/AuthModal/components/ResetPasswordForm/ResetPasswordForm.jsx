import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { resetSchema } from '@/features/auth/schemas/auth.schema'
import { requestPasswordReset } from '@/features/auth/api/auth.api'
import Button from '@/components/ui/Button'
import styles from './ResetPasswordForm.module.scss'

const ResetPasswordForm = ({ onBackToLogin }) => {
	const [isSuccess, setIsSuccess] = useState(false)
	const [serverError, setServerError] = useState('')

	// Инициализация формы и подключение схемы
	const {
		register,
		handleSubmit,
		getValues,
		formState: { errors, isSubmitting },
		// formState: { errors, isSubmitting, isValid }, // isValid - возвращает true, если поля заполнены правильно; isSubmitting - принимает значение true когда пользователь нажимает на кнопку отправки (и срабатывает функция handleSubmit(onSubmit)) и остаётся true пока выполняется запрос к серверу
	} = useForm({
		resolver: zodResolver(resetSchema),
		// mode: 'onChange', // Валидация на-лету (в реальном времени). Используем для isValid
		// mode: 'onSubmit', // Режим по-умолчанию. Проверка при отправке формы
		// mode: 'onTouched', // Проверка при потере фокуса полем
	})

	const onSubmit = async (data) => {
		setServerError('')
		try {
			await requestPasswordReset(data.email)
			setIsSuccess(true)
		} catch (err) {
			// Бэкенд возвращает 200 даже если email не найден (для безопасности),
			// но на случай 500-й ошибки или проблем с сетью обрабатываем catch
			setServerError(err.response?.data?.error || 'Произошла ошибка. Попробуйте позже.')
		}
	}

	// Если запрос успешен — показываем сообщение
	if (isSuccess) {
		return (
			<div className={styles.container}>
				<h2 className={styles.title}>ПРОВЕРЬТЕ ПОЧТУ</h2>
				<p className={styles.message}>
					Мы отправили инструкции по сбросу пароля на адрес:
					<br />
					<strong>{getValues('email')}</strong>
				</p>
				<p className={styles.submessage}>
					Если письмо не пришло в течение нескольких минут, проверьте папку «Спам».
				</p>
				<div className="submitBtnWrapper">
					<Button className="submitBtn" onClick={onBackToLogin}>
						ВЕРНУТЬСЯ
					</Button>
				</div>
			</div>
		)
	}

	return (
		<>
			<h2 className={styles.title}>ВОССТАНОВЛЕНИЕ ПАРОЛЯ</h2>
			<p className={styles.description}>
				Введите email, указанный при регистрации, и мы отправим вам письмо с инструкциями
				по сбросу пароля.
			</p>

			<form className="form" onSubmit={handleSubmit(onSubmit)} noValidate>
				<div className={`inputGroup ${errors.email ? 'inputError' : ''}`.trim()}>
					<label>Email:</label>
					<input
						type="email"
						placeholder="yavasyaivanov@gmail.com"
						{...register('email')}
					/>
					{errors.email && <span className="errorText">{errors.email.message}</span>}
				</div>

				{serverError && <div className="serverErrorMessage">{serverError}</div>}

				{/* Блокируем кнопку пока поле не будет правильно заполнено (isValid) и на время отправки запроса (isSubmitting) */}
				{/* <Button
				type="submit"
				className={styles.submitBtn}
				disabled={!isValid || isSubmitting}
			>
				{isSubmitting ? 'ОТПРАВКА...' : 'СБРОС ПАРОЛЯ'}
			</Button> */}

				<div className="submitBtnWrapper">
					{/* Блокируем кнопку на время отправки запроса (isSubmitting) */}
					<Button
						type="submit"
						className={`submitBtn ${styles.Btn}`}
						disabled={isSubmitting}
					>
						{isSubmitting ? 'ОТПРАВКА...' : 'СБРОС ПАРОЛЯ'}
					</Button>
				</div>
			</form>
			<div className={styles.backToLoginText}>
				<span>Вспомнили пароль? </span>
				<button type="button" onClick={onBackToLogin}>
					Вернуться
				</button>
			</div>
		</>
	)
}

export default ResetPasswordForm
