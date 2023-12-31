from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(filters.FilterSet):
    """Фильтрация рецептов по определенным полям."""

    author = filters.AllValuesMultipleFilter(
        field_name='author__id',
        label='Автор')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        label='Тег',
        to_field_name='slug'
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        """Показывает рецепты, добавленные в избранное."""
        if self.request.user.is_authenticated:
            if value:
                return queryset.filter(favorite__user=self.request.user)
            return queryset
        else:
            return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """Показывает рецепты, добавленные в список покупок."""
        if self.request.user.is_authenticated:
            if value:
                return queryset.filter(shopping_cart__user=self.request.user)
            return queryset
        else:
            return queryset


class IngredientSearchFilter(filters.FilterSet):
    """Фильтр поиска по названию ингредиента."""

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
