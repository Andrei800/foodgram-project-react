from django.db.models import F, Sum
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
                             IngredientInRecipes, Recipes,
                             ShoppingCart, Tag)
from users.models import Subscription, User

from .filters import IngredientFilter, RecipesFilter
from .mixins import ListCreateRetrieveUpdateDestroyViewSet, ListRetrieveViewSet
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipesMinifiedSerializer,
                          RecipesReadSerializer, RecipesSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserDjoserSerializer)


class UserViewSet(UserViewSet):
    http_method_names = ['get', 'post', 'delete']
    pagination_class = CustomPagination

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
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
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
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
    queryset = Ingredient.objects.all().order_by(F('name'))
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter, )
    http_method_names = ['get', ]
    lookup_fields = ['id', ]
    search_fields = ('^name', )
    permission_classes = [IsAdminOrReadOnly]


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all().order_by(F('id'))
    serializer_class = TagSerializer
    http_method_names = ['get', ]
    lookup_fields = ['id']
    permission_classes = [IsAdminOrReadOnly]


class RecipesViewSet(ListCreateRetrieveUpdateDestroyViewSet):
    queryset = Recipes.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filter_class = RecipesFilter

    def get_queryset(self):
        return self.queryset.add_user_annotations(self.request.user.id)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipesReadSerializer
        return RecipesSerializer

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        response = HttpResponse(content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename=shopping_list.txt'

        user = request.user
        ingredients = IngredientInRecipes.objects.filter(
            recipes__foodgram_shoppingcarts__user=user
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
    def post_or_delete_object(model, recipes, request):
        current_model = model.objects.filter(
            user=request.user, recipes=recipes
        )
        if request.method == 'POST':
            if current_model.exists():
                return Response(
                    {'errors': 'Ошибка добавления. Уже есть в списке'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=request.user, recipes=recipes)
            serializer = RecipesMinifiedSerializer(recipes)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        current_model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        permission_classes=[IsAuthenticated],
        methods=['POST', 'DELETE']
    )
    def shopping_cart(self, request, pk):
        recipes = get_object_or_404(Recipes, pk=pk)
        return self.post_or_delete_object(
            model=ShoppingCart, recipes=recipes, request=request)

    @action(
        detail=True,
        permission_classes=[IsAuthenticated],
        methods=['POST', 'DELETE']
    )
    def favorite(self, request, pk):
        recipes = get_object_or_404(Recipes, pk=pk)
        return self.post_or_delete_object(
            model=Favorite, recipe=recipes, request=request)