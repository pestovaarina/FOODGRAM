import base64
from typing import Any

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            Shopping_cart, Tag)
from users.models import Subscription, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания объекта класса User."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'password')


class CustomUserSerializer(UserSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj: Subscription) -> bool:
        """Функция для проверки подписки текущего
        пользователя на автора аккаунта."""
        request: Any | None = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.author.filter(subscriber=request.user).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для связи модели ингредиентов и рецептов."""

    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientRecipeAddSerializer(serializers.ModelSerializer):
    """Сериализатор для связи модели ингредиентов и рецептов."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class Base64ImageField(serializers.ImageField):
    """Сериализатор для работы с изображениями."""

    def to_internal_value(self, data: str) -> str:
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецепта."""

    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_ingredients(self, obj: Recipe) -> dict:
        """Функция отображения ингредиентов в рецепте."""
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj: Recipe) -> bool:
        """Проверяет, добавил ли текущий пользователь рецепт в избанное."""
        request: Any | None = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.favorite.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj: Recipe) -> bool:
        """Проверяет, добавил ли текущий пользователь
        рецепт в список покупок."""
        request: Any | None = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.shopping_cart.filter(recipe=obj).exists()


class RecipeCreateSerializer(RecipeSerializer):
    """Сериализатор создания/обновления рецепта."""

    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = IngredientRecipeAddSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def validate(self, data: dict) -> dict:
        """Проверяем, что рецепт содержит уникальные ингредиенты
        и их количество не меньше 1."""
        if not data.get('ingredients'):
            raise serializers.ValidationError(
                'Нужно добавить хотя бы 1 ингредиент!')
        if not data.get('tags'):
            raise serializers.ValidationError(
                'Нужно добавить хотя бы 1 тег!')
        ingredients: list = self.initial_data.get('ingredients')
        ingredient_list: list = []
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть меньше 1.')
            ingredient_list.append(ingredient['id'])
        if len(ingredient_list) != len(set(ingredient_list)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.')
        return data

    def validate_tags(self, tags: dict) -> dict:
        """Проверяем, что рецепт содержит уникальные теги."""
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги рецепта должны быть уникальными'
            )
        return tags

    @staticmethod
    def add_ingredient(ingredients, recipe):
        """Добавляет ингредиент."""
        ingredients_list: list = []
        for ingredient in ingredients:
            current_ingredient = ingredient['id']
            current_amount = ingredient['amount']
            ingredients_list.append(
                IngredientRecipe(
                    recipe=recipe,
                    ingredient=current_ingredient,
                    amount=current_amount
                )
            )
        IngredientRecipe.objects.bulk_create(ingredients_list)

    def create(self, validated_data: dict) -> Recipe:
        """Функция для создания рецепта."""
        author: Any = self.context.get('request').user
        ingredients: list = validated_data.pop('ingredients')
        tags: list = validated_data.pop('tags')
        recipe: Recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.add(*tags)
        self.add_ingredient(ingredients, recipe)
        return recipe

    def update(self, instance: Recipe, validated_data: dict) -> Recipe:
        """Функция для изменения рецепта."""
        recipe = instance
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        tags = validated_data.get('tags')
        instance.tags.clear()
        instance.tags.add(*tags)
        ingredients = validated_data.get('ingredients')
        instance.ingredients.clear()
        self.add_ingredient(ingredients, recipe)
        instance.save()
        return instance

    def to_representation(self, recipe: Recipe) -> dict:
        """Определяет какой сериализатор будет использоваться для чтения."""
        serializer = RecipeSerializer(recipe)
        return serializer.data


class RecipeMiniSerializer(RecipeSerializer):
    """Сериализатор для отображения рецептов в сокращенном виде."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Subscription."""

    class Meta:
        model = Subscription
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('author', 'subscriber'),
                message='Вы уже подписались на этого автора'
            )
        ]

    def validate(self, data: dict) -> dict:
        """Проверяем, что пользователь не подписывается на самого себя."""
        if data['subscriber'] == data['author']:
            raise serializers.ValidationError(
                'Ты, конечно, супер, но дай другим подписаться на тебя!')
        return data


class SubscriptionShowSerializer(CustomUserSerializer):
    """Сериализатор отображения подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = Recipe.objects.filter(author=obj)
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeMiniSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, object: User) -> int:
        return object.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Favorite."""

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже в вашем списке избранного!'
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Shopping_Cart."""

    class Meta:
        model = Shopping_cart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Shopping_cart.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже в вашем списке покупок!'
            )
        ]
