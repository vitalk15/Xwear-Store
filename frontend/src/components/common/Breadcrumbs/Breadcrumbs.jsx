import { Link } from 'react-router-dom'
import { paths } from '@/routes/paths'
import styles from './Breadcrumbs.module.scss'

const Breadcrumbs = ({ backendBreadcrumbs = [] }) => {
	// Формируем массив для рендера
	const items = backendBreadcrumbs.map((crumb, index) => {
		// Собираем полный путь (например: obuv/muzhchinam/krossovki)
		const fullPath = backendBreadcrumbs
			.slice(0, index + 1)
			.map((c) => c.slug)
			.join('/')

		const isRoot = index === 0 // Корневая категория (Обувь, Одежда)
		const isLast = index === backendBreadcrumbs.length - 1 // Текущая страница

		return {
			id: crumb.id,
			name: crumb.name,
			path: `${paths.catalog}/${fullPath}`,
			isClickable: !isRoot && !isLast, // Кликабельны только промежуточные
		}
	})

	return (
		<nav className={styles.breadcrumbs} aria-label="Хлебные крошки">
			<ul className={styles.list}>
				<li className={styles.item}>
					<Link to={paths.home} className={styles.link}>
						Главная
					</Link>
				</li>
				<li className={styles.separator}>/</li>

				<li className={styles.item}>
					<span className={styles.text}>Каталог товаров</span>
				</li>

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
			</ul>
		</nav>
	)
}

export default Breadcrumbs
