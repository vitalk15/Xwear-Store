import styles from './Button.module.scss'

/**
 * Универсальный компонент кнопки.
 *
 * @param {Object} props - Пропсы компонента.
 * @param {React.ReactNode} [props.children] - Текст или вложенный контент кнопки.
 * @param {'button' | 'submit' | 'reset'} [props.type='button'] - HTML-тип кнопки.
 * @param {boolean} [props.disabled=false] - Состояние блокировки кнопки.
 * @param {string} [props.className=''] - Дополнительные CSS-классы для стилизации.
 * @param {React.ButtonHTMLAttributes<HTMLButtonElement>} [props...props] - Дополнительные HTML-атрибуты элемента <button> (onClick, aria-label, data-* и т. д.).
 *
 * @returns {JSX.Element}
 */
const Button = ({
	children,
	type = 'button',
	disabled = false,
	className = '',
	...props
}) => {
	return (
		<button
			type={type}
			disabled={disabled}
			className={`${styles.button} ${className}`.trim()}
			{...props}
		>
			{children}
		</button>
	)
}

export default Button
