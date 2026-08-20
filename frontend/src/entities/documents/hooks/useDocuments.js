import { useSuspenseQuery } from '@tanstack/react-query'
import { fetchDocumentsData } from '../api/documentsApi'

export const useDocuments = () => {
	// делегируя обработку состояний компонентам Suspense (для загрузки)
	return useSuspenseQuery({
		queryKey: ['documents'], // имя ячейки памяти (кэша)
		// функция, которая объясняет React Query, как именно нужно получить данные, если их нет в кэше.
		queryFn: fetchDocumentsData,
		// Кэшируем контакты на 1 час, так как контакты практически не меняются
		staleTime: 60 * 60 * 1000,
	})
}
