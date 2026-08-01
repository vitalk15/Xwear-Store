import styles from '../CatalogSidebar.module.scss'

const SizeFilter = ({ sizes, selectedSizes, onToggle }) => {
	if (!sizes || sizes.length === 0) return null

	return (
		<div className={styles.sizeGrid}>
			{sizes.map((sizeObj) => {
				// Достаем значения из объекта
				const value = typeof sizeObj === 'object' ? sizeObj.value : sizeObj
				const label = typeof sizeObj === 'object' ? sizeObj.label : sizeObj
				const isDisabled = typeof sizeObj === 'object' ? sizeObj.disabled : false

				const sizeStr = String(value)
				const isChecked = selectedSizes.includes(sizeStr)

				return (
					<label
						key={sizeStr}
						className={`${styles.sizeTile} ${isDisabled ? styles.disabled : ''}`}
					>
						{/* Нативный чекбокс скрыт, но сохраняет доступность для клавиатуры/скринридеров */}
						<input
							type="checkbox"
							className={styles.hiddenCheckbox}
							checked={isChecked}
							disabled={isDisabled}
							onChange={() => !isDisabled && onToggle(sizeStr)}
						/>
						{/* Кастомный чекбокс в виде кнопки */}
						<span className={styles.sizeButton}>{label}</span>
					</label>
				)
			})}
		</div>
	)
}

export default SizeFilter
