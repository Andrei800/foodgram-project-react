from django.db import models
from django.db.models import Sum, Exists, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient,
                            IngredientInRecipe, Recipe, ShoppingCart, Tag)
from users.models import Subscription, User

from backend.settings import SHOP_LIST
from api.filters import IngredientFilter, RecipeFilter
from api.mixins import (ListCreateRetrieveUpdateDestroyViewSet,
                        ListRetrieveViewSet)
from api.pagination import CustomPagination
from api.permissions import IsAdminOrReadOnly, IsAuthenticatedOwnerOnly
from api.serializers import (IngredientSerializer, RecipeMinifiedSerializer,
                             RecipeReadSerializer, RecipeSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserDjoserSerializer)


CONTENT_TYPE = 'text/plain'


class UserViewSet(UserViewSet):
    http_method_names = ('get', 'post', 'delete',)
    pagination_class = CustomPagination

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            subscribed_to__user=request.user).order_by('subscribed_to')
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('POST', 'DELETE',),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)
        subscription = Subscription.objects.filter(
            user=user, author=author
        )
        if request.method == 'POST':
            if subscription:
                return Response(
                    {'errors': 'Вы уже подписаны на данного автора'},
                    status=status.HTTP_400_BAD_REQUEST)
            elif user == author:
                return Response(
                    {'errors': 'Вы пытаетесь подписаться на самого себя!'},
                    status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.create(
                user=user, author=author)
            serializer = UserDjoserSerializer(
                author, context={'request': request, })
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if not subscription:
            return Response(
                {'errors': 'У Вас нет подписки на данного автора'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all().order_by('name',)
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter, )
    http_method_names = ('get',)
    lookup_fields = ('id',)
    search_fields = ('^name', )
    permission_classes = (IsAdminOrReadOnly,)


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all().order_by('name',)
    serializer_class = TagSerializer
    http_method_names = ('get',)
    lookup_fields = ('id',)
    permission_classes = (IsAdminOrReadOnly,)


class RecipeQuerySet(models.QuerySet):
    def add_user_annotations(self, user_id):
        return self.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    user_id=user_id, recipe__pk=OuterRef('pk')
                )
            ),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user_id=user_id, recipe__pk=OuterRef('pk')
                )
            ),
        )


class RecipeViewSet(ListCreateRetrieveUpdateDestroyViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthenticatedOwnerOnly)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    queryset = Recipe.objects.all()

    def get_queryset(self):
        return self.queryset.add_user_annotations(self.request.user.id)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeSerializer

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={SHOP_LIST}'

        user = request.user
        ingredients = IngredientInRecipe.objects.filter(
            recipe__recipes_shoppingcarts__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(
                total_amount=Sum('amount')
        )
        lines = []
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            amount = ingredient['total_amount']
            unit = ingredient['ingredient__measurement_unit']
            lines += f'{name}: {amount} {unit}\n'
        response.writelines(lines)
        return response

    @staticmethod
    def post_or_delete_object(model, recipe, request):
        current_model = model.objects.filter(
            user=request.user, recipe=recipe
        )
        if request.method == 'POST':
            if current_model.exists():
                return Response(
                    {'errors': 'Ошибка добавления. Уже есть в списке'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        current_model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        permission_classes=(IsAuthenticated,),
        methods=('POST', 'DELETE',)
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        return self.post_or_delete_object(
            model=ShoppingCart, recipe=recipe, request=request)

    @action(
        detail=True,
        permission_classes=(IsAuthenticated,),
        methods=('POST', 'DELETE',)
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        return self.post_or_delete_object(
            model=Favorite, recipe=recipe, request=request)
