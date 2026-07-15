import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { useLocation } from 'react-router-dom'
import { paths } from '@/routes/paths'
import { SilentFallback } from '@/components/common/ErrorBoundary/SilentFallback'
import { handleError } from '@/shared/utils/errorHandler'
import Logo from '@/components/ui/Logo'
import Navigation from './components/Navigation'
import NavigationSkeleton from './components/Navigation/NavigationSkeleton'
import Contacts from './components/Contacts'
import ContactsSkeleton from './components/Contacts/ContactsSkeleton'
import Subscribe from './components/Subscribe'
import SubscribeSkeleton from './components/Subscribe/SubscribeSkeleton'
import styles from './Footer.module.scss'

const Footer = () => {
	const location = useLocation()
	const isHomePage = location.pathname === paths.home // Проверяем, находимся ли мы на главной странице

	return (
		<footer className={styles.footer}>
			<div className="container">
				<div className={styles.topRow}>
					{/* Навигация */}
					<div className={styles.contentsWrapper}>
						<ErrorBoundary fallback={<SilentFallback />} onError={handleError}>
							<Suspense fallback={<NavigationSkeleton />}>
								<Navigation />
							</Suspense>
						</ErrorBoundary>
					</div>

					{/* Контакты */}
					<div className={styles.contentsWrapper}>
						<ErrorBoundary fallback={<SilentFallback />} onError={handleError}>
							<Suspense fallback={<ContactsSkeleton />}>
								<Contacts />
							</Suspense>
						</ErrorBoundary>
					</div>

					{/* Подписка */}
					<div className={styles.contentsWrapper}>
						<ErrorBoundary fallback={<SilentFallback />} onError={handleError}>
							<Suspense fallback={<SubscribeSkeleton />}>
								<Subscribe />
							</Suspense>
						</ErrorBoundary>
					</div>
				</div>

				<div className={styles.bottomRow}>
					{/* Логотип и копирайт */}
					<div className={styles.brandCol}>
						<Logo isHomePage={isHomePage} position="footer" />
						{/* <p className={styles.copyright}>
							© {new Date().getFullYear()} Xwear. Все права защищены.
						</p> */}
					</div>
				</div>
			</div>
		</footer>
	)
}

export default Footer
