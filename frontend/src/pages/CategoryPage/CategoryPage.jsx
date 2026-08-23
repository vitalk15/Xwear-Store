import { useParams } from 'react-router-dom'
import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { SilentFallback } from '@/components/common/ErrorBoundary/SilentFallback'
import { useCategoryByPath } from '@/entities/category/hooks/useCategoryByPath'
import { handleCriticalError } from '@/shared/utils/errorHandler'
import PageTitle from '@/components/common/PageTitle'
import NotFoundPage from '../NotFoundPage'
import CategoryContent from './CategoryContent'
import CategorySkeleton from './CategorySkeleton'
import styles from './CategoryPage.module.scss'

const CategoryPage = () => {
	// Ловим всё, что идет после /catalog/ (например: obuv/muzhchinam)
	const { '*': fullPath } = useParams()

	// Ищем ID категории в нашем закэшированном дереве навигации
	const category = useCategoryByPath(fullPath)

	if (fullPath && !category)
		return <NotFoundPage title="Упс! Категория не найдена (404)" />

	// Если пути нет (fullPath === ""), значит мы в корне каталога (глобальный поиск).
	// Передаем categoryId как null (или undefined)
	const targetCategoryId = category ? category.id : null

	return (
		<>
			<PageTitle title="Каталог" />

			<div className={`container ${styles.pageWrapper}`}>
				<ErrorBoundary fallback={<SilentFallback />} onError={handleCriticalError}>
					<Suspense fallback={<CategorySkeleton />}>
						{/* Передаем ID найденной категории во внутренний компонент */}
						<CategoryContent categoryId={targetCategoryId} />
					</Suspense>
				</ErrorBoundary>
			</div>
		</>
	)
}

export default CategoryPage
