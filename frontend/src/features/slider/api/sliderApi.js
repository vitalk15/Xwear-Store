import { apiClient } from '@/api/client'

export const fetchSliderData = async () => {
	const response = await apiClient.get('/shop/slider/')
	return response.data
}
