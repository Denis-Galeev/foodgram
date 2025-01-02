from django.contrib import admin

from recipes.models import Ingredient, Tag

PER_PAGE = 10


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
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


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
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
