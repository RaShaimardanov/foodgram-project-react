from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from .pagination import CustomPagination
from .filters import IngredientFilter, RecipeFilter
from .models import (Tag, Recipe, Ingredient, Favorite,
                     ShoppingList, RecipeIngredient)
from .serializers import (TagSerializer, RecipeSerializer,
                          IngredientSerializer, RecipeViewSerializer,
                          RecipeSchemeSerializer)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None

    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Tag, pk=pk)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return RecipeSerializer
        return RecipeViewSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'massage': 'Рецепт успешно удален'},
            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self._add(Favorite, request.user, pk)
        else:
            return self._delete(Favorite, request.user, pk)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self._add(ShoppingList, request.user, pk)
        else:
            return self._delete(ShoppingList, request.user, pk)

    @action(detail=False, methods=["get"],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        cart = request.user.shopping_cart.all()
        filename = "shop_list.txt"
        shop_list = {}

        for item in cart:
            ingredients = RecipeIngredient.objects.filter(recipe=item.recipe)
            for ingredient in ingredients:
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                amount = ingredient.amount

                if name not in shop_list:
                    shop_list[name] = {
                        'amount': amount,
                        'measurement_unit': measurement_unit,
                    }
                else:
                    shop_list[name]['amount'] = (shop_list[name]['amount']
                                                 + amount)

        download_list = []
        for item in shop_list:
            download_list.append(f'{item} - '
                                 f'{shop_list[item]["amount"]} '
                                 f'{shop_list[item]["measurement_unit"]}.\n')

        response = HttpResponse(download_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    def _add(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeSchemeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _delete(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, )
    filter_class = IngredientFilter
