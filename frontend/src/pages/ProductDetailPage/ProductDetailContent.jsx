import Breadcrumbs from '@/components/common/Breadcrumbs'
import ProductGallery from '@/features/catalog/components/ProductGallery'
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
				{/* Слайдер галереи */}
				<ProductGallery images={images} />

				{/* Правая колонка: Название, Размеры, Выбор цвета, Кнопка Корзины */}
				<div className={styles.infoWrapper}>{/* Это мы сделаем на следующем шаге */}</div>
			</div>
		</>
	)
}

export default ProductDetailContent
