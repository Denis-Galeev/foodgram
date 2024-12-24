from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import Tag
from recipes.serializers import TagSerializer


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет Тегов"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
