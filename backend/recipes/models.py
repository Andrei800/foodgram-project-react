from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='name',
        help_text='Укажите навзание тега. Например, "Завтрак"',
    )
    color = models.CharField(
        max_length=7,
        help_text='Color in HEX',
        unique=True,
        null=True,
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        null=True,
        verbose_name='Unique Slug',
        help_text=(
            "Укажите уникальный фрагмент URL-адреса "
            "для тега. Используйте только латиницу, "
            "цифры, дефисы и знаки подчёркивания."
        ),
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Ingredient name',
        help_text='Укажите название игредиента. Например: Капуста',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Units',
        help_text='Единицы измерения. Например: кг',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


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


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Recipe Author',
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='ingredient list',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='List of id tags',
        help_text='Добавьте теги к своему рецепту',
    )
    image = models.ImageField(
        upload_to='recipes/media/image/',
        verbose_name='Recipe Image',
        help_text='Картинка, закодированная в Base64',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Name',
        help_text='Введите название рецепта',
    )
    text = models.TextField(
        help_text='Описание Вашего рецепта здесь',
        verbose_name='Recipe description'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Время приготовления (в минутах)',
        verbose_name='Cooking time (in minutes)',
    )
    pub_date = models.DateTimeField(
        verbose_name='Publication date',
        auto_now_add=True,
    )

    objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tag'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipe_tag'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('recipe', 'tag',),
                                    name='tag_recipe'),
        )

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),),
        help_text='Минимальное количество 1',
        verbose_name='Количество в рецепте',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('recipe', 'ingredient',),
                                    name='ingredient_in_recipes'),
        )

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class UserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_%(app_label)s_%(class)s_related',
        related_query_name='%(app_label)s_%(class)ss',
        verbose_name='User'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_%(app_label)s_%(class)s_related',
        related_query_name='%(app_label)s_%(class)ss',
        verbose_name='Recipe'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
    )
    created = models.DateTimeField(
        auto_now_add=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ['-created']

        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='%(class)s_unique_favorite_user_recipes',
            ),
        )

    def __str__(self):
        return f'Пользователь: {self.user}, рецепт {self.recipe}'


class Favorite(UserRecipe):
    pass


class ShoppingCart(UserRecipe):
    pass
