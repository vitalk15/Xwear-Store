import { useSearchParams } from 'react-router-dom'
import FilterSection from './FilterSection'
import PriceFilter from './PriceFilter'
import { CrossIcon } from './Icons'
import styles from './CatalogSidebar.module.scss'

const CatalogSidebar = ({ filters }) => {
	const [searchParams, setSearchParams] = useSearchParams()

	// --- Хелперы для работы с URL ---

	// Получить текущие выбранные значения в виде массива
	const getActiveList = (paramName) => {
		return searchParams.get(paramName)?.split(',') || []
	}

	// Обработчик клика по чекбоксу
	const toggleFilter = (paramName, value) => {
		const activeList = getActiveList(paramName)
		let newList

		if (activeList.includes(value)) {
			// Если уже есть - удаляем
			newList = activeList.filter((item) => item !== value)
		} else {
			// Если нет - добавляем
			newList = [...activeList, value]
		}

		const newParams = new URLSearchParams(searchParams)

		if (newList.length > 0) {
			newParams.set(paramName, newList.join(','))
		} else {
			newParams.delete(paramName) // Очищаем URL от пустого параметра
		}

		// При любом изменении фильтра всегда сбрасываем страницу на первую!
		newParams.delete('page')

		setSearchParams(newParams)
	}

	// Сброс всех фильтров
	const handleReset = () => {
		// Получаем get-параметры из url
		const newParams = new URLSearchParams(searchParams)
		// Удаляем все параметры, связанные с фильтрами
		const filterKeys = ['brands', 'colors', 'sizes', 'min_price', 'max_price']
		filterKeys.forEach((key) => newParams.delete(key))

		// Сбрасываем страницу на первую
		newParams.delete('page')
		// Устанавливаем новые get-параметры в url
		setSearchParams(newParams)
	}

	// Читаем текущие значения цен из URL
	const minBound = filters.price_range?.min ?? 0
	const maxBound = filters.price_range?.max ?? 100000

	const urlMinParam = searchParams.get('min_price')
	const urlMaxParam = searchParams.get('max_price')

	const urlMin = urlMinParam !== null ? Number(urlMinParam) : undefined
	const urlMax = urlMaxParam !== null ? Number(urlMaxParam) : undefined

	// Эта функция будет вызвана ползунком, когда пользователь отпустит мышку
	const handlePriceChange = (newMin, newMax) => {
		const newParams = new URLSearchParams(searchParams)

		// Если значение отличается от базового минимума — пишем в URL
		if (newMin !== undefined && newMin > minBound) {
			newParams.set('min_price', newMin.toString())
		} else {
			newParams.delete('min_price')
		}

		// Если значение отличается от базового максимума — пишем в URL
		if (newMax !== undefined && newMax < maxBound) {
			newParams.set('max_price', newMax.toString())
		} else {
			newParams.delete('max_price')
		}

		newParams.delete('page')
		setSearchParams(newParams, { replace: true })
	}

	// Проверяем, есть ли хотя бы один активный фильтр, чтобы показать кнопку сброса
	const hasActiveFilters = ['brands', 'colors', 'sizes', 'min_price', 'max_price'].some(
		(key) => searchParams.has(key),
	)

	// Защита: если данные фильтров еще не загрузились
	if (!filters) return <aside className={styles.sidebar}>Загрузка фильтров...</aside>

	return (
		<aside className={styles.sidebar}>
			{/* 1. ФИЛЬТР: ЦЕНА */}
			<FilterSection title="Фильтр по цене">
				<PriceFilter
					minBound={minBound}
					maxBound={maxBound}
					urlMin={urlMin}
					urlMax={urlMax}
					onChange={handlePriceChange}
				/>
			</FilterSection>

			<hr className={styles.divider} />

			{/* 2. ФИЛЬТР: БРЕНДЫ (со скроллом) */}
			{filters.brands && filters.brands.length > 0 && (
				<FilterSection title="Бренды">
					<div className={`${styles.checkboxList} ${styles.scrollable}`}>
						{filters.brands.map((brand) => (
							<label key={brand.slug} className={styles.checkboxLabel}>
								{/* Нативный чекбокс скрыт, но сохраняет доступность для клавиатуры/скринридеров */}
								<input
									type="checkbox"
									className={styles.hiddenCheckbox}
									checked={getActiveList('brands').includes(brand.slug)}
									onChange={() => toggleFilter('brands', brand.slug)}
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
						))}
					</div>
				</FilterSection>
			)}

			{filters.brands && filters.brands.length > 0 && <hr className={styles.divider} />}

			{/* 3. ФИЛЬТР: РАЗМЕРЫ (бэкенд отдает список строк) */}
			{filters.sizes && filters.sizes.length > 0 && (
				<FilterSection title="Размеры (EU)">
					<div className={styles.sizeGrid}>
						{filters.sizes.map((size) => (
							<label key={size} className={styles.sizeTile}>
								<input
									type="checkbox"
									className={styles.hiddenCheckbox}
									checked={getActiveList('sizes').includes(size)}
									onChange={() => toggleFilter('sizes', size)}
								/>
								<span className={styles.sizeButton}>{size}</span>
							</label>
						))}
					</div>
				</FilterSection>
			)}

			{filters.sizes && filters.sizes.length > 0 && <hr className={styles.divider} />}

			{/* 4. ФИЛЬТР: ЦВЕТА */}
			{filters.colors && filters.colors.length > 0 && (
				<FilterSection title="Цвет">
					<div className={styles.colorGrid}>
						{filters.colors.map((color) => {
							const isActive = getActiveList('colors').includes(color.slug)

							// Логика формирования фона (один цвет или градиент из двух)
							const bgStyle = color.hex_code_2
								? `linear-gradient(135deg, ${color.hex_code} 50%, ${color.hex_code_2} 50%)`
								: color.hex_code || '#ffffff'

							return (
								<button
									key={color.slug}
									type="button"
									className={`${styles.colorItem} ${isActive ? styles.active : ''}`}
									onClick={() => toggleFilter('colors', color.slug)}
									title={color.name} // Нативный тултип браузера при наведении
								>
									<span className={styles.colorCircle} style={{ background: bgStyle }} />
									{/* <span className={styles.colorName}>{color.name}</span> */}
								</button>
							)
						})}
					</div>
				</FilterSection>
			)}

			{hasActiveFilters && <hr className={styles.divider} />}

			{/* КНОПКА СБРОСА */}
			{hasActiveFilters && (
				<button className={styles.resetButton} onClick={handleReset}>
					<CrossIcon />
					Сбросить все фильтры
				</button>
			)}
		</aside>
	)
}

export default CatalogSidebar
