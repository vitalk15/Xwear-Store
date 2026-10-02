import { YMaps, Map, Placemark, ZoomControl } from '@pbe/react-yandex-maps'
import styles from '@/pages/ContactsPage/ContactsPage.module.scss'

const ContactsMap = ({ pickupPoints = [], selectedPointId, onPointSelect }) => {
	// Ищем ПВЗ, выбранный в списке, либо первый активный с координатами для дефолтного отображения
	const activePoint = selectedPointId
		? pickupPoints.find((p) => p.id === selectedPointId)
		: pickupPoints.find((p) => p.lat && p.lon && p.is_active)

	// Дефолтный центр (например, Минск), если координат нет
	const defaultCenter = [53.9006, 27.559]
	const mapCenter = activePoint
		? [Number(activePoint.lat), Number(activePoint.lon)]
		: defaultCenter

	return (
		// Если есть API-ключ Яндекса для коммерческого использования, укажите его в apikey.
		// Для базовой разработки можно оставить load: 'package.full' без ключа (с ограничениями).
		<YMaps query={{ lang: 'ru_RU', load: 'package.full' }}>
			<div className={styles.mapContainer}>
				<Map
					state={{
						center: mapCenter,
						zoom: selectedPointId ? 15 : 11, // Приближаем ближе, если ПВЗ выбран конкретно
					}}
					width="100%"
					height="100%"
					// options={{ suppressMapOpenBlock: true }} // Убирает лишние кнопки перехода в Яндекс
				>
					{/* Кнопка зума на карте */}
					<ZoomControl options={{ float: 'right' }} />

					{/* Рендерим метки ПВЗ */}
					{pickupPoints.map((point) => {
						if (!point.is_active || !point.lat || !point.lon) return null

						const isSelected = selectedPointId === point.id

						return (
							<Placemark
								key={point.id}
								geometry={[Number(point.lat), Number(point.lon)]}
								properties={{
									balloonContentHeader: `ПВЗ №${point.id}`,
									balloonContentBody: `<b>${point.address}</b>`,
									balloonContentFooter: `
                    <div>
                      <p><b>Режим работы:</b> ${point.work_schedule}</p>
                      ${point.phone ? `<p><b>Тел:</b> ${point.phone}</p>` : ''}
                    </div>
                  `,
									hintContent: point.address,
								}}
								options={{
									// Если ПВЗ выбран - голубая метка, иначе черная
									preset: isSelected ? 'islands#blueIcon' : 'islands#blackDotIcon',
									// Выводим выбранную метку поверх остальных
									zIndex: isSelected ? 1000 : 1,
								}}
								// При клике на метку обновляем стейт в родительском компоненте
								onClick={() => {
									if (onPointSelect) onPointSelect(point.id)
								}}
							/>
						)
					})}
				</Map>
			</div>
		</YMaps>
	)
}

export default ContactsMap
