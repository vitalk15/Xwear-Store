window.addEventListener('load', function () {
	const $ = django.jQuery

	function refreshBlocks() {
		$('tr').each(function () {
			const row = $(this)
			const checkboxCell = row.find('.field-is_active')
			const reasons = [] // Причины блокировки

			// 1. ПРОВЕРКА БАЗОВОГО ТОВАРА
			const productStatus = row.find('.product-status-data').text().trim()
			if (productStatus === 'inactive') {
				reasons.push('базовый товар выключен')
			}

			// 2. ПРОВЕРКА ДЛЯ ВАРИАНТОВ (Есть ли размеры)
			const sizeCell = row.find('.field-active_sizes_count')
			if (sizeCell.length) {
				// Извлекаем первое число из текста (например, "0 / 12" -> 0)
				const activeCount = parseInt(sizeCell.text().split('/')[0].trim())
				if (activeCount === 0) {
					reasons.push('нет активных размеров')
				}
			}

			// 3. ПРОВЕРКА ДЛЯ БАЗОВОГО ТОВАРА (Есть ли варианты/цвета)
			const variantCell = row.find('.field-variants_count')
			if (variantCell.length) {
				// Текст может быть просто "0" (если вариантов нет) или "3 ➔" (если есть ссылка)
				// parseInt("3 ➔") корректно вернет 3
				const variantCount = parseInt(variantCell.text().trim())
				if (variantCount === 0) {
					reasons.push('нет вариантов')
				}
			}

			// ЛОГИКА ОБЪЕДИНЕНИЯ
			if (reasons.length > 0) {
				row.addClass('is-blocked')

				// Формируем красивую строку: "Причина 1 + Причина 2"
				const fullMessage = 'Активация невозможна: ' + reasons.join(' и ')
				checkboxCell.attr('data-tooltip', fullMessage)

				// Блокируем чекбокс
				row.find('.field-is_active input').prop('checked', false)
			} else {
				row.removeClass('is-blocked')
				checkboxCell.removeAttr('data-tooltip')
			}
		})
	}

	refreshBlocks()
})
