from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField
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

    # def update(self, instance, validated_data):
    #     instance.avatar = validated_data.get('avatar', instance.avatar)
    #     instance.save()
    #     return instance


class UserRecipeSerializer(UserSerializer):
    """Сериплизатор представления рецептов пользователя"""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        read_only=True, source='recipes.count'
    )

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

    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='email',
        default=serializers.CurrentUserDefault(),
    )
    author = serializers.SlugRelatedField(
        slug_field='email',
        queryset=User.objects.all(),
    )

    class Meta:
        model = Subscription
        fields = ('author', 'user')
        validators = [UniqueTogetherValidator(
            queryset=model.objects.all(),
            fields=('author', 'user'),
            message='У вас уже есть подписка на этого пользователя',)
        ]

    def validate_author(self, author):
        if self.context['request'].user == author:
            raise serializers.ValidationError(
                'Подписаться на самого себя нельзя - это странно'
            )
        return author

    def to_representation(self, instance):
        return UserRecipeSerializer(instance.author, context=self.context).data
