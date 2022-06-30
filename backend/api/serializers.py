from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Ingredient, IngredientInRecipes, Recipes, Tag,
                             TagRecipes)
from users.models import Subscription, User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )


class IngredientInRecipesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipes
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class UserDjoserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

        def create(self, validated_data):
            user = User.objects.create(**validated_data)
            user.set_password(validated_data['password'])
            user.save()
            return user

        def validate_username(self, value):
            if value == 'me':
                raise serializers.ValidationError(
                    'Имя пользователя me запрещено'
                )
            return value


class UserDjoserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Subscription.objects.filter(
                user=user, author=obj).exists())


class SubscriptionSerializer(UserDjoserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        depth = 1
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
            'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get("recipes_limit", None)
        if limit is not None:
            recipes = Recipes.objects.filter(author=obj)[:int(limit)]
        else:
            recipes = Recipes.objects.filter(author=obj)
        return RecipesMinifiedSerializer(
            recipes, many=True, read_only=True
        ).data

    def get_recipes_count(self, obj):
        return Recipes.objects.filter(author=obj).count()


class RecipesReadSerializer(serializers.ModelSerializer):
    author = UserDjoserSerializer(many=False, read_only=True)
    ingredients = IngredientInRecipesSerializer(
        source='ingredient_in_recipe', many=True, read_only=True
    )
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipes
        depth = 1
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image',
            'text', 'cooking_time',
        )


class TagRecipesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='tag.id')
    name = serializers.ReadOnlyField(source='tag.name')
    color = serializers.ReadOnlyField(source='tag.color')
    slug = serializers.ReadOnlyField(source='tag.slug')

    class Meta:
        model = TagRecipes
        fields = ('id', 'name', 'color', 'slug')
        validators = [
            UniqueTogetherValidator(
                queryset=TagRecipes.objects.all(),
                fields=('recipe', 'tag'),
                message='Данный тег уже указан в рецепте!',
            ),
        ]


class RecipesSerializer(WritableNestedModelSerializer):
    author = UserDjoserSerializer(read_only=True)
    ingredients = IngredientInRecipesSerializer(many=True)
    tags = tags = serializers.ListField(child=serializers.IntegerField())
    image = Base64ImageField()

    class Meta:
        model = Recipes
        depth = 1
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, attrs):
        self._kwargs['partial'] = True
        return super().validate(attrs)

    def validate_ingredients(self, value):
        ingredient_id_list = []
        for ingredient in value:
            ingredient_id_list.append(ingredient['ingredient']['id'])
        if len(ingredient_id_list) != len(set(ingredient_id_list)):
            raise serializers.ValidationError(
                'Ингредиент уже есть в рецепте!'
            )
        return value

    def get_or_set_ingredients_in_recipe(
        self, ingredients_data, recipe,
    ):
        for ingredient_data in ingredients_data:
            IngredientInRecipes.objects.create(
                recipe=recipe,
                ingredient=get_object_or_404(
                    Ingredient,
                    id=ingredient_data['ingredient']['id']
                ),
                amount=ingredient_data['amount']
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipes = Recipes.objects.create(
            author=self.context['request'].user, **validated_data)
        self.get_or_set_ingredients_in_recipes(ingredients_data, recipes)
        recipes.tags.set(tags_data)
        return recipes

    def to_representation(self, instance):
        return RecipesReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        super().update(instance, validated_data)
        self.get_or_set_ingredients_in_recipe(ingredients_data, instance)
        instance.tags.set(tags_data)
        return instance


class RecipesMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'

        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на данного автора!',
            ),
        ]

    def validate_author(self, value):
        if value == self.context['request'].user:
            raise serializers.ValidationError(
                'Вы пытаетесь подписаться на самого себя!')
        return value