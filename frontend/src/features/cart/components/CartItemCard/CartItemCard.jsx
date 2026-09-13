import {
	useUpdateCartItemMutation,
	useRemoveCartItemMutation,
} from '@/features/cart/hooks/useCart'
import { formatPriceBy } from '@/shared/utils/formatPriceBy'
import DeleteIcon from '@/shared/icons/cross.svg' // Или иконка мусорки
import styles from './CartItemCard.module.scss'

const CartItemCard = ({ item }) => {
	const { mutate: updateItem, isPending: isUpdating } = useUpdateCartItemMutation()
	const { mutate: removeItem, isPending: isRemoving } = useRemoveCartItemMutation()

	// Достаем данные безопасно
	// Когда бэкенд будет обновлен, здесь заработает item.product_info.naming.full_title
	const title = item.product_info.naming?.full_title || item.product_info.name
	const imageUrl = item.product_info.main_image?.thumbnail?.product_small || ''
	const price = formatPriceBy(item.total_item_price)

	// Блокируем кнопки, если идет запрос (чтобы юзер не накликал лишнего)
	const isBusy = isUpdating || isRemoving

	const handleIncrease = () => {
		updateItem({ id: item.id, quantity: item.quantity + 1 })
	}

	const handleDecrease = () => {
		if (item.quantity > 1) {
			updateItem({ id: item.id, quantity: item.quantity - 1 })
		}
	}

	const handleRemove = () => {
		removeItem(item.id)
	}

	return (
		<div className={`${styles.card} ${isRemoving ? styles.removing : ''}`}>
			{/* Картинка */}
			<div className={styles.imageWrapper}>
				{imageUrl ? (
					<img src={imageUrl} alt={title} className={styles.image} />
				) : (
					<div className={styles.placeholder} />
				)}
			</div>

			{/* Информация о товаре */}
			<div className={styles.info}>
				<h3 className={styles.title}>{title}</h3>
				<span className={styles.size}>Размер: {item.size_name}</span>
			</div>

			{/* Управление количеством */}
			<div className={styles.quantityControls}>
				<button
					type="button"
					onClick={handleDecrease}
					disabled={item.quantity <= 1 || isBusy}
					className={styles.qtyBtn}
				>
					-
				</button>
				<span className={styles.qtyValue}>{item.quantity}</span>
				<button
					type="button"
					onClick={handleIncrease}
					disabled={isBusy}
					className={styles.qtyBtn}
				>
					+
				</button>
			</div>

			{/* Цена */}
			<div className={styles.priceBlock}>
				<span className={styles.price}>{price}</span>
			</div>

			{/* Кнопка удаления */}
			<button
				type="button"
				onClick={handleRemove}
				disabled={isBusy}
				className={styles.deleteBtn}
				aria-label="Удалить товар"
			>
				<DeleteIcon className={styles.deleteIcon} />
			</button>
		</div>
	)
}

export default CartItemCard
