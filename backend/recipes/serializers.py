import re
import webcolors

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from .models import (Tag, Recipe, Ingredient, RecipeIngredient,
                     Favorite,
                     ShoppingList)
from users.serializers import UserDetailSerializer


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

    def validate_color(self, value):
        try:
            value = webcolors.hex_to_name(value)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return value

    def validate_slug(self, value):
        if not re.match('^[-a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError('Некоректный slug')
        return value


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeChangeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов в рецепте."""

    id = serializers.IntegerField()
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'recipe', 'measurement_unit', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для представления ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeViewSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра списка рецептов."""

    author = UserDetailSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients')
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    def get_ingredients(self, obj):
        ingredient = RecipeIngredient.objects.filter(recipe=obj)
        serializer = RecipeIngredientSerializer(ingredient, many=True)
        return serializer.data

    def get_is_favorited(self, obj):
        return Recipe.is_favorited(obj, self.context['request'].user.id)

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user

        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(user=user, recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = RecipeChangeIngredientSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            recipe.tags.add(tag)

        recipe_ingredients = []
        for ingredient in ingredients:
            recipe_ingredients.append(RecipeIngredient(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, pk=ingredient['id']),
                amount=ingredient['amount']))
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get(
            'text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        if ingredients:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            recipe_ingredients = []
            for ingredient in ingredients:
                recipe_ingredients.append(RecipeIngredient(
                    recipe=instance,
                    ingredient=get_object_or_404(Ingredient,
                                                 pk=ingredient['id']),
                    amount=ingredient['amount']
                ))
            RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return instance

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализтор для списка избранного."""

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')


class RecipeSchemeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
