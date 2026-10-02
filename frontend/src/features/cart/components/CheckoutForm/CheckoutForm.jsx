import { useState, useEffect, useMemo } from 'react'
import { useForm, useWatch, Controller } from 'react-hook-form'
import { motion as Motion } from 'framer-motion'
import { useProfileQuery } from '@/features/profile/hooks/useProfile'
import { usePickupPointsQuery, useCitiesQuery } from '@/features/orders/hooks/useOrders'
import { useToastStore } from '@/shared/store/useToastStore'
import CustomSelect from '@/components/ui/CustomSelect'
import EditAddressForm from '@/features/profile/components/EditAddressForm'
// import Toast from '@/components/ui/Toast'
import styles from './CheckoutForm.module.scss'

const CheckoutForm = ({ onDeliveryInfoChange, onSubmitOrder }) => {
	// 1. Данные профиля (адреса)
	const { data: profileData, isLoading: isProfileLoading } = useProfileQuery()

	// Мемоизируем (кешируем) адреса, опираясь на profileData
	const addresses = useMemo(() => {
		const profile = profileData?.profile || profileData
		return profile?.addresses || []
	}, [profileData])

	// Телефон (это строка, поэтому useMemo для нее не обязателен)
	const userPhone = profileData?.profile?.phone || profileData?.phone || ''

	// 2. Данные ПВЗ и Городов
	const { data: pickupPoints = [], isLoading: isLoadingPickups } = usePickupPointsQuery()
	const { data: cities = [], isLoading: isCitiesLoading } = useCitiesQuery()

	// Состояние: режим добавления нового адреса
	const [isAddingNew, setIsAddingNew] = useState(false)

	// Достаем глобальный метод уведомлений (локальный toastMessage удален)
	const showToast = useToastStore((state) => state.showToast)

	// ВЫЧИСЛЯЕМ НАЧАЛЬНЫЕ ЗНАЧЕНИЯ ДО ИНИЦИАЛИЗАЦИИ ФОРМЫ
	// Чтобы убрать дёргание анимации, когда city_id ещё пустой
	const initialCityAndAddress = useMemo(() => {
		if (!cities.length) return { cityId: '', addressId: null }

		if (addresses.length > 0) {
			const defaultAddr = addresses.find((a) => a.is_default) || addresses[0]
			const defaultCityId =
				defaultAddr.city_details?.id || defaultAddr.city?.id || defaultAddr.city
			if (defaultCityId) {
				return { cityId: String(defaultCityId), addressId: defaultAddr.id }
			}
		}

		return { cityId: String(cities[0].id), addressId: null }
	}, [cities, addresses])

	const {
		control,
		handleSubmit,
		setValue,
		formState: { errors },
	} = useForm({
		defaultValues: {
			delivery_method: 'delivery', // 'delivery' | 'pickup'
			payment_method: 'upon_receipt', // 'upon_receipt' | 'online'
			city_id: initialCityAndAddress.cityId, // ID доступного города
			address_id: initialCityAndAddress.addressId, // ID сохраненного адреса (если выбрана доставка)
			pickup_point_id: null, // ID ПВЗ (если выбран самовывоз)
		},
	})

	// Следим за тем, какой способ доставки выбран в реальном времени и др.
	const currentMethod = useWatch({ control, name: 'delivery_method' })
	const currentPayment = useWatch({ control, name: 'payment_method' })
	const selectedCityId = useWatch({ control, name: 'city_id' })
	const selectedAddressId = useWatch({ control, name: 'address_id' })
	const selectedPickupId = useWatch({ control, name: 'pickup_point_id' })

	// Синхронизируем форму, если данные загрузились чуть позже монтирования
	useEffect(() => {
		if (!selectedCityId && initialCityAndAddress.cityId) {
			setValue('city_id', initialCityAndAddress.cityId)
			if (initialCityAndAddress.addressId) {
				setValue('address_id', initialCityAndAddress.addressId)
			}
		}
	}, [initialCityAndAddress, selectedCityId, setValue])

	// Объект выбранного города
	const currentCityObj = useMemo(() => {
		return cities.find((c) => String(c.id) === String(selectedCityId)) || null
	}, [cities, selectedCityId])

	// Сохранённые адреса, отфильтрованные по выбранному городу
	const filteredAddresses = useMemo(() => {
		if (!selectedCityId) return []
		return addresses.filter((addr) => {
			const addrCityId = addr.city_details?.id || addr.city?.id || addr.city
			return String(addrCityId) === String(selectedCityId)
		})
	}, [addresses, selectedCityId])

	// Форматирование опций адресов для CustomSelect
	const addressOptions = useMemo(() => {
		return filteredAddresses.map((addr) => ({
			id: addr.id,
			name: `${addr.address_simple} ${addr.is_default ? '(Основной)' : ''}`,
		}))
	}, [filteredAddresses])

	// Автоматический выбор адреса при смене города
	useEffect(() => {
		if (currentMethod === 'delivery' && !isAddingNew) {
			if (filteredAddresses.length > 0) {
				const existsInFiltered = filteredAddresses.some(
					(a) => a.id === Number(selectedAddressId),
				)
				if (!existsInFiltered) {
					const defaultInCity =
						filteredAddresses.find((a) => a.is_default) || filteredAddresses[0]
					setValue('address_id', defaultInCity.id)
				}
			} else {
				setValue('address_id', null)
			}
		}
	}, [
		filteredAddresses,
		selectedCityId,
		currentMethod,
		isAddingNew,
		selectedAddressId,
		setValue,
	])

	// ПВЗ, отфильтрованные по выбранному городу
	const filteredPickupPoints = useMemo(() => {
		if (!currentCityObj) return []
		return pickupPoints.filter((point) => {
			if (point.city) return String(point.city) === String(currentCityObj.id)
			return point.city_name?.toLowerCase() === currentCityObj.name?.toLowerCase()
		})
	}, [pickupPoints, currentCityObj])

	// Форматирование опций ПВЗ для CustomSelect
	const pickupOptions = useMemo(() => {
		return filteredPickupPoints.map((point) => ({
			id: point.id,
			name: `ПВЗ №${point.id}: ${point.address} (${point.work_schedule})`,
		}))
	}, [filteredPickupPoints])

	// Эффект для сохранения выбранного ПВЗ в localStorage
	useEffect(() => {
		if (selectedPickupId) {
			localStorage.setItem('lastUsedPickupPoint', selectedPickupId)
		}
	}, [selectedPickupId])

	// Автоматический выбор сохраненного из localStorage ПВЗ при смене города
	useEffect(() => {
		if (currentMethod === 'pickup') {
			if (filteredPickupPoints.length > 0) {
				// Считываем сохраненный ID из памяти браузера
				const savedPointId = localStorage.getItem('lastUsedPickupPoint')

				// Проверяем, существует ли сохраненный ПВЗ или текущий выпадающий в выбранном городе
				const savedExists = filteredPickupPoints.some(
					(p) => p.id === Number(savedPointId),
				)
				const currentExists = filteredPickupPoints.some(
					(p) => p.id === Number(selectedPickupId),
				)

				if (savedExists) {
					// Выбираем ранее использованный ПВЗ
					setValue('pickup_point_id', Number(savedPointId))
				} else if (!currentExists) {
					// Пользователь сменил город (где нет старого ПВЗ) или покупает впервые — выбираем первый из списка
					setValue('pickup_point_id', filteredPickupPoints[0].id)
				}
			} else {
				setValue('pickup_point_id', null)
			}
		}
	}, [filteredPickupPoints, selectedCityId, currentMethod, selectedPickupId, setValue])

	// Передача актуального города в CartData для расчёта стоимости доставки
	useEffect(() => {
		onDeliveryInfoChange?.({
			deliveryMethod: currentMethod,
			selectedCity: currentCityObj,
		})
	}, [currentMethod, currentCityObj, onDeliveryInfoChange])

	// Обработчик успешного создания адреса в EditAddressForm
	const handleAddressCreated = (message) => {
		setIsAddingNew(false)
		// Если сообщение пришло, показываем Toast
		if (typeof message === 'string') {
			showToast(message, 'success')
		}
	}

	// Показываем форму добавления адреса ТОЛЬКО если:
	// 1. Пользователь сам нажал "+ Указать другой адрес" (isAddingNew === true)
	// 2. ИЛИ загрузка завершилась и у пользователя ВООБЩЕ 0 адресов в системе
	const showAddAddressForm = isAddingNew || (!isProfileLoading && addresses.length === 0)

	// Проверка телефона при доставке курьером
	const isPhoneMissingForDelivery =
		currentMethod === 'delivery' && !isProfileLoading && !userPhone

	const handleFormSubmit = (formData) => {
		if (isPhoneMissingForDelivery) {
			showToast('Для курьерской доставки укажите номер телефона в профиле', 'error')
			return
		}
		onSubmitOrder?.(formData)
	}

	// Флаг загрузки для секции доставки
	const isDeliveryLoading = isProfileLoading || !selectedCityId

	return (
		<Motion.div
			initial={{ opacity: 0, x: -20 }}
			animate={{ opacity: 1, x: 0 }}
			exit={{ opacity: 0, x: -20 }}
			className={styles.formContainer}
		>
			{/* {toastMessage && (
				<Toast
					message={toastMessage}
					type={isPhoneMissingForDelivery ? 'error' : 'success'}
					onClose={() => setToastMessage(null)}
				/>
			)} */}

			{!showAddAddressForm ? (
				<form id="checkout-form" onSubmit={handleSubmit(handleFormSubmit)}>
					<div className={styles.topFormWrapper}>
						{/* ПЕРЕКЛЮЧАТЕЛЬ СПОСОБА ПОЛУЧЕНИЯ */}
						<div className={styles.toggleGroup}>
							<button
								type="button"
								className={`${styles.toggleBtn} ${currentMethod === 'delivery' ? styles.active : ''}`}
								onClick={() => setValue('delivery_method', 'delivery')}
							>
								Доставка курьером
							</button>
							<button
								type="button"
								className={`${styles.toggleBtn} ${currentMethod === 'pickup' ? styles.active : ''}`}
								onClick={() => setValue('delivery_method', 'pickup')}
							>
								Самовывоз
							</button>
						</div>

						{/* 1. ВЫБОР ГОРОДА (Общий для обоих способов) */}
						<Controller
							name="city_id"
							control={control}
							rules={{ required: 'Выберите город' }}
							render={({ field }) => (
								<CustomSelect
									className={styles.selectCity}
									label="Город доставки / получения"
									options={cities}
									value={field.value}
									onChange={(val) => {
										field.onChange(val)
										setIsAddingNew(false)
									}}
									placeholder={isCitiesLoading ? 'Загрузка...' : 'Выберите ваш город'}
									error={errors.city_id}
									disabled={isCitiesLoading}
								/>
							)}
						/>
					</div>

					{/* ПРЕДУПРЕЖДЕНИЕ ОБ ОТСУТСТВИИ ТЕЛЕФОНА */}
					{isPhoneMissingForDelivery && (
						<div className={styles.warningBox}>
							<p>
								Для оформления доставки курьером необходимо указать номер телефона в
								профиле.
							</p>
						</div>
					)}

					{/* 2. СЕКЦИЯ: ДОСТАВКА КУРЬЕРОМ */}
					{currentMethod === 'delivery' && (
						<div className={styles.section}>
							{/* Плашка об отсутствии адресов показывается только когда загрузка завершена и адресов точно 0 */}
							{!isDeliveryLoading && filteredAddresses.length === 0 ? (
								<div className={styles.noAddressesNotice}>
									<p>У вас нет сохраненных адресов в этом городе.</p>
									<button
										type="button"
										className={styles.addAddressBtn}
										onClick={() => setIsAddingNew(true)}
									>
										+ Добавить новый адрес
									</button>
								</div>
							) : (
								/* Во время загрузки ИЛИ при наличии адресов рендерится один и тот же блок */
								<div className={styles.addressSelectorGroup}>
									{/* ВЫБОР АДРЕСА (CustomSelect) */}
									<Controller
										name="address_id"
										control={control}
										rules={{ required: 'Выберите адрес доставки' }}
										render={({ field }) => (
											<CustomSelect
												label="Адрес доставки"
												options={addressOptions}
												value={field.value || ''}
												onChange={(val) => field.onChange(val)}
												placeholder={
													isDeliveryLoading
														? 'Загрузка адресов...'
														: 'Выберите сохранённый адрес'
												}
												error={errors.address_id}
												disabled={isDeliveryLoading} // Блокируем селект при загрузке
											/>
										)}
									/>

									<button
										type="button"
										className={styles.addAddressBtn}
										onClick={() => setIsAddingNew(true)}
										disabled={isDeliveryLoading} // Блокируем кнопку при загрузке
										style={{
											opacity: isDeliveryLoading ? 0.5 : 1, // Визуально приглушаем кнопку
											cursor: isDeliveryLoading ? 'default' : 'pointer',
										}}
									>
										+ Указать другой адрес
									</button>
								</div>
							)}
						</div>
					)}

					{/* 3. СЕКЦИЯ: САМОВЫВОЗ */}
					{currentMethod === 'pickup' && (
						<div className={styles.section}>
							{/* Сообщение об отсутствии ПВЗ показываем только когда загрузка завершена и список пуст */}
							{isLoadingPickups && filteredPickupPoints.length === 0 ? (
								<p className={styles.emptyText}>
									В выбранном городе пока нет доступных ПВЗ.
								</p>
							) : (
								/* Во время загрузки ИЛИ при наличии ПВЗ рендерим CustomSelect */
								<div className={styles.pickupSelectorGroup}>
									<Controller
										name="pickup_point_id"
										control={control}
										rules={{ required: 'Выберите пункт выдачи' }}
										render={({ field }) => (
											<CustomSelect
												label="Адрес ПВЗ"
												options={pickupOptions}
												value={field.value || ''}
												onChange={(val) => {
													field.onChange(val)
													if (val) {
														localStorage.setItem('lastUsedPickupPoint', val)
													}
												}}
												placeholder={
													isLoadingPickups
														? 'Загрузка пунктов выдачи...'
														: 'Выберите пункт выдачи'
												}
												error={errors.pickup_point_id}
												disabled={isLoadingPickups} // Блокируем селект при загрузке
											/>
										)}
									/>
								</div>
							)}
						</div>
					)}

					{/* 4. СЕКЦИЯ: СПОСОБ ОПЛАТЫ */}
					<div className={styles.paymentSection}>
						<h3 className={styles.sectionTitle}>Способ оплаты</h3>
						<div className={styles.paymentOptions}>
							<label
								className={`${styles.paymentCard} ${currentPayment === 'upon_receipt' ? styles.activePayment : ''}`}
							>
								<input
									type="radio"
									value="upon_receipt"
									checked={currentPayment === 'upon_receipt'}
									onChange={() => setValue('payment_method', 'upon_receipt')}
								/>
								<div className={styles.paymentMeta}>
									<span className={styles.paymentTitle}>При получении</span>
									<span className={styles.paymentSub}>Оплата картой или наличными</span>
								</div>
							</label>

							<label
								className={`${styles.paymentCard} ${currentPayment === 'online' ? styles.activePayment : ''}`}
							>
								<input
									type="radio"
									value="online"
									checked={currentPayment === 'online'}
									onChange={() => setValue('payment_method', 'online')}
								/>
								<div className={styles.paymentMeta}>
									<span className={styles.paymentTitle}>Онлайн на сайте</span>
									<span className={styles.paymentSub}>Банковской картой или СБП</span>
								</div>
							</label>
						</div>
					</div>
				</form>
			) : (
				/* ФОРМА ДОБАВЛЕНИЯ АДРЕСА */
				<div className={styles.newAddressWrapper}>
					<EditAddressForm
						initialCityId={selectedCityId}
						onSuccess={handleAddressCreated}
					/>

					{addresses.length > 0 && (
						<button
							type="button"
							className={styles.cancelAddBtn}
							onClick={() => setIsAddingNew(false)}
						>
							← Отмена (выбрать из сохранённых адресов)
						</button>
					)}
				</div>
			)}
		</Motion.div>
	)
}

export default CheckoutForm
