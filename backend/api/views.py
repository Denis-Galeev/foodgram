from django.http import HttpResponse  # новый
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django_filters.rest_framework import (
    AllValuesMultipleFilter,
    BooleanFilter,
    CharFilter,
    DjangoFilterBackend,
    FilterSet,
    NumberFilter
)
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny,
    BasePermission,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS,
)
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST
)
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from reportlab.pdfgen import canvas  # новый

from api.models import Ingredient, Tag, Subscription, User, Recipe
from api.models import ShortLink, ShoppingList, Favorite, RecipeIngredient
from api.serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    SubscribeSerializer,
    TagSerializer,
    UserSerializer,
    UserRecipeSerializer,
)


class FoodgramPagination(PageNumberPagination):
    """Пагинация для проекта."""

    page_size_query_param = 'limit'


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


class RecipeFilter(FilterSet):  # новый
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


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для тегов"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter
    pagination_class = None


class UserViewSet(UserViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = FoodgramPagination
    lookup_field = 'id'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'put', 'delete')

    @action(
        detail=False, methods=['get', 'patch'], url_path='me',
        url_name='me', permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data,
                partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=HTTP_200_OK)

    @action(
        detail=True, methods=['post', 'delete'], url_path='subscribe',
        url_name='subscribe', permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        """Подписка на автора или отмена подписки."""
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data={'user': request.user.id, 'author': author.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            subscription = serializer.save()
            return Response(
                serializer.to_representation(subscription),
                status=HTTP_201_CREATED
            )
        try:
            subscription = Subscription.objects.get(
                user=request.user, author=author)
            subscription.delete()
            return Response(status=HTTP_204_NO_CONTENT)
        except Subscription.DoesNotExist:
            return Response(
                {'detail': 'Подписка не найдена.'}, status=HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False, methods=['get'], url_path='subscriptions',
        url_name='subscriptions', permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Получить список пользователей, на которых подписан пользователь."""
        subscriptions = User.objects.filter(author__user=request.user)
        paginator = self.pagination_class()
        authors = paginator.paginate_queryset(subscriptions, request,)
        serializer = UserRecipeSerializer(
            authors, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=False, methods=['put', 'delete'],
        url_path='me/avatar', permission_classes=(IsAuthenticated,)
    )
    def update_avatar(self, request):
        user = request.user
        if request.method == 'DELETE':
            user.avatar = None
            user.save()
            return Response(status=HTTP_204_NO_CONTENT)
        elif 'avatar' not in request.data:
            return Response({'detail': 'Поле аватар обязательно.'},
                            status=HTTP_400_BAD_REQUEST)
        serializer = AvatarSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class IsAuthorOrReadOnly(BasePermission):  # новое
    """
    Разрешение: Только автор может изменять или удалять рецепт.
    Другие пользователи могут только просматривать.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class RecipeViewSet(ModelViewSet):  # новое
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = RecipeFilter
    pagination_class = FoodgramPagination

    def get_queryset(self):
        """Оптимизация запроса."""
        queryset = super().get_queryset().prefetch_related(
            'tags',
            'ingredients',
            'author'
        )
        return queryset

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавить рецепт в список покупок."""
        recipe = self.get_object()
        user = request.user
        if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'detail': 'Рецепт уже в списке покупок.'},
                status=HTTP_400_BAD_REQUEST
            )
        ShoppingList.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, pk=None):
        """Удалить рецепт из списка покупок."""
        recipe = self.get_object()
        user = request.user
        shopping_item = ShoppingList.objects.filter(
            user=user,
            recipe=recipe
        ).first()
        if not shopping_item:
            return Response(
                {'detail': 'Рецепта нет в списке покупок.'},
                status=HTTP_400_BAD_REQUEST
            )
        shopping_item.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавить рецепт в избранное."""
        recipe = self.get_object()
        user = request.user
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'detail': 'Рецепт уже в избранном.'},
                status=HTTP_400_BAD_REQUEST
            )
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @favorite.mapping.delete
    def remove_favorite(self, request, pk=None):
        """Удалить рецепт из избранного."""
        recipe = self.get_object()
        user = request.user
        favorite_item = Favorite.objects.filter(
            user=user,
            recipe=recipe
        ).first()
        if not favorite_item:
            return Response(
                {'detail': 'Рецепта нет в избранном.'},
                status=HTTP_400_BAD_REQUEST
            )
        favorite_item.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачать список покупок в формате PDF."""
        user = request.user
        shopping_list = ShoppingList.objects.filter(user=user)
        if not shopping_list.exists():
            return Response({'detail': 'Список покупок пуст.'}, status=400)

        # Суммируем ингредиенты из всех рецептов пользователя
        ingredients = {}
        for item in shopping_list:
            recipe_ingredients = RecipeIngredient.objects.filter(
                recipe=item.recipe
            )
            for ingredient in recipe_ingredients:
                name = f"{ingredient.ingredient.name} ({ingredient.ingredient.measurement_unit})"
                amount = ingredient.amount
                if name in ingredients:
                    ingredients[name] += amount
                else:
                    ingredients[name] = amount

        # Создаем PDF-файл
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.pdf"'

        p = canvas.Canvas(response)
        p.setFont("Helvetica", 12)
        p.drawString(100, 800, "Список покупок:")

        y = 780
        for name, amount in ingredients.items():
            p.drawString(100, y, f"{name} — {amount}")
            y -= 20
            if y < 50:  # Если места на странице не хватает, добавляем новую
                p.showPage()
                p.setFont("Helvetica", 12)
                y = 800

        p.save()
        return response

    @action(detail=True,
            methods=['get'],
            url_path='get-link',
            url_name='get-link',
            permission_classes=[IsAuthenticatedOrReadOnly])
    def get_link(self, request, pk=None):
        """Получить короткую ссылку на рецепт."""
        recipe = self.get_object()  # Убедитесь, что объект существует
        short_link, created = ShortLink.objects.get_or_create(recipe=recipe)
        base_url = "https://foodgram.example.org/s/"
        return Response({"short-link": f"{base_url}{short_link.short_code}"})
