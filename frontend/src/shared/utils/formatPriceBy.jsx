/**
 * Форматирует числовое значение цены в удобный для чтения белорусский формат.
 * @param {number} price - Цена товара.
 * @param {string} [currency='BYN'] - Символ валюты (по умолчанию BYN). Текст BYN превратится в иконку знака если иконочный шрифт установлен). Второй вариант - HTML-код знака &#xe901; Третий вариант - использование псевдоэлемента в пустом теге <i class="nbrb-icon nbrb-icon-byn"></i>
 * @returns {JSX.Element | null} Отформатированная строка цены.
 */
export const formatPriceBy = (price, currency = 'BYN') => {
	if (price === null || price === undefined) return null

	const formatted = new Intl.NumberFormat('ru-RU').format(price)
	return (
		<>
			{formatted} <i className="nbrb-icon">{currency}</i>
		</>
	)
}
