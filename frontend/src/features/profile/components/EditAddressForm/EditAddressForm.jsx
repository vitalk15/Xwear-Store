import { useState } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { editAddressSchema } from '@/features/profile/schemas/editAddressSchema'
import {
	useCitiesQuery,
	useCreateAddressMutation,
} from '@/features/profile/hooks/useProfile'
import InputField from '@/components/ui/InputField'
import Button from '@/components/ui/Button'
import Toast from '@/components/ui/Toast'
import CustomSelect from '@/components/ui/CustomSelect'
import styles from './EditAddressForm.module.scss'

const EditAddressForm = () => {
	const [toast, setToast] = useState(null) // Состояние для уведомлений
	const { data: cities = [], isLoading: isCitiesLoading } = useCitiesQuery()
	const { mutate: createAddress, isPending } = useCreateAddressMutation()

	const {
		register,
		handleSubmit,
		reset,
		control,
		formState: { errors },
	} = useForm({
		resolver: zodResolver(editAddressSchema),
		defaultValues: {
			city_id: '',
			street: '',
			house: '',
			apartment: '',
		},
	})

	const onSubmit = (formData) => {
		createAddress(formData, {
			onSuccess: () => {
				setToast({ message: 'Адрес успешно сохранен!', type: 'success' })
				reset() // Очищаем форму после успешного сохранения
			},
			onError: () => {
				setToast({ message: 'Ошибка при сохранении адреса', type: 'error' })
			},
		})
	}

	return (
		<>
			{toast && (
				<Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />
			)}

			<h2 className={styles.formTitle}>Редактирование адреса</h2>

			<form
				className={`form ${styles.addressForm}`}
				onSubmit={handleSubmit(onSubmit)}
				noValidate
			>
				<div className={styles.grid}>
					{/* Кастомное поле выбора города */}
					{/* <div className={`inputGroup ${errors.city_id ? 'inputError' : ''}`.trim()}>
						<label>Город</label>
						<select
							className={`${styles.selectInput} ${
								errors.city_id ? styles.selectError : ''
							}`.trim()}
							disabled={isCitiesLoading}
							{...register('city_id')}
						>
							<option value="" disabled>
								{isCitiesLoading ? 'Загрузка городов...' : 'Выберите ваш город'}
							</option>
							{cities.map((city) => (
								<option key={city.id} value={city.id}>
									{city.name}
								</option>
							))}
						</select>
						{errors.city_id && (
							<span className="errorText">{errors.city_id.message}</span>
						)}
					</div> */}

					<Controller
						name="city_id"
						control={control}
						render={({ field }) => (
							<CustomSelect
								options={cities}
								value={field.value}
								onChange={field.onChange}
								placeholder={isCitiesLoading ? 'Загрузка...' : 'Выберите ваш город'}
								error={errors.city_id}
								disabled={isCitiesLoading}
							/>
						)}
					/>

					<InputField
						label="Улица:"
						placeholder="Введите название улицы"
						error={errors.street}
						{...register('street')}
					/>

					<InputField
						label="Номер дома:"
						placeholder="Введите номер дома"
						error={errors.house}
						{...register('house')}
					/>

					<InputField
						label="Номер квартиры:"
						placeholder="Введите номер квартиры (необязательно)"
						error={errors.apartment}
						{...register('apartment')}
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

export default EditAddressForm
