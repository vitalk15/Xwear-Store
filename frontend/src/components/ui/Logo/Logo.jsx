import { Link } from 'react-router-dom'
import { paths } from '@/routes/paths'
import styles from './Logo.module.scss'

const Logo = ({ isHomePage }) => {
	const logoImage = <img src="/logo.svg" alt="XWEAR Logo" className={styles.logoImg} />

	if (isHomePage) {
		return <div className={styles.logoStatic}>{logoImage}</div>
	}

	return (
		<Link to={paths.home} className={styles.logoLink} aria-label="На главную страницу">
			{logoImage}
		</Link>
	)
}

export default Logo
