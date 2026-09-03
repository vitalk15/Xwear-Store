import { create } from 'zustand'

// Стор для управления авторизацией (хранения access-токена, данных вошедшего пользователя и статуса авторизации)
const useAuthStore = create((set) => ({
	user: null,
	accessToken: null,
	isAuthenticated: false,

	// Установка данных после успешного входа или активации
	setAuth: ({ user, access }) => {
		set({
			user,
			accessToken: access,
			isAuthenticated: true,
		})
	},

	// Выход из системы
	logout: () => {
		set({
			user: null,
			accessToken: null,
			isAuthenticated: false,
		})
	},
}))

export default useAuthStore
