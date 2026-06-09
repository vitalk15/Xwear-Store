import { Link, useLocation } from 'react-router-dom'
import { paths } from '@/routes/paths'
import useScrollVisibility from '@/hooks/useScrollVisibility'
import Logo from '@/components/ui/Logo'
import { SearchIcon, StarIcon, UserIcon, BagIcon, ChevronDownIcon } from './Icons'
import styles from './Header.module.scss'

// --- MOCK ДАННЫЕ МЕНЮ (Имитация ответа от Django API) ---
const MOCK_MENU = [
	{ id: 1, title: 'Одежда', url: paths.clothes, hasDropdown: true },
	{ id: 2, title: 'Обувь', url: paths.shoes, hasDropdown: true },
	{ id: 3, title: 'Аксессуары', url: paths.accessories, hasDropdown: true },
	{ id: 4, title: 'Бренды', url: paths.brands, hasDropdown: true },
	{ id: 5, title: 'Информация', url: paths.info, hasDropdown: true },
]

const Header = () => {
	// const [isVisible, setIsVisible] = useState(true)
	// const [lastScrollY, setLastScrollY] = useState(0)
	const location = useLocation()

	// Проверяем, находимся ли мы на главной странице
	const isHomePage = location.pathname === paths.home

	// Хук скрытия/появления хедера при скролле
	const isVisible = useScrollVisibility(300)

	// Имитация состояния авторизации (потом заменим на Zustand useAuthStore)
	const isAuthenticated = true

	// Имитация данных корзины (потом заменим на Zustand useCartStore)
	const cartTotalItems = 7
	const cartTotalPrice = '11 899'

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
				<nav className={styles.navArea}>
					{MOCK_MENU.map((item) => (
						<div key={item.id} className={styles.navItem}>
							{item.title}
							{item.hasDropdown && <ChevronDownIcon />}

							{/* Выпадающее меню */}
							{item.hasDropdown && (
								<div className={styles.dropdown}>
									<Link to={`${item.url}/sub1`} className={styles.dropdownItem}>
										Подкатегория 1
									</Link>
									<Link to={`${item.url}/sub2`} className={styles.dropdownItem}>
										Подкатегория 2
									</Link>
									<Link to={`${item.url}/sub3`} className={styles.dropdownItem}>
										Подкатегория 3
									</Link>
								</div>
							)}
						</div>
					))}
				</nav>

				{/* ИКОНКИ ДЕЙСТВИЙ */}
				<div className={styles.actionsArea}>
					<button className={styles.actionBtn} aria-label="Поиск">
						<SearchIcon />
					</button>

					{isAuthenticated ? (
						// Авторизованный пользователь
						<>
							<button className={styles.actionBtn} aria-label="Избранное">
								<StarIcon />
							</button>
							<button className={styles.actionBtn} aria-label="Профиль">
								<UserIcon />
							</button>
							<button
								className={`${styles.actionBtn} ${styles.cartBtn}`}
								aria-label="Корзина"
							>
								<BagIcon />
								<div className={styles.cartInfo}>
									<span>{cartTotalPrice} ₽</span>
									<span className={styles.cartBadge}>{cartTotalItems}</span>
								</div>
							</button>
						</>
					) : (
						// НЕ авторизованный пользователь
						<button className={styles.actionBtn} aria-label="Войти">
							<UserIcon />
						</button>
					)}
				</div>
			</div>
		</header>
	)
}

export default Header
