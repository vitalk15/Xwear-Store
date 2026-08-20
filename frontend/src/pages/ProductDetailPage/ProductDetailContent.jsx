import Breadcrumbs from '@/components/common/Breadcrumbs'
import ProductGallery from '@/features/catalog/components/ProductGallery'
import ProductInfo from '@/features/catalog/components/ProductInfo'
import ProductDescription from '@/features/catalog/components/ProductDescription'
import ProductCharacteristics from '@/features/catalog/components/ProductCharacteristics'
import ProductRecommends from '@/features/catalog/components/ProductRecommends'
import styles from './ProductDetailPage.module.scss'

const ProductDetailContent = ({ product }) => {
	const { breadcrumbs, naming, images } = product

	// Формируем лаконичный заголовок для хлебных крошек (Бренд + Модель)
	const breadcrumbTitle = `${naming.brand.name} ${naming.model}`

	return (
		<>
			{/* 1. Хлебные крошки */}
			<Breadcrumbs backendBreadcrumbs={breadcrumbs} currentTitle={breadcrumbTitle} />

			{/* 2. Слайдер галереи и информация о товаре */}
			<section className={styles.topSection}>
				<ProductGallery images={images} />
				<ProductInfo product={product} />
			</section>

			{/* 3. Описание */}
			<ProductDescription description={product.description} />
			{/* 4. Характеристики */}
			<ProductCharacteristics product={product} />
			{/* 5. Рекомендации */}
			<ProductRecommends productId={product.id} />
		</>
	)
}

export default ProductDetailContent
