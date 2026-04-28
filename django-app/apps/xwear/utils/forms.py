# ВАЛИДАТОРЫ И АТРИБУТЫ ВИДЖЕТОВ ФОРМЫ


# Извлекает лимиты из ImageValidator и добавляет их в data-атрибуты виджета
def add_validator_attrs_to_widget(db_field, formfield):
    if not formfield:
        return formfield

    from ..validators import ImageValidator

    # Ищем наш валидатор ImageValidator среди всех валидаторов поля
    for v in db_field.validators:
        if isinstance(v, ImageValidator):
            # Прокидываем значения в атрибуты виджета
            formfield.widget.attrs.update(
                {
                    "data-min-width": v.min_width or 0,
                    "data-min-height": v.min_height or 0,
                    "data-max-mb": v.max_mb or 0,
                }
            )
            break
    return formfield
