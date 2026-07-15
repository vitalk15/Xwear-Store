import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { SilentFallback } from '@/components/common/ErrorBoundary/SilentFallback'
import { handleCriticalError } from '@/shared/utils/errorHandler'
import SliderWidget from '@/features/slider/components/SliderWidget'
import SliderSkeleton from '@/features/slider/components/SliderSkeleton'
import CatalogSection from '@/features/catalog/components/CatalogSection'
import CatalogSkeleton from '@/features/catalog/components/CatalogSection/CatalogSkeleton'
import AboutUs from '@/pages/HomePage/components/AboutUs'
import PageTitle from '@/components/common/PageTitle'
import styles from './HomePage.module.scss'

const HomePage = () => {
	return (
		<>
			<PageTitle title="Главная" />

			{/* Слайдер */}
			<ErrorBoundary fallback={<SilentFallback />} onError={handleCriticalError}>
				<Suspense fallback={<SliderSkeleton />}>
					<SliderWidget />
				</Suspense>
			</ErrorBoundary>

			{/* Блок с секциями категорий */}
			<div className={styles.catalogWrapper}>
				{/* Секция: Обувь */}
				<ErrorBoundary fallback={<SilentFallback />} onError={handleCriticalError}>
					<Suspense fallback={<CatalogSkeleton />}>
						<CatalogSection title="Обувь" categoryId={2} />
					</Suspense>
				</ErrorBoundary>

				{/* Секция: Одежда */}
				<ErrorBoundary fallback={<SilentFallback />} onError={handleCriticalError}>
					<Suspense fallback={<CatalogSkeleton />}>
						<CatalogSection title="Одежда" categoryId={1} />
					</Suspense>
				</ErrorBoundary>

				{/* Секция: Аксессуары */}
				<ErrorBoundary fallback={<SilentFallback />} onError={handleCriticalError}>
					<Suspense fallback={<CatalogSkeleton />}>
						<CatalogSection title="Аксессуары" categoryId={3} />
					</Suspense>
				</ErrorBoundary>
			</div>

			{/* Секция: О Нас */}
			<AboutUs />
		</>
	)
}

export default HomePage
