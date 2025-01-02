from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    IntegerField, ModelSerializer, SerializerMethodField,
    ValidationError
)
from rest_framework.validators import UniqueTogetherValidator

from recipes.serializers import ShortRecipeSerializer
from users.models import Subscription

User = get_user_model()


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
        """Проверяет, подписан ли текущий пользователь на этого автора."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False


class AvatarSerializer(ModelSerializer):
    """Сериализатор для аватарки / фотографии пользователя"""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


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
