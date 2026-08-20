import ProductCardSkeleton from '@/features/catalog/components/ProductCard/ProductCardSkeleton'
import styles from './CategoryPage.module.scss'

const CategorySkeleton = () => {
	// Имитируем пагинацию: 12 пустых карточек, как настроено в Django
	const skeletonCards = Array.from({ length: 12 }, (_, i) => i)

	return (
		<>
			{/* Имитация хлебных крошек */}
			<div className={styles.breadcrumbsSkeleton} />

			<div className={styles.layout}>
				{/* ЛЕВЫЙ БЛОК: Имитация сайдбара с фильтрами */}
				<aside className={styles.sidebar}>
					<div className={styles.sidebarSkeleton}>
						<div className={styles.filterBlockSkeleton} />
						<div className={styles.filterBlockSkeleton} />
						<div className={styles.filterBlockSkeleton} />
						<div className={styles.filterBlockSkeleton} />
					</div>
				</aside>

				{/* ПРАВЫЙ БЛОК: Сетка пустых карточек */}
				<main className={styles.main}>
					{/* Имитация заголовка и количества товаров */}
					<div className={styles.header}>
						<div className={styles.titleRow}>
							<div className={styles.titleSkeleton} />
							<div className={styles.sortPlaceholderSkeleton} />
						</div>
						<div className={styles.countSkeleton} />
					</div>
					{/* Имитация карточек */}
					<div className={styles.grid}>
						{skeletonCards.map((index) => (
							<ProductCardSkeleton key={index} />
						))}
					</div>
				</main>
			</div>
		</>
	)
}

export default CategorySkeleton
