import { useMemo } from 'react'
import styles from './ProductCharacteristics.module.scss'

const ProductCharacteristics = ({ product }) => {
	// Формируем массивы характеристик, отфильтровывая те, которых нет в данных товара
	const generalSpecs = useMemo(() => {
		return [
			{ label: 'Пол', value: product?.gender_display },
			{ label: 'Цвет', value: product?.color?.name },
			{ label: 'Сезон', value: product?.season_display },
		].filter((spec) => spec.value) // Убираем пустые
	}, [product])

	const compositionSpecs = useMemo(() => {
		return [
			{ label: 'Материал верха', value: product?.composition?.material_outer?.name },
			{ label: 'Материал подкладки', value: product?.composition?.material_inner?.name },
			{ label: 'Материал подошвы', value: product?.composition?.material_sole?.name },
		].filter((spec) => spec.value) // Убираем пустые
	}, [product])

	// Если нет вообще никаких характеристик, не рендерим блок
	if (generalSpecs.length === 0 && compositionSpecs.length === 0) {
		return null
	}

	// Вспомогательная функция для рендера списка, чтобы не дублировать код
	const renderSpecList = (specs) => (
		<ul className={styles.specList}>
			{specs.map((spec, index) => (
				<li key={index} className={styles.specRow}>
					<span className={styles.specLabel}>{spec.label}</span>
					<span className={styles.dots}></span>
					<span className={styles.specValue}>{spec.value}</span>
				</li>
			))}
		</ul>
	)

	return (
		<section className={styles.characterWrapper}>
			<h2 className={styles.mainTitle}>Характеристики</h2>

			<div className={styles.blocksContainer}>
				{/* Блок общих характеристик */}
				{generalSpecs.length > 0 && (
					<div className={styles.specBlock}>
						<h3 className={styles.blockTitle}>Общая характеристика</h3>
						{renderSpecList(generalSpecs)}
					</div>
				)}

				{/* Блок состава */}
				{compositionSpecs.length > 0 && (
					<div className={styles.specBlock}>
						<h3 className={styles.blockTitle}>Состав</h3>
						{renderSpecList(compositionSpecs)}
					</div>
				)}
			</div>
		</section>
	)
}

export default ProductCharacteristics
