import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import useAuthStore from '@/features/auth/store/useAuthStore'
import { logoutUser } from '@/features/auth/api/auth.api'
import { paths } from '@/routes/paths'
import PageTitle from '@/components/common/PageTitle'
import ProfileIcon from '@/shared/icons/profile.svg'
import EditProfileIcon from '@/shared/icons/redaction-profile.svg'
import StoryOrdersIcon from '@/shared/icons/story.svg'
import OrdersIcon from '@/shared/icons/orders.svg'
import AddressIcon from '@/shared/icons/address.svg'
import EditAddressIcon from '@/shared/icons/redaction-address.svg'
import PasswordIcon from '@/shared/icons/password.svg'
import LogoutIcon from '@/shared/icons/logout.svg'
import styles from './ProfilePage.module.scss'

const ProfilePage = () => {
	const navigate = useNavigate()
	const logout = useAuthStore((state) => state.logout)
	const user = useAuthStore((state) => state.user) // Чтобы достать имя/email

	// Временное состояние для управления активной вкладкой
	const [activeTab, setActiveTab] = useState('account')

	const handleLogout = async () => {
		try {
			// Отправляем запрос на сервер для удаления куки
			await logoutUser()
		} catch (error) {
			console.error('Ошибка при логауте на сервере', error)
			// Даже если сервер недоступен, мы всё равно должны выкинуть юзера из фронтенда
		} finally {
			// Очищаем Zustand Store
			logout()
			// Возвращаем на главную страницу
			navigate(paths.home)
		}
	}

	// Конфигурация меню для удобного рендера
	const menuItems = [
		{ id: 'account', label: 'Мой аккаунт', icon: <ProfileIcon /> },
		{ id: 'edit-profile', label: 'Редактировать профиль', icon: <EditProfileIcon /> },
		{ id: 'orders-history', label: 'История заказов', icon: <StoryOrdersIcon /> },
		{ id: 'my-orders', label: 'Мои заказы', icon: <OrdersIcon /> }, // По макету их два разных?
		{ id: 'addresses', label: 'Адреса', icon: <AddressIcon /> },
		{ id: 'edit-addresses', label: 'Редактировать адреса', icon: <EditAddressIcon /> },
		{ id: 'password', label: 'Пароль', icon: <PasswordIcon /> },
	]

	return (
		<>
			<PageTitle title="Личный кабинет" />

			<div className="container">
				{/* Хлебные крошки */}
				<nav className={styles.breadcrumbs} aria-label="Хлебные крошки">
					<Link to={paths.home} className={styles.breadcrumbLink}>
						Главная
					</Link>
					<span className={styles.breadcrumbSeparator}>/</span>
					<span className={styles.breadcrumbCurrent}>Личный кабинет</span>
				</nav>

				<h1 className={styles.pageTitle}>ЛИЧНЫЙ КАБИНЕТ</h1>

				<div className={styles.layout}>
					{/* Левая колонка (Сайдбар) */}
					<aside className={styles.sidebar}>
						<nav aria-label="Меню профиля">
							<ul className={styles.navList}>
								{menuItems.map((item) => (
									<li key={item.id} className={styles.navItem}>
										<button
											className={`${styles.navBtn} ${activeTab === item.id ? styles.active : ''}`}
											onClick={() => setActiveTab(item.id)}
										>
											<span className={styles.iconWrapper}>{item.icon}</span>
											{item.label}
										</button>
									</li>
								))}

								{/* Кнопка выхода всегда внизу и имеет отдельную логику */}
								<li className={styles.navItem}>
									<button className={styles.navBtn} onClick={handleLogout}>
										<span className={styles.iconWrapper}>
											<LogoutIcon />
										</span>
										Выход
									</button>
								</li>
							</ul>
						</nav>
					</aside>

					{/* Правая колонка (Контентная часть) */}
					<section className={styles.content}>
						<h2 className={styles.welcomeText}>
							Приветствуем, {user?.email || 'Пользователь'}!
						</h2>
						{/* Здесь мы будем рендерить компоненты в зависимости от выбранной вкладки */}
					</section>
				</div>
			</div>
		</>
	)
}

export default ProfilePage
