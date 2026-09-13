import Breadcrumbs from '@/components/common/Breadcrumbs'
import EmptyCart from './EmptyCart'
import styles from './CartPage.module.scss'

const CartContent = () => {
	return (
		<>
			<Breadcrumbs items={[{ name: 'Корзина' }]} />

			<h1 className={styles.title}>КОРЗИНА ТОВАРОВ</h1>
			{/* {count > 0 ? (
				<>
					<CartData />
				</>
			) : (
				<EmptyCart />
			)} */}
		</>
	)
}

export default CartContent
