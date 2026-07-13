import { useRef, useEffect } from 'react'
import { SearchIcon, StarIcon, UserIcon, BagIcon } from '@/components/common/Header/Icons'
import { formatPriceBy } from '@/shared/utils/formatPriceBy'
import styles from './HeaderActions.module.scss'

// Принимаем пропсы из Header
const HeaderActions = ({ isSearchOpen, setIsSearchOpen }) => {
	// Todo: После подключим Zustand Store для авторизации и корзины
	// Имитация состояния авторизации (потом заменим на Zustand useAuthStore)
	const isAuthenticated = true
	// Имитация данных корзины (потом заменим на Zustand useCartStore)
	const cartTotalItems = 5
	const cartTotalPrice = formatPriceBy(1250)

	// Ссылки для управления фокусом поля поиска и кликом вне области
	const searchWrapperRef = useRef(null)
	const inputRef = useRef(null)

	// Обработчик клика по лупе
	const handleSearchToggle = (e) => {
		e.preventDefault()
		setIsSearchOpen(!isSearchOpen)
	}

	// Управление фокусом поля поиска и очисткой
	useEffect(() => {
		if (isSearchOpen && inputRef.current) {
			// Даем браузеру 50мс на применение CSS-свойств видимости перед фокусом
			setTimeout(() => {
				inputRef.current.focus()
			}, 50)
		} else if (!isSearchOpen && inputRef.current) {
			inputRef.current.value = ''
			inputRef.current.blur()

			// Очищаем текст только ПОСЛЕ того, как инпут плавно уехал (400мс)
			// setTimeout(() => {
			// 	if (inputRef.current) inputRef.current.value = ''
			// }, 400)
		}
	}, [isSearchOpen])

	// Закрытие поиска при клике вне его области
	useEffect(() => {
		const handleClickOutside = (e) => {
			// Если клик был не по обертке поиска и поиск открыт — закрываем
			if (
				isSearchOpen &&
				searchWrapperRef.current &&
				!searchWrapperRef.current.contains(e.target)
			) {
				setIsSearchOpen(false)
			}
		}
		document.addEventListener('mousedown', handleClickOutside)
		return () => document.removeEventListener('mousedown', handleClickOutside)
	}, [isSearchOpen, setIsSearchOpen])

	return (
		<ul className={styles.actionsList}>
			<li className={styles.searchWrapper} ref={searchWrapperRef}>
				<input
					ref={inputRef}
					type="text"
					className={`${styles.searchInput} ${isSearchOpen ? styles.searchInputOpen : ''}`}
					placeholder="Поиск по каталогу товаров"
				/>
				<button
					className={`${styles.actionBtn} ${isSearchOpen ? styles.actionBtnActive : ''}`}
					aria-label="Открыть поиск"
					onClick={handleSearchToggle}
				>
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
								<span className={styles.cartPrice}>{cartTotalPrice}</span>
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
