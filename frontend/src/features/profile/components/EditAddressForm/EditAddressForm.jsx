import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { editAddressSchema } from '@/features/profile/schemas/editAddressSchema'
import {
	useCitiesQuery,
	useCreateAddressMutation,
	useUpdateAddressMutation,
} from '@/features/profile/hooks/useProfile'
import InputField from '@/components/ui/InputField'
import Button from '@/components/ui/Button'
import CustomSelect from '@/components/ui/CustomSelect'
import styles from './EditAddressForm.module.scss'

const EditAddressForm = ({ editingAddress, onSuccess, onError }) => {
	const { data: cities = [], isLoading: isCitiesLoading } = useCitiesQuery()

	const { mutate: createAddress, isPending: isCreating } = useCreateAddressMutation()
	const { mutate: updateAddress, isPending: isUpdating } = useUpdateAddressMutation()

	const isEditMode = Boolean(editingAddress)
	const isLoading = isCreating || isUpdating

	const {
		register,
		handleSubmit,
		reset,
		control,
		formState: { errors },
	} = useForm({
		resolver: zodResolver(editAddressSchema),
		defaultValues: {
			city_id: editingAddress?.city?.id || '',
			street: editingAddress?.street || '',
			house: editingAddress?.house || '',
			apartment: editingAddress?.apartment || '',
		},
	})

	const onSubmit = (formData) => {
		if (isEditMode) {
			updateAddress(
				{ id: editingAddress.id, ...formData },
				{
					onSuccess: () => {
						if (onSuccess) onSuccess('Адрес успешно обновлен!') // Передаем текст в родителя
					},
					onError: () => {
						if (onError) onError('Ошибка при обновлении адреса')
					},
				},
			)
		} else {
			createAddress(formData, {
				onSuccess: () => {
					reset() // Очищаем форму после успешного сохранения
					if (onSuccess) onSuccess('Адрес успешно добавлен!')
				},
				onError: () => {
					if (onError) onError('Ошибка при добавлении адреса')
				},
			})
		}
	}

	return (
		<>
			<h2 className={styles.formTitle}>
				{isEditMode ? 'Редактирование адреса' : 'Добавление адреса'}
			</h2>

			<form
				className={`form ${styles.addressForm}`}
				onSubmit={handleSubmit(onSubmit)}
				noValidate
			>
				<div className={styles.grid}>
					{/* Кастомный селект выбора города */}
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
						label="Улица / Проспект / Переулок:"
						placeholder="Например: пр-т Независимости"
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
						disabled={isLoading}
						className={`submitBtn ${styles.Btn}`}
					>
						{isLoading ? 'СОХРАНЕНИЕ...' : 'СОХРАНИТЬ'}
					</Button>
				</div>
			</form>
		</>
	)
}

export default EditAddressForm
