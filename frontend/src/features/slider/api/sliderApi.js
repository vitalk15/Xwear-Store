import { apiClient } from '@/shared/api/apiClient'

export const fetchSliderData = async () => {
	const response = await apiClient.get('/shop/slider/')
	return response.data
}
