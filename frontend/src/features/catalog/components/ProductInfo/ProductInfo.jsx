import { useState } from 'react'
import { Link } from 'react-router-dom'
import useAuthStore from '@/features/auth/store/useAuthStore'
import { useAddToCartMutation } from '@/features/cart/hooks/useCart'
import { useCartNotificationStore } from '@/features/cart/store/useCartNotificationStore'
import { formatPriceBy } from '@/shared/utils/formatPriceBy'
import AuthModal from '@/features/auth/components/AuthModal'
import Button from '@/components/ui/Button'
import ArrowIcon from '@/shared/icons/arrow.svg'
import styles from './ProductInfo.module.scss'

const ProductInfo = ({ product }) => {
	const { naming, sizes, images, available_colors, article } = product
	const [selectedSize, setSelectedSize] = useState(null)

	const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
	const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)

	const { mutate: addToCart, isPending } = useAddToCartMutation()
	const showNotification = useCartNotificationStore((state) => state.showNotification)

	// Состояние для отслеживания предыдущего ID товара
	const [prevProductId, setPrevProductId] = useState(product.id)

	// Паттерн "Adjusting state on render" - стандарт React 19 (вместо использования useEffect для синхронизации локального стейта с входящими пропсами, который приводит к «каскадному рендеру»)
	// Если ID товара изменился (пользователь кликнул на другой цвет),
	// мы обновляем трекер и сбрасываем размер прямо во время рендера.
	if (product.id !== prevProductId) {
		setPrevProductId(product.id)
		setSelectedSize(null)
	}

	// Отфильтровываем текущий цвет для блока "Другие цвета"
	const otherColors = available_colors?.filter((c) => !c.is_current) || []

	const handleAddToCart = () => {
		// 1. Проверка авторизации
		if (!isAuthenticated) {
			setIsAuthModalOpen(true)
			return
		}

		// 2. Проверка выбора размера
		if (!selectedSize) return

		// 3. Достаем ID и название размера из объекта ProductSizeSerializer
		const sizeId = typeof selectedSize === 'object' ? selectedSize.id : selectedSize
		const sizeName = typeof selectedSize === 'object' ? selectedSize.size_name : ''

		// 4. Безопасно достаем превью главной картинки из массива images
		const mainImageObj = images?.find((img) => img.is_main) || images?.[0]
		const imageUrl = mainImageObj?.thumbnails?.small?.url || ''

		addToCart(
			{ product_size: sizeId, quantity: 1 },
			{
				onSuccess: () => {
					// Триггерим показ плашки и передаем данные для нее
					showNotification({
						name: naming.full_title,
						image: imageUrl,
						size: sizeName,
					})
				},
				onError: (error) => {
					// !!! ToDo: Заменить на всплывающее уведомление?
					console.error('Ошибка добавления в корзину:', error)
				},
			},
		)
	}

	return (
		<>
			<div className={styles.infoWrapper}>
				{/* 1. Заголовок товара */}
				<h1 className={styles.title}>{naming.full_title}</h1>
				<span className={styles.article}>AРТ. {article}</span>

				{/* 2. Сетка размеров */}
				<div className={styles.sizesSection}>
					<h3 className={styles.titleSizeSection}>EU Размеры:</h3>
					<div className={styles.sizesGrid}>
						{sizes?.map((size) => {
							const isActive = selectedSize?.id === size.id
							const isUnavailable = !size.is_available
							const hasDiscount = size.discount_percent > 0

							return (
								<div
									key={size.id}
									role="button" // Сообщаем скринридерам, что это кнопка
									tabIndex={isUnavailable ? -1 : 0} // Оставляем навигацию с клавиатуры
									className={`
                  ${styles.sizeBtn} 
                  ${isActive ? styles.active : ''} 
                  ${isUnavailable ? styles.unavailable : ''}
                `}
									onClick={() => {
										if (!isUnavailable) {
											setSelectedSize(selectedSize?.id === size.id ? null : size)
										}
									}}
									onKeyDown={(e) => {
										// Поддержка выбора размера с клавиатуры (Enter или Пробел)
										if (!isUnavailable && (e.key === 'Enter' || e.key === ' ')) {
											e.preventDefault()
											setSelectedSize(selectedSize?.id === size.id ? null : size)
										}
									}}
								>
									<span className={styles.sizeName}>{size.size_name}</span>

									<div className={styles.priceBlock}>
										{hasDiscount ? (
											<>
												<span className={styles.newPrice}>
													{formatPriceBy(size.final_price)}
												</span>
												<span className={styles.oldPrice}>
													{formatPriceBy(size.price)}
												</span>
											</>
										) : (
											<span className={styles.regularPrice}>
												{formatPriceBy(size.price)}
											</span>
										)}
									</div>
								</div>
							)
						})}
					</div>
				</div>

				{/* 3. Блок цены и кнопки добавления в корзину */}
				<div className={styles.actionBlock}>
					<div className={styles.selectedPriceInfo}>
						{selectedSize ? (
							<>
								{selectedSize.discount_percent > 0 ? (
									<div className={styles.discountWrapper}>
										<span className={styles.actionFinalPrice}>
											{formatPriceBy(selectedSize.final_price)}
										</span>
										<span className={styles.actionDiscountBadge}>
											-{selectedSize.discount_percent}%
										</span>
									</div>
								) : (
									<span className={styles.actionRegularPrice}>
										{formatPriceBy(selectedSize.price)}
									</span>
								)}
								<span className={styles.actionSizeName}>
									Размер - {selectedSize.size_name}
								</span>
							</>
						) : (
							// Заглушка, пока размер не выбран, чтобы блок не прыгал по высоте
							<span className={styles.actionRegularPrice}>&ensp;— — —</span>
						)}
					</div>

					<Button
						className={styles.addToCartBtn}
						onClick={handleAddToCart}
						// disabled={!selectedSize}
						disabled={isPending || !selectedSize}
					>
						{isPending ? 'ДОБАВЛЕНИЕ...' : 'ДОБАВИТЬ В КОРЗИНУ'}
						<ArrowIcon className={styles.cartIcon} />
					</Button>
				</div>

				{/* 4. Другие цвета (кружочки-ссылки) */}
				{otherColors.length > 0 && (
					<div className={styles.colorsSection}>
						<h3 className={styles.colorsTitle}>Другие цвета:</h3>
						<div className={styles.colorsGrid}>
							{otherColors.map((colorItem) => {
								const { color, frontend_url } = colorItem
								const isDualColor = color.hex_code_2 // Проверка на двухцветность

								return (
									<Link
										key={color.id}
										to={frontend_url}
										className={styles.colorLink}
										title={color.name}
									>
										<div
											className={styles.colorCircle}
											style={{
												background: isDualColor
													? `linear-gradient(135deg, ${color.hex_code} 50%, ${color.hex_code_2} 50%)`
													: color.hex_code,
											}}
										/>
										<span className={styles.colorName}>{color.name}</span>
									</Link>
								)
							})}
						</div>
					</div>
				)}
			</div>

			{/* Модальное окно авторизации для незарегистрированных пользователей */}
			<AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />
		</>
	)
}

export default ProductInfo
