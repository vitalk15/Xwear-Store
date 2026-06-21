import { Swiper, SwiperSlide } from 'swiper/react'
import { Navigation, Pagination, Autoplay, EffectFade } from 'swiper/modules'
import { useSliderQuery } from '@/features/slider/hooks/useSliderQuery'
import Slide from '../Slide'
// Импорт стилей Swiper. Обязательно в таком порядке!
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/effect-fade'

import styles from './SliderWidget.module.scss'

const SliderWidget = () => {
	// Хук вызовет Suspense (покажет скелетон) сам, если данных еще нет
	const { data: slides = [] } = useSliderQuery()

	// Если бэкенд не вернул ни одного слайда (пустой массив)
	if (slides.length === 0) {
		return null // или можно вернуть резервный баннер по умолчанию
	}

	// Если изображение только одно, показываем просто как баннер
	if (slides.length === 1) {
		return (
			<section className={styles.sectionWrapper}>
				<Slide slide={slides[0]} />
			</section>
		)
	}

	// Если слайдов больше одного — инициализируем Swiper
	return (
		<section className={styles.sectionWrapper}>
			{/* Обертка для стилизации кастомных кнопок навигации */}
			<div className={styles.swiperWrapper}>
				<Swiper
					modules={[Navigation, Pagination, Autoplay, EffectFade]}
					effect="fade" // Плавное растворение вместо свайпа (лучше для hero-баннеров)
					fadeEffect={{ crossFade: true }}
					speed={1000} // Скорость анимации смены слайда
					slidesPerView={1}
					loop={true} // Бесконечная прокрутка
					autoplay={{
						delay: 6000, // Переключение каждые 6 секунд
						disableOnInteraction: false, // Продолжать автоплей после ручного свайпа
					}}
					pagination={{
						clickable: true,
						bulletClass: styles.customBullet, // Наши стильные точки
						bulletActiveClass: styles.customBulletActive,
					}}
					navigation={{
						prevEl: `.${styles.customPrev}`, // Наши стильные стрелки
						nextEl: `.${styles.customNext}`,
					}}
					className={styles.swiperContainer}
				>
					{slides.map((slide) => (
						<SwiperSlide key={slide.id}>
							<Slide slide={slide} />
						</SwiperSlide>
					))}
				</Swiper>

				{/* Кастомная навигация (вынесена за пределы SwiperContainer для свободного позиционирования) */}
				<button
					className={`${styles.navBtn} ${styles.customPrev}`}
					aria-label="Предыдущий слайд"
				>
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							strokeWidth={2}
							d="M15 19l-7-7 7-7"
						/>
					</svg>
				</button>
				<button
					className={`${styles.navBtn} ${styles.customNext}`}
					aria-label="Следующий слайд"
				>
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
						<path
							strokeLinecap="round"
							strokeLinejoin="round"
							strokeWidth={2}
							d="M9 5l7 7-7 7"
						/>
					</svg>
				</button>
			</div>
		</section>
	)
}

export default SliderWidget
