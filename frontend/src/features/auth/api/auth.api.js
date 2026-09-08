import apiClient from '@/shared/api/apiClient'

/**
 * Регистрация нового пользователя (создает неактивный аккаунт и отправляет письмо)
 * @param {Object} userData - Данные пользователя из формы
 * @param {string} userData.email - Email пользователя
 * @param {string} userData.password - Пароль
 * @param {string} [userData.confirmPassword] - Подтверждение пароля (если бэкенд его ожидает)
 * @returns {Promise<Object>} Ответ сервера { message, email }
 */
export const registerUser = async (userData) => {
	const { data } = await apiClient.post('/auth/register/', userData)
	return data
}

/**
 * Активация аккаунта пользователя (и одновременный логин)
 * @param {Object} payload - Данные для активации из URL
 * @param {string} payload.uid - Закодированный ID пользователя (uid_b64)
 * @param {string} payload.token - Токен для проверки (token)
 * @returns {Promise<Object>} Ответ сервера { message, user, access }
 */
export const activateUser = async (payload) => {
	const { data } = await apiClient.post('/auth/activate/', payload, {
		// Обязательный параметр для эндпоинтов, которые работают с HttpOnly cookies!
		// Без него браузер не сохранит cookie с refresh-токеном
		withCredentials: true,
	})

	return data
}

/**
 * Авторизация пользователя (Вход)
 * @param {Object} credentials - Данные для входа
 * @param {string} credentials.email - Email пользователя
 * @param {string} credentials.password - Пароль
 * @returns {Promise<Object>} Ответ сервера { user, access }
 */
export const loginUser = async (credentials) => {
	const { data } = await apiClient.post('/auth/token/', credentials, {
		// Обязательный параметр для эндпоинтов, которые работают с HttpOnly cookies!
		// Без него браузер не сохранит cookie с refresh-токеном
		withCredentials: true,
	})
	return data
}

/**
 * Выход пользователя (Удаляет HttpOnly cookie на стороне сервера)
 * @returns {Promise<Object>}
 */
export const logoutUser = async () => {
	const { data } = await apiClient.post('/auth/logout/', null, { withCredentials: true })
	return data
}

/**
 * Запрос ссылки для сброса пароля на email
 * @param {string} email
 * @returns {Promise<Object>}
 */
export const requestPasswordReset = async (email) => {
	const { data } = await apiClient.post('/auth/password-reset/', { email })
	return data
}

/**
 * Подтверждение сброса пароля по uid и token из ссылки
 * @param {Object} payload
 * @param {string} payload.uid
 * @param {string} payload.token
 * @param {string} payload.new_password
 * @param {string} payload.new_password_confirm
 * @returns {Promise<Object>}
 */
export const confirmPasswordReset = async ({
	uid,
	token,
	new_password,
	new_password_confirm,
}) => {
	const { data } = await apiClient.post(`/auth/password-reset/${uid}/${token}/`, {
		new_password,
		new_password_confirm,
	})
	return data
}
