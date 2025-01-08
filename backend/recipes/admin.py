from django.contrib.admin import ModelAdmin, site
from django.contrib.admin.decorators import register
from django.utils.html import format_html, mark_safe

from constants import ADMIN_PER_PAGE
from recipes.models import Ingredient, Tag, Recipe, Favorite, ShoppingList


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    """Админка для модели избранное"""

    list_display = ('user', 'recipe',)
    list_filter = ('user__username', 'recipe__name')
    search_fields = ('user__username', 'recipe__name')
    list_per_page = ADMIN_PER_PAGE


@register(ShoppingList)
class ShoppingListAdmin(ModelAdmin):
    """Админка для модели список покупок"""

    list_display = ('user', 'recipe',)
    list_filter = ('user__username', 'recipe__name')
    search_fields = ('user__username', 'recipe__name')
    list_per_page = ADMIN_PER_PAGE


@register(Tag)
class TagAdmin(ModelAdmin):
    """Админка для модели тегов."""

    list_display = ('id', 'name', 'slug')
    list_editable = ('name', 'slug')
    list_filter = ('name',)
    list_per_page = ADMIN_PER_PAGE
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    """Админка для моделей ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    list_per_page = ADMIN_PER_PAGE
    search_fields = ('name',)


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    """Админка для модели рецептов"""

    def favorite_count(self, obj):
        """Вывести количество добавлений рецепта в избранное."""
        count = Favorite.objects.filter(recipe=obj).count()
        return format_html(f'<b>{count}</b>')

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="100" height="70"')

    favorite_count.short_description = 'Добавлений в избранное'
    get_image.short_description = 'Миниатюра'

    list_display = ('id', 'name', 'author', 'cooking_time',
                    'favorite_count', 'image', 'get_image',)
    list_display_links = ('name', 'author')
    list_editable = ('cooking_time', 'image')
    list_filter = ('tags',)
    list_per_page = ADMIN_PER_PAGE
    search_fields = ('name', 'author__username')
    search_help_text = 'Поиск по названию рецепта или `username` автора'


site.empty_value_display = '-- Не задано --'
