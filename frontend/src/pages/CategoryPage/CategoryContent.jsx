import { useSearchParams } from 'react-router-dom'
import { useCategoryProducts } from '@/features/catalog/hooks/useCategoryProducts'
import { getDeclension } from '@/shared/utils/declensionWords'
import { ChevronDownIcon } from './Icons'
import { CATALOG_ITEMS_PER_PAGE } from '@/shared/constants/pagination'
import ProductCard from '@/features/catalog/components/ProductCard'
import Breadcrumbs from '@/components/common/Breadcrumbs'
import Pagination from '@/components/ui/Pagination'
import CatalogSidebar from '@/features/catalog/components/CatalogSidebar'
import SortDropdown from '@/features/catalog/components/SortDropdown'
import styles from './CategoryPage.module.scss'

const CategoryContent = ({ categoryId }) => {
	const [searchParams] = useSearchParams()

	// 1. Пагинация
	// Достаем страницу из URL для передачи в бэкенд-запрос
	const currentPage = parseInt(searchParams.get('page') || '1', 10)

	// Рассчитываем limit и offset для Django (LimitOffsetPagination)
	const limit = CATALOG_ITEMS_PER_PAGE // Количество товаров на страницу
	const offset = (currentPage - 1) * limit

	// 2. Собираем ВСЕ параметры фильтров из URL для передачи на бэкенд
	const apiParams = {
		limit,
		offset,
		brands: searchParams.get('brands') || undefined,
		sizes: searchParams.get('sizes') || undefined,
		colors: searchParams.get('colors') || undefined,
		min_price: searchParams.get('min_price') || undefined,
		max_price: searchParams.get('max_price') || undefined,
		sort: searchParams.get('sort') || undefined,
	}

	// 3. Отправляем запрос (пустые параметры axios/fetch автоматически проигнорируют, если хук настроен верно). Suspense поставит этот компонент "на паузу", пока данные не придут.
	const { data } = useCategoryProducts(categoryId, apiParams)

	// 4. Вытаскиваем данные от Django
	const { results: products, count, category: catData, filters } = data

	// Вычисляем общее количество страниц для компонента Pagination
	const totalPages = Math.ceil(count / limit)

	// 5. Применяем утилиту для правильного склонения
	const productWord = getDeclension(count, ['товар', 'товара', 'товаров'])

	// 6. Формирование заголовка
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
				{/* ЛЕВЫЙ БЛОК: Сайдбар */}
				<CatalogSidebar filters={filters} />

				{/* ПРАВЫЙ БЛОК: Сетка товаров, сортировка и пагинация */}
				<section className={styles.main}>
					<div className={styles.header}>
						<div className={styles.titleRow}>
							<h1 className={styles.title}>{getPageTitle()}</h1>
							<div className={styles.sortPlaceholder}>
								Сортировать:
								<SortDropdown />
								{/* <ChevronDownIcon /> */}
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
