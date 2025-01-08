from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK,
                                   HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)

from users.models import Subscription
from users.serializers import (AvatarSerializer,
                               SubscribeSerializer,
                               UserRecipeSerializer,
                               UserSerializer)

User = get_user_model()


class FoodgramPagination(PageNumberPagination):
    page_size_query_param = 'limit'


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
