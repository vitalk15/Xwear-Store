window.addEventListener('load', function () {
	const $ = django.jQuery

	function refreshBlocks() {
		$('tr').each(function () {
			const row = $(this)

			// 1. ПРОВЕРКА ДЛЯ ВАРИАНТОВ (Есть ли размеры)
			const sizeCell = row.find('.field-active_sizes_count')
			if (sizeCell.length) {
				// Извлекаем первое число из текста (например, "0 / 12" -> 0)
				const activeCount = parseInt(sizeCell.text().split('/')[0].trim())

				if (activeCount === 0) {
					row.addClass('no-active-sizes')
					// Снимаем чекбокс, если он был нажат
					row.find('.field-is_active input').prop('checked', false)
				} else {
					row.removeClass('no-active-sizes')
				}
			}

			// 2. ПРОВЕРКА ДЛЯ БАЗОВОГО ТОВАРА (Есть ли варианты/цвета)
			const variantCell = row.find('.field-variants_count')
			if (variantCell.length) {
				// Текст может быть просто "0" (если вариантов нет) или "3 ➔" (если есть ссылка)
				// parseInt("3 ➔") корректно вернет 3
				const variantCount = parseInt(variantCell.text().trim())

				if (variantCount === 0) {
					row.addClass('no-active-variants')
					// Снимаем чекбокс, если он был нажат
					row.find('.field-is_active input').prop('checked', false)
				} else {
					row.removeClass('no-active-variants')
				}
			}
		})
	}

	refreshBlocks()
})
