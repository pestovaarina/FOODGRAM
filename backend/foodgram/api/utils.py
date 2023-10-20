from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from recipes.models import Recipe, Shopping_cart, Favorite
from .serializers import (FavoriteSerializer, ShoppingCartSerializer,
                          RecipeMiniSerializer)


MODELS = {
    Shopping_cart: ShoppingCartSerializer,
    Favorite: FavoriteSerializer
}


def post_request(self, model, request, pk) -> Response:
    """Обрабатывает POST запрос."""
    try:
        recipe: Recipe = get_object_or_404(Recipe, pk=pk)
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    serializer = MODELS[model](
        data={'user': request.user.id, 'recipe': recipe.id}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    show_serializer = RecipeMiniSerializer(recipe)
    return Response(show_serializer.data, status=status.HTTP_201_CREATED)


def delete_request(self, model, request, pk) -> Response:
    """Обрабатывает DELETE запрос."""
    recipe: Recipe = get_object_or_404(Recipe, pk=pk)
    try:
        current_recipe = get_object_or_404(
            model, user=request.user, recipe=recipe)
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    current_recipe.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
