from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (Ingredient, Recipe, Tag, Favorite,
                            Shopping_cart, IngredientRecipe)
from users.models import User, Subscription

from .filters import RecipeFilter, IngredientSearchFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (IngredientSerializer,
                          RecipeSerializer, TagSerializer,
                          SubscriptionShowSerializer, SubscriptionSerializer,
                          FavoriteSerializer, RecipeMiniSerializer,
                          ShoppingCartSerializer, RecipeCreateSerializer)
from .pagination import CustomPagination


class SubscribtionViewSet(viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer
    queryset = User.objects.all()

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='subscribe',
        permission_classes=(IsAuthorOrAdminOrReadOnly, )
    )
    def get_subscribe(self, request, pk):
        """Позволяет пользователю подписываться и отписываться от авторов."""
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                data={'subscriber': request.user.id, 'author': author.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            author_serializer = SubscriptionShowSerializer(
                author, context={'request': request}
            )
            return Response(
                author_serializer.data, status=status.HTTP_201_CREATED
            )
        subscription = get_object_or_404(
            Subscription, subscriber=request.user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        url_path='subscriptions',
        permission_classes=(permissions.IsAuthenticated, )
    )
    def get_subscriptions(self, request):
        """Отображение подписок."""
        queryset = User.objects.filter(author__subscriber=request.user)
        paginator = CustomPagination()
        result_pages = paginator.paginate_queryset(
            queryset=queryset, request=request
        )
        serializer = SubscriptionShowSerializer(
            result_pages, context={'request': request}, many=True
        )
        return paginator.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для создания обьектов класса Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для создания обьектов класса Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientSearchFilter
    search_fields = ('^name', )


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания обьектов класса Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly, ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_favorite(self, request, pk):
        """Позволяет текущему пользователю добавлять рецепты в избранное."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            show_favorite_serializer = RecipeMiniSerializer(recipe)
            return Response(
                show_favorite_serializer.data, status=status.HTTP_201_CREATED)
        favorite_recipe = get_object_or_404(
            Favorite, user=request.user, recipe=recipe)
        favorite_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_shopping_cart(self, request, pk):
        """Позволяет текущему пользователю добавлять рецепты
        в список покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            show_cart_serializer = RecipeMiniSerializer(recipe)
            return Response(
                show_cart_serializer.data, status=status.HTTP_201_CREATED)
        shopping_cart_recipe = get_object_or_404(
            Shopping_cart, user=request.user, recipe=recipe)
        shopping_cart_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Позволяет текущему пользователю скачать список покупок."""
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(total_amount=Sum('amount'))
        content_list = []
        for ingredient in ingredients:
            content_list.append(
                f'{ingredient["ingredient__name"]}, '
                f'{ingredient["ingredient__measurement_unit"]}, '
                f'{ingredient["total_amount"]}')
        content = 'Ваш список покупок:\n\n' + '\n'.join(content_list)
        filename = 'shopping_cart.txt'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(filename))
        return response

    def get_serializer_class(self):
        """Определяет сериализатор, который будет использоваться
        для разных типов запроса."""
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer
