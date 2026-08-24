import PageTitle from '@/components/common/PageTitle'
import styles from './NotFoundPage.module.scss'

const NotFoundPage = () => {
	return (
		<>
			<PageTitle title="404" />

			<div className="container">
				<div className={styles.notFoundContent}>
					<h1 className={styles.title}>Упс! Страница не найдена (404)</h1>
					<p className={styles.description}>
						Возможно, она была удалена, переименована, или вы просто ошиблись в адресе.
					</p>
				</div>
			</div>
		</>
	)
}

export default NotFoundPage
