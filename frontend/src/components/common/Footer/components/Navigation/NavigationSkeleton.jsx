import styles from '@/components/common/Footer/Footer.module.scss'

const NavigationSkeleton = () => {
	return (
		<>
			{/* Имитируем 4 колонки (3 категории + Информация) */}
			{[...Array(4)].map((_, index) => (
				<div key={index} className={styles.navCol}>
					<div className={`${styles.skeleton} ${styles.titleSkeleton}`}></div>
					<div className={`${styles.skeleton} ${styles.linkSkeleton}`}></div>
					<div className={`${styles.skeleton} ${styles.linkSkeletonShort}`}></div>
					<div className={`${styles.skeleton} ${styles.linkSkeleton}`}></div>
				</div>
			))}
		</>
	)
}

export default NavigationSkeleton
