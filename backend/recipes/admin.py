from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from . import models


class IngredientResource(resources.ModelResource):
    """Модель предназначена для импорта ингредиентов в админке"""
    class Meta:
        model = models.Ingredient
        import_id_fields = ('name',)
        report_skipped = True


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Модель предназначена для отображения модели рецептов в админке"""
    list_display = ('id', 'name', 'author')
    list_display_links = ('id', 'name', 'author')


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    """Модель предназначена для отображения модели тегов в админке"""
    list_display = ('id', 'name', 'color', 'slug')
    list_display_links = ('id', 'name', 'color', 'slug')


@admin.register(models.Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    """Модель предназначена для отображения модели ингредиентов в админке"""
    resource_classes = (IngredientResource)
    list_display = ('id', 'name', 'measurement_unit')
    list_display_links = ('id', 'name', 'measurement_unit')


@admin.register(models.RecipeIngredient)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """Модель предназначена для отображения связывающей
       модели ингредиентов и рецептов в админке"""
    list_display = ('id', 'recipe', 'amount')
    list_display_links = ('id', 'recipe', 'amount')


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Модель предназначена для отображения модели избранного в админке"""
    list_display = ('id', 'user', 'recipe')
    list_display_links = ('id', 'user', 'recipe')


@admin.register(models.ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Модель предназначена для отображения
       модели списка покупок в админ панели"""
    list_display = ('id', 'user', 'recipe')
    list_display_links = ('id', 'user', 'recipe')
