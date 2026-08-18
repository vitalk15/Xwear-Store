import Breadcrumbs from '@/components/common/Breadcrumbs'
import ProductGallery from '@/features/catalog/components/ProductGallery'
import ProductInfo from '@/features/catalog/components/ProductInfo'
import ProductDescription from '@/features/catalog/components/ProductDescription'
import ProductCharacteristics from '@/features/catalog/components/ProductCharacteristics'
import styles from './ProductDetailPage.module.scss'

const ProductDetailContent = ({ product }) => {
	const { breadcrumbs, naming, images } = product

	// Формируем лаконичный заголовок для хлебных крошек (Бренд + Модель)
	const breadcrumbTitle = `${naming.brand.name} ${naming.model}`

	return (
		<>
			{/* 1. Хлебные крошки */}
			<Breadcrumbs backendBreadcrumbs={breadcrumbs} currentTitle={breadcrumbTitle} />

			{/* 2. Верхний блок (Слайдер галереи и Информация о товаре) */}
			<div className={styles.topSection}>
				<ProductGallery images={images} />
				<ProductInfo product={product} />
			</div>

			{/* 3. Средний блок (Описание и Характеристики) */}
			<ProductDescription description={product.description} />
			<ProductCharacteristics product={product} />
		</>
	)
}

export default ProductDetailContent
