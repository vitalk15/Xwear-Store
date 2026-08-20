import styles from '../ProductCard.module.scss' // Переиспользуем некоторые стили
import skeletonStyles from './ProductCardSkeleton.module.scss'

const ProductCardSkeleton = () => {
	return (
		<div className={styles.card}>
			<div className={`${skeletonStyles.imageSkeleton} ${skeletonStyles.pulse}`}></div>
			<div className={styles.infoWrapper}>
				<div className={`${skeletonStyles.titleSkeleton} ${skeletonStyles.pulse}`}></div>
				<div className={`${skeletonStyles.priceSkeleton} ${skeletonStyles.pulse}`}></div>
			</div>
		</div>
	)
}

export default ProductCardSkeleton
