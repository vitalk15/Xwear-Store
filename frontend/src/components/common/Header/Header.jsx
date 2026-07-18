import { useState, Suspense } from 'react'
import { useLocation } from 'react-router-dom'
import { ErrorBoundary } from 'react-error-boundary'
import { paths } from '@/routes/paths'
import { SilentFallback } from '@/components/common/ErrorBoundary/SilentFallback'
import { handleCriticalError } from '@/shared/utils/errorHandler'
import useScrollVisibility from './hooks/useScrollVisibility'
import Logo from '@/components/ui/Logo'
import Navigation from './components/Navigation'
import NavigationSkeleton from './components/Navigation/NavigationSkeleton'
import HeaderActions from './components/HeaderActions'
import styles from './Header.module.scss'

const Header = () => {
	const location = useLocation()
	const isHomePage = location.pathname === paths.home // Проверяем, находимся ли мы на главной странице
	const isVisible = useScrollVisibility(160) // Хук скрытия/появления хедера при скролле
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
					<ErrorBoundary fallback={<SilentFallback />} onError={handleCriticalError}>
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
