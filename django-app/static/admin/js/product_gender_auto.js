window.addEventListener('load', function () {
	// 1. Проверяем, загрузился ли jQuery от Django
	if (typeof django === 'undefined' || typeof django.jQuery === 'undefined') {
		return
	}

	// 2. Безопасно присваиваем $
	const $ = django.jQuery

	// 3. Вешаем слушатель на событие Select2
	$(document).on('select2:select', '#id_category', function (e) {
		// Получаем текст выбранной категории и переводим в нижний регистр для надежности
		const selectedText = e.params.data.text.toLowerCase()
		const genderField = document.getElementById('id_gender')

		if (!genderField) return

		// 4. Логика автовыбора
		if (selectedText.includes('мужчинам')) {
			genderField.value = 'M'
		} else if (selectedText.includes('женщинам')) {
			genderField.value = 'F'
		}

		// Опционально: искусственно вызываем событие change,
		// чтобы админка поняла, что поле изменилось
		$(genderField).trigger('change')
	})
})
