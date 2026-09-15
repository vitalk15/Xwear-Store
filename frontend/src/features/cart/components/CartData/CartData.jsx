import { useSuspenseCartQuery } from '@/features/cart/hooks/useCart'
import { formatPriceBy } from '@/shared/utils/formatPriceBy'
import CartItemCard from '../CartItemCard'
import Button from '@/components/ui/Button'
import styles from './CartData.module.scss'

const CartData = () => {
	const { data: cart } = useSuspenseCartQuery()

	const itemsCount = cart.items.reduce((total, item) => total + item.quantity, 0)
	const formattedTotal = formatPriceBy(cart.total_price)

	return (
		<div className={styles.cartLayout}>
			{/* ЛЕВАЯ КОЛОНКА: Список товаров */}
			<div className={styles.itemsList}>
				{cart.items.map((item) => (
					<CartItemCard key={item.id} item={item} />
				))}
			</div>

			{/* ПРАВАЯ КОЛОНКА: Оформление заказа (Order Summary) */}
			<div className={styles.summarySidebar}>
				<h2 className={styles.summaryTitle}>ДЕТАЛИ ЗАКАЗА</h2>

				<div className={styles.summaryInfo}>
					<div className={styles.summaryRow}>
						<span>Всего товаров: </span>
						<b>{itemsCount} шт.</b>
					</div>
					<div className={styles.summaryRow}>
						<span>Стоимость: </span>
						<b>{formattedTotal}</b>
					</div>
				</div>

				{/* С учётом скидок и доставок */}
				{/* <div className={styles.totalRow}>
					<span>Итого</span>
					<span>{formattedTotal}</span>
				</div> */}

				<Button className={styles.checkoutBtn}>ПЕРЕЙТИ К ОФОРМЛЕНИЮ</Button>
			</div>
		</div>
	)
}

export default CartData
