import { Link } from 'react-router-dom'
import { useCategories } from '@/hooks/useCategories'
import { ChevronDownIcon } from '../Icons'
import styles from './Navigation.module.scss'

// Статический пункт меню "Информация", имитирует структуру данных от Django API
const STATIC_INFO_MENU = {
	id: 'static-info',
	name: 'Информация',
	is_clickable: false, // Главный пункт не кликабелен, только открывает dropdown
	full_path: '',
	children: [
		{
			id: 'info-contacts',
			name: 'Контакты',
			full_path: 'contacts',
			is_clickable: true,
		},
		{
			id: 'info-delivery',
			name: 'Доставка и оплата',
			full_path: 'delivery', // Укажите здесь актуальный путь (например, 'info/delivery' или импортируйте из paths)
			is_clickable: true,
		},
		{
			id: 'info-legal',
			name: 'Юр. документы',
			full_path: 'legal-documents',
			is_clickable: true,
		},
	],
}

const Navigation = () => {
	const { data: categories = [], isLoading, isError } = useCategories()

	if (isLoading) {
		return (
			<nav className={styles.navArea}>
				<span className={styles.status}>Загрузка меню...</span>
			</nav>
		)
	}

	if (isError) {
		return (
			<nav className={styles.navArea}>
				<span className={styles.status}>Ошибка загрузки</span>
			</nav>
		)
	}

	// Объединяем динамические данные от сервера и нашу статику в один массив
	const navMenu = [...categories, STATIC_INFO_MENU]

	return (
		<nav className={styles.navArea}>
			<ul className={styles.navList}>
				{navMenu.map((item) => {
					// ПРОВЕРКА: Есть ли у этой категории вложенность 3-го уровня (дети у детей)
					const hasDeepChildren = item.children?.some(
						(child) => child.children?.length > 0,
					)

					return (
						<li
							key={item.id}
							className={`${styles.navItem} ${item.is_clickable ? styles.clickable : ''}`}
						>
							{/* КОРНЕВАЯ КАТЕГОРИЯ */}
							{item.is_clickable ? (
								<Link to={`/${item.full_path}`} className={styles.navLink}>
									{item.name}
								</Link>
							) : (
								<span className={styles.navLink}>{item.name}</span>
							)}

							{item.children?.length > 0 && <ChevronDownIcon />}

							{/* ВЫПАДАЮЩЕЕ МЕНЮ */}
							{item.children?.length > 0 && (
								<div
									// className={`${styles.dropdown} ${!hasDeepChildren ? styles.dropdownSimple : ''}`}
									className={styles.dropdown}
								>
									{hasDeepChildren ? (
										// --- ВАРИАНТ 1: МНОГОКОЛОНОЧНОЕ МЕНЮ (Одежда, Обувь) ---
										item.children.map((sub1) => (
											<div key={sub1.id} className={styles.dropdownColumn}>
												{sub1.is_clickable ? (
													<Link
														to={`/${sub1.full_path}`}
														className={`${styles.dropdownItem} ${styles.columnTitle}`}
													>
														{sub1.name}
													</Link>
												) : (
													<span className={styles.columnTitle}>{sub1.name}</span>
												)}

												{sub1.children?.length > 0 && (
													<ul className={styles.subList}>
														{sub1.children.map((sub2) => (
															<li key={sub2.id}>
																<Link
																	to={`/${sub2.full_path}`}
																	className={styles.dropdownItem}
																>
																	{sub2.name}
																</Link>
															</li>
														))}
													</ul>
												)}
											</div>
										))
									) : (
										// --- ВАРИАНТ 2: ПРОСТОЙ СПИСОК (Аксессуары, Бренды) ---
										<ul className={`${styles.subList} ${styles.simpleList}`}>
											{item.children.map((sub1) => (
												<li key={sub1.id}>
													{sub1.is_clickable ? (
														<Link
															to={`/${sub1.full_path}`}
															className={styles.dropdownItem}
														>
															{sub1.name}
														</Link>
													) : (
														<span className={styles.dropdownItem}>{sub1.name}</span>
													)}
												</li>
											))}
										</ul>
									)}
								</div>
							)}
						</li>
					)
				})}
			</ul>
		</nav>
	)
}

export default Navigation
