/**
 * Преобразует строку "+375296525269" в читаемый формат "+375 (29) 652-52-69"
 */
export const formatBelarusPhone = (phone) => {
	if (!phone) return ''
	const cleaned = phone.replace(/\D/g, '') // Оставляем только цифры

	// Проверяем, что это белорусский номер (12 цифр)
	if (cleaned.length === 12 && cleaned.startsWith('375')) {
		const code = cleaned.slice(3, 5)
		const part1 = cleaned.slice(5, 8)
		const part2 = cleaned.slice(8, 10)
		const part3 = cleaned.slice(10, 12)
		return `+375 (${code}) ${part1}-${part2}-${part3}`
	}

	return phone // Возвращаем исходник, если формат непривычный
}
