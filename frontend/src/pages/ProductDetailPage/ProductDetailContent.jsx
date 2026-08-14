import Breadcrumbs from '@/components/common/Breadcrumbs'
import ProductGallery from '@/features/catalog/components/ProductGallery'
import ProductInfo from '@/features/catalog/components/ProductInfo'
import styles from './ProductDetailPage.module.scss'

const ProductDetailContent = ({ product }) => {
	const { breadcrumbs, naming, images } = product

	// Формируем лаконичный заголовок для хлебных крошек (Бренд + Модель)
	const breadcrumbTitle = `${naming.brand.name} ${naming.model}`

	return (
		<>
			{/* 1. Хлебные крошки */}
			<Breadcrumbs backendBreadcrumbs={breadcrumbs} currentTitle={breadcrumbTitle} />

			{/* 2. Верхняя часть страницы */}
			<div className={styles.topSection}>
				{/* Левая колонка: Слайдер галереи */}
				<ProductGallery images={images} />

				{/* Правая колонка: Информация о товаре */}
				<ProductInfo product={product} />
			</div>
		</>
	)
}

export default ProductDetailContent
