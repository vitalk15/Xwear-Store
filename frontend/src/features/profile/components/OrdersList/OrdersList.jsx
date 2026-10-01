import { useState } from 'react'
import { useOrdersQuery } from '@/features/orders/hooks/useOrders'
import { useSearchParams } from 'react-router-dom'
import { ORDERS_ITEMS_PER_PAGE } from '@/shared/constants/pagination'
import Pagination from '@/components/ui/Pagination'
import OrderRow from './OrderRow'
import styles from './OrdersList.module.scss'

const OrdersList = ({ filterType = 'active' }) => {
	const { data: orders, isLoading, isError } = useOrdersQuery()
	// Храним ID развернутого заказа. Если null - все закрыты.
	const [expandedOrderId, setExpandedOrderId] = useState(null)

	// Достаем searchParams, чтобы знать текущую страницу
	const [searchParams] = useSearchParams()

	if (isLoading) return <div className={styles.loading}>Загрузка заказов...</div>
	if (isError) return <div className={styles.error}>Ошибка при загрузке заказов.</div>

	// Фильтруем заказы в зависимости от вкладки
	const filteredOrders =
		orders?.filter((order) => {
			// Считаем активными все, кроме завершенных и отмененных
			const isActive = !['completed', 'canceled'].includes(order.status)
			return filterType === 'active' ? isActive : !isActive
		}) || []

	const title = filterType === 'active' ? 'Текущие заказы' : 'История заказов'

	// --- ЛОГИКА ПАГИНАЦИИ ---
	// Читаем текущую страницу
	const currentPage = parseInt(searchParams.get('page') || '1', 10)

	// Считаем общее количество страниц
	const totalPages = Math.ceil(filteredOrders.length / ORDERS_ITEMS_PER_PAGE)

	// Вычисляем индексы для среза массива (slice)
	const startIndex = (currentPage - 1) * ORDERS_ITEMS_PER_PAGE
	const endIndex = startIndex + ORDERS_ITEMS_PER_PAGE

	// Получаем заказы только для текущей страницы
	const paginatedOrders = filteredOrders.slice(startIndex, endIndex)
	// ------------------------

	return (
		<>
			{filterType !== 'active' && <h2 className={styles.title}>{title}</h2>}

			<div className={styles.container}>
				{filterType === 'active' && <h2 className={styles.titleTable}>{title}</h2>}

				{filteredOrders.length === 0 ? (
					<div className={styles.emptyState}>
						<p>
							{filterType === 'active'
								? 'У вас нет активных заказов.'
								: 'Ваша история заказов пуста.'}
						</p>
					</div>
				) : (
					<div className={styles.table}>
						{/* Шапка таблицы */}
						<div className={styles.tableHeader}>
							<span className={styles.colNumber}>НОМЕР</span>
							<span className={styles.colDate}>ДАТА</span>
							<span className={styles.colStatus}>СТАТУС</span>
							<span className={styles.colTotal}>ИТОГ</span>
						</div>

						{/* Тело таблицы */}
						<div className={styles.tableBody}>
							{paginatedOrders.map((order) => (
								<OrderRow
									key={order.id}
									order={order}
									isExpanded={expandedOrderId === order.id}
									onToggle={() =>
										setExpandedOrderId(expandedOrderId === order.id ? null : order.id)
									}
								/>
							))}
						</div>

						{/* Рендерим пагинацию внизу таблицы, если страниц больше одной */}
						{totalPages > 1 && (
							<div className={styles.paginationWrapper}>
								<Pagination totalPages={totalPages} className={styles.orderPagination} />
							</div>
						)}
					</div>
				)}
			</div>
		</>
	)
}

export default OrdersList
