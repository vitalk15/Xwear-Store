import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

const ScrollToTop = () => {
	const { pathname, search } = useLocation()

	useEffect(() => {
		// Достаем pathname (путь) и search-параметры (все что после знака ?)
		window.scrollTo({
			top: 0,
			left: 0,
			behavior: 'instant', // 'instant' нужен, чтобы не было дерганой анимации прокрутки при смене страниц
		})
	}, [pathname, search])

	return null
}

export default ScrollToTop
