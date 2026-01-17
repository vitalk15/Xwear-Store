from django.contrib.auth import get_user_model
from easy_thumbnails.files import get_thumbnailer

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


# получение данных миниатюр
def get_thumbnail_data(image_field, alias, request):
    if not image_field:
        return None
    thumbnailer = get_thumbnailer(image_field)
    thumb = thumbnailer.get_thumbnail({"alias": alias})
    return {
        "url": request.build_absolute_uri(thumb.url),
        "width": thumb.width,
        "height": thumb.height,
    }
