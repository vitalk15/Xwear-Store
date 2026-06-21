import styles from './Slide.module.scss'

const Slide = ({ slide }) => {
	// Распаковываем данные из JSON
	const {
		title,
		links = [],
		grid_layout,
		content_width,
		text_color,
		font_size_title,
		font_size_link,
		thumbnails,
	} = slide

	// Если thumbnails.large.url существует — берем его.
	// Если нет (ошибка бэкенда/пустой слайд) — можно подставить заглушку
	const imageUrl = thumbnails?.large?.url || '/images/placeholder-banner.webp'

	return (
		<div
			className={styles.slideWrapper}
			style={{ backgroundImage: `url(${imageUrl})`, color: text_color }}
		>
			{/* Обертка, которая отвечает за позиционирование (center_left, bottom_center и т.д.) 
        Берем класс динамически из grid_layout
      */}
			<div className={`container ${styles.gridContainer} ${styles[grid_layout] || ''}`}>
				{/* Сам контент, ширину которого мы регулируем через CSS-переменную */}
				<div
					className={styles.contentBlock}
					style={{ '--content-width': `${content_width}%` }}
				>
					{/* ЗАГОЛОВОК */}
					{/* !!! Нужен ли здесь text_color? */}
					{title && (
						<h2
							className={`${styles.title} ${styles[`text_${text_color}`]}`}
							style={{ fontSize: font_size_title }}
						>
							{title}
						</h2>
					)}
					{/* ССЫЛКИ / КНОПКИ */}
					{links.length > 0 && (
						<div className={styles.linksGroup}>
							{links.map((link, idx) => (
								<a
									key={idx}
									href={link.url}
									className={`${styles.linkItem} ${styles[`btn_${link.style}`]}`}
									style={{ fontSize: font_size_link }}
								>
									{link.title}
								</a>
							))}
						</div>
					)}
				</div>
			</div>
		</div>
	)
}

export default Slide
