import { useLocation } from 'react-router-dom'
import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { paths } from '@/routes/paths'
import useScrollVisibility from '@/hooks/useScrollVisibility'
import Logo from '@/components/ui/Logo'
import Navigation from './Navigation'
import NavigationSkeleton from './Navigation/NavigationSkeleton'
import HeaderActions from './HeaderActions'
import styles from './Header.module.scss'

// Что показать, если категории не загрузились
// const NavigationErrorFallback = ({ resetErrorBoundary }) => (
// 	<nav className={styles.navAreaError}>
// 		<span className={styles.errorText}>Каталог временно недоступен</span>
// 		<button onClick={resetErrorBoundary} className={styles.retryButton}>
// 			Обновить ↻
// 		</button>
// 	</nav>
// )

// Что показать, если категории не загрузились
const NavigationErrorFallback = () => (
	<nav className={styles.navAreaError}>
		<span className={styles.errorText}>Каталог временно недоступен</span>
	</nav>
)

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
				{/* Если ошибка загрузки — показывается запасной вариант */}
				<ErrorBoundary FallbackComponent={NavigationErrorFallback}>
					{/* Пока идет загрузка — показывается скелетон */}
					<Suspense fallback={<NavigationSkeleton />}>
						<Navigation />
					</Suspense>
				</ErrorBoundary>

				{/* ИКОНКИ ДЕЙСТВИЙ */}
				<HeaderActions />
			</div>
		</header>
	)
}

export default Header
