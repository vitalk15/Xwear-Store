import { forwardRef } from 'react'

/**
 * Базовый инпут для форм (email, text)
 */
const InputField = forwardRef(({ label, error, ...props }, ref) => {
	return (
		<div className={`inputGroup ${error ? 'inputError' : ''}`.trim()}>
			{label && <label>{label}</label>}
			<input ref={ref} {...props} />
			{error && <span className="errorText">{error.message}</span>}
		</div>
	)
})

InputField.displayName = 'InputField' // !!! Для чего это?
export default InputField
