window.addEventListener('load', function () {
	const $ = django.jQuery

	// Функция для отрисовки превью
	const showPreview = (input) => {
		if (input.files && input.files[0]) {
			const file = input.files[0]
			// Считываем лимиты из атрибутов (преобразуем в числа)
			const limits = {
				width: parseInt(input.dataset.minWidth) || 0,
				height: parseInt(input.dataset.minHeight) || 0,
				size: parseFloat(input.dataset.maxMb) || 0,
			}

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
					// imgContainer.style.cssText =
					// 	'margin-top: 10px; padding: 8px; background: #f8f9fa; border-radius: 4px; border: 1px dashed #79aec8; display: inline-block;'
					imgContainer.style.marginTop = '10px'
					// Вставляем после инпута
					input.parentNode.appendChild(imgContainer)
				}

				// Создаем временный объект изображения для получения разрешения
				const tempImg = new Image()
				tempImg.src = e.target.result
				tempImg.onload = function () {
					const fileSizeMb = file.size / (1024 * 1024)

					// Проверки для подсветки
					const isWidthBad = limits.width && this.width < limits.width
					const isHeightBad = limits.height && this.height < limits.height
					const isSizeBad = limits.size && fileSizeMb > limits.size

					imgContainer.innerHTML = `
                <div style="font-size: 11px; font-weight: bold; color: #444; margin-bottom: 5px;">Предпросмотр:</div>
                <img src="${e.target.result}" style="width: 160px; height: auto; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.2); ${isWidthBad || isHeightBad || isSizeBad ? 'border: 2px solid #ba2121;' : 'border: 2px solid #79aec8;'}" />
                <div style="font-size: 10px; margin-top: 5px; line-height: 1.4; color: #666">
                    <span style="color: ${isWidthBad ? '#ba2121' : 'inherit'}; font-weight: ${isWidthBad ? 'bold' : 'normal'}">
                        📏 ${this.width}
                    </span>x
                    <span style="color: ${isHeightBad ? '#ba2121' : 'inherit'}; font-weight: ${isHeightBad ? 'bold' : 'normal'}">
                        ${this.height}
                    </span> px<br>
                    <span style="color: ${isSizeBad ? '#ba2121' : 'inherit'}; font-weight: ${isSizeBad ? 'bold' : 'normal'}">
                        💾 ${fileSizeMb.toFixed(2)} MB
                    </span>
                </div>
            `
				}
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
