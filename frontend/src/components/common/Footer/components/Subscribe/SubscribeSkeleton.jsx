import styles from '@/components/common/Footer/Footer.module.scss'

const SubscribeSkeleton = () => {
	return (
		<div className={styles.subscribeCol}>
			{/* Заголовок */}
			<div className={`${styles.skeleton} ${styles.titleSkeleton}`}></div>

			{/* Описание */}
			<div
				className={`${styles.skeleton} ${styles.linkSkeleton}`}
				style={{ marginBottom: '24px' }}
			></div>

			{/* Имитация формы подписки */}
			<div
				className={`${styles.skeleton} ${styles.inputSkeleton}`}
				style={{ marginBottom: '24px', height: '36px' }}
			></div>

			{/* Дисклеймер и ссылки */}
			<div className={styles.disclaimerBlock}>
				<div
					className={`${styles.skeleton} ${styles.linkSkeletonShort}`}
					style={{ height: '32px', width: '100%' }}
				></div>

				{/* Пульсирующие ссылки на документы */}
				<div className={styles.skeletonLinks}>
					<div className={styles.skeletonLine} style={{ width: '170px' }} />
					<div className={styles.skeletonLine} style={{ width: '150px' }} />
				</div>
			</div>
		</div>
	)
}

export default SubscribeSkeleton
