import { Link } from 'react-router-dom'
import { StarIcon } from './Icons'
import { formatPriceBy } from '@/shared/utils/formatPriceBy'
import placeholderProduct from '@/assets/images/placeholder-product.webp'
import styles from './ProductCard.module.scss'

const ProductCard = ({ product }) => {
	// const { id, naming, pricing, main_image, frontend_url, available_colors = [] } = product
	const { id, naming, pricing, main_image, frontend_url } = product

	// Безопасно извлекаем объект с миниатюрой
	const mediumThumb = main_image?.thumbnails?.medium

	// Получаем URL картинки (если нет medium, показываем заглушку)
	const imageUrl = mediumThumb?.url || placeholderProduct

	// Динамически получаем ширину и высоту (с резервными значениями)
	const imageWidth = mediumThumb?.width || 320
	const imageHeight = mediumThumb?.height || 360

	// Форматируем цену
	const formattedPrice = formatPriceBy(pricing.min_price)

	const handleFavoriteClick = (e) => {
		e.preventDefault() // Чтобы клик по звездочке не перекидывал на страницу товара
		// TODO: Интегрировать Zustand store для проверки авторизации и добавления в избранное
		console.log(`Клик по избранному для товара ${id}`)
	}

	return (
		<article className={styles.card}>
			{/* Верхняя часть: Картинка и Иконка */}
			<div
				className={styles.imageWrapper}
				style={{
					aspectRatio: `${imageWidth} / ${imageHeight}`,
				}}
			>
				<button
					className={styles.favoriteBtn}
					onClick={handleFavoriteClick}
					aria-label="Добавить в избранное"
				>
					<StarIcon />
				</button>

				<Link to={frontend_url} className={styles.imageLink}>
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
				<Link to={frontend_url} className={styles.titleLink}>
					<h3 className={styles.title}>
						{naming.brand.name} {naming.model}
					</h3>
				</Link>
				<span className={styles.price}>от {formattedPrice}</span>
			</div>
		</article>
	)
}

export default ProductCard
