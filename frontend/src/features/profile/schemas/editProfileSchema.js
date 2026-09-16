import { z } from 'zod'

// Регулярное выражение для белорусских номеров (+375 и коды 25, 29, 33, 44)
const belarusPhoneRegex = /^\+375(25|29|33|44)\d{7}$/

export const editProfileSchema = z.object({
	first_name: z.string().max(150, 'Имя слишком длинное').optional().or(z.literal('')),
	last_name: z.string().max(150, 'Фамилия слишком длинная').optional().or(z.literal('')),
	email: z.string().email(),
	phone: z
		.string()
		.optional()
		.or(z.literal(''))
		.refine(
			(val) => {
				if (!val) return true // Поле необязательное
				// Очищаем от пробелов, скобок и дефисов для проверки regex
				const cleaned = val.replace(/[\s()-]/g, '')
				return belarusPhoneRegex.test(cleaned)
			},
			{
				message: 'Формат: +375 25/29/33/44 XXXXXXX',
			},
		),
})
