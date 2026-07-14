import { useContacts } from '@/entities/contacts/hooks/useContacts'
import styles from '@/components/common/Footer/Footer.module.scss'

const Contacts = () => {
	const { data: contacts } = useContacts()

	const hasMessengers = contacts?.tg_url || contacts?.vb_url
	const hasSocials = contacts?.vk_url || contacts?.ig_url

	return (
		<div className={styles.navCol}>
			{/* Контакты: email и тел. */}
			<h4 className={styles.colTitle}>Контакты</h4>
			<ul className={styles.contactList}>
				<li>
					<a href={`mailto:${contacts?.email}`} className={styles.emailLink}>
						{contacts?.email}
					</a>
				</li>
				<li>
					<a href={`tel:${contacts?.phone}`} className={styles.phoneLink}>
						{contacts?.phone}
					</a>
				</li>
			</ul>

			{/* Мессенджеры (рендерим только если есть ссылки) */}
			{hasMessengers && (
				<div className={styles.socialBlock}>
					<h5 className={styles.subTitle}>Мессенджеры</h5>
					<div className={styles.iconGroup}>
						{contacts.tg_url && (
							<a href={contacts.tg_url} target="_blank" rel="noreferrer">
								<img src="/telegram.svg" alt="Telegram" />
							</a>
						)}
						{contacts.vb_url && (
							<a href={contacts.vb_url} target="_blank" rel="noreferrer">
								<img src="/viber.svg" alt="Viber" />
							</a>
						)}
					</div>
				</div>
			)}

			{/* Соц. сети (рендерим только если есть ссылки) */}
			{hasSocials && (
				<div className={styles.socialBlock}>
					<h5 className={styles.subTitle}>Наши соц. сети</h5>
					<div className={styles.iconGroup}>
						{contacts.vk_url && (
							<a href={contacts.vk_url} target="_blank" rel="noreferrer">
								<img src="/vk.svg" alt="VK" />
							</a>
						)}
						{contacts.ig_url && (
							<a href={contacts.ig_url} target="_blank" rel="noreferrer">
								<img src="/instagram.svg" alt="Instagram" />
							</a>
						)}
					</div>
				</div>
			)}
		</div>
	)
}

export default Contacts
