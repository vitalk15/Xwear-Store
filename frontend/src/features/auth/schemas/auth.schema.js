import { z } from 'zod'

// --- Схемы валидации Zod ---

// Базовая схема для пароля
export const passwordValidation = z
	.string()
	.min(8, { message: 'Пароль должен содержать минимум 8 символов' })
	.regex(/^[a-zA-Z0-9!?$@#_.]+$/, {
		message: 'Допускаются только латинские буквы, цифры и определённые спецсимволы',
	})
	.regex(/[a-z]/, { message: 'Добавьте хотя бы одну строчную латинскую букву' })
	.regex(/[A-Z]/, { message: 'Добавьте хотя бы одну заглавную латинскую букву' })
	.regex(/\d/, { message: 'Добавьте хотя бы одну цифру' })
	.regex(/[!?$@#_.]/, { message: 'Добавьте хотя бы один спецсимвол (!?$@#_.)' })

// Базовая схема email
export const emailValidation = z
	.string()
	.trim()
	.toLowerCase()
	.min(1, { message: 'Введите email адрес' })
	.email({ message: 'Некорректный email адрес' })

// Схема логина
export const loginSchema = z.object({
	email: emailValidation,
	password: z.string().min(1, { message: 'Введите пароль' }), // Для логина достаточно просто проверить, что поле не пустое
	rememberMe: z.boolean().optional(),
})

// Схема регистрации
export const registerSchema = z
	.object({
		email: emailValidation,
		password: passwordValidation,
		confirmPassword: z.string(),
	})
	.refine((data) => data.password === data.confirmPassword, {
		message: 'Пароли не совпадают',
		path: ['confirmPassword'], // Ошибка будет привязана к этому полю
	})
