import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion as Motion, AnimatePresence } from 'framer-motion'
import { useSuspenseCartQuery } from '@/features/cart/hooks/useCart'
import {
	useCommercialConfigQuery,
	useCreateOrderMutation,
} from '@/features/orders/hooks/useOrders'
import { calculateDeliveryCost } from '@/features/orders/utils/calculateDelivery'
import { formatPriceBy } from '@/shared/utils/formatPriceBy'
import CartItemCard from '../CartItemCard'
import CompactCartItem from '../CompactCartItem'
import CheckoutForm from '../CheckoutForm'
import { useToastStore } from '@/shared/store/useToastStore'
import Button from '@/components/ui/Button'
import { paths } from '@/routes/paths'
import styles from './CartData.module.scss'

const CartData = ({ onCheckoutChange }) => {
	const navigate = useNavigate()
	const { data: cart } = useSuspenseCartQuery()
	const { data: config } = useCommercialConfigQuery()
	const { mutateAsync: createOrder, isPending } = useCreateOrderMutation()
	const showToast = useToastStore((state) => state.showToast)

	// Состояние: находимся ли мы на этапе оформления
	const [isCheckout, setIsCheckout] = useState(false)

	const [deliveryInfo, setDeliveryInfo] = useState({
		deliveryMethod: 'delivery',
		selectedCity: null,
	})

	const isDelivery = deliveryInfo.deliveryMethod === 'delivery'

	useEffect(() => {
		// Добавляем плавную прокрутку на самый верх страницы
		// Небольшой таймаут всё еще может быть полезен из-за <AnimatePresence>
		const timer = setTimeout(() => {
			window.scrollTo({ top: 0, behavior: 'smooth' })
		}, 50)

		// Очистка таймаута на случай быстрого двойного клика
		return () => clearTimeout(timer)
	}, [isCheckout])

	const itemsCount = cart.items.reduce((total, item) => total + item.quantity, 0)
	const cartTotal = Number(cart.total_price) || 0

	// Расчёт стоимости доставки
	const { deliveryCost, isFree } = calculateDeliveryCost({
		cartTotal,
		deliveryMethod: deliveryInfo.deliveryMethod,
		selectedCity: deliveryInfo.selectedCity,
		config,
	})

	const finalTotal = cartTotal + (isCheckout ? deliveryCost : 0)

	const handleGoToCheckout = () => {
		setIsCheckout(true)
		if (onCheckoutChange) onCheckoutChange(true)
	}

	const handleGoBack = () => {
		setIsCheckout(false)
		if (onCheckoutChange) onCheckoutChange(false)
	}

	const handleOrderSubmit = async (formData) => {
		try {
			// 1. Формируем payload. Оставляем только нужный ID в зависимости от способа доставки
			const payload = {
				delivery_method: formData.delivery_method,
				payment_method: formData.payment_method,
				city_id: formData.city_id,
			}

			if (formData.delivery_method === 'delivery') {
				payload.address_id = formData.address_id
			} else {
				payload.pickup_point_id = formData.pickup_point_id
			}

			// 2. Отправляем заказ
			await createOrder(payload)

			// 3. Показываем сообщение на текущей странице
			showToast('Заказ успешно оформлен!', 'success')

			// 4. Переходим в профиль
			navigate(paths.profile)
		} catch {
			showToast('Произошла ошибка при оформлении заказа', 'error')
		}
	}

	return (
		<div className={styles.cartLayout}>
			{/* ЛЕВАЯ КОЛОНКА: Список товаров */}
			<div className={styles.itemsList}>
				<AnimatePresence mode="wait">
					{!isCheckout ? (
						// Состояние 1: Корзина
						<Motion.div
							key="cart-view"
							initial={{ opacity: 0 }}
							animate={{ opacity: 1 }}
							exit={{ opacity: 0 }}
						>
							{cart.items.map((item) => (
								<Motion.div
									key={item.id}
									layoutId={`cart-item-${item.id}`}
									className={styles.cartItem}
								>
									<CartItemCard item={item} />
								</Motion.div>
							))}
						</Motion.div>
					) : (
						// Состояние 2: Форма оформления заказа
						<CheckoutForm
							key="checkout-view"
							onDeliveryInfoChange={setDeliveryInfo}
							onSubmitOrder={handleOrderSubmit}
						/>
					)}
				</AnimatePresence>
			</div>

			{/* ПРАВАЯ КОЛОНКА: Оформление заказа (Order Summary) */}
			<div className={styles.summarySidebar}>
				<h2 className={styles.summaryTitle}>ДЕТАЛИ ЗАКАЗА</h2>

				<div className={styles.summaryInfo}>
					{/* Если мы в чекауте, показываем компактный список товаров в сайдбаре */}
					<AnimatePresence>
						{isCheckout && (
							<Motion.div
								initial={{ opacity: 0, height: 0 }}
								animate={{ opacity: 1, height: 'auto' }}
								exit={{ opacity: 0, height: 0 }}
								className={styles.compactItemsWrapper}
							>
								{cart.items.map((item) => (
									// Тот самый layoutId, который "притянет" карточку из левой колонки!
									<CompactCartItem key={item.id} item={item} />
								))}
							</Motion.div>
						)}
					</AnimatePresence>

					<div>
						<div className={styles.summaryRow}>
							<span>Всего товаров: </span>
							<b>{itemsCount} шт.</b>
						</div>
						<div className={styles.summaryRow}>
							<span>Стоимость: </span>
							<b>{formatPriceBy(cartTotal)}</b>
						</div>
					</div>

					{isCheckout && (
						<>
							{isDelivery && (
								<div>
									<div className={styles.summaryRow}>
										<span>Доставка: </span>
										<b>{isFree ? 'Бесплатно' : formatPriceBy(deliveryCost)}</b>
									</div>
								</div>
							)}
							<div className={`${styles.summaryRow} ${styles.totalRow}`}>
								<b>Итого:</b>
								<b>{formatPriceBy(finalTotal)}</b>
							</div>
						</>
					)}
				</div>

				{!isCheckout ? (
					<div className={styles.submitBtnWrapper}>
						<Button className={styles.checkoutBtn} onClick={handleGoToCheckout}>
							ПЕРЕЙТИ К ОФОРМЛЕНИЮ
						</Button>
					</div>
				) : (
					<div className={styles.submitBtnAction}>
						<Button
							type="submit"
							form="checkout-form"
							disabled={isPending}
							className={styles.checkoutBtn}
						>
							{isPending ? 'ОФОРМЛЕНИЕ...' : 'ОФОРМИТЬ ЗАКАЗ'}
						</Button>
						<button className={styles.backBtn} onClick={handleGoBack}>
							← Вернуться к редактированию корзины
						</button>
					</div>
				)}
			</div>
		</div>
	)
}

export default CartData
