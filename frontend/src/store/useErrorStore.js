import { create } from 'zustand'

const useErrorStore = create((set) => ({
	hasError: false,
	errorMessage: '',

	// Экшен для установки ошибки
	setError: (message) => set({ hasError: true, errorMessage: message }),

	// Экшен для сброса ошибки
	clearError: () => set({ hasError: false, errorMessage: '' }),
}))

export default useErrorStore
