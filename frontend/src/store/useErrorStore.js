import { create } from 'zustand'

const useErrorStore = create((set) => ({
	hasError: false,
	statusCode: null, // e.g., 429, 500, 502, 'ERR_NETWORK'
	errorMessage: '',

	// Экшен для установки ошибки
	setError: ({ statusCode, message }) =>
		set({ hasError: true, statusCode, errorMessage: message }),

	// Экшен для сброса ошибки
	clearError: () => set({ hasError: false, statusCode: null, errorMessage: '' }),
}))

export default useErrorStore
