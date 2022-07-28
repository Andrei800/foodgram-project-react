from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Favorite,
                            IngredientInRecipe, Recipe, ShoppingCart)
from users.models import Subscription, User

from backend.settings import SHOP_LIST
from api.filters import IngredientFilter, RecipeFilter
from api.mixins import (ListCreateRetrieveUpdateDestroyViewSet,
                        ListRetrieveViewSet)
from api.pagination import CustomPagination
from api.permissions import IsAdminOrReadOnly
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
        methods=('post', 'delete',),
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
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter, )
    http_method_names = ('get',)
    lookup_fields = ('id',)
    search_fields = ('^name', )
    permission_classes = (IsAdminOrReadOnly,)


class TagViewSet(ListRetrieveViewSet):
    serializer_class = TagSerializer
    http_method_names = ('get',)
    lookup_fields = ('id',)
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(ListCreateRetrieveUpdateDestroyViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete',)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend)
    filter_class = RecipeFilter

    def get_queryset(self):
        return self.queryset.add_user_annotations(self.request.user.id)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeSerializer

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in_purchases__user=request.user).values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(total=Sum('amount'))

        shopping_cart = '\n'.join([
            f'{ingredient["ingredient__name"]} - {ingredient["total"]} '
            f'{ingredient["ingredient__measurement_unit"]}'
            for ingredient in ingredients
        ])
        filename = 'shopping_cart.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


    def download_shopping_cart(self, request):
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=' + SHOP_LIST

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
