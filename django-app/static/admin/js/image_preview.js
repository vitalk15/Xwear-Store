window.addEventListener('load', function () {
	const $ = django.jQuery

	// Функция для отрисовки превью
	const showPreview = (input) => {
		if (input.files && input.files[0]) {
			const reader = new FileReader()

			reader.onload = function (e) {
				// Ищем, есть ли уже превью рядом с инпутом
				let imgContainer = input
					.closest('.form-row')
					.querySelector('.live-preview-container')

				// Если контейнера нет — создаем его
				if (!imgContainer) {
					imgContainer = document.createElement('div')
					imgContainer.className = 'live-preview-container'
					imgContainer.style.marginTop = '10px'
					// Вставляем после инпута
					input.parentNode.appendChild(imgContainer)
				}

				// Рисуем само изображение (стили как в утилите get_admin_thumb)
				imgContainer.innerHTML = `
				    <div style="margin-bottom: 5px; font-size: 11px; color: #666;">Предпросмотр:</div>
				    <img src="${e.target.result}"
				          style="width: 80px; height: auto; object-fit: cover; object-position: center; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.2); border: 2px solid #79aec8;" />
				`
			}
			reader.readAsDataURL(input.files[0])
		}
	}

	// Делегирование события на весь документ (подходит для инлайнов)
	$(document).on('change', 'input[type="file"]', function () {
		showPreview(this)
	})

	// Обработка динамических инлайнов Django
	$(document).on('formset:added', function (event, $row, formsetName) {
		// Очищаем контейнер превью, если он вдруг скопировался
		const oldPreview = $row[0].querySelector('.live-preview-container')
		if (oldPreview) oldPreview.remove()
	})
})
