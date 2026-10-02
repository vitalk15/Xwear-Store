import apiClient from '@/shared/api/apiClient'

export const fetchDocumentsData = async () => {
	const response = await apiClient.get('/core/documents/')
	return response.data
}
