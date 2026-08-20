/**
 * Форматирует числовое значение цены в удобный для чтения российский формат.
 * @param {number} price - Цена товара.
 * @param {string} [currency='₽'] - Символ валюты (по умолчанию ₽).
 * @returns {string} Отформатированная строка цены.
 */
export const formatPriceRu = (price, currency = ' ₽') => {
	if (price === null || price === undefined) return ''

	const formatted = new Intl.NumberFormat('ru-RU').format(price)
	return `${formatted}${currency}`
}
