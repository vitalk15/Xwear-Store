import { useState } from 'react'
import styles from '../CatalogSidebar.module.scss'

const PriceFilter = ({ minBound = 0, maxBound = 100000, urlMin, urlMax, onChange }) => {
	// 1. Если в URL нет значений, инициализируем пустой строкой '',
	// чтобы показывался placeholder, а не конкретное число
	const [localMin, setLocalMin] = useState(urlMin ?? '')
	const [localMax, setLocalMax] = useState(urlMax ?? '')

	// 2. Отслеживаем ВСЕ пропсы, влияющие на границы и URL
	const [prevProps, setPrevProps] = useState({ minBound, maxBound, urlMin, urlMax })

	// Реакция на изменение категории (новые minBound/maxBound) или сброс/изменение URL
	if (
		prevProps.minBound !== minBound ||
		prevProps.maxBound !== maxBound ||
		prevProps.urlMin !== urlMin ||
		prevProps.urlMax !== urlMax
	) {
		setPrevProps({ minBound, maxBound, urlMin, urlMax })
		setLocalMin(urlMin ?? '')
		setLocalMax(urlMax ?? '')
	}

	// 3. ВЫЧИСЛЕНИЕ «БЕЗОПАСНЫХ» ЗНАЧЕНИЙ ДЛЯ ПОЛЗУНКА (CLAMP)
	// Гарантирует, что полоса НЕ выйдет за пределы [minBound, maxBound]
	const parsedMin =
		localMin === '' || isNaN(Number(localMin)) ? minBound : Number(localMin)
	const parsedMax =
		localMax === '' || isNaN(Number(localMax)) ? maxBound : Number(localMax)

	// Ограничиваем рамками минимальной и максимальной цены
	const safeMin = Math.min(Math.max(parsedMin, minBound), maxBound)
	const safeMax = Math.min(Math.max(parsedMax, minBound), maxBound)

	// Гарантируем, что safeMin не станет больше safeMax для ползунка
	const displayMin = Math.min(safeMin, safeMax)
	const displayMax = Math.max(safeMin, safeMax)

	// Рассчитываем проценты для CSS трека
	const range = maxBound - minBound || 1
	const leftPercent = ((displayMin - minBound) / range) * 100
	const rightPercent = 100 - ((displayMax - minBound) / range) * 100

	// 4. Обработчики потери фокуса (onBlur)
	// Автоматически исправляют некорректные или пустые значения, когда пользователь уводит курсор
	const handleMinBlur = () => {
		if (localMin === '') {
			if (onChange) onChange(undefined, localMax === '' ? undefined : safeMax)
			return
		}
		let val = Number(localMin)
		if (isNaN(val) || val < minBound) val = minBound
		else if (val > safeMax) val = safeMax

		setLocalMin(val)
		if (onChange) onChange(val, localMax === '' ? undefined : safeMax)

		// let val = Number(localMin)
		// if (localMin === '' || isNaN(val) || val < minBound) {
		// 	val = minBound
		// } else if (val > safeMax) {
		// 	val = safeMax
		// }
		// setLocalMin(val)
		// if (onChange) onChange(val, safeMax)
	}

	const handleMaxBlur = () => {
		if (localMax === '') {
			if (onChange) onChange(localMin === '' ? undefined : safeMin, undefined)
			return
		}
		let val = Number(localMax)
		if (isNaN(val) || val > maxBound) val = maxBound
		else if (val < safeMin) val = safeMin

		setLocalMax(val)
		if (onChange) onChange(localMin === '' ? undefined : safeMin, val)

		// let val = Number(localMax)
		// if (localMax === '' || isNaN(val) || val > maxBound) {
		// 	val = maxBound
		// } else if (val < safeMin) {
		// 	val = safeMin
		// }
		// setLocalMax(val)
		// if (onChange) onChange(safeMin, val)
	}

	// 5. Обработчик отпускания ползунка (mouse / touch)
	const handleMouseUp = () => {
		if (onChange) {
			const finalMin = displayMin <= minBound ? undefined : displayMin
			const finalMax = displayMax >= maxBound ? undefined : displayMax
			onChange(finalMin, finalMax)
		}

		// if (onChange) onChange(displayMin, displayMax)
	}

	return (
		<div className={styles.priceFilterWrapper}>
			{/* Поля ввода */}
			<div className={styles.priceInputs}>
				<input
					type="number"
					value={localMin}
					onChange={(e) => setLocalMin(e.target.value)}
					onBlur={handleMinBlur}
					placeholder={`от ${minBound}`}
					className={styles.input}
				/>
				<span className={styles.priceDivider}>-</span>
				<input
					type="number"
					value={localMax}
					onChange={(e) => setLocalMax(e.target.value)}
					onBlur={handleMaxBlur}
					placeholder={`до ${maxBound}`}
					className={styles.input}
				/>
			</div>

			{/* Трек и двойной ползунок */}
			<div className={styles.sliderContainer}>
				{/* Серая полоса-фон */}
				<div className={styles.sliderTrack} />

				{/* Активная подсвеченная полоса между ползунками */}
				<div
					className={styles.sliderRange}
					style={{
						left: `${leftPercent}%`,
						right: `${rightPercent}%`,
					}}
				/>

				{/* Левый ползунок */}
				<input
					type="range"
					min={minBound}
					max={maxBound}
					value={displayMin}
					onChange={(e) => {
						const val = Number(e.target.value)
						if (val <= displayMax) {
							setLocalMin(val)
						}
					}}
					onMouseUp={handleMouseUp}
					onTouchEnd={handleMouseUp}
					className={styles.thumb}
				/>
				{/* Правый ползунок */}
				<input
					type="range"
					min={minBound}
					max={maxBound}
					value={displayMax}
					onChange={(e) => {
						const val = Number(e.target.value)
						if (val >= displayMin) {
							setLocalMax(val)
						}
					}}
					onMouseUp={handleMouseUp}
					onTouchEnd={handleMouseUp}
					className={styles.thumb}
				/>
			</div>
		</div>
	)
}

export default PriceFilter
