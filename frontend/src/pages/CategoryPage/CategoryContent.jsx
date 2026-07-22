import { useSearchParams } from 'react-router-dom'
import { useCategoryProducts } from '@/features/catalog/hooks/useCategoryProducts'
import { getDeclension } from '@/shared/utils/declensionWords'
import { ChevronDownIcon } from './Icons'
import { CATALOG_ITEMS_PER_PAGE } from '@/shared/constants/pagination'
import ProductCard from '@/features/catalog/components/ProductCard'
import Breadcrumbs from '@/components/common/Breadcrumbs'
import Pagination from '@/components/ui/Pagination'
import styles from './CategoryPage.module.scss'

const CategoryContent = ({ categoryId }) => {
	const [searchParams] = useSearchParams()

	// Достаем страницу из URL для передачи в бэкенд-запрос
	const currentPage = parseInt(searchParams.get('page') || '1', 10)

	// 2. Рассчитываем limit и offset для Django (LimitOffsetPagination)
	const limit = CATALOG_ITEMS_PER_PAGE // Количество товаров на страницу
	const offset = (currentPage - 1) * limit

	// Запрашиваем товары с передачей параметров в хук. Suspense поставит этот компонент "на паузу", пока данные не придут.
	const { data } = useCategoryProducts(categoryId, { limit, offset })

	// DRF возвращает нам count и results. А также мы "подмешали" category.
	const { results: products, count, category: catData } = data

	const productWord = getDeclension(count, ['товар', 'товара', 'товаров'])

	// Вычисляем общее количество страниц для компонента Pagination
	const totalPages = Math.ceil(count / limit)

	const getPageTitle = () => {
		const name = catData.name
		if (name === 'Мужчинам' || name === 'Женщинам') {
			// Достаем имя самой первой (корневой) категории из хлебных крошек
			const rootName = catData.breadcrumbs?.[0]?.name

			if (rootName) {
				// Возвращаем название корневой категории (например, "Обувь")
				// Оставляем только корень
				// return rootName

				// Склеиваем названия
				return `${rootName} ${name}` // Результат: "Обувь мужчинам"
			}
		}
		return name
	}

	return (
		<>
			<Breadcrumbs backendBreadcrumbs={catData.breadcrumbs} />

			<div className={styles.layout}>
				{/* ЛЕВЫЙ БЛОК: Сайдбар (пока заглушка) */}
				<aside className={styles.sidebar}>
					<div className={styles.sidebarPlaceholder}>Фильтры (скоро)</div>
				</aside>

				{/* ПРАВЫЙ БЛОК: Сетка товаров и пагинация */}
				<section className={styles.main}>
					<div className={styles.header}>
						<div className={styles.titleRow}>
							<h1 className={styles.title}>{getPageTitle()}</h1>
							<div className={styles.sortPlaceholder}>
								Сортировать: От дешевых к дорогим
								<ChevronDownIcon />
							</div>
						</div>
						<span className={styles.count}>
							{count} {productWord}
						</span>
					</div>

					<div className={styles.grid}>
						{products.map((product) => (
							<ProductCard key={product.id} product={product} />
						))}
					</div>

					<Pagination totalPages={totalPages} />
				</section>
			</div>
		</>
	)
}

export default CategoryContent
