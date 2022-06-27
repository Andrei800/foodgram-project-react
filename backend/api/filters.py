from django_filters.rest_framework import FilterSet, filters
from django_filters.widgets import BooleanWidget
from rest_framework.filters import SearchFilter

from recipes.models import Recipes


class RecipesFilter(FilterSet):
    author = filters.AllValuesMultipleFilter(
        field_name='author__id'
    )
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = filters.BooleanFilter(
        widget=BooleanWidget()
    )
    is_in_shopping_cart = filters.BooleanFilter(
        widget=BooleanWidget()
    )

    class Meta:
        model = Recipes
        fields = [
            'author__id', 'tags__slug',
            'is_favorited',
            'is_in_shopping_cart'
        ]


class IngredientFilter(SearchFilter):
    search_param = "name"
