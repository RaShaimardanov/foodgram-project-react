import django_filters
from rest_framework.filters import SearchFilter

from .models import Recipe
from users.models import User


class IngredientFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = django_filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)
