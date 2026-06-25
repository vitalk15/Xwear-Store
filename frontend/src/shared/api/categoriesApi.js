import { apiClient } from './apiClient'

export const fetchCategoriesData = async () => {
	const response = await apiClient.get('/shop/categories/')
	return response.data
}
