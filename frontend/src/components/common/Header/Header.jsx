import { useState, Suspense } from 'react'
import { useLocation } from 'react-router-dom'
import { ErrorBoundary } from 'react-error-boundary'
import { paths } from '@/routes/paths'
import useScrollVisibility from '@/hooks/useScrollVisibility'
import Logo from '@/components/ui/Logo'
import Navigation from './Navigation'
import NavigationSkeleton from './Navigation/NavigationSkeleton'
import HeaderActions from './HeaderActions'
import styles from './Header.module.scss'

// Что показать, если категории не загрузились
const NavigationErrorFallback = () => (
	<nav className={styles.navAreaError}>
		<span className={styles.errorText}>Каталог временно недоступен</span>
	</nav>
)

const Header = () => {
	const location = useLocation()
	const isHomePage = location.pathname === paths.home // Проверяем, находимся ли мы на главной странице
	const isVisible = useScrollVisibility(300) // Хук скрытия/появления хедера при скролле
	const [isSearchOpen, setIsSearchOpen] = useState(false) // Стейт для управления состоянием поисковой строки

	return (
		<header
			className={`${styles.headerWrapper} ${!isVisible ? styles.headerHidden : ''}`}
		>
			<div className={`container ${styles.headerContainer}`}>
				{/* ЛОГОТИП */}
				<div className={styles.logoArea}>
					<Logo isHomePage={isHomePage} />
				</div>

				{/* НАВИГАЦИЯ */}
				<div className={`${styles.navWrapper} ${isSearchOpen ? styles.navHidden : ''}`}>
					{/* Если ошибка загрузки — показывается запасной вариант */}
					<ErrorBoundary FallbackComponent={NavigationErrorFallback}>
						{/* Пока идет загрузка — показывается скелетон */}
						<Suspense fallback={<NavigationSkeleton />}>
							<Navigation />
						</Suspense>
					</ErrorBoundary>
				</div>

				{/* ИКОНКИ ДЕЙСТВИЙ */}
				<HeaderActions isSearchOpen={isSearchOpen} setIsSearchOpen={setIsSearchOpen} />
			</div>
		</header>
	)
}

export default Header
