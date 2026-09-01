import styles from './PasswordHints.module.scss'

const PasswordHints = ({ password = '', isVisible = false }) => {
	const isAllowedChars = password.length > 0 && /^[a-zA-Z0-9!?$@#_.]+$/.test(password)
	const isMinLength = password.length >= 8
	const hasLowercase = /[a-z]/.test(password)
	const hasUppercase = /[A-Z]/.test(password)
	const hasNumber = /\d/.test(password)
	const hasSpecialChar = /[!?$@#_.]/.test(password)

	return (
		<div className={`${styles.hintsContainer} ${isVisible ? styles.visible : ''}`}>
			<p>Пароль должен содержать:</p>
			<ul>
				<li className={isAllowedChars ? styles.hintValid : ''}>
					Только латиницу, цифры и допустимые спецсимволы
				</li>
				<li className={isMinLength ? styles.hintValid : ''}>Минимум 8 символов</li>
				<li className={hasLowercase ? styles.hintValid : ''}>Строчную букву (a-z)</li>
				<li className={hasUppercase ? styles.hintValid : ''}>Заглавную букву (A-Z)</li>
				<li className={hasNumber ? styles.hintValid : ''}>Цифру (0-9)</li>
				<li className={hasSpecialChar ? styles.hintValid : ''}>Спецсимвол (!?$@#_.)</li>
			</ul>
		</div>
	)
}

export default PasswordHints
