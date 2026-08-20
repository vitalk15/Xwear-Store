import ProductCardSkeleton from '@/features/catalog/components/ProductCard/ProductCardSkeleton'
import styles from './ProductDetailPage.module.scss'

const ProductDetailSkeleton = () => {
	return (
		<>
			{/* Имитация хлебных крошек */}
			<div className={styles.breadcrumbsSkeleton} />
			{/* Верхняя секция: Галерея + Информация о товаре */}
			<div className={styles.topSection}>
				{/* Левая колонка: Карусель / Галерея изображений */}
				<div className={styles.galleryBlock}>
					{/* Главное изображение */}
					<div className={styles.mainImageSkeleton} />
					{/* Превью (миниатюры) слева или снизу */}
					<div className={styles.thumbnails}>
						{Array.from({ length: 4 }).map((_, i) => (
							<div key={i} className={styles.thumbnailSkeleton} />
						))}
					</div>
				</div>

				{/* Правая колонка: Детали товара */}
				<div className={styles.infoBlock}>
					{/* Название товара (2 строки) */}
					<div className={styles.titleSkeletonLine1} />
					<div className={styles.titleSkeletonLine2} />

					{/* Сетка размеров */}
					<div className={styles.sizeSection}>
						<div className={styles.labelSizeSkeleton} />
						<div className={styles.sizeGrid}>
							{Array.from({ length: 8 }).map((_, i) => (
								<div key={i} className={styles.sizeBoxSkeleton} />
							))}
						</div>
					</div>

					<div className={styles.actionBlock}>
						{/* Цена */}
						<div className={styles.priceSkeleton} />
						{/* Кнопка добавления в корзину */}
						<div className={styles.buttonSkeleton} />
					</div>
				</div>
			</div>

			{/* Описание */}
			<div className={styles.descSection}>
				<div className={styles.descTitleSkeleton} />
				<div className={styles.descSkeleton} />
			</div>

			{/* Характеристики */}
			<div className={styles.characterSection}>
				<div className={styles.characterTitleSkeleton} />
				<div className={styles.characterSkeleton} />
			</div>

			{/* Рекомендации */}
			<div className={styles.recommendsSection}>
				<div className={styles.recommendsTitleSkeleton} />
				<div className={styles.recommendsGrid}>
					{Array.from({ length: 4 }).map((_, i) => (
						<ProductCardSkeleton key={i} />
					))}
				</div>
			</div>
		</>
	)
}

export default ProductDetailSkeleton
