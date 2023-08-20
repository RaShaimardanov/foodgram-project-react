from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response


from .models import User, Follow
from .serializers import UserSerializer, FollowSerializer
from recipes.pagination import CustomPagination


class CustomUserViewSet(UserViewSet):
    # permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = User.objects.all().order_by('-date_joined')
    pagination_class = CustomPagination

    @action(methods=['get', 'patch'], detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Выводит информацию о пользователе"""

        serializer = UserSerializer(
            request.user, context={'request': request})
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user,
                data=request.data,
                context={'request': request},
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Выводит информацию о подписках"""
        queryset = Follow.objects.filter(user=request.user)
        if queryset:
            pages = self.paginate_queryset(queryset)
            serializer = FollowSerializer(pages, many=True,
                                          context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response('У Вас нет подписок.',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=('post',),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        """Возможность подписаться на пользователя"""
        if id == 'me':
            return Response('На себя подписываться нельзя!',
                            status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        following = get_object_or_404(User, id=id)
        subscription = Follow.objects.filter(
            user=user.id, following=following.id
        )
        if user == following:
            return Response('На себя подписываться нельзя!',
                            status=status.HTTP_400_BAD_REQUEST)
        if subscription.exists():
            return Response(f'Вы уже подписаны на {following}',
                            status=status.HTTP_400_BAD_REQUEST)
        subscribe = Follow.objects.create(
            user=user,
            following=following
        )
        subscribe.save()
        return Response(f'Вы успешно подписались на пользователя {following}',
                        status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        """Возможность отписаться на пользователя"""
        user = request.user
        following = get_object_or_404(User, id=id)
        unsubscription = Follow.objects.filter(
            user=user.id, following=following.id
        )
        unsubscription.delete()
        return Response(f'Вы успешно отписались от пользователя {following}',
                        status=status.HTTP_204_NO_CONTENT)
