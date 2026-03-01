document.addEventListener('change', function (e) {
	// Проверяем, что изменилось поле цены или скидки внутри инлайна
	if (e.target.name.includes('price') || e.target.name.includes('discount_percent')) {
		const row = e.target.closest('tr') // Находим строку инлайна
		const priceInput = row.querySelector('[name$="-price"]')
		const discountInput = row.querySelector('[name$="-discount_percent"]')
		const finalPriceDisplay = row.querySelector(
			'.field-display_final_price p, .field-display_final_price div',
		)

		if (priceInput && discountInput && finalPriceDisplay) {
			const price = parseFloat(priceInput.value) || 0
			const discount = parseFloat(discountInput.value) || 0

			// Считаем итоговую цену (аналог нашей логики на Python)
			const final = Math.round(price * (1 - discount / 100))

			// Обновляем текст
			finalPriceDisplay.innerHTML = `<strong style="color: #d9534f;">${final} (превью)</strong>`
		}
	}
})
