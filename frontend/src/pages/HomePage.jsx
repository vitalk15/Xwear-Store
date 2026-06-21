import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import SliderWidget from '@/features/slider/components/SliderWidget'
import SliderSkeleton from '@/features/slider/components/SliderSkeleton'
import PageTitle from '@/components/common/PageTitle'

const HomePage = () => {
	return (
		<div>
			<PageTitle title="Главная" />
			{/* Слайдер с безопасной загрузкой */}
			<ErrorBoundary fallback={<div className="container">Ошибка загрузки баннеров</div>}>
				<Suspense fallback={<SliderSkeleton />}>
					<SliderWidget />
				</Suspense>
			</ErrorBoundary>
		</div>
	)
}

export default HomePage
