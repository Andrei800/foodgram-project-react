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
    list_display = ['id', 'name', 'color', 'slug']
    search_fields = ['name', 'slug']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit', )
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
        return obj.recipe_recipes_favorite_related.all().count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    search_fields = ('recipes', 'user__username', 'user__email',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    search_fields = ('recipes', 'user__username', 'user__email',)


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    search_fields = ('recipes', 'user__username', 'user__email',)
    list_filter = ('tag',)


empty_value_display = '-empty-'
