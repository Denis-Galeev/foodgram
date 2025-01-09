from django.contrib.admin import ModelAdmin, site
from django.contrib.admin.decorators import register
from django.utils.html import format_html

from constants import ADMIN_PER_PAGE
from recipes.models import Recipe
from shortlinks.models import ShortLink


@register(ShortLink)
class ShortenerAdmin(ModelAdmin):
    """Админка Коротких ссылок."""

    list_display = ('id', 'original_url', 'short_code', 'recipe_name',
                    'recipe_image')
    list_per_page = ADMIN_PER_PAGE
    search_fields = ('original_url', 'recipe_name')

    def get_recipe(self, obj):
        """Получение объекта рецепта из original_url."""
        try:
            recipe_id = int(obj.original_url.rstrip('/').split('/')[-1])
            return Recipe.objects.get(id=recipe_id)
        except (ValueError, Recipe.DoesNotExist):
            return None

    def recipe_name(self, obj):
        """Отображение названия рецепта."""
        recipe = self.get_recipe(obj)
        if recipe:
            return recipe.name
        return '-- Не указано --'
    recipe_name.short_description = 'Название рецепта'

    def recipe_image(self, obj):
        """Отображение миниатюры изображения рецепта."""
        recipe = self.get_recipe(obj)
        if recipe and recipe.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: auto;" />',
                recipe.image.url
            )
        return '-- Нет изображения --'
    recipe_image.short_description = 'Изображение рецепта'


site.empty_value_display = '-- Не задано --'
