from django.contrib.admin import ModelAdmin, site
from django.contrib.admin.decorators import register
from django.contrib.auth.models import Group

from api.models import Ingredient, Tag, User

PER_PAGE = 10


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


@register(Tag)
class TagAdmin(ModelAdmin):
    """Класс настройки раздела тегов."""

    list_display = (
        'pk',
        'name',
        'slug'
    )
    empty_value_display = 'значение отсутствует'
    list_filter = ('name',)
    list_per_page = PER_PAGE
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    """Класс настройки раздела ингредиентов."""

    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )
    empty_value_display = 'значение отсутствует'
    list_filter = ('name',)
    list_per_page = PER_PAGE
    search_fields = ('name',)


site.empty_value_display = '-- Не задано --'
site.unregister(Group)
