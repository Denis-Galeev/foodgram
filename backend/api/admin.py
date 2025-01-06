from django.contrib.admin import ModelAdmin, site
from django.contrib.admin.decorators import register
from django.contrib.auth.models import Group

from api.models import Ingredient, Tag, User, Recipe

PER_PAGE = 20


@register(User)
class UsersAdmin(ModelAdmin):
    """Админка для модели пользователя"""

    list_display = (
        'id', 'username', 'email', 'role', 'first_name', 'last_name', 'avatar'
    )
    list_display_links = ('id', 'username', 'email')
    list_editable = ('role', 'avatar')
    list_filter = ('role', 'email')
    list_per_page = PER_PAGE
    search_fields = ('username', 'email', 'first_name', 'last_name')
    search_help_text = 'Поиск по username, email, имени и фамилии'


@register(Tag)
class TagAdmin(ModelAdmin):
    """Админка для моделей тегов."""

    list_display = ('id', 'name', 'slug')
    list_editable = ('name', 'slug')
    list_filter = ('name',)
    list_per_page = PER_PAGE
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    """Админка для моделей ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    list_per_page = PER_PAGE
    search_fields = ('name',)


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    """Админка для моделей рецептов"""

    list_display = ('id', 'name', 'author',
                    'cooking_time', 'pub_date', 'image')
    list_display_links = ('name', 'author')
    list_editable = ('cooking_time', 'image')
    list_filter = ('tags',)
    list_per_page = PER_PAGE
    search_fields = ('name', 'author__username')
    search_help_text = 'Поиск по названию рецепта или `username` автора'


site.empty_value_display = '-- Не задано --'
site.unregister(Group)
