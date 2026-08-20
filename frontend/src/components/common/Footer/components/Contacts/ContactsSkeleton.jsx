import styles from '@/components/common/Footer/Footer.module.scss'

const ContactsSkeleton = () => {
	return (
		<div className={styles.navCol}>
			<div className={`${styles.skeleton} ${styles.titleSkeleton}`}></div>
			<div className={`${styles.skeleton} ${styles.linkSkeleton}`}></div>
			<div className={`${styles.skeleton} ${styles.linkSkeletonShort}`}></div>
			<div className={`${styles.skeleton} ${styles.inputSkeleton}`}></div>
		</div>
	)
}

export default ContactsSkeleton
