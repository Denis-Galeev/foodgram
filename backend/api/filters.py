from django_filters.rest_framework import (
    AllValuesMultipleFilter, BooleanFilter, CharFilter, FilterSet, NumberFilter
)

from api.models import Ingredient, Recipe


class IngredientSearchFilter(FilterSet):
    """
    Фильтр для вьюсета ингредиентов.
    Ищет ингредиенты по полю name регистронезависимо,
    по вхождению в начало названия
    """

    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(FilterSet):
    """
    Кастомный фильтр для рецептов.
    Доступна фильтрация по избранному, автору, списку покупок и тегам.
    """

    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    author = NumberFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'tags', 'author']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset.none() if value else queryset
        if value:
            return queryset.filter(favorites__user=user)
        return queryset.exclude(favorites__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return queryset.none() if value else queryset
        if value:
            return queryset.filter(shoppinglists__user=user)
        return queryset.exclude(shoppinglists__user=user)
