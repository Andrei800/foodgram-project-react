from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название ингредиента',
        help_text='Укажите название игредиента',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения',
        help_text='Единицы измерения',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название',
        help_text='Укажите название тега',
    )
    color = models.CharField(
        max_length=7,
        help_text='Цвет',
        unique=True,
        null=True,
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        null=True,
        verbose_name='Уникальный слаг',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes',
        help_text='Выберите автора рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipes',
        verbose_name='Список ингредиентов',
        related_name='recipes',
        help_text='Выберите продукты рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipes',
        verbose_name='Список id тегов',
        help_text='Добавьте теги к своему рецепту',
    )
    image = models.ImageField(
        upload_to='recipes/media/image/',
        verbose_name='Изображение рецепта',
        help_text='Выберите изображение рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Введите название рецепта',
    )
    text = models.TextField(
        help_text='Описание Вашего рецепта здесь',
        verbose_name='Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Время приготовления (в минутах)',
        verbose_name='Время приготовления (в минутах)',
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        help_text='Добавить дату создания',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class TagRecipes(models.Model):
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipes_tag'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipes_tag'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recipes', 'tag'],
                                    name='tag_recipes')
        ]

    def __str__(self):
        return f'{self.recipes} {self.tag}'


class Cart(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите пользователя'
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Рецепты',
        help_text='Выберите рецепты для добавления в корзину'
    )

    class Meta:

        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipes'],
                                    name='unique_cart')
        ]

    def __str__(self):
        return f'{self.user} {self.recipes}'


class IngredientInRecipes(models.Model):
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Минимальное количество 1',
        verbose_name='Количество в рецепте',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recipes', 'ingredient'],
                                    name='ingredient_in_recipes')
        ]

    def __str__(self):
        return f'{self.recipes} {self.ingredient}'


class UserRecipes(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_%(app_label)s_%(class)s_related',
        related_query_name='%(app_label)s_%(class)ss',
        verbose_name='Пользователь'
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipes_%(app_label)s_%(class)s_related',
        related_query_name='%(app_label)s_%(class)ss',
        verbose_name='Рецепт'
    )
    created = models.DateTimeField(
        auto_now_add=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ('-created',)

        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipes',),
                name='%(class)s_unique_favorite_user_recipes'
            )
        ]

    def __str__(self):
        return f'Пользователь: {self.user}, рецепт {self.recipes}'


class Favorite(UserRecipes):
    pass


class ShoppingCart(UserRecipes):
    pass
