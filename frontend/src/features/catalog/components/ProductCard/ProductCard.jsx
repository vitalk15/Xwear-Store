import { Link } from 'react-router-dom'
import { formatPriceBy } from '@/shared/utils/formatPriceBy'
import ButtonFavorite from '@/features/favorites/components/ButtonFavorite'
import placeholderProduct from '@/assets/images/placeholder-product.webp'
import styles from './ProductCard.module.scss'

const ProductCard = ({ product, variantId = null, locationState = null }) => {
	const { id, naming, pricing, main_image, frontend_url } = product
	const targetVariantId = variantId || id

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
					<ButtonFavorite targetId={targetVariantId} className={styles.favoriteBtn} />

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
		</>
	)
}

export default ProductCard
