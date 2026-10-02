import { create } from 'zustand'
import { persist } from 'zustand/middleware'
// Если вынесен инстанс queryClient, импортируем его для мягкой очистки:
import { queryClient } from '@/shared/api/queryClient'
// import { FAVORITES_QUERY_KEY } from '@/features/favorites/hooks/useFavorites'
// import { paths } from '@/routes/paths'

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
				// 1. Очищаем стейт авторизации
				// ProtectedRoute мгновенно убирает страницу и начинает переход на главную
				set({ user: null, access: null, isAuthenticated: false })

				// 2. Выполняем жесткую перезагрузку и редирект на главную.
				// Это гарантированно сотрет весь кэш React Query из памяти браузера.
				// window.location.href = paths.home

				// или чтобы пользователь не мог вернуться назад кнопкой «Назад» (стереть историю текущей сессии)
				// window.location.replace(paths.home)

				/* 
        АЛЬТЕРНАТИВНЫЙ ВАРИАНТ (SPA-подход без белой вспышки перезагрузки):
        Если нужно, чтобы страница не перезагружалась целиком, 
        а просто очистился кэш, то раскомментировать код ниже, а window.location.href удалить.
        */
				// 2. Очищаем весь кэш React Query (включая избранное, корзину, профиль)
				// Откладываем очистку кэша буквально на 100 миллисекунд.
				// За это время страница закроется, компоненты размонтируются
				setTimeout(() => {
					queryClient.clear()
				}, 100)

				// 2. Альтернатива: если нужно очистить только конкретный ключ из кэша React Query
				// setTimeout(() => {
				// 	queryClient.removeQueries({ queryKey: FAVORITES_QUERY_KEY })
				// }, 50)
			},
		}),
		{
			name: 'auth-storage', // Ключ, по которому данные будут лежать в localStorage
		},
	),
)

export default useAuthStore
