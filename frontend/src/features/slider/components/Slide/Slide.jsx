import placeholderBanner from '@/assets/images/placeholder-banner.webp'
import styles from './Slide.module.scss'

const Slide = ({ slide }) => {
	// Распаковываем данные из JSON
	const {
		title,
		links = [],
		grid_layout = 'center_left',
		content_width = 50,
		text_color = 'dark',
		font_size_title = '4.5cqw',
		font_size_link = '1.5cqw',
		thumbnails,
	} = slide

	const imgData = thumbnails?.large

	// Если thumbnails.large.url существует — берем его.
	// Если нет (ошибка бэкенда/пустой слайд) — подставляем заглушку
	const imageUrl = imgData?.url || placeholderBanner

	// Если бэкенд прислал размеры, вычисляем пропорцию (например, 1540 / 630)
	const aspectRatio = imgData ? `${imgData.width} / ${imgData.height}` : '1540 / 630'

	return (
		<div
			className={styles.slideWrapper}
			style={{
				backgroundImage: `url(${imageUrl})`,
				aspectRatio: aspectRatio,
			}}
		>
			{/* Слой сетки (9 зон).
        Класс из grid_layout (например, styles.center_left) сам выставит 
        justify-content, align-items и CSS-переменные для выравнивания кнопок
      */}
			<div className={`container ${styles.gridContainer} ${styles[grid_layout]}`}>
				{/* Блок контента: задаем ширину из админки и цветовую тему
				 */}
				<div
					className={`${styles.contentBlock} ${styles[`theme_${text_color}`]}`}
					style={{ '--content-width': `${content_width}%` }}
				>
					{/* ЗАГОЛОВОК */}
					{title && (
						<h2 className={styles.title} style={{ fontSize: font_size_title }}>
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
									className={`${styles.linkItem} ${styles[`btn_${link.style || 'primary'}`]}`}
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
