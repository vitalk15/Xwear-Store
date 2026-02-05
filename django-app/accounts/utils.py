from django.contrib.auth import get_user_model

User = get_user_model()


# проверка user_id + token_version из payload при извлечении пользователя при api-запросе
def jwt_get_user_id_from_payload_handler(payload):
    user_id = payload.get("user_id")
    token_version = payload.get("token_version")

    try:
        user = User.objects.get(id=user_id, token_version=token_version)
        return user
    except User.DoesNotExist:
        return None
