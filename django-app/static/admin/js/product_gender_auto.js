// document.addEventListener('DOMContentLoaded', function () {
// 	// Находим элементы по ID, которые Django генерирует стандартно
// 	const categoryField = document.getElementById('id_category')
// 	const genderField = document.getElementById('id_gender')

// 	if (!categoryField || !genderField) return

// 	// Функция для обновления пола
// 	const updateGender = (text) => {
// 		if (!text) return

// 		// Логика поиска ключевых слов в строке
// 		if (text.includes('Мужчинам')) {
// 			genderField.value = 'M'
// 		} else if (text.includes('Женщинам')) {
// 			genderField.value = 'F'
// 		}
// 	}

// 	// 1. Обработка стандартного select
// 	categoryField.addEventListener('change', function () {
// 		const selectedOption = this.options[this.selectedIndex]
// 		updateGender(selectedOption.text)
// 	})

// 	// 2. Поддержка Select2 (autocomplete_fields)
// 	// Select2 — это jQuery-плагин, и он генерирует свои события.
// 	// Чтобы поймать выбор в autocomplete на чистом JS,
// 	// мы используем всплытие события 'change'.
// 	categoryField.addEventListener('change', (e) => {
// 		// В Select2 при выборе программно вызывается событие change
// 		const selectedOption = categoryField.options[categoryField.selectedIndex]
// 		if (selectedOption) {
// 			updateGender(selectedOption.text)
// 		}
// 	})
// })

// document.addEventListener('DOMContentLoaded', function () {
// 	console.log('Скрипт автовыбора пола загружен')

// 	const categoryField = document.getElementById('id_category')
// 	const genderField = document.getElementById('id_gender')

// 	if (!categoryField || !genderField) {
// 		console.error('Поля не найдены! Проверь ID: id_category и id_gender')
// 		return
// 	}

// 	const updateGender = (text) => {
// 		console.log('Выбрана категория с текстом:', text)

// 		if (text.includes('Мужчинам')) {
// 			genderField.value = 'M'
// 			console.log('Установлен пол: Мужской')
// 		} else if (text.includes('Женщинам')) {
// 			genderField.value = 'F'
// 			console.log('Установлен пол: Женский')
// 		}
// 	}

// 	// Слушаем изменения
// 	categoryField.addEventListener('change', function () {
// 		const selectedOption = this.options[this.selectedIndex]
// 		if (selectedOption) {
// 			updateGender(selectedOption.text)
// 		}
// 	})

// 	// Специальный хак для Select2 (autocomplete_fields)
// 	// Поскольку Select2 — это jQuery плагин, он не всегда пробрасывает нативные события
// 	// Мы подпишемся на его внутреннее событие через глобальный jQuery админки,
// 	// если он доступен, но оставим логику на чистом JS
// 	if (window.jQuery) {
// 		window.jQuery(categoryField).on('select2:select', function (e) {
// 			const data = e.params.data
// 			updateGender(data.text)
// 		})
// 	}
// })

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
