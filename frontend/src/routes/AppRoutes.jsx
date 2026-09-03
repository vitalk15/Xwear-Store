import { Routes, Route } from 'react-router-dom'
import MainLayout from '@/components/layout/MainLayout'
import HomePage from '@/pages/HomePage'
import ActivatePage from '@/pages/ActivatePage'
import CatalogDispatcher from './CatalogDispatcher'
import NotFoundPage from '@/pages/NotFoundPage'
import { paths } from './paths'

const AppRoutes = () => {
	return (
		<Routes>
			{/* Главный Layout объединяет общие элементы (Header, Footer) */}
			<Route element={<MainLayout />}>
				<Route path={paths.home} element={<HomePage />} />
				<Route path={`${paths.catalog}/*`} element={<CatalogDispatcher />} />
				<Route path={paths.activate} element={<ActivatePage />} />
				{/* Перехватывает всё, что не подошло под условия выше */}
				<Route path="*" element={<NotFoundPage />} />
			</Route>
		</Routes>
	)
}

export default AppRoutes
