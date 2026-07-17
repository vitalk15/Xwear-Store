import { useMemo } from 'react'
import { useCategories } from './useCategories'

// хук для поиска категории по пути
export const useCategoryByPath = (fullPath) => {
	const { data: categories = [] } = useCategories()

	const currentCategory = useMemo(() => {
		if (!fullPath || !categories.length) return null

		// Рекурсивный поиск категории по дереву
		const findCategory = (nodes, targetPath) => {
			for (const node of nodes) {
				if (node.full_path === targetPath) return node
				if (node.children?.length) {
					const found = findCategory(node.children, targetPath)
					if (found) return found
				}
			}
			return null
		}

		return findCategory(categories, fullPath)
	}, [categories, fullPath])

	return currentCategory
}
