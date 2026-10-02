import apiClient from '@/shared/api/apiClient'

export const fetchCategoriesData = async () => {
	const response = await apiClient.get('/shop/categories/')
	return response.data
}
