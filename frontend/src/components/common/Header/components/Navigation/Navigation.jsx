import { Link } from 'react-router-dom'
import { useCategories } from '@/entities/category/hooks/useCategories'
import { ChevronDownIcon } from '@/components/common/Header/Icons'
import { STATIC_INFO_MENU } from '@/shared/constants/info-menu'
import { getLinkPath } from '@/shared/utils/getLinkPath'
import styles from './Navigation.module.scss'

const Navigation = () => {
	const { data: categories = [] } = useCategories()

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
								<Link to={getLinkPath(item, item)} className={styles.navLink}>
									{item.name}
								</Link>
							) : (
								<span className={styles.navLink}>{item.name}</span>
							)}

							{item.children?.length > 0 && <ChevronDownIcon />}

							{/* ВЫПАДАЮЩЕЕ МЕНЮ */}
							{item.children?.length > 0 && (
								<div className={styles.dropdownWrapper}>
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
															to={getLinkPath(item, sub1)}
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
																		to={getLinkPath(item, sub2)}
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
																to={getLinkPath(item, sub1)}
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
