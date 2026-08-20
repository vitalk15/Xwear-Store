/**
 * Возвращает правильное склонение слова в зависимости от числа
 * @param {number} count - Число
 * @param {Array<string>} words - Массив из 3-х вариантов ['товар', 'товара', 'товаров']
 * @returns {string}
 */
export const getDeclension = (count, words) => {
	const value = Math.abs(count) % 100
	const num = value % 10

	if (value > 10 && value < 20) return words[2]
	if (num > 1 && num < 5) return words[1]
	if (num === 1) return words[0]

	return words[2]
}
