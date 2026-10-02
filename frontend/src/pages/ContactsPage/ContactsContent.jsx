import { useMemo, useState } from 'react'
import { YMaps, Map, Placemark, ZoomControl } from '@pbe/react-yandex-maps'
import { useContacts } from '@/entities/contacts/hooks/useContacts'
import { useSuspensePickupPointsQuery } from '@/features/orders/hooks/useOrders'
import ContactsMap from '@/features/contacts/components/ContactsMap'
import Breadcrumbs from '@/components/common/Breadcrumbs'
import styles from './ContactsPage.module.scss'

const ContactsContent = () => {
	const { data: contacts } = useContacts()
	const { data: pickupPoints } = useSuspensePickupPointsQuery()

	// Стейт для выбранного ПВЗ (чтобы центрировать карту по клику в списке)
	const [selectedPointId, setSelectedPointId] = useState(null)

	// Группируем ПВЗ по имени города для удобного рендера и кэшируем результат вычислений
	const groupedPickupPoints = useMemo(() => {
		if (!pickupPoints) return {}

		// Метод reduce проходит по каждому элементу (point) массива pickupPoints и собирает итоговый результат в аккумулятор (acc). Изначально аккумулятор — это пустой объект {}

		return pickupPoints.reduce((acc, point) => {
			// Исключаем неактивные пункты, если вдруг бэкенд их пришлет
			if (!point.is_active) return acc

			// Проверяем, есть ли уже в нашем объекте acc ключ с названием города текущего ПВЗ.
			// Если нет, мы создаем этот ключ и кладем в него пустой массив.
			if (!acc[point.city_name]) {
				acc[point.city_name] = []
			}
			// Когда массив для этого города точно существует, мы добавляем в него текущий ПВЗ.
			acc[point.city_name].push(point)
			// Передаем обновленный объект на следующую итерацию цикла.
			return acc
			// В итоге из массива [{ id: 1, city_name: 'Москва' }, { id: 2, city_name: 'Минск' }] получается удобный для рендера объект: {"Москва": [{id: 1}], "Минск": [{id: 2}]}
		}, {})
	}, [pickupPoints])

	return (
		<>
			<Breadcrumbs items={[{ name: 'Контакты' }]} />
			<h1 className={styles.title}>КОНТАКТЫ</h1>

			<div className={styles.contentLayout}>
				{/* ЛЕВАЯ КОЛОНКА: ИНФОРМАЦИЯ */}
				<div className={styles.infoColumn}>
					{/* СЕКЦИЯ 1: Контакты магазина */}
					<section className={styles.section}>
						<h2 className={styles.sectionTitle}>Служба поддержки</h2>

						<div className={styles.contactBlock}>
							<div className={styles.contactItem}>
								<span className={styles.label}>Телефон:</span>
								<a href={`tel:${contacts.phone}`} className={styles.link}>
									{contacts.phone}
								</a>
							</div>
							<div className={styles.contactItem}>
								<span className={styles.label}>Email:</span>
								<a href={`mailto:${contacts.email}`} className={styles.link}>
									{contacts.email}
								</a>
							</div>
						</div>

						<div className={styles.scheduleBlock}>
							<p className={styles.scheduleRow}>
								<span className={styles.label}>Режим работы: </span>
								{contacts.schedule_days}, {contacts.schedule_time}
							</p>
							<p className={styles.scheduleRow}>
								<span className={styles.label}>Дополнительно: </span>
								{contacts.schedule_extra}
							</p>
						</div>
					</section>

					{/* СЕКЦИЯ 1: Соцсети и мессенджеры */}
					<section className={styles.section}>
						<h2 className={styles.sectionTitle}>Наши Соцсети и мессенджеры</h2>
						<div className={styles.socials}>
							{contacts.tg_url && (
								<a
									href={contacts.tg_url}
									target="_blank"
									rel="noreferrer"
									className={styles.socialLink}
								>
									<img src="/telegram.svg" alt="Telegram" />
								</a>
							)}
							{contacts.vb_url && (
								<a
									href={contacts.vb_url}
									target="_blank"
									rel="noreferrer"
									className={styles.socialLink}
								>
									<img src="/viber.svg" alt="Viber" />
								</a>
							)}
							{contacts.vk_url && (
								<a
									href={contacts.vk_url}
									target="_blank"
									rel="noreferrer"
									className={styles.socialLink}
								>
									<img src="/vk.svg" alt="VK" />
								</a>
							)}
							{contacts.ig_url && (
								<a
									href={contacts.ig_url}
									target="_blank"
									rel="noreferrer"
									className={styles.socialLink}
								>
									<img src="/instagram.svg" alt="Instagram" />
								</a>
							)}
						</div>
					</section>

					{/* СЕКЦИЯ 2: Пункты выдачи заказов */}
					<section className={styles.section}>
						<h2 className={styles.sectionTitle}>Пункты выдачи заказов</h2>

						{Object.keys(groupedPickupPoints).length === 0 ? (
							<p>В данный момент доступных пунктов выдачи нет.</p>
						) : (
							<div className={styles.citiesList}>
								{Object.entries(groupedPickupPoints).map(([city, points]) => (
									<div key={city} className={styles.cityGroup}>
										<h3 className={styles.cityName}>{city}</h3>
										<ul className={styles.pointsList}>
											{points.map((point) => (
												<li
													key={point.id}
													className={`${styles.pointItem} ${selectedPointId === point.id ? styles.pointItemActive : ''}`.trim()}
													onClick={() => setSelectedPointId(point.id)}
												>
													<p className={styles.pointAddress}>{point.address}</p>
													<p className={styles.pointSchedule}>{point.work_schedule}</p>
													{point.phone && (
														<p className={styles.pointPhone}>Тел: {point.phone}</p>
													)}
												</li>
											))}
										</ul>
									</div>
								))}
							</div>
						)}
					</section>
				</div>

				{/* ПРАВАЯ КОЛОНКА: КАРТА */}
				<div className={styles.mapColumn}>
					<ContactsMap
						pickupPoints={pickupPoints}
						selectedPointId={selectedPointId}
						onPointSelect={setSelectedPointId}
					/>
				</div>
			</div>
		</>
	)
}

export default ContactsContent
