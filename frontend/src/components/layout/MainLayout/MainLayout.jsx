import { Outlet } from 'react-router-dom'
import Header from '@/components/common/Header'
import Footer from '@/components/common/Footer'
import ServerErrorPage from '@/pages/ServerErrorPage'
import useErrorStore from '@/store/useErrorStore'
import styles from './MainLayout.module.scss'

const MainLayout = () => {
	const { hasError } = useErrorStore()

	if (hasError) {
		return <ServerErrorPage />
	}

	return (
		<div className={styles.layout}>
			<Header />
			<main className={styles.mainContent}>
				<Outlet />
			</main>
			<Footer />
		</div>
	)
}

export default MainLayout
