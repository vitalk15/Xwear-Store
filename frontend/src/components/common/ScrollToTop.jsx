import { useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'

// Функция извлекает из URL только параметры фильтров (игнорируя 'page')
const getFilterParamsString = (searchString) => {
	const params = new URLSearchParams(searchString)
	params.delete('page')
	params.sort() // Сортировка нужна для корректного сравнения независимых ключей
	return params.toString()
}

const ScrollToTop = () => {
	const { pathname, search } = useLocation()

	// Используем useRef для хранения предыдущих значений URL без вызова ререндера
	const prevPathname = useRef(pathname)
	const prevSearch = useRef(search)

	useEffect(() => {
		// Парсим текущие и предыдущие параметры URL
		const currentParams = new URLSearchParams(search)
		const prevParams = new URLSearchParams(prevSearch.current)

		// Достаем значения пагинации
		const currentPage = currentParams.get('page')
		const prevPage = prevParams.get('page')

		// 1. Изменился ли сам URL-путь (например, переход между разделами сайта)
		const isPathChanged = pathname !== prevPathname.current

		// 2. Изменилась ли страница пагинации
		const isPageChanged = currentPage !== prevPage

		// 3. Изменились ли какие-либо фильтры в сайдбаре (без учета страницы)
		const isFilterChanged =
			getFilterParamsString(prevSearch.current) !== getFilterParamsString(search)

		// Прокручиваем страницу наверх ТОЛЬКО если:
		// - Изменился путь (pathname)
		// - ИЛИ изменилась пагинация, НО фильтры НЕ менялись (чистый клик по пагинации)
		if (isPathChanged || (isPageChanged && !isFilterChanged)) {
			window.scrollTo({
				top: 0,
				left: 0,
				behavior: isPathChanged ? 'instant' : 'smooth', // При смене URL-пути — мгновенно, при смене пагинации — плавно
			})
		}

		// Обновляем рефы актуальными данными для следующего срабатывания
		prevPathname.current = pathname
		prevSearch.current = search
	}, [pathname, search])

	return null
}

export default ScrollToTop
