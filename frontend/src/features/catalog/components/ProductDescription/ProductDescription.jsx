import { useMemo } from 'react'
import styles from './ProductDescription.module.scss'

/**
 * 1. Функция парсинга Delta ops (из данных Django-библиотеки django_quill) в массив базовых блоков
 */
const parseDeltaToBlocks = (ops) => {
	const blocks = []
	let currentInlines = []

	ops.forEach((op) => {
		if (typeof op.insert !== 'string') return

		const lines = op.insert.split('\n')

		lines.forEach((line, i) => {
			const isLast = i === lines.length - 1

			if (line.length > 0) {
				currentInlines.push({
					text: line,
					attributes: op.attributes || {},
				})
			}

			if (!isLast) {
				// Quill указывает атрибуты блока (например, header) на символе переноса строки (\n)
				const blockAttr =
					op.attributes && (op.attributes.header || op.attributes.list)
						? op.attributes
						: {}

				blocks.push({
					id: Math.random().toString(36).substring(2, 10), // Уникальный ключ
					inlines: currentInlines,
					attributes: blockAttr,
				})
				currentInlines = []
			}
		})
	})

	// Пушим остатки, если нет финального переноса строки
	if (currentInlines.length > 0) {
		blocks.push({
			id: Math.random().toString(36).substring(2, 10),
			inlines: currentInlines,
			attributes: {},
		})
	}

	return blocks
}

/**
 * 2. Функция группировки Заголовок + Текст в единую секцию с шахматным порядком
 */
const groupBlocksIntoSections = (blocks) => {
	const sections = []
	let currentSection = { id: 'sec_start', title: null, content: [] }

	blocks.forEach((block) => {
		// Если находим заголовок (header: 3)
		if (block.attributes.header) {
			// Сохраняем предыдущую секцию, если в ней что-то есть
			if (currentSection.title || currentSection.content.length > 0) {
				sections.push(currentSection)
			}
			// Начинаем новую секцию с заголовком
			currentSection = { id: block.id, title: block, content: [] }
		} else {
			currentSection.content.push(block)
		}
	})

	if (currentSection.title || currentSection.content.length > 0) {
		sections.push(currentSection)
	}
	return sections
}

const ProductDescription = ({ description }) => {
	// Парсим данные только если они изменились
	const sections = useMemo(() => {
		if (!description || !description.ops) return []
		const parsedBlocks = parseDeltaToBlocks(description.ops)
		return groupBlocksIntoSections(parsedBlocks)
	}, [description])

	// Если описания нет — ничего не рендерим
	if (sections.length === 0) return null

	// Разделяем логику: Общее описание (без заголовка) и Преимущества (с заголовками)
	const introSection = sections.find((sec) => !sec.title)
	const advantageSections = sections.filter((sec) => sec.title)

	// Рендер текста с инлайн-стилями (bold, color)
	const renderInlines = (inlines) => {
		return inlines.map((inline, idx) => {
			const { attributes, text } = inline
			const Tag = attributes.bold ? 'strong' : 'span'

			return (
				<Tag
					key={idx}
					style={{ color: attributes.color || 'inherit' }} // Применяем цвет из JSON
				>
					{text}
				</Tag>
			)
		})
	}

	return (
		<section className={styles.descWrapper}>
			<h2 className={styles.mainTitle}>Описание</h2>

			<div className={styles.checkerboard}>
				{/* Рендерим вводное описание (если оно есть) отдельным блоком */}
				{introSection && introSection.content.length > 0 && (
					<div className={styles.introBlock}>
						{introSection.content.map((block) => (
							<p key={block.id} className={styles.introParagraph}>
								{renderInlines(block.inlines)}
							</p>
						))}
					</div>
				)}

				{/* Рендерим преимущества в шахматном порядке */}
				{advantageSections.length > 0 &&
					advantageSections.map((section, index) => {
						// Шахматный порядок: четные слева, нечетные справа
						const isEven = index % 2 === 0
						const alignmentClass = isEven ? styles.alignLeft : styles.alignRight

						return (
							<div key={section.id} className={`${styles.sectionCard} ${alignmentClass}`}>
								{/* Рендерим заголовок секции, если он есть */}
								{section.title && (
									<h3 className={styles.sectionTitle}>
										{renderInlines(section.title.inlines)}
									</h3>
								)}

								{/* Рендерим абзацы */}
								{section.content.map((block) => (
									<p key={block.id} className={styles.sectionParagraph}>
										{renderInlines(block.inlines)}
									</p>
								))}
							</div>
						)
					})}
			</div>
		</section>
	)
}

export default ProductDescription
