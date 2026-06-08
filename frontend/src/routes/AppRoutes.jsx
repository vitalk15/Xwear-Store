import { Routes, Route } from 'react-router-dom'
import { paths } from './paths'

// Временная заглушка для Главной страницы (с большой высотой для теста скролла хедера)
const HomePage = () => (
	<div
		style={{
			padding: '120px 40px',
			minHeight: '200vh',
			background: '#f9f9fb',
			color: '#121214',
		}}
	>
		<h1 style={{ fontSize: '32px', marginBottom: '16px' }}>Главная страница</h1>
		<p style={{ color: '#8c8f96' }}>
			Покрутите страницу вниз, чтобы проверить, как плавно скрывается хедер.
		</p>
	</div>
)

// Универсальная заглушка для внутренних страниц
const TargetPage = ({ title }) => (
	<div
		style={{
			padding: '120px 40px',
			minHeight: '100vh',
			background: '#f0f2f5',
			color: '#121214',
		}}
	>
		<h1 style={{ fontSize: '32px', marginBottom: '16px' }}>{title}</h1>
		<p style={{ color: '#8c8f96' }}>
			Обратите внимание на логотип в хедере — теперь он кликабелен и вернет вас на
			главную.
		</p>
	</div>
)

const AppRoutes = () => {
	return (
		<Routes>
			<Route path={paths.home} element={<HomePage />} />
			<Route path={paths.clothes} element={<TargetPage title="Одежда" />} />
			<Route path={paths.shoes} element={<TargetPage title="Обувь" />} />
			<Route path={paths.accessories} element={<TargetPage title="Аксессуары" />} />
			<Route path={paths.brands} element={<TargetPage title="Бренды" />} />
			<Route path={paths.calculator} element={<TargetPage title="Расчет стоимости" />} />
			<Route path={paths.info} element={<TargetPage title="Информация" />} />
		</Routes>
	)
}

export default AppRoutes
