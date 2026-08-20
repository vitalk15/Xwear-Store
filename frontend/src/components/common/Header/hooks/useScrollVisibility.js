import { useState, useEffect } from 'react'

// скрытие/появление элемента при скролле
const useScrollVisibility = (threshold = 80) => {
	const [isVisible, setIsVisible] = useState(true)
	const [lastScrollY, setLastScrollY] = useState(0)

	useEffect(() => {
		const handleScroll = () => {
			const currentScrollY = window.scrollY

			// Если листаем вниз и пролистали больше threshold px — скрываем
			if (currentScrollY > lastScrollY && currentScrollY > threshold) {
				setIsVisible(false)
			} else if (currentScrollY < lastScrollY) {
				// Если листаем вверх — показываем
				setIsVisible(true)
			}
			setLastScrollY(currentScrollY)
		}

		window.addEventListener('scroll', handleScroll, { passive: true })
		return () => window.removeEventListener('scroll', handleScroll)
	}, [lastScrollY, threshold])

	return isVisible
}

export default useScrollVisibility
