import { useState } from 'react'
import styles from './CatalogSidebar.module.scss'

const FilterSection = ({ title, children, defaultOpen = true }) => {
	const [isOpen, setIsOpen] = useState(defaultOpen)

	const titleFilter =
		title === 'Фильтр по цене' ? (
			<>
				{title}, <i className="nbrb-icon">BYN</i>
			</>
		) : (
			title
		)

	return (
		<div className={styles.filterSection}>
			<button
				className={styles.sectionHeader}
				onClick={() => setIsOpen(!isOpen)}
				type="button"
			>
				<span className={styles.sectionTitle}>{titleFilter}</span>
				{/* стрелочка, которая будет крутиться через CSS */}
				<svg
					className={`${styles.arrow} ${isOpen ? styles.open : ''}`}
					width="12"
					height="8"
					viewBox="0 0 12 8"
					fill="none"
				>
					<path
						d="M1 1.5L6 6.5L11 1.5"
						stroke="currentColor"
						strokeWidth="1.5"
						strokeLinecap="round"
						strokeLinejoin="round"
					/>
				</svg>
			</button>

			{isOpen && <div className={styles.sectionContent}>{children}</div>}
		</div>
	)
}

export default FilterSection
