import { SearchIcon, StarIcon, UserIcon, BagIcon } from '../Icons'
import styles from './HeaderActions.module.scss'

const HeaderActions = () => {
	// После подключим Zustand Store для авторизации и корзины
	// Имитация состояния авторизации (потом заменим на Zustand useAuthStore)
	const isAuthenticated = true
	// Имитация данных корзины (потом заменим на Zustand useCartStore)
	const cartTotalItems = 5
	const cartTotalPrice = '11 899'

	return (
		<ul className={styles.actionsList}>
			<li>
				<button className={styles.actionBtn} aria-label="Поиск">
					<SearchIcon />
				</button>
			</li>

			{isAuthenticated ? (
				// Авторизованный пользователь
				<>
					<li>
						<button className={styles.actionBtn} aria-label="Избранное">
							<StarIcon />
						</button>
					</li>
					<li>
						<button className={styles.actionBtn} aria-label="Профиль">
							<UserIcon />
						</button>
					</li>
					<li>
						<button
							className={`${styles.actionBtn} ${styles.cartBtn}`}
							aria-label="Корзина"
						>
							<BagIcon />
							<div className={styles.cartInfo}>
								<span>{cartTotalPrice} ₽</span>
								<span className={styles.cartBadge}>{cartTotalItems}</span>
							</div>
						</button>
					</li>
				</>
			) : (
				// НЕ авторизованный пользователь
				<li>
					<button className={styles.actionBtn} aria-label="Войти">
						<UserIcon />
					</button>
				</li>
			)}
		</ul>
	)
}

export default HeaderActions
