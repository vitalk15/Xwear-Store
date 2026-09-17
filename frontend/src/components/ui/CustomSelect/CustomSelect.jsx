import { useState, useRef, useEffect } from 'react'
import styles from './CustomSelect.module.scss'

const CustomSelect = ({ options, value, onChange, placeholder, error, disabled }) => {
	const [isOpen, setIsOpen] = useState(false)
	const containerRef = useRef(null)

	// Находим выбранный объект
	const selectedOption = options.find((opt) => String(opt.id) === String(value))

	// Закрываем список при клике вне компонента
	useEffect(() => {
		const handleClickOutside = (e) => {
			if (containerRef.current && !containerRef.current.contains(e.target)) {
				setIsOpen(false)
			}
		}
		document.addEventListener('mousedown', handleClickOutside)
		return () => document.removeEventListener('mousedown', handleClickOutside)
	}, [])

	return (
		<div
			className={`inputGroup ${styles.selectWrapper} ${isOpen ? styles.wrapperActive : ''} ${error ? 'inputError' : ''}`}
			ref={containerRef}
		>
			<label>Город</label>

			{/* Поле-триггер */}
			<div
				className={`${styles.trigger} ${error ? styles.error : ''} ${
					disabled ? styles.disabled : ''
				}`}
				onClick={() => !disabled && setIsOpen((prev) => !prev)}
				tabIndex={0} // <--- Добавляем возможность получить фокус
			>
				<span className={selectedOption ? styles.value : styles.placeholder}>
					{selectedOption ? selectedOption.name : placeholder}
				</span>
				<span className={`${styles.arrow} ${isOpen ? styles.arrowOpen : ''}`} />
			</div>

			{/* Всплывающее меню с настраиваемой рамкой и скруглением */}
			{isOpen && (
				<ul className={styles.dropdown}>
					{options.map((option) => (
						<li
							key={option.id}
							className={`${styles.option} ${
								String(option.id) === String(value) ? styles.selected : ''
							}`}
							onClick={() => {
								onChange(option.id)
								setIsOpen(false)
							}}
						>
							{option.name}
						</li>
					))}
				</ul>
			)}

			{error && <span className="errorText">{error.message}</span>}
		</div>
	)
}

export default CustomSelect
