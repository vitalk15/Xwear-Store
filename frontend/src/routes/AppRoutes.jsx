import { Routes, Route } from 'react-router-dom'
import MainLayout from '@/components/layout/MainLayout'
import ProtectedRoute from '@/components/routing/ProtectedRoute'
import HomePage from '@/pages/HomePage'
import ActivatePage from '@/pages/ActivatePage'
import ResetPasswordConfirmPage from '@/pages/ResetPasswordConfirmPage'
import FavoritesPage from '@/pages/FavoritesPage'
import ProfilePage from '@/pages/ProfilePage'
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
				<Route path={paths.reset} element={<ResetPasswordConfirmPage />} />
				{/* Защищённые маршруты, требующие аутентификации */}
				<Route element={<ProtectedRoute />}>
					<Route path={paths.profile} element={<ProfilePage />} />
					<Route path={paths.favorites} element={<FavoritesPage />} />
				</Route>
				{/* Перехватывает всё, что не подошло под условия выше */}
				<Route path="*" element={<NotFoundPage />} />
			</Route>
		</Routes>
	)
}

export default AppRoutes
