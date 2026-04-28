# Импортируем, чтобы декораторы @admin.register сработали
from .catalog import CategoryAdmin, BrandAdmin, ColorAdmin, SizeAdmin, MaterialAdmin
from .products import ProductAdmin, ProductVariantAdmin
from .marketing import SliderBannerAdmin, FavoriteAdmin
