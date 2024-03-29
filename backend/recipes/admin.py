from django.contrib import admin

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag, TagRecipe)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


class TagRecipeInline(admin.TabularInline):
    model = Recipe.tags.through


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)
    search_fields = ('name', 'slug',)
    inlines = [
        TagRecipeInline,
    ]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    inlines = (IngredientInRecipeInline,)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'amount_in_favorite')
    list_filter = (
        ('tags', admin.RelatedOnlyFieldListFilter),
    )
    inlines = [
        IngredientInRecipeInline,
        TagRecipeInline,
    ]

    @admin.display
    def amount_in_favorite(self, obj):
        return obj.recipe_recipes_favorite_related.all().count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('recipe__name', 'user__username', 'user__email',)
    list_filter = ('recipe__tags',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('recipe__name', 'user__username', 'user__email',)
    list_filter = ('recipe__tags',)


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    search_fields = ('recipe__name', 'recipe__author__username',
                     'recipe__author__email',)
    list_filter = ('tag',)


empty_value_display = '-empty-'
