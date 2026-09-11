import EmptyFavoritesIcon from '@/shared/icons/empty-favorites.svg'
import styles from './FavoritesPage.module.scss'

const EmptyFavorites = () => {
	return (
		<div className={styles.emptyContainer}>
			<EmptyFavoritesIcon className={styles.icon} />
			<h2 className={styles.title}>ЭТОТ СПИСОК ЖЕЛАНИЙ ПУСТ.</h2>
			<p className={styles.description}>У вас пока нет товаров в списке желаний.</p>
		</div>
	)
}

export default EmptyFavorites
