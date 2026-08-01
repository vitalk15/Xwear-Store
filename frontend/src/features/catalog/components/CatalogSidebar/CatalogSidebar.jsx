import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import FilterSection from './FiltersSidebar/FilterSection'
import PriceFilter from './FiltersSidebar/PriceFilter'
import BrandFilter from './FiltersSidebar/BrandFilter'
import SizeFilter from './FiltersSidebar/SizeFilter'
import ColorFilter from './FiltersSidebar/ColorFilter'
import { CrossIcon } from './Icons'
import styles from './CatalogSidebar.module.scss'

const CatalogSidebar = ({ filters, categoryId }) => {
	const [searchParams, setSearchParams] = useSearchParams()

	// Проверяем, есть ли хотя бы один активный фильтр
	const hasActiveFilters = ['brands', 'colors', 'sizes', 'min_price', 'max_price'].some(
		(key) => searchParams.has(key),
	)

	// --- ЛОГИКА КЭШИРОВАНИЯ БАЗОВЫХ ФИЛЬТРОВ ---
	const [baseFilters, setBaseFilters] = useState(filters)

	// Создаем трекер, чтобы понимать, когда изменилась категория или сбросились фильтры
	const [prevTracker, setPrevTracker] = useState({ categoryId, hasActiveFilters })

	// Обновляем стейт прямо во время рендера
	if (
		prevTracker.categoryId !== categoryId || // Если сменили категорию
		(prevTracker.hasActiveFilters && !hasActiveFilters) // Если нажали "Сбросить все фильтры"
	) {
		setPrevTracker({ categoryId, hasActiveFilters })
		setBaseFilters(filters)
	} else if (prevTracker.hasActiveFilters !== hasActiveFilters) {
		// Просто синхронизируем трекер, когда пользователь начал выбирать фильтры
		setPrevTracker({ categoryId, hasActiveFilters })
	}

	// --- ХЕЛПЕРЫ ДЛЯ РАБОТЫ С URL ---

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

	// --- ПОДГОТОВКА ДАННЫХ С ФЛАГОМ DISABLED ---
	// Функция проверяет, есть ли элемент в текущем (урезанном) ответе бэкенда
	const checkIsDisabled = (filterKey, slugOrValue) => {
		if (!filters || !filters[filterKey]) return true // Если бэкенд вообще не прислал этот блок
		if (filterKey === 'sizes') {
			return !filters.sizes.includes(slugOrValue)
		}
		return !filters[filterKey].some((item) => item.slug === slugOrValue)
	}

	// Мапим базовые фильтры, добавляя каждому флаг disabled
	const brandsWithDisabled =
		baseFilters?.brands?.map((brand) => ({
			...brand,
			disabled: checkIsDisabled('brands', brand.slug),
		})) || []

	const sizesWithDisabled =
		baseFilters?.sizes?.map((size) => ({
			value: size,
			label: size,
			disabled: checkIsDisabled('sizes', size),
		})) || []

	const colorsWithDisabled =
		baseFilters?.colors?.map((color) => ({
			...color,
			disabled: checkIsDisabled('colors', color.slug),
		})) || []

	// Читаем текущие значения цен из URL

	const minBound = filters.price_range?.min ?? 0
	const maxBound = filters.price_range?.max ?? 100000

	// const minBound = baseFilters?.price_range?.min ?? 0
	// const maxBound = baseFilters?.price_range?.max ?? 100000

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

	// !!! Todo: заменить на скелетон?
	// Защита: если данные фильтров еще не загрузились
	// if (!filters) return <aside className={styles.sidebar}>Загрузка фильтров...</aside>
	if (!baseFilters) return <aside className={styles.sidebar}>Загрузка фильтров...</aside>

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
			{brandsWithDisabled.length > 0 && (
				// {filters.brands && filters.brands.length > 0 && (
				<FilterSection title="Бренды">
					<BrandFilter
						// brands={filters.brands}
						brands={brandsWithDisabled}
						selectedBrands={getActiveList('brands')}
						onToggle={(value) => toggleFilter('brands', value)}
					/>
				</FilterSection>
			)}

			{/* {filters.brands && filters.brands.length > 0 && <hr className={styles.divider} />} */}
			{brandsWithDisabled.length > 0 && <hr className={styles.divider} />}

			{/* 3. ФИЛЬТР: РАЗМЕРЫ (бэкенд отдает список строк) */}
			{sizesWithDisabled.length > 0 && (
				// {filters.sizes && filters.sizes.length > 0 && (
				<FilterSection title="Размеры (EU)">
					<SizeFilter
						// sizes={filters.sizes}
						sizes={sizesWithDisabled}
						selectedSizes={getActiveList('sizes')}
						onToggle={(value) => toggleFilter('sizes', value)}
					/>
				</FilterSection>
			)}

			{/* {filters.sizes && filters.sizes.length > 0 && <hr className={styles.divider} />} */}
			{sizesWithDisabled.length > 0 && <hr className={styles.divider} />}

			{/* 4. ФИЛЬТР: ЦВЕТА */}
			{colorsWithDisabled.length > 0 && (
				// {filters.colors && filters.colors.length > 0 && (
				<FilterSection title="Цвет">
					<ColorFilter
						// colors={filters.colors}
						colors={colorsWithDisabled}
						selectedColors={getActiveList('colors')}
						onToggle={(value) => toggleFilter('colors', value)}
					/>
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
