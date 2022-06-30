from django.contrib import admin

from users.models import User, Subscription
from recipes.models import (Cart, Favorite, Ingredient,
                            IngredientInRecipes, Recipes, Tag, TagRecipes)


class IngredientRecipesInline(admin.TabularInline):

    model = IngredientInRecipes
    extra = 1


class TagRecipesInline(admin.TabularInline):

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

    list_display = ('name', 'color', 'slug')
    search_fields = ('name', )
    empty_value_display = '-пусто-'
    list_filter = ('name',)


class CartAdmin(admin.ModelAdmin):

    list_display = ('user', 'recipes', 'id')
    search_fields = ('user', )
    empty_value_display = '-пусто-'
    list_filter = ('user',)


class FavoriteAdmin(admin.ModelAdmin):

    list_display = ('user', 'recipes')
    search_fields = ('user', )
    empty_value_display = '-пусто-'
    list_filter = ('user',)


class RecipesAdmin(admin.ModelAdmin):

    inlines = (IngredientRecipesInline, TagRecipesInline,)
    list_display = ('name', 'author', 'cooking_time',
                    'id', 'count_favorite', 'pub_date')
    search_fields = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    list_filter = ('name', 'author', 'tags')

    def count_favorite(self, obj):
        return Favorite.objects.filter(recipes=obj).count()
    count_favorite.short_description = 'Число добавлении в избранное'


class SubscriptionAdmin(admin.ModelAdmin):

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
