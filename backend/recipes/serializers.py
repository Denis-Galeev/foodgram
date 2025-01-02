from rest_framework.serializers import ModelSerializer, SerializerMethodField

from recipes.models import Ingredient, Recipe, Tag
from users.serializers import UserSerializer


class TagSerializer(ModelSerializer):
    """Сериализатор для тегов"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(ModelSerializer):
    """Сериализатор для ингредиентов """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ShortRecipeSerializer(ModelSerializer):
    """Сериалайзер представления укороченных данных о рецепте"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerilizer(ModelSerializer):
    """Сериалайзер для рецептов"""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingrediens = ''
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, object):
        pass

    def get_is_in_shopping_cart(self, object):
        pass
