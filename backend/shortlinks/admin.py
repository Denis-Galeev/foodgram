from django.contrib.admin import ModelAdmin
from django.contrib.admin.decorators import register

from shortlinks.models import ShortLink


@register(ShortLink)
class ShortenerAdmin(ModelAdmin):
    """Админка Коротких ссылок"""
