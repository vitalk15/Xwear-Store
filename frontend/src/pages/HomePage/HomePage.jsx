import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import SliderWidget from '@/features/slider/components/SliderWidget'
import SliderSkeleton from '@/features/slider/components/SliderSkeleton'
import CatalogSection from '@/features/catalog/components/CatalogSection'
import CatalogSkeleton from '@/features/catalog/components/CatalogSection/CatalogSkeleton'
import PageTitle from '@/components/common/PageTitle'
import styles from './HomePage.module.scss'

const HomePage = () => {
	return (
		<>
			<PageTitle title="Главная" />
			{/* Слайдер */}
			<ErrorBoundary fallback={<div className="container">Ошибка загрузки баннеров</div>}>
				<Suspense fallback={<SliderSkeleton />}>
					<SliderWidget />
				</Suspense>
			</ErrorBoundary>

			{/* Блок с секциями */}
			<div className={styles.catalogWrapper}>
				{/* Секция: Обувь */}
				<ErrorBoundary
					fallback={<div className="container">Ошибка загрузки категории "Обувь"</div>}
				>
					<Suspense fallback={<CatalogSkeleton />}>
						<CatalogSection title="Обувь" categoryId={2} />
					</Suspense>
				</ErrorBoundary>

				{/* Секция: Одежда */}
				<ErrorBoundary
					fallback={<div className="container">Ошибка загрузки категории "Одежда"</div>}
				>
					<Suspense fallback={<CatalogSkeleton />}>
						<CatalogSection title="Одежда" categoryId={1} />
					</Suspense>
				</ErrorBoundary>

				{/* Секция: Аксессуары */}
				<ErrorBoundary
					fallback={
						<div className="container">Ошибка загрузки категории "Аксессуары"</div>
					}
				>
					<Suspense fallback={<CatalogSkeleton />}>
						<CatalogSection title="Аксессуары" categoryId={3} />
					</Suspense>
				</ErrorBoundary>
			</div>
		</>
	)
}

export default HomePage
