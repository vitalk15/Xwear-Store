import { useParams } from 'react-router-dom'
import CategoryPage from '@/pages/CategoryPage'
import ProductDetailPage from '@/pages/ProductDetailPage'
import NotFoundPage from '@/pages/NotFoundPage'

const CatalogDispatcher = () => {
	// Вытаскиваем весь путь, который попал под звездочку '*'
	// Например: 'obuv/muzhchinam/kedy/kedyi-fila-sp-court-belyj-60'
	const { '*': splat } = useParams()

	// Если пути после /catalog/ нет, рендерим корневую категорию (или перенаправляем)
	if (!splat) {
		return <NotFoundPage />
	}

	// Разбиваем путь по слешам и берем последний сегмент
	const segments = splat.split('/').filter(Boolean)
	const lastSegment = segments[segments.length - 1]

	// Регулярное выражение: ищем дефис и цифры в самом конце строки (например, "-60")
	const productMatch = lastSegment.match(/-(\d+)$/)

	if (productMatch) {
		// Это товар! Достаем ID (первая группа захвата из регулярки)
		const productId = productMatch[1]

		// Передаем ID в компонент детальной страницы товара
		return <ProductDetailPage productId={productId} />
	}

	// Если цифр в конце нет, значит это просто страница категории
	return <CategoryPage />
}

export default CatalogDispatcher
