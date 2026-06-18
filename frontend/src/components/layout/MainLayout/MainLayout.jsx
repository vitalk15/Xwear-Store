import { Outlet } from 'react-router-dom'
import Header from '@/components/common/Header'
import styles from './MainLayout.module.scss'

const MainLayout = () => {
	return (
		<div className={styles.layout}>
			<Header />

			{/* Семантический тег для основного контента */}
			<main className={styles.mainContent}>
				<Outlet />
			</main>

			{/* Здесь в будущем появится <Footer />, и он автоматически прижмется к низу */}
		</div>
	)
}

export default MainLayout
