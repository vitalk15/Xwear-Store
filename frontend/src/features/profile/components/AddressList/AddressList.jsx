import {
	useUpdateAddressMutation,
	useDeleteAddressMutation,
} from '@/features/profile/hooks/useProfile'
import { formatBelarusPhone } from '@/shared/utils/formatPhone'
import AddIcon from '@/shared/icons/add.svg'
import EditIcon from '@/shared/icons/edit.svg'
import DeleteIcon from '@/shared/icons/delete2.svg'
import styles from './AddressList.module.scss'

const AddressList = ({
	profileData,
	onEditAddress,
	onAddNewAddress,
	onSuccess,
	onError,
}) => {
	const { mutate: updateAddress } = useUpdateAddressMutation()
	const { mutate: deleteAddress } = useDeleteAddressMutation()

	const addresses = profileData?.profile?.addresses || []
	const userFullName =
		`${profileData?.profile?.first_name || ''} ${profileData?.profile?.last_name || ''}`.trim() ||
		'Пользователь'
	const userPhone = formatBelarusPhone(profileData?.profile?.phone)
	const userEmail = profileData?.email

	const handleSetDefault = (addressId, isCurrentDefault) => {
		if (isCurrentDefault) return
		updateAddress(
			{ id: addressId, is_default: true },
			{
				onSuccess: () => onSuccess && onSuccess('Основной адрес изменен'),
				onError: () => onError && onError('Ошибка изменения адреса'),
			},
		)
	}

	const handleDelete = (e, addressId) => {
		e.stopPropagation() // Предотвращаем срабатывание выбора адреса по умолчанию
		deleteAddress(addressId, {
			onSuccess: () => onSuccess && onSuccess('Адрес удален'),
			onError: () => onError && onError('Ошибка удаления адреса'),
		})
	}

	return (
		<>
			<h2 className={styles.title}>Мои адреса</h2>

			<div className={styles.container}>
				<div className={styles.grid}>
					{addresses.map((address, index) => {
						const isDefault =
							address.is_default || (index === 0 && !addresses.some((a) => a.is_default))

						return (
							<div
								key={address.id}
								className={`${styles.card} ${isDefault ? styles.defaultCard : ''}`}
								onClick={() => handleSetDefault(address.id, isDefault)}
							>
								{/* Бейдж с номером адреса */}
								<div
									className={`${styles.badge} ${isDefault ? styles.defaultBadge : ''}`}
								>
									АДРЕС ДОСТАВКИ #{index + 1}
								</div>

								<div className={styles.cardContent}>
									<h3 className={styles.userName}>{userFullName}</h3>
									<p className={styles.addressText}>
										{address.city?.name}, {address.address_simple}
									</p>

									{userPhone && (
										<div className={styles.infoBlock}>
											<span className={styles.infoLabel}>Телефон</span>
											<span className={styles.infoValue}>{userPhone}</span>
										</div>
									)}

									{userEmail && (
										<div className={styles.infoBlock}>
											<span className={styles.infoLabel}>Email</span>
											<span className={styles.infoValue}>{userEmail}</span>
										</div>
									)}
								</div>

								{/* Действия с карточкой */}
								<div className={styles.cardActions}>
									<button
										type="button"
										className={styles.actionBtn}
										onClick={(e) => {
											e.stopPropagation()
											onEditAddress(address)
										}}
									>
										<EditIcon className={styles.editIcon} />
										<span className={styles.actionText}>Редактировать</span>
									</button>
									<button
										type="button"
										className={`${styles.actionBtn} ${styles.deleteBtn}`}
										onClick={(e) => handleDelete(e, address.id)}
									>
										<DeleteIcon className={styles.deleteIcon} />
										<span className={styles.actionText}>Удалить</span>
									</button>
								</div>
							</div>
						)
					})}
				</div>

				{/* Кнопка с пунктирной рамкой «Добавить новый» */}
				<button type="button" className={styles.addCardBtn} onClick={onAddNewAddress}>
					<div className={styles.addIconWrapper}>
						<AddIcon className={styles.addIcon} />
					</div>
					<span className={styles.addText}>Добавить новый</span>
				</button>
			</div>
		</>
	)
}

export default AddressList
