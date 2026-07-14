// Статический пункт меню "Информация", имитирует структуру данных от Django API
export const STATIC_INFO_MENU = {
	id: 'static-info',
	name: 'Информация',
	is_clickable: false, // Главный пункт не кликабелен, только открывает dropdown
	full_path: '',
	children: [
		{
			id: 'info-contacts',
			name: 'Контакты',
			full_path: 'contacts',
			is_clickable: true,
		},
		{
			id: 'info-delivery',
			name: 'Доставка и оплата',
			full_path: 'delivery', // Укажите здесь актуальный путь (например, 'info/delivery' или импортируйте из paths)
			is_clickable: true,
		},
		{
			id: 'info-legal',
			name: 'Юр. документы',
			full_path: 'legal-documents',
			is_clickable: true,
		},
	],
}
