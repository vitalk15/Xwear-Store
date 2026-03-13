from django.core.validators import RegexValidator


# Валидатор номеров телефонов для Беларуси (+375XXXXXXXXX)
phone_regex = RegexValidator(
    regex=r"^\+375(25|29|33|44)\d{7}$",
    message="Номер должен быть в формате +375XXXXXXXXX (МТС, А1, life:).",
)
