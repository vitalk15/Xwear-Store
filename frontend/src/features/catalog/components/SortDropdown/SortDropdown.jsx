import React, { useState, useRef, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import styles from './SortDropdown.module.scss'

const SORT_OPTIONS = [
	{ value: 'price_asc', label: 'Сначала дешевые' },
	{ value: 'price_desc', label: 'Сначала дорогие' },
	{ value: 'newest', label: 'Сначала новинки' },
]

const SortDropdown = () => {
	const [searchParams, setSearchParams] = useSearchParams()
	const [isOpen, setIsOpen] = useState(false)
	const dropdownRef = useRef(null)

	// Текущее значение сортировки из URL (или 'default')
	const currentSort = searchParams.get('sort') || 'newest'
	const selectedOption =
		SORT_OPTIONS.find((opt) => opt.value === currentSort) || SORT_OPTIONS[0]

	// Закрываем дропдаун при клике вне его области
	useEffect(() => {
		const handleClickOutside = (event) => {
			if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
				setIsOpen(false)
			}
		}
		document.addEventListener('mousedown', handleClickOutside)
		return () => document.removeEventListener('mousedown', handleClickOutside)
	}, [])

	const handleSelect = (value) => {
		const newParams = new URLSearchParams(searchParams)

		if (value === 'newest') {
			newParams.delete('sort')
		} else {
			newParams.set('sort', value)
		}

		// При смене сортировки сбрасываем страницу на первую (если есть пагинация)
		newParams.delete('page')

		setSearchParams(newParams)
		setIsOpen(false)
	}

	return (
		<div className={styles.sortContainer} ref={dropdownRef}>
			<button
				type="button"
				className={styles.sortButton}
				onClick={() => setIsOpen(!isOpen)}
			>
				<span>{selectedOption.label}</span>
				<svg
					className={`${styles.arrowIcon} ${isOpen ? styles.open : ''}`}
					width="12"
					height="8"
					viewBox="0 0 12 8"
					fill="none"
				>
					<path
						d="M1 1.5L6 6.5L11 1.5"
						stroke="currentColor"
						strokeWidth="1.5"
						strokeLinecap="round"
						strokeLinejoin="round"
					/>
				</svg>
			</button>

			{isOpen && (
				<ul className={styles.dropdownMenu}>
					{SORT_OPTIONS.map((option) => (
						<li
							key={option.value}
							className={`${styles.dropdownItem} ${option.value === currentSort ? styles.active : ''}`}
							onClick={() => handleSelect(option.value)}
						>
							{option.label}
						</li>
					))}
				</ul>
			)}
		</div>
	)
}

export default SortDropdown
