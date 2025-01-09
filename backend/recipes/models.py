from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from constants import (DEFAULT_MAX_AMOUNT, DEFAULT_MAX_VALUE,
                       DEFAULT_MIN_VALUE, INGREDIENT_NAME_LEN, LENGTH_TEXT,
                       MAX_TIME_MSG, MEASUREMENT_UNIT_LEN, MESSAGE_AMOUNT,
                       MIN_TIME_MSG, RECIPE_NAME_LEN)

User = get_user_model()


class Tag(models.Model):
    """
    Модель для работы с тегами,
    отвечающая за уникальную фильтрацию рецептов.
    """

    name = models.CharField(
        max_length=LENGTH_TEXT,
        unique=True,
        verbose_name='Название тега',
        help_text='Укажите название тега',
    )
    slug = models.SlugField(
        max_length=LENGTH_TEXT,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Уникальный слаг тега',
        help_text='Укажите слаг тега',
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'Тег "{self.name}"'


class Ingredient(models.Model):
    """Модель ингредиентов, используемых в рецептах."""

    name = models.CharField(
        max_length=INGREDIENT_NAME_LEN,
        unique=True,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_LEN,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        default_related_name = 'ingredient'

    def __str__(self):
        return f'Ингредиент: {self.name}, ед. изм.: {self.measurement_unit}'


class Recipe(models.Model):
    """Модель для работы с рецептами."""

    name = models.CharField(
        max_length=RECIPE_NAME_LEN,
        verbose_name='Название',
        help_text='Придумайте название для рецепта',
    )
    text = models.TextField(
        verbose_name='Текстовое описание рецепта',
        help_text='Опишите последовательность действий',
    )
    cooking_time = models.PositiveSmallIntegerField(
        null=False,
        verbose_name='Время приготовления',
        help_text='Укажите время приготовления блюда в минутах',
        validators=(
            MinValueValidator(DEFAULT_MIN_VALUE, MIN_TIME_MSG),
            MaxValueValidator(DEFAULT_MAX_VALUE, MAX_TIME_MSG),
        ),
        default=DEFAULT_MIN_VALUE,
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=False,
        null=False,
        verbose_name='Фото блюда',
        help_text='Загрузите подходящее фото блюда',
    )
    author = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Укажите автора рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        help_text='Нужно указать хотя бы один тег',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиент',
        help_text='Укажите список требуемых ингредиентов',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации рецепта',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return self.name[:LENGTH_TEXT]


class RecipeIngredient(models.Model):
    """
    Количество ингридиентов в рецепте блюда.
    Вспомогательная модель для связывания модели Recipe и Ingredient.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Укажите рецепт, к которому относится ингредиент',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        help_text='Укажите ингредиент, используемый в рецепте'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента в рецепте',
        help_text='Укажите количество ингредиента в рецепте',
        validators=(
            MinValueValidator(DEFAULT_MIN_VALUE, MESSAGE_AMOUNT),
            MaxValueValidator(DEFAULT_MAX_AMOUNT, MESSAGE_AMOUNT),
        ),
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        default_related_name = 'ingredients_in_recipe'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_recipe_ingredient'
        )
        ]

    def __str__(self):
        return f'{self.recipe.name}: {self.ingredient.name} — {self.amount}'


class BaseUserRecipeModel(models.Model):
    """
    Вспомогательная абстрактная модель для связывания модели Recipe и User.
    Модель является базовой моделью для меделей Fovorite и ShoppingList.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='%(class)s_user_recipe_unique')
        ]


class Favorite(BaseUserRecipeModel):
    """
    Модель для избранных рецептов пользлвателя.
    Данная модель наследуется от базовой BaseUserRecipeModel.
    """

    class Meta(BaseUserRecipeModel.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'


class ShoppingList(BaseUserRecipeModel):
    """
    Модель для списка покупок пользлвателя.
    Данная модель наследуется от базовой BaseUserRecipeModel.
    """

    class Meta(BaseUserRecipeModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shoppinglists'
