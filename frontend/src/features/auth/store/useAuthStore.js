import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Стор для управления авторизацией (хранения access-токена, данных вошедшего пользователя и статуса авторизации). Persist - для автоматического сохранения данных в localStorage (чтобы они пережили перезагрузку сайта).
const useAuthStore = create(
	persist(
		(set) => ({
			user: null,
			access: null,
			isAuthenticated: false,

			// Установка данных после успешного входа или активации
			setAuth: ({ user, access }) => {
				set({ user, access, isAuthenticated: true })
			},

			// Выход из системы
			logout: () => {
				set({ user: null, access: null, isAuthenticated: false })
			},
		}),
		{
			name: 'auth-storage', // Ключ, по которому данные будут лежать в localStorage
		},
	),
)

export default useAuthStore
