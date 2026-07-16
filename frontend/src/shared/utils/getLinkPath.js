import { paths } from '@/routes/paths'

// Вспомогательная функция для генерации путей в меню навигации
export const getLinkPath = (rootItem, targetItem) => {
	// Если это наша статичная колонка "Информация"
	if (rootItem.id === 'static-info') {
		return `/${targetItem.full_path}` // Выдаст: /contacts, /delivery и т.д.
	}
	// Если это динамические данные из каталога Django
	return `${paths.catalog}/${targetItem.full_path}` // Выдаст: /catalog/obuv/krossovki
}
