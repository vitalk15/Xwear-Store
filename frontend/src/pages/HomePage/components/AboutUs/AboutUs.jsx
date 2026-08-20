import bgXwear from '@/assets/images/background-xwear.webp'
import BoxIcon from '@/shared/icons/box.svg'
import UsersIcon from '@/shared/icons/users.svg'
import CheckIcon from '@/shared/icons/check.svg'
import styles from './AboutUs.module.scss'

const AboutUs = () => {
	return (
		<section className={styles.sectionWrapper}>
			<div className={`container ${styles.section}`}>
				<img src={bgXwear} className={styles.bgImage} />
				<div className={styles.content}>
					<div className={styles.description}>
						<h2>
							Об интернет-
							<br />
							магазине xwear
						</h2>
						<p>
							Команда XWEAR предоставляет услугу доставки только оригинальных товаров c
							крупнейшего китайского маркетплейса Poizon, чтобы наши клиенты экономили
							более 40% на каждой покупке.
						</p>
						<p>
							Работаем без посредников, благодаря чему можем предоставлять лучшую цену.
							Быстрая, бесплатная доставка.
						</p>
						<p>
							Сайт, на котором можно будет удобно оформить покупку, не скачивая китайское
							мобильное приложение Poizon, с удобной фильтрацией огромного количества
							товаров, а так же с возможностью сразу увидеть окончательную цену товара.
						</p>
					</div>
					<div className={styles.advantage}>
						<div className={styles.advantageItem}>
							<BoxIcon />
							<div>
								<div className={styles.title}>Доставка во все города Беларуси</div>
								<div className={styles.text}>
									Доставим вам заказ абсолютно бесплатно до Беларуси
								</div>
							</div>
						</div>
						<div className={styles.advantageItem}>
							<UsersIcon />
							<div>
								<div className={styles.title}>Мы работаем без посредников</div>
								<div className={styles.text}>
									Между нами и клиентом нет третьего лишнего
								</div>
							</div>
						</div>
						<div className={styles.advantageItem}>
							<CheckIcon />
							<div>
								<div className={styles.title}>Простота в заказе и использовании</div>
								<div className={styles.text}>
									Для заказа с Poizon не нужно никаких приложений
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>
	)
}

export default AboutUs
