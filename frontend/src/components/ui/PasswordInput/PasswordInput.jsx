import { forwardRef, useState } from 'react'
import ShowIcon from '@/shared/icons/show.svg'
import HideIcon from '@/shared/icons/hide.svg'

/**
 * Инпут для пароля со встроенной логикой скрытия/показа
 */
const PasswordInput = forwardRef(
	({ label, error, children, onChange, ...props }, ref) => {
		// стейт для показа/скрытия пароля
		const [showPassword, setShowPassword] = useState(false)
		// стейт отслеживает, есть ли текст
		const [hasValue, setHasValue] = useState(false)

		// Перехватываем onChange от react-hook-form, чтобы добавить свою логику
		const handleChange = (e) => {
			const value = e.target.value
			setHasValue(value.length > 0) // Управляем показом глазика

			if (value.length === 0) {
				setShowPassword(false) // Сбрасываем тип на password при пустом поле
			}

			// Вызываем оригинальный onChange от RHF, если он передан
			if (onChange) {
				onChange(e)
			}
		}

		return (
			<div className={`inputGroup ${error ? 'inputError' : ''}`.trim()}>
				{label && <label>{label}</label>}

				<div className="passwordInputWrapper">
					<input
						type={showPassword ? 'text' : 'password'}
						autoComplete="new-password" // Защита от автозаполнения браузером
						ref={ref}
						onChange={handleChange}
						{...props}
					/>

					{hasValue && (
						<button
							type="button"
							className="eyeBtn"
							onClick={() => setShowPassword(!showPassword)}
							tabIndex="-1" // Чтобы кнопка не мешала навигации клавишей Tab
						>
							{showPassword ? <ShowIcon /> : <HideIcon />}
						</button>
					)}

					{/* Сюда можно передать PasswordHints при необходимости */}
					{children}
				</div>

				{error && <span className="errorText">{error.message}</span>}
			</div>
		)
	},
)

PasswordInput.displayName = 'PasswordInput' // !!! Для чего это?
export default PasswordInput
