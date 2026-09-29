import { useState } from 'react'
import Breadcrumbs from '@/components/common/Breadcrumbs'
import CartData from '@/features/cart/components/CartData'
import { useSuspenseCartQuery } from '@/features/cart/hooks/useCart'
import PageTitle from '@/components/common/PageTitle'
import EmptyCart from './EmptyCart'
import styles from './CartPage.module.scss'

const CartContent = () => {
	const { data: cart } = useSuspenseCartQuery()
	const [isCheckoutMode, setIsCheckoutMode] = useState(false)

	// Показываем контент корзины, если есть товары в корзине
	const hasItems = cart.items && cart.items.length > 0

	return (
		<>
			{isCheckoutMode ? (
				<PageTitle title="Оформление заказа" />
			) : (
				<PageTitle title="Корзина" />
			)}

			<Breadcrumbs items={[{ name: isCheckoutMode ? 'Оформление заказа' : 'Корзина' }]} />

			<h1 className={isCheckoutMode ? styles.titleOrder : styles.title}>
				{isCheckoutMode ? 'ОФОРМЛЕНИЕ ЗАКАЗА' : 'КОРЗИНА ТОВАРОВ'}
			</h1>
			{hasItems ? <CartData onCheckoutChange={setIsCheckoutMode} /> : <EmptyCart />}
		</>
	)
}

export default CartContent
