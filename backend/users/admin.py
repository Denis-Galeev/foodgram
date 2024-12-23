from django.contrib.admin import ModelAdmin, site
from django.contrib.admin.decorators import register
from django.contrib.auth.models import Group

from users.models import User


@register(User)
class UsersAdmin(ModelAdmin):
    """Админка для модели пользователя"""

    list_display = (
        'id', 'username', 'email', 'role', 'first_name', 'last_name', 'avatar'
    )
    list_editable = ('role', 'avatar')
    list_display_links = ('id', 'username', 'email')
    list_filter = ('role', 'email')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    search_help_text = 'Поиск по username, email, имени и фамилии'


site.empty_value_display = '-- Не задано --'
site.unregister(Group)
