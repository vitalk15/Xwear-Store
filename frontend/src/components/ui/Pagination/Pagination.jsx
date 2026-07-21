import { useSearchParams } from 'react-router-dom'
import styles from './Pagination.module.scss'

const Pagination = ({ totalPages }) => {
	const [searchParams, setSearchParams] = useSearchParams()

	// Читаем текущую страницу из URL (например, ?page=2). Если параметра нет — по умолчанию 1.
	const currentPage = parseInt(searchParams.get('page') || '1', 10)

	if (totalPages <= 1) return null

	// Функция для смены страницы через URL
	const handlePageChange = (pageNumber) => {
		const newParams = new URLSearchParams(searchParams)
		if (pageNumber === 1) {
			newParams.delete('page') // Красивый URL: для первой страницы убираем ?page=1
		} else {
			newParams.set('page', pageNumber.toString())
		}
		setSearchParams(newParams)
	}

	// Функция генерации массива страниц с троеточиями (профессиональный подход)
	const getVisiblePages = () => {
		const pages = []
		const range = 1 // Сколько страниц показывать слева и справа от текущей (например, при текущей 5 покажет 4 и 6)

		for (let i = 1; i <= totalPages; i++) {
			if (
				i === 1 || // Всегда показываем первую
				i === totalPages || // Всегда показываем последнюю
				(i >= currentPage - range && i <= currentPage + range) // Страницы вокруг текущей
			) {
				pages.push(i)
			} else if (pages[pages.length - 1] !== '...') {
				pages.push('...')
			}
		}
		return pages
	}

	const visiblePages = getVisiblePages()

	return (
		<div className={styles.pagination}>
			{/* Стрелка Назад */}
			<button
				className={styles.arrowBtn}
				disabled={currentPage === 1}
				onClick={() => handlePageChange(currentPage - 1)}
			>
				&larr;
			</button>

			{/* Список страниц */}
			<div className={styles.pages}>
				{visiblePages.map((page, index) => {
					if (page === '...') {
						return (
							<span key={`dots-${index}`} className={styles.dots}>
								...
							</span>
						)
					}

					return (
						<button
							key={page}
							className={`${styles.pageBtn} ${currentPage === page ? styles.active : ''}`}
							onClick={() => handlePageChange(page)}
						>
							{page}
						</button>
					)
				})}
			</div>

			{/* Стрелка Вперед */}
			<button
				className={styles.arrowBtn}
				disabled={currentPage === totalPages}
				onClick={() => handlePageChange(currentPage + 1)}
			>
				&rarr;
			</button>
		</div>
	)
}

export default Pagination
