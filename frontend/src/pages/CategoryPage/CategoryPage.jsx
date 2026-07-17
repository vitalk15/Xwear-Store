import { useParams } from 'react-router-dom'
import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { useCategoryByPath } from '@/entities/category/hooks/useCategoryByPath'
import CategoryContent from './CategoryContent'
import PageTitle from '@/components/common/PageTitle'
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
				<ErrorBoundary fallback={<div>Ошибка загрузки товаров категории</div>}>
					<Suspense fallback={<div>Загрузка товаров...</div>}>
						{/* Передаем ID найденной категории во внутренний компонент */}
						<CategoryContent categoryId={category.id} />
					</Suspense>
				</ErrorBoundary>
			</div>
		</>
	)
}

export default CategoryPage
