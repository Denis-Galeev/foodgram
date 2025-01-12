from pathlib import Path

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientSearchFilter, RecipeFilter
from api.pagination import FoodgramPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    SubscribeSerializer,
    TagSerializer,
    UserRecipeSerializer,
    UserSerializer,
)
from constants import (
    LINE_SPACING,
    PAGE_BOTTOM_MARGIN,
    PAGE_TOP,
    PAGE_WIDTH_MARGIN,
    TEXT_FONT_SIZE,
    TITLE_FONT_SIZE,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag,
)
from shortlinks.models import ShortLink
from users.models import Subscription


User = get_user_model()


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
        if 'avatar' not in request.data:
            return Response({'detail': 'Поле аватар обязательно.'},
                            status=HTTP_400_BAD_REQUEST)
        serializer = AvatarSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class RecipeViewSet(ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = RecipeFilter
    pagination_class = FoodgramPagination

    def get_queryset(self):
        """Оптимизация запроса."""
        return (super().get_queryset().prefetch_related(
            'tags', 'ingredients', 'author'))

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавить рецепт в список покупок."""
        recipe = self.get_object()
        user = request.user
        if recipe.shoppinglists.filter(user=user).exists():
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
        shopping_item = recipe.shoppinglists.filter(user=user).first()
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
        if recipe.favorites.filter(user=user).exists():
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
        favorite_item = recipe.favorites.filter(user=user).first()
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
            return Response(
                {'detail': 'Список покупок пуст.'},
                status=HTTP_400_BAD_REQUEST
            )

        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shoppinglists__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; filename="list.pdf"')
        pdf = canvas.Canvas(response)

        BASE_DIR = Path(__file__).resolve().parent.parent
        FONT_PATH = BASE_DIR / 'fonts' / 'DejaVuSans.ttf'
        pdfmetrics.registerFont(TTFont('DejaVuSans', str(FONT_PATH)))

        pdf.setFont('DejaVuSans', TITLE_FONT_SIZE)
        page_width = pdf._pagesize[0]
        title = 'Список покупок'
        title_width = pdf.stringWidth(title, 'DejaVuSans', TITLE_FONT_SIZE)
        pdf.drawString((page_width - title_width) / 2, PAGE_TOP, title)

        y = PAGE_TOP - LINE_SPACING * 2
        pdf.setFont('DejaVuSans', TEXT_FONT_SIZE)
        for idx, ingredient in enumerate(ingredients, start=1):
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['total_amount']
            line = f'{idx}. {name} — {amount} {unit}'
            pdf.drawString(PAGE_WIDTH_MARGIN, y, line)
            y -= LINE_SPACING
            if y < PAGE_BOTTOM_MARGIN:
                pdf.showPage()
                pdf.setFont('DejaVuSans', TEXT_FONT_SIZE)
                y = PAGE_TOP - LINE_SPACING
        pdf.save()
        return response

    @action(detail=True,
            methods=['get'],
            url_path='get-link',
            url_name='get-link',
            permission_classes=[IsAuthenticatedOrReadOnly])
    def get_link(self, request, pk=None):
        url = request.build_absolute_uri(f'/recipes/{pk}/')
        short_link, created = ShortLink.objects.get_or_create(original_url=url)
        base_url = request.build_absolute_uri('/s/').rstrip('/')
        return Response({'short-link': f'{base_url}/{short_link.short_code}'})


def redirect_to_recipe(request, code):
    """Перенаправление по короткой ссылке на оригинальный URL."""
    return redirect(get_object_or_404(ShortLink, short_code=code).original_url)
