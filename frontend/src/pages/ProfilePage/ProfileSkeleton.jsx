import styles from './ProfilePage.module.scss'

const ProfileSkeleton = () => {
	return (
		<>
			{/* Имитация хлебных крошек */}
			<div className={styles.breadcrumbsSkeleton} />

			<div className={styles.titleSkeleton} />

			<div className={styles.skeletonLayout}>
				{/* Левая колонка (Сайдбар) */}
				<aside className={styles.sidebarSkeleton}>
					{[...Array(6)].map((_, i) => (
						<div key={i} className={styles.menuItemSkeleton} />
					))}
				</aside>

				{/* Правая колонка */}
				<div className={styles.contentSkeleton}>
					<div className={styles.welcomeSkeleton} />
					{/* Таблица заказов */}
					<div className={styles.tableSkeleton}></div>
				</div>
			</div>
		</>
	)
}

export default ProfileSkeleton
