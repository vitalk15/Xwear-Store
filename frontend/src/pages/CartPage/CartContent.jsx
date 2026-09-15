import Breadcrumbs from '@/components/common/Breadcrumbs'
import CartData from '@/features/cart/components/CartData'
import { useSuspenseCartQuery } from '@/features/cart/hooks/useCart'
import EmptyCart from './EmptyCart'
import styles from './CartPage.module.scss'

const CartContent = () => {
	const { data: cart } = useSuspenseCartQuery()

	// Проверяем, есть ли товары в корзине (длина массива)
	const hasItems = cart.items && cart.items.length > 0

	return (
		<>
			<Breadcrumbs items={[{ name: 'Корзина' }]} />

			<h1 className={styles.title}>КОРЗИНА ТОВАРОВ</h1>
			{hasItems ? <CartData /> : <EmptyCart />}
		</>
	)
}

export default CartContent
