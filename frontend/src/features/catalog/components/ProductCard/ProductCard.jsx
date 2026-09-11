import { Link } from 'react-router-dom'
import { formatPriceBy } from '@/shared/utils/formatPriceBy'
import { useFavoriteAction } from '@/features/favorites/hooks/useFavoriteAction'
import AuthModal from '@/features/auth/components/AuthModal'
import StarIcon from '@/shared/icons/star.svg'
import placeholderProduct from '@/assets/images/placeholder-product.webp'
import styles from './ProductCard.module.scss'

const ProductCard = ({ product, variantId = null, locationState = null }) => {
	const { id, naming, pricing, main_image, frontend_url } = product
	const targetVariantId = variantId || id

	const { isFav, isAuthModalOpen, setIsAuthModalOpen, handleFavoriteClick } =
		useFavoriteAction(targetVariantId)

	// Безопасно извлекаем объект с миниатюрой
	const mediumThumb = main_image?.thumbnails?.medium

	// Получаем URL картинки (если нет medium, показываем заглушку)
	const imageUrl = mediumThumb?.url || placeholderProduct

	// Динамически получаем ширину и высоту (с резервными значениями)
	const imageWidth = mediumThumb?.width || 320
	const imageHeight = mediumThumb?.height || 360

	// Форматируем цену
	const formattedPrice = formatPriceBy(pricing.min_price)

	return (
		<>
			<article className={styles.card}>
				{/* Верхняя часть: Картинка и Иконка */}
				<div
					className={styles.imageWrapper}
					style={{
						aspectRatio: `${imageWidth} / ${imageHeight}`,
					}}
				>
					<button
						className={`${styles.favoriteBtn} ${isFav ? styles.favoriteActive : ''}`}
						onClick={handleFavoriteClick}
						aria-label={isFav ? 'Удалить из избранного' : 'Добавить в избранное'}
					>
						<StarIcon className={styles.starIcon} />
					</button>

					<Link to={frontend_url} state={locationState} className={styles.imageLink}>
						<img
							src={imageUrl}
							alt={main_image?.alt || naming.full_title}
							className={styles.image}
							width={imageWidth}
							height={imageHeight}
							loading="lazy"
						/>
					</Link>
				</div>

				{/* Опционально: Палитра доступных цветов (если их больше одного) */}
				{/* {available_colors.length > 1 && (
				<div className={styles.colorsPalette}>
					{available_colors.map((colorObj, index) => (
						<Link
							key={index}
							to={colorObj.frontend_url}
							className={styles.colorDot}
							style={{ backgroundColor: colorObj.color.hex_code }}
							title={colorObj.color.name}
						/>
					))}
				</div>
			)} */}

				{/* Нижняя часть: Информация о товаре */}
				<div className={styles.infoWrapper}>
					<Link to={frontend_url} state={locationState} className={styles.titleLink}>
						<h3 className={styles.title}>
							{naming.brand.name} {naming.model}
						</h3>
					</Link>
					<span className={styles.price}>от {formattedPrice}</span>
				</div>
			</article>
			{/* Модальное окно авторизации для незарегистрированных пользователей */}
			<AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />
		</>
	)
}

export default ProductCard
