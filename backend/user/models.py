from django.contrib.auth.models import AbstractUser
from django.db import models

from api.constants import (
    MAX_EMAIL_FIELD, MAX_NAME_FIELD,
    LENGTH_TEXT, HELP_TEXT_NAME, UNIQUE_FIELDS
)
from .validators import UsernameValidator, validate_username


class User(AbstractUser):
    """
    Расширенная стандартная Django модель User -
    добавлены поля биография и роль пользователя.
    """
    username = models.CharField(
        max_length=MAX_NAME_FIELD,
        unique=True,
        verbose_name='Имя пользователя',
        help_text=HELP_TEXT_NAME,
        validators=(UsernameValidator(), validate_username,),
        error_messages={
            'unique': UNIQUE_FIELDS[1],
        },
    )
    first_name = models.CharField(
        max_length=MAX_NAME_FIELD,
        blank=True,
        null=True,
        verbose_name='Имя',
        help_text='Заполните Имя',
        default='Пусто'
    )
    last_name = models.CharField(
        max_length=MAX_NAME_FIELD,
        blank=True,
        null=True,
        verbose_name='Фамилия',
        help_text='Заполните Фамилию',
        default='Пусто'
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_FIELD,
        unique=True,
        verbose_name='Электронная почта',
        help_text='Введите свой email',
        error_messages={
            'unique': UNIQUE_FIELDS[0],
        },
    )

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
