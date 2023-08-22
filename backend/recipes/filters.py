import django_filters as filters
from django_filters.filters import ModelMultipleChoiceFilter

from .models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        method='is_favorited_method'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_method'
    )
    tags = ModelMultipleChoiceFilter(
        field_name='tagrecipe__tag__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def is_favorited_method(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(favorite__user=self.request.user)
        return Recipe.objects.all()

    def is_in_shopping_cart_method(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(shopping_cart__user=self.request.user)
        return Recipe.objects.all()
