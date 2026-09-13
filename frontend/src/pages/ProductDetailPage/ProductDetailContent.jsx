import { useLocation } from 'react-router-dom'
import Breadcrumbs from '@/components/common/Breadcrumbs'
import ProductGallery from '@/features/catalog/components/ProductGallery'
import ProductInfo from '@/features/catalog/components/ProductInfo'
import ProductDescription from '@/features/catalog/components/ProductDescription'
import ProductCharacteristics from '@/features/catalog/components/ProductCharacteristics'
import ProductRecommends from '@/features/catalog/components/ProductRecommends'
import CartNotification from '@/features/cart/components/CartNotification'
import { paths } from '@/routes/paths'
import styles from './ProductDetailPage.module.scss'

const ProductDetailContent = ({ product }) => {
	const { breadcrumbs, naming, images, id } = product

	const location = useLocation()

	// Проверяем, есть ли "маячок" от страницы Избранного
	const isFromFavorites = location.state?.fromFavorites

	// Формируем лаконичный заголовок для хлебных крошек (Бренд + Модель)
	const breadcrumbTitle = `${naming.brand.name} ${naming.model}`

	return (
		<>
			{/* 1. Хлебные крошки */}
			{isFromFavorites ? (
				// Если пришли из Избранного:
				<Breadcrumbs
					items={[
						{ name: 'Избранные товары', path: paths.favorites },
						{ name: breadcrumbTitle }, // Имя текущего товара
					]}
				/>
			) : (
				// Если пришли из Каталога или по прямой ссылке:
				<Breadcrumbs backendBreadcrumbs={breadcrumbs} currentTitle={breadcrumbTitle} />
			)}

			{/* 2. Слайдер галереи и информация о товаре */}
			<section className={styles.topSection}>
				<ProductGallery images={images} targetId={id} />
				<ProductInfo product={product} />
			</section>

			{/* 3. Описание */}
			<ProductDescription description={product.description} />
			{/* 4. Характеристики */}
			<ProductCharacteristics product={product} />
			{/* 5. Рекомендации */}
			<ProductRecommends productId={product.id} />
			{/* Всплывающая плашка добавления в корзину*/}
			<CartNotification />
		</>
	)
}

export default ProductDetailContent
