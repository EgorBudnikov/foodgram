"""Вьюхи для работы с пользователями.

Содержит ViewSet для пользователей и функции для:
- получения/удаления токена
- смены пароля
- управления аватаром
- подписок на авторов
"""
from rest_framework import permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from users.models import User
from users.serializers import (
    AvatarSerializer,
    PasswordSerializers,
    TokenSerializer,
    UserDetailSerializer,
    UserSerializer,
    UserSubscribeSerializer,
    UserSubscriptionSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для получения общедоступных данных."""

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от запроса."""
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer

    @action(
        detail=False, methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """Получение своего профиля."""
        serializer = UserDetailSerializer(
            instance=request.user, context={'request': request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Добавление и удаление аватара."""
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            return Response({'avatar': serializer.save(user, request)})

        else:
            if user.avatar:
                user.avatar.delete()
            return Response(status=204)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        """Получение своих подписок."""
        recipes_limit = int(request.query_params.get('recipes_limit', 3))
        queryset = request.user.following.all()
        page = self.paginate_queryset(queryset)

        serializer = UserSubscriptionSerializer(
            page, many=True,
            context={'request': request, 'recipes_limit': recipes_limit}
        )

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='subscribe')
    def subscribe(self, request, pk=None):
        """Обработка подписок и отписок на пользователей."""
        recipes_limit = int(request.query_params.get('recipes_limit', 3))
        user_for_sub = get_object_or_404(User, pk=pk)
        user = request.user
        if request.method == 'POST':
            if user_for_sub == user:
                return Response(
                    'Вы не можете подписаться на самого себя!', status=400)
            elif user.following.filter(pk=pk).exists():
                return Response('Вы уже подписаны!', status=400)
            else:
                user.following.add(user_for_sub)

            serializer = UserSubscribeSerializer(
                instance=user_for_sub,
                context={'request': request,
                         'recipes_limit': recipes_limit}
            )
            return Response(serializer.data, status=201)
        else:
            if user.following.filter(pk=pk).exists():
                user.following.remove(user_for_sub)
            else:
                return Response(
                    'Вы не подписаны на этого пользователя.', status=400
                )
            return Response(status=204)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def token_obtain(request):
    """Функция для получения токена."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    return Response({'auth_token': str(serializer.save())})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def token_delete(request):
    """Удаление токена."""
    request.user.auth_token.delete()
    return Response(status=204)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Функция для смены пароля."""
    serializers = PasswordSerializers(
        data=request.data, context={'request': request})
    serializers.is_valid(raise_exception=True)
    serializers.save()
    return Response(status=204)
