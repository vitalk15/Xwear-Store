import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { SilentFallback } from '@/components/common/ErrorBoundary/SilentFallback'
import { handleCriticalError } from '@/shared/utils/errorHandler'
import PageTitle from '@/components/common/PageTitle'
import FavoritesContent from './FavoritesContent'
import FavoritesSkeleton from './FavoritesSkeleton'
import styles from './FavoritesPage.module.scss'

const FavoritesPage = () => {
	return (
		<>
			<PageTitle title="Избранные товары" />

			<div className={`container ${styles.pageWrapper}`}>
				<ErrorBoundary fallback={<SilentFallback />} onError={handleCriticalError}>
					<Suspense fallback={<FavoritesSkeleton />}>
						<FavoritesContent />
					</Suspense>
				</ErrorBoundary>
			</div>
		</>
	)
}

export default FavoritesPage
