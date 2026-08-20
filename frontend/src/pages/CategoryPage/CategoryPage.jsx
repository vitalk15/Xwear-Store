import { useParams } from 'react-router-dom'
import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { SilentFallback } from '@/components/common/ErrorBoundary/SilentFallback'
import { useCategoryByPath } from '@/entities/category/hooks/useCategoryByPath'
import { handleCriticalError } from '@/shared/utils/errorHandler'
import PageTitle from '@/components/common/PageTitle'
import CategoryContent from './CategoryContent'
import CategorySkeleton from './CategorySkeleton'
import styles from './CategoryPage.module.scss'

const CategoryPage = () => {
	// Ловим всё, что идет после /catalog/ (например: obuv/muzhchinam)
	const { '*': fullPath } = useParams()

	// Ищем ID категории в нашем закэшированном дереве навигации
	const category = useCategoryByPath(fullPath)

	// !!! Todo: Потом заменить на показ страницы PageNotFound
	if (!category) {
		return (
			<div className="container" style={{ padding: '80px 0' }}>
				Категория не найдена (404)
			</div>
		)
	}

	return (
		<>
			<PageTitle title="Каталог" />

			<div className={`container ${styles.pageWrapper}`}>
				<ErrorBoundary fallback={<SilentFallback />} onError={handleCriticalError}>
					<Suspense fallback={<CategorySkeleton />}>
						{/* Передаем ID найденной категории во внутренний компонент */}
						<CategoryContent categoryId={category.id} />
					</Suspense>
				</ErrorBoundary>
			</div>
		</>
	)
}

export default CategoryPage
