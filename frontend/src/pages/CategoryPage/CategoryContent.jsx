import { useSearchParams } from 'react-router-dom'
import { useCategoryProducts } from '@/features/catalog/hooks/useCategoryProducts'
import { getDeclension } from '@/shared/utils/declensionWords'
import { CATALOG_ITEMS_PER_PAGE } from '@/shared/constants/pagination'
import ProductCard from '@/features/catalog/components/ProductCard'
import Breadcrumbs from '@/components/common/Breadcrumbs'
import Pagination from '@/components/ui/Pagination'
import CatalogSidebar from '@/features/catalog/components/CatalogSidebar'
import SortDropdown from '@/features/catalog/components/SortDropdown'
import styles from './CategoryPage.module.scss'

const CategoryContent = ({ categoryId }) => {
	const [searchParams] = useSearchParams()

	// Извлекаем поисковый запрос из URL
	const searchQuery = searchParams.get('search') || undefined

	// 1. Пагинация
	// Достаем страницу из URL для передачи в бэкенд-запрос
	const currentPage = parseInt(searchParams.get('page') || '1', 10)

	// Рассчитываем limit и offset для Django (LimitOffsetPagination)
	const limit = CATALOG_ITEMS_PER_PAGE // Количество товаров на страницу
	const offset = (currentPage - 1) * limit

	// 2. Собираем ВСЕ параметры фильтров, сортировки и поискового запроса из URL для передачи на бэкенд
	const apiParams = {
		limit,
		offset,
		brands: searchParams.get('brands') || undefined,
		sizes: searchParams.get('sizes') || undefined,
		colors: searchParams.get('colors') || undefined,
		min_price: searchParams.get('min_price') || undefined,
		max_price: searchParams.get('max_price') || undefined,
		sort: searchParams.get('sort') || undefined,
		search: searchQuery,
	}

	// 3. Отправляем запрос (пустые параметры axios/fetch автоматически проигнорируют, если хук настроен верно). Suspense поставит этот компонент "на паузу", пока данные не придут.
	const { data } = useCategoryProducts(categoryId, apiParams)

	// 4. Вытаскиваем данные от Django
	const { results: products, count, category: catData, filters } = data

	// Флаг: категория абсолютно пустая сама по себе
	const isCategoryEmpty = count === 0

	// Вычисляем общее количество страниц для компонента Pagination
	const totalPages = Math.ceil(count / limit)

	// 5. Применяем утилиту для правильного склонения
	const productWord = getDeclension(count, ['товар', 'товара', 'товаров'])

	// 6. Формирование заголовка
	const getPageTitle = () => {
		// Если есть поисковый запрос, приоритет отдается ему
		if (searchQuery) {
			return `Результаты поиска: «${searchQuery}»`
		}

		const name = catData?.name
		if (name === 'Мужчинам' || name === 'Женщинам') {
			// Достаем имя самой первой (корневой) категории из хлебных крошек
			const rootName = catData?.breadcrumbs?.[0]?.name

			if (rootName) {
				// Возвращаем название корневой категории (например, "Обувь")
				// Оставляем только корень
				// return rootName

				// Склеиваем названия
				return `${rootName} ${name}` // Результат: "Обувь мужчинам"
			}
		}
		// Фолбек, если catData.name нет (например, на корневой странице)
		return name || 'Каталог'
	}

	return (
		<>
			{/* Если данных категории нет (например, глобальный поиск), крошки не рендерим */}
			{catData?.breadcrumbs && <Breadcrumbs backendBreadcrumbs={catData.breadcrumbs} />}

			<div
				className={`${styles.layout} ${!catData?.breadcrumbs ? styles.layoutNoBreadcrumbs : ''}`}
			>
				{/* ЛЕВЫЙ БЛОК: Сайдбар */}
				{/* Показываем сайдбар ТОЛЬКО если категория не пустая */}
				{!isCategoryEmpty && <CatalogSidebar filters={filters} categoryId={categoryId} />}

				{/* ПРАВЫЙ БЛОК: Сетка товаров, сортировка и пагинация */}
				<section className={styles.main}>
					<div className={styles.header}>
						<div className={styles.titleRow}>
							<h1 className={styles.title}>{getPageTitle()}</h1>
							{/* Сортировку тоже скрываем, если товаров вообще нет */}
							{!isCategoryEmpty && (
								<div className={styles.sortPlaceholder}>
									Сортировать:
									<SortDropdown />
								</div>
							)}
						</div>
						<span className={styles.count}>
							{count} {productWord}
						</span>
					</div>

					{/* Сетка товаров */}
					{count > 0 ? (
						// 1. Если товары есть — рендерим сетку
						<>
							<div className={styles.grid}>
								{products.map((product) => (
									<ProductCard key={product.id} product={product} />
								))}
							</div>

							{/* Пагинация */}
							<Pagination totalPages={totalPages} />
						</>
					) : (
						// 2. Если категория пустая или по поиску ничего не найдено
						<div className={styles.emptyState}>
							{searchQuery ? (
								<>
									<h2>По вашему запросу «{searchQuery}» ничего не найдено</h2>
									<p>
										Попробуйте изменить формулировку, проверить орфографию или поискать
										что-то другое.
									</p>
								</>
							) : (
								<>
									<h2>В этой категории пока нет товаров</h2>
									<p>Мы уже работаем над пополнением ассортимента!</p>
								</>
							)}
						</div>
					)}
				</section>
			</div>
		</>
	)
}

export default CategoryContent
