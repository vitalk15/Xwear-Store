import { apiClient } from '@/shared/api/apiClient'

export const fetchCategoryProducts = async (categoryId, params = {}) => {
	const { data } = await apiClient.get(`/shop/categories/${categoryId}/products/`, {
		params,
	})
	return data
}
