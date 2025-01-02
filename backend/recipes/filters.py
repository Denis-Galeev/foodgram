from django_filters.rest_framework import FilterSet, CharFilter

from recipes.models import Ingredient


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
