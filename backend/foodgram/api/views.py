from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from requests import Request
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            Shopping_cart, Tag)
from users.models import Subscription, User

from .pagination import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .filters import IngredientSearchFilter, RecipeFilter
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          SubscriptionSerializer, SubscriptionShowSerializer,
                          TagSerializer)
from .utils import delete_request, post_request


class CustomUserViewSet(UserViewSet):

    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly, )

    def get_permissions(self) -> list:
        """Запрещает неавторизованному пользователю
        заходить на эндпоинт users/me/."""
        if self.action == 'me':
            self.permission_classes = (permissions.IsAuthenticated, )
        return super().get_permissions()

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='subscribe',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_subscribe(self, request: Request, id: int) -> Response:
        """Позволяет пользователю подписываться и отписываться от авторов."""
        author: User = get_object_or_404(User, id=id)
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
        try:
            subscription: Subscription = get_object_or_404(
                Subscription, subscriber=request.user, author=author
            )
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        url_path='subscriptions',
        permission_classes=(permissions.IsAuthenticated, )
    )
    def get_subscriptions(self, request: Request) -> Response:
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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrAdminOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_favorite(self, request: Request, pk: int) -> Response:
        """Позволяет текущему пользователю добавлять рецепты в избранное."""
        if request.method == 'POST':
            return post_request(self, Favorite, request, pk)
        return delete_request(self, Favorite, request, pk)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_shopping_cart(self, request: Request, pk: int):
        """Позволяет текущему пользователю добавлять рецепты
        в список покупок."""
        if request.method == 'POST':
            return post_request(self, Shopping_cart, request, pk)
        return delete_request(self, Shopping_cart, request, pk)

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request: Request) -> HttpResponse:
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
