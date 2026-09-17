import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { editProfileSchema } from '@/features/profile/schemas/editProfileSchema'
import { useUpdateProfileMutation } from '@/features/profile/hooks/useProfile'
import InputField from '@/components/ui/InputField'
import { formatBelarusPhone } from '@/shared/utils/formatPhone'
import Button from '@/components/ui/Button'
import Toast from '@/components/ui/Toast'
import styles from './EditProfileForm.module.scss'

const EditProfileForm = ({ initialData }) => {
	const [toast, setToast] = useState(null) // Состояние для уведомлений
	const { mutate: updateProfile, isPending } = useUpdateProfileMutation()

	const {
		register,
		handleSubmit,
		formState: { errors, dirtyFields }, // dirtyFields для отправки на сервер только тех полей, которые были изменены (бэкенд принимает PATCH-запросы с флагом partial=True).
	} = useForm({
		resolver: zodResolver(editProfileSchema),
		defaultValues: {
			first_name: initialData?.profile?.first_name || '',
			last_name: initialData?.profile?.last_name || '',
			email: initialData?.email || '',
			phone: formatBelarusPhone(initialData?.profile?.phone) || '',
		},
	})

	const onSubmit = (formData) => {
		// Собираем только измененные поля
		const changedData = {}

		if (dirtyFields.first_name) changedData.first_name = formData.first_name
		if (dirtyFields.last_name) changedData.last_name = formData.last_name
		if (dirtyFields.phone) changedData.phone = formData.phone

		// Если пользователь ничего не изменил и нажал "Сохранить"
		if (Object.keys(changedData).length === 0) {
			setToast({ message: 'Данные не были изменены', type: 'success' })
			return
		}

		updateProfile(changedData, {
			onSuccess: () => {
				setToast({ message: 'Профиль успешно обновлен!', type: 'success' })
			},
			onError: () => {
				setToast({ message: 'Ошибка при сохранении данных', type: 'error' })
			},
		})
	}

	return (
		<>
			{toast && (
				<Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />
			)}

			<h2 className={styles.formTitle}>Редактирование профиля</h2>

			<form
				className={`form ${styles.profileForm}`}
				onSubmit={handleSubmit(onSubmit)}
				noValidate
			>
				<div className={styles.grid}>
					<InputField
						label="Ваше имя:"
						placeholder="Введите ваше имя"
						error={errors.first_name}
						{...register('first_name')}
					/>

					<InputField
						label="Фамилия:"
						placeholder="Введите вашу фамилию"
						error={errors.last_name}
						{...register('last_name')}
					/>

					<InputField
						label="Email адрес:"
						type="email"
						disabled
						error={errors.email}
						{...register('email')}
					/>

					<InputField
						label="Номер телефона:"
						placeholder="+375 29 0000000"
						error={errors.phone}
						{...register('phone')}
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

export default EditProfileForm
