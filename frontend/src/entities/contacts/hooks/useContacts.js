import { useSuspenseQuery } from '@tanstack/react-query'
import { fetchContactsData } from '../api/contactsApi'

export const useContacts = () => {
	// делегируя обработку состояний компонентам Suspense (для загрузки)
	return useSuspenseQuery({
		queryKey: ['contacts'], // имя ячейки памяти (кэша)
		// функция, которая объясняет React Query, как именно нужно получить данные, если их нет в кэше.
		queryFn: fetchContactsData,
		// Кэшируем контакты на 1 час, так как контакты практически не меняются
		staleTime: 60 * 60 * 1000,
	})
}
