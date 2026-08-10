import { Link } from 'react-router-dom'
import { paths } from '@/routes/paths'
import styles from './Breadcrumbs.module.scss'

/**
 * @param {Array} backendBreadcrumbs - Массив категорий [{ name, slug, id? }]
 * @param {string} [currentTitle] - Название текущей страницы/товара (опционально)
 */
const Breadcrumbs = ({ backendBreadcrumbs = [], currentTitle = '' }) => {
	// 1. Формируем элементы категорий
	const items = backendBreadcrumbs.map((crumb, index) => {
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

	return (
		<nav className={styles.breadcrumbs} aria-label="Хлебные крошки">
			<ul className={styles.list}>
				{/* Главная страница */}
				<li className={styles.item}>
					<Link to={paths.home} className={styles.link}>
						Главная
					</Link>
				</li>
				<li className={styles.separator}>/</li>

				{/* Каталог товаров */}
				<li className={styles.item}>
					<span className={styles.text}>Каталог товаров</span>
				</li>

				{/* Категории из бэкенда */}
				{items.map((item) => (
					<div key={item.id} className={styles.crumbWrapper}>
						<li className={styles.separator}>/</li>
						<li className={styles.item}>
							{item.isClickable ? (
								<Link to={item.path} className={styles.link}>
									{item.name}
								</Link>
							) : (
								<span className={styles.text}>{item.name}</span>
							)}
						</li>
					</div>
				))}

				{/* Название текущего товара (если передано) */}
				{currentTitle && (
					<div className={styles.crumbWrapper}>
						<li className={styles.separator}>/</li>
						<li className={styles.item}>
							<span className={styles.text}>{currentTitle}</span>
						</li>
					</div>
				)}
			</ul>
		</nav>
	)
}

export default Breadcrumbs
