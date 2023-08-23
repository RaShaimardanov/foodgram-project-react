from django.core.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Recipe
from recipes.serializers import RecipeSchemeSerializer
from .models import Follow, User


class UserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    def validate_username(self, value):
        """
        Проверяет, что имя пользователя уникально и не равно 'me'.
        """
        if User.objects.filter(username__iexact=value).exists():
            raise ValidationError('Имя пользователя уже используется.')
        if value.casefold() == 'me':
            raise ValidationError('Имя пользователя не может быть "me".')
        return value

    def validate_email(self, value):
        """Проверка уникальности электронной почты."""

        if User.objects.filter(email__iexact=value).exists():
            raise ValidationError(
                'Этот адрес электронной почты уже используется.')
        return value.lower()

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password')


class UserSerializer(UserSerializer):
    """Сериализатор для пользователя."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user

        if user.is_anonymous:
            return False

        return Follow.objects.filter(user=user, following=obj).exists()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed')


class FollowSerializer(UserSerializer):
    id = serializers.ReadOnlyField(source='following.id')
    email = serializers.ReadOnlyField(source='following.email')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user,
            following=obj.following
        ).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.following.id)
        serializer = RecipeSchemeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.following.id).count()

    class Meta:
        model = Follow
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count']
