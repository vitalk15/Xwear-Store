import { Link } from 'react-router-dom'
import ProductCard from '../ProductCard'
import { useCategoryProductsQuery } from '@/features/catalog/hooks/useCategoryProductsQuery'
import ArrowIcon from '@/shared/icons/arrow.svg'
import styles from './CatalogSection.module.scss'

const CatalogSection = ({ title, categoryId }) => {
	// Запрашиваем 4 товара для указанной категории
	const { data } = useCategoryProductsQuery(categoryId, 4)

	// Извлекаем массив из ответа DRF
	const products = data || []

	if (products.length === 0) return null

	// !!! Todo: Ссылка "Больше товаров" - переписать на динамический адрес (д.б. `/catalog/${categorySlug}`)

	return (
		<section className={styles.section}>
			<div className="container">
				{/* Обертка для заголовка и ссылки */}
				<div className={styles.header}>
					<h2 className={styles.title}>{title}</h2>
					{/* Ссылка "Больше товаров". URL пока делаем шаблонным  */}
					<Link to={`/catalog/${categoryId}`} className={styles.moreLink}>
						Больше товаров
						<ArrowIcon />
					</Link>
				</div>
				{/* Контейнер с карточками товаров */}
				<div className={styles.row}>
					{products.map((product) => (
						<ProductCard key={product.id} product={product} />
					))}
				</div>
			</div>
		</section>
	)
}

export default CatalogSection
