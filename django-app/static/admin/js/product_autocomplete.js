// window.addEventListener('load', function () {
// 	const $ = django.jQuery

// 	// Используем делегирование события на document,
// 	// чтобы скрипт работал даже если форма подгружается динамически
// 	$(document).on('select2:opening', function (e) {
// 		const targetId = e.target.id

// 		// Нас интересует только поле выбора базового товара
// 		if (targetId === 'id_base_product') {
// 			const selectElement = $(e.target)

// 			// Получаем доступ к конфигурации Select2
// 			const s2Instance = selectElement.data('select2')

// 			if (s2Instance && s2Instance.options.options.ajax) {
// 				// Переопределяем функцию формирования данных для отправки на сервер
// 				s2Instance.options.options.ajax.data = function (params) {
// 					return {
// 						term: params.term, // Текст, который менеджер вводит в поиск
// 						page: params.page, // Номер страницы (пагинация)
// 						field_name: 'base_product', // Маркер для Python-кода

// 						// Забираем актуальные значения из формы прямо в момент клика
// 						forward_brand: $('#id_brand').val(),
// 						forward_category: $('#id_category').val(),
// 						forward_model: $('#id_model_name').val(),
// 					}
// 				}
// 			}
// 		}
// 	})
// })
;(function () {
	'use strict'

	// Функция инициализации, которая принимает jQuery как параметр $
	function initAutocomplete($) {
		const fields = $('#id_brand, #id_category, #id_model_name')
		const baseProductSelect = $('#id_base_product')

		// 1. Перехват AJAX для ручного поиска
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

		// 2. Автоматический поиск при заполнении полей
		fields.on('change keyup', function () {
			const brand = $('#id_brand').val()
			const category = $('#id_category').val()
			const model = $('#id_model_name').val()

			// Ищем, только если заполнены все три поля и модель длиннее 2 символов
			if (brand && category && model && model.length > 2) {
				$.getJSON(
					'/admin/autocomplete/',
					{
						app_label: 'xwear', // Проверьте, что имя приложения совпадает
						model_name: 'product',
						field_name: 'base_product',
						forward_brand: brand,
						forward_category: category,
						forward_model: model,
					},
					function (data) {
						if (data.results && data.results.length === 1) {
							const item = data.results[0]

							// Если в Select2 еще не выбран этот ID
							if (baseProductSelect.val() !== String(item.id)) {
								// Создаем опцию, если её нет, и выбираем её
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
	}

	// Ожидание появления django.jQuery
	var checkTimer = setInterval(function () {
		if (window.django && window.django.jQuery) {
			clearInterval(checkTimer)
			// ПЕРЕДАЕМ jQuery в функцию
			initAutocomplete(window.django.jQuery)
		}
	}, 100)
})()
