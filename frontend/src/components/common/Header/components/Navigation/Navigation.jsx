import { Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { useCategories } from '@/entities/category/hooks/useCategories'
import { ChevronDownIcon } from '@/components/common/Header/Icons'
import { STATIC_INFO_MENU } from '@/shared/constants/info-menu'
import { getLinkPath } from '@/shared/utils/getLinkPath'
import styles from './Navigation.module.scss'

const Navigation = () => {
	const { data: categories = [] } = useCategories()
	const location = useLocation()

	// --- ЗАКРЫТИЕ ВЫПАДАЮЩЕГО МЕНЮ ПРИ ПЕРЕХОДЕ ---

	// 1. Храним ID текущей наведенной категории
	const [activeItemId, setActiveItemId] = useState(null)

	// 2. Трекер для принудительного закрытия меню при смене URL
	const currentUrl = location.pathname + location.search
	const [prevUrl, setPrevUrl] = useState(currentUrl)

	if (currentUrl !== prevUrl) {
		setPrevUrl(currentUrl)
		setActiveItemId(null) // Сбрасываем меню
	}

	// 3. Хэндлер для принудительного закрытия при клике на любую ссылку
	const handleLinkClick = () => {
		setActiveItemId(null)
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

					const isOpen = activeItemId === item.id

					return (
						<li
							key={item.id}
							className={`${styles.navItem} ${item.is_clickable ? styles.clickable : ''}`}
							onMouseEnter={() => setActiveItemId(item.id)}
							onMouseLeave={() => setActiveItemId(null)}
						>
							{/* КОРНЕВАЯ КАТЕГОРИЯ */}
							{item.is_clickable ? (
								<Link
									to={getLinkPath(item, item)}
									className={styles.navLink}
									onClick={handleLinkClick}
								>
									{item.name}
								</Link>
							) : (
								<span className={styles.navLink}>{item.name}</span>
							)}

							{item.children?.length > 0 && <ChevronDownIcon />}

							{/* ВЫПАДАЮЩЕЕ МЕНЮ */}
							{item.children?.length > 0 && isOpen && (
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
															onClick={handleLinkClick}
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
																		onClick={handleLinkClick}
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
																onClick={handleLinkClick}
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
