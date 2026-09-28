import { useState, useEffect, useMemo } from 'react'
import { useForm, useWatch, Controller } from 'react-hook-form'
import { motion as Motion } from 'framer-motion'
import { useProfileQuery } from '@/features/profile/hooks/useProfile'
import { usePickupPointsQuery, useCitiesQuery } from '@/features/orders/hooks/useOrders'
import CustomSelect from '@/components/ui/CustomSelect'
import EditAddressForm from '@/features/profile/components/EditAddressForm'
import Toast from '@/components/ui/Toast'
import styles from './CheckoutForm.module.scss'

const CheckoutForm = ({ onDeliveryInfoChange }) => {
	// Стейт для уведомлений
	const [toastMessage, setToastMessage] = useState(null)

	// 1. Данные профиля (адреса)
	const { data: profileData, isLoading: isProfileLoading } = useProfileQuery()
	// Кешируем ссылку на массив адресов, чтобы useEffect не срабатывал на каждом рендере
	const addresses = useMemo(() => profileData?.profile?.addresses || [], [profileData])

	// 2. Данные ПВЗ и Городов
	const { data: pickupPoints = [], isLoading: isLoadingPickups } = usePickupPointsQuery()
	const { data: cities = [], isLoading: isCitiesLoading } = useCitiesQuery()

	// Состояние: режим добавления нового адреса
	const [isAddingNew, setIsAddingNew] = useState(false)

	const {
		control,
		handleSubmit,
		setValue,
		formState: { errors },
	} = useForm({
		defaultValues: {
			delivery_method: 'delivery', // 'delivery' | 'pickup'
			city_id: '', // ID доступного города
			address_id: null, // ID сохраненного адреса (если выбрана доставка)
			pickup_point_id: null, // ID ПВЗ (если выбран самовывоз)
		},
	})

	// Следим за тем, какой способ доставки выбран в реальном времени и др.
	const currentMethod = useWatch({ control, name: 'delivery_method' })
	const selectedCityId = useWatch({ control, name: 'city_id' })
	const selectedAddressId = useWatch({ control, name: 'address_id' })
	const selectedPickupId = useWatch({ control, name: 'pickup_point_id' })

	// Инициализация города по умолчанию (город основного адреса или первый город)
	// ждем строго окончания загрузки профиля и городов
	useEffect(() => {
		if (isCitiesLoading || isProfileLoading || isLoadingPickups || cities.length === 0)
			return

		// Если город уже инициализирован, не перезаписываем его
		if (selectedCityId) return

		if (addresses.length > 0) {
			const defaultAddr = addresses.find((a) => a.is_default) || addresses[0]
			const defaultCityId =
				defaultAddr.city_details?.id || defaultAddr.city?.id || defaultAddr.city

			if (defaultCityId) {
				setValue('city_id', String(defaultCityId))
				setValue('address_id', defaultAddr.id)
				return
			}
		}

		// Если у пользователя нет сохраненных адресов, берем первый город
		setValue('city_id', String(cities[0].id))
	}, [
		isCitiesLoading,
		isProfileLoading,
		isLoadingPickups,
		cities,
		addresses,
		selectedCityId,
		setValue,
	])

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
			name: `${point.address} (${point.work_schedule})`,
		}))
	}, [filteredPickupPoints])

	// Автоматический выбор первой ПВЗ при смене города
	useEffect(() => {
		if (currentMethod === 'pickup') {
			if (filteredPickupPoints.length > 0) {
				const existsInFiltered = filteredPickupPoints.some(
					(p) => p.id === Number(selectedPickupId),
				)
				if (!existsInFiltered) {
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

	// Выбранные объекты для превью-карточек
	// const selectedAddressObj = useMemo(() => {
	// 	return addresses.find((a) => a.id === Number(selectedAddressId)) || null
	// }, [addresses, selectedAddressId])

	// const selectedPickupObj = useMemo(() => {
	// 	return pickupPoints.find((p) => p.id === Number(selectedPickupId)) || null
	// }, [pickupPoints, selectedPickupId])

	// Обработчик успешного создания адреса в EditAddressForm
	const handleAddressCreated = (message) => {
		setIsAddingNew(false)
		// Если сообщение пришло, показываем Toast
		if (typeof message === 'string') {
			setToastMessage(message)
		}
	}

	// Показываем форму добавления адреса ТОЛЬКО если:
	// 1. Пользователь сам нажал "+ Указать другой адрес" (isAddingNew === true)
	// 2. ИЛИ загрузка завершилась и у пользователя ВООБЩЕ 0 адресов в системе
	const showAddAddressForm = isAddingNew || (!isProfileLoading && addresses.length === 0)

	const onSubmit = (formData) => {
		console.log('Готовые данные для отправки заказа:', formData)
		// Здесь позже будет отправка мутации createOrder
	}

	return (
		<>
			{toastMessage && (
				<Toast message={toastMessage} onClose={() => setToastMessage(null)} />
			)}

			<Motion.div
				initial={{ opacity: 0, x: -20 }}
				animate={{ opacity: 1, x: 0 }}
				exit={{ opacity: 0, x: -20 }}
				className={styles.formContainer}
			>
				{!showAddAddressForm ? (
					<form id="checkout-form" onSubmit={handleSubmit(onSubmit)}>
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

						{/* 2. СЕКЦИЯ: ДОСТАВКА КУРЬЕРОМ */}
						{currentMethod === 'delivery' && (
							<div className={styles.section}>
								{isProfileLoading ? (
									<p className={styles.loadingText}>Загрузка адресов...</p>
								) : filteredAddresses.length > 0 ? (
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
													value={field.value}
													onChange={(val) => field.onChange(val)}
													placeholder="Выберите сохранённый адрес"
													error={errors.address_id}
												/>
											)}
										/>

										{/* Превью выбранного адреса */}
										{/* {selectedAddressObj && (
                      <div className={`${styles.addressCard} ${styles.selectedCard}`}>
                        <div className={styles.addressInfo}>
                          <div className={styles.addressCity}>
                            {selectedAddressObj.city_details?.name ||
                              selectedAddressObj.city?.name ||
                              currentCityObj?.name}
                            {selectedAddressObj.is_default && (
                              <span className={styles.defaultBadge}>Основной</span>
                            )}
                          </div>
                          <div className={styles.addressText}>
                            {selectedAddressObj.address_simple}
                          </div>
                        </div>
                      </div>
                    )} */}

										<button
											type="button"
											className={styles.addAddressBtn}
											onClick={() => setIsAddingNew(true)}
										>
											+ Указать другой адрес
										</button>
									</div>
								) : (
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
								)}
							</div>
						)}

						{/* 3. СЕКЦИЯ: САМОВЫВОЗ */}
						{currentMethod === 'pickup' && (
							<div className={styles.section}>
								{isLoadingPickups ? (
									<p className={styles.loadingText}>Загрузка пунктов выдачи...</p>
								) : filteredPickupPoints.length > 0 ? (
									<div className={styles.pickupSelectorGroup}>
										{/* ВЫБОР ПВЗ (CustomSelect) */}
										<Controller
											name="pickup_point_id"
											control={control}
											rules={{ required: 'Выберите пункт выдачи' }}
											render={({ field }) => (
												<CustomSelect
													label="Адрес ПВЗ"
													options={pickupOptions}
													value={field.value}
													onChange={(val) => field.onChange(val)}
													placeholder="Выберите пункт выдачи"
													error={errors.pickup_point_id}
												/>
											)}
										/>

										{/* Превью выбранного ПВЗ */}
										{/* {selectedPickupObj && (
                      <div className={`${styles.addressCard} ${styles.selectedCard}`}>
                        <div className={styles.addressInfo}>
                          <div className={styles.addressCity}>
                            ПВЗ: {selectedPickupObj.city_name || currentCityObj?.name}
                          </div>
                          <div className={styles.addressText}>
                            {selectedPickupObj.address}
                          </div>
                          <div className={styles.scheduleText}>
                            Режим работы: {selectedPickupObj.work_schedule}
                          </div>
                          {selectedPickupObj.phone && (
                            <div className={styles.scheduleText}>
                              Тел: {selectedPickupObj.phone}
                            </div>
                          )}
                        </div>
                      </div>
                    )} */}
									</div>
								) : (
									<p className={styles.emptyText}>
										В выбранном городе пока нет доступных пунктов выдачи.
									</p>
								)}
							</div>
						)}

						{/* Способ оплаты пока пропустим, добавим позже */}
					</form>
				) : (
					/* Форма создания нового адреса */
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
		</>
	)
}

export default CheckoutForm
