import { useSearchParams } from 'react-router-dom'
import { useFavorites } from '@/features/favorites/hooks/useFavorites'
import { getDeclension } from '@/shared/utils/declensionWords'
import FavoriteGrid from '@/features/favorites/components/FavoriteGrid'
import { FAVORITES_ITEMS_PER_PAGE } from '@/shared/constants/pagination'
import Breadcrumbs from '@/components/common/Breadcrumbs'
import Pagination from '@/components/ui/Pagination'
import EmptyFavorites from './EmptyFavorites'
import styles from './FavoritesPage.module.scss'

const FavoritesContent = () => {
	const { data: favorites } = useFavorites()
	const [searchParams] = useSearchParams() // Получаем параметры из URL для пагинации

	// 1. Вычисляем общее количество товаров
	const count = favorites?.length || 0
	// Применяем утилиту для правильного склонения
	const productWord = getDeclension(count, ['товар', 'товара', 'товаров'])

	// 2. Клиентская пагинация
	// Достаем страницу из URL
	const currentPage = parseInt(searchParams.get('page') || '1', 10)
	// Вычисляем общее количество страниц
	const totalPages = Math.ceil(count / FAVORITES_ITEMS_PER_PAGE)

	// Вычисляем индексы для обрезки массива (например, с 0 по 16 для первой страницы)
	const startIndex = (currentPage - 1) * FAVORITES_ITEMS_PER_PAGE
	const endIndex = startIndex + FAVORITES_ITEMS_PER_PAGE
	// Отрезаем нужные карточки для текущей страницы
	const paginatedFavorites = favorites?.slice(startIndex, endIndex) || []

	return (
		<>
			<Breadcrumbs items={[{ name: 'Избранные товары' }]} />

			<div className={styles.header}>
				<h1 className={styles.title}>ИЗБРАННЫЕ ТОВАРЫ</h1>
				<span className={styles.count}>
					{count > 0 && (
						<span className={styles.count}>
							{count} {productWord}
						</span>
					)}
				</span>
			</div>
			{count > 0 ? (
				<>
					<FavoriteGrid items={paginatedFavorites} />
					{totalPages > 1 && <Pagination totalPages={totalPages} />}
				</>
			) : (
				<EmptyFavorites />
			)}
		</>
	)
}

export default FavoritesContent
