from django.contrib import admin

from .models import (Tag, Ingredient, Recipe, IngredientRecipe,
                     Shopping_cart, Favorite)


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    empty_value_display = '-empty-'
    list_editable = ('name', 'slug',)
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-empty-'


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_editable = ('ingredient', 'amount')
    search_fields = ('ingredient',)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'count_favorite')
    inlines = [IngredientRecipeInline, ]
    empty_value_display = '-empty-'
    list_editable = ('name', 'author')
    search_fields = ('name', 'author')
    list_filter = ('author', 'name', 'tags')

    def count_favorite(self, object):
        return object.favorite.count()

    count_favorite.short_description = 'Количество добавлений в избранное'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    empty_value_display = '-empty-'
    list_editable = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    empty_value_display = '-empty-'
    list_editable = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Shopping_cart, ShoppingCartAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
