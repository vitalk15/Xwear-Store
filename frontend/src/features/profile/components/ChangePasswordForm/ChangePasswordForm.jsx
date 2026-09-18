import { useState } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { changePasswordSchema } from '@/features/profile/schemas/changePasswordSchema'
import { useChangePasswordMutation } from '@/features/profile/hooks/useProfile'
import PasswordInput from '@/components/ui/PasswordInput'
import PasswordHints from '@/features/auth/components/PasswordHints'
import Button from '@/components/ui/Button'
import styles from './ChangePasswordForm.module.scss'

const ChangePasswordForm = ({ onSuccess, onError }) => {
	const { mutate: changePassword, isPending } = useChangePasswordMutation()

	// Состояние фокуса на поле пароля
	const [isPasswordFocused, setIsPasswordFocused] = useState(false)
	// Ключ для принудительного сброса внутренних состояний PasswordInput
	const [resetKey, setResetKey] = useState(0)

	const {
		register,
		handleSubmit,
		control,
		reset,
		setError,
		formState: { errors },
	} = useForm({
		resolver: zodResolver(changePasswordSchema),
		defaultValues: {
			old_password: '',
			new_password: '',
			new_password_confirm: '',
		},
	})

	// Следим за полем пароля в реальном времени
	const newPasswordValue = useWatch({ control, name: 'new_password', defaultValue: '' })

	const onSubmit = (formData) => {
		changePassword(formData, {
			onSuccess: (response) => {
				reset() // Очищаем значения полей в RHF
				setIsPasswordFocused(false) // Скрываем подсказки
				setResetKey((prev) => prev + 1) // Перемонтируем инпуты (сбрасывает глазик в closed / type="password")

				if (onSuccess) onSuccess(response?.message || 'Пароль успешно изменён!')
			},
			onError: (error) => {
				const serverErrors = error.response?.data

				// Если бэкенд вернул ошибку конкретного поля (например, неверный старый пароль)
				if (serverErrors && typeof serverErrors === 'object') {
					Object.keys(serverErrors).forEach((field) => {
						const message = Array.isArray(serverErrors[field])
							? serverErrors[field][0]
							: serverErrors[field]

						if (
							['old_password', 'new_password', 'new_password_confirm'].includes(field)
						) {
							setError(field, { type: 'server', message })
						}
					})

					if (serverErrors.non_field_errors) {
						if (onError) onError(serverErrors.non_field_errors[0])
						return
					}
				}

				if (onError) onError('Не удалось изменить пароль. Проверьте введенные данные.')
			},
		})
	}

	return (
		<>
			<h2 className={styles.formTitle}>Смена пароля</h2>
			<form
				className={`form ${styles.changeForm}`}
				onSubmit={handleSubmit(onSubmit)}
				noValidate
			>
				<div className={styles.grid}>
					<PasswordInput
						key={`old_${resetKey}`}
						label="Текущий пароль:"
						placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱"
						error={errors.old_password}
						{...register('old_password')}
					/>

					<PasswordInput
						key={`new_${resetKey}`}
						label="Новый пароль:"
						placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱"
						error={errors.new_password}
						onFocus={() => setIsPasswordFocused(true)} // Показываем подсказку
						{...register('new_password', {
							onBlur: () => setIsPasswordFocused(false), // Передаем onBlur в RHF и скрываем подсказку
						})}
					>
						{/* Компонент подсказок */}
						<PasswordHints password={newPasswordValue} isVisible={isPasswordFocused} />
					</PasswordInput>

					<PasswordInput
						key={`confirm_${resetKey}`}
						label="Новый пароль еще раз:"
						placeholder="✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱✱"
						error={errors.new_password_confirm}
						{...register('new_password_confirm')}
					/>
				</div>

				<div className={styles.submitBtnWrapper}>
					<Button
						type="submit"
						disabled={isPending}
						className={`submitBtn ${styles.Btn}`}
					>
						{isPending ? 'СОХРАНЕНИЕ...' : 'СОХРАНИТЬ'}
					</Button>
				</div>
			</form>
		</>
	)
}

export default ChangePasswordForm
