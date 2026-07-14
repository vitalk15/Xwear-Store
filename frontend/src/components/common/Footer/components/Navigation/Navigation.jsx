import { Link } from 'react-router-dom'
import { useCategories } from '@/entities/category/hooks/useCategories'
import { STATIC_INFO_MENU } from '@/shared/constants/info-menu'
import styles from '@/components/common/Footer/Footer.module.scss'

const Navigation = () => {
	const { data: categories } = useCategories()

	// Объединяем динамические данные от сервера и нашу статику в один массив
	const navMenu = [...categories, STATIC_INFO_MENU]

	return (
		<>
			{/* Колонки категорий */}
			{navMenu?.map((rootCategory) => (
				<div key={rootCategory.id} className={styles.navCol}>
					<h4 className={styles.colTitle}>{rootCategory.name}</h4>
					<ul className={styles.linkList}>
						{rootCategory.children?.map((child) => (
							<li key={child.id}>
								<Link to={`/${child.full_path}`}>{child.name}</Link>
							</li>
						))}
					</ul>
				</div>
			))}
		</>
	)
}

export default Navigation
