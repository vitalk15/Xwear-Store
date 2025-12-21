import os
from uuid import uuid4
from .models import Product


# изменение имени изображения товара
def rename_prod(instance, filename):
    upload_to = "products"
    ext = filename.split(".")[-1]
    rec = Product.objects.all()

    # получаем id последней записи
    if len(rec) == 0:
        max_rec = 0
    else:
        max_rec = rec.last().id

    max_id = max_rec + 1  # id следующей записи
    photo = f"prod_{max_id}"

    if instance.pk:
        filename = f"prod_{instance.pk}.{ext}"
    elif photo:
        filename = f"{photo}.{ext}"
    else:
        filename = f"prod_{uuid4().hex}.{ext}"

    return os.path.join(upload_to, filename)
