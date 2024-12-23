from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


@admin.register(User)
class UsersAdmin(UserAdmin):
    """Админка для пользователя"""

    list_display = ('id', 'username', 'email', 'role')
    search_fields = ('username', 'email')
    search_help_text = 'Поиск по `username` и `email`'
    list_display_links = ('id', 'username', 'email')
