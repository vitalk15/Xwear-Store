import { useLocation } from 'react-router-dom'
import { paths } from '@/routes/paths'
import useScrollVisibility from '@/hooks/useScrollVisibility'
import Logo from '@/components/ui/Logo'
import Navigation from './Navigation'
import HeaderActions from './HeaderActions'
import styles from './Header.module.scss'

// --- MOCK ДАННЫЕ МЕНЮ (Имитация ответа от Django API) ---
// const MOCK_MENU = [
// 	{ id: 1, title: 'Одежда', url: paths.clothes, hasDropdown: true },
// 	{ id: 2, title: 'Обувь', url: paths.shoes, hasDropdown: true },
// 	{ id: 3, title: 'Аксессуары', url: paths.accessories, hasDropdown: true },
// 	{ id: 4, title: 'Бренды', url: paths.brands, hasDropdown: true },
// 	{ id: 5, title: 'Информация', url: paths.info, hasDropdown: true },
// ]

const Header = () => {
	const location = useLocation()

	// Проверяем, находимся ли мы на главной странице
	const isHomePage = location.pathname === paths.home

	// Хук скрытия/появления хедера при скролле
	const isVisible = useScrollVisibility(300)

	return (
		<header
			className={`${styles.headerWrapper} ${!isVisible ? styles.headerHidden : ''}`}
		>
			<div className={styles.headerContainer}>
				{/* ЛОГОТИП */}
				<div className={styles.logoArea}>
					<Logo isHomePage={isHomePage} />
				</div>

				{/* НАВИГАЦИЯ */}
				<Navigation />

				{/* ИКОНКИ ДЕЙСТВИЙ */}
				<HeaderActions />
			</div>
		</header>
	)
}

export default Header
