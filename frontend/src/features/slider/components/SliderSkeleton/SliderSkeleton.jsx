import styles from './SliderSkeleton.module.scss'

const SliderSkeleton = () => {
	return (
		<div className={styles.skeletonWrapper}>
			<div className={styles.skeletonSlide}>
				<div className={styles.pulse}></div>
			</div>
		</div>
	)
}

export default SliderSkeleton
