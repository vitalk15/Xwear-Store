import { Outlet } from 'react-router-dom'
import Header from '@/components/common/Header'
import Footer from '@/components/common/Footer'
import GlobalErrorModal from '@/components/common/GlobalErrorModal'
import styles from './MainLayout.module.scss'

const MainLayout = () => {
	return (
		<div className={styles.layout}>
			<Header />

			{/* Семантический тег для основного контента */}
			<main className={styles.mainContent}>
				<Outlet />
			</main>

			<Footer />

			<GlobalErrorModal />
		</div>
	)
}

export default MainLayout
