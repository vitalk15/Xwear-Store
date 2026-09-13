import { useCartQuery } from '@/features/cart/hooks/useCart'
import useAuthStore from '@/features/auth/store/useAuthStore'
import { formatPriceBy } from '@/shared/utils/formatPriceBy'
import CartItemCard from '../CartItemCard'
import styles from './CartData.module.scss'

const CartData = () => {
	const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
	const { data: cart } = useCartQuery(isAuthenticated)

	if (!cart) return null

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

				<div className={styles.summaryRow}>
					<span>Всего товаров: {itemsCount} шт.</span>
					<span>Стоимость: {formattedTotal}</span>
				</div>

				{/* С учётом скидок и доставок */}
				{/* <div className={styles.totalRow}>
					<span>Итого</span>
					<span>{formattedTotal}</span>
				</div> */}

				<button className={styles.checkoutBtn} type="button">
					ПЕРЕЙТИ К ОФОРМЛЕНИЮ
				</button>
			</div>
		</div>
	)
}

export default CartData
