import apiClient from '@/shared/api/apiClient'

export const fetchContactsData = async () => {
	const response = await apiClient.get('/core/contacts/')
	return response.data
}
