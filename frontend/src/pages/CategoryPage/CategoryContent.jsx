import { useState } from 'react'
import { useCategoryProducts } from '@/features/catalog/hooks/useCategoryProducts'
import { getDeclension } from '@/shared/utils/declensionWords'
import ProductCard from '@/features/catalog/components/ProductCard'
import Breadcrumbs from '@/components/common/Breadcrumbs'
import Pagination from '@/components/ui/Pagination'
import styles from './CategoryPage.module.scss'

const CategoryContent = ({ categoryId }) => {
	// Состояние пагинации (позже перенесем в URL-параметры)
	const [page, setPage] = useState(1)
	const limit = 12 // Настройка из Django
	const offset = (page - 1) * limit

	// Запрашиваем товары. Suspense поставит этот компонент "на паузу", пока данные не придут
	const { data } = useCategoryProducts(categoryId, { limit, offset })

	// DRF возвращает нам count и results. А также мы "подмешали" category.
	const { results: products, count, category: catData } = data

	const productWord = getDeclension(count, ['товар', 'товара', 'товаров'])
	const totalPages = Math.ceil(count / limit)

	return (
		<>
			<Breadcrumbs backendBreadcrumbs={catData.breadcrumbs} />

			<div className={styles.header}>
				<div className={styles.titleRow}>
					<h1 className={styles.title}>{catData.name}</h1>
					<div className={styles.sortPlaceholder}>
						Сортировать по: От дешевых к дорогим ˅
					</div>
				</div>
				<span className={styles.count}>
					{count} {productWord}
				</span>
			</div>

			<div className={styles.layout}>
				{/* ЛЕВЫЙ БЛОК: Сайдбар (пока заглушка) */}
				<aside className={styles.sidebar}>
					<div className={styles.sidebarPlaceholder}>Фильтры (скоро)</div>
				</aside>

				{/* ПРАВЫЙ БЛОК: Сетка товаров и пагинация */}
				<main className={styles.main}>
					<div className={styles.grid}>
						{products.map((product) => (
							<ProductCard key={product.id} product={product} />
						))}
					</div>

					<Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />
				</main>
			</div>
		</>
	)
}

export default CategoryContent
