import pxtorem from 'postcss-pxtorem'

export default {
	plugins: [
		pxtorem({
			rootValue: 16, // Базовый размер шрифта
			unitPrecision: 5, // Округление до 5 знаков после запятой
			propList: ['*'], // Конвертировать px во всех свойствах (font-size, padding, margin и т.д.)
			selectorBlackList: [], // Исключения (например, если какие-то классы нельзя трогать)
			replace: true, // Заменять px на rem (false — оставит и px, и rem для бэкапа)
			mediaQuery: false, // Конвертировать ли px внутри @media запросов
			minPixelValue: 2, // Все, что меньше или равно 2px (например, бордеры 1px), плагин не тронет
		}),
	],
}
