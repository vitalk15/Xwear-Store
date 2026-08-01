import styles from '../CatalogSidebar.module.scss'

const ColorFilter = ({ colors, selectedColors, onToggle }) => {
	if (!colors || colors.length === 0) return null

	return (
		<div className={styles.colorGrid}>
			{colors.map((color) => {
				const isActive = selectedColors.includes(color.slug)
				const isDisabled = color.disabled

				// Логика формирования фона (один цвет или градиент из двух)
				const bgStyle = color.hex_code_2
					? `linear-gradient(135deg, ${color.hex_code} 50%, ${color.hex_code_2} 50%)`
					: color.hex_code || '#ffffff'

				return (
					<button
						key={color.slug}
						type="button"
						className={`${styles.colorItem} ${isActive ? styles.active : ''} ${isDisabled ? styles.disabled : ''}`}
						onClick={() => !isDisabled && onToggle(color.slug)}
						title={color.name} // Нативный тултип браузера при наведении
						disabled={isDisabled}
					>
						<span className={styles.colorCircle} style={{ background: bgStyle }} />
						<span className={styles.colorName}>{color.name}</span>
					</button>
				)
			})}
		</div>
	)
}

export default ColorFilter
