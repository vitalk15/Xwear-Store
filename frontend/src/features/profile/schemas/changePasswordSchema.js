import { z } from 'zod'

// Базовая схема для нового пароля
export const newPasswordValidation = z
	.string()
	.min(8, { message: 'Пароль должен содержать минимум 8 символов' })
	.regex(/^[a-zA-Z0-9!?$@#_.]+$/, {
		message: 'Допускаются только латинские буквы, цифры и определённые спецсимволы',
	})
	.regex(/[a-z]/, { message: 'Добавьте хотя бы одну строчную латинскую букву' })
	.regex(/[A-Z]/, { message: 'Добавьте хотя бы одну заглавную латинскую букву' })
	.regex(/\d/, { message: 'Добавьте хотя бы одну цифру' })
	.regex(/[!?$@#_.]/, { message: 'Добавьте хотя бы один спецсимвол (!?$@#_.)' })

// Базовая схема для текущего пароля
export const oldPasswordValidation = z
	.string()
	.min(1, { message: 'Введите текущий пароль' })
	.min(8, { message: 'Пароль должен содержать минимум 8 символов' })

// Схема смены пароля
export const changePasswordSchema = z
	.object({
		old_password: oldPasswordValidation,
		new_password: newPasswordValidation,
		new_password_confirm: z.string().min(1, 'Подтвердите новый пароль'),
	})
	.refine((data) => data.new_password === data.new_password_confirm, {
		message: 'Пароли не совпадают',
		path: ['new_password_confirm'],
	})
