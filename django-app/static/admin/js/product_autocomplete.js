window.addEventListener('load', function () {
	const $ = django.jQuery

	// Используем делегирование события на document,
	// чтобы скрипт работал даже если форма подгружается динамически
	$(document).on('select2:opening', function (e) {
		const targetId = e.target.id

		// Нас интересует только поле выбора базового товара
		if (targetId === 'id_base_product') {
			const selectElement = $(e.target)

			// Получаем доступ к конфигурации Select2
			const s2Instance = selectElement.data('select2')

			if (s2Instance && s2Instance.options.options.ajax) {
				// Переопределяем функцию формирования данных для отправки на сервер
				s2Instance.options.options.ajax.data = function (params) {
					return {
						term: params.term, // Текст, который менеджер вводит в поиск
						page: params.page, // Номер страницы (пагинация)
						field_name: 'base_product', // Маркер для Python-кода

						// Забираем актуальные значения из формы прямо в момент клика
						forward_brand: $('#id_brand').val(),
						forward_category: $('#id_category').val(),
						forward_model: $('#id_model_name').val(),
					}
				}
			}
		}
	})
})
