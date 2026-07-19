import { BrowserRouter } from 'react-router-dom'
import ScrollToTop from './components/common/ScrollToTop'
import AppRoutes from './routes/AppRoutes'

const App = () => {
	return (
		<BrowserRouter>
			<ScrollToTop />
			<AppRoutes />
		</BrowserRouter>
	)
}

export default App
