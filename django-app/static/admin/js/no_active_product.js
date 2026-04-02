window.addEventListener('load', function () {
	const $ = django.jQuery

	function refreshSizeBlocks() {
		$('tr').each(function () {
			const sizeCell = $(this).find('.field-active_sizes_count')
			if (sizeCell.length) {
				// Извлекаем первое число из текста (например, "0 / 12" -> 0)
				const activeCount = parseInt(sizeCell.text().split('/')[0].trim())

				if (activeCount === 0) {
					$(this).addClass('no-active-sizes')
					// Снимаем чекбокс, если он вдруг был нажат
					$(this).find('.field-is_active input').prop('checked', false)
				} else {
					$(this).removeClass('no-active-sizes')
				}
			}
		})
	}

	refreshSizeBlocks()

	// Если у вас динамическое обновление (например, через AJAX),
	// можно запускать refreshSizeBlocks после изменений.
})
