import { Routes, Route } from 'react-router-dom'
import MainLayout from '@/components/layout/MainLayout'
import HomePage from '@/pages/HomePage'
import CatalogDispatcher from './CatalogDispatcher'
import { paths } from './paths'

const AppRoutes = () => {
	return (
		<Routes>
			{/* Главный Layout объединяет общие элементы (Header, Footer) */}
			<Route element={<MainLayout />}>
				<Route path={paths.home} element={<HomePage />} />
				<Route path={`${paths.catalog}/*`} element={<CatalogDispatcher />} />
			</Route>
		</Routes>
	)
}

export default AppRoutes
