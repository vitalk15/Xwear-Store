import { Routes, Route } from 'react-router-dom'
import MainLayout from '@/components/layout/MainLayout'
import HomePage from '@/pages/HomePage'
import { paths } from './paths'

// Универсальная заглушка для внутренних страниц
const TargetPage = ({ title }) => (
	<div className="container" style={{ padding: '40px 0', minHeight: '80vh' }}>
		<h1 style={{ fontSize: '32px', marginBottom: '16px' }}>{title}</h1>
		<p style={{ color: '#8c8f96' }}>Страница находится в разработке.</p>
	</div>
)

const AppRoutes = () => {
	return (
		<Routes>
			{/* Главный Layout объединяет общие элементы */}
			<Route element={<MainLayout />}>
				<Route path={paths.home} element={<HomePage />} />
				<Route path={paths.clothes} element={<TargetPage title="Одежда" />} />
				<Route path={paths.shoes} element={<TargetPage title="Обувь" />} />
				<Route path={paths.accessories} element={<TargetPage title="Аксессуары" />} />
				<Route path={paths.brands} element={<TargetPage title="Бренды" />} />
				<Route path={paths.info} element={<TargetPage title="Информация" />} />
			</Route>
		</Routes>
	)
}

export default AppRoutes
