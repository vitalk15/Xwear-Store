import ProductCardSkeleton from '@/features/catalog/components/ProductCard/ProductCardSkeleton'
import skeletonStyles from './CatalogSkeleton.module.scss'
import styles from '../CatalogSection.module.scss'

const CatalogSkeleton = () => {
	return (
		<section className={styles.section}>
			<div className="container">
				{/* Пульсирующая заглушка для заголовка секции */}
				<div className={skeletonStyles.titleSkeleton}></div>

				<div className={styles.row}>
					{/* Генерируем 4 скелетона карточек */}
					{[...Array(4)].map((_, index) => (
						<ProductCardSkeleton key={index} />
					))}
				</div>
			</div>
		</section>
	)
}

export default CatalogSkeleton
