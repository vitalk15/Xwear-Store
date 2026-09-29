import { create } from 'zustand'

export const useToastStore = create((set) => ({
	toast: null, // { message: string, type: 'success' | 'error' }

	showToast: (message, type = 'success') => {
		set({ toast: { message, type } })
	},

	hideToast: () => {
		set({ toast: null })
	},
}))
