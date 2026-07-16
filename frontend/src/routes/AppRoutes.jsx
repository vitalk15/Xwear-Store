import { Routes, Route } from 'react-router-dom'
import MainLayout from '@/components/layout/MainLayout'
import HomePage from '@/pages/HomePage'
import CategoryPage from '@/pages/CategoryPage'
import { paths } from './paths'

const AppRoutes = () => {
	return (
		<Routes>
			{/* Главный Layout объединяет общие элементы */}
			<Route element={<MainLayout />}>
				<Route path={paths.home} element={<HomePage />} />
				<Route path={`${paths.catalog}/*`} element={<CategoryPage />} />
			</Route>
		</Routes>
	)
}

export default AppRoutes
