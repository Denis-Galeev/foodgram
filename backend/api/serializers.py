from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
    ValidationError
)
from rest_framework.validators import UniqueTogetherValidator

from api.models import (
    Ingredient,
    Recipe,
    ShortLink,
    Subscription,
    Tag,
    RecipeIngredient
)

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
        if value and not value.name.lower().endswith(
            ('.png', '.jpg', '.jpeg')
        ):
            raise ValidationError(
                'Загруженный файл не является корректным файлом.')
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
    name = SerializerMethodField()
    measurement_unit = SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


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
        return (not user.is_anonymous
                and obj.favorites.filter(user=user).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (not user.is_anonymous
                and obj.shoppinglists.filter(user=user).exists())

    def validate(self, data):
        """
        Объединённая валидация:
        - Проверка на пустоту: `tags`, `ingredients`, `cooking_time`, `image`.
        - Проверка уникальности: `tags`, `ingredients`.
        - Проверка существования ингредиентов.
        - Проверка на положительное значение: `amount` и `cooking_time`.
        """
        errors = {}

        def validate_not_empty(field, value, required=True):
            """Проверка, что поле не пустое."""
            if required and value is None:
                errors[field] = f'Поле `{field}` не может быть пустым.'

        def validate_unique(field, items):
            """Проверка, что элементы в поле уникальны."""
            if len(items) != len(set(items)):
                errors[field] = f'Элементы `{field}` должны быть уникальными.'

        def validate_positive(field, value):
            """Проверка, что значение больше нуля."""
            if value <= 0:
                errors[field] = f'Значение `{field}` должно быть больше 0.'

        def validate_ingredient_exists(id):
            """Проверка, что ингредиент существует."""
            if not Ingredient.objects.filter(id=id).exists():
                raise ValidationError(f'Ингредиент с id={id} не существует.')

        validate_not_empty('tags', data.get('tags'))
        validate_not_empty('ingredients', data.get('ingredients_in_recipe'))
        validate_not_empty('cooking_time', data.get('cooking_time'))
        validate_not_empty('image', data.get('image'),
                           required=not self.instance)

        tags = data.get('tags', [])
        validate_unique('tags', tags)
        ingredients = data.get('ingredients_in_recipe', [])
        validate_unique(
            'ingredients', [item['ingredient']['id'] for item in ingredients]
        )

        cooking_time = data.get('cooking_time')
        if cooking_time is not None:
            validate_positive('cooking_time', cooking_time)

        for item in ingredients:
            ingredient_id = item['ingredient']['id']
            validate_ingredient_exists(ingredient_id)
            validate_positive('amount', item['amount'])

        if errors:
            raise ValidationError(errors)
        return data

    def create_ingredients(self, recipe, data):
        RecipeIngredient.objects.bulk_create([RecipeIngredient(
            recipe=recipe,
            ingredient=Ingredient.objects.get(
                id=ingredient['ingredient']['id']),
            amount=ingredient['amount']
        ) for ingredient in data])

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients_in_recipe')
        tags_data = validated_data.pop('tags')
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients_in_recipe', None)
        tags = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        if tags:
            instance.tags.set(tags)
        if ingredients_data:
            instance.ingredients_in_recipe.all().delete()
            self.create_ingredients(instance, ingredients_data)
        return instance

    def to_representation(self, instance):
        """Переопределение для изменения представления поля `tags`."""
        rep = super().to_representation(instance)
        rep['tags'] = TagSerializer(instance.tags.all(), many=True).data
        return rep


class ShortLinkSerializer(ModelSerializer):
    """Сериализатор для короткой ссылки."""
    class Meta:
        model = ShortLink
        fields = ('original_url', 'short_code')
