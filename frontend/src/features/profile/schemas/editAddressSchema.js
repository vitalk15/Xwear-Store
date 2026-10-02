import { z } from 'zod'

export const editAddressSchema = z.object({
	city_id: z.coerce
		.number({ invalid_type_error: 'Выберите город из списка' })
		.min(1, 'Выберите город из списка'),
	street: z
		.string()
		.min(1, 'Укажите название улицы')
		.max(100, 'Название улицы слишком длинное'),
	house: z.string().min(1, 'Укажите номер дома').max(20, 'Номер дома слишком длинный'),
	apartment: z
		.string()
		.max(10, 'Номер квартиры слишком длинный')
		.optional()
		.or(z.literal('')),
})
