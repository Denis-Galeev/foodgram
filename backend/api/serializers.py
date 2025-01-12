from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    CharField,
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
    ValidationError,
)
from rest_framework.validators import UniqueTogetherValidator

from constants import (
    DEFAULT_MAX_AMOUNT,
    DEFAULT_MAX_VALUE,
    DEFAULT_MIN_VALUE,
    EMPTY_FIELDS,
    FORBIDDEN_FILE,
    MAX_TIME_MSG,
    MESSAGE_AMOUNT,
    MIN_TIME_MSG,
    RESOLVED_TYPE,
    UNIQUE_FIELDS,
)
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from shortlinks.models import ShortLink
from users.models import Subscription


User = get_user_model()


class TagSerializer(ModelSerializer):
    """Сериализатор для тегов"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(ModelSerializer):
    """Сериализатор для Ингредиентов """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ShortRecipeSerializer(ModelSerializer):
    """Сериализатор для краткой информации о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(ModelSerializer):
    """Сериализатор для кастомной модели User."""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        return getattr(obj, 'is_subscribed', False)


class AvatarSerializer(ModelSerializer):
    """Сериализатор для аватарки / фотографии пользователя"""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate_avatar(self, value):
        if value and not value.name.lower().endswith(RESOLVED_TYPE):
            raise ValidationError(FORBIDDEN_FILE)
        return value


class UserRecipeSerializer(UserSerializer):
    """Сериализатор представления рецептов пользователя"""

    recipes = SerializerMethodField()
    recipes_count = IntegerField(read_only=True, source='recipes.count')

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        try:
            recipes_limit = int(request.query_params.get('recipes_limit'))
        except (ValueError, TypeError):
            pass
        else:
            recipes = recipes[:recipes_limit]
        return ShortRecipeSerializer(recipes, many=True).data


class SubscribeSerializer(ModelSerializer):
    """Сериализатор для подписок"""

    class Meta:
        model = Subscription
        fields = ('author', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='У вас уже есть подписка на этого пользователя',
            )
        ]

    def validate_author(self, author):
        """Запрет подписки на самого себя."""
        if self.context['request'].user == author:
            raise ValidationError('Подписаться на самого себя нельзя.')
        return author

    def to_representation(self, instance):
        """Форматирование данных для ответа."""
        return UserRecipeSerializer(instance.author, context=self.context).data


class RecipeIngredientSerializer(ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""
    id = IntegerField(source='ingredient.id')
    name = CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = IntegerField(
        validators=(
            MinValueValidator(DEFAULT_MIN_VALUE, MESSAGE_AMOUNT),
            MaxValueValidator(DEFAULT_MAX_AMOUNT, MESSAGE_AMOUNT),
        ),
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(ModelSerializer):
    """Сериализатор для рецептов."""
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='ingredients_in_recipe'
    )
    author = SerializerMethodField(read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()
    cooking_time = IntegerField(
        validators=(
            MinValueValidator(DEFAULT_MIN_VALUE, MIN_TIME_MSG),
            MaxValueValidator(DEFAULT_MAX_VALUE, MAX_TIME_MSG),
        ),
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_author(self, obj):
        return UserSerializer(obj.author, context=self.context).data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            not user.is_anonymous
            and obj.favorites.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            not user.is_anonymous
            and obj.shoppinglists.filter(user=user).exists()
        )

    def validate_tags(self, value):
        if not value:
            raise ValidationError(EMPTY_FIELDS[0])
        if len(set(value)) != len(value):
            raise ValidationError(UNIQUE_FIELDS[3])
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError(EMPTY_FIELDS[1])
        unique_ids = set()
        for item in value:
            ingredient = item['ingredient']
            id = ingredient['id']
            if not Ingredient.objects.filter(id=id).exists():
                raise ValidationError(f'Ингредиент с id={id} не существует.')
            if id in unique_ids:
                raise ValidationError(UNIQUE_FIELDS[2])
            unique_ids.add(id)
        return value

    def validate_image(self, value):
        """Проверка изображения."""
        if value == '' or value is None:
            raise ValidationError(EMPTY_FIELDS[2])
        return value

    def create_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(
                    id=ingredient['ingredient']['id']
                ),
                amount=ingredient['amount']
            ) for ingredient in ingredients_data
        ])

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients_in_recipe')
        tags_data = validated_data.pop('tags')
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('ingredients_in_recipe', None)
        if not ingredients_data:
            raise ValidationError({'ingredients': EMPTY_FIELDS[1]})
        if not tags:
            raise ValidationError({'tags': EMPTY_FIELDS[0]})
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.ingredients_in_recipe.all().delete()
        self.create_ingredients(instance, ingredients_data)
        return instance

    def to_representation(self, instance):
        """Переопределение для изменения представления поля `tags`."""
        represent = super().to_representation(instance)
        represent['tags'] = TagSerializer(instance.tags.all(), many=True).data
        return represent


class ShortLinkSerializer(ModelSerializer):
    """Сериализатор для короткой ссылки."""
    class Meta:
        model = ShortLink
        fields = ('original_url', 'short_code')
