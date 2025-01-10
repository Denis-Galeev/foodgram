from django.contrib.admin import ModelAdmin, site
from django.contrib.admin.decorators import register
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.html import mark_safe

from constants import ADMIN_PER_PAGE
from users.models import Subscription


User = get_user_model()


@register(User)
class UsersAdmin(ModelAdmin):
    """Админка для модели пользователя"""

    def get_image(self, obj):
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" width="70" height="70">'
            )
        else:
            return '- нет аватарки -'

    get_image.short_description = 'Миниатюра'

    list_display = (
        'id', 'username', 'email', 'role', 'first_name',
        'last_name', 'avatar', 'get_image'
    )
    list_display_links = ('id', 'username', 'email')
    list_editable = ('role', 'avatar')
    list_filter = ('role', 'email')
    list_per_page = ADMIN_PER_PAGE
    search_fields = ('username', 'email', 'first_name', 'last_name')
    search_help_text = 'Поиск по username, email, имени и фамилии'


@register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ['user', 'author']
    search_fields = [
        'author__username',
        'author__email',
        'user__username',
        'user__email'
    ]
    list_filter = ['author__username', 'user__username']
    list_per_page = ADMIN_PER_PAGE


site.empty_value_display = '-- Не задано --'
site.unregister(Group)
