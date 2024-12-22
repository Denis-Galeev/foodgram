from django.contrib.auth.models import AbstractUser
from django.db import models

from api.constants import (
    MAX_EMAIL_FIELD, MAX_NAME_FIELD, LENGTH_TEXT, HELP_TEXT_NAME, UNIQUE_FIELDS
)
from .validators import UsernameValidator, validate_username


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
        blank=False,
        null=False,
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
        # default='avatars/default.png',
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
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор рецеата'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique_user_author'
        )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
