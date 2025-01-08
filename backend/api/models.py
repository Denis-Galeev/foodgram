import hashlib

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from constants import (LENGTH_TEXT, INGREDIENT_NAME_LEN, RECIPE_NAME_LEN,
                       DEFAULT_MIN_VALUE, DEFAULT_MAX_VALUE, MIN_TIME_MSG,
                       MAX_TIME_MSG, MESSAGE_AMOUNT, MEASUREMENT_UNIT_LEN,
                       MAX_EMAIL_FIELD, MAX_NAME_FIELD, HELP_TEXT_NAME,
                       UNIQUE_FIELDS, DEFAULT_MAX_AMOUNT)
from users.validators import UsernameValidator, validate_username


class User(AbstractUser):
    """
    Расширенная Django модель User -
    добавлены поля для аватарки и роли пользователя.
    """

    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        ADMIN = 'admin', 'Администратор'

    username = models.CharField(
        max_length=MAX_NAME_FIELD,
        unique=True,
        verbose_name='Имя пользователя',
        help_text=HELP_TEXT_NAME,
        validators=(UsernameValidator(), validate_username,),
        error_messages={'unique': UNIQUE_FIELDS[1], },
    )
    first_name = models.CharField(
        max_length=MAX_NAME_FIELD,
        blank=False,
        null=False,
        verbose_name='Имя',
        help_text='Введите Имя',
    )
    last_name = models.CharField(
        max_length=MAX_NAME_FIELD,
        blank=False,
        null=False,
        verbose_name='Фамилия',
        help_text='Введите Фамилию',
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_FIELD,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Электронная почта',
        help_text='Введите свой email',
        error_messages={'unique': UNIQUE_FIELDS[0], },
    )
    role = models.CharField(
        max_length=max(len(role) for role, _ in Role.choices),
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль пользователя',
        help_text='Уровень доступа пользователя'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Аватарка или фото',
        help_text='Загрузите аватарку или фото',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    @property
    def is_admin(self):
        return (
            self.role == self.Role.ADMIN
            or self.is_superuser
            or self.is_staff
        )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id', 'username',)

    def __str__(self):
        return self.username[:LENGTH_TEXT]


class Subscription(models.Model):
    """
    Модель подписок пользователей на других пользователей.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор рецеата'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique_user_author'
        )
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'


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
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время добавления'
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


class ShortLink(models.Model):
    """Модель для хранения коротких ссылок."""
    original_url = models.URLField(unique=True)
    short_code = models.CharField(max_length=10, unique=True)

    def generate_short_code(self):
        """Генерация короткого кода на основе оригинального URL."""
        return hashlib.md5(self.original_url.encode()).hexdigest()[:6]

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self.generate_short_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.original_url} -> {self.short_code}'
