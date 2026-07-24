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
				{/* Простая стрелочка, которая будет крутиться через CSS */}
				<span className={`${styles.arrow} ${isOpen ? styles.open : ''}`}>►</span>
			</button>

			{isOpen && <div className={styles.sectionContent}>{children}</div>}
		</div>
	)
}

export default FilterSection
