from pathlib import Path

from django_filters.rest_framework import (AllValuesMultipleFilter,
                                           BooleanFilter,
                                           CharFilter,
                                           DjangoFilterBackend,
                                           FilterSet,
                                           NumberFilter)

from django.http import HttpResponse

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny,
                                        BasePermission,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,
                                        SAFE_METHODS,)

from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)

from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from recipes.models import (Ingredient,
                            Tag,
                            Recipe,
                            ShoppingList,
                            Favorite,
                            RecipeIngredient)

from shortlinks.models import ShortLink

from recipes.serializers import (IngredientSerializer,
                                 RecipeSerializer,
                                 ShortRecipeSerializer,
                                 TagSerializer,)


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


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешение: Только автор может изменять или удалять рецепт.
    Другие пользователи могут только просматривать.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


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

        ingredients = {}
        for item in shopping_list:
            recipe_ingredients = RecipeIngredient.objects.filter(
                recipe=item.recipe
            )
            for ingredient in recipe_ingredients:
                key = ingredient.ingredient.name
                amount = ingredient.amount
                unit = ingredient.ingredient.measurement_unit
                if key in ingredients:
                    ingredients[key]['amount'] += amount
                else:
                    ingredients[key] = {
                        'amount': amount,
                        'unit': unit
                    }

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.pdf"'
        )
        p = canvas.Canvas(response)

        BASE_DIR = Path(__file__).resolve().parent.parent
        FONT_PATH = BASE_DIR / 'fonts' / 'DejaVuSans.ttf'
        pdfmetrics.registerFont(TTFont('DejaVuSans', str(FONT_PATH)))
        p.setFont('DejaVuSans', 16)

        page_width = p._pagesize[0]
        title = 'Список покупок'
        title_width = p.stringWidth(title, 'DejaVuSans', 16)
        p.drawString((page_width - title_width) / 2, 800, title)

        y = 760
        p.setFont('DejaVuSans', 14)
        for idx, (name, data) in enumerate(ingredients.items(), start=1):
            amount = data['amount']
            unit = data['unit']
            line = f'{idx}. {name}  —  {amount} {unit}'
            p.drawString(100, y, line)
            y -= 20
            if y < 50:
                p.showPage()
                p.setFont('DejaVuSans', 14)
                y = 800
        p.save()
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
