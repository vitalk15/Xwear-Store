import { Navigate, Outlet } from 'react-router-dom'
import useAuthStore from '@/features/auth/store/useAuthStore'
import { paths } from '@/routes/paths'

const ProtectedRoute = () => {
	const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

	// Если пользователь не авторизован — перекидываем его на главную
	if (!isAuthenticated) {
		return <Navigate to={paths.home} replace />
	}

	// Если авторизован — рендерим дочерние роуты (ProfilePage)
	return <Outlet />
}

export default ProtectedRoute
