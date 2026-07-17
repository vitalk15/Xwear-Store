import styles from './Pagination.module.scss'

// Временный простой компонент (позже научим его менять URL-параметры)
const Pagination = ({ currentPage, totalPages, onPageChange }) => {
	if (totalPages <= 1) return null

	// Генерируем массив страниц (пока простая версия без троеточий для старта)
	const pages = Array.from({ length: totalPages }, (_, i) => i + 1)

	return (
		<div className={styles.pagination}>
			<button
				className={styles.arrowBtn}
				disabled={currentPage === 1}
				onClick={() => onPageChange(currentPage - 1)}
			>
				&larr;
			</button>

			<div className={styles.pages}>
				{pages.map((page) => (
					<button
						key={page}
						className={`${styles.pageBtn} ${currentPage === page ? styles.active : ''}`}
						onClick={() => onPageChange(page)}
					>
						{page}
					</button>
				))}
			</div>

			<button
				className={styles.arrowBtn}
				disabled={currentPage === totalPages}
				onClick={() => onPageChange(currentPage + 1)}
			>
				&rarr;
			</button>
		</div>
	)
}

export default Pagination
