import { motion as Motion, AnimatePresence } from 'framer-motion'
import { formatPriceBy } from '@/shared/utils/formatPriceBy'
import styles from './OrdersList.module.scss'

// Помощник для даты формата "27.06.2026"
const formatDateShort = (isoString) => {
	const date = new Date(isoString)
	return date.toLocaleDateString('ru-RU', {
		day: '2-digit',
		month: '2-digit',
		year: 'numeric',
	})
}

// Помощник для даты формата "27 Июня в 12:34"
const formatDateDetailed = (isoString) => {
	if (!isoString) return ''
	const date = new Date(isoString)

	// При передаче day и month одновременно, JS форматирует месяц в родительном падеже ("27 июня")
	const dateParts = date
		.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
		.split(' ')

	const day = dateParts[0]
	const month = dateParts[1]
	// Делаем первую букву месяца заглавной
	const capitalizedMonth = month.charAt(0).toUpperCase() + month.slice(1)
	const time = date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })

	return `${day} ${capitalizedMonth} в ${time}`
}

const OrderRow = ({ order, isExpanded, onToggle }) => {
	// Считаем суммы
	const itemsTotal = order.items.reduce(
		(sum, item) => sum + Number(item.price_at_purchase) * item.quantity,
		0,
	)
	const deliveryCost = Number(order.delivery_cost) || 0
	const finalTotal = itemsTotal + deliveryCost

	// Зеленый цвет применяем только для статусов "ready" (Готов к получению) и "shipped" (Отправлен), красный - для "canceled" (отменён)
	const isSuccessStatus = ['ready', 'shipped'].includes(order.status)
	const isCanceledStatus = ['canceled'].includes(order.status)
	const statusClass = isSuccessStatus
		? styles.statusSuccess
		: isCanceledStatus
			? styles.statusCanceled
			: ''

	// Текст способа получения
	const deliveryMethodText =
		order.delivery_method_display ||
		(order.delivery_method === 'delivery' ? 'Доставка' : 'Самовывоз')

	return (
		<div className={`${styles.rowWrapper} ${isExpanded ? styles.expanded : ''}`}>
			{/* КЛИКАБЕЛЬНАЯ СТРОКА ТАБЛИЦЫ */}
			<div className={styles.rowMain} onClick={onToggle}>
				<span className={styles.colNumber}>#{order.id}</span>
				<span className={styles.colDate}>{formatDateShort(order.created_at)}</span>
				<span className={`${styles.colStatus} ${statusClass}`}>
					{order.status_display}
				</span>
				<span className={styles.colTotal}>{formatPriceBy(finalTotal)}</span>
			</div>

			{/* РАЗВЕРНУТАЯ ИНФОРМАЦИЯ (АККОРДЕОН) */}
			<AnimatePresence initial={false}>
				{isExpanded && (
					<Motion.div
						initial={{ height: 0, opacity: 0 }}
						animate={{ height: 'auto', opacity: 1 }}
						exit={{ height: 0, opacity: 0 }}
						transition={{ duration: 0.3, ease: 'easeInOut' }}
						className={styles.rowDetailsWrapper}
					>
						<div className={styles.rowDetailsContent}>
							{/* Шапка детализации */}
							<div className={styles.detailsHeader}>
								<h3>Заказ #{order.id}</h3>
								<p className={styles.detailsMeta}>
									Был оформлен <b>{formatDateDetailed(order.created_at)}</b> - статус
									заказа:
									<span className={`${styles.statusBadge} ${statusClass}`}>
										{order.status_display}
									</span>
								</p>
							</div>

							{/* Информация о доставке и адресе */}
							<div className={styles.deliveryInfoSection}>
								<div className={styles.infoRow}>
									<span className={styles.infoLabel}>Способ получения:</span>
									<span className={styles.infoValue}>{deliveryMethodText}</span>
								</div>
								<div className={styles.infoRow}>
									<span className={styles.infoLabel}>
										{order.delivery_method === 'delivery'
											? 'Адрес доставки:'
											: 'Пункт выдачи:'}
									</span>
									<span className={styles.infoValue}>{order.address_text}</span>
								</div>
							</div>

							{/* Таблица товаров */}
							<div className={styles.itemsTable}>
								<div className={styles.itemsHeader}>
									<span>ТОВАР</span>
									<span>ИТОГО</span>
								</div>
								{order.items.map((item) => (
									<div key={item.id} className={styles.itemRow}>
										<span>
											{item.product_name}
											<span className={styles.itemQty}>- р.{item.size_name}</span>
											<span className={styles.itemQty}>x {item.quantity}</span>
										</span>
										<span className={styles.itemSum}>
											{formatPriceBy(Number(item.price_at_purchase) * item.quantity)}
										</span>
									</div>
								))}
							</div>

							{/* Итоги */}
							<div className={styles.summarySection}>
								<div className={styles.summaryRow}>
									<span>Всего</span>
									<span className={styles.summaryPrice}>{formatPriceBy(itemsTotal)}</span>
								</div>
								<div className={`${styles.summaryRow} ${styles.deliveryCost}`}>
									<span>Доставка</span>
									<span className={styles.summaryPrice}>
										{formatPriceBy(deliveryCost)}
									</span>
								</div>
								<div className={`${styles.summaryRow} ${styles.finalTotal}`}>
									<span>Итого</span>
									<span>{formatPriceBy(finalTotal)}</span>
								</div>
							</div>
						</div>
					</Motion.div>
				)}
			</AnimatePresence>
		</div>
	)
}

export default OrderRow
