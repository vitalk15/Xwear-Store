import styles from './Navigation.module.scss'

const NavigationSkeleton = () => {
	// Рисуем 4 фейковых пунктов меню, пока настоящие грузятся
	return (
		<nav className={styles.navArea}>
			<div className={styles.skeletonList}>
				{[1, 2, 3, 4].map((item) => (
					<div key={item} className={styles.skeletonItem} />
				))}
			</div>
		</nav>
	)
}

export default NavigationSkeleton
