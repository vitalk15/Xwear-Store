import styles from '../CatalogSidebar.module.scss'

const BrandFilter = ({ brands, selectedBrands, onToggle }) => {
	if (!brands || brands.length === 0) return null

	return (
		<div className={`${styles.checkboxList} ${styles.scrollable}`}>
			{brands.map((brand) => {
				const isDisabled = brand.disabled

				return (
					<label
						key={brand.slug}
						className={`${styles.checkboxLabel} ${isDisabled ? styles.disabled : ''}`}
					>
						{/* Нативный чекбокс скрыт, но сохраняет доступность для клавиатуры/скринридеров */}
						<input
							type="checkbox"
							className={styles.hiddenCheckbox}
							checked={selectedBrands.includes(brand.slug)}
							disabled={isDisabled}
							onChange={() => !isDisabled && onToggle(brand.slug)}
						/>
						{/* Кастомный квадрат чекбокса с иконкой галочки */}
						<span className={styles.customCheckbox}>
							<svg
								className={styles.checkmark}
								viewBox="0 0 12 10"
								fill="none"
								xmlns="http://www.w3.org/2000/svg"
							>
								<path
									d="M1.5 5L4.5 8L10.5 1.5"
									stroke="currentColor"
									strokeWidth="2"
									strokeLinecap="round"
									strokeLinejoin="round"
								/>
							</svg>
						</span>
						<span className={styles.brandName}>{brand.name}</span>
					</label>
				)
			})}
		</div>
	)
}

export default BrandFilter
