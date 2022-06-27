from django.contrib import admin

from users.models import User, Subscription
from recipes.models import (Cart, Favorite, Ingredient,
                            IngredientRecipes, Recipes, Tag, TagRecipes)

class IngredientRecipeInline(admin.TabularInline):

    model = IngredientRecipes
    extra = 1


class TagRecipeInline(admin.TabularInline):

    model = TagRecipes
    extra = 1


class UserAdmin(admin.ModelAdmin):

    list_display = ('username', 'email', 'id')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'
    list_filter = ('username', 'email')


class IngredientAdmin(admin.ModelAdmin):
 
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )
    empty_value_display = '-пусто-'
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    """Parametrs of the tags admin zone."""

    list_display = ('name', 'color', 'slug')
    search_fields = ('name', )
    empty_value_display = '-пусто-'
    list_filter = ('name',)


class CartAdmin(admin.ModelAdmin):
    """Parametrs of the cart admin zone."""

    list_display = ('user', 'recipes', 'id')
    search_fields = ('user', )
    empty_value_display = '-пусто-'
    list_filter = ('user',)


class FavoriteAdmin(admin.ModelAdmin):
    """Parametrs of the favorite recipes admin zone."""

    list_display = ('user', 'recipes')
    search_fields = ('user', )
    empty_value_display = '-пусто-'
    list_filter = ('user',)


class RecipesAdmin(admin.ModelAdmin):
    """Parametrs of the recipes admin zone."""

    inlines = (IngredientRecipeInline, TagRecipeInline,)
    list_display = ('name', 'author', 'cooking_time',
                    'id', 'count_favorite', 'pub_date')
    search_fields = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    list_filter = ('name', 'author', 'tags')

    def count_favorite(self, obj):
        """Count the number of the recipe additions to favorites."""
        return Favorite.objects.filter(recipes=obj).count()
    count_favorite.short_description = 'Число добавлении в избранное'


class SubscriptionAdmin(admin.ModelAdmin):
    """Parametrs of the admin zone."""

    list_display = ('user', 'following')
    search_fields = ('user', )
    empty_value_display = '-пусто-'
    list_filter = ('user',)


admin.site.register(Cart, CartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Subscription)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipes, RecipesAdmin)
