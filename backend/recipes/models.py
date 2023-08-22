from django.core.validators import MinValueValidator, MinLengthValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Модель, представляющая ингредиент для рецепта."""

    name = models.CharField(
        max_length=100, verbose_name='Название ингредиента',
        validators=[MinLengthValidator(1)],)
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f' {self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель, представляющая тег для категоризации рецептов."""

    name = models.CharField(
        max_length=50,
        verbose_name='Название тега',
        unique=True)
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет для тега')
    slug = models.SlugField(
        max_length=50,
        verbose_name='Слаг',
        unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color'],
                name='unique_tag'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель, представляющая рецепт для приготовления блюда."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE,)
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта')
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение рецепта',
        null=True,
        blank=True,)
    text = models.TextField(
        verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Список ингредиентов')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True,
        db_index=True,)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Модель, представляющая промежуточную таблицу.

    Для взаимосвязи количества ингредиентов с конкретным рецептом.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,)
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE,)
    amount = models.FloatField(
        verbose_name='Количество ингредиента',
        validators=(MinValueValidator(
            1, message='Минимальное количество ингредиентов 1'),))

    class Meta:
        verbose_name = 'RecipeIngredient'
        verbose_name_plural = 'RecipeIngredients'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='unique_recipe_ingredient')
        ]

    def __str__(self):
        return (f"{self.recipe.name} - {self.ingredient.name} - {self.amount}")


class Favorite(models.Model):
    """Модель, представляющая рецепт, добавленный в избранное пользователем."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite',
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное'


class ShoppingList(models.Model):
    """Модель, представляющая рецепт, добавленный в список покупок."""

    user = models.ForeignKey(
        User,
        related_name='shopping_cart',
        on_delete=models.CASCADE,)
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        on_delete=models.CASCADE,)

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_list',
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок'
