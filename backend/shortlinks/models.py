import hashlib

from django.db.models import CharField, Model, URLField

from constants import CODE_LEN, MAX_URL_FIELD


class ShortLink(Model):
    """Модель для хранения коротких ссылок."""

    original_url = URLField(
        max_length=MAX_URL_FIELD,
        unique=True,
        verbose_name='Оригинальный URL'
    )
    short_code = CharField(
        max_length=CODE_LEN,
        unique=True,
        verbose_name='Короткий код'
    )

    def generate_short_code(self):
        """Генерация короткого кода на основе оригинального URL."""
        return hashlib.md5(self.original_url.encode()).hexdigest()[:CODE_LEN]

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self.generate_short_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.original_url} -> {self.short_code}'

    class Meta:
        verbose_name = 'Короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'
