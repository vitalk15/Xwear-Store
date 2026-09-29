import { BrowserRouter } from 'react-router-dom'
import ScrollToTop from './components/common/ScrollToTop'
import { useToastStore } from './shared/store/useToastStore'
import Toast from './components/ui/Toast'
import AppRoutes from './routes/AppRoutes'

const App = () => {
	const toast = useToastStore((state) => state.toast)
	const hideToast = useToastStore((state) => state.hideToast)

	return (
		<>
			{/* Глобальный Toast для всего приложения */}
			{toast && <Toast message={toast.message} type={toast.type} onClose={hideToast} />}

			<BrowserRouter>
				<ScrollToTop />
				<AppRoutes />
			</BrowserRouter>
		</>
	)
}

export default App
