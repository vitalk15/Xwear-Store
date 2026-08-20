import { useState } from 'react'
import ProductCard from '../ProductCard'
import { useProductRecommends } from '@/features/catalog/hooks/useProductRecommends'
import styles from './ProductRecommends.module.scss'

const ProductRecommends = ({ productId }) => {
	const { data: recommends } = useProductRecommends(productId)

	const [currentIndex, setCurrentIndex] = useState(0)

	// Если нет рекомендаций — ничего не показываем
	if (!recommends || recommends.length === 0) return null

	const visibleCards = 4 // Количество карточек на экране
	const maxIndex = Math.max(0, recommends.length - visibleCards)

	const handlePrev = () => setCurrentIndex((prev) => Math.max(0, prev - 1))
	const handleNext = () => setCurrentIndex((prev) => Math.min(maxIndex, prev + 1))

	return (
		<section className={styles.section}>
			<h2 className={styles.title}>Интересные предложения</h2>

			<div className={styles.carouselContainer}>
				<div
					className={styles.track}
					// Сдвигаем ленту влево на 25% (одна карточка) за каждый шаг
					style={{ transform: `translateX(-${currentIndex * (100 / visibleCards)}%)` }}
				>
					{recommends.map((product) => (
						<div key={product.id} className={styles.slide}>
							<ProductCard product={product} />
						</div>
					))}
				</div>
			</div>

			{maxIndex > 0 && (
				<div className={styles.controls}>
					<button
						onClick={handlePrev}
						disabled={currentIndex === 0}
						className={styles.arrowBtn}
					>
						<svg
							width="20"
							height="20"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							strokeWidth="2"
						>
							<polyline points="15 18 9 12 15 6"></polyline>
						</svg>
					</button>

					<div className={styles.dots}>
						{Array.from({ length: maxIndex + 1 }).map((_, i) => (
							<button
								key={i}
								className={`${styles.dot} ${i === currentIndex ? styles.activeDot : ''}`}
								onClick={() => setCurrentIndex(i)}
								aria-label={`Слайд ${i + 1}`}
							/>
						))}
					</div>

					<button
						onClick={handleNext}
						disabled={currentIndex === maxIndex}
						className={styles.arrowBtn}
					>
						<svg
							width="20"
							height="20"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							strokeWidth="2"
						>
							<polyline points="9 18 15 12 9 6"></polyline>
						</svg>
					</button>
				</div>
			)}
		</section>
	)
}

export default ProductRecommends
