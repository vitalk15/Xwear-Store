import { motion as Motion } from 'framer-motion'
import { formatPriceBy } from '@/shared/utils/formatPriceBy'
import styles from './CompactCartItem.module.scss'

const CompactCartItem = ({ item }) => {
	const title = item.product_info?.naming?.full_title || item.product_info?.name
	const price = formatPriceBy(item.total_item_price)
	const size = item.size_name

	return (
		// Важно: layoutId должен совпадать с layoutId большой карточки!
		<Motion.div layoutId={`cart-item-${item.id}`} className={styles.compactItem}>
			<div className={styles.name}>{title}</div>
			<div className={styles.info}>
				<span className={styles.size}>размер {size}</span>
				<span className={styles.quantity}> x {item.quantity}</span>
				<span className={styles.price}> = {price}</span>
			</div>
		</Motion.div>
	)
}

export default CompactCartItem
