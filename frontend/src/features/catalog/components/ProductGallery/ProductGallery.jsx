import { useState, useEffect } from 'react'
import { Swiper, SwiperSlide } from 'swiper/react'
import { Thumbs, FreeMode, Navigation, EffectFade } from 'swiper/modules'
import StarIcon from '@/shared/icons/star.svg'
import placeholderProduct from '@/assets/images/placeholder-product.webp'

// Импорт базовых стилей Swiper
import 'swiper/css'
import 'swiper/css/free-mode'
import 'swiper/css/thumbs'
import 'swiper/css/navigation'

import styles from './ProductGallery.module.scss'

/**
 * Галерея изображений товара со слайдером, миниатюрами и модальным окном
 * @param {Array} images - Массив объектов изображений из product.images
 */
const ProductGallery = ({ images = [] }) => {
	// Состояние для связки основного слайдера и слайдера миниатюр
	const [thumbsSwiper, setThumbsSwiper] = useState(null)

	// Состояние для показа полноразмерного фото (Modal / Lightbox)
	const [activeOriginalImage, setActiveOriginalImage] = useState(null)

	// Блокировка прокрутки страницы при открытом модальном окне
	useEffect(() => {
		if (activeOriginalImage) {
			// Скрываем скроллбар и запрещаем прокрутку
			document.body.style.overflow = 'hidden'
		} else {
			// Возвращаем всё как было
			document.body.style.overflow = ''
		}

		// Функция очистки на случай, если компонент будет размонтирован
		// до того, как пользователь закроет модалку
		return () => {
			document.body.style.overflow = ''
		}
	}, [activeOriginalImage])

	// Обработка клика на звёздочку
	const handleFavoriteClick = (e) => {
		e.stopPropagation() // Чтобы не срабатывал клик по открытию картинки
		// !!! TODO: Добавить/удалить из избранного (Zustand/API)
		console.log('Избранное переключено')
	}

	// Если изображения товара будут отсутствовать
	if (!images || images.length === 0) {
		return (
			<div className={styles.galleryContainer}>
				<div className={styles.mainWrapper}>
					<div className={styles.mainImageWrapper}>
						<img
							src={placeholderProduct}
							alt="Изображение временно отсутствует"
							className={styles.mainImage}
						/>
					</div>
					{/* Оставляем иконку избранного даже без фото */}
					<button
						type="button"
						className={styles.favoriteBtn}
						onClick={handleFavoriteClick}
						aria-label="Добавить в избранное"
					>
						<StarIcon className={styles.starIcon} />
					</button>
				</div>
			</div>
		)
	}

	return (
		<div className={styles.galleryContainer}>
			{/* 1. ОСНОВНОЙ СЛАЙДЕР (Большие фото) */}
			<div className={styles.mainWrapper}>
				<Swiper
					spaceBetween={10}
					thumbs={{
						swiper: thumbsSwiper && !thumbsSwiper.destroyed ? thumbsSwiper : null,
					}}
					modules={[FreeMode, Thumbs, EffectFade]}
					effect="fade" // Плавное растворение вместо свайпа
					fadeEffect={{ crossFade: true }}
					speed={300}
					className={styles.mainSwiper}
				>
					{images.map((img) => (
						<SwiperSlide key={img.id}>
							<div
								className={styles.mainImageWrapper}
								onClick={() => setActiveOriginalImage(img.thumbnails.original)}
								title="Нажмите, чтобы увеличить"
							>
								<img
									src={img.thumbnails.large.url}
									alt={img.alt || 'Фото товара'}
									className={styles.mainImage}
								/>
							</div>
						</SwiperSlide>
					))}
				</Swiper>

				{/* Иконка «Избранное» в правом верхнем углу */}
				<button
					type="button"
					className={styles.favoriteBtn}
					onClick={handleFavoriteClick}
					aria-label="Добавить в избранное"
				>
					<StarIcon className={styles.starIcon} />
				</button>
			</div>

			{/* 2. СЛАЙДЕР МИНИАТЮР (Маленькие фото) */}
			{images.length > 1 && (
				<Swiper
					onSwiper={setThumbsSwiper}
					spaceBetween={0}
					slidesPerView={4}
					freeMode={true}
					watchSlidesProgress={true}
					modules={[FreeMode, Thumbs, Navigation]}
					className={styles.thumbsSwiper}
				>
					{images.map((img) => (
						<SwiperSlide key={img.id} className={styles.thumbSlide}>
							<div className={styles.thumbImageWrapper}>
								<img
									src={img.thumbnails.small.url}
									alt={img.alt || 'Миниатюра товара'}
									className={styles.thumbImage}
								/>
							</div>
						</SwiperSlide>
					))}
				</Swiper>
			)}

			{/* 3. МОДАЛЬНОЕ ОКНО ДЛЯ ПРОСМОТРА ОРИГИНАЛА ("original") */}
			{activeOriginalImage && (
				<div className={styles.modalOverlay} onClick={() => setActiveOriginalImage(null)}>
					<div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
						<button
							type="button"
							className={styles.closeBtn}
							onClick={() => setActiveOriginalImage(null)}
							aria-label="Закрыть"
						>
							✕
						</button>
						<img
							src={activeOriginalImage}
							alt="Оригинальное изображение товара"
							className={styles.originalImage}
						/>
					</div>
				</div>
			)}
		</div>
	)
}

export default ProductGallery
