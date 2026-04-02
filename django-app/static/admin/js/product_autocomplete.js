window.addEventListener('load', function () {
	const $ = django.jQuery

	const fields = $('#id_brand, #id_category, #id_model_name')
	const baseProductSelect = $('#id_base_product')

	// 1. Перехват AJAX для ручного поиска (при клике по Select2)
	$.ajaxSetup({
		beforeSend: function (jqXHR, settings) {
			if (settings.url && settings.url.includes('field_name=base_product')) {
				const brand = $('#id_brand').val() || ''
				const category = $('#id_category').val() || ''
				const model = $('#id_model_name').val() || ''

				const params = `&forward_brand=${brand}&forward_category=${category}&forward_model=${encodeURIComponent(model)}`
				settings.url += params
			}
		},
	})

	// 2. Автоматический поиск при заполнении полей Бренд, Категория, Модель
	fields.on('change keyup', function () {
		const brand = $('#id_brand').val()
		const category = $('#id_category').val()
		const model = $('#id_model_name').val()

		// Если все три поля заполнены и введено хотя бы 3 символа в модель
		if (brand && category && model && model.length > 2) {
			$.getJSON(
				'/admin/autocomplete/',
				{
					app_label: 'xwear', // Проверьте, что app_label верный
					model_name: 'product',
					field_name: 'base_product',
					forward_brand: brand,
					forward_category: category,
					forward_model: model,
				},
				function (data) {
					// Если сервер нашел ровно один подходящий базовый товар
					if (data.results && data.results.length === 1) {
						const item = data.results[0]

						// Если в Select2 еще не выбран этот ID
						if (baseProductSelect.val() !== String(item.id)) {
							// Проверяем, нет ли уже такой опции в списке (если нет — создаем)
							if (
								baseProductSelect.find("option[value='" + item.id + "']").length === 0
							) {
								const newOption = new Option(item.text, item.id, true, true)
								baseProductSelect.append(newOption).trigger('change')
							} else {
								baseProductSelect.val(item.id).trigger('change')
							}
						}
					}
				},
			)
		}
	})
})
