from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag, TagRecipe)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


class TagRecipeInline(admin.TabularInline):
    model = Recipe.tags.through


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    inlines = [
        TagRecipeInline,
    ]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', )
    list_filter = ('name', )
    inlines = (IngredientInRecipeInline,)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'amount_in_favorite')
    list_filter = (
        ('author', admin.RelatedOnlyFieldListFilter),
        'name',
        ('tags', admin.RelatedOnlyFieldListFilter),
    )
    inlines = [
        IngredientInRecipeInline,
        TagRecipeInline,
    ]

    @admin.display
    def amount_in_favorite(self, obj):
        return obj.recipe_foodgram_favorite_related.all().count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    pass


empty_value_display = '-empty-'
