import ProductCard from '@/features/catalog/components/ProductCard'
import styles from './FavoriteGrid.module.scss'

const FavoriteGrid = ({ items = [] }) => {
	return (
		<div className={styles.grid}>
			{items.map((fav) => {
				// Если объект развернут из backend (variant_details)
				const productData = fav.variant_details || fav

				return (
					<ProductCard
						key={fav.id || fav.variant}
						product={productData}
						variantId={fav.variant}
						locationState={{ fromFavorites: true }} // вешаем "маячок" для хлебных крошек детальной страницы товаров
					/>
				)
			})}
		</div>
	)
}

export default FavoriteGrid
