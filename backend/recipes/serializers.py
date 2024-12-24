from rest_framework.serializers import ModelSerializer

from recipes.models import Recipe, Tag


class TagSerializer(ModelSerializer):
    """Сериализатор для тегов"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class ShortRecipeSerializer(ModelSerializer):
    """Сериалайзер представления ответа укороченных данных о Рецепте"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
