import { Fragment } from 'react'
import { Link } from 'react-router-dom'
import { paths } from '@/routes/paths'
import styles from './Breadcrumbs.module.scss'

/**
 * Универсальный компонент хлебных крошек.
 *
 * @param {Array<{ name: string, path?: string, id?: string|number }>} [items] - Массив крошек для статичных страниц (ЛК, Корзина и т.д. Например items={[{ name: 'Личный кабинет',
 * path: paths.profile }, { name: 'Мои заказы' }]})
 * @param {Array<{ name: string, slug: string, id?: string|number }>} [backendBreadcrumbs] - Массив категорий с бэкенда (для каталога)
 * @param {string} [currentTitle] - Название текущего товара или страницы (опционально)
 */
const Breadcrumbs = ({ items = null, backendBreadcrumbs = [], currentTitle = '' }) => {
	let listItems = []

	// 1. Если передан кастомный массив items (для статичных страниц)
	if (items && Array.isArray(items)) {
		listItems = items.map((item, index) => {
			const isLast = index === items.length - 1
			return {
				id: item.id || item.path || index,
				name: item.name,
				path: item.path,
				// Кликабельно только если есть путь и это не последняя крошка
				isClickable: Boolean(item.path) && !isLast,
			}
		})
	}
	// 2. Если переданы категории бэкенда или название товара (для каталога и карточки товара)
	else if (backendBreadcrumbs.length > 0 || currentTitle) {
		// const isCatalogClickable = backendBreadcrumbs.length > 0 || Boolean(currentTitle)
		// Жёстко задаём пункт "Каталог товаров" некликабельным
		const catalogItem = {
			id: 'catalog-root',
			name: 'Каталог товаров',
			path: paths.catalog,
			isClickable: false,
		}

		// Формируем элементы категорий
		const categoryItems = backendBreadcrumbs.map((crumb, index) => {
			// Собираем полный путь (например: obuv/muzhchinam/krossovki)
			const fullPath = backendBreadcrumbs
				.slice(0, index + 1)
				.map((c) => c.slug)
				.join('/')

			// Если передан currentTitle, значит, все категории в цепочке должны быть кликабельны, если нет - то текущая не кликабельна
			const isLastCategory = index === backendBreadcrumbs.length - 1 // Текущая страница
			// const isRoot = index === 0 // Корневая категория (Обувь, Одежда)
			const isClickable = currentTitle ? true : !isLastCategory

			return {
				id: crumb.id || crumb.slug || index,
				name: crumb.name,
				path: `${paths.catalog}/${fullPath}`,
				// isClickable: !isRoot && !isLast,
				isClickable,
			}
		})

		listItems = [catalogItem, ...categoryItems]

		if (currentTitle) {
			listItems.push({
				id: 'current-title',
				name: currentTitle,
				isClickable: false,
			})
		}
	}
	// 3. Если компонент вызван без аргументов (корневая страница каталога)
	else {
		listItems = [
			{
				id: 'catalog-root',
				name: 'Каталог товаров',
				isClickable: false,
			},
		]
	}

	return (
		<nav className={styles.breadcrumbs} aria-label="Хлебные крошки">
			<ul className={styles.list}>
				{/* Главная страница */}
				<li className={styles.item}>
					<Link to={paths.home} className={styles.link}>
						Главная
					</Link>
				</li>

				{/* Отрисовка всех цепочек крошек */}
				{listItems.map((item) => (
					<Fragment key={item.id}>
						<li className={styles.separator}>/</li>
						<li className={styles.item}>
							{item.isClickable && item.path ? (
								<Link to={item.path} className={styles.link}>
									{item.name}
								</Link>
							) : (
								<span className={styles.text}>{item.name}</span>
							)}
						</li>
					</Fragment>
				))}
			</ul>
		</nav>
	)
}

export default Breadcrumbs
