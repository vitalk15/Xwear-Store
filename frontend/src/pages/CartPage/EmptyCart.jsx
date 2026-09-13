import EmptyCartIcon from '@/shared/icons/empty-cart.svg'
import styles from './CartPage.module.scss'

const EmptyCart = () => {
	return (
		<div className={styles.emptyContainer}>
			<EmptyCartIcon className={styles.icon} />
			<h2 className={styles.title}>ВАША КОРЗИНА НА ДАННЫЙ МОМЕНТ ПУСТА.</h2>
			<p className={styles.description}>
				Прежде чем приступить к оформлению заказа, вы должны добавить некоторые товары в
				корзину.
			</p>
		</div>
	)
}

export default EmptyCart
