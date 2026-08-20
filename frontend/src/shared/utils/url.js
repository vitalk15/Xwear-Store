/**
 * Преобразует любую внутреннюю ссылку (абсолютную или относительную) в pathname для React Router.
 * Если ссылка внешняя, возвращает null.
 */
export const getInternalPath = (url) => {
	if (!url) return null

	try {
		// Если ссылка относительная (начинается с '/')
		if (url.startsWith('/')) {
			return url
		}

		// Если ссылка абсолютная, парсим через URL
		const parsedUrl = new URL(url)

		// Проверяем, совпадает ли домен с текущим сайтом (localhost или рабочий домен)
		if (parsedUrl.origin === window.location.origin) {
			return parsedUrl.pathname + parsedUrl.search + parsedUrl.hash
		}

		// Внешняя ссылка
		return null
	} catch {
		// Если URL некорректный
		return null
	}
}
