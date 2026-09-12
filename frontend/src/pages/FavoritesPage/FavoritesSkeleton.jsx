import ProductCardSkeleton from '@/features/catalog/components/ProductCard/ProductCardSkeleton'
import styles from './FavoritesPage.module.scss'

const FavoritesSkeleton = () => {
	// Имитируем пагинацию: 4 пустых карточек
	const skeletonCards = Array.from({ length: 4 }, (_, i) => i)

	return (
		<>
			{/* Имитация хлебных крошек */}
			<div className={styles.breadcrumbsSkeleton} />

			{/* Имитация заголовка и количества товаров */}
			<div className={styles.header}>
				<div className={styles.titleSkeleton} />
				<div className={styles.countSkeleton} />
			</div>
			{/* Имитация карточек */}
			<div className={styles.grid}>
				{skeletonCards.map((index) => (
					<ProductCardSkeleton key={index} />
				))}
			</div>
		</>
	)
}

export default FavoritesSkeleton
